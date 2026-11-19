<!-- gerado por IA em 2026-11-19T17:40:05+00:00 — revisar antes de publicar -->

# Sugestões de Roadmap

## Nova atualização

Sugestão: ## Nova atualização

Sugestão: Sugestões sujeitas a revisão humana: validar o conteúdo da documentação gerada por IA no commit 33ccab3 (release-notes.md, leadership.md, roadmap.md) antes de incorporá-la à documentação oficial; considerar adicionar verificação automatizada de sintaxe bash nos workflows para capturar erros de substituição GHA em tempo de PR; avaliar a inclusão de testes de contrato para o pipeline de documentação por IA, garantindo que steps de publish e summary generation funcionem em diferentes modos (PR vs push); monitorar a estabilidade do workflow ai-docs após a correção do Generate Summary; revisar periodicamente a consistência do manifesto de documentação e do drift report para evitar acúmulo de entradas `MANIFEST_STALE_SHA`.

---

## Nova atualização 2

Sugestão: Sugestões sujeitas a revisão humana: validar a compatibilidade de todos os consumidores de cache (summary, history, trailhead, processed_releases, orchestrator, health) após a migração para o envelope v2 e a remoção do MD5; submeter as correções de segurança do CodeQL (injeção em workflow_run, untrusted-checkout e permissões de arquivo) à revisão humana obrigatória e confirmar o fechamento completo dos alertas; monitorar a estabilidade do pipeline de documentação após os reparos de plugins mkdocs e a restauração do SOURCE_SCHEMA.md; avaliar testes de contrato ou de integração para o novo store processed_releases e para o comportamento de single-flight; considerar automação da validação das dependências de plugins de documentação (ex.: build --strict em PR) para evitar regressões; verificar no diff o escopo real da evolução para o Release Intelligence Hub (release 264), dado o commit de baixa confiança; confirmar a política final de qualidade (Ruff-only) e alinhar documentação interna e hooks; e revisar o conteúdo de atualizações automáticas de documentação geradas por bots antes de incorporá-las.

---

## Nova atualização 3

Sugestão: Sugestões sujeitas a revisão humana: definir e documentar política de exceção para execução de workflows em PRs de forks confiáveis ou migrar contribuidores externos para branches internos; implementar rotação programada e monitoramento de uso do segredo RELEASE_PLEASE_TOKEN; adicionar validação automatizada de dependências (ex: Dependabot alerts ou teste de integração pós-sync) após a sincronização automática de uv.lock no release-please; revisar a consistência dos hashes no docs/.documentation-manifest.json confirmando que todas as entradas correspondem a arquivos efetivamente modificados e não há duplicatas; avaliar a necessidade de testes de contrato para a interface de release notes dada a alteração nos extras do pytest; monitorar a estabilidade do pipeline de release notes após a adição dos extras 'dev' e 'healing'; considerar automação da verificação de lint markdown em PRs para evitar regressões de formatação em docs/index.md.

---

## Nova atualização 4

Sugestão: Sugestões sujeitas a revisão humana: validar a estabilidade dos novos triggers de workflow (event_name guards, branches filter, dummy jobs) em cenários de push reais e PRs; mapear consumidores de automações que dependiam de triggers push e comunicar mudanças; avaliar inclusão de testes de contrato para a interface do Release Intelligence Hub, dado o novo conjunto de artefatos JSON e HTML; monitorar a cobertura e confiabilidade dos hooks Python (pre-commit, pre-push, post-tool-use, session-start) em diferentes ambientes de desenvolvimento; revisar a sincronização automatizada de uv.lock após release-please para evitar dessincronizações recorrentes; considerar automação da validação de permissões GitHub Actions em workflows novos; avaliar a necessidade de testes de integração para o AI Triage refatorado, cobrindo casos de corpos de issue/PR com quebras de linha e encoding especial; monitorar a execução do Scheduled Pipeline após adição de Playwright e 'uv run python' no job de detecção; revisar se a remoção do deploy GitHub Pages do Intelligence Hub requer alternativa de publicação de artefatos.

---

## Nova atualização 5

Sugestão: Sugestões sujeitas a revisão humana: definir e documentar a política final do portão de qualidade (Black versus Ruff), eliminando a alternância de adição e remoção do job no workflow; mapear os consumidores do servidor MCP e validar a compatibilidade com a FastMCP API antes de ampliar a adoção; avaliar a inclusão de testes de contrato para a interface do servidor MCP, dado que a migração exigiu regeneração dos golden files; revisar o conteúdo produzido pela atualização automática de documentação por IA antes de incorporá-lo à documentação oficial; monitorar a estabilidade dos workflows de documentação e de qualidade após as correções aplicadas; considerar verificação automatizada de que o manifesto de documentação permanece consistente com os artefatos gerados.

---

## Nova atualização 6

Sugestão: Sugestões sujeitas a revisão humana: validar a consistência do inventário do manifesto de documentação com o gerador de documentação; revisar o comportamento esperado da geração do bloco antes de liberar, confirmando formatação esperada; confirmar que a API testada corresponde ao contrato publicado do MCP após adaptação dos testes.

---

## Nova atualização 7

Sugestão: ## Nova atualização

Sugestão: Sugestões sujeitas a revisão humana: mapear os consumidores do servidor MCP e validar a compatibilidade com a nova API v2 antes de ampliar a adoção; avaliar a inclusão de testes de contrato ou de integração para a interface do servidor MCP, considerando a remoção recente de testes de `call_tool`; revisar a ordem de lógica em `release_docs.py` para garantir que a correção de links não introduza regressões em outros idiomas; monitorar a cobertura dos testes de baixo nível e verificar se a refatoração afetou a confiabilidade dos testes de integração.

---

## Nova atualização 8

Sugestão: Sugestões sujeitas a revisão humana: avaliar validação automatizada de links de release por locale, incluindo slugs de categoria; considerar testes de regressão para a geração de links e para os testes de ouro; revisar a compatibilidade dos testes do servidor MCP com a versão do SDK e a validade das asserções de erro; monitorar a cobertura e a confiabilidade dos testes após a migração para a API de baixo nível.

---

## Nova atualização 9

Sugestão: Investigar se a reversão de versão de 3.1.0 para 0.1.0 foi intencional e definir critério de versionamento; mapear consumidores do servidor MCP e validar compatibilidade com a FastMCP API v2 antes de ampliar adoção; avaliar inclusão de testes de contrato para a interface do servidor MCP para detectar quebras futuras; manter teste que garante que a engine de documentação não reescreva fixtures de teste; monitorar estabilidade do gate de qualidade Python após sincronização uv.lock e correções de formatação; validar resolução de conflitos em src/infrastructure/mcp/knowledge_server.py e confirmar cobertura dos testes; revisar ajuste em src/release_docs.py para confirmar se é apenas refatoração ou altera saída; avaliar se exclusões ao markdownlint podem ocultar problemas relevantes de lint; monitorar estabilidade da coleta de testes após inclusão das dependências structlog e mcp; considerar automação recorrente da reconciliação do manifesto de documentação e da navegação do MkDocs.

---

## Nova atualização 10

Sugestão: Sugestões sujeitas a revisão humana: investigar se a reversão de versão de 3.1.0 para 0.1.0 foi intencional ou resultado de erro de versionamento, e definir o critério de versionamento a ser seguido. Mapear os consumidores do servidor MCP e validar a compatibilidade com a FastMCP API v2 antes de ampliar a adoção. Avaliar a inclusão de testes de contrato para a interface do servidor MCP, de modo a detectar quebras em futuras migrações de API. Considerar verificação automatizada de legibilidade dos badges gerados (contraste de cor) para evitar regressões visuais. Avaliar a manutenção de um teste que garanta que a engine de documentação não reescreva fixtures de teste. Monitorar a estabilidade do gate de qualidade Python após a sincronização do uv.lock e as correções de formatação e tipagem.

---

## Nova atualização 11

Sugestão: Sugestões sujeitas a revisão humana: validar a resolução de conflitos em src/infrastructure/mcp/knowledge_server.py e confirmar que os testes MCP cobrem o comportamento esperado. Revisar o pequeno ajuste em src/release_docs.py para confirmar se é apenas refatoração ou se altera a saída documental. Avaliar se as exclusões adicionadas ao markdownlint não ocultam problemas relevantes de lint. Monitorar a estabilidade da coleta de testes após a inclusão das dependências structlog e mcp. Considerar automação recorrente da reconciliação do manifesto de documentação e da navegação do MkDocs.

---

## Nova atualização 12

Sugestão: ## Nova atualização

Sugestão: revisar a remoção das variáveis de ambiente TEST_OPENROUTER_KEY e TEST_OPENCODE_KEY nos testes de infraestrutura para confirmar que a configuração e a execução dos testes permanecem corretas. Sugestão: monitorar o gate de formatação Black em novas alterações de código para evitar falhas recorrentes no workflow de qualidade. Sugestão: avaliar a padronização e a revisão da geração automática de documentação via IA.

---

## Nova atualização 13

Sugestão: Sugestões de roadmap: revisar e elevar o score de mutation testing acima do limiar; avaliar a remoção do arquivo .bak; revisar secrets e permissões nos workflows de IA; validar a arquitetura de adaptadores LLM e scraping; expandir testes e fixtures golden; monitorar a qualidade dos prompts de IA.

---

## Nova atualização 14

Sugestão: revisar o repositório para identificar outros arquivos sem newline final no fim do arquivo e aplicar o mesmo critério de formatação. Sugestão: monitorar o gate de formatação Black em novas adições de código.

---

## Nova atualização 15

Sugestão: Validar a exportação lazy do graphql_router para garantir compatibilidade com consumidores. Sugestão: Revisar o manifesto de documentação periodicamente. Sugestão: Automatizar atualização de checksums. Sugestão: Expandir testes de cobertura para GraphQL. Sugestão: Monitorar estabilidade dos testes após adição do plugin syrupy.

---

## Nova atualização 16

Sugestão: Sugestões de roadmap: revisar a refatoração para Clean Architecture e validar compatibilidade de imports antes de adotar os novos módulos. Sugestão: revisar o schema GraphQL com ChangeType e avaliar impactos para consumidores externos. Sugestão: revisar a lógica de fallback do LLMService. Sugestão: validar os novos documentos de API em relação à implementação. Sugestão: monitorar dependências e quality gates.

---

## Nova atualização 17

Sugestão: Revisar a implementação do design system para possíveis expansões, como componentes adicionais e integração com mais temas. Sugestão: Continuar monitorando as atualizações de dependências para manter a estabilidade do CI. Sugestão: Realizar testes de acessibilidade no dashboard para garantir conformidade com as normas.

---

## Nova atualização 18

Sugestão: Revisar a captura genérica de Exception em docs_sync_engine para evitar mascaramento de erros específicos de I/O e parsing JSON. Validar se o import de re em orchestrator.py é necessário ou resíduo. Monitorar a eficácia do orçamento de tokens de saída em chamadas a modelos gratuitos OpenRouter. Ampliar a cobertura de testes para os novos fluxos de deploy e sincronização de documentação. Avaliar automação adicional no sync de documentação com base nos resultados do monitoramento de logs de IA.

---

Sugestão: Otimizar integração com OpenRouter free-tier para melhorar custo-benefício. Expandir funcionalidades do change_collector para cobertura de mais contextos Git/GitHub. Reforçar validação de prompts de IA para garantir qualidade de saída. Implementar monitoramento contínuo de logs AI Docs para detecção precoce de falhas. Avaliar possibilidade de automação adicional no sync de documentação.
