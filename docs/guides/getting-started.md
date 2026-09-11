# Quickstart — Primeiros Passos

Configuração mínima para rodar o pipeline de extração e documentação em 5 minutos.

## Pré-requisitos

- Python 3.13 ou superior (o projeto usa `uv` para gerenciamento)
- Git
- Conta no GitHub (para clonar o repositório)
- Chave LLM (opcional — OpenAI, Google Gemini, OpenCode ou MiMoCode)

## Instalação

### 1. Clonar o repositório

```bash
git clone https://github.com/Fatal1tyBarucco/Salesforce-WebDev.git
cd Salesforce-WebDev
```

### 2. Instalar dependências com uv

```bash
# Instala todas as dependências, incluindo ferramentas de desenvolvimento
uv sync --extra dev

# Se quiser apenas o ambiente de execução (sem lint/test tools):
# uv sync
```

### 3. Instalar navegador Playwright

O scraper usa Playwright para renderizar a Salesforce Help (SPA JavaScript).

```bash
uv run playwright install chromium
```

## Execução Rápida

### Executar o pipeline completo

```bash
uv run python src/main.py
```

### Executar em modo dry-run (sem efeitos colaterais)

```bash
uv run python src/main.py --dry-run
```

### Executar testes

```bash
uv run pytest
```

### Verificar cobertura de testes

```bash
uv run pytest --cov=src --cov-fail-under=95
```

### Validar qualidade de código

```bash
uv run ruff check .
uv run black --check .
uv run mypy src/
```

## Configuração de API Keys

O pipeline usa LLMs para classificação, resumos e relatórios. Configure pelo menos uma das chaves:

| Variável | Descrição | Obrigatória |
|----------|-----------|-------------|
| `OPENAI_API_KEY` | API Key da OpenAI | Não* |
| `GOOGLE_API_KEY` | API Key do Google Gemini (fallback) | Não* |
| `OPENCODE_API_KEY` | API Key OpenCode (compatível OpenAI) | Não* |
| `MIMOCODE_API_KEY` | API Key MiMoCode (compatível OpenAI) | Não* |

*Pelo menos uma chave é necessária para funcionalidades de IA.

```bash
# Exemplo: configurar Google Gemini
export GOOGLE_API_KEY="sua-chave-aqui"
```

## Estrutura do Projeto

```
Salesforce-WebDev/
├── src/                    # Código-fonte Python
│   ├── main.py             # Orquestrador principal
│   ├── scraper.py          # Scraper Playwright
│   ├── parser.py           # Parser HTML/Markdown
│   ├── llm_service.py      # Multi-provider LLM
│   ├── generator.py        # Geração Markdown
│   └── ...
├── docs/                   # Documentação MkDocs
├── releases/               # Artefatos Markdown gerados
├── tests/                  # Testes pytest
├── mkdocs.yml              # Configuração do site de docs
└── pyproject.toml          # Configuração do projeto e dependências
```

## Próximos Passos

- [Executando o Pipeline](running-pipeline.md) — Detalhes do fluxo completo
- [Desenvolvimento Local](local-development.md) — Configuração avançada
- [Arquitetura](https://fatal1tybarucco.github.io/Salesforce-WebDev/architecture/overview/) — Visão geral do sistema
- [Runbooks](../runbooks/index.md) — Procedimentos de resposta a falhas
