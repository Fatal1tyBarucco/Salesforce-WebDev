<!-- gerado por IA em 2026-11-17T04:10:09+00:00 — revisar antes de publicar -->

# Sugestões de Roadmap

## Nova atualização

Sugestão: Sugestões sujeitas a revisão humana: definir e documentar a política final do portão de qualidade (Black versus Ruff), eliminando a alternância de adição e remoção do job no workflow; mapear os consumidores do servidor MCP e validar a compatibilidade com a FastMCP API antes de ampliar a adoção; avaliar a inclusão de testes de contrato para a interface do servidor MCP, dado que a migração exigiu regeneração dos golden files; revisar o conteúdo produzido pela atualização automática de documentação por IA antes de incorporá-lo à documentação oficial; monitorar a estabilidade dos workflows de documentação e de qualidade após as correções aplicadas; considerar verificação automatizada de que o manifesto de documentação permanece consistente com os artefatos gerados.

---

## Nova atualização

Sugestão: Sugestões sujeitas a revisão humana: validar a consistência do inventário do manifesto de documentação com o gerador de documentação; revisar o comportamento esperado da geração do bloco antes de liberar, confirmando formatação esperada; confirmar que a API testada corresponde ao contrato publicado do MCP após adaptação dos testes.

---

## Nova atualização 2

Sugestão: ## Nova atualização

Sugestão: Sugestões sujeitas a revisão humana: mapear os consumidores do servidor MCP e validar a compatibilidade com a nova API v2 antes de ampliar a adoção; avaliar a inclusão de testes de contrato ou de integração para a interface do servidor MCP, considerando a remoção recente de testes de `call_tool`; revisar a ordem de lógica em `release_docs.py` para garantir que a correção de links não introduza regressões em outros idiomas; monitorar a cobertura dos testes de baixo nível e verificar se a refatoração afetou a confiabilidade dos testes de integração.

---

## Nova atualização 3

Sugestão: Sugestões sujeitas a revisão humana: avaliar validação automatizada de links de release por locale, incluindo slugs de categoria; considerar testes de regressão para a geração de links e para os testes de ouro; revisar a compatibilidade dos testes do servidor MCP com a versão do SDK e a validade das asserções de erro; monitorar a cobertura e a confiabilidade dos testes após a migração para a API de baixo nível.

---

## Nova atualização 4

Sugestão: Investigar se a reversão de versão de 3.1.0 para 0.1.0 foi intencional e definir critério de versionamento; mapear consumidores do servidor MCP e validar compatibilidade com a FastMCP API v2 antes de ampliar adoção; avaliar inclusão de testes de contrato para a interface do servidor MCP para detectar quebras futuras; manter teste que garante que a engine de documentação não reescreva fixtures de teste; monitorar estabilidade do gate de qualidade Python após sincronização uv.lock e correções de formatação; validar resolução de conflitos em src/infrastructure/mcp/knowledge_server.py e confirmar cobertura dos testes; revisar ajuste em src/release_docs.py para confirmar se é apenas refatoração ou altera saída; avaliar se exclusões ao markdownlint podem ocultar problemas relevantes de lint; monitorar estabilidade da coleta de testes após inclusão das dependências structlog e mcp; considerar automação recorrente da reconciliação do manifesto de documentação e da navegação do MkDocs.

---

## Nova atualização 5

Sugestão: Sugestões sujeitas a revisão humana: investigar se a reversão de versão de 3.1.0 para 0.1.0 foi intencional ou resultado de erro de versionamento, e definir o critério de versionamento a ser seguido. Mapear os consumidores do servidor MCP e validar a compatibilidade com a FastMCP API v2 antes de ampliar a adoção. Avaliar a inclusão de testes de contrato para a interface do servidor MCP, de modo a detectar quebras em futuras migrações de API. Considerar verificação automatizada de legibilidade dos badges gerados (contraste de cor) para evitar regressões visuais. Avaliar a manutenção de um teste que garanta que a engine de documentação não reescreva fixtures de teste. Monitorar a estabilidade do gate de qualidade Python após a sincronização do uv.lock e as correções de formatação e tipagem.

---

## Nova atualização 6

Sugestão: Sugestões sujeitas a revisão humana: validar a resolução de conflitos em src/infrastructure/mcp/knowledge_server.py e confirmar que os testes MCP cobrem o comportamento esperado. Revisar o pequeno ajuste em src/release_docs.py para confirmar se é apenas refatoração ou se altera a saída documental. Avaliar se as exclusões adicionadas ao markdownlint não ocultam problemas relevantes de lint. Monitorar a estabilidade da coleta de testes após a inclusão das dependências structlog e mcp. Considerar automação recorrente da reconciliação do manifesto de documentação e da navegação do MkDocs.

---

## Nova atualização 7

Sugestão: ## Nova atualização

Sugestão: revisar a remoção das variáveis de ambiente TEST_OPENROUTER_KEY e TEST_OPENCODE_KEY nos testes de infraestrutura para confirmar que a configuração e a execução dos testes permanecem corretas. Sugestão: monitorar o gate de formatação Black em novas alterações de código para evitar falhas recorrentes no workflow de qualidade. Sugestão: avaliar a padronização e a revisão da geração automática de documentação via IA.

---

## Nova atualização 8

Sugestão: Sugestões de roadmap: revisar e elevar o score de mutation testing acima do limiar; avaliar a remoção do arquivo .bak; revisar secrets e permissões nos workflows de IA; validar a arquitetura de adaptadores LLM e scraping; expandir testes e fixtures golden; monitorar a qualidade dos prompts de IA.

---

## Nova atualização 9

Sugestão: revisar o repositório para identificar outros arquivos sem newline final no fim do arquivo e aplicar o mesmo critério de formatação. Sugestão: monitorar o gate de formatação Black em novas adições de código.

---

## Nova atualização 10

Sugestão: Validar a exportação lazy do graphql_router para garantir compatibilidade com consumidores. Sugestão: Revisar o manifesto de documentação periodicamente. Sugestão: Automatizar atualização de checksums. Sugestão: Expandir testes de cobertura para GraphQL. Sugestão: Monitorar estabilidade dos testes após adição do plugin syrupy.

---

## Nova atualização 11

Sugestão: Sugestões de roadmap: revisar a refatoração para Clean Architecture e validar compatibilidade de imports antes de adotar os novos módulos. Sugestão: revisar o schema GraphQL com ChangeType e avaliar impactos para consumidores externos. Sugestão: revisar a lógica de fallback do LLMService. Sugestão: validar os novos documentos de API em relação à implementação. Sugestão: monitorar dependências e quality gates.

---

## Nova atualização 12

Sugestão: Revisar a implementação do design system para possíveis expansões, como componentes adicionais e integração com mais temas. Sugestão: Continuar monitorando as atualizações de dependências para manter a estabilidade do CI. Sugestão: Realizar testes de acessibilidade no dashboard para garantir conformidade com as normas.

---

## Nova atualização 13

Sugestão: Revisar a captura genérica de Exception em docs_sync_engine para evitar mascaramento de erros específicos de I/O e parsing JSON. Validar se o import de re em orchestrator.py é necessário ou resíduo. Monitorar a eficácia do orçamento de tokens de saída em chamadas a modelos gratuitos OpenRouter. Ampliar a cobertura de testes para os novos fluxos de deploy e sincronização de documentação. Avaliar automação adicional no sync de documentação com base nos resultados do monitoramento de logs de IA.

---

Sugestão: Otimizar integração com OpenRouter free-tier para melhorar custo-benefício. Expandir funcionalidades do change_collector para cobertura de mais contextos Git/GitHub. Reforçar validação de prompts de IA para garantir qualidade de saída. Implementar monitoramento contínuo de logs AI Docs para detecção precoce de falhas. Avaliar possibilidade de automação adicional no sync de documentação.
