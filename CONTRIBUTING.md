# 🤝 Contributing to Salesforce-WebDev

Obrigado por contribuir! Este documento descreve como contribuir de forma eficiente.

---

## 🚀 Quick Start

```bash
# 1. Clone e instale
git clone https://github.com/Fatal1tyBarucco/Salesforce-WebDev.git
cd Salesforce-WebDev
uv sync --extra dev

# 2. Instale Playwright
uv run playwright install chromium

# 3. Instale hooks de qualidade (OBRIGATÓRIO)
uv run pre-commit install
uv run pre-commit install --hook-type pre-push

# 4. Configure LLM (pelo menos uma key)
export OPENAI_API_KEY="sk-..."
```

---

## 📋 Processo de Contribuição

### 1. Branch Naming
```
feat/nome-da-feature    # Nova funcionalidade
fix/nome-do-bug         # Correção de bug
docs/nome-da-doc        # Documentação
refactor/nome           # Refatoração
test/nome               # Testes
```

### 2. Commits (Conventional Commits)
```
feat(scope): descrição curta
fix(scope): descrição curta
docs(scope): descrição curta
refactor(scope): descrição curta
test(scope): descrição curta
chore(scope): descrição curta
```

Exemplos:
```
feat(scraper): add parallel URL fetching
fix(llm): handle None response from provider
docs(readme): update installation steps
test(cache): add namespace invalidation tests
```

### 3. Pull Requests

1. Fork o repositório
2. Crie uma branch (`feat/minha-feature`)
3. Faça commits seguindo conventional commits
4. Rode os checks localmente antes de push:
   ```bash
   pre-commit run --all-files
   ```
5. Abra um PR com:
   - Título descritivo
   - Descrição do que mudou e por quê
   - Link para issue relacionada (se houver)
   - Screenshots (se UI)

---

## 🔍 Checks de Qualidade

Os hooks rodam automaticamente em cada commit/push:

| Hook | Quando | O que faz |
|------|--------|-----------|
| **Ruff** | commit | Lint + auto-fix |
| **Black** | commit | Formatação |
| **Mypy** | commit | Type checking (strict) |
| **Pytest** | push | Testes (para no primeiro erro) |

### Rodar manualmente:
```bash
# Todos os checks
pre-commit run --all-files

# Apenas ruff
pre-commit run ruff --all-files

# Apenas black
pre-commit run black --all-files

# Apenas mypy
pre-commit run mypy --all-files

# Pytest com cobertura
pre-commit run --hook-stage manual pytest-coverage

# Pytest completo
uv run pytest tests/ --cov=src --cov-report=term-missing -q
```

---

## 🧪 Testes

### Estrutura
```
tests/
├── conftest.py              # Fixtures globais (mock LLM, OpenAI)
├── test_events.py           # EventBus tests
├── test_cache_manager.py    # CacheManager tests
├── test_llm_service.py      # LLMService tests
├── test_main_coverage.py    # Pipeline coverage
└── ...
```

### Criar novos testes
```python
import pytest
from src.meu_modulo import MinhaClasse

@pytest.fixture
def minha_fixture():
    return MinhaClasse()

def test_funcionalidade(minha_fixture):
    resultado = minha_fixture.metodo()
    assert resultado == "esperado"

@pytest.mark.asyncio
async def test_async():
    resultado = await minha_funcao_async()
    assert resultado is not None
```

### Mocks de LLM
Use a fixture `mock_llm_service` do `conftest.py`:
```python
def test_com_mock(mock_llm_service):
    resultado = asyncio.run(mock_llm_service.generate_text("prompt"))
    assert resultado == "mocked LLM response"
```

---

## 📐 Padrões de Código

### Type Hints (obrigatório)
```python
# ✅ Correto
def calcular_total(items: list[dict[str, int]]) -> int:
    return sum(item["count"] for item in items)

# ❌ Errado
def calcular_total(items):
    return sum(item["count"] for item in items)
```

### Null Safety
```python
# ✅ Correto
nome = meta.get("name", "Unknown")
if nome is None:
    nome = "Unknown"

# ❌ Errado
nome = meta["name"]  # KeyError se ausente
```

### Tratamento de Exceções
```python
# ✅ Correto
try:
    resultado = await chamar_api()
except (TimeoutError, ConnectionError) as e:
    logger.error("API falhou: %s", e)
    return None

# ❌ Errado
try:
    resultado = await chamar_api()
except Exception:
    pass
```

---

## 📚 Documentação

### Docstrings (Google style)
```python
def processar_release(slug: str, dry_run: bool = False) -> ReleaseResult:
    """Processa uma release Salesforce.

    Args:
        slug: Identificador da release (ex: 'summer_26').
        dry_run: Se True, não escreve arquivos.

    Returns:
        ReleaseResult com status e artefatos gerados.

    Raises:
        ReleaseNotFoundError: Se a release não existir.
    """
```

---

## 🏗️ Arquitetura

```
src/
├── main.py              # Entry point + PipelineConfig
├── orchestrator.py      # PipelineOrchestrator (coordenação)
├── scraper.py           # Playwright scraping
├── parser.py            # Feature Impact parsing
├── llm_service.py       # Multi-provider LLM (OpenAI, Gemini)
├── events.py            # EventBus (pub/sub)
├── cache_manager.py     # TTL + content-hash caching
├── circuit_breaker.py   # Circuit breaker pattern
├── config.py            # Constants + dataclasses
├── release_docs.py      # Markdown generation
├── health.py            # Health checks
└── automation/          # AI automation services
    ├── service.py       # AIAutomationService
    ├── content.py       # Content deduplication
    ├── comparison.py    # Release comparison
    └── ...
```

---

## ❓ Dúvidas

- **Issues**: Use GitHub Issues para bugs e feature requests
- **Discussions**: Use GitHub Discussions para perguntas
- **Email**: barucco@gmail.com

---

## 📄 Licença

Este projeto é educacional. Veja [LICENSE](./LICENSE) para detalhes.
