# Executando o Pipeline

Fluxo completo de execução do pipeline ETL de Salesforce Release Notes.

## Visão Geral do Fluxo

```
Detectar Nova Release → Scraper (Playwright) → Parser (HTML) → Classifier (LLM)
    → Generator (Markdown) → Atualizar README → Notificações → GitHub Pages
```

## 1. Detecção de Nova Release

O pipeline detecta automaticamente novas release notes verificando a página principal da Salesforce Help.

```python
from src.main import run_pipeline, PipelineConfig

# Configuração do pipeline
config = PipelineConfig(
    dry_run=False,              # False = executar mudanças reais
    release_filter=None,        # None = todas as releases, ou "summer_26"
    log_level="INFO",           # DEBUG, INFO, WARNING, ERROR
)
```

## 2. Execução Local

```bash
# Modo normal (gera releases, atualiza README, notifica)
uv run python src/main.py

# Modo dry-run (valida sem escrever arquivos)
uv run python src/main.py --dry-run

# Modo debug (logs detalhados)
LOG_LEVEL=DEBUG uv run python src/main.py
```

## 3. Saídas do Pipeline

Após execução bem-sucedida, o pipeline gera:

| Artefato | Localização | Descrição |
|----------|-------------|-----------|
| Markdown por categoria | `releases/<slug>/<categoria>.md` | Documentação de cada categoria |
| Meta.json | `releases/<slug>.meta.json` | Metadados da release |
| Resumo executive | `releases/<slug>/executive-summary.md` | Resumo AI da release |
| Resumo por categoria | `releases/<slug>/<categoria>-summary.md` | Resumo AI porcategoria |
| README atualizado | `README.md`, `README.en.md` | Badges e lista de releases |
| Changelog | Gerado pelo LLM | Histórico de mudanças |

## 4. Variáveis de Ambiente

| Variável | Obrigatória | Padrão | Descrição |
|----------|-------------|--------|-----------|
| `OPENAI_API_KEY` | Não* | — | Chave OpenAI |
| `GOOGLE_API_KEY` | Não* | — | Chave Google Gemini |
| `OPENCODE_API_KEY` | Não* | — | Chave OpenCode |
| `MIMOCODE_API_KEY` | Não* | — | Chave MiMoCode |
| `LOG_LEVEL` | Não | `INFO` | Nível de log |
| `LOG_FORMAT` | Não | `text` | Formato: `text` ou `json` |
| `SENTRY_DSN` | Não | — | DSN do Sentry para error tracking |

*Pelo menos uma chave LLM é necessária.

## 5. Execução no CI/CD

O pipeline é executado automaticamente via GitHub Actions:

- **Push na branch main** — Execução incremental
- **Cron a cada 6 horas** — Execução completa (`schedule: 17 */6 * * *`)
- **Manual** — Via `workflow_dispatch` com modos `incremental`, `full` ou `audit`

Ver [Operações de Workflow](../maintenance/workflow-operations.md) para detalhes.

## 6. Troubleshooting

| Sintoma | Ação |
|---------|------|
| Scraper falha | Ver [Runbook — Falha no Scraper](../runbooks/scraper-failure.md) |
| Parser falha | Rodar snapshot tests: `uv run pytest tests/test_snapshot.py -v` |
| LLM falha | Verificar API keys e quotas nos providers |
| GitHub Actions falha | Ver [Runbook — Falha no GitHub Actions](../runbooks/github-actions-failure.md) |
| Build do site falha | Ver [Runbook — Falha no MkDocs Build](../runbooks/mkdocs-build-failure.md) |
