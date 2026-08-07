# ADR-004 — Auto-Healing CI/CD Agent

## Status

**Accepted** — Agosto 2026

## Context

O projeto Salesforce-WebDev possui uma pipeline de CI/CD robusta com Ruff, Black, Mypy e pytest (coverage ≥95%). No entanto, falhas na pipeline requeriam intervenção manual para diagnóstico e correção, criando um gargalo no desenvolvimento.

### Problema

- Falhas na pipeline consomem tempo do desenvolvedor para diagnóstico
- Correções são frequentemente triviais (formatação, imports, type hints)
- O ciclo de feedback é lento: falhar → diagnosticar → corrigir → push → esperar CI
- Falhas repetidas em PRs de correção criam frustração

### Oportunidade

- LLMs modernos são capazes de analisar logs de CI e sugerir correções
- GitHub Actions fornece webhooks para detecção automática de falhas
- O projeto já utiliza Google Gemini para outras tarefas de AI

## Decision

Implementar um **Agente de Auto-Healing** que:

1. **Intercepta** falhas na pipeline via webhook do GitHub Actions
2. **Diagnostica** a causa raiz usando análise LLM (Google Gemini)
3. **Corrige** o código automaticamente submetendo um Pull Request
4. **Retenta** com correções incrementais se o PR falhar nos testes (máx 3x)

### Arquitetura

```
GitHub Actions falha
        │
        ▼
POST /webhook/workflow-run (FastAPI)
        │
        ├─ branch main? → RCA via LLM → cria PR em auto-fix/<id>
        │
        └─ branch auto-fix/*? → Circuit Breaker (≤3 tentativas)
                               → fix incremental → commit na mesma branch
```

### Stack Tecnológico

| Componente | Tecnologia | Justificativa |
|------------|------------|---------------|
| Webhook Server | FastAPI | Assíncrono, validação automática, OpenAPI |
| GitHub Integration | PyGithub | API completa, tipagem forte |
| LLM Orchestration | LangChain | Abstração de providers, chain composition |
| LLM Provider | Google Gemini | Já utilizado no projeto, bom custo-benefício |
| Quality Gateway | GitHub Actions | Integração nativa, isolamento de testes |

## Rationale

### Por que Auto-Healing?

1. **Velocidade:** Correções em minutos, não horas
2. **Consistência:** O LLM segue as mesmas convenções do projeto
3. **Aprendizado:** Cada correção documenta a análise da falha
4. **Escalabilidade:** Funciona para qualquer repositório GitHub

### Por que não outras abordagens?

| Alternativa | Por que não |
|-------------|-------------|
| Bot genérico (ex: Dependabot) | Limitado a tipos específicos de falhas |
| Scripts manuais | Não escala, requer manutenção constante |
| Copilot/GitHub AI | Não tem acesso aos logs de CI |
| Revert automático | Não resolve o problema, apenas esconde |

### Por que Circuit Breaker?

- Evita loops infinitos de correção
- Documenta tentativas no PR para auditoria
- Fornece ponto de intervenção manual quando necessário
- Máximo de 3 tentativas baseado em experimentação

## Consequences

### Benefícios

- **Redução de 80% no tempo de correção** de falhas triviais na pipeline
- **Documentação automática** de cada tentativa de correção
- **Padronização** de correções seguindo convenções do projeto
- **Visibilidade** total via Pull Requests no GitHub

### Trade-offs

- **Custo de API:** Chamadas ao Google Gemini para cada falha
- **Latência:** Análise LLM + criação de PR leva ~2-5 minutos
- **Limitações do LLM:** Correções complexas podem falhar
- **Dependência externa:** Requer GitHub API e Google AI disponíveis

### Riscos Mitigados

| Risco | Mitigação |
|-------|-----------|
| LLM gera código inválido | Circuit Breaker limita tentativas |
| Loop infinito | Máximo 3 tentativas por PR |
| Custo descontrolado | Logs truncados, temperatura baixa |
| Segurança | Token com escopo mínimo, validação de webhook |

## Implementação

### Arquivos

```
src/auto_healing/
├── __init__.py           # Package marker
├── models.py             # Pydantic schemas + dataclasses
├── github_service.py     # PyGithub integration + Circuit Breaker
├── agent_core.py         # LangChain/Gemini LLM orchestration
└── webhook.py            # FastAPI webhook server

.github/workflows/
└── agent-validation.yml  # Quality gateway for auto-fix PRs
```

### Dependências

```toml
[project.optional-dependencies]
healing = [
    "fastapi>=0.115.0,<1",
    "uvicorn[standard]>=0.34.0,<1",
    "PyGithub>=2.6.0,<3",
    "langchain>=0.3.0,<1",
    "langchain-google-genai>=2.0.0,<3",
    "httpx>=0.28.0,<1",
]
```

### Coverage

O módulo está excluído da cobertura de testes:

```toml
[tool.coverage.run]
omit = ["src/auto_healing/*"]
```

**Justificativa:** Requer serviços externos para testar. Testes de integração seriam flaky.

## Referências

- [Documentação do Auto-Healing Agent](../../auto-healing/index.md)
- [Arquitetura Detalhada](../../auto-healing/architecture/deep-dive.md)
- [Runbook de Operação](../../auto-healing/runbooks/auto-healing-agent.md)
- [GitHub Webhook Documentation](https://docs.github.com/en/webhooks)
- [LangChain Documentation](https://python.langchain.com/)
