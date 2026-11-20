# Catálogo de Automação

Inventário público e descritivo de todos os artefatos de automação do repositório:
workflows do GitHub Actions, scripts de CI, scripts utilitários, manifestos
Kubernetes e prompts versionados. A cobertura deste catálogo é verificada
deterministicamente pelo validador de contrato (`.github/scripts/docs_contract.py`,
ADR-012): todo artefato documentável precisa de cobertura documental prose.

O índice gerado por código em [Índice do Repositório](../reference/repo-index.md)
lista os mesmos artefatos com links; esta página fornece a descrição funcional.

## Workflows (`.github/workflows/`)

| Workflow | Gatilhos | Função |
| :--- | :--- | :--- |
| `.github/workflows/python-quality.yml` | push (main/develop), pull_request, dispatch | Gates de qualidade: Ruff lint + format, mypy, pytest com cobertura mínima de 95%. |
| `.github/workflows/release_notes_pipeline.yml` | schedule (segunda 08:00 UTC), dispatch | Pipeline principal de extração, classificação e versionamento das Release Notes. |
| `.github/workflows/scheduled-pipeline.yml` | schedule (segunda 08:00 UTC), dispatch | Knowledge-as-Code: detecta nova release (`scripts/detect_release.py`) e processa incrementalmente. |
| `.github/workflows/salesforce_release_intelligence_hub.yml` | schedule (segunda 04:00 UTC), dispatch | Intelligence Hub defensivo: consolida inteligência de releases, atualiza README bilíngue e publica artefatos. |
| `.github/workflows/documentation-sync.yml` | push (main), schedule (a cada 6 h), dispatch | Reconciliação determinística da documentação (engine LLM-free) com guards anti-loop e commit do bot. |
| `.github/workflows/documentation-build.yml` | push (main, paths de docs/src/releases), dispatch | Build MkDocs strict, versionamento com mike e deploy oficial do GitHub Pages (upload-pages-artifact + deploy-pages). |
| `.github/workflows/ai-docs.yml` | push (main/release, paths de src), dispatch, workflow_call | Geração de documentação por IA (OpenRouter free) com auditoria em `docs/.ai-logs/` e publicação via commit ou PR. |
| `.github/workflows/ai-pr-review.yml` | pull_request, pull_request_review, issue_comment | Revisão automática de PRs por IA, incluindo auditoria de segurança. |
| `.github/workflows/ai-triage.yml` | issues, pull_request | Triagem e rotulagem automática de issues e PRs por IA. |
| `.github/workflows/ci-repair.yml` | workflow_run | Reparo automático de falhas de CI; jobs privilegiados protegidos por guard de mesmo repositório e sem interpolação de payload em `run:`. |
| `.github/workflows/opencode.yml` | issue_comment, pull_request_review_comment | Executa o agente opencode sob comando `/oc fix` em issues de falha de qualidade; requer `OPENCODE_API_KEY`. |
| `.github/workflows/release-please.yml` | push (main) | Release PRs semânticos (release-type python) com sincronização de `uv.lock` pós-bump. |
| `.github/workflows/dependabot-lock-refresh.yml` | pull_request_target | Atualiza `uv.lock` em PRs do Dependabot e do release-please (guard de mesmo repositório), eliminando a janela de desync pós-release. |
| `.github/workflows/dependency-review.yml` | pull_request | Revisão de dependências introduzidas por PRs (diff de licenças e vulnerabilidades). |
| `.github/workflows/copilot-setup-steps.yml` | push/PR (paths do próprio arquivo), dispatch | Prepara o ambiente de execução do agente GitHub Copilot (setup de dependências do repositório). |
| `.github/workflows/docs-deps-refresh.yml` | schedule (segunda 05:23 UTC), dispatch | Mantém o mkdocs-material na versão mais recente dentro do pin (<10): compara lock × PyPI, valida strict + contrato e abre PR (ADR-012, req 3.6). |
| `.github/workflows/docs-version-backfill.yml` | dispatch | Backfill best-effort de uma versão de docs por tag de release (v*) no ledger do mike; falhas por tag registradas no sumário; alias latest preservado (ADR-012, req 3.4). |

Detalhes de operação, runbooks e histórico de correções: [Operações de Workflow](../maintenance/workflow-operations.md)
e [ARQUITETURA](../ARQUITETURA.md).

## Scripts de CI (`.github/scripts/`)

| Script | Função |
| :--- | :--- |
| `.github/scripts/docs_sync_engine.py` | Engine determinística de reconciliação (stdlib-only): inventário por blob SHA, audit, reconcile bidirecional com histórico de remoções, manifest e índice do repositório. |
| `.github/scripts/docs_contract.py` | Validador do contrato de documentação (ADR-012): classifica divergências em OK/ÓRFÃO/OMITO/OBSOLETO/DIVERGENTE e falha o build em qualquer divergência. |
| `.github/scripts/documentation_sync.py` | Engine predecessora de inventário, manifest e drift detection (Documentation Intelligence). |
| `.github/scripts/documentation_reconcile.py` | Braço LLM da reconciliação: consome o drift report e pede ao LLMService (Gemini → OpenCode → OpenRouter) a correção de prose; superfície escrevível restrita a `docs/`, READMEs e `mkdocs.yml`. |
| `.github/scripts/fix_markdown.py` | Correções determinísticas de lint markdown (MD022, MD024, MD032, MD040, MD047, MD012, MD009) com rastreamento de estado de fences. |
| `.github/scripts/update_changelog_auto.py` | Atualiza `docs/changelog.md` apenas com commits de grande impacto (idempotente). |
| `.github/scripts/build_failure_issue.py` | Constrói o corpo didático de issue de diagnóstico de falha do Release Notes Pipeline. |
| `.github/scripts/llm_fallback.py` | Reparo assistido por LLM quando o reparo determinístico não resolve todos os erros. |
| `.github/scripts/select_free_model.py` | Seleciona dinamicamente um modelo free-tier saudável no início de cada execução de IA. |
| `.github/scripts/progress.sh` | Logging de progresso por estágio para steps do GitHub Actions. |
| `.github/scripts/ci-visual.sh` | Helpers visuais de CI (banners, grupos de log, tabelas de sumário, cores ANSI). |

## Scripts utilitários (`scripts/`)

| Script | Função |
| :--- | :--- |
| `scripts/detect_release.py` | Detecta nova release Salesforce para o workflow scheduled-pipeline; fail-safe (retorna `has-new-release=false` em erro). |
| `scripts/generate_pr_body.py` | Gera o corpo do PR aberto pelo scheduled pipeline. |
| `scripts/cache_maintenance.py` | Manutenção explícita do cache (ADR-011, R5/R8): varredura completa de TTLs e quarentena. |
| `scripts/quality-check-local.sh` | Wrapper local das verificações de qualidade (lint, formatação, tipos e testes). |
| `scripts/restore_releases.py` | Restaura releases apagadas no GitHub a partir do diretório `releases/` e marca a mais recente como latest. |
| `scripts/restore_releases.sh` | Versão shell do procedimento de restauração de releases. |
| `scripts/promptfoo_prompts.py` | Loaders promptfoo dos prompts de produção (bootstrap de sys.path; eval keyless de fidelidade ao manifest, ADR-012). |
| `scripts/promptfoo_echo.py` | Provider determinístico do promptfoo para avaliação de fidelidade do prompt sem chaves de API. |

## Infraestrutura Kubernetes (`k8s/`)

| Manifesto | Recurso | Descrição |
| :--- | :--- | :--- |
| `k8s/deployment.yaml` | Deployment `salesforce-release-notes` | Execução containerizada do pipeline com a imagem `ghcr.io/fatal1tybarucco/salesforce-webdev:latest`. |
| `k8s/cronjob.yaml` | CronJob `salesforce-release-notes` | Agendamento semanal do pipeline (`0 8 * * 1`, segunda 08:00 UTC) com a mesma imagem do Deployment. |
| `k8s/service.yaml` | Service `salesforce-release-notes` | Expõe o Deployment do pipeline dentro do cluster. |

## Prompts versionados (`prompts/`)

Os prompts de produção são versionados em YAML (ADR-008) e avaliados com
promptfoo (`.promptfoo.yaml`):

| Prompt | Uso |
| :--- | :--- |
| `prompts/classification/v1.yaml` | Classificação de features por categoria e impacto. |
| `prompts/enrichment/v1.yaml` | Enriquecimento de features com contexto e metadados. |
| `prompts/reporting/v1.yaml` | Geração de relatórios e sumários executivos. |

## Contrato de cobertura

Novos diretórios em `src/`, novos workflows, scripts, manifestos `k8s/`,
prompts e ADRs entram automaticamente como pendência de documentação
(estado `OMITO`) até que exista cobertura prose. Superfícies excluídas do
índice público por decisão de arquitetura (ADR-012): `docs/ai-generated/`,
`docs/internal/`, `docs/plans/` e artefatos locais de runtime.
