# Logging Strategy

## Objectives

- Centralized operational visibility
- Easier troubleshooting
- Pipeline execution traceability
- Correlation ID tracking across pipeline steps

## Logging Principles

- Structured logs (JSON ou texto formatado)
- Consistent formatting com correlation_id
- Operational context preservation
- Failure visibility com stack traces

## Current Implementation

### Módulo `src/logger.py`

O projeto emprega logging estruturado com as seguintes componentes:

| Componente | Responsabilidade |
|------------|-----------------|
| `setup_logging()` | Configura o logger raiz com formatter texto ou JSON |
| `JSONFormatter` | Formata registros como JSON (timestamps, nível, mensagem, correlation_id, exception) |
| `TextFormatter` | Formata registros em texto com prefixo de correlation_id `[xxxxxxxx]` |
| `CorrelationFilter` | Insere correlation_id em cada log record para rastreamento cross-componente |
| `new_correlation_id()` | Gera novo correlation_id (12 caracteres hex) por execução |
| `setup_sentry()` | Integrção opcional com Sentry (via `SENTRY_DSN`) |

### Saída de Log

Por padrão, os logs são emitidos para stdout em formato texto com prefixo de correlation_id. Em ambientes de produção ou para integração com sistemas de agregação, pode-se ativar o modo JSON com a variável de ambiente `LOG_FORMAT=json` ou chamando `setup_logging(json_format=True)`.

### Níveis de Log

- **INFO** — Operação normal do pipeline (default, controlado por `LOG_LEVEL`)
- **WARNING** — Situações recuperáveis (retry, fallback de provider)
- **ERROR** — Falhas que interrompem o fluxo (scraper, parsing, geração)
- **DEBUG** — Detail para diagnóstico (ativado com `LOG_LEVEL=DEBUG`)

## Health Checks e Métricas

Veja [Pipeline Health](pipeline-health.md) para detalhes sobre:

- Health endpoints (`/health`, `/ready`, `/metrics`)
- Métricas Prometheus expostas para monitoramento
- Status do pipeline e retries

## Future Improvements

- Dashboard de logs centralizado (ELK / Loki)
- Métricas de latência por etapa do pipeline
- Alertas baseados em log patterns
- Distribuição de correlation_id para notificações externas
