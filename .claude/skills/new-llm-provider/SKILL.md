---
name: new-llm-provider
description: Adicionar novo provedor LLM ao fallback chain (ex.: Anthropic, Mistral, local Ollama). Inclui: adapter, config, testes de contrato, fallback order, custos.
---

# Skill: new-llm-provider

## Quando Usar
- Novo provedor LLM disponível (ex.: Anthropic Claude, Mistral, Cohere, Ollama local)
- Provedor existente muda API (breaking change)
- Quer testar provedor alternativo para custo/latência

## Passos

### 1. Criar Adapter em `src/llm_service.py` (legado) ou `src/infrastructure/llm_adapters.py` (nova arch)
```python
class NovoProviderAdapter(LLMAdapter):
    async def generate_completion(self, prompt: str, **kwargs) -> LLMResponse:
        # Implemente chamada ao provedor
        pass
    
    async def classify_text(self, text: str) -> ClassificationResult:
        # Implemente classificação
        pass
```

### 2. Registrar no Fallback Chain (`src/llm_service.py` ou `src/infrastructure/llm_adapters.py`)
```python
_PROVIDER_CHAIN = [
    ("openrouter", OpenRouterAdapter()),
    ("opencode", OpenCodeAdapter()),
    ("gemini", GeminiAdapter()),
    ("novo", NovoProviderAdapter()),  # Adicione na ordem de preferência
]
```

### 3. Configuração (`src/config.py` ou `src/ai/config/models.py`)
- Adicione variáveis de ambiente necessárias (API_KEY, BASE_URL, MODEL_NAME)
- Documente em `.env.example` e `CLAUDE.md`
- Crie `.env.example` se não existir (referenciado em CLAUDE.md e .claude/settings.json deny)

### 4. Testes de Contrato (`tests/test_infrastructure_llm.py`)
- Mock do adapter com respostas fixas
- Teste: success, rate limit, auth error, timeout, invalid response
- Valide fallback para próximo provider

### 5. Tracking de Custo/Tokens
- Implemente `usage` property no adapter
- Log agregado por execução no pipeline principal

### 6. Validação Final
```bash
uv run ruff check . && uv run ruff format --check . && uv run mypy src/ --ignore-missing-imports && uv run pytest tests/test_infrastructure_llm.py -q
```
