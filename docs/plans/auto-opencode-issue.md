# Feature: Comentário automático `/oc fix` no issue do Python Quality

Status: Proposto (Backlog) | Referência: `.github/workflows/python-quality.yml:224-294`, `.github/workflows/opencode.yml:3-34`, `.github/scripts/build_failure_issue.py`

## Objetivo

Quando o workflow `Python Quality` falhar (`python-quality.yml`) e criar um issue automaticamente (`create-issue`), incluir um comentário `/oc fix` nesse issue para acionar a action `opencode` (`opencode.yml`) e tentar corrigir automaticamente erros simples (`ruff`, `black`).

## Arquivos afetados

- `.github/workflows/python-quality.yml` — adicionar captura do número do issue e step de comentário (`create-issue` job, linhas 224-294).
- `.github/workflows/opencode.yml` — aumentar permissões (`contents`, `pull-requests`, `issues` de `read` para `write`) para que `opencode` possa abrir PR com correções (linhas 14-20, 29-30).
- `.github/scripts/build_failure_issue.py` — opcional: incluir referência ao `opencode` no corpo do issue (linha 245: `> 🤖 Issue gerada automaticamente...`).
- `docs/plans/auto-opencode-issue.md` — este arquivo.

## Passos de implementação

1. **Capturar o número do issue** (`python-quality.yml`, step `Create GitHub Issue`, linha 275-294)
   - Alterar `gh issue create --title ... --body-file ...` para salvar o número:
     `NUMBER=$(gh issue create --title "$TITLE" --body-file "$BODY_FILE" --json number --jq '.number')`

   - Adicionar `echo "issue_number=$NUMBER" >> "$GITHUB_OUTPUT"`.

2. **Restringir a quais falhas aplicar** (`python-quality.yml`, step `Create Issue on Failure`, linha 228)
   - Só comentar se `ruff` ou `black` falhar (`needs.ruff.result == 'failure' || needs.black.result == 'failure'`).
   - Não comentar se `mypy` ou `tests` falhar — risco de PR incorreto (`build_failure_issue.py:103-121`).

3. **Comentar no issue** (novo step `Comment /oc fix`, após `Create GitHub Issue`)
   - Executar apenas se `NUMBER` existir e se `ruff`/`black` falhou:
     `gh issue comment "$NUMBER" --body "/oc fix only ruff and black formatting. Do not touch mypy or tests."`

   - Usar `gh issue comment` com `GH_TOKEN` (`python-quality.yml` já define `permissions: issues: write` no job `create-issue`, linha 230-231).

4. **Ajustar permissões do `opencode.yml`** (linhas 14-20, 29-30)
   - Atualizar `permissions` de:
     `contents: read, pull-requests: read, issues: read`
     para:
     `id-token: write, contents: write, pull-requests: write, issues: write`

   - Confirmar que `OPENCODE_API_KEY` está configurada nos secrets do repositório (`opencode.yml:31`; `docs/guides/getting-started.md:81`).

5. **Ajustar o comando no comentário**
   - Evitar `/oc fix` genérico; especificar:
     `/oc fix only ruff (lint) and black (format) errors. Skip mypy and tests.`

   - Isso limita o escopo e reduz risco de PR incorreto.

6. **Documentar no corpo do issue** (opcional, `build_failure_issue.py`)
   - Adicionar no `build_body` uma seção indicando que o `/oc fix` foi solicitado automaticamente (ex: `> 💬 Solicitação automática: /oc fix enviada no comentário do issue.`).

## Critério de aceitação

- Quando `python-quality.yml` cria issue (`create-issue`), dentro de 30s o comentário `/oc fix` aparece no issue (verificável via `gh issue view <N> --comments`).
- A action `opencode` reage (`opencode.yml`: `on: issue_comment`) e cria uma branch/PR se `ruff` ou `black` falhou.
- Se `tests` ou `mypy` falhar, **nenhum** comentário `/oc fix` é adicionado ao issue.
- Se `OPENCODE_API_KEY` estiver ausente, o `opencode` falha silenciosamente (sem quebrar o `create-issue`).

## Riscos e mitigações

| Risco | Impacto | Mitigação |
|---|---|---|
| `opencode` cria PR incorreto para `ruff`/`black` complexo | PR com código quebrado | Restringir comando (`only ruff/black`); revisar PR manualmente antes de merge |
| `opencode` falha por falta de permissões (`opencode.yml`) | Nenhuma ação; comentário existe mas PR não é criado | Ajustar permissões (`contents: write`, `pull-requests: write`) antes de ativar |
| `opencode` falha por falta de `OPENCODE_API_KEY` | Nenhuma ação | Confirmar secret; o workflow `python-quality.yml` continua funcionando independentemente |
| Loop: PR do `opencode` não resolve tudo → novo commit → novo issue | Múltiplos issues para o mesmo erro | `python-quality.yml` evita duplicata por SHA (`linha 283-286`); se PR não corrigir tudo, o próximo push (novo SHA) criará novo issue — aceitável |
| Comentar no issue errado (duplicata) | `create-issue` pula (`line 284-286`) | Nenhum — a duplicata não cria novo issue, portanto não há comentário |

## Dependências externas

- Secret `OPENCODE_API_KEY` configurada no repositório (`docs/guides/getting-started.md:81`).
- Modelo `opencode/mimo-v2.5-free` disponível (configurado em `opencode.yml:34`).

## Referências

- `.github/workflows/python-quality.yml` — job `create-issue` (linha 224-294), permissões (linha 229-231), guarda de duplicata (linha 283-286).
- `.github/workflows/opencode.yml` — triggers (`linha 4-7`), permissões (`linha 14-20`), modelo (`linha 34`), env (`linha 31`).
- `.github/scripts/build_failure_issue.py` — classificação de falhas (`PATTERNS`, linha 33-122), corpo do issue (`build_body`, linha 207-247).
- `docs/guides/getting-started.md` — referência `OPENCODE_API_KEY` (linha 81).
