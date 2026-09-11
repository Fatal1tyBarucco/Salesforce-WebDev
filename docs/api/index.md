# API Reference

Referência de API autogerada a partir das docstrings do código-fonte Python, utilizando o plugin [`mkdocstrings`](https://mkdocstrings.github.io/) com_handler Python e estilo Google.

## Como Funciona

Cada módulo documentado possui um arquivo "evocador" em `docs/api/` com uma diretiva do tipo:

```markdown
::: src.modulo
```

O mkdocstrings lê as docstrings (Google-style) das classes, métodos e funções definidas em `src/` e gera a documentação automaticamente no site.

## Módulos Documentados

| Módulo | Descrição |
|--------|-----------|
| [`src.main`](main.md) | Orquestrador principal do pipeline |
| [`src.scraper`](scraper.md) | Scraper Playwright para Salesforce Help |
| [`src.parser`](parser.md) | Parser HTML para árvore de tópicos e feature impact |
| [`src.llm_service`](llm_service.md) | Serviço LLM multi-provider com fallback |
| [`src.feature_classifier`](feature_classifier.md) | Classificação de features via LLM |
| [`src.translator`](translator.md) | Tradução de conteúdo via LLM |
| [`src.notifications`](notifications.md) | Sistema de notificações (Email, Slack, Discord) |
| [`src.cache_manager`](cache_manager.md) | Cache unificado (TTL + content-hash) |

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
