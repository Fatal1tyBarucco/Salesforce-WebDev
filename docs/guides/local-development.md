# Desenvolvimento Local

Guia de configuração e operação do ambiente de desenvolvimento local.

## Setup

Instale as dependências do projeto:

```bash
uv sync --extra dev
```

Para instalar apenas o ambiente de execução (sem ferramentas de desenvolvimento):

```bash
uv sync
```

## Execute Pipeline

```bash
uv run python src/main.py
```

## Execute Tests

```bash
uv run pytest
```

## Validate Quality

```bash
uv run ruff check .
uv run black --check .
uv run mypy src/
```

## Instalar Navegador Playwright

O scraper utiliza Playwright para renderizar a Salesforce Help (SPA JavaScript). Instale o navegador Chromium:

```bash
uv run playwright install chromium
```

## Variáveis de Ambiente

| Variável | Obrigatória | Padrão | Descrição |
|----------|-------------|--------|-----------|
| `OPENAI_API_KEY` | Não* | — | Chave da API OpenAI |
| `GOOGLE_API_KEY` | Não* | — | Chave do Google Gemini |
| `OPENCODE_API_KEY` | Não* | — | Chave OpenCode |
| `MIMOCODE_API_KEY` | Não* | — | Chave MiMoCode |
| `LOG_LEVEL` | Não | `INFO` | Nível de log (DEBUG, INFO, WARNING, ERROR) |
| `LOG_FORMAT` | Não | `text` | Formato do log: `text` ou `json` |

*Pelo menos uma chave LLM é necessária para funcionalidades de IA.

## Execução em Modo Dry-Run

Para validar o pipeline sem gerar efeitos colaterais (sem escrever arquivos, sem notificações):

```bash
uv run python src/main.py --dry-run
```

## Debugging

Para logs detalhados com correlation_id:

```bash
LOG_LEVEL=DEBUG uv run python src/main.py
```

Para logs em formato JSON (integração com sistemas de agregação):

```bash
LOG_FORMAT=json LOG_LEVEL=DEBUG uv run python src/main.py
```
