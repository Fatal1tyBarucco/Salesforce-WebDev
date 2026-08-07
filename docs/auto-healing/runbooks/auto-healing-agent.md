# Runbook: Auto-Healing Agent

## Visão Geral

Este runbook cobre operações comuns do Auto-Healing CI/CD Agent.

## Cenários Comuns

### 1. Agent Não Responde a Falhas

**Sintomas:**
- Pipeline falha mas nenhum PR é criado
- Webhook não é entregue pelo GitHub

**Diagnóstico:**

```bash
# 1. Verificar se o agent está rodando
curl https://auto-healing.seu-dominio.com/health

# 2. Verificar logs do GitHub
# Repository → Settings → Webhooks → Recent Deliveries
# Procurar por entregas com status ≠ 200

# 3. Verificar logs do agent
docker logs auto-healing 2>&1 | tail -50

# 4. Testar o endpoint manualmente
curl -X POST https://auto-healing.seu-dominio.com/webhook/workflow-run \
  -H "Content-Type: application/json" \
  -d '{
    "action": "completed",
    "workflow_run": {
      "id": 12345,
      "name": "Python Quality",
      "head_branch": "main",
      "head_sha": "abc123",
      "conclusion": "failure",
      "html_url": "https://github.com/owner/repo/actions/runs/12345",
      "repository": {"full_name": "owner/repo"}
    }
  }'
```

**Soluções:**

| Causa | Solução |
|-------|---------|
| Agent offline | Reiniciar: `docker-compose restart auto-healing` |
| Webhook mal configurado | Reconfigurar no GitHub (ver Deploy Guide) |
| Token expirado | Gerar novo token e atualizar `GITHUB_ACCESS_TOKEN` |
| API key inválida | Verificar `GOOGLE_API_KEY` |
| Firewall bloqueando | Verificar regras de rede |

---

### 2. PR Criado mas Testes Falham

**Sintomas:**
- PR é criado pelo agent
- Pipeline `agent-validation.yml` falha
- Agent tenta correção incremental

**Diagnóstico:**

```bash
# 1. Verificar o PR no GitHub
# Procurar PRs de branches auto-fix/*

# 2. Verificar logs da pipeline agent-validation
# PR → Checks → Agent Validation → Ver detalhes

# 3. Verificar se o Circuit Breaker foi ativado
# PR → Comments → Procurar comentário "Circuit Breaker Triggered"
```

**Soluções:**

| Causa | Solução |
|-------|---------|
| LLM gerou código inválido | Fechar PR, corrigir manualmente |
| Teste não existe | Criar teste para o arquivo alterado |
| Coverage < 95% | Adicionar testes ou ajustar threshold |
| Circuit Breaker ativado | Intervenção manual necessária |

---

### 3. Circuit Breaker Ativado

**Sintomas:**
- PR tem comentário "🚫 Auto-Healing Circuit Breaker Triggered"
- Agent não faz mais tentativas

**Diagnóstico:**

```bash
# 1. Contar commits do agente no PR
git log --oneline --grep="[auto-heal]" PR_BRANCH

# 2. Verificar se o limite foi atingido (3 tentativas)
# Cada commit com prefixo [auto-heal] conta como uma tentativa
```

**Soluções:**

1. **Revisar tentativas do agent:**
   - Ler comentários no PR documentando cada tentativa
   - Identificar padrão de falha

2. **Fechar PR e corrigir manualmente:**
   ```bash
   git checkout main
   git pull origin main
   # Fazer correção manual
   git commit -m "fix: correção manual após circuit breaker"
   git push origin main
   ```

3. **Resetar Circuit Breaker (se necessário):**
   - Fechar o PR atual
   - O próximo push que falhar criará um novo PR com contador zerado

---

### 4. LLM Não Responde ou Retorna Erro

**Sintomas:**
- Logs mostram "LLM invocation failed"
- PR não é criado
- Outcome: `analysis_failed`

**Diagnóstico:**

```bash
# 1. Verificar logs do agent
docker logs auto-healing 2>&1 | grep -i "llm\|error\|failed"

# 2. Testar a API key do Google
curl "https://generativelanguage.googleapis.com/v1beta/models?key=$GOOGLE_API_KEY"

# 3. Verificar quota da API
# Google AI Studio → Dashboard → Usage
```

**Soluções:**

| Causa | Solução |
|-------|---------|
| API key inválida | Gerar nova key no Google AI Studio |
| Quota excedida | Aguardar reset ou aumentar quota |
| Timeout | Verificar conectividade de rede |
| Modelo indisponível | Verificar status do Google Gemini |

---

### 5. Webhook Recebe Eventos Indesejados

**Sintomas:**
- Agent processa eventos que não são falhas
- Logs mostram "Ignoring workflow action 'requested'"

**Diagnóstico:**

```bash
# 1. Verificar configuração do webhook no GitHub
# Repository → Settings → Webhooks → Edit
# Verificar se apenas "Workflow runs" está selecionado

# 2. Verificar logs do agent
docker logs auto-healing 2>&1 | grep "Ignoring"
```

**Soluções:**

1. **Reconfigurar webhook:**
   - Ir para Repository → Settings → Webhooks
   - Editar webhook existente
   - Em "Which events would you like to trigger this webhook?", selecionar apenas "Workflow runs"

2. **Verificar filtros no agent:**
   - O agent já filtra `action == "completed"` e `conclusion == "failure"`
   - Eventos de outras branches são ignorados com `SKIPPED`

---

### 6. PR Criado na Branch Errada

**Sintomas:**
- PR aponta para branch diferente de `main`
- Branch `auto-fix/*` não é criada

**Diagnóstico:**

```bash
# 1. Verificar variável PRIMARY_BRANCH
echo $PRIMARY_BRANCH

# 2. Verificar logs do agent
docker logs auto-healing 2>&1 | grep "branch"

# 3. Verificar se a branch existe no repositório
git branch -r | grep auto-fix
```

**Soluções:**

| Causa | Solução |
|-------|---------|
| `PRIMARY_BRANCH` errado | Configurar corretamente (default: `main`) |
| Branch já existe | Fechar PR existente, agent criará nova |
| Permissão insuficiente | Verificar escopo do token |

---

### 7. Coverage Threshold Falha no PR

**Sintomas:**
- Pipeline `agent-validation.yml` falha no step de pytest
- Erro: "Required test coverage of 95% not reached"

**Diagnóstico:**

```bash
# 1. Verificar qual arquivo foi alterado
# PR → Files changed

# 2. Verificar se existe teste correspondente
ls tests/test_*NOME*.py

# 3. Rodar teste localmente
uv run pytest tests/test_NOME.py --cov=src/NOME --cov-report=term-missing
```

**Soluções:**

1. **Criar teste para o arquivo alterado:**
   ```python
   # tests/test_NOME.py
   def test_function():
       # Testar a função alterada
       pass
   ```

2. **Verificar mapeamento fonte → teste:**
   - `src/service.py` → `tests/test_service.py`
   - `src/auto_healing/webhook.py` → `tests/test_auto_healing_webhook.py`

---

## Comandos Úteis

### Verificar Status

```bash
# Health check
curl https://auto-healing.seu-dominio.com/health

# Logs em tempo real
docker logs -f auto-healing

# Últimos 100 logs
docker logs --tail 100 auto-healing

# Logs com filtro
docker logs auto-healing 2>&1 | grep -E "ERROR|WARNING"
```

### Reiniciar Serviço

```bash
# Docker Compose
docker-compose restart auto-healing

# Docker direto
docker restart auto-healing

# Com rebuild
docker-compose up -d --build auto-healing
```

### Testar Webhook Manualmente

```bash
# Simular falha na pipeline
curl -X POST https://auto-healing.seu-dominio.com/webhook/workflow-run \
  -H "Content-Type: application/json" \
  -d '{
    "action": "completed",
    "workflow_run": {
      "id": 99999,
      "name": "Python Quality",
      "head_branch": "main",
      "head_sha": "abc123def456",
      "conclusion": "failure",
      "html_url": "https://github.com/owner/repo/actions/runs/99999",
      "repository": {"full_name": "owner/repo"}
    }
  }'
```

### Verificar PRs do Agent

```bash
# Listar PRs abertos de branches auto-fix
gh pr list --head "auto-fix/*" --state open

# Ver detalhes de um PR
gh pr view 42

# Ver commits do agent em um PR
gh pr view 42 --json commits | jq '.[] | select(.messageHeadline | startswith("[auto-heal]"))'
```

## Contatos e Escalação

| Nível | Responsável | Contato |
|-------|-------------|---------|
| L1 | DevOps Team | #devops Slack |
| L2 | Tech Lead | #engineering Slack |
| L3 | Repository Owner | GitHub Issues |

## Referências

- [Guia de Deploy](../deployment/guide.md)
- [Arquitetura do Agent](../architecture/deep-dive.md)
- [ADR-004: Auto-Healing Agent](../../architecture/decisions/adr-004-auto-healing-agent.md)
- [Troubleshooting Geral](../../maintenance/troubleshooting.md)
