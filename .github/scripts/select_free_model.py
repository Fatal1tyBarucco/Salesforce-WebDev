"""Dynamically select a healthy free-tier LLM model at the start of every run.

Free-tier models rotate between healthy and broken (503 upstream, stalls,
quota exhaustion) throughout the day, so hardcoding one model makes scheduled
runs flaky. This script probes the free-model pools — OpenRouter first, then
OpenCode, matching the provider priority in ``src/llm_service.py`` — with a
tiny completion request and exports the first healthy provider/model pair to
the GitHub Actions environment via ``$GITHUB_ENV`` / ``$GITHUB_OUTPUT``:

    LLM_PROVIDER=<provider>
    <PROVIDER>_MODEL=<model>        (OPENROUTER_MODEL / OPENCODE_MODEL)

``src/llm_service.py`` honors both, so every run starts on a model that
answered a live probe minutes earlier. Gemini is deliberately never probed:
its free tier allows only ~20 requests/day, so it stays the untouched last
resort of the built-in fallback chain.

If nothing is healthy the script exits 0 WITHOUT exporting anything — the
pipeline then falls back to the service's own provider/model sweep.

Stdlib only; safe to run with ``python3`` or ``uv run python``.
"""

import json
import os
import sys
import time
import urllib.request
from typing import TypedDict

# Per-model probe cap. A dead model answers 503 quickly; a stalling one must
# not eat the whole budget before healthier candidates are tried.
PROBE_TIMEOUT_S = int(os.environ.get("FREE_MODEL_PROBE_TIMEOUT_S") or 20)

# Whole-run probe budget. Keeps the workflow step well under a couple of
# minutes even when every candidate is down.
PROBE_BUDGET_S = int(os.environ.get("FREE_MODEL_PROBE_BUDGET_S") or 90)

PROBE_PROMPT = "Reply with the single word: ok"


class ModelPool(TypedDict):
    """A provider's free-model candidate pool."""

    provider: str
    key_env: str
    model_env: str
    base_url: str
    models: list[str]


# Pools mirror src/llm_service.py (service order) plus the extra free Zen
# models maintained in .github/scripts/llm_fallback.py.
POOLS: list[ModelPool] = [
    ModelPool(
        provider="openrouter",
        key_env="OPENROUTER_API_KEY",
        model_env="OPENROUTER_MODEL",
        base_url="https://openrouter.ai/api/v1",
        models=[
            "openrouter/free",
            "google/gemma-4-31b-it:free",
            "meta-llama/llama-4-scout:free",
            "qwen/qwen-3-coder:free",
            "mistralai/mistral-nemo:free",
            "deepseek/deepseek-chat-v3:free",
            "anthropic/claude-3-haiku:free",
        ],
    ),
    ModelPool(
        provider="opencode",
        key_env="OPENCODE_API_KEY",
        model_env="OPENCODE_MODEL",
        base_url="https://opencode.ai/zen/v1",
        models=[
            "ling-3.0-flash-free",
            "ling-3.0-tiny-free",
            "nemotron-3-ultra-free",
            "north-mini-code-free",
            "laguna-s-2.1-free",
            "longcat-2.0-free",
            "mus-e-spark-1.2-contributor-free",
            "x-preview-f-free",
            "glm-5-free",
            "deepseek-v4-flash-free",
            "kimi-k2.5-free",
            "minimax-m2.5-free",
        ],
    ),
]


def _rotate(models: list[str], offset: int) -> list[str]:
    """Rotate the pool so each run starts on a different candidate.

    Deterministic per run (``GITHUB_RUN_ID``), which spreads probe load and
    start preference across models instead of always hammering the first one.
    """
    if not models:
        return []
    start = offset % len(models)
    return models[start:] + models[:start]


def probe_model(base_url: str, api_key: str, model: str) -> None:
    """Send a minimal completion request. Raises when the model is unhealthy."""
    payload = json.dumps(
        {
            "model": model,
            "messages": [{"role": "user", "content": PROBE_PROMPT}],
            "temperature": 0,
            "max_tokens": 8,
            "stream": False,
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        base_url.rstrip("/") + "/chat/completions",
        data=payload,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(request, timeout=PROBE_TIMEOUT_S) as response:
        body = json.loads(response.read().decode("utf-8"))
    choices = body.get("choices") or [{}]
    text = (choices[0].get("message") or {}).get("content") or ""
    if not text.strip():
        raise RuntimeError("empty completion")


def _append_github_file(var: str, lines: list[str]) -> None:
    """Append ``key=value`` lines to a GitHub Actions file (if set)."""
    path = os.environ.get(var)
    if not path:
        return
    with open(path, "a", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")


def main() -> int:
    """Probe the pools and export the first healthy provider/model pair."""
    offset = int(os.environ.get("GITHUB_RUN_ID") or "0")
    deadline = time.monotonic() + PROBE_BUDGET_S
    probed = 0

    for pool in POOLS:
        provider = pool["provider"]
        key_env = pool["key_env"]
        model_env = pool["model_env"]
        base_url = pool["base_url"]
        api_key = os.environ.get(key_env, "")
        if not api_key:
            print(f"[select-free-model] {provider}: {key_env} not set — skipping pool")
            continue

        for model in _rotate(pool["models"], offset):
            if time.monotonic() >= deadline:
                print("[select-free-model] probe budget exhausted — stopping")
                break
            probed += 1
            try:
                probe_model(base_url, api_key, model)
            except (OSError, ValueError, RuntimeError) as err:
                # OSError covers URLError/HTTPError/TimeoutError, ValueError
                # covers malformed JSON responses.
                print(f"[select-free-model] ✗ {provider}/{model}: {err}")
                continue
            print(f"[select-free-model] ✓ healthy: {provider}/{model}")
            _append_github_file("GITHUB_OUTPUT", [f"provider={provider}", f"model={model}"])
            _append_github_file("GITHUB_ENV", [f"LLM_PROVIDER={provider}", f"{model_env}={model}"])
            print(f"[select-free-model] exported LLM_PROVIDER={provider}, {model_env}={model}")
            return 0

    print(
        f"[select-free-model] no healthy free model found after {probed} probe(s) — "
        "keeping defaults (service fallback chain will sweep every pool)."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
