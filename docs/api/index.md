# API Reference

Referência de API autogerada a partir das docstrings do código-fonte Python, utilizando o plugin [`mkdocstrings`](https://mkdocstrings.github.io/) com_handler Python e estilo Google.

## Como Funciona

Cada módulo documentado possui um arquivo "evocador" em `docs/api/` com uma diretiva do tipo:

```markdown
::: src.modulo
```markdown

O mkdocstrings lê as docstrings (Google-style) das classes, métodos e funções definidas em `src/` e gera a documentação automaticamente no site.

## Módulos Documentados

| Módulo | Evocador |
|--------|----------|
| `src.ai.generators.badges` | [`ai-generators-badges.md`](ai-generators-badges.md) |
| `src.ai.generators.code` | [`ai-generators-code.md`](ai-generators-code.md) |
| `src.ai.generators.markdown` | [`ai-generators-markdown.md`](ai-generators-markdown.md) |
| `src.ai.integrations.salesforce` | [`ai-integrations-salesforce.md`](ai-integrations-salesforce.md) |
| `src.ai.integrations.trailhead` | [`ai-integrations-trailhead.md`](ai-integrations-trailhead.md) |
| `src.ai.prompts.classification` | [`ai-prompts-classification.md`](ai-prompts-classification.md) |
| `src.ai.prompts.enrichment` | [`ai-prompts-enrichment.md`](ai-prompts-enrichment.md) |
| `src.ai.prompts.reporting` | [`ai-prompts-reporting.md`](ai-prompts-reporting.md) |
| `src.ai.prompts.validation` | [`ai-prompts-validation.md`](ai-prompts-validation.md) |
| `src.ai_automation` | [`ai_automation.md`](ai_automation.md) |
| `src.analytics` | [`analytics.md`](analytics.md) |
| `src.api` | [`api.md`](api.md) |
| `src.automation.badge` | [`automation-badge.md`](automation-badge.md) |
| `src.automation.comparison` | [`automation-comparison.md`](automation-comparison.md) |
| `src.automation.content` | [`automation-content.md`](automation-content.md) |
| `src.automation.export` | [`automation-export.md`](automation-export.md) |
| `src.automation.github_ops` | [`automation-github_ops.md`](automation-github_ops.md) |
| `src.automation.impact` | [`automation-impact.md`](automation-impact.md) |
| `src.automation.models` | [`automation-models.md`](automation-models.md) |
| `src.automation.notifications` | [`automation-notifications.md`](automation-notifications.md) |
| `src.automation.reporting` | [`automation-reporting.md`](automation-reporting.md) |
| `src.automation.service` | [`automation-service.md`](automation-service.md) |
| `src.cache_manager` | [`cache_manager.md`](cache_manager.md) |
| `src.circuit_breaker` | [`circuit_breaker.md`](circuit_breaker.md) |
| `src.config` | [`config.md`](config.md) |
| `src.dashboard` | [`dashboard.md`](dashboard.md) |
| `src.events` | [`events.md`](events.md) |
| `src.exceptions` | [`exceptions.md`](exceptions.md) |
| `src.feature_classifier` | [`feature_classifier.md`](feature_classifier.md) |
| `src.feature_enricher` | [`feature_enricher.md`](feature_enricher.md) |
| `src.generator` | [`generator.md`](generator.md) |
| `src.health` | [`health.md`](health.md) |
| `src.heuristic_classifier` | [`heuristic_classifier.md`](heuristic_classifier.md) |
| `src.i18n` | [`i18n.md`](i18n.md) |
| `src.impact_analyzer` | [`impact_analyzer.md`](impact_analyzer.md) |
| `src.issue_triage` | [`issue_triage.md`](issue_triage.md) |
| `src.limiters.rate_limiter` | [`limiters-rate_limiter.md`](limiters-rate_limiter.md) |
| `src.llm_service` | [`llm_service.md`](llm_service.md) |
| `src.logger` | [`logger.md`](logger.md) |
| `src.main` | [`main.md`](main.md) |
| `src.models` | [`models.md`](models.md) |
| `src.nl_search` | [`nl_search.md`](nl_search.md) |
| `src.notifications` | [`notifications.md`](notifications.md) |
| `src.orchestrator` | [`orchestrator.md`](orchestrator.md) |
| `src.parser` | [`parser.md`](parser.md) |
| `src.release_docs` | [`release_docs.md`](release_docs.md) |
| `src.release_summarizer` | [`release_summarizer.md`](release_summarizer.md) |
| `src.salesforce` | [`salesforce.md`](salesforce.md) |
| `src.scraper` | [`scraper.md`](scraper.md) |
| `src.smart_notifications` | [`smart_notifications.md`](smart_notifications.md) |
| `src.translator` | [`translator.md`](translator.md) |
| `src.workflow` | [`workflow.md`](workflow.md) |

## Diretrizes de Docstring

Para que a referência de API seja consistente e útil, todas as novas classes e funções públicas devem seguir:

- **Estilo Google:** `Args:`, `Returns:`, `Raises:`
- **Tipo anotado:** Type hints em parâmetros e retorno
- **Exemplo de uso (opcional):** Quando a função tem semântica não-obvia

Exemplo:

```python

def classify_release(
    self,
    slug: str,
    *,
    max_features: int = 50,
) -> ClassificationResult:
    """Classifica uma release quanto ao impacto e temas dominantes.

    Analisa o conjunto de features da release e retorna uma classificação
    com impacto geral, audiencia-alvo e recomendações de ação.

    Args:
        slug: Identificador da release (ex: ``summer_26``).
        max_features: Número máximo de features a considerar na análise.

    Returns:
        ClassificationResult com impact_level, audience e summary.

    Raises:
        LLMProviderExhausted: Se nenhum provider LLM estiver disponível.
        ReleaseNotFoundError: Se a release não existir no armazenamento.
    """

```

## Manutenção da Referência

- A adição de um novo módulo público exige a criação de um arquivo evocador em `docs/api/<nome>.md`
- A remoção de um módulo deve ser acompanhada da remoção do arquivo evocador correspondente
- O mkdocs build --strict falha se um arquivo evocador referenciar um módulo que não existe — isso garante que a referência nunca fique órfã
