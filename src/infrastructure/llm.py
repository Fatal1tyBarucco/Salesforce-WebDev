"""LLM infrastructure — unified adapters implementing domain contracts.

This module consolidates the multi-provider LLM chain (OpenRouter → OpenCode → Gemini)
from the legacy `src/llm_service.py` and implements the ClassificationAdapter
and EnrichmentAdapter contracts defined in the core layer.
"""

from __future__ import annotations

import json
import logging
import os
import re
import time
from dataclasses import dataclass, field
from typing import Any, ClassVar

from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from src.ai.prompts.classification import build_classification_system_prompt
from src.core.classification.service import ClassificationAdapter
from src.core.enrichment.service import EnrichmentAdapter
from src.models.enrichment import CategoryEnrichment, ReleaseEnrichment

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Provider Configuration (consolidated from legacy LLMService)
# ---------------------------------------------------------------------------

LLM_CALL_TIMEOUT_S = int(os.getenv("LLM_CALL_TIMEOUT_S") or 60)


@dataclass
class _ProviderConfig:
    """Internal provider configuration."""

    name: str
    api_key_env: str
    base_url: str = ""
    default_model: str = ""
    fallback_models: list[str] = field(default_factory=list)


# Ordered by priority (first = preferred).
# Gemini is LAST: free tier caps at ~20 req/day, so we protect that quota
# and only fall back to it after exhausting OpenRouter/OpenCode pools.
_PROVIDER_CHAIN: list[_ProviderConfig] = [
    _ProviderConfig(
        name="openrouter",
        api_key_env="OPENROUTER_API_KEY",
        base_url="https://openrouter.ai/api/v1",
        default_model="openrouter/free",
        fallback_models=[
            "google/gemma-4-31b-it:free",
            "meta-llama/llama-4-scout:free",
            "qwen/qwen-3-coder:free",
            "mistralai/mistral-nemo:free",
            "deepseek/deepseek-chat-v3:free",
            "anthropic/claude-3-haiku:free",
        ],
    ),
    _ProviderConfig(
        # OpenCode free tier models are largely unavailable in 2026-08
        # (401 CreditsError on default, 400 upstream on free variants).
        # Kept as secondary; useful for paid OpenCode accounts.
        name="opencode",
        api_key_env="OPENCODE_API_KEY",
        base_url="https://opencode.ai/zen/v1",
        default_model="gemini-3.6-flash",
        fallback_models=[
            "ling-3.0-flash-free",
            "ling-3.0-tiny-free",
            "nemotron-3-ultra-free",
            "north-mini-code-free",
            "laguna-s-2.1-free",
            "longcat-2.0-free",
            "mus-e-spark-1.2-contributor-free",
        ],
    ),
    _ProviderConfig(
        # Gemini is LAST: free tier caps at ~20 req/day, so we protect that
        # quota and only fall back to it after exhausting OpenRouter/OpenCode.
        name="gemini",
        api_key_env="GOOGLE_API_KEY",
        default_model="gemini-3.6-flash",
    ),
]


def _env_model_override(cfg: _ProviderConfig) -> str:
    """Resolve the model for a provider, honoring per-provider env overrides.

    Each provider reads ``<PROVIDER>_MODEL`` (e.g. ``OPENROUTER_MODEL``,
    ``OPENCODE_MODEL``, ``GEMINI_MODEL``) so automation — such as the
    release-notes pipeline's dynamic free-tier selector — can pin the
    healthiest model for the current run. Unset/blank values fall back to
    the provider's built-in default.
    """
    override = os.getenv(f"{cfg.name.upper()}_MODEL", "").strip()
    return override or cfg.default_model


# Try to import Gemini, make it optional
try:
    import google.genai as _genai_module

    genai = _genai_module
    _HAS_GENAI = True
except ImportError:  # pragma: no cover
    genai = None  # type: ignore[assignment]
    _HAS_GENAI = False

# Classification system prompt - delegated to ai.prompts.classification
CLASSIFICATION_SYSTEM_PROMPT = build_classification_system_prompt()

# Enrichment system prompt
ENRICHMENT_SYSTEM_PROMPT = """
Você é um Arquiteto de Soluções Salesforce sênior especializado em
análise de Release Notes, governança de mudanças e comunicação técnica.

Sua tarefa é enriquecer categorias e releases do Salesforce com:
1. Visão geral de negócio (overview)
2. Temas principais (key_themes)
3. Impacto de negócio (business_impact)
4. Orientações de adoção (adoption_guidance)
5. Avaliação de risco (risk_assessment)
6. Detalhes por feature (summary, details, business_context, technical_context, migration_notes)

Responda em JSON válido com a estrutura solicitada. Escreva em Português Brasileiro (pt-BR).
Seja conciso mas completo. Foque no valor prático para admins e desenvolvedores.
"""

RELEASE_ENRICHMENT_SYSTEM_PROMPT = """
Você é um CTO Salesforce sênior preparando um resumo executivo para liderança.

Sua tarefa é gerar um enriquecimento de nível de release com:
1. Resumo executivo (executive_summary) - 2-3 parágrafos
2. Temas estratégicos (strategic_themes) - lista de 5-10 temas
3. Checklist de migração (migration_checklist) - 5-8 itens acionáveis

Responda em JSON válido. Escreva em Português Brasileiro (pt-BR).
Foque em impacto estratégico, riscos de negócio e decisões de arquitetura.
"""


# ---------------------------------------------------------------------------
# Unified LLM Client (encapsulates the full provider chain)
# ---------------------------------------------------------------------------


class UnifiedLLMClient:
    """Unified LLM client with multi-provider fallback chain.

    Implements the complete provider chain from legacy LLMService:
    1. OpenRouter (free tier, primary)
    2. OpenCode (secondary, for paid accounts)
    3. Google Gemini (tertiary, free tier 20 req/day protected)
    """

    def __init__(
        self,
        api_key: str | None = None,
        model_name: str | None = None,
        provider: str | None = None,
    ) -> None:
        """Initialize the LLM client.

        Args:
            api_key: Optional API key override. If None, resolved from env.
            model_name: Model override. If None, uses provider default.
            provider: Provider override. If None, falls back to the
                ``LLM_PROVIDER`` env var, then auto-detects from available keys.
        """
        self._provider_chain = list(_PROVIDER_CHAIN)
        self._active_provider: _ProviderConfig | None = None
        self._tried_providers: set[str] = set()

        if provider is None:
            provider = os.getenv("LLM_PROVIDER", "").strip() or None

        if provider:
            # Explicit provider requested
            cfg = self._find_provider_config(provider)
            if cfg:
                resolved_key = api_key or os.getenv(cfg.api_key_env, "")
                if resolved_key:
                    self._active_provider = cfg
                    self.api_key = resolved_key
                    self.model_name = model_name or _env_model_override(cfg)
                    self.provider = cfg.name
                    return
            # Fallback: try auto-detect below

        # Auto-detect: find first provider with a valid API key
        for cfg in self._provider_chain:
            resolved_key = api_key or os.getenv(cfg.api_key_env, "")
            if resolved_key:
                self._active_provider = cfg
                self.api_key = resolved_key
                self.model_name = model_name or _env_model_override(cfg)
                self.provider = cfg.name
                return

        # No provider available — will return mock responses
        self.api_key = ""
        self.model_name = model_name or "mock"
        self.provider = "none"
        self._active_provider = None
        logger.warning("No LLM API key configured. Service will return mock responses.")

    @staticmethod
    def _find_provider_config(name: str) -> _ProviderConfig | None:
        """Find a provider config by name."""
        name_lower = name.lower()
        for cfg in _PROVIDER_CHAIN:
            if cfg.name == name_lower:
                return cfg
        return None

    def _next_fallback_provider(self) -> _ProviderConfig | None:
        """Get the next untried provider from the chain."""
        for cfg in self._provider_chain:
            if cfg.name not in self._tried_providers:
                key = os.getenv(cfg.api_key_env, "")
                if key:
                    return cfg
        return None

    def _switch_to_next_provider(self) -> bool:
        """Switch to the next available fallback provider. Returns True if switched."""
        self._tried_providers.add(self.provider)
        next_cfg = self._next_fallback_provider()
        if next_cfg:
            self._active_provider = next_cfg
            self.api_key = os.getenv(next_cfg.api_key_env, "")
            self.model_name = _env_model_override(next_cfg)
            self.provider = next_cfg.name
            logger.info(
                "Switching to fallback provider=%s, model=%s",
                self.provider,
                self.model_name,
            )
            return True
        return False

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    def generate_completion(
        self,
        prompt: str,
        system_instruction: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = 1000,
    ) -> str:
        """Generate text completion using the configured LLM provider.

        Automatically falls back to the next provider in the chain on failure.

        Args:
            prompt: The input user prompt.
            system_instruction: Optional system prompt to guide behavior.
            temperature: Sampling temperature for output generation.
            max_tokens: Maximum number of tokens to generate.

        Returns:
            The generated string response from the model.
        """
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        if self.provider == "none":
            logger.warning("No LLM provider available, returning mock response.")
            return f"[Mock LLM Response] Prompt: {prompt[:50]}..."

        logger.info(
            "Generating completion using provider=%s, model=%s",
            self.provider,
            self.model_name,
        )

        try:
            result = self._dispatch_to_provider(
                prompt=prompt,
                system_instruction=system_instruction,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            # Success clears the blacklist so transient failures on one call
            # don't permanently skip providers for the rest of a long run.
            self._tried_providers.clear()
            return result
        except Exception as err:
            logger.error(
                "Provider=%s failed: %s. Attempting fallback...",
                self.provider,
                err,
            )
            last_err: Exception = err
            while self._switch_to_next_provider():
                try:
                    return self._dispatch_to_provider(
                        prompt=prompt,
                        system_instruction=system_instruction,
                        temperature=temperature,
                        max_tokens=max_tokens,
                    )
                except Exception as next_err:
                    logger.error(
                        "Fallback provider=%s failed: %s. Continuing chain...",
                        self.provider,
                        next_err,
                    )
                    last_err = next_err
            raise last_err

    def _dispatch_to_provider(
        self,
        prompt: str,
        system_instruction: str | None,
        temperature: float,
        max_tokens: int | None,
    ) -> str:
        """Dispatch the request to the currently active provider."""
        if self.provider == "gemini":
            return self._generate_gemini(
                prompt=prompt,
                system_instruction=system_instruction,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        elif self.provider in ("opencode", "openrouter"):
            return self._generate_openai_compatible(
                prompt=prompt,
                system_instruction=system_instruction,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")

    def _generate_gemini(
        self,
        prompt: str,
        system_instruction: str | None,
        temperature: float,
        max_tokens: int | None,
    ) -> str:
        """Generate response via Google Gemini API."""
        import concurrent.futures

        if genai is None:
            raise ImportError("google.genai package not available")

        client = genai.Client(api_key=self.api_key)
        full_prompt = f"{system_instruction}\n\n{prompt}" if system_instruction else prompt

        def _gen() -> Any:
            return client.models.generate_content(
                model=self.model_name,
                contents=full_prompt,
            )

        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
            future = ex.submit(_gen)
            try:
                response = future.result(timeout=LLM_CALL_TIMEOUT_S)
            except concurrent.futures.TimeoutError:
                future.cancel()
                raise RuntimeError(f"Gemini call timed out after {LLM_CALL_TIMEOUT_S}s")

        return response.text.strip() if response.text else ""

    def _generate_openai_compatible(
        self,
        prompt: str,
        system_instruction: str | None,
        temperature: float,
        max_tokens: int | None,
    ) -> str:
        """Generate response via OpenAI-compatible API (OpenCode, OpenRouter)."""
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("openai package required for OpenAI-compatible providers")

        assert self._active_provider is not None
        client = OpenAI(
            api_key=self.api_key,
            base_url=self._active_provider.base_url,
            timeout=LLM_CALL_TIMEOUT_S,
            max_retries=0,
        )
        messages: list[dict[str, Any]] = []

        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})

        messages.append({"role": "user", "content": prompt})

        models_to_try = [self.model_name] + self._active_provider.fallback_models
        last_error: Exception | None = None

        for model in models_to_try:
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=messages,  # type: ignore[arg-type]
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                content = response.choices[0].message.content
                return content.strip() if content else ""
            except Exception as err:
                err_str = str(err)
                # 403 may mean the model slug exists but isn't accessible via API (e.g.
                # "only available on agentic harnesses") — skip without retry
                is_forbidden = "403" in err_str or "inaccessible" in err_str.lower()
                if is_forbidden:
                    logger.warning("Model %s permanently inaccessible (403), skipping.", model)
                    last_error = err
                    continue
                # 401 from OpenRouter usually means the model slug is no longer
                # available on the free tier ("not supported"). Skip without
                # retry to avoid wasting the next model's quota.
                is_unsupported = "401" in err_str and (
                    "not supported" in err_str.lower() or "modelerror" in err_str.lower()
                )
                if is_unsupported:
                    logger.warning("Model %s unsupported (401), skipping.", model)
                    last_error = err
                    continue
                # 429 = rate limit or quota exceeded — back off and retry up to 3 times
                is_rate_limit = (
                    "429" in err_str
                    or "rate limit" in err_str.lower()
                    or "quota exceeded" in err_str.lower()
                )
                if is_rate_limit:
                    if models_to_try.index(model) < len(models_to_try) - 1:
                        backoff = min(30, 2 ** (3 - models_to_try.index(model)))
                        logger.warning(
                            "Model %s hit rate limit (429), backing off %ds before retry.",
                            model,
                            backoff,
                        )
                        time.sleep(backoff)
                        last_error = err
                        continue
                    else:
                        last_error = err
                        continue
                logger.warning("Model %s failed: %s", model, err)
                last_error = err
                continue

        # All models exhausted — raise so caller switches to the next provider
        if last_error:
            raise last_error
        # Unreachable: every exception path above sets last_error. Kept as defensive
        # fallback in case a future refactoring introduces a non-exception exit.
        raise RuntimeError(f"All models failed for provider {self.provider}")  # pragma: no cover

    async def generate_text(
        self,
        prompt: str,
        system_instruction: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = 1000,
    ) -> str:
        """Alias for generate_completion (async-compatible wrapper)."""
        return self.generate_completion(
            prompt=prompt,
            system_instruction=system_instruction,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    async def classify_text(
        self,
        text: str,
        categories: list[str] | None = None,
        system_prompt: str | None = None,
    ) -> str:
        """Alias for generate_completion for classification tasks."""
        prompt = text
        if categories:
            prompt = "Classify into: " + ", ".join(categories) + "\n\n" + text
        return self.generate_completion(
            prompt=prompt,
            system_instruction=system_prompt,
        )

    def summarize(self, text: str, max_length: int = 200) -> str:
        """Summarize given text content using LLM.

        Args:
            text: The text content to summarize.
            max_length: Target word/token length for summary.

        Returns:
            Summarized string output.
        """
        system_prompt = (
            f"You are a concise summarizer. Summarize the text in under {max_length} words."
        )
        return self.generate_completion(prompt=text, system_instruction=system_prompt)

    async def summarize_release_notes(self, notes: str, max_length: int = 200) -> str:
        """Summarize release notes content using the LLM."""
        return self.summarize(text=notes, max_length=max_length)

    async def enrich_feature(
        self, feature: dict[str, Any], context: str | None = None
    ) -> dict[str, Any]:
        """Enrich a feature dictionary with additional LLM-derived details."""
        prompt = f"Enrich the following feature:\n{feature}"
        if context:
            prompt += f"\n\nContext:\n{context}"
        details = self.generate_completion(prompt=prompt)
        enriched = dict(feature)
        enriched["details"] = details
        enriched["enriched"] = True
        return enriched


# ---------------------------------------------------------------------------
# OpenRouter LLM Adapter (for Classification and Enrichment)
# ---------------------------------------------------------------------------


class OpenRouterLLMAdapter:
    """OpenRouter LLM adapter for classification and enrichment."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        base_url: str = "https://openrouter.ai/api/v1",
        timeout: float = 60.0,
    ) -> None:
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY", "")
        self.model = model or os.getenv("OPENROUTER_MODEL", "openrouter/free")
        self.base_url = base_url
        self.timeout = timeout
        self._client: OpenAI | None = None

        if not self.api_key:
            logger.warning("OpenRouter API key not configured")

    def _get_client(self) -> OpenAI:
        if self._client is None:
            self._client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
                timeout=self.timeout,
                max_retries=0,
            )
        return self._client

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    async def _complete(
        self,
        prompt: str,
        system_prompt: str,
        temperature: float = 0.2,
        max_tokens: int = 3000,
        response_format: dict[str, str] | None = None,
    ) -> str:
        """Generate completion with retry logic."""
        if not self.api_key:
            raise RuntimeError("OpenRouter API key not configured")

        client = self._get_client()
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ]

        kwargs: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if response_format:
            kwargs["response_format"] = response_format

        response = client.chat.completions.create(**kwargs)
        content = response.choices[0].message.content
        return content.strip() if content else ""

    async def classify_batch(
        self, features: list[str], categories: list[str] | None = None
    ) -> list[dict[str, Any]]:
        """Classify a batch of features."""
        results = []
        for feature in features:
            prompt = f"Feature: {feature}\n\nClassifique esta feature."
            try:
                response = await self._complete(
                    prompt=prompt,
                    system_prompt=CLASSIFICATION_SYSTEM_PROMPT,
                    response_format={"type": "json_object"},
                )
                data = json.loads(response)
                results.append(data)
            except Exception as e:
                logger.warning("Classification failed for '%s': %s", feature[:50], e)
                results.append(self._default_classification())

        return results

    async def enrich_category(
        self,
        category_name: str,
        features: list[str],
        classifications: dict[str, Any],
        locale: str,
    ) -> CategoryEnrichment:
        """Enrich a category with AI-generated details."""
        # Build classification summary
        class_summary = "\n".join(
            f"- {name}: impact={c.get('impact', 'medium')}, type={c.get('type', 'other')}"
            for name, c in classifications.items()
            if name in features
        )

        prompt = f"""Categoria: {category_name}
Features ({len(features)}):
{class_summary}

Gere enriquecimento para esta categoria."""

        try:
            response = await self._complete(
                prompt=prompt,
                system_prompt=ENRICHMENT_SYSTEM_PROMPT,
                response_format={"type": "json_object"},
                max_tokens=4000,
            )
            data = json.loads(response)
            return self._parse_category_enrichment(category_name, features, data, locale)
        except Exception as e:
            logger.warning("Category enrichment failed for %s: %s", category_name, e)
            return self._minimal_category_enrichment(category_name, features, locale)

    async def enrich_release(
        self,
        release_slug: str,
        category_enrichments: list[CategoryEnrichment],
        locale: str,
    ) -> ReleaseEnrichment:
        """Enrich a release with executive summary."""
        cat_summary = "\n".join(
            f"- {c.category_name}: {c.overview[:100]}..." for c in category_enrichments
        )

        prompt = f"""Release: {release_slug}
Categorias ({len(category_enrichments)}):
{cat_summary}

Gere enriquecimento executivo para este release."""

        try:
            response = await self._complete(
                prompt=prompt,
                system_prompt=RELEASE_ENRICHMENT_SYSTEM_PROMPT,
                response_format={"type": "json_object"},
                max_tokens=4000,
            )
            data = json.loads(response)
            return self._parse_release_enrichment(release_slug, category_enrichments, data, locale)
        except Exception as e:
            logger.warning("Release enrichment failed for %s: %s", release_slug, e)
            return self._minimal_release_enrichment(release_slug, category_enrichments, locale)

    def _default_classification(self) -> dict[str, Any]:
        return {
            "impact": "medium",
            "type": "other",
            "confidence": 0.1,
            "audience": "ambos",
            "priority": "opcional",
            "justification": "Classificação padrão (LLM indisponível)",
        }

    def _parse_category_enrichment(
        self,
        category_name: str,
        features: list[str],
        data: dict[str, Any],
        locale: str,
    ) -> CategoryEnrichment:
        from src.models.enrichment import FeatureEnrichment

        feature_enrichments = []
        for feat_data in data.get("feature_enrichments", []):
            feature_enrichments.append(
                FeatureEnrichment(
                    feature_name=feat_data.get("feature_name", ""),
                    summary=feat_data.get("summary", ""),
                    details=feat_data.get("details", ""),
                    business_context=feat_data.get("business_context", ""),
                    technical_context=feat_data.get("technical_context", ""),
                    migration_notes=feat_data.get("migration_notes", ""),
                    related_features=tuple(feat_data.get("related_features", [])),
                    tags=tuple(feat_data.get("tags", [])),
                    confidence=feat_data.get("confidence", 0.8),
                    locale=locale,
                )
            )

        return CategoryEnrichment(
            category_name=category_name,
            overview=data.get("overview", ""),
            key_themes=tuple(data.get("key_themes", [])),
            business_impact=data.get("business_impact", ""),
            adoption_guidance=data.get("adoption_guidance", ""),
            risk_assessment=data.get("risk_assessment", ""),
            feature_enrichments=tuple(feature_enrichments),
            locale=locale,
        )

    def _parse_release_enrichment(
        self,
        release_slug: str,
        category_enrichments: list[CategoryEnrichment],
        data: dict[str, Any],
        locale: str,
    ) -> ReleaseEnrichment:
        return ReleaseEnrichment(
            release_slug=release_slug,
            executive_summary=data.get("executive_summary", ""),
            strategic_themes=tuple(data.get("strategic_themes", [])),
            category_enrichments=tuple(category_enrichments),
            migration_checklist=tuple(data.get("migration_checklist", [])),
            locale=locale,
        )

    def _minimal_category_enrichment(
        self, category_name: str, features: list[str], locale: str
    ) -> CategoryEnrichment:
        from src.models.enrichment import FeatureEnrichment

        return CategoryEnrichment(
            category_name=category_name,
            overview=f"Categoria {category_name} com {len(features)} features.",
            key_themes=tuple(features[:5]),
            business_impact="Análise não disponível.",
            adoption_guidance="Consulte a documentação oficial.",
            risk_assessment="Avaliação não disponível.",
            feature_enrichments=tuple(
                FeatureEnrichment(
                    feature_name=name,
                    summary="",
                    locale=locale,
                )
                for name in features
            ),
            locale=locale,
        )

    def _minimal_release_enrichment(
        self,
        release_slug: str,
        category_enrichments: list[CategoryEnrichment],
        locale: str,
    ) -> ReleaseEnrichment:
        return ReleaseEnrichment(
            release_slug=release_slug,
            executive_summary=f"Release {release_slug} processado.",
            strategic_themes=tuple(c.category_name for c in category_enrichments[:10]),
            category_enrichments=tuple(category_enrichments),
            migration_checklist=(
                "Revisar notas oficiais",
                "Testar em sandbox",
                "Comunicar equipes",
            ),
            locale=locale,
        )


# ---------------------------------------------------------------------------
# Classification Adapters (implementing domain contracts)
# ---------------------------------------------------------------------------


class OpenRouterClassificationAdapter(ClassificationAdapter):
    """ClassificationAdapter implementation using OpenRouter."""

    def __init__(self, llm_adapter: OpenRouterLLMAdapter | None = None) -> None:
        self._llm = llm_adapter or OpenRouterLLMAdapter()

    @property
    def name(self) -> str:
        return "openrouter_classification"

    async def classify(
        self, features: list[str], categories: list[str] | None = None
    ) -> list[dict[str, Any]]:
        return await self._llm.classify_batch(features, categories)


class HeuristicClassificationAdapter(ClassificationAdapter):
    """Heuristic (keyword-based) classification adapter — no LLM required."""

    # Keyword rules: (pattern, impact, type, confidence)
    _RULES: ClassVar[list[tuple[str, str, str, float]]] = [
        (r"(?i)\b(security|vulnerability|cve|auth|xss|injection|mfa)\b", "high", "security", 0.8),
        (
            r"(?i)\b(performance|latency|speed|optimization|cache|throughput)\b",
            "high",
            "performance",
            0.7,
        ),
        (r"(?i)\b(deprecated|end.of.life|sunset|removal)\b", "high", "deprecation", 0.8),
        (
            r"(?i)\b(breaking|incompatible|migration|upgrade.required)\b",
            "high",
            "breaking_change",
            0.8,
        ),
        (r"(?i)\b(bug|fix|patch|hotfix|issue)\b", "medium", "bug_fix", 0.6),
        (r"(?i)\b(new|add|introduce|launch|feature)\b", "medium", "new_feature", 0.6),
        (r"(?i)\b(improve|enhance|update|extend)\b", "medium", "improvement", 0.5),
        (
            r"(?i)\b(api|integration|webhook|endpoint|rest|graphql|mulesoft)\b",
            "medium",
            "integration",
            0.6,
        ),
        (
            r"(?i)\b(ui|ux|interface|design|lightning|experience|accessibility)\b",
            "low",
            "ui_ux",
            0.5,
        ),
        (r"(?i)\b(agentforce|einstein|ai|llm|model)\b", "high", "new_feature", 0.7),
    ]

    @property
    def name(self) -> str:
        return "heuristic_classification"

    async def classify(
        self, features: list[str], categories: list[str] | None = None
    ) -> list[dict[str, Any]]:
        results = []
        for text in features:
            best = None
            best_conf = 0.0

            for pattern, impact, ftype, conf in self._RULES:
                if re.search(pattern, text) and conf > best_conf:
                    best_conf = conf
                    best = {"impact": impact, "type": ftype, "confidence": conf}

            if best:
                best["audience"] = "ambos"
                best["priority"] = "importante" if best["impact"] == "high" else "opcional"
                best["justification"] = (
                    f"Classificação heurística baseada em palavras-chave ({best_conf:.0%} confiança)"
                )
                results.append(best)
            else:
                results.append(
                    {
                        "impact": "medium",
                        "type": "other",
                        "confidence": 0.3,
                        "audience": "ambos",
                        "priority": "opcional",
                        "justification": "Classificação padrão (sem match de palavras-chave)",
                    }
                )

        return results


# ---------------------------------------------------------------------------
# Enrichment Adapters (implementing domain contracts)
# ---------------------------------------------------------------------------


class OpenRouterEnrichmentAdapter(EnrichmentAdapter):
    """EnrichmentAdapter implementation using OpenRouter."""

    def __init__(self, llm_adapter: OpenRouterLLMAdapter | None = None) -> None:
        self._llm = llm_adapter or OpenRouterLLMAdapter()

    @property
    def name(self) -> str:
        return "openrouter_enrichment"

    async def enrich_category(
        self,
        category_name: str,
        features: list[str],
        classifications: dict[str, Any],
        locale: str,
    ) -> CategoryEnrichment:
        return await self._llm.enrich_category(category_name, features, classifications, locale)

    async def enrich_release(
        self,
        release_slug: str,
        category_enrichments: list[CategoryEnrichment],
        locale: str,
    ) -> ReleaseEnrichment:
        return await self._llm.enrich_release(release_slug, category_enrichments, locale)


# ---------------------------------------------------------------------------
# Optional: Gemini Adapters (when google.genai is available)
# ---------------------------------------------------------------------------


class GeminiLLMAdapter:
    """Google Gemini LLM adapter (optional)."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
    ) -> None:
        if not _HAS_GENAI:
            raise ImportError("google.genai package not available")
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY", "")
        self.model = model or os.getenv("GEMINI_MODEL", "gemini-3.6-flash")

    async def _complete(self, prompt: str, system_prompt: str) -> str:
        client = genai.Client(api_key=self.api_key)  # type: ignore[arg-type]
        full_prompt = f"{system_prompt}\n\n{prompt}"
        response = client.models.generate_content(
            model=self.model,  # type: ignore[arg-type]
            contents=full_prompt,
        )
        return response.text.strip() if response.text else ""


class GeminiClassificationAdapter(ClassificationAdapter):
    """ClassificationAdapter using Gemini."""

    def __init__(self, llm_adapter: GeminiLLMAdapter | None = None) -> None:
        if not _HAS_GENAI:
            raise ImportError("google.genai not available")
        self._llm = llm_adapter or GeminiLLMAdapter()

    @property
    def name(self) -> str:
        return "gemini_classification"

    async def classify(
        self, features: list[str], categories: list[str] | None = None
    ) -> list[dict[str, Any]]:
        results = []
        for feature in features:
            prompt = f"Feature: {feature}\n\nClassifique."
            try:
                response = await self._llm._complete(prompt, CLASSIFICATION_SYSTEM_PROMPT)
                data = json.loads(response)
                results.append(data)
            except Exception as e:
                logger.warning("Gemini classification failed: %s", e)
                results.append({"impact": "medium", "type": "other", "confidence": 0.1})
        return results
