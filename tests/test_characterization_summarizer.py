"""Testes de caracterização do summarizer, do bloco de release do README e dos
validadores de cache (.summary_cache.json / .meta.json).

Congela em `tests/golden/`:
- `summarizer/cache_hit_summary.json` + `summarizer/cache_hit.md`:
  contrato do ReleaseSummary lido do cache válido (sem LLM);
- `summarizer/fallback_summary.json` + `summarizer/fallback.md`:
  resumo de fallback 100% determinístico quando o LLM devolve None;
- `summarizer/llm_contract_summary.json` + `summarizer/llm_contract.md`:
  contrato JSON→ReleaseSummary com o provider substituído por stub fixo
  (congelamos o parser/contrato, não o texto de um modelo real);
- `summarizer/readme_block_pt.md` / `readme_block_en.md`:
  saída de `_build_release_block()` (release atual + antiga);
- `summarizer/readme_pt_updated.md`: README completo após `_update_single_readme()`;
- `main/summary_cache_validation.json`: tabela de casos de `_validate_summary_cache()`;
- `main/load_meta_cases.json`: casos de `_load_meta_for_release()`.

Todos os arquivos ficam em tmp_path. Regenerar goldens:
CHAR_GOLDEN_UPDATE=1 uv run pytest tests/test_characterization_summarizer.py
"""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

import pytest
from freezegun import freeze_time

import src.main as main_module
from src.release_docs import (
    _build_release_block,
    _slugify_category,
    _update_single_readme,
)
from src.release_summarizer import ReleaseSummarizer
from tests.factories import make_release, make_release_metadata
from tests.test_characterization_golden import (
    FROZEN_TIMESTAMP,
    assert_matches_golden,
    assert_matches_golden_json,
)

# Resposta fixa do "LLM" para o caso de contrato. O texto é autoral (escrito
# por este teste), portanto determinístico — o que se congela é o contrato
# JSON → ReleaseSummary, não a geração de um modelo.
LLM_CONTRACT_RESPONSE: str = (
    "```json\n"
    + json.dumps(
        {
            "executive_summary": (
                "Resumo executativo vindo do contrato LLM (stub): a release Winter '26 "
                "aporta automação e segurança para administradores e desenvolvedores."
            ),
            "business_impact": (
                "Impacto de negócio vindo do contrato LLM (stub): redução de tarefas "
                "manuais e maior adoção de fluxos automatizados."
            ),
            "strategic_themes": ["AI-First", "Automação", "Compliance & Security"],
            "top_categories": [
                {
                    "name": "Desenvolvimento",
                    "feature_count": 2,
                    "percentage": 50.0,
                    "top_feature": "Recurso Um",
                    "theme": "Ferramentas de desenvolvimento",
                },
                {
                    "name": "Vendas",
                    "feature_count": 2,
                    "percentage": 50.0,
                    "top_feature": "Venda Feature 1",
                    "theme": "Automação de vendas",
                },
            ],
            "category_summaries": {
                "Desenvolvimento": "Resumo autoral do contrato LLM para Desenvolvimento.",
                "Vendas": "Resumo autoral do contrato LLM para Vendas.",
            },
            "migration_notes": "Notas de migração do contrato LLM: revisar fluxos antigos.",
        },
        ensure_ascii=False,
    )
    + "\n```"
)


class _StubLLM:
    """Substituto determinístico do LLMService (apenas contrato de saída)."""

    def __init__(self, response: str | None) -> None:
        self._response = response
        self.calls: list[tuple[str, str]] = []

    async def generate_text(self, user_prompt: str, system_prompt: str) -> str | None:
        self.calls.append((user_prompt, system_prompt))
        return self._response


def _category_md(name: str, features: list[str]) -> str:
    """Markdown de categoria no formato produzido por _generate_release_files()."""
    lines = [
        f"## {name}",
        "",
        f"> **{len(features)} recursos**",
        "",
        "| Recurso | Usuários | Admins/Devs | Config | Contato | Docs |",
        "| :--- | :---: | :---: | :---: | :---: | :---: |",
    ]
    for feature in features:
        lines.append(f"| **{feature}** | ✅ | ✅ | ❌ | ❌ | |")
    lines.append("")
    return "\n".join(lines)


def _valid_cache(prefix: str) -> dict[str, Any]:
    """Cache de resumo válido segundo as 4 checagens de validação atuais."""
    return {
        "executive_summary": (
            f"Resumo executativo determinístico ({prefix}): a release consolida "
            "automação, segurança, inteligência artificial e experiência do "
            "desenvolvedor no ecossistema Salesforce para administradores, "
            "desenvolvedores e times de vendas."
        ),
        "business_impact": f"Impacto de negócio determinístico ({prefix}).",
        "strategic_themes": ["AI-First", "Automação", "Segurança"],
        "migration_notes": "Migrar fluxos antigos para a API nova antes do upgrade.",
        "category_summaries": {
            "Desenvolvimento": f"Resumo por categoria ({prefix}) de Desenvolvimento.",
            "Vendas": f"Resumo por categoria ({prefix}) de Vendas.",
        },
        "fallback": False,
    }


def _write_release_dir(
    releases_dir: Path,
    meta: dict[str, Any],
    cache: dict[str, Any] | None = None,
    cache_en: dict[str, Any] | None = None,
    md_features: dict[str, list[str]] | None = None,
) -> Path:
    """Materializa releases/{slug}/ com .meta.json, caches e .md de categoria.

    `md_features` mapeia nome de categoria pt_BR → features; o arquivo segue o
    padrão de produção (pt_BR: slugified pt_BR, en_US: ENGLISH_CATEGORY_SLUGS).
    """
    from src.config import ENGLISH_CATEGORY_SLUGS

    slug = str(meta["slug"])
    release_dir = releases_dir / slug
    (release_dir / "pt_BR").mkdir(parents=True, exist_ok=True)
    (release_dir / "en_US").mkdir(parents=True, exist_ok=True)
    (release_dir / ".meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    if cache is not None:
        (release_dir / ".summary_cache.json").write_text(
            json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    if cache_en is not None:
        (release_dir / ".summary_cache_en.json").write_text(
            json.dumps(cache_en, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    for category_name, features in (md_features or {}).items():
        # pt_BR file with slugified Portuguese name
        pt_slug = f"{_slugify_category(category_name)}.md"
        (release_dir / "pt_BR" / pt_slug).write_text(
            _category_md(category_name, features), encoding="utf-8"
        )
        # en_US file with English slug
        en_slug = (
            f"{ENGLISH_CATEGORY_SLUGS.get(category_name, _slugify_category(category_name))}.md"
        )
        (release_dir / "en_US" / en_slug).write_text(
            _category_md(category_name, features), encoding="utf-8"
        )
    return release_dir


def _make_summarizer(releases_dir: Path, response: str | None) -> ReleaseSummarizer:
    return ReleaseSummarizer(base_dir=str(releases_dir), llm=_StubLLM(response))  # type: ignore[arg-type]


def _summer_meta() -> dict[str, Any]:
    release = make_release(name="Summer '26", release_id=262, slug="summer_26")
    return make_release_metadata(
        release=release, total_features=8, categories=["Desenvolvimento", "Vendas"]
    )


def _winter_meta() -> dict[str, Any]:
    release = make_release(name="Winter '26", release_id=258, slug="winter_26")
    return make_release_metadata(
        release=release, total_features=8, categories=["Desenvolvimento", "Vendas"]
    )


def _spring_meta() -> dict[str, Any]:
    release = make_release(name="Spring '26", release_id=260, slug="spring_26")
    return make_release_metadata(
        release=release, total_features=8, categories=["Desenvolvimento", "Vendas"]
    )


# ---------------------------------------------------------------------------
# summarize(): cache válido, fallback sem LLM e contrato do provider
# ---------------------------------------------------------------------------


async def test_summarize_cache_hit_matches_golden(tmp_path: Path) -> None:
    """Cache válido → ReleaseSummary do cache + to_markdown(), sem tocar o LLM."""
    releases_dir = tmp_path / "releases"
    with freeze_time(FROZEN_TIMESTAMP):
        meta = _summer_meta()
    _write_release_dir(
        releases_dir,
        meta,
        cache=_valid_cache("pt"),
        md_features={
            "Desenvolvimento": ["Recurso Um", "Recurso Dois"],
            "Vendas": ["Venda Feature 1", "Venda Feature 2"],
        },
    )

    stub = _StubLLM(None)
    summarizer = ReleaseSummarizer(base_dir=str(releases_dir), llm=stub)  # type: ignore[arg-type]
    summary = await summarizer.summarize("summer_26")
    assert summary is not None
    assert stub.calls == [], "cache válido não deve chamar o LLM"

    assert_matches_golden_json(asdict(summary), "summarizer/cache_hit_summary.json")
    assert_matches_golden(summarizer.to_markdown(summary), "summarizer/cache_hit.md")


async def test_summarize_fallback_without_llm_matches_golden(tmp_path: Path) -> None:
    """Sem cache e com LLM indisponível → _generate_fallback_summary() congelado."""
    releases_dir = tmp_path / "releases"
    with freeze_time(FROZEN_TIMESTAMP):
        meta = _spring_meta()
    _write_release_dir(
        releases_dir,
        meta,
        md_features={
            "Desenvolvimento": ["Recurso Um", "Recurso Dois"],
            "Vendas": ["Venda Feature 1", "Venda Feature 2"],
        },
    )

    summarizer = _make_summarizer(releases_dir, response=None)
    summary = await summarizer.summarize("spring_26")
    assert summary is not None
    assert summary.confidence == 0.7, "fallback atual fixa confiança 0.7"

    assert_matches_golden_json(asdict(summary), "summarizer/fallback_summary.json")
    assert_matches_golden(summarizer.to_markdown(summary), "summarizer/fallback.md")


async def test_summarize_llm_contract_matches_golden(tmp_path: Path) -> None:
    """Provider stubado devolve JSON fixo → contrato JSON→ReleaseSummary congelado."""
    releases_dir = tmp_path / "releases"
    with freeze_time(FROZEN_TIMESTAMP):
        meta = _winter_meta()
    _write_release_dir(
        releases_dir,
        meta,
        md_features={
            "Desenvolvimento": ["Recurso Um", "Recurso Dois"],
            "Vendas": ["Venda Feature 1", "Venda Feature 2"],
        },
    )

    stub = _StubLLM(LLM_CONTRACT_RESPONSE)
    summarizer = ReleaseSummarizer(base_dir=str(releases_dir), llm=stub)  # type: ignore[arg-type]
    summary = await summarizer.summarize("winter_26")
    assert summary is not None
    assert len(stub.calls) == 1, "provider deve ser chamado exatamente 1 vez"

    assert_matches_golden_json(asdict(summary), "summarizer/llm_contract_summary.json")
    assert_matches_golden(summarizer.to_markdown(summary), "summarizer/llm_contract.md")


async def test_summarize_missing_release_returns_none(tmp_path: Path) -> None:
    """Release inexistente no disco → None (sem exceção, sem LLM)."""
    summarizer = _make_summarizer(tmp_path / "releases", response=None)
    assert await summarizer.summarize("release_que_nao_existe") is None


# ---------------------------------------------------------------------------
# README: _build_release_block() e _update_single_readme()
# ---------------------------------------------------------------------------

README_BEFORE: str = """# Salesforce Release Notes

Intro anterior à seção de releases.
## 📋 Releases Disponíveis
conteúdo antigo que será substituído

## 📌 Como Contribuir
Texto depois da seção de releases.
"""


def _block_fixtures(releases_dir: Path) -> list[dict[str, Any]]:
    """Dois releases em disco (mais novo primeiro) com caches pt/en válidos."""
    with freeze_time(FROZEN_TIMESTAMP):
        summer_meta = _summer_meta()
        winter_meta = _winter_meta()
    for meta, prefix in ((summer_meta, "summer"), (winter_meta, "winter")):
        _write_release_dir(
            releases_dir,
            meta,
            cache=_valid_cache(f"{prefix} pt"),
            cache_en=_valid_cache(f"{prefix} en"),
            md_features={
                "Desenvolvimento": ["Recurso Um", "Recurso Dois"],
                "Vendas": ["Venda Feature 1", "Venda Feature 2"],
            },
        )
    return [summer_meta, winter_meta]


async def test_build_release_block_matches_golden(tmp_path: Path) -> None:
    """Bloco de releases do README (pt_BR e en_US) com release atual + antiga."""
    releases_dir = tmp_path / "releases"
    metas = _block_fixtures(releases_dir)
    summarizer = _make_summarizer(releases_dir, response=None)

    block_pt = await _build_release_block(metas, "pt_BR", summarizer)
    block_en = await _build_release_block(metas, "en_US", summarizer)

    assert_matches_golden(block_pt, "summarizer/readme_block_pt.md")
    assert_matches_golden(block_en, "summarizer/readme_block_en.md")


async def test_update_single_readme_output_matches_golden(tmp_path: Path) -> None:
    """Substituição da seção de releases no README com limit=1 + bloco de arquivo."""
    releases_dir = tmp_path / "releases"
    metas = _block_fixtures(releases_dir)
    summarizer = _make_summarizer(releases_dir, response=None)

    readme_path = tmp_path / "README.md"
    readme_path.write_text(README_BEFORE, encoding="utf-8")

    await _update_single_readme(readme_path, metas, "pt_BR", summarizer, limit=1, all_metas=metas)

    assert_matches_golden(
        readme_path.read_text(encoding="utf-8"), "summarizer/readme_pt_updated.md"
    )


# ---------------------------------------------------------------------------
# Validadores de cache/meta em src/main.py
# ---------------------------------------------------------------------------

VALIDATE_CASES: list[dict[str, Any]] = [
    {
        "case": "cache_valido",
        "meta": {"total_features": 8, "categories": [{"name": "A"}, {"name": "B"}]},
        "cache": {
            "executive_summary": "Resumo com tamanho normal para release pequena.",
            "category_summaries": {"A": "sa", "B": "sb"},
        },
    },
    {
        "case": "exec_diz_zero_recursos_mas_meta_tem_dados",
        "meta": {"total_features": 8, "categories": [{"name": "A"}, {"name": "B"}]},
        "cache": {
            "executive_summary": "A release tem 0 novos recursos nesta versão.",
            "category_summaries": {"A": "sa", "B": "sb"},
        },
    },
    {
        "case": "meta_com_categorias_mas_cache_sem_summaries",
        "meta": {"total_features": 8, "categories": [{"name": "A"}, {"name": "B"}]},
        "cache": {"executive_summary": "Resumo normal.", "category_summaries": {}},
    },
    {
        "case": "cache_com_menos_metade_das_categorias",
        "meta": {
            "total_features": 40,
            "categories": [{"name": "A"}, {"name": "B"}, {"name": "C"}, {"name": "D"}],
        },
        "cache": {
            "executive_summary": "Resumo normal.",
            "category_summaries": {"A": "sa"},
        },
    },
    {
        "case": "exec_curta_para_release_grande",
        "meta": {"total_features": 200, "categories": [{"name": "A"}]},
        "cache": {
            "executive_summary": "Curto demais.",
            "category_summaries": {"A": "sa"},
        },
    },
    {
        "case": "meta_vazia_cache_qualquer",
        "meta": {},
        "cache": {
            "executive_summary": "Resumo sem meta.",
            "category_summaries": {"A": "sa"},
        },
    },
    {
        "case": "frase_zero_recursos_mas_meta_total_zero",
        "meta": {"total_features": 0, "categories": []},
        "cache": {
            "executive_summary": "A release tem 0 novos recursos nesta versão.",
            "category_summaries": {"A": "sa"},
        },
    },
]


def test_validate_summary_cache_cases_match_golden() -> None:
    """Congela a tabela de decisão de _validate_summary_cache()."""
    results = [
        {
            "case": case["case"],
            "valid": main_module._validate_summary_cache(case["cache"], case["meta"], "summer_26"),
        }
        for case in VALIDATE_CASES
    ]
    assert_matches_golden_json(results, "main/summary_cache_validation.json")


async def test_load_meta_for_release_cases_match_golden(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Congela _load_meta_for_release(): válido, JSON corrompido e ausente."""
    releases_dir = tmp_path / "releases"
    monkeypatch.setattr(main_module, "RELEASES_DIR", str(releases_dir))

    with freeze_time(FROZEN_TIMESTAMP):
        meta = _summer_meta()
    release_dir = releases_dir / "summer_26"
    release_dir.mkdir(parents=True, exist_ok=True)
    (release_dir / ".meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    broken_dir = releases_dir / "broken_release"
    broken_dir.mkdir(parents=True, exist_ok=True)
    (broken_dir / ".meta.json").write_text("{ json inválido", encoding="utf-8")

    payload = {
        "valid": main_module._load_meta_for_release("summer_26"),
        "corrupt": main_module._load_meta_for_release("broken_release"),
        "missing": main_module._load_meta_for_release("nao_existe"),
    }
    assert_matches_golden_json(payload, "main/load_meta_cases.json")
