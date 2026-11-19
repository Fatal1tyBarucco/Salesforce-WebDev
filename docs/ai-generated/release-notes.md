<!-- gerado por IA em 2026-11-19T17:26:25+00:00 — revisar antes de publicar -->

# Notas de Release

## Nova atualização

Esta atualização fortalece a camada de cache e a segurança do pipeline de CI/CD. A camada de cache foi reescrita com escritas atômicas (temp+fsync+os.replace), locks por entrada/namespace com fallback fcntl/msvcrt, checksums SHA-256 canônicos e quarentena com backups rotacionados; o CacheManager passa a usar envelope v2 (schema_version+checksum), com estatísticas por namespace e motivos de evicção, orçamentos LRU com pré-checagem stat-only e clear_expired lazy. O MD5 foi removido por completo do código-fonte, com migração tolerante a partir de hashes MD5 existentes. Um novo store processed_releases baseado em fingerprint, com locking single-flight por release, evita processamento duplicado, e o orquestrador integra single-flight e persistência de estatísticas por execução.

No campo de segurança, o workflow ci-repair foi endurecido contra injeção via eventos workflow_run (alertas críticos de code-injection e alto de untrusted-checkout): os jobs só executam para eventos do mesmo repositório, sem interpolar payloads de fork em blocos run, e arquivos de lock e contadores de teste multiprocess passam a usar permissões owner-only (0o600). A configuração do gitleaks foi corrigida de padrões glob para regex RE2, restaurando a detecção efetiva de segredos.

O pipeline de documentação, que estava quebrado na main, foi reparado: adicionadas as dependências ausentes dos plugins mkdocs-minify e mkdocs-htmlproofer, corrigido o nome da opção validate_external_urls, removido o plugin e a dependência mkdocs-sitemap inexistentes e restaurado o docs/SOURCE_SCHEMA.md, corrompido por um auto-fix de lint. O link checker ganhou resiliência a erros transitórios do GitHub (retry) e o anchor do README em inglês foi corrigido.

Como mudança de tooling, o gate de qualidade migrou integralmente de Black para Ruff Format (lint e formatação em um único job), com remoção do job Black separado e atualização de READMEs e hooks pre-commit. Também foram aplicadas melhorias visuais nos 14 workflows (grupos de log colapsáveis, cores ANSI, run-names dinâmicos e Job Summaries) sem alteração de lógica, corrigida a condição que pula 'uv lock --check' em branches do release-please (agora por padrão de nome de branch) e ajustado o rebase antes do push no job ai-docs para evitar corridas de non-fast-forward com o Documentation Sync.

Riscos e pontos de atenção: a mudança de formato de cache (envelope v2 e remoção de MD5) depende da migração tolerante para não invalidar caches existentes e pode afetar consumidores do formato antigo; as correções de segurança do CodeQL exigem revisão humana para confirmar a mitigação completa dos alertas; e o escopo da evolução para o Release Intelligence Hub (release 264) tem baixa confiança e requer verificação no diff. Recomenda-se validar a compatibilidade dos consumidores de cache após a migração e monitorar o pipeline de documentação após os reparos.

| Feature | Descrição | Impacto | Público |
| :--- | :--- | :---: | :--- |
| **Harden cache layer with atomic writes, locks, integrity checks and fingerprints (ADR-011) — 📋 feature** | Refatoração profunda da camada de cache: cache_io agora usa escritas atômicas (temp+fsync+os.repl… | 🔴 high | src/cache_io.py, src/cache_manager.py, src/processed_releases.py, src/orchestrator.py, src/config.py, src/health.py, src/infrastructure/llm_adapters/cache.py, src/infrastructure/scraping/playwright_adapter.py, tests/test_cache_io.py, tests/test_cache_manager.py, tests/test_cache_robustness.py, tests/test_processed_releases.py, tests/test_orchestrator_cache.py, tests/test_summary_cache_atomic.py, tests/test_history_cache.py, tests/test_trailhead_cache.py, docs/adr/ADR-011.md, docs/cache-management.md, .github/workflows/*.yml · Prioridade: 💡 P0 |
| **CI visual makeover — colors, groups, summaries, dynamic run-names across all workflows — 📋 feature** | Melhoria visual em todos os 14 workflows: adicionado .github/scripts/ci-visual.sh com helpers reu… | 🟢 low | .github/scripts/ci-visual.sh, .github/actions/ci-visual/action.yml, .github/actions/ci-visual/ci-visual.sh, .github/workflows/*.yml · Prioridade: 💡 P3 |
| **Repair Deploy Docs — fix missing mkdocs plugin deps and corrupted SOURCE_SCHEMA.md fences — 📋 bugfix** | Correção do build de documentação que falhava desde 51528de: mkdocs.yml declarava plugins minify … | 🔴 high | mkdocs.yml, pyproject.toml, docs/SOURCE_SCHEMA.md, .github/workflows/documentation-build.yml, .github/workflows/documentation-sync.yml · Prioridade: 💡 P0 |
| **CodeQL security hardening — workflow_run injection guards and file permission fixes — 🔒 Segurança** | Endurecimento contra injeção em ci-repair.yml: CodeQL actions/code-injection (crítico, alerts #11… | 🔴 high | .github/workflows/ci-repair.yml, src/cache_io.py, tests/test_cache_manager.py, tests/test_cache_robustness.py · Prioridade: 💡 P0 |
| **Migrate python-quality.yml from Black to Ruff Format — Ruff-only quality gate — 📋 refactor** | Migração completa do Black para Ruff Format: job Black separado removido (era linhas 85-116); ste… | 🟡 medium | .github/workflows/python-quality.yml, README.md, README.en.md, .pre-commit-config.yaml, pyproject.toml · Prioridade: 💡 P1 |
| **Fix gitleaks config — glob patterns to proper RE2 regex — 📋 bugfix** | Configuração gitleaks usava padrões glob (**) não suportados pelo motor RE2. Alterados para padrõ… | 🟡 medium | .gitleaks.toml · Prioridade: 💡 P1 |
| **Remove non-existent mkdocs-sitemap plugin and dependency — 📋 bugfix** | Pacote mkdocs-sitemap não existe no PyPI, causando falha no build de documentação. Removido plugi… | 🔴 high | mkdocs.yml, pyproject.toml · Prioridade: 💡 P0 |
| **Fix ai-docs rebase before push — avoid non-fast-forward race with Documentation Sync — 📋 bugfix** | Job ai-docs gerava e commitava docs localmente mas push era rejeitado porque bot Documentation Sy… | 🟡 medium | .github/workflows/ai-docs.yml · Prioridade: 💡 P1 |
| **Harden link checker vs transient GitHub errors and fix English README anchor — 📋 bugfix** | Documentation Sync falhou em erro 503 transitório do github.com (link não morto — docs/index.md i… | 🟡 medium | docs/index.md, .github/link-check-config.json, .github/workflows/documentation-sync.yml · Prioridade: 💡 P1 |
| **Release 0.3.2 — patch release with documentation reconciliation — 📋 feature** | Release patch 0.3.2 via release-please; inclui reconciliação de documentação automatizada. | 🟢 low | pyproject.toml, CHANGELOG.md, docs/.documentation-manifest.json · Prioridade: 💡 P3 |
| **Release 0.3.1 — patch release with mkdocs-sitemap fix and uv setup — 📋 feature** | Release patch 0.3.1: correção de dependência mkdocs-sitemap inexistente + configuração uv para sy… | 🟢 low | pyproject.toml, mkdocs.yml, CHANGELOG.md · Prioridade: 💡 P3 |
| **Release 0.3.0 — minor release with Ruff-only migration and audit fixes — 📋 feature** | Release minor 0.3.0 (0.2.4 → 0.3.0): migração completa para Ruff-only (remove Black), correções d… | 🟡 medium | pyproject.toml, .github/workflows/python-quality.yml, README.md, README.en.md, .pre-commit-config.yaml, CHANGELOG.md · Prioridade: 💡 P2 |
| **Fix ci-repair workflow_run injection and untrusted checkout (CodeQL alerts) — 🔒 Segurança** | Duplicado da mudança de segurança acima — mesmo commit 8e7a3eedeb57be8f12a55ee8cc6b4f3bf8feaedb c… | 🔴 high | .github/workflows/ci-repair.yml · Prioridade: 💡 P0 |
| **Skip uv lock check for release-please branches — use branch name pattern — 📋 bugfix** | Condição verificava 'release-please' na mensagem de commit, mas release-please gera commits como … | 🟢 low | .github/workflows/release-please.yml, .github/workflows/python-quality.yml · Prioridade: 💡 P2 |
| **Clean up README.md — remove test commit garbage and auto-generated index — 📋 documentation** | Limpeza do README.md removendo lixo de commits de teste e índice auto-gerado. | 🟢 low | README.md · Prioridade: 💡 P3 |
| **Documentation sync reconciliation — multiple automated bot runs — 📋 documentation** | Múltiplos commits docs(sync): reconcile documentation do bot Documentation Sync (github-actions[b… | 🟢 low | docs/.documentation-manifest.json, drift_report.json, docs/**/*.md · Prioridade: 💡 P3 |
| **Style fixes — ruff-format Python blocks in SOURCE_SCHEMA.md, EOF newlines, trailing whitespace — 📋 refactor** | Formatação ruff em blocos Python dentro de Markdown restaurado (CI 'ruff format --check .' format… | 🟢 low | docs/SOURCE_SCHEMA.md, src/**/*.py, tests/**/*.py · Prioridade: 💡 P3 |
| **Evolve to Release Intelligence Hub (release=264) — defensive — 📋 feature** | Evolução para Release Intelligence Hub (release=264) com abordagem defensiva; atualizações em ass… | 🟡 medium | src/automation/content.py, src/automation/ledger/service.py, src/release_docs.py, src/release_summarizer.py, src/salesforce.py, docs/intelligence_hub/**, docs/deploy_manuals/**, docs/release_readiness/** · Prioridade: 💡 P2 |
| **AI-Docs bot automatic update [skip ci] — 📋 documentation** | Atualização automática via IA [skip ci] pelo AI-Docs Bot; atualização de release notes automática. | 🟢 low | docs/**, CHANGELOG.md · Prioridade: 💡 P3 |

## 📊 Distribuição de Impacto

🔴 Alto: **5** (26%) 🔴🔴🔴🔴🔴
🟡 Médio: **6** (31%) 🟡🟡🟡🟡🟡🟡
🟢 Baixo: **8** (42%) 🟢🟢🟢🟢🟢🟢🟢🟢

Total: **19 features**

## Mudanças por tipo nesta execução

```text
📋 bugfix             │██████████████████████████████│    6 →
📋 documentation      │███████████████░░░░░░░░░░░░░░░│    3 →
📋 feature            │██████████████████████████████│    6 →
📋 refactor           │██████████░░░░░░░░░░░░░░░░░░░░│    2 →
🔒 Segurança          │██████████░░░░░░░░░░░░░░░░░░░░│    2 →
```

Sparkline da distribuição alto/médio/baixo: ▅▆█

## Revisão Necessária

- **CodeQL security hardening — workflow_run injection guards and file permission fixes** — Mudança de segurança crítica; revisão humana obrigatória para validar mitigação completa dos alertas CodeQL. (0.97)
- **Evolve to Release Intelligence Hub (release=264) — defensive** — Commit message em português com poucos detalhes técnicos; verificar escopo real da mudança no diff. (0.75)
- **AI-Docs bot automatic update [skip ci]** — Commit de bot com [skip ci]; conteúdo não verificado no diff; marcar para revisão humana. (0.70)
- **Fix ci-repair workflow_run injection and untrusted checkout (CodeQL alerts)** — Possível duplicação com change 'CodeQL security hardening'; verificar se deve ser mesclado. (0.97)

---

## Nova atualização 2

Esta atualização fortalece a segurança do pipeline de CI/CD ao impedir que workflows privilegiados (ai-pr-review, ai-triage, python-quality, release_notes_pipeline) sejam executados em pull requests originados de forks externos, mitigando riscos de exposição de segredos e operações não autorizadas. O workflow release-please ganha automação completa: token PAT dedicado, auto-merge de PRs de release e sincronização automática do uv.lock após bump de versão, eliminando intervenção manual e inconsistências de lockfile. Correções operacionais incluem: pular verificação 'uv lock --check' em commits de release-please para evitar falhas falsas; adicionar extras 'dev' e 'healing' ao pytest no pipeline de release notes garantindo dependências completas; correções de lint markdown (MD025, MD036, MD051) em docs/index.md; e ajustes de estilo pre-commit (trailing whitespace, final newline). Manifestos de documentação e relatório de drift foram sincronizados. Riscos: a verificação de origem do PR pode afetar contribuidores legítimos de forks se não houver exceções documentadas; a automação de release-please com PAT exige rotação e auditoria do segredo; a sincronização automática de uv.lock deve ser monitorada para regressões de dependência pós-release.

| Feature | Descrição | Impacto | Público |
| :--- | :--- | :---: | :--- |
| **Proteger workflows de CI contra execução em PRs de forks — 🔒 Segurança** | Adicionadas condições de verificação de origem do PR (github.event.pull_request.head.repo.full_na… | 🔴 high | .github/workflows/ai-pr-review.yml, .github/workflows/ai-triage.yml, .github/workflows/python-quality.yml, .github/workflows/release_notes_pipeline.yml · Prioridade: 💡 P0 |
| **Habilitar auto-merge e sincronização automática de uv.lock no release-please — 📋 feature** | Workflow release-please.yml foi atualizado para usar token PAT (secrets.RELEASE_PLEASE_TOKEN), ha… | 🟡 medium | .github/workflows/release-please.yml · Prioridade: 💡 P1 |
| **Corrigir erros de lint markdown em docs/index.md — 📋 bugfix** | Correções aplicadas para atender às regras MD025 (único título H1), MD036 (enfatizar termos com a… | 🟢 low | docs/index.md · Prioridade: 💡 P3 |
| **Aplicar correções de estilo pre-commit (espaço em branco e EOF) — 📋 refactor** | Remoção de espaços em branco no final de linhas e garantia de newline no final de arquivos, confo… | 🟢 low | .github/workflows/ai-pr-review.yml, .github/workflows/ai-triage.yml, .github/workflows/release-please.yml · Prioridade: 💡 P3 |
| **Corrigir sincronização de uv.lock em commits de release — 📋 bugfix** | Adicionada condição para pular a verificação 'uv lock --check' quando a mensagem do commit contém… | 🟡 medium | .github/workflows/python-quality.yml · Prioridade: 💡 P2 |
| **Atualizar comando pytest com extras dev e healing no pipeline de release notes — 📋 bugfix** | Comando de pytest foi atualizado para incluir '--extra dev --extra healing' no workflow release_n… | 🟡 medium | .github/workflows/release_notes_pipeline.yml · Prioridade: 💡 P2 |
| **Sincronizar manifestos de documentação e relatório de drift — 📋 refactor** | Arquivos docs/.documentation-manifest.json e drift_report.json foram atualizados para refletir as… | 🟢 low | docs/.documentation-manifest.json, drift_report.json · Prioridade: 💡 P3 |

## 📊 Distribuição de Impacto 2

🔴 Alto: **1** (14%) 🔴
🟡 Médio: **3** (42%) 🟡🟡🟡
🟢 Baixo: **3** (42%) 🟢🟢🟢

Total: **7 features**

## Mudanças por tipo nesta execução 2

```text
📋 bugfix             │██████████████████████████████│    3 →
📋 feature            │██████████░░░░░░░░░░░░░░░░░░░░│    1 →
📋 refactor           │████████████████████░░░░░░░░░░│    2 →
🔒 Segurança          │██████████░░░░░░░░░░░░░░░░░░░░│    1 →
```

Sparkline da distribuição alto/médio/baixo: ▂██

## Revisão Necessária 2

- **Verificar consistência de hashes no manifesto de documentação** — Revisar se todos os hashes atualizados correspondem a arquivos que foram efetivamente modificados nos commits, e se não há entradas duplicadas ou obsoletas no manifesto. (0.70)

---

## Nova atualização 3

Esta atualização entrega o Release Intelligence Hub para o release 264, adicionando assets de deploy manual, guias de preparação de org, relatórios de prontidão e configuração de sandbox — nova capacidade operacional de alto impacto para processos de release. Em paralelo, estabiliza o pipeline de CI/CD com múltiplas correções críticas: resolve falhas 100% no Intelligence Hub adicionando dependências ausentes (requests, types-html5lib, types-webencodings), torna detect_release.py resiliente a erros de rede eliminando crashes do Scheduled Pipeline, corrige triggers de workflow que causavam execuções vazias (ghost runs) e loops de bot em todo push, e ajusta permissões GitHub Actions inválidas (pull_requests→pull-requests, repository-projects, projects V2, SHA real do claude-code-action). Substitui hooks baseados em shell por scripts Python robustos (pre-commit, pre-push, post-tool-use, session-start) com ruff, mypy e pytest integrados, atingindo 95,55% de cobertura. Refatora o AI Triage como script Python para lidar com conteúdo multilinha. Sincroniza uv.lock com versões de release 0.1.2 a 0.1.7 corrigindo dessincronização recorrente do release-please. Aplica formatação Black para conformidade do gate de qualidade. Inclui correções operacionais no workflow do Intelligence Hub (remove deploy Pages problemático, adiciona git pull --rebase, corrige nome do README) e instala Playwright no job de detecção. Riscos: consumidores de automações dependentes de triggers push podem ter comportamento alterado; migração de hooks shell→Python exige validação de fluxos locais; regeneração de uv.lock em múltiplas versões deve ser monitorada para regressões de dependência.

| Feature | Descrição | Impacto | Público |
| :--- | :--- | :---: | :--- |
| **Implementação do Release Intelligence Hub (release=264) — 📋 feature** | Nova funcionalidade que evolui o sistema para um Release Intelligence Hub, incluindo assets de de… | 🔴 high | intelligence-hub, deploy-manuals, release-readiness, sandbox-config · Prioridade: 💡 P1 |
| **Correção de workflows CI/CD falhando - dependências e resiliência de rede — 📋 bugfix** | Corrige falhas 100% no Intelligence Hub adicionando dependência 'requests', adiciona types-html5l… | 🔴 high | scheduled-pipeline, intelligence-hub, detect-release, ci-dependencies · Prioridade: 💡 P0 |
| **Sistema de hooks Python para qualidade de código (pre-commit, pre-push, post-tool-use, session-start) — 📋 refactor** | Substitui hooks baseados em shell por scripts Python que leem JSON do stdin. Adiciona: post-tool-… | 🟡 medium | .claude/hooks, .claude/settings.json, pre-commit, pre-push, post-tool-use, session-start · Prioridade: 💡 P1 |
| **Correção de triggers de workflow para evitar execuções vazias (ghost runs) e loops de bot — 📋 bugfix** | Múltiplas correções iterativas: remove triggers 'push' de workflows (scheduled-pipeline, ai-triag… | 🔴 high | scheduled-pipeline.yml, ai-triage.yml, ci-repair.yml, ai-pr-review.yml, opencode.yml · Prioridade: 💡 P0 |
| **Correção de permissões GitHub Actions (projects, pull-requests, repository-projects, SHA action) — 📋 bugfix** | Corrige permissões inválidas: 'pull_requests' -> 'pull-requests' (hyphen), usa 'repository-projec… | 🟡 medium | scheduled-pipeline, ai-triage, ai-pr-review, ci-repair, claude-code-action · Prioridade: 💡 P1 |
| **Refatoração do AI Triage como script Python para lidar com conteúdo multilinha — 📋 refactor** | Reescreve o workflow ai-triage.yml (405 linhas alteradas) convertendo lógica de shell para script… | 🟡 medium | ai-triage.yml, workflows/ai-triage · Prioridade: 💡 P2 |
| **Sincronização de uv.lock com versões de release (0.1.2 a 0.1.7) e correção de release-please desync — 📋 bugfix** | Múltiplas correções de uv.lock dessincronizado após release-please bump pyproject.toml sem regene… | 🟡 medium | uv.lock, pyproject.toml, release-please, docs/.documentation-manifest.json, docs/index.md, AGENTS.md · Prioridade: 💡 P1 |
| **Formatação Black aplicada para passar gate Python Quality — 📋 refactor** | Múltiplas aplicações de formatação Black (6 arquivos reformados) para corrigir falhas no gate de … | 🟢 low | src/, scripts/, hooks/ · Prioridade: 💡 P3 |
| **Atualizações de documentação automatizada (reconcile documentation) — 📋 documentation** | Múltiplos commits de sincronização automática de documentação via IA [skip ci], regenerando docum… | 🟢 low | docs/, documentation-manifest.json, drift_report.json · Prioridade: 💡 P3 |
| **Correções no workflow Intelligence Hub - deploy Pages, pull rebase, README filename — 📋 bugfix** | Remove deploy problemático do GitHub Pages do workflow Intelligence Hub, adiciona 'git pull --reb… | 🟡 medium | salesforce_release_intelligence_hub.yml, GitHub Pages deploy, README handling · Prioridade: 💡 P2 |
| **Instalação Playwright e uso 'uv run python' no job detect do Scheduled Pipeline — 📋 bugfix** | Adiciona instalação do Playwright no job de detecção do pipeline agendado e altera execução para … | 🟢 low | scheduled-pipeline.yml, detect_release.py, Playwright · Prioridade: 💡 P3 |

## 📊 Distribuição de Impacto 3

🔴 Alto: **3** (27%) 🔴🔴🔴
🟡 Médio: **5** (45%) 🟡🟡🟡🟡🟡
🟢 Baixo: **3** (27%) 🟢🟢🟢

Total: **11 features**

## Mudanças por tipo nesta execução 3

```text
📋 bugfix             │██████████████████████████████│    6 →
📋 documentation      │█████░░░░░░░░░░░░░░░░░░░░░░░░░│    1 →
📋 feature            │█████░░░░░░░░░░░░░░░░░░░░░░░░░│    1 →
📋 refactor           │███████████████░░░░░░░░░░░░░░░│    3 →
```

Sparkline da distribuição alto/médio/baixo: ▄█▄

---

## Nova atualização 4

Esta atualização concentra-se na estabilidade do pipeline de integração contínua e na modernização do servidor MCP. As correções nos workflows de documentação e de qualidade endereçam falhas que comprometiam a geração automática de documentação e a execução do gate Python, com impacto médio e prioridade alta. A migração do servidor MCP para a FastMCP API, com pinagem do pacote mcp na versão 1.30.0, é a mudança de maior impacto desta execução: ela reescreve a implementação principal do servidor e exige regeneração dos arquivos de teste ouro, podendo afetar integrações que dependem da API MCP anterior. Não há breaking change formalmente classificado, mas consumidores do servidor MCP devem ser validados.

Os demais itens são de impacto baixo: correções de lint Ruff e organização de imports, formatação Black, configuração das portas de qualidade, instalação editável do pacote para o mkdocstrings, reconciliação automática da documentação com atualização de manifesto e a marcação da versão de release com sincronização do arquivo de lock.

Riscos e revisão: a configuração do portão de qualidade Black aparece de forma contraditória entre os commits (adição, remoção e restauração do job), e há um commit de atualização automática de documentação via IA sem detalhes no corpo — ambos sinalizados para revisão humana antes de consolidar a política final.

| Feature | Descrição | Impacto | Público |
| :--- | :--- | :---: | :--- |
| **Correção de falhas no GitHub Actions e sincronização de documentação — 📋 bugfix** | Vários commits corrigem falhas no GitHub Actions, incluindo uso de 'git add -A' no documentation-… | 🟡 medium | .github/workflows/documentation-sync.yml, .github/workflows/documentation-build.yml, .github/workflows/python-quality.yml · Prioridade: 💡 P1 |
| **Migração do servidor MCP para FastMCP API (mcp 1.30.0) — 📋 refactor** | Reescrita de knowledge_server.py para usar FastMCP em vez da API de baixo nível Server, atualizaç… | 🔴 high | src/infrastructure/mcp/knowledge_server.py, tests/infrastructure/mcp/test_knowledge_server.py, pyproject.toml · Prioridade: 💡 P1 |
| **Correções de lint Ruff e organização de imports — 📋 refactor** | Correção de erros E402 (import de nível de módulo no topo do arquivo) e diversos problemas Ruff (… | 🟢 low | src/infrastructure/llm_adapters/unified_client.py, tests/infrastructure/llm_coverage.py, src/domain/llm.py, vários arquivos de teste · Prioridade: 💡 P2 |
| **Reconciliação automática de documentação e atualização de manifesto — 📋 documentation** | Commits docs(sync) reconciliam documentação, atualizam docs/.documentation-manifest.json com novo… | 🟢 low | docs/.documentation-manifest.json, drift_report.json, .github/scripts/docs_sync_engine.py, docs/ · Prioridade: 💡 P3 |
| **Release da versão 0.1.1 — 📋 documentation** | Commits chore(main): release 0.1.1 e atualização de uv.lock para corresponder à versão 0.1.1 no p… | 🟢 low | pyproject.toml, uv.lock, CHANGELOG.md · Prioridade: 💡 P3 |
| **Configuração de portas de qualidade Black e Ruff — 📋 refactor** | Atualização de CLAUDE.md, pyproject.toml, .claude/settings.json e adição de .ruffignore para excl… | 🟢 low | .claude/settings.json, pyproject.toml, .ruffignore, CLAUDE.md · Prioridade: 💡 P2 |
| **Instalação editável do pacote para mkdocstrings — 📋 bugfix** | Adição de src/domain/**init**.py para tornar domain um pacote adequado e atualização do documenta… | 🟢 low | src/domain/**init**.py, .github/workflows/documentation-build.yml · Prioridade: 💡 P2 |
| **Formatação Black e ajustes de estilo de código — 📋 refactor** | Aplicação de formatação Black para corrigir o portão de qualidade Python, incluindo remoção e res… | 🟢 low | .github/workflows/python-quality.yml, arquivos Python diversos · Prioridade: 💡 P3 |

## 📊 Distribuição de Impacto 4

🔴 Alto: **1** (12%) 🔴
🟡 Médio: **1** (12%) 🟡
🟢 Baixo: **6** (75%) 🟢🟢🟢🟢🟢🟢

Total: **8 features**

## Mudanças por tipo nesta execução 4

```text
📋 bugfix             │███████████████░░░░░░░░░░░░░░░│    2 →
📋 documentation      │███████████████░░░░░░░░░░░░░░░│    2 →
📋 refactor           │██████████████████████████████│    4 →
```

Sparkline da distribuição alto/médio/baixo: ▁▁█

## Revisão Necessária 3

- **Configuração contraditória do portão de qualidade Black** — Verificar decisão final entre Black e Ruff como portão de qualidade obrigatório. (0.60)
- **Atualização automática de documentação via IA** — Revisar conteúdo gerado por IA antes de incorporar à documentação oficial. (0.50)

---

## Nova atualização 5

Sincronização do manifesto de documentação com atualização de referências, hashes e metadados de geração, impactando arquivos de documentação associadas, risco baixo de alteração de comportamento funcional. Correção na inicialização de linhas do bloco de release docs, ajustando lista de inicialização de vazia para linha em branco para restaurar formatação esperada, impacto médio na formatação gerada. Adaptação de testes do servidor MCP de release notes para API atual, incluindo objetos query, retorno JSON string e registro de ferramentas via FastMCP; maior parte do impacto na suíte de testes, comportamento pode necessitar de validação adicional.

| Feature | Descrição | Impacto | Público |
| :--- | :--- | :---: | :--- |
| **Sincronização do manifesto de documentação — 📋 documentation** | Atualizou o manifesto de documentação com novas referências, hashes e metadados de geração, inclu… | 🟢 low | docs/.documentation-manifest.json, docs · Prioridade: 💡 P3 |
| **Correção na inicialização de linhas do bloco de release docs — 📋 bugfix** | Ajustou a inicialização da lista de linhas do bloco de release docs, passando de lista vazia para… | 🟡 medium | src/release_docs.py, src/release_summarizer.py · Prioridade: 💡 P2 |
| **Adaptação de testes do servidor MCP de release notes — 📋 refactor** | Reescreveu os testes do MCP knowledge server para usar a API atual, incluindo objetos query, reto… | 🟢 low | tests/infrastructure/mcp/test_knowledge_server.py, src/infrastructure/mcp/knowledge_server.py · Prioridade: 💡 P2 |

## 📊 Distribuição de Impacto 5

🔴 Alto: **0** (0%)
🟡 Médio: **1** (33%) 🟡
🟢 Baixo: **2** (66%) 🟢🟢

Total: **3 features**

## Mudanças por tipo nesta execução 5

```text
📋 bugfix             │██████████████████████████████│    1 →
📋 documentation      │██████████████████████████████│    1 →
📋 refactor           │██████████████████████████████│    1 →
```

Sparkline da distribuição alto/médio/baixo:  ▄█

## Revisão Necessária 4

- **Correção na inicialização de linhas do bloco de release docs** — Revisar o comportamento esperado da geração do bloco antes de liberar. (0.85)
- **Adaptação de testes do servidor MCP de release notes** — Confirmar que a API testada corresponde ao contrato publicado do MCP. (0.90)

---

## Nova atualização 6

## Nova atualização 7

Esta atualização traz uma migração crítica de arquitetura do FastMCP para a API do Servidor MCP v2, que altera a assinatura de `create_server` e a forma de registro de ferramentas, gerando um impacto alto devido à quebra de compatibilidade com clientes que dependiam da API anterior. También corrige a ordem de cálculo de links em `release_docs.py` para garantir que slugs de categorias em inglês sejam aplicados corretamente, evitando links quebrados na documentação (impacto médio). Por fim, refatora os testes do MCP Server, introduzindo a função `_decode` e removendo testes de chamada direta de ferramentas (`call_tool`), o que reduz a cobertura de integração mas simplifica a manutenção (impacto médio).

Riscos principais: quebra de integração com consumidores que utilizavam a API antiga do FastMCP, e a necessidade de verificar se a remoção de testes de integração não mascarou falhas de extremidade a extremidade. Próximos passos: validar a compatibilidade dos consumidores com a nova API, confirmar o registro correto de todos os handlers e avaliar a necessidade de testes de integração alternativos.

| Feature | Descrição | Impacto | Público |
| :--- | :--- | :---: | :--- |
| **Migração do FastMCP para MCP Server API v2 — 💥 Breaking Change** | Substitui a implementação baseada em FastMCP por uma nova arquitetura utilizando Server, CallTool… | 🔴 high | src/infrastructure/mcp/knowledge_server.py, MCP Server Client · Prioridade: 💡 P0 |
| **Correção de ordem de link em release_docs.py — 📋 bugfix** | A variável `link` era calculada antes de ser redefinida para idioma en_US, gerando links incorret… | 🟡 medium | src/release_docs.py, Documentação Gerada · Prioridade: 💡 P1 |
| **Refatoração e simplificação de testes do MCP Server — 📋 refactor** | Testes foram refatorados para usar uma função auxiliar `_decode` que extrai o payload JSON do úni… | 🟡 medium | tests/infrastructure/mcp/test_knowledge_server.py · Prioridade: 💡 P2 |

## 📊 Distribuição de Impacto 6

🔴 Alto: **1** (33%) 🔴
🟡 Médio: **2** (66%) 🟡🟡
🟢 Baixo: **0** (0%)

Total: **3 features**

## Mudanças por tipo nesta execução 6

```text
💥 Breaking Change    │██████████████████████████████│    1 →
📋 bugfix             │██████████████████████████████│    1 →
📋 refactor           │██████████████████████████████│    1 →
```

Sparkline da distribuição alto/médio/baixo: ▄█

## Revisão Necessária 5

- **Migração do FastMCP para MCP Server API v2** — Migração crítica de arquitetura. Requer validação de compatibilidade com consumidores externos e verificação de que todos os handlers estão corretamente registrados. (0.95)
- **Refatoração e simplificação de testes do MCP Server** — Verificar se a remoção de testes de call_tool é intencional e se há testes de integração alternativos. A cobertura de handlers pode ter diminuído. (0.85)

---

## Nova atualização 8

## Nova atualização 9

Esta atualização corrige a geração de links de release para a documentação em inglês, passando a usar slugs de categoria em inglês definidos para o locale en_US e montando o link antes do bloco de exibição. A correção tem impacto alto na navegação da documentação em inglês, pois evita links apontando para slugs em português inexistentes.

Também foi feita a migração dos testes do servidor MCP Knowledge Server para a API de baixo nível do SDK, com registro de handlers para ListToolsRequest e CallToolRequest e uso de métodos internos como _build_tools, _search_release_notes,_get_release_summary, _list_releases e _compare_releases. Essa mudança tem impacto médio na infraestrutura de testes, sem alteração de comportamento de produção.

Não há breaking change identificado nas mudanças classificadas. O risco concentra-se na compatibilidade dos testes MCP com a versão do SDK e na validade das asserções de erro, além da necessidade de validar a geração de links e a regeneração dos testes de ouro.

| Feature | Descrição | Impacto | Público |
| :--- | :--- | :---: | :--- |
| **Corrigir slugs de categorias em inglês para links de release — 📋 bugfix** | A correção ajusta a construção de links para arquivos de release ao localizar categorias em inglê… | 🔴 high | src/release_docs.py · Prioridade: 💡 P1 |
| **Migrar testes do MCP knowledge server para API de baixo nível — 📋 refactor** | Os testes do MCP knowledge server foram ajustados para usar o Server de baixo nível do SDK, regis… | 🟡 medium | tests/infrastructure/mcp/test_knowledge_server.py · Prioridade: 💡 P2 |

## 📊 Distribuição de Impacto 7

🔴 Alto: **1** (50%) 🔴
🟡 Médio: **1** (50%) 🟡
🟢 Baixo: **0** (0%)

Total: **2 features**

## Mudanças por tipo nesta execução 7

```text
📋 bugfix             │██████████████████████████████│    1 →
📋 refactor           │██████████████████████████████│    1 →
```

Sparkline da distribuição alto/médio/baixo: ██

## Revisão Necessária 6

- **Migrar testes do MCP knowledge server para API de baixo nível** — Revisar compatibilidade com a versão do SDK MCP e se as asserções de erro continuam válidas. (0.85)

---

## Nova atualização 10

Esta atualização traz a reescrita dos testes do servidor MCP Knowledge Server para a API FastMCP v2, substituindo a interface antiga por decoradores @tool, com 35 testes atualizados que cobrem search, summary, list, compare e unknown tool. A versão do projeto foi revertida de 3.1.0 para 0.1.0 no pyproject.toml, representando uma breaking change que pode impactar consumidores que dependem de versionamento semântico. Foram corrigidos problemas de qualidade (sincronização uv.lock, formatação Black, mypy), restaurados blocos README no release_docs.py, regenerados arquivos golden de testes de caracterização e incluída documentação automatizada sem alterações funcionais. Impacto: alto para migração do MCP e reversão de versão; médio para correções de badges e golden files; baixo para qualidade de código e documentação. Risco: alto a médio, concentrado na compatibilidade de consumidores do MCP e na confirmação da reversão de versão.

| Feature | Descrição | Impacto | Público |
| :--- | :--- | :---: | :--- |
| **Correção de qualidade: sincronização uv.lock e formatação Black — 📋 bugfix** | Corrigido versionamento no uv.lock (3.1.0 -> 0.1.0) para corresponder ao pyproject.toml, restaura… | 🟡 medium | uv.lock, src/infrastructure/mcp/knowledge_server.py, src/release_docs.py · Prioridade: 💡 P1 |
| **Reescrita completa dos testes do MCP Knowledge Server para FastMCP API — 📋 refactor** | Testes reescritos contra a API FastMCP travada em mcp==1.30.0 (35 testes incluindo dispatch call_… | 🔴 high | tests/infrastructure/mcp/test_knowledge_server.py · Prioridade: 💡 P0 |
| **Restauração do formato de bloco README no release_docs.py — 📋 bugfix** | Restaurado comportamento pré-reconcile do _build_release_block: linhas em branco iniciais e finai… | 🟡 medium | src/release_docs.py, tests/golden/summarizer/ · Prioridade: 💡 P1 |
| **Regeneração de golden files corrompidos do summarizer — 📋 bugfix** | Três arquivos golden (readme_block_pt.md, readme_block_en.md, readme_pt_updated.md) regenerados v… | 🟡 medium | tests/golden/summarizer/readme_block_pt.md, tests/golden/summarizer/readme_block_en.md, tests/golden/summarizer/readme_pt_updated.md · Prioridade: 💡 P1 |
| **Atualização automática de documentação via IA — 📋 documentation** | Commit de documentação automatizada ([skip ci]) sem alterações funcionais; provavelmente atualiza… | 🟢 low | docs/, README* · Prioridade: 💡 P3 |

## 📊 Distribuição de Impacto 8

🔴 Alto: **1** (20%) 🔴
🟡 Médio: **3** (60%) 🟡🟡🟡
🟢 Baixo: **1** (20%) 🟢

Total: **5 features**

## Mudanças por tipo nesta execução 8

```text
📋 bugfix             │██████████████████████████████│    3 →
📋 documentation      │██████████░░░░░░░░░░░░░░░░░░░░│    1 →
📋 refactor           │██████████░░░░░░░░░░░░░░░░░░░░│    1 →
```

Sparkline da distribuição alto/médio/baixo: ▂█▂

## Revisão Necessária 7

- **Reescrita completa dos testes do MCP Knowledge Server para FastMCP API** — Reescrita ampla de testes; validar se novos casos de borda (ToolError, extra_forbid) refletem requisitos de negócio. (0.98)
- **Atualização automática de documentação via IA** — Conteúdo exato não visível no diff; verificar se mudanças são desejadas. (0.70)

---

## Nova atualização 11

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

## 📊 Distribuição de Impacto 9

🔴 Alto: **2** (33%) 🔴🔴
🟡 Médio: **2** (33%) 🟡🟡
🟢 Baixo: **2** (33%) 🟢🟢

Total: **6 features**

## Mudanças por tipo nesta execução 9

```text
💥 Breaking Change    │██████████░░░░░░░░░░░░░░░░░░░░│    1 →
📋 bugfix             │██████████████████████████████│    3 →
📋 documentation      │██████████░░░░░░░░░░░░░░░░░░░░│    1 →
📋 refactor           │██████████░░░░░░░░░░░░░░░░░░░░│    1 →
```

Sparkline da distribuição alto/médio/baixo: ███

## Revisão Necessária 8

- **Reverter versão para 0.1.0 e atualizar dependência mcp** — Reversão inesperada de versão (3.1.0 → 0.1.0) requer investigação se foi intencional ou se houve erro de versionamento. (0.85)

---

## Nova atualização 12

Esta atualização concentra-se em sincronização documental e em correções de infraestrutura de testes. Foram reconciliados o manifesto de documentação, a navegação do MkDocs e diversos documentos, alinhando inventário, links e conteúdo gerado, incluindo resolução de conflitos de merge em arquivos de documentação. Foi adicionado o script fix_md.py para correção de markdown, com ampliação das exclusões do markdownlint para diretórios de documentação gerada e ADRs, além de correções pontuais de lint. As dependências structlog e mcp foram incluídas no pyproject.toml para corrigir erros de coleta de testes, atendendo aos módulos de observabilidade da infraestrutura e ao knowledge server. Também houve resolução de conflitos de merge em src/infrastructure/mcp/knowledge_server.py e nos testes MCP.

Impacto: predominantemente baixo, com itens de impacto médio associados às dependências e ao servidor MCP. Risco: baixo a médio. Não há breaking change identificado.

Ponto de atenção: a resolução de conflitos em src/infrastructure/mcp/knowledge_server.py e em tests/infrastructure/mcp/test_knowledge_server.py requer revisão, pois o diff completo não está disponível e é necessário confirmar que os testes cobrem o comportamento esperado. Recomenda-se ainda revisar o pequeno ajuste em src/release_docs.py, cuja finalidade não pôde ser determinada a partir das evidências.

| Feature | Descrição | Impacto | Público |
| :--- | :--- | :---: | :--- |
| **Reconciliação da documentação, manifesto e navegação — 📋 documentation** | Atualiza o manifesto de documentação, a navegação do MkDocs e diversos documentos para reconcilia… | 🟢 low | docs/.documentation-manifest.json, mkdocs.yml, docs · Prioridade: 💡 P3 |
| **Adição de script fix_md.py e ajuste de exclusões do markdownlint — 📋 refactor** | Inclui o script fix_md.py para correção de markdown e amplia as exclusões do markdownlint para di… | 🟢 low | .markdownlint.json, fix_md.py, docs · Prioridade: 💡 P3 |
| **Adição das dependências structlog e mcp — 📋 bugfix** | Adiciona structlog e mcp ao pyproject.toml para corrigir erros de coleta de testes. Os commits in… | 🟡 medium | pyproject.toml, src/infrastructure/mcp/knowledge_server.py, observabilidade · Prioridade: 💡 P2 |
| **Resolução de conflitos no knowledge_server e nos testes MCP — 📋 bugfix** | Resolve conflitos de merge em src/infrastructure/mcp/knowledge_server.py e em tests/infrastructur… | 🟡 medium | src/infrastructure/mcp/knowledge_server.py, tests/infrastructure/mcp/test_knowledge_server.py · Prioridade: 💡 P2 |

## 📊 Distribuição de Impacto 10

🔴 Alto: **0** (0%)
🟡 Médio: **2** (50%) 🟡🟡
🟢 Baixo: **2** (50%) 🟢🟢

Total: **4 features**

## Mudanças por tipo nesta execução 10

```text
📋 bugfix             │██████████████████████████████│    2 →
📋 documentation      │███████████████░░░░░░░░░░░░░░░│    1 →
📋 refactor           │███████████████░░░░░░░░░░░░░░░│    1 →
```

Sparkline da distribuição alto/médio/baixo:  ██

## Revisão Necessária 9

- **Resolução de conflitos no knowledge_server e nos testes MCP** — O diff completo não está disponível; é necessário validar a resolução de conflitos e confirmar que os testes cobrem o comportamento esperado do knowledge_server. (0.65)
- **Pequeno ajuste em src/release_docs.py** — Diff detalhado não fornecido; revisar a mudança para confirmar se é apenas refatoração ou se altera saída documental. (0.35)

---

## Nova atualização 13

## Nova atualização 14

Esta atualização inclui uma correção de formatação de código com Black 26.10.0 em unified_client e nos testes relacionados, ajustando expressões ternárias e asserts multilinha para atender aos padrões de estilo e resolver uma falha no workflow de qualidade Python. A alteração é apenas de reformatação, sem mudança de lógica ou comportamento. Também há uma atualização automática de documentação via ferramenta de IA, sem impacto funcional.

Impacto: baixo. Risco: baixo. Não há breaking change identificado.

Ponto de atenção: a remoção das definições das variáveis de ambiente TEST_OPENROUTER_KEY e TEST_OPENCODE_KEY nos testes de infraestrutura requer revisão para confirmar que a execução dos testes permanece correta.

| Feature | Descrição | Impacto | Público |
| :--- | :--- | :---: | :--- |
| **Style fix: Black formatting in unified_client and tests — 📋 refactor** | Correção de formatação de código usando Black 26.10.0, ajustando expressões ternárias e assert mu… | 🟢 low | src/infrastructure/llm_adapters/unified_client.py, tests/infrastructure/llm_adapters/test_unified_client.py, tests/test_characterization.py · Prioridade: 💡 P2 |
| **Documentação: atualização automática via IA — 📋 documentation** | Atualização da documentação via ferramenta de IA, sem alterações funcionais, marcadas com [skip c… | 🟢 low | documentation · Prioridade: 💡 P3 |

## 📊 Distribuição de Impacto 11

🔴 Alto: **0** (0%)
🟡 Médio: **0** (0%)
🟢 Baixo: **2** (100%) 🟢🟢

Total: **2 features**

## Mudanças por tipo nesta execução 11

```text
📋 documentation      │██████████████████████████████│    1 →
📋 refactor           │██████████████████████████████│    1 →
```

Sparkline da distribuição alto/médio/baixo:   █

## Revisão Necessária 10

- **Revisão de remoção de variáveis de ambiente nos testes** — Verificar se a remoção das variáveis de ambiente não quebra a execução dos testes. (0.80)

---

## Nova atualização 15

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

## 📊 Distribuição de Impacto 12

🔴 Alto: **4** (50%) 🔴🔴🔴🔴
🟡 Médio: **3** (37%) 🟡🟡🟡
🟢 Baixo: **1** (12%) 🟢

Total: **8 features**

## Mudanças por tipo nesta execução 12

```text
📋 bugfix             │███████░░░░░░░░░░░░░░░░░░░░░░░│    1 →
📋 documentation      │███████░░░░░░░░░░░░░░░░░░░░░░░│    1 →
📋 feature            │██████████████████████████████│    4 →
📋 refactor           │███████████████░░░░░░░░░░░░░░░│    2 →
```

Sparkline da distribuição alto/médio/baixo: █▆▂

## Revisão Necessária 11

- **Arquivo service.py.bak pendente de remoção** — Verificar se o arquivo .bak é intencional ou se deve ser removido do repositório. (0.80)
- **Configuração de secrets e permissões nos workflows de IA** — Substituir placeholder do SHA da ação anthropics/claude-code-action por SHA real e revisar configuração de permissões e secrets. (0.75)
- **Score de mutation testing abaixo do limiar estabelecido** — Avaliar necessidade de adicionar testes para elevar o score de mutation testing acima de 80% ou ajustar o limiar. (0.85)
- **Prompts de IA em YAML para classificação, enrichment e reporting** — Revisar prompts para garantir que estão protegidos contra injection e que as instruções são claras e consistentes. (0.70)

---

## Nova atualização 16

Correção de newline no final do arquivo `src/infrastructure/api/__init__.py` para atender ao gate de formatação Black. A alteração não introduz mudança de lógica ou comportamento.

Impacto: baixo. Risco: baixo. Não há breaking change identificado.

| Feature | Descrição | Impacto | Público |
| :--- | :--- | :---: | :--- |
| **Correção de newline no EOF do src/infrastructure/api/**init**.py — 📋 refactor** | Adiciona nova linha ausente no final do arquivo src/infrastructure/api/**init**.py para atender a… | 🟢 low | src/infrastructure/api/**init**.py · Prioridade: 💡 P3 |

## 📊 Distribuição de Impacto 13

🔴 Alto: **0** (0%)
🟡 Médio: **0** (0%)
🟢 Baixo: **1** (100%) 🟢

Total: **1 features**

## Mudanças por tipo nesta execução 13

```text
📋 refactor           │██████████████████████████████│    1 →
```

Sparkline da distribuição alto/médio/baixo:   █

---

## Nova atualização 17

Correção de alto impacto no strawberry-graphql que resolve ModuleNotFoundError em 11 testes, restaurando a capacidade de build e elevando a cobertura para 95,35%; atualização de baixo impacto do manifesto de documentação com novos checksums; e adição do plugin syrupy ao conftest.py para corrigir erros de registro de fixture.

| Feature | Descrição | Impacto | Público |
| :--- | :--- | :---: | :--- |
| **Corrige erro de importação do strawberry-graphql que causava falhas nos testes — 📋 bugfix** | Adiciona strawberry-graphql[fastapi] ao extra healing e implementa exportação lazy do graphql_rou… | 🔴 high | src/infrastructure/api/**init**.py, pyproject.toml, tests/test_infrastructure_api_graphql.py · Prioridade: 💡 P0 |
| **Atualiza o manifesto de documentação com novos checksums de arquivos — 📋 documentation** | Reconcilia o docs/.documentation-manifest.json com checksums atualizados para pyproject.toml, src… | 🟢 low | docs/.documentation-manifest.json · Prioridade: 💡 P3 |
| **Adiciona plugin syrupy ao conftest.py para resolver erros de registro de fixture — 📋 refactor** | Adiciona pytest_plugins = ["syrupy"] ao conftest.py, garantindo que o plugin syrupy seja carregad… | 🟢 low | tests/conftest.py · Prioridade: 💡 P3 |

## 📊 Distribuição de Impacto 14

🔴 Alto: **1** (33%) 🔴
🟡 Médio: **0** (0%)
🟢 Baixo: **2** (66%) 🟢🟢

Total: **3 features**

## Mudanças por tipo nesta execução 14

```text
📋 bugfix             │██████████████████████████████│    1 →
📋 documentation      │██████████████████████████████│    1 →
📋 refactor           │██████████████████████████████│    1 →
```

Sparkline da distribuição alto/médio/baixo: ▄ █

## Revisão Necessária 12

- **Corrige erro de importação do strawberry-graphql que causava falhas nos testes** — Revisão necessária devido a alterações em dependências e exportação lazy; garantir que o GraphQL funcione corretamente. (0.95)
- **Atualiza o manifesto de documentação com novos checksums de arquivos** — Revisão para garantir que os checksums estejam corretos. (0.90)
- **Adiciona plugin syrupy ao conftest.py para resolver erros de registro de fixture** — Revisão para confirmar a ordem de registro do plugin. (0.80)

---

## Nova atualização 18

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

## 📊 Distribuição de Impacto 15

🔴 Alto: **2** (22%) 🔴🔴
🟡 Médio: **3** (33%) 🟡🟡🟡
🟢 Baixo: **4** (44%) 🟢🟢🟢🟢

Total: **9 features**

## Mudanças por tipo nesta execução 15

```text
⚡ Performance        │██████░░░░░░░░░░░░░░░░░░░░░░░░│    1 →
📋 bugfix             │██████████████████████████████│    5 →
📋 documentation      │██████░░░░░░░░░░░░░░░░░░░░░░░░│    1 →
📋 feature            │██████░░░░░░░░░░░░░░░░░░░░░░░░│    1 →
📋 refactor           │██████░░░░░░░░░░░░░░░░░░░░░░░░│    1 →
```

Sparkline da distribuição alto/médio/baixo: ▄▆█

## Revisão Necessária 13

- **Verificação de backwards compatibility da arquitetura** — Executar análise estática de dependências para identificar todos os imports que precisam ser atualizados (0.80)
- **Revisão do schema GraphQL para consumers externos** — Verificar versão do schema GraphQL e comunicar mudanças para consumidores externos se necessário (0.75)
- **Revisão da lógica de fallback do LLMService** — Revisar todos os caminhos de fallback e testes de integração com providers reais (0.85)
- **Validação dos novos documentos de API** — Comparar documentação com código-fonte para verificar consistência (0.70)

---

## Nova atualização 19

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

## 📊 Distribuição de Impacto 16

🔴 Alto: **1** (12%) 🔴
🟡 Médio: **0** (0%)
🟢 Baixo: **7** (87%) 🟢🟢🟢🟢🟢🟢🟢

Total: **8 features**

## Mudanças por tipo nesta execução 16

```text
⚡ Performance        │██████████████████████████████│    6 →
📋 bugfix             │█████░░░░░░░░░░░░░░░░░░░░░░░░░│    1 →
📋 feature            │█████░░░░░░░░░░░░░░░░░░░░░░░░░│    1 →
```

Sparkline da distribuição alto/médio/baixo: ▁ █

---

## Nova atualização 20

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

## 📊 Distribuição de Impacto 17

🔴 Alto: **1** (14%) 🔴
🟡 Médio: **2** (28%) 🟡🟡
🟢 Baixo: **4** (57%) 🟢🟢🟢🟢

Total: **7 features**

## Mudanças por tipo nesta execução 17

```text
📋 bugfix             │██████████████████████████████│    3 →
📋 documentation      │██████████░░░░░░░░░░░░░░░░░░░░│    1 →
📋 feature            │████████████████████░░░░░░░░░░│    2 →
📋 refactor           │██████████░░░░░░░░░░░░░░░░░░░░│    1 →
```yaml

Sparkline da distribuição alto/médio/baixo: ▂▄█

## Revisão Necessária 14

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

## 📊 Distribuição de Impacto 18

🔴 Alto: **3** (42%) 🔴🔴🔴
🟡 Médio: **3** (42%) 🟡🟡🟡
🟢 Baixo: **1** (14%) 🟢

Total: **7 features**

## Mudanças por tipo nesta execução 18

```text
📋 bugfix             │██████████████████████████████│    3 →
📋 documentation      │██████████░░░░░░░░░░░░░░░░░░░░│    1 →
📋 feature            │██████████████████████████████│    3 →
```

Sparkline da distribuição alto/médio/baixo: ██▂

## Revisão Necessária 15

- **Revisão de alterações no change_collector.py** — Baixa confiança ou sinalizada pelo classificador. (0.70)
- **Validação de novos prompts de IA** — Baixa confiança ou sinalizada pelo classificador. (0.65)
- **Verificação de schemas de documentos gerados** — Baixa confiança ou sinalizada pelo classificador. (0.70)
- **Auditoria de logs AI Docs** — Baixa confiança ou sinalizada pelo classificador. (0.60)
