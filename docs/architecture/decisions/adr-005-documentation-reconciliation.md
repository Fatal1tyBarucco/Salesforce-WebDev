# ADR-005 — Continuous Documentation Reconciliation Pipeline

## Status

**Accepted** — Agosto 2026

## Context

O workflow `documentation-build.yml` é essencialmente um build/deploy de MkDocs: dispara em mudanças de paths (`docs/**`, `mkdocs.yml`, `src/**`, `releases/**` etc.), executa `mkdocs build --strict` e publica no GitHub Pages.

Isso deixa uma lacuna estrutural:

- Uma alteração em `src/**` pode não produzir atualização documental adequada.
- A estrutura documental é extensa (Architecture, Auto-Healing, Refatoração, Maintenance, Observability, Runbooks, Roadmap, API Reference), tornando drift silencioso cada vez mais provável.
- Exemplo real detectado manualmente: `pyproject.toml` exige Python `>=3.13,<3.14`, mas o README exibia badge `Python 3.12+`.
- Código removido (ex.: providers OpenAI removidos do `LLMService`) pode deixar documentação órfã descrevendo comportamento inexistente.

### Problema

- Trigger baseado em paths não garante reconciliação semântica.
- Não existe detecção de documentação órfã, contraditória ou desatualizada.
- Não existe mecanismo que compare sistematicamente o estado do repositório com a documentação publicada.

## Decision

Transformar o sistema em um **Continuous Documentation Reconciliation Pipeline**, separando responsabilidades (SoC):

| Workflow | Responsabilidade |
|---|---|
| `documentation-sync.yml` (novo) | inventário → diff → drift → análise LLM → reconciliação → validação → commit |
| `documentation-build.yml` (existente) | exclusivamente `docs/` → MkDocs → GitHub Pages |

### Princípios

1. **Git Repository = Source of Truth.** GitHub Pages é apenas a projeção publicada. Precedência: código > configuração > workflows > dependências > testes > estrutura > histórico git > documentação existente. Nunca modificar código para adequá-lo à documentação.
2. **Detecção determinística primeiro, IA depois.** Código determinístico detecta arquivos criados/removidos/alterados, links quebrados, nav inválida e mapeamento API↔módulo. O LLM atua apenas na interpretação semântica e reescrita — reduzindo hallucination.
3. **Reutilizar a infraestrutura LLM existente.** O agente consome o `LLMService` (`src/llm_service.py`) com a cadeia Gemini → OpenCode → OpenRouter já configurada. Nenhum provider/credencial novo é introduzido.
4. **Manifesto interno** (`docs/.documentation-manifest.json`): snapshot `{path: blob_sha}` + mapa `documentation_map` (fonte → docs). Permite detectar alterado/criado/removido/órfão entre execuções. Ignorado pelo MkDocs (dotfile).
5. **Modos:** `incremental` (push), `full` (schedule a cada 6h — `17 */6 * * *`), `audit` (somente análise).
6. **Segurança:** o agente só pode escrever em `docs/**`, `README.md`, `README.en.md` e `mkdocs.yml`. Nunca modifica `src/**`, `tests/**`, secrets ou workflows. Respostas fora da allowlist são bloqueadas.
7. **Anti-loop:** commits de automação usam prefixo `docs(sync):`; o workflow encerra cedo quando o HEAD já é um commit do próprio bot com esse prefixo.
8. **Falha segura:** sem provider disponível (ou resposta mock), o agente aborta sem escrever nada e registra os findings no step summary para revisão manual.

### Fluxo

```text
Push (incremental) ─┐
Schedule 6h (full) ─┼─→ Inventory → Manifest Diff → Drift Report
Manual (audit)    ──┘         │
                              ▼
                    LLM Reconciliation (LLMService)
                              ▼
                   mkdocs build --strict (bloqueante)
                              ▼
              commit "docs(sync): ..." → push main
                              ▼
                documentation-build.yml → GitHub Pages
```

## Consequences

- Documentação óbsoleta passa a ser detectada automaticamente a cada push e auditada integralmente a cada 6 horas.
- Custo de IA controlado: análise só ocorre sobre findings acionáveis, com cap por execução (`DOC_SYNC_MAX_FINDINGS`).
- Risco residual: navegação para documentos novos criados pelo agente pode exigir ajuste manual (limitação registrada no sumário da execução).

## Related

- ADR-002 — GitHub Actions (padrões de workflow)
- ADR-004 — Auto-Healing CI/CD Agent (reuso da cadeia de providers LLM)
