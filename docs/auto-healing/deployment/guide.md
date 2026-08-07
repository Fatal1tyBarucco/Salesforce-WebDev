# Guia de Deploy do Auto-Healing Agent

## Pré-requisitos

- Python 3.12+
- GitHub Personal Access Token com scope `repo`
- Google Gemini API Key
- Servidor com acesso público (para webhook)

## 1. Configuração do GitHub

### Personal Access Token

1. Ir para **GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)**
2. Criar token com escopo:
   - `repo` — Acesso completo ao repositório
3. Copiar o token (formato: `ghp_...`)

### Webhook Configuration

1. Ir para **Repository → Settings → Webhooks → Add webhook**
2. Configurar:
   - **Payload URL:** `https://seu-dominio.com/webhook/workflow-run`
   - **Content type:** `application/json`
   - **Secret:** (opcional, recomendado)
   - **Events:** Selecionar apenas `Workflow runs`

## 2. Configuração do Google Gemini

1. Ir para [Google AI Studio](https://aistudio.google.com/)
2. Criar API Key
3. Copiar a chave (formato: `AI...`)

## 3. Deploy Local (Desenvolvimento)

```bash
# Clone o repositório
git clone https://github.com/Fatal1tyBarucco/Salesforce-WebDev.git
cd Salesforce-WebDev

# Instalar dependências
uv sync --extra dev --extra healing

# Configurar variáveis de ambiente
export GITHUB_ACCESS_TOKEN="ghp_..."
export GOOGLE_API_KEY="AI..."
export GITHUB_WEBHOOK_SECRET="..."  # opcional

# Executar o servidor
uvicorn src.auto_healing.webhook:app --host 0.0.0.0 --port 8000 --reload
```

### Verificar

```bash
# Health check
curl http://localhost:8000/health

# Resposta esperada:
# {
#   "status": "healthy",
#   "github_service_available": true,
#   "agent_core_available": true
# }
```

## 4. Deploy com Docker

### Dockerfile

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Instalar uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copiar dependências
COPY pyproject.toml uv.lock ./

# Instalar dependências
RUN uv sync --frozen --extra healing --no-dev

# Copiar código
COPY src/ src/

# Configurar variáveis de ambiente
ENV GITHUB_ACCESS_TOKEN=""
ENV GOOGLE_API_KEY=""
ENV GITHUB_WEBHOOK_SECRET=""

# Executar
CMD ["uv", "run", "uvicorn", "src.auto_healing.webhook:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Build e Run

```bash
# Build
docker build -t auto-healing-agent .

# Run
docker run -d \
  --name auto-healing \
  -p 8000:8000 \
  -e GITHUB_ACCESS_TOKEN="ghp_..." \
  -e GOOGLE_API_KEY="AI..." \
  -e GITHUB_WEBHOOK_SECRET="..." \
  auto-healing-agent
```

## 5. Deploy com Docker Compose

### docker-compose.yml

```yaml
version: "3.8"

services:
  auto-healing:
    build: .
    ports:
      - "8000:8000"
    environment:
      - GITHUB_ACCESS_TOKEN=${GITHUB_ACCESS_TOKEN}
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - GITHUB_WEBHOOK_SECRET=${GITHUB_WEBHOOK_SECRET}
      - PRIMARY_BRANCH=main
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### Executar

```bash
# Criar .env
cat > .env << EOF
GITHUB_ACCESS_TOKEN=ghp_...
GOOGLE_API_KEY=AI...
GITHUB_WEBHOOK_SECRET=...
EOF

# Executar
docker-compose up -d

# Logs
docker-compose logs -f auto-healing
```

## 6. Deploy em Produção

### Requisitos de Produção

- **HTTPS:** Obrigatório para webhooks do GitHub
- **Reverse Proxy:** Nginx, Traefik, ou Caddy
- **Secrets Management:** Vault, AWS Secrets Manager, ou similar
- **Monitoring:** Logs estruturados, métricas, alertas
- **Rate Limiting:** Proteger endpoint de webhook

### Exemplo com Nginx

```nginx
server {
    listen 443 ssl;
    server_name auto-healing.seu-dominio.com;

    ssl_certificate /etc/ssl/certs/cert.pem;
    ssl_certificate_key /etc/ssl/private/key.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Rate limiting
        limit_req zone=webhook burst=10 nodelay;
    }
}

limit_req_zone $binary_remote_addr zone=webhook:10m rate=10r/s;
```

### Exemplo com Caddy

```
auto-healing.seu-dominio.com {
    reverse_proxy localhost:8000
    
    # Rate limiting
    rate_limit {
        zone webhook {
            key {remote_host}
            events 10
            window 1m
        }
    }
}
```

## 7. Monitoramento

### Health Check

```bash
curl https://auto-healing.seu-dominio.com/health
```

Resposta:
```json
{
  "status": "healthy",
  "github_service_available": true,
  "agent_core_available": true
}
```

### Logs Estruturados

O agent produz logs em formato estruturado:

```
2026-08-07 00:25:19 | src.auto_healing.webhook | INFO | Auto-Healing Agent started.
2026-08-07 00:25:20 | src.auto_healing.webhook | INFO | Detected failure on primary branch 'main'. Initiating healing flow.
2026-08-07 00:25:21 | src.auto_healing.github_service | INFO | Retrieving logs for workflow run 31134588250...
2026-08-07 00:25:23 | src.auto_healing.agent_core | INFO | Performing root cause analysis...
2026-08-07 00:25:30 | src.auto_healing.github_service | INFO | Created healing branch 'auto-fix/31134588250' from 'main' (SHA: abc12345).
2026-08-07 00:25:35 | src.auto_healing.github_service | INFO | Opened pull request #42: https://github.com/owner/repo/pull/42
```

### Métricas Recomendadas

| Métrica | Descrição | Alerta |
|---------|-----------|--------|
| `healing_requests_total` | Total de webhooks recebidos | - |
| `healing_success_total` | Correções bem-sucedidas | - |
| `healing_failure_total` | Falhas na correção | > 5/hora |
| `circuit_breaker_open_total` | Circuit Breakers ativados | > 0/dia |
| `llm_latency_seconds` | Latência da chamada LLM | > 30s |
| `pr_creation_latency_seconds` | Latência da criação de PR | > 60s |

## 8. Troubleshooting

### Problema: Webhook não chega

```bash
# Verificar se o servidor está rodando
curl http://localhost:8000/health

# Verificar logs do GitHub
# Repository → Settings → Webhooks → Recent Deliveries

# Verificar se o endpoint está acessível
curl -X POST http://localhost:8000/webhook/workflow-run \
  -H "Content-Type: application/json" \
  -d '{"action": "completed", "workflow_run": {"conclusion": "failure"}}'
```

### Problema: LLM não responde

```bash
# Verificar se a API key está configurada
echo $GOOGLE_API_KEY

# Testar a API key
curl "https://generativelanguage.googleapis.com/v1beta/models?key=$GOOGLE_API_KEY"
```

### Problema: PR não é criado

```bash
# Verificar se o token tem permissão
curl -H "Authorization: token $GITHUB_ACCESS_TOKEN" \
  https://api.github.com/repos/owner/repo

# Verificar logs do agent
docker logs auto-healing 2>&1 | grep ERROR
```

## 9. Segurança

### Checklist de Segurança

- [ ] HTTPS habilitado
- [ ] Webhook secret configurado
- [ ] Token com escopo mínimo (`repo` apenas)
- [ ] Rate limiting no endpoint
- [ ] Logs não expõem tokens/keys
- [ ] Variáveis de ambiente seguras (não hardcoded)
- [ ] Acesso restrito ao servidor
- [ ] Monitoramento de tentativas de acesso

### Rotação de Tokens

```bash
# Gerar novo token no GitHub
# Atualizar variável de ambiente
export GITHUB_ACCESS_TOKEN="novo_token"

# Reiniciar serviço
docker-compose restart auto-healing
```
