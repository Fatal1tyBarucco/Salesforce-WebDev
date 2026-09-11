# Runbooks — Índice

Procedimentos de resposta a falhas comuns do pipeline e da infraestrutura de documentação.

## Runbooks Disponíveis

| Runbook | Quando Usar |
|---------|-------------|
| [Falha no Scraper](scraper-failure.md) | O Playwright não consegue extrair conteúdo da Salesforce Help |
| [Falha no GitHub Actions](github-actions-failure.md) | Workflow de CI/CD falha (extração, sync ou build) |
| [Falha no Document Sync](documentation-sync-failure.md) | O workflow documentation-sync.yml não consegue reconciliar documentação |
| [Falha no MkDocs Build](mkdocs-build-failure.md) | O mkdocs build --strict falha (nav inválida, snippet faltando, etc.) |
| [Falha na Geração de Release](release-generation-failure.md) | O pipeline de releases não gera artefatos Markdown esperados |

## Procedimento Geral de Resposta

1. **Identificar o escopo:** Verifique se o problema é pontual (uma release específica) ou estrutural (todo o pipeline).
2. **Consultar logs:** GitHub Actions logs para workflows; `src/logger.py` para logs locais com correlation_id.
3. **Executar validação local:** `uv run mkdocs build --strict` e `uv run pytest` para isolamento.
4. **Aplicar runbook específico:** Siga o runbook correspondente ao tipo de falha.
5. **Validar a recuperação:** Confirme que o build do site e os testes passam.
6. **Documentar a causa raiz:** Se o problema revelar uma lacuna na documentação ou no código, registrar em issue ou ADR.
