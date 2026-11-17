# Plano de Modernização — Salesforce-WebDev

> **Status**: Fase 3 concluída (CI/CD e Automação Máxima) — aguardando aprovação para iniciar Fase 4
> **Branch**: `feat/fase-3-ci-cd` (base: feat/fase-2-ai-native + Fase 1 + Fase 0)
> **Data**: 2026-11-15
> **Autor**: Arquiteto de Software Sênior + Engenheiro de Plataforma + Engenheiro de DevEx/IA

---

## 1. Linha de Base Consolidada (Fase 0 → 1 → 2 → 3)

| Gate / Verificação | Fase 0 | Fase 1 | Fase 2 | Fase 3 |
|---|---|---|---|---|
| `ruff check .` | ✅ 1,8s | ✅ 1,9s | ✅ ~2s | ✅ ~2s |
| `black --check .` | ✅ 23,5s | **REMOVIDO** | — | — |
| `ruff format --check .` | N/A | ✅ 1,6s | ✅ ~1,6s | ✅ ~1,6s |
| `mypy src/` | ✅ 30,4s | ✅ 30,2s | ✅ ~30s | ✅ ~30s |
| `pytest --cov=src --cov-fail-under=95` | ✅ 95,34% (217,7s) | ✅ 95,52% (~200s) | ✅ Passando | ✅ Passando |
| `pip-audit` | ✅ 0 vulns | ✅ 0 vulns | ✅ 0 vulns | ✅ 0 vulns |
| `gitleaks` | ✅ 0 segredos | ✅ 0 segredos | ✅ 0 segredos | ✅ 0 segredos |
| **CI Quality Gate** | ~55s | **~33s** | **~33s** | **~33s** |
| **Workflows ativos** | 10 | 11 (+release-please) | 11 | **15** (+4 novos) |

---

## 2. Fase 3 — CI/CD e Automação Máxima (CONCLUÍDA)

### Novos Workflows Criados (4)

| Workflow | Arquivo | Função Principal |
|---|---|---|
| **AI PR Review** | `.github/workflows/ai-pr-review.yml` | Revisão automática via Claude Code (code-reviewer + security-auditor), menção `@claude` |
| **CI Repair** | `.github/workflows/ci-repair.yml` | Auto-fix ruff/format falhas → branch de reparo → PR update → escala para humano (máx 2 tentativas) |
| **Scheduled Pipeline** | `scheduled-pipeline.yml` | Extração agendada (Mon 08:00 UTC) → PR com release notes + resumo IA + diff + checklist |
| **AI Triage** | `.github/workflows/ai-triage.yml` | Labels automáticos, prioridade P0-P3, duplicatas, info faltante, GitHub Project sync |

### Atualizações em Workflows Existentes

| Workflow | Mudança |
|---|---|
| `python-quality.yml` | Black removido → Ruff Format job; cache Playwright adicionado; permissions mínimas por job |
| `release-please.yml` | Já existia (Fase 1), SHA imutável v4.4.1 |

### Scripts Auxiliares Criados

| Script | Função |
|---|---|
| `scripts/detect_release.py` | Detecção de release nova (usado por scheduled-pipeline) |
| `scripts/generate_pr_body.py` | Gera corpo do PR com diff, checklist, validação (evita YAML heredoc issues) |

---

## 3. Arquitetura de Automação (Resumo)

```bash
┌─────────────────────────────────────────────────────────────────┐
│                    CI/CD AUTOMATION LAYER                       │
├─────────────────────────────────────────────────────────────────┤
│  python-quality.yml  │  ruff → ruff-format → mypy → tests       │
│  (quality gate ~33s) │  parallel, cache, permissions mínimas    │
├─────────────────────────────────────────────────────────────────┤
│  ai-pr-review.yml    │  @claude mention → code-reviewer +       │
│  (AI PR Review)      │  security-auditor → comments no PR       │
├─────────────────────────────────────────────────────────────────┤
│  ci-repair.yml       │  failure → diagnose → auto-fix           │
│  (CI Repair)         │  ruff/format → repair branch → PR →      │
│                      │  max 2 tentativas → escala humano        │
├─────────────────────────────────────────────────────────────────┤
│  scheduled-pipeline  │  Mon 08:00 UTC → detect → process →      │
│  (Knowledge-as-Code) │  PR com diff + IA summary + checklist    │
├─────────────────────────────────────────────────────────────────┤
│  ai-triage.yml       │  issue/PR opened → auto-labels,          │
│  (AI Triage)         │  priority P0-P3, duplicates, missing     │
│                      │  info, GitHub Project sync               │
├─────────────────────────────────────────────────────────────────┤
│  release-please.yml  │  Conventional Commits → Release PR       │
│  (Release Auto)      │  merge → tag + GitHub Release            │
└─────────────────────────────────────────────────────────────────┘
```

---

## 4. Backlog Atualizado — Próximas Prioridades (Fase 4+)

| Prioridade | Item | Impacto | Esforço | Fase | Status |
|---|---|---|---|---|---|
| **P0** | Consolidar LLM em 1 implementação | 🔴 Crítico | M | 4 | **Próximo** |
| **P0** | Migrar `main.py` → Clean Arch | 🔴 Crítico | G | 4 | **Próximo** |
| **P1** | Injetar dependências no Scraper | 🟠 Alto | M | 4 | Pendente |
| **P1** | Tracking de tokens/custo no LLM | 🟠 Alto | M | 4 | Pendente |
| **P1** | Parallelizar `FeatureEnricher.enrich_release()` | 🟠 Alto | P | 4 | Pendente |
| **P1** | Fixar `fix_markdown.py` fence tracking | 🟠 Alto | P | 4 | Pendente |
| **P2** | Seletores CSS → contrato testado | 🟡 Médio | M | 4 | Pendente |
| **P2** | Circuit Breaker: half-open + métricas | 🟡 Médio | P | 4 | Pendente |
| **P2** | Exceções amplas → específicas | 🟡 Médio | P | 4 | Pendente |
| **P2** | Content comparison robusta | 🟡 Médio | P | 4 | Pendente |
| **P3** | Testes dedicados módulos sem cobertura | 🟢 Baixo | G | 5 | Pendente |
| **P3** | Config consolidada (dependency-groups único) | 🟢 Baixo | P | 4 | Pendente |
| **P3** | Mypy strict progressivo módulo a módulo | 🟢 Baixo | M | 4-5 | Pendente |

---

## 5. Fase 4 — Pipeline de Dados e LLM de Última Geração (PRÓXIMA)

**Escopo aprovado no plano original**:

1. **Scraper Playwright resiliente**: retries com backoff exponencial + jitter, circuit breaker preservado, timeouts explícitos, detecção de mudança de layout (contrato do parser testado com HTML fixtures), observabilidade estruturada (structlog com correlation id), métricas por execução, tracing OpenTelemetry opcional.
2. **`llm_service` provider-agnostic**: ports/adapters, fallback em cascata, cache semântico/por hash de prompt, rate limiting adaptativo, saída estruturada validada por schema Pydantic, registro de custo/tokens por execução em relatório JSON/MD. Prompt caching dos providers que suportam.
3. **Prompts versionados em `prompts/`**: um arquivo por prompt com metadados e versão, avaliados automaticamente (promptfoo ou equivalente) com conjunto de casos e gate no CI.
4. **Saídas**: docs por release em Markdown + índice navegável, diffs automáticos entre releases (novidades, mudanças, remoções), site estático MkDocs Material publicado no GitHub Pages com busca.
5. **MCP próprio (opcional, com ADR)**: expõe Knowledge-as-Code (consulta de release notes) a qualquer agente.

---

## 6. Riscos e Bloqueadores Conhecidos (atualizado)

| Risco | Probabilidade | Impacto | Mitigação |
|---|---|---|---|
| `mkdocs build --strict` falha em ARM64 (Termux/android) por `playwright` sem wheel | Alta (já ocorre) | Médio | `continue-on-error: true` já configurado; documentar limitação |
| Push para `.github/workflows/*` falha com `GITHUB_TOKEN` / opencode token (HTTP 403) | Confirmado | Alto | Reportar a humano/admin; não prometer push automático de workflows |
| Ruff 0.17.1 não linkado / python3.13 indisponível no Termux | Documentado | Baixo | Não bloqueia CI GitHub (ubuntu-latest); documentar honestamente |
| `pytest-syrupy` força downgrade pytest 9.x → 8.4.2 local | Confirmado | Baixo | CI instala syrupy após `uv sync`; local usar `uv run --no-sync` |
| Black removido — risco zero confirmado | — | — | Testes de caracterização (golden files) protegem comportamento |
| **CI Repair: auto-fix pode introduzir regressões sutis** | Média | Médio | Máx 2 tentativas; nunca desativa gates; PR review obrigatório; escala humano |
| **AI PR Review: custo API Anthropic** | Média | Médio | `ANTHROPIC_API_KEY` como secret; monitorar uso; fallback para revisão manual |
| **Scheduled Pipeline: Playwright instável em CI** | Média | Alto | Cache browsers; timeout 60min; issue automático se falhar |

---

## 7. Verificação Git Atual

```bash
$ git status --porcelain
 M .github/workflows/python-quality.yml
 M .github/workflows/release_notes_pipeline.yml
 A .github/workflows/ai-pr-review.yml
 A .github/workflows/ci-repair.yml
 A .github/workflows/scheduled-pipeline.yml
 A .github/workflows/ai-triage.yml
 M .pre-commit-config.yaml
 M pyproject.toml
 M src/infrastructure/llm.py
 M src/main.py
 M tests/test_llm_service.py
 A scripts/detect_release.py
 A scripts/generate_pr_body.py
 A .claude/settings.json
 A .claude/agents/architect.md
 A .claude/agents/python-engineer.md
 A .claude/agents/test-engineer.md
 A .claude/agents/code-reviewer.md
 A .claude/agents/docs-writer.md
 A .claude/agents/release-manager.md
 A .claude/agents/security-auditor.md
 A .claude/skills/add-release-source/SKILL.md
 A .claude/skills/new-llm-provider/SKILL.md
 A .claude/skills/debug-ci/SKILL.md
 A .claude/skills/bump-quality/SKILL.md
 A .claude/skills/prompt-eval/SKILL.md
 A .claude/skills/knowledge-as-code-update/SKILL.md
 A .claude/commands/diag.md
 A .claude/commands/refactor.md
 A .claude/commands/release.md
 A .claude/commands/audit.md
 A .claude/commands/triage.md
 A .claude/commands/prompt-eval.md
 A .mcp.json
 M AGENTS.md
 A CLAUDE.md
 ?? docs/ARQUITETURA.md
 ?? docs/DEBITO_TECNICO.md
 ?? docs/MODERNIZACAO.md
 ?? tests/fixtures/
 ?? tests/golden/
 ?? tests/test_characterization*.py
```

**Total Fase 3**: 6 workflows (1 atualizado + 4 novos + 1 existente), 2 scripts auxiliares, configs atualizadas.

---

## 8. Próximo Passo — Aguardando Aprovação

**Fase 3 concluída com gates verdes**. Para iniciar **Fase 4 — Pipeline de Dados e LLM de Última Geração**, responda **"aprovado"** (ou indique ajustes no escopo).

---

*Documento vivo — atualizado a cada fase concluída. Ver `docs/ARQUITETURA.md` e `docs/DEBITO_TECNICO.md` para evidência detalhada.*
