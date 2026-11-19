---
name: test-conventions
description: Convenções de testes para Salesforce-WebDev
paths:
  - "tests/**/*.py"
---

# Convenções de Testes

## Estrutura
- `tests/test_*.py` — testes unitários/integração
- `tests/test_characterization_*.py` — golden files (determinísticos, byte-exatos)
- `tests/test_snapshot.py` — syrupy snapshots (não determinísticos)
- `tests/conftest.py` — fixtures globais (stub openai/google, isolated_cwd, freeze_time)
- `tests/factories.py` — 8 factory functions (`make_release`, `make_topic_tree`, etc.)
- `tests/golden/` — JSON/MD versionados (comportamento congelado)
- `tests/fixtures/golden/` — .meta.json, .summary_cache.json, .md de releases reais

## Regras Obrigatórias
1. **Determinístico**: sem rede, sem relógio real (`freezegun`), sem LLM real (stubs/mocks em `conftest.py`)
2. **Isolado**: `tmp_path` para testes que escrevem arquivos (ex.: `generate_ai_reports_async` usa `isolated_cwd` fixture)
3. **Factories**: use `make_release`, `make_topic_tree`, `make_toc_html`, `make_feature_impact_text`, etc.
4. **Golden files**: `assert_matches_golden(output, "path/to/golden.json")` — regenere só com `CHAR_GOLDEN_UPDATE=1`
5. **Syrupy**: para snapshots LLM não determinísticos — `snapshot.assert_match(output)`
6. **pytest-asyncio**: `asyncio_mode = "auto"` no pyproject.toml
7. **Timeout**: `--timeout=120` global; testes lentos (>30s) marcam com `@pytest.mark.slow`
8. **Cobertura**: ≥95% branch coverage — gate obrigatório

## Executando Testes
```bash
# Rápido (sem syrupy)
uv run pytest tests/ -q

# Completo (com syrupy, coverage)
uv pip install "syrupy>=4.9.0,<5" && uv run pytest tests/ --cov=src --cov-fail-under=95

# Atualizar golden files (apenas quando comportamento muda intencionalmente)
CHAR_GOLDEN_UPDATE=1 uv run pytest tests/test_characterization_*.py -q

# Atualizar snapshots syrupy
uv run pytest tests/test_snapshot.py --snapshot-update
```

## O que NÃO Fazer
- Não edite golden files à mão — são byte-exatos
- Não commite `NOTIFICATION_DIGEST.md`, `DIFF_REPORT.md`, `CHANGELOG.md` gerados em testes
- Não adicione `pytest-syrupy` ao `pyproject.toml` (rebaixa pytest para 8.4.2)
- Não use rede real ou LLM real em testes
