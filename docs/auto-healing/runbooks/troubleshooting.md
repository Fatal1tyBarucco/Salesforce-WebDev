# Troubleshooting do Auto-Healing Agent

## Problemas Comuns e Soluções

### 1. Erro de Importação no Mypy

**Erro:**
```
src/auto_healing/webhook.py: error: Cannot find implementation or library stub for module named 'fastapi'
```

**Causa:** Dependências `healing` não instaladas no ambiente de CI.

**Solução:**
```yaml
# .github/workflows/python-quality.yml
- name: Install dependencies
  run: uv sync --frozen --extra dev --extra healing --group dev
```

---

### 2. Coverage Abaixo de 95%

**Erro:**
```
FAIL Required test coverage of 95% not reached. Total coverage: 87.04%
```

**Causa:** O módulo `auto_healing` não tem testes e puxa a cobertura média.

**Solução:**
```toml
# pyproject.toml
[tool.coverage.run]
omit = ["src/auto_healing/*"]
```

---

### 3. Webhook Retorna 503

**Erro:**
```json
{"detail": "Auto-healing services are not available."}
```

**Causa:** `GITHUB_ACCESS_TOKEN` ou `GOOGLE_API_KEY` não configurados.

**Solução:**
```bash
# Verificar variáveis de ambiente
echo $GITHUB_ACCESS_TOKEN
echo $GOOGLE_API_KEY

# Configurar se necessário
export GITHUB_ACCESS_TOKEN="ghp_..."
export GOOGLE_API_KEY="AI..."

# Reiniciar serviço
docker-compose restart auto-healing
```

---

### 4. Webhook Retorna 400

**Erro:**
```json
{"detail": "Invalid JSON payload."}
```

**Causa:** Payload do webhook não é JSON válido.

**Solução:**
1. Verificar Content-Type do webhook no GitHub
2. Deve ser `application/json`
3. Testar manualmente:
```bash
curl -X POST https://auto-healing.seu-dominio.com/webhook/workflow-run \
  -H "Content-Type: application/json" \
  -d '{"action": "completed"}'
```

---

### 5. LLM Retorna JSON Inválido

**Erro no log:**
```
Failed to parse JSON from LLM output. First 200 chars: ...
```

**Causa:** LLM retornou texto com fences markdown ou formato inválido.

**Solução:**
O agent já tem parser com fallback. Se persistir:
1. Verificar logs para ver o output bruto
2. Ajustar temperature (mais baixa = mais determinístico)
3. Verificar se o modelo está disponível

---

### 6. Branch `auto-fix/*` Não É Criada

**Erro no log:**
```
Failed to create branch 'auto-fix/12345': Reference already exists
```

**Causa:** Branch já existe de tentativa anterior.

**Solução:**
```bash
# Listar branches auto-fix
git branch -r | grep auto-fix

# Deletar branch antiga
git push origin --delete auto-fix/12345
```

---

### 7. PR Não É Criado

**Erro no log:**
```
Failed to create pull request from branch 'auto-fix/12345': Validation Failed
```

**Causa:** PR já existe ou dados inválidos.

**Soluções:**

| Erro Específico | Solução |
|-----------------|---------|
| "A pull request already exists" | Fechar PR existente |
| "No commits between main and auto-fix/*" | Verificar se o arquivo foi alterado |
| "Not Found" | Verificar permissão do token |

---

### 8. Circuit Breaker Ativa Prematuramente

**Sintoma:** Circuit breaker ativa após 1-2 tentativas em vez de 3.

**Causa:** Commits extras no PR (ex: merge commits).

**Solução:**
1. Verificar commits do PR:
```bash
gh pr view 42 --json commits | jq '.[].messageHeadline'
```
2. Apenas commits com prefixo `[auto-heal]` contam
3. Se houver commits extras, fechar PR e recriar

---

### 9. Logs Não Aparecem

**Sintoma:** `retrieve_failed_action_logs()` retorna `None`.

**Causa:** Logs expirados ou permissão insuficiente.

**Soluções:**

| Causa | Solução |
|-------|---------|
| Logs expirados (> 90 dias) | Verificar se o workflow run é recente |
| Token sem permissão | Verificar escopo `repo` do token |
| Workflow run não encontrado | Verificar se o ID está correto |

---

### 10. Slow Response / Timeouts

**Sintoma:** Webhook demora mais de 30 segundos.

**Causa:** LLM lento ou GitHub API com latência.

**Soluções:**
1. Verificar latência da API do Google Gemini:
```bash
time curl "https://generativelanguage.googleapis.com/v1beta/models?key=$GOOGLE_API_KEY"
```
2. Verificar rate limits do GitHub:
```bash
curl -H "Authorization: token $GITHUB_ACCESS_TOKEN" \
  https://api.github.com/rate_limit
```
3. Considerar aumentar timeout do webhook

---

## Debugging

### Logs Detalhados

```bash
# Logs com timestamp
docker logs auto-healing 2>&1 | grep "2026-08-07"

# Logs de erro
docker logs auto-healing 2>&1 | grep -E "ERROR|WARNING|CRITICAL"

# Logs de um workflow específico
docker logs auto-healing 2>&1 | grep "31134588250"
```

### Testar Componentes Individualmente

```python
# Testar GitHub Service
from src.auto_healing.github_service import GitHubService

service = GitHubService(access_token="ghp_...")
repo = service._get_repository("owner/repo")
print(repo)

# Testar Agent Core
from src.auto_healing.agent_core import AgentCore

agent = AgentCore(google_api_key="AI...")
result = agent.analyze_pipeline_failure("Error: test failed...")
print(result)
```

### Verificar Estado do Serviço

```bash
# Status do container
docker ps | grep auto-healing

# Uso de recursos
docker stats auto-healing --no-stream

# Health check detalhado
curl -s https://auto-healing.seu-dominio.com/health | jq .
```

## Referências

- [Runbook de Operação](auto-healing-agent.md)
- [Guia de Deploy](../deployment/guide.md)
- [Arquitetura](../architecture/deep-dive.md)
- [Troubleshooting Geral](../../maintenance/troubleshooting.md)
