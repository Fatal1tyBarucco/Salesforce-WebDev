<!-- gerado por IA em 2026-11-16T16:13:25+00:00 — revisar antes de publicar -->

# Notas de Release

## Nova atualização

## Nova atualização 2

Esta atualização corrige a geração de links de release para a documentação em inglês, passando a usar slugs de categoria em inglês definidos para o locale en_US e montando o link antes do bloco de exibição. A correção tem impacto alto na navegação da documentação em inglês, pois evita links apontando para slugs em português inexistentes.

Também foi feita a migração dos testes do servidor MCP Knowledge Server para a API de baixo nível do SDK, com registro de handlers para ListToolsRequest e CallToolRequest e uso de métodos internos como `_build_tools`, `_search_release_notes`, `_get_release_summary`, `_list_releases` e `_compare_releases`. Essa mudança tem impacto médio na infraestrutura de testes, sem alteração de comportamento de produção.

Não há breaking change identificado nas mudanças classificadas. O risco concentra-se na compatibilidade dos testes MCP com a versão do SDK e na validade das asserções de erro, além da necessidade de validar a geração de links e a regeneração dos testes de ouro.

| Feature | Descrição | Impacto | Público |
| :--- | :--- | :---: | :--- |
| **Corrigir slugs de categorias em inglês para links de release — 📋 bugfix** | A correção ajusta a construção de links para arquivos de release ao localizar categorias em inglê… | 🔴 high | src/release_docs.py · Prioridade: 💡 P1 |
| **Migrar testes do MCP knowledge server para API de baixo nível — 📋 refactor** | Os testes do MCP knowledge server foram ajustados para usar o Server de baixo nível do SDK, regis… | 🟡 medium | tests/infrastructure/mcp/test_knowledge_server.py · Prioridade: 💡 P2 |

## 📊 Distribuição de Impacto

🔴 Alto: **1** (50%) 🔴
🟡 Médio: **1** (50%) 🟡
🟢 Baixo: **0** (0%)

Total: **2 features**

## Mudanças por tipo nesta execução

```text
📋 bugfix             │██████████████████████████████│    1 →
📋 refactor           │██████████████████████████████│    1 →
```

Sparkline da distribuição alto/médio/baixo: ██

## Revisão Necessária

- **Migrar testes do MCP knowledge server para API de baixo nível** — Revisar compatibilidade com a versão do SDK MCP e se as asserções de erro continuam válidas. (0.85)

---

## Nova atualização 3

Esta atualização traz a reescrita dos testes do servidor MCP Knowledge Server para a API FastMCP v2, substituindo a interface antiga por decoradores @tool, com 35 testes atualizados que cobrem search, summary, list, compare e unknown tool. A versão do projeto foi revertida de 3.1.0 para 0.1.0 no pyproject.toml, representando uma breaking change que pode impactar consumidores que dependem de versionamento semântico. Foram corrigidos problemas de qualidade (sincronização uv.lock, formatação Black, mypy), restaurados blocos README no release_docs.py, regenerados arquivos golden de testes de caracterização e incluída documentação automatizada sem alterações funcionais. Impacto: alto para migração do MCP e reversão de versão; médio para correções de badges e golden files; baixo para qualidade de código e documentação. Risco: alto a médio, concentrado na compatibilidade de consumidores do MCP e na confirmação da reversão de versão.

| Feature | Descrição | Impacto | Público |
| :--- | :--- | :---: | :--- |
| **Correção de qualidade: sincronização uv.lock e formatação Black — 📋 bugfix** | Corrigido versionamento no uv.lock (3.1.0 -> 0.1.0) para corresponder ao pyproject.toml, restaura… | 🟡 medium | uv.lock, src/infrastructure/mcp/knowledge_server.py, src/release_docs.py · Prioridade: 💡 P1 |
| **Reescrita completa dos testes do MCP Knowledge Server para FastMCP API — 📋 refactor** | Testes reescritos contra a API FastMCP travada em mcp==1.30.0 (35 testes incluindo dispatch call_… | 🔴 high | tests/infrastructure/mcp/test_knowledge_server.py · Prioridade: 💡 P0 |
| **Restauração do formato de bloco README no release_docs.py — 📋 bugfix** | Restaurado comportamento pré-reconcile do _build_release_block: linhas em branco iniciais e finai… | 🟡 medium | src/release_docs.py, tests/golden/summarizer/ · Prioridade: 💡 P1 |
| **Regeneração de golden files corrompidos do summarizer — 📋 bugfix** | Três arquivos golden (readme_block_pt.md, readme_block_en.md, readme_pt_updated.md) regenerados v… | 🟡 medium | tests/golden/summarizer/readme_block_pt.md, tests/golden/summarizer/readme_block_en.md, tests/golden/summarizer/readme_pt_updated.md · Prioridade: 💡 P1 |
| **Atualização automática de documentação via IA — 📋 documentation** | Commit de documentação automatizada ([skip ci]) sem alterações funcionais; provavelmente atualiza… | 🟢 low | docs/, README* · Prioridade: 💡 P3 |

## 📊 Distribuição de Impacto 2

🔴 Alto: **1** (20%) 🔴
🟡 Médio: **3** (60%) 🟡🟡🟡
🟢 Baixo: **1** (20%) 🟢

Total: **5 features**

## Mudanças por tipo nesta execução 2

```text
📋 bugfix             │██████████████████████████████│    3 →
📋 documentation      │██████████░░░░░░░░░░░░░░░░░░░░│    1 →
📋 refactor           │██████████░░░░░░░░░░░░░░░░░░░░│    1 →
```

Sparkline da distribuição alto/médio/baixo: ▂█▂

## Revisão Necessária 2

- **Reescrita completa dos testes do MCP Knowledge Server para FastMCP API** — Reescrita ampla de testes; validar se novos casos de borda (ToolError, extra_forbid) refletem requisitos de negócio. (0.98)
- **Atualização automática de documentação via IA** — Conteúdo exato não visível no diff; verificar se mudanças são desejadas. (0.70)

---

## Nova atualização 4

Esta atualização concentra-se na migração do servidor MCP para a FastMCP API v2, com reescrita do knowledge_server.py para uso de decoradores @tool no lugar da API anterior baseada em Server.on_list_tools/on_call_tool, além da atualização dos testes para a API assíncrona, correção de erros de mypy e remoção de importações não utilizadas. A dependência mcp passa a exigir a faixa >=2.0.0,<3.

Atenção — breaking change: a mudança de API principal do servidor MCP pode afetar consumidores que ainda utilizem a interface antiga, e a versão declarada no pyproject.toml foi revertida de 3.1.0 para 0.1.0, o que pode impactar consumidores que dependam da versão semântica. Ambos os pontos estão marcados para revisão humana.

Também foram corrigidas a cor padrão da label dos badges, que deixava o texto ilegível, com adição de emojis de impacto e padronização de constantes de cor; a restauração dos arquivos golden dos testes de caracterização, com o escopo da engine de documentação restrito a docs/ e DOC_ROOT_FILES para não reescrever fixtures de teste; correções de qualidade (sincronização do uv.lock, formatação Black e erros de mypy); e atualização do manifesto de documentação com correção de links quebrados.

Impacto: alto para a migração do MCP e para a reversão de versão; médio para as correções de badges e de golden files; baixo para qualidade de código e documentação. Risco: alto a médio, concentrado na compatibilidade de consumidores do MCP e na confirmação da reversão de versão. Ponto de atenção: confirmar se a reversão de versão foi intencional e validar a integração dos consumidores com a nova API do servidor MCP.

| Feature | Descrição | Impacto | Público |
| :--- | :--- | :---: | :--- |
| **Migrar servidor MCP para FastMCP API v2 — 📋 refactor** | Rewrite do knowledge_server.py para utilizar FastMCP com decoradores @tool, substituindo a API an… | 🔴 high | src/infrastructure/mcp/knowledge_server.py, tests/infrastructure/mcp/test_knowledge_server.py, pyproject.toml · Prioridade: 💡 P1 |
| **Corrigir cor padrão de label dos badges e adicionar emojis de impacto — 📋 bugfix** | Corrige texto invisível em badges HTML alterando a cor padrão da label para branco (_DEFAULT_FG =… | 🟡 medium | src/ai/generators/badges.py · Prioridade: 💡 P2 |
| **Restaurar golden files e escopar engine de docs fora de tests/ — 📋 bugfix** | Regenera arquivos golden de characterization tests (readme_block_en.md, readme_block_pt.md, readm… | 🟡 medium | .github/scripts/docs_sync_engine.py, tests/golden/summarizer/readme_block_en.md, tests/golden/summarizer/readme_block_pt.md, tests/golden/summarizer/readme_pt_updated.md, docs/.documentation-manifest.json · Prioridade: 💡 P2 |
| **Reverter versão para 0.1.0 e atualizar dependência mcp — 💥 Breaking Change** | Versão do projeto é revertida de 3.1.0 para 0.1.0 no pyproject.toml, sinalizando uma mudança de c… | 🔴 high | pyproject.toml · Prioridade: 💡 P0 |
| **Corrigir falhas do Python Quality gate — 📋 bugfix** | Corrige problemas de qualidade de código detectados pelo pipeline: sincronização de uv.lock (Ruff… | 🟢 low | uv.lock, pyproject.toml · Prioridade: 💡 P3 |
| **Atualizar manifest e corrigir links em documentação — 📋 documentation** | Atualiza docs/.documentation-manifest.json com novos hashes de arquivos, adiciona referências a C… | 🟢 low | docs/.documentation-manifest.json, .github/scripts/docs_sync_engine.py · Prioridade: 💡 P3 |

## 📊 Distribuição de Impacto 3

🔴 Alto: **2** (33%) 🔴🔴
🟡 Médio: **2** (33%) 🟡🟡
🟢 Baixo: **2** (33%) 🟢🟢

Total: **6 features**

## Mudanças por tipo nesta execução 3

```text
💥 Breaking Change    │██████████░░░░░░░░░░░░░░░░░░░░│    1 →
📋 bugfix             │██████████████████████████████│    3 →
📋 documentation      │██████████░░░░░░░░░░░░░░░░░░░░│    1 →
📋 refactor           │██████████░░░░░░░░░░░░░░░░░░░░│    1 →
```

Sparkline da distribuição alto/médio/baixo: ███

## Revisão Necessária 3

- **Reverter versão para 0.1.0 e atualizar dependência mcp** — Reversão inesperada de versão (3.1.0 → 0.1.0) requer investigação se foi intencional ou se houve erro de versionamento. (0.85)

---

## Nova atualização 5

Esta atualização concentra-se em sincronização documental e em correções de infraestrutura de testes. Foram reconciliados o manifesto de documentação, a navegação do MkDocs e diversos documentos, alinhando inventário, links e conteúdo gerado, incluindo resolução de conflitos de merge em arquivos de documentação. Foi adicionado o script fix_md.py para correção de markdown, com ampliação das exclusões do markdownlint para diretórios de documentação gerada e ADRs, além de correções pontuais de lint. As dependências structlog e mcp foram incluídas no pyproject.toml para corrigir erros de coleta de testes, atendendo aos módulos de observabilidade da infraestrutura e ao knowledge server. Também houve resolução de conflitos de merge em src/infrastructure/mcp/knowledge_server.py e nos testes MCP.

Impacto: predominantemente baixo, com itens de impacto médio associados às dependências e ao servidor MCP. Risco: baixo a médio. Não há breaking change identificado.

Ponto de atenção: a resolução de conflitos em src/infrastructure/mcp/knowledge_server.py e em tests/infrastructure/mcp/test_knowledge_server.py requer revisão, pois o diff completo não está disponível e é necessário confirmar que os testes cobrem o comportamento esperado. Recomenda-se ainda revisar o pequeno ajuste em src/release_docs.py, cuja finalidade não pôde ser determinada a partir das evidências.

| Feature | Descrição | Impacto | Público |
| :--- | :--- | :---: | :--- |
| **Reconciliação da documentação, manifesto e navegação — 📋 documentation** | Atualiza o manifesto de documentação, a navegação do MkDocs e diversos documentos para reconcilia… | 🟢 low | docs/.documentation-manifest.json, mkdocs.yml, docs · Prioridade: 💡 P3 |
| **Adição de script fix_md.py e ajuste de exclusões do markdownlint — 📋 refactor** | Inclui o script fix_md.py para correção de markdown e amplia as exclusões do markdownlint para di… | 🟢 low | .markdownlint.json, fix_md.py, docs · Prioridade: 💡 P3 |
| **Adição das dependências structlog e mcp — 📋 bugfix** | Adiciona structlog e mcp ao pyproject.toml para corrigir erros de coleta de testes. Os commits in… | 🟡 medium | pyproject.toml, src/infrastructure/mcp/knowledge_server.py, observabilidade · Prioridade: 💡 P2 |
| **Resolução de conflitos no knowledge_server e nos testes MCP — 📋 bugfix** | Resolve conflitos de merge em src/infrastructure/mcp/knowledge_server.py e em tests/infrastructur… | 🟡 medium | src/infrastructure/mcp/knowledge_server.py, tests/infrastructure/mcp/test_knowledge_server.py · Prioridade: 💡 P2 |

## 📊 Distribuição de Impacto 4

🔴 Alto: **0** (0%)
🟡 Médio: **2** (50%) 🟡🟡
🟢 Baixo: **2** (50%) 🟢🟢

Total: **4 features**

## Mudanças por tipo nesta execução 4

```text
📋 bugfix             │██████████████████████████████│    2 →
📋 documentation      │███████████████░░░░░░░░░░░░░░░│    1 →
📋 refactor           │███████████████░░░░░░░░░░░░░░░│    1 →
```

Sparkline da distribuição alto/médio/baixo:  ██

## Revisão Necessária 4

- **Resolução de conflitos no knowledge_server e nos testes MCP** — O diff completo não está disponível; é necessário validar a resolução de conflitos e confirmar que os testes cobrem o comportamento esperado do knowledge_server. (0.65)
- **Pequeno ajuste em src/release_docs.py** — Diff detalhado não fornecido; revisar a mudança para confirmar se é apenas refatoração ou se altera saída documental. (0.35)

---

## Nova atualização 6

## Nova atualização 7

Esta atualização inclui uma correção de formatação de código com Black 26.10.0 em unified_client e nos testes relacionados, ajustando expressões ternárias e asserts multilinha para atender aos padrões de estilo e resolver uma falha no workflow de qualidade Python. A alteração é apenas de reformatação, sem mudança de lógica ou comportamento. Também há uma atualização automática de documentação via ferramenta de IA, sem impacto funcional.

Impacto: baixo. Risco: baixo. Não há breaking change identificado.

Ponto de atenção: a remoção das definições das variáveis de ambiente TEST_OPENROUTER_KEY e TEST_OPENCODE_KEY nos testes de infraestrutura requer revisão para confirmar que a execução dos testes permanece correta.

| Feature | Descrição | Impacto | Público |
| :--- | :--- | :---: | :--- |
| **Style fix: Black formatting in unified_client and tests — 📋 refactor** | Correção de formatação de código usando Black 26.10.0, ajustando expressões ternárias e assert mu… | 🟢 low | src/infrastructure/llm_adapters/unified_client.py, tests/infrastructure/llm_adapters/test_unified_client.py, tests/test_characterization.py · Prioridade: 💡 P2 |
| **Documentação: atualização automática via IA — 📋 documentation** | Atualização da documentação via ferramenta de IA, sem alterações funcionais, marcadas com [skip c… | 🟢 low | documentation · Prioridade: 💡 P3 |

## 📊 Distribuição de Impacto 5

🔴 Alto: **0** (0%)
🟡 Médio: **0** (0%)
🟢 Baixo: **2** (100%) 🟢🟢

Total: **2 features**

## Mudanças por tipo nesta execução 5

```text
📋 documentation      │██████████████████████████████│    1 →
📋 refactor           │██████████████████████████████│    1 →
```

Sparkline da distribuição alto/médio/baixo:   █

## Revisão Necessária 5

- **Revisão de remoção de variáveis de ambiente nos testes** — Verificar se a remoção das variáveis de ambiente não quebra a execução dos testes. (0.80)

---

## Nova atualização 8

Implementação da Fase 5 concluída com mutation testing, devcontainer e documentação; criação de workflows de CI/CD com IA; arquitetura de adaptadores LLM e scraping; MCP Knowledge Server; expansão de testes e fixtures golden; configuração de ambiente e qualidade. Correção de headings duplicados em documentação gerada por IA; reconciliação do manifest. Riscos: score de mutation testing abaixo do limiar; arquivo .bak pendente; secrets e permissões nos workflows com placeholder. Possíveis impactos em consumidores devido à remoção do módulo de scraping. Nenhum breaking change confirmado sem suporte.

| Feature | Descrição | Impacto | Público |
| :--- | :--- | :---: | :--- |
| **Finalização da Fase 5 - Mutation testing, devcontainer e documentação — 📋 feature** | Configuração completa do mutmut 2.5.1 para mutation testing com score de 66.67% (limiar de 80% do… | 🔴 high | testes, infraestrutura de desenvolvimento, documentação, qualidade de código · Prioridade: 💡 P0 |
| **Correção de headings duplicados em documentação gerada por IA — 📋 bugfix** | Reescrita da função fix_md024_duplicate_headings em .github/scripts/fix_markdown.py para lidar co… | 🟡 medium | documentação, scripts de automação · Prioridade: 💡 P2 |
| **Reconciliação do manifest de documentação — 📋 documentation** | Atualização do arquivo docs/.documentation-manifest.json com os mapeamentos mais recentes de docu… | 🟢 low | documentação · Prioridade: 💡 P3 |
| **Implementação de workflows de CI/CD com IA e automação — 📋 feature** | Criação de cinco novos workflows GitHub Actions: AI PR Review (revisão automática de PRs via Clau… | 🔴 high | CI/CD, segurança, automação de desenvolvimento · Prioridade: 💡 P0 |
| **Implementação de arquitura de adaptadores LLM e scraping — 📋 refactor** | Criação de uma camada de infraestrutura modular para integração com LLMs, incluindo unified_clien… | 🔴 high | infraestrutura, domínio de dados, integração com LLM · Prioridade: 💡 P0 |
| **Implementação do MCP Knowledge Server — 📋 feature** | Criação do knowledge_server.py em src/infrastructure/mcp/, um servidor MCP (Model Context Protoco… | 🟡 medium | infraestrutura, ferramentas de IA · Prioridade: 💡 P1 |
| **Expansão de testes e fixtures golden files — 📋 feature** | Adição de 28 novos arquivos de teste cobrindo os componentes de infraestrutura: test_cache.py, te… | 🔴 high | testes, qualidade de código · Prioridade: 💡 P0 |
| **Configuração de ambiente de desenvolvimento e ferramentas de qualidade — 📋 refactor** | Adição de .claude/settings.json com configuração de permissões e hooks para automação de qualidad… | 🟡 medium | infraestrutura de desenvolvimento, ferramentas de qualidade, scripts · Prioridade: 💡 P1 |

## 📊 Distribuição de Impacto 6

🔴 Alto: **4** (50%) 🔴🔴🔴🔴
🟡 Médio: **3** (37%) 🟡🟡🟡
🟢 Baixo: **1** (12%) 🟢

Total: **8 features**

## Mudanças por tipo nesta execução 6

```text
📋 bugfix             │███████░░░░░░░░░░░░░░░░░░░░░░░│    1 →
📋 documentation      │███████░░░░░░░░░░░░░░░░░░░░░░░│    1 →
📋 feature            │██████████████████████████████│    4 →
📋 refactor           │███████████████░░░░░░░░░░░░░░░│    2 →
```

Sparkline da distribuição alto/médio/baixo: █▆▂

## Revisão Necessária 6

- **Arquivo service.py.bak pendente de remoção** — Verificar se o arquivo .bak é intencional ou se deve ser removido do repositório. (0.80)
- **Configuração de secrets e permissões nos workflows de IA** — Substituir placeholder do SHA da ação anthropics/claude-code-action por SHA real e revisar configuração de permissões e secrets. (0.75)
- **Score de mutation testing abaixo do limiar estabelecido** — Avaliar necessidade de adicionar testes para elevar o score de mutation testing acima de 80% ou ajustar o limiar. (0.85)
- **Prompts de IA em YAML para classificação, enrichment e reporting** — Revisar prompts para garantir que estão protegidos contra injection e que as instruções são claras e consistentes. (0.70)

---

## Nova atualização 9

Correção de newline no final do arquivo `src/infrastructure/api/__init__.py` para atender ao gate de formatação Black. A alteração não introduz mudança de lógica ou comportamento.

Impacto: baixo. Risco: baixo. Não há breaking change identificado.

| Feature | Descrição | Impacto | Público |
| :--- | :--- | :---: | :--- |
| **Correção de newline no EOF do src/infrastructure/api/**init**.py — 📋 refactor** | Adiciona nova linha ausente no final do arquivo src/infrastructure/api/**init**.py para atender a… | 🟢 low | src/infrastructure/api/**init**.py · Prioridade: 💡 P3 |

## 📊 Distribuição de Impacto 7

🔴 Alto: **0** (0%)
🟡 Médio: **0** (0%)
🟢 Baixo: **1** (100%) 🟢

Total: **1 features**

## Mudanças por tipo nesta execução 7

```text
📋 refactor           │██████████████████████████████│    1 →
```

Sparkline da distribuição alto/médio/baixo:   █

---

## Nova atualização 10

Correção de alto impacto no strawberry-graphql que resolve ModuleNotFoundError em 11 testes, restaurando a capacidade de build e elevando a cobertura para 95,35%; atualização de baixo impacto do manifesto de documentação com novos checksums; e adição do plugin syrupy ao conftest.py para corrigir erros de registro de fixture.

| Feature | Descrição | Impacto | Público |
| :--- | :--- | :---: | :--- |
| **Corrige erro de importação do strawberry-graphql que causava falhas nos testes — 📋 bugfix** | Adiciona strawberry-graphql[fastapi] ao extra healing e implementa exportação lazy do graphql_rou… | 🔴 high | src/infrastructure/api/**init**.py, pyproject.toml, tests/test_infrastructure_api_graphql.py · Prioridade: 💡 P0 |
| **Atualiza o manifesto de documentação com novos checksums de arquivos — 📋 documentation** | Reconcilia o docs/.documentation-manifest.json com checksums atualizados para pyproject.toml, src… | 🟢 low | docs/.documentation-manifest.json · Prioridade: 💡 P3 |
| **Adiciona plugin syrupy ao conftest.py para resolver erros de registro de fixture — 📋 refactor** | Adiciona pytest_plugins = ["syrupy"] ao conftest.py, garantindo que o plugin syrupy seja carregad… | 🟢 low | tests/conftest.py · Prioridade: 💡 P3 |

## 📊 Distribuição de Impacto 8

🔴 Alto: **1** (33%) 🔴
🟡 Médio: **0** (0%)
🟢 Baixo: **2** (66%) 🟢🟢

Total: **3 features**

## Mudanças por tipo nesta execução 8

```text
📋 bugfix             │██████████████████████████████│    1 →
📋 documentation      │██████████████████████████████│    1 →
📋 refactor           │██████████████████████████████│    1 →
```

Sparkline da distribuição alto/médio/baixo: ▄ █

## Revisão Necessária 7

- **Corrige erro de importação do strawberry-graphql que causava falhas nos testes** — Revisão necessária devido a alterações em dependências e exportação lazy; garantir que o GraphQL funcione corretamente. (0.95)
- **Atualiza o manifesto de documentação com novos checksums de arquivos** — Revisão para garantir que os checksums estejam corretos. (0.90)
- **Adiciona plugin syrupy ao conftest.py para resolver erros de registro de fixture** — Revisão para confirmar a ordem de registro do plugin. (0.80)

---

## Nova atualização 11

Esta release implementa uma refatoração para Clean Architecture em src/core e src/infrastructure, com módulos de core, infrastructure e models organizados em camadas desacopladas. Refatoração estrutural de alto impacto pode exigir atualização de imports e deve ser validada quanto a compatibilidade com consumidores existentes. A correção no fallback do LLMService visa preservar a disponibilidade do serviço em falhas de provedores. Ajustes no schema GraphQL com tipos Strawberry e ChangeType podem alterar contratos de API para consumidores externos. A ampliação da cobertura de testes, correções de quality gates, atualizações de dependências e reconciliação documental também foram incluídas. Riscos principais: possíveis imports desatualizados após a refatoração, necessidade de revisão de compatibilidade do schema GraphQL e fallback do LLM.

| Feature | Descrição | Impacto | Público |
| :--- | :--- | :---: | :--- |
| **Implementação da Clean Architecture em src/core e src/infrastructure — 📋 refactor** | Adição de módulos core (classification, enrichment, pipeline, summarization) e infrastructure (ap… | 🔴 high | src/core, src/infrastructure, src/models, src/orchestrator.py, src/main.py · Prioridade: 💡 P1 |
| **Adição de cobertura de teste abrangente (95% meta) — 📋 feature** | Criação de 14 novos arquivos de teste cobrindo core (classification, enrichment, pipeline, summar… | 🟡 medium | tests/test_core_classification_service.py, tests/test_core_enrichment_service.py, tests/test_core_pipeline_orchestrator.py, tests/test_core_summarization_service.py, tests/test_infrastructure_generation.py, tests/test_infrastructure_github.py, tests/test_infrastructure_llm.py, tests/test_infrastructure_llm_coverage.py, tests/test_infrastructure_messaging.py, tests/test_infrastructure_notification_step.py, tests/test_infrastructure_parsing.py, tests/test_infrastructure_routes.py, tests/test_infrastructure_scraping.py, tests/test_infrastructure_storage.py, tests/test_infrastructure_translation.py, tests/test_main_coverage_additional.py, tests/test_models_coverage.py, tests/test_orchestrator_coverage.py · Prioridade: 💡 P2 |
| **Correção de quality gates (ruff, black, mypy, mkdocs) — 📋 bugfix** | Correção de múltiplos problemas de linting e formatação: ISC004 (concatenação implícita de string… | 🟢 low | .github/scripts/build_failure_issue.py, .github/scripts/documentation_reconcile.py, .github/scripts/documentation_sync.py, .github/scripts/fix_markdown.py, .github/scripts/update_changelog_auto.py, src/ai/llm/client.py, src/api.py, src/release_discovery.py, tests/test_ai_docs.py, tests/test_llm_service.py, stubs/openai, stubs/prometheus_client, stubs/syrupy · Prioridade: 💡 P3 |
| **Correção do schema GraphQL com Strawberry types — 📋 bugfix** | Substituição de dict[str, Any] por ChangeType (Strawberry type) no schema GraphQL em src/infrastr… | 🟡 medium | src/infrastructure/api/graphql.py, src/infrastructure/api/**init**.py, pyproject.toml · Prioridade: 💡 P2 |
| **Adição da dependência strawberry-graphql — 📋 bugfix** | Adição do pacote strawberry-graphql às dependências core em pyproject.toml e atualização do uv.lo… | 🟡 medium | pyproject.toml, uv.lock, src/infrastructure/api/graphql.py · Prioridade: 💡 P1 |
| **Fix do chain de fallback do LLMService — 📋 bugfix** | Correção de bug no chain de fallback do LLMService (linhas 147, 158-163 do src/infrastructure/llm… | 🔴 high | src/infrastructure/llm.py, tests/test_infrastructure_llm_coverage.py · Prioridade: 💡 P0 |
| **Atualização de dependência soupsieve (2.9 para 4.0) — ⚡ Performance** | Upgrade da dependência indireta soupsieve de versão 2.9 para 4.0 no grupo uv, aplicado em 1 diret… | 🟢 low | uv.lock, pyproject.toml · Prioridade: 💡 P3 |
| **Atualização de testes para novos limites de retry e tokens — 📋 bugfix** | Ajuste das expectativas de teste em test_ai_docs.py e test_ai_docs_coverage.py para coincidir com… | 🟢 low | tests/test_ai_docs.py, tests/test_ai_docs_coverage.py · Prioridade: 💡 P3 |
| **Reconciliação de documentação e atualização do manifest — 📋 documentation** | Atualização do docs/.documentation-manifest.json com novos mapeamentos entre código e documentaçã… | 🟢 low | docs/.documentation-manifest.json, mkdocs.yml, docs/api/core-classification-service.md, docs/api/core-enrichment-service.md, docs/api/core-pipeline-orchestrator.md, docs/api/core-pipeline-steps.md, docs/api/core-summarization-service.md, docs/architecture/decisions/adr-007-clean-architecture.md · Prioridade: 💡 P3 |

## 📊 Distribuição de Impacto 9

🔴 Alto: **2** (22%) 🔴🔴
🟡 Médio: **3** (33%) 🟡🟡🟡
🟢 Baixo: **4** (44%) 🟢🟢🟢🟢

Total: **9 features**

## Mudanças por tipo nesta execução 9

```text
⚡ Performance        │██████░░░░░░░░░░░░░░░░░░░░░░░░│    1 →
📋 bugfix             │██████████████████████████████│    5 →
📋 documentation      │██████░░░░░░░░░░░░░░░░░░░░░░░░│    1 →
📋 feature            │██████░░░░░░░░░░░░░░░░░░░░░░░░│    1 →
📋 refactor           │██████░░░░░░░░░░░░░░░░░░░░░░░░│    1 →
```

Sparkline da distribuição alto/médio/baixo: ▄▆█

## Revisão Necessária 8

- **Verificação de backwards compatibility da arquitetura** — Executar análise estática de dependências para identificar todos os imports que precisam ser atualizados (0.80)
- **Revisão do schema GraphQL para consumers externos** — Verificar versão do schema GraphQL e comunicar mudanças para consumidores externos se necessário (0.75)
- **Revisão da lógica de fallback do LLMService** — Revisar todos os caminhos de fallback e testes de integração com providers reais (0.85)
- **Validação dos novos documentos de API** — Comparar documentação com código-fonte para verificar consistência (0.70)

---

## Nova atualização 12

Esta release introduz o design system no dashboard com suporte a dark mode e recursos de acessibilidade, além de corrigir o rastreamento de estado de fences no fix_markdown.py e atualizar diversas dependências de ferramentas e bibliotecas para as versões mais recentes.

| Feature | Descrição | Impacto | Público |
| :--- | :--- | :---: | :--- |
| **Aplicar design system ao dashboard com suporte a dark mode e acessibilidade — 📋 feature** | Extração de tokens e componentes reutilizáveis em src/design-system/, migração do dashboard_templ… | 🔴 high | src/dashboard_template.html, src/design-system/ · Prioridade: 💡 P0 |
| **Corrigir rastreamento de estado de fences em fix_markdown.py — 📋 bugfix** | Script passa a rastrear in_fence para distinguir abertura e fechamento de blocos markdown, evitan… | 🟢 low | .github/scripts/fix_markdown.py · Prioridade: 💡 P2 |
| **Atualizar actions/setup-python para v7.1.0 — ⚡ Performance** | Bump da ação actions/setup-python de 7.0.0 para 7.1.0 em workflows de CI. | 🟢 low | .github/workflows/ai-docs.yml, .github/workflows/dependabot-lock-refresh.yml · Prioridade: 💡 P3 |
| **Atualizar astral-sh/setup-uv para v10.3.3 — ⚡ Performance** | Bump da ação astral-sh/setup-uv para versão 10.3.3 em múltiplos workflows. | 🟢 low | .github/workflows/copilot-setup-steps.yml, .github/workflows/dependabot-lock-refresh.yml · Prioridade: 💡 P3 |
| **Atualizar pyasn1 para 0.6.5 — ⚡ Performance** | Bump da dependência indireta pyasn1 de 0.6.4 para 0.6.5 no grupo uv. | 🟢 low | pyproject.toml · Prioridade: 💡 P3 |
| **Atualizar grupo uv com certifi, filelock, langgraph-sdk e virtualenv — ⚡ Performance** | Bump de quatro dependências indiretas do grupo uv para versões mais recentes. | 🟢 low | pyproject.toml · Prioridade: 💡 P3 |
| **Atualizar aiohttp para 3.14.4 — ⚡ Performance** | Bump da dependência direta aiohttp de 3.14.3 para 3.14.4. | 🟢 low | pyproject.toml · Prioridade: 💡 P3 |
| **Atualizar black para 26.10.1 — ⚡ Performance** | Bump da dependência de desenvolvimento black de 26.10.0 para 26.10.1. | 🟢 low | pyproject.toml · Prioridade: 💡 P3 |

## 📊 Distribuição de Impacto 10

🔴 Alto: **1** (12%) 🔴
🟡 Médio: **0** (0%)
🟢 Baixo: **7** (87%) 🟢🟢🟢🟢🟢🟢🟢

Total: **8 features**

## Mudanças por tipo nesta execução 10

```text
⚡ Performance        │██████████████████████████████│    6 →
📋 bugfix             │█████░░░░░░░░░░░░░░░░░░░░░░░░░│    1 →
📋 feature            │█████░░░░░░░░░░░░░░░░░░░░░░░░░│    1 →
```

Sparkline da distribuição alto/médio/baixo: ▁ █

---

## Nova atualização 13

Esta release corrige a falha de deploy no GitHub Pages que impedia a publicação de artefatos de release e afetava a entrega contínua do Intelligence Hub. Ajusta cabeçalhos Markdown para conformidade com lint MD001/MD036 e melhora o upload de artefatos de logs de IA no workflow ai-docs. Introduz gestão de orçamento de tokens de saída no cliente LLM, com variáveis de ambiente e escalonamento exponencial em retentativas para reduzir completions vazias ou truncadas. Adiciona novos testes de cobertura para módulos de IA e documentação. Simplifica o tratamento de exceções no docs_sync_engine, substituindo blocos específicos por captura genérica de Exception, o que pode mascarar erros específicos e requer atenção. Atualiza o manifesto de documentação com novos artefatos gerados por IA. Um import não utilizado em orchestrator.py está sob revisão.

| Feature | Descrição | Impacto | Público |
| :--- | :--- | :---: | :--- |
| **Simplificação de tratamento de exceções no docs_sync_engine — 📋 refactor** | Substituição de múltiplos blocos `except OSError, ValueError:` por `except Exception:` em funções… | 🟢 low | .github/scripts/docs_sync_engine.py · Prioridade: 💡 P3 |
| **Correção do deploy no GitHub Pages com etapa de upload — 📋 bugfix** | Adição de job de build do site (index.html com links aos artefatos), upload do artefato via actio… | 🔴 high | .github/workflows/salesforce_release_intelligence_hub.yml · Prioridade: 💡 P0 |
| **Ajuste de cabeçalhos Markdown para conformidade MD001/MD036 — 📋 bugfix** | Alteração de cabeçalhos `###` para `##` no gerador de relatórios de impacto e adição de spec `tex… | 🟢 low | src/ai/generators/markdown.py · Prioridade: 💡 P3 |
| **Gestão de orçamento de tokens de saída no cliente LLM — 📋 feature** | Introdução de variáveis de ambiente AI_DOCS_MAX_OUTPUT_TOKENS e AI_DOCS_MAX_OUTPUT_TOKENS_LIMIT, … | 🟡 medium | src/ai/llm/client.py · Prioridade: 💡 P1 |
| **Atualização do manifesto de documentação com novos artefatos IA — 📋 documentation** | Adição de referências a docs/ai-generated/release-notes.md, leadership.md, roadmap.md em múltipla… | 🟢 low | docs/.documentation-manifest.json · Prioridade: 💡 P3 |
| **Novos testes de cobertura para módulos IA e docs — 📋 feature** | Adição de test_ai_docs.py, test_ai_docs_coverage.py, test_ai_coverage.py e atualização de test_ma… | 🟡 medium | tests/test_ai_docs.py, tests/test_ai_docs_coverage.py, tests/test_ai_coverage.py, tests/test_main_coverage.py · Prioridade: 💡 P2 |
| **Ajuste no workflow ai-docs para upload de artefatos ocultos — 📋 bugfix** | Mudança de if-no-files-found: ignore para warn e adição de include-hidden-files: true no upload d… | 🟢 low | .github/workflows/ai-docs.yml · Prioridade: 💡 P3 |

## 📊 Distribuição de Impacto 11

🔴 Alto: **1** (14%) 🔴
🟡 Médio: **2** (28%) 🟡🟡
🟢 Baixo: **4** (57%) 🟢🟢🟢🟢

Total: **7 features**

## Mudanças por tipo nesta execução 11

```text
📋 bugfix             │██████████████████████████████│    3 →
📋 documentation      │██████████░░░░░░░░░░░░░░░░░░░░│    1 →
📋 feature            │████████████████████░░░░░░░░░░│    2 →
📋 refactor           │██████████░░░░░░░░░░░░░░░░░░░░│    1 →
```yaml

Sparkline da distribuição alto/médio/baixo: ▂▄█

## Revisão Necessária 9

- **Importação de re no orchestrator.py sem uso aparente** — Baixa confiança ou sinalizada pelo classificador. (0.40)

---

Correções críticas no pipeline de geração de documentação via IA. Corrige falha em completions LLM vazias que impactava a funcionalidade principal. Implementa novo pipeline OpenRouter gratuito com suporte a rate-limiting. Expansão significativa do change_collector.py para coleta de mudanças Git/GitHub. Prevenção de headings duplicados no changelog automático. Correção de caminhos no sync de documentação para ambientes CI. Atualização do manifesto de documentação com novos arquivos.

| Feature | Descrição | Impacto | Público |
| :--- | :--- | :---: | :--- |
| **Correção de falha em completions LLM vazios — 📋 bugfix** | Corrige problema onde respostas do LLM retornavam vazias, impactando a geração automática de docu… | 🔴 high | src/ai/llm/client.py, src/ai/orchestrator.py · Prioridade: 💡 P0 |
| **Adição de pipeline OpenRouter gratuito para documentação — 📋 feature** | Implementa novo pipeline de documentação usando OpenRouter free tier, com suporte a rate-limiting… | 🔴 high | .github/workflows/ai-docs.yml, src/ai/orchestrator.py, src/ai/llm/client.py, src/ai/config/models.py · Prioridade: 💡 P1 |
| **Prevenção de headings duplicados no changelog automático — 📋 bugfix** | Modifica a lógica de atualização automática do changelog para evitar criação de múltiplas seções … | 🟡 medium | .github/scripts/update_changelog_auto.py · Prioridade: 💡 P2 |
| **Correção de caminhos no pipeline de sync de documentação — 📋 bugfix** | Altera uso de /tmp para caminhos relativos ao workspace, garantindo consistência em ambientes CI. | 🟡 medium | .github/workflows/documentation-sync.yml, .github/scripts/docs_sync_engine.py · Prioridade: 💡 P2 |
| **Atualização de manifesto de documentação com novos arquivos — 📋 documentation** | Adiciona novos arquivos ao manifesto de documentação incluindo README.en.md, ai-config-models.md … | 🟢 low | docs/.documentation-manifest.json, mkdocs.yml · Prioridade: 💡 P3 |
| **Expansão significativa do change collector — 📋 feature** | Reescrita completa do change_collector.py com novas funcionalidades de coleta de mudanças Git/Git… | 🔴 high | src/ai/collectors/change_collector.py, src/ai/schemas/change.py, tests/test_ai_docs.py, tests/test_ai_docs_coverage.py · Prioridade: 💡 P1 |
| **Exposição de diagnóstico de falha com testes validados — 📋 feature** | Implementa exposição de diagnóstico de falhas com cobertura de testes validada. | 🟡 medium | src/ai/orchestrator.py, tests/test_ledger/test_service.py · Prioridade: 💡 P2 |

## 📊 Distribuição de Impacto 12

🔴 Alto: **3** (42%) 🔴🔴🔴
🟡 Médio: **3** (42%) 🟡🟡🟡
🟢 Baixo: **1** (14%) 🟢

Total: **7 features**

## Mudanças por tipo nesta execução 12

```text
📋 bugfix             │██████████████████████████████│    3 →
📋 documentation      │██████████░░░░░░░░░░░░░░░░░░░░│    1 →
📋 feature            │██████████████████████████████│    3 →
```

Sparkline da distribuição alto/médio/baixo: ██▂

## Revisão Necessária 10

- **Revisão de alterações no change_collector.py** — Baixa confiança ou sinalizada pelo classificador. (0.70)
- **Validação de novos prompts de IA** — Baixa confiança ou sinalizada pelo classificador. (0.65)
- **Verificação de schemas de documentos gerados** — Baixa confiança ou sinalizada pelo classificador. (0.70)
- **Auditoria de logs AI Docs** — Baixa confiança ou sinalizada pelo classificador. (0.60)
