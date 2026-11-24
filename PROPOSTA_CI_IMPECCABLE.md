# Proposta: Job CI para Impeccable Design Quality

## Resumo

Esta proposta adiciona um job dedicado no pipeline de CI/CD (`python-quality.yml`) para executar o **Impeccable detect** em todos os arquivos de superfície web (HTML, CSS, Markdown) a cada push/PR, garantindo conformidade contínua com o design system definido em `DESIGN.md`.

---

## Motivação

- **Detecção precoce**: Impede que regressões visuais (cores hardcoded, tokens não utilizados, contraste insuficiente) cheguem à branch principal
- **Source of truth único**: `DESIGN.md` + `src/design-system/tokens.css` são a fonte de verdade; o Impeccable valida se o código respeita esses tokens
- **Automação zero-config**: O detector roda sem necessidade de browser/CDP para arquivos estáticos (Markdown, CSS, HTML templates)
- **Alinhamento com hooks locais**: O hook de pre-commit (adicionado em `.pre-commit-config.yaml`) roda o mesmo check; o CI garante que ninguém faça bypass

---

## Arquivos-alvo

| Padrão | Descrição |
|--------|-----------|
| `docs/**/*.md` | Documentação MkDocs (inclui diagramas Mermaid) |
| `README.md`, `README.en.md` | READMEs raiz (badges, visão geral) |
| `src/**/*.html` | Templates Jinja2 (dashboard, etc.) |
| `src/design-system/**/*.css` | Design system tokens + componentes |
| `docs/assets/stylesheets/**/*.css` | CSS customizado do MkDocs (ex: `mermaid.css`) |

---

## Job YAML Proposto

```yaml
# .github/workflows/python-quality.yml
# Adicionar ao final do arquivo, após o job 'quality-gate'

impeccable-design-quality:
  name: 🎨 Impeccable Design Quality
  runs-on: ubuntu-latest
  timeout-minutes: 10
  permissions:
    contents: read
  steps:
    - name: Checkout repository
      uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4.2.2

    - name: Setup Node.js
      uses: actions/setup-node@49933ea5288caeca8642d1e84afbd3f7d6820020 # v4.4.0
      with:
        node-version: '22'
        cache: 'npm'

    - name: Install Impeccable
      run: npm ci --prefer-offline --no-audit 2>/dev/null || npm install --prefer-offline --no-audit impeccable@latest

    - name: Run Impeccable detect on Markdown
      run: |
        npx impeccable detect \
          --target docs/index.md \
          --target README.md \
          --target README.en.md
      continue-on-error: false

    - name: Run Impeccable detect on HTML templates
      run: |
        npx impeccable detect \
          --target src/dashboard_template.html
      continue-on-error: false

    - name: Run Impeccable detect on CSS
      run: |
        npx impeccable detect \
          --target src/design-system/tokens.css \
          --target src/design-system/dashboard-combined.css \
          --target docs/assets/stylesheets/mermaid.css
      continue-on-error: false

    - name: Upload Impeccable report (on failure)
      if: failure()
      uses: actions/upload-artifact@4cec3d8aa04e39d1a6839620c93a0f0cf401a9e1 # v4.6.2
      with:
        name: impeccable-report
        path: |
          *.impeccable.json
          .impeccable/
        retention-days: 7
```

---

## Integração com Workflow Existente

O job deve rodar **em paralelo** com os jobs atuais (`lint`, `typecheck`, `test`) para não aumentar o tempo total do pipeline. Exemplo de integração no `python-quality.yml`:

```yaml
jobs:
  lint:
    # ... existing lint job
  
  typecheck:
    # ... existing mypy job
  
  test:
    # ... existing pytest job
  
  impeccable-design-quality:  # NOVO - roda em paralelo
    # ... (yaml acima)
  
  quality-gate:
    needs: [lint, typecheck, test, impeccable-design-quality]
    # ... existing gate
```

---

## Tratamento de Falhas

| Cenário | Ação |
|---------|------|
| **Violação de token** (cor hardcoded, spacing errado) | Falha o job; desenvolvedor corrige usando tokens de `DESIGN.md` |
| **Contraste insuficiente** (WCAG AA < 4.5:1) | Falha; ajustar cor/opacidade via tokens semânticos (`--color-on-surface-variant`, `--input-placeholder-opacity`) |
| **Mermaid sem classDef** | Falha; converter `style` inline para `classDef` + CSS em `mermaid.css` |
| **Falso positivo** | Documentar em `DESIGN.md` como exceção justificada (raro) |

---

## Estimativa de Impacto

| Métrica | Valor |
|---------|-------|
| Tempo adicional no CI | ~30-60s (roda em paralelo) |
| Arquivos verificados | ~15-20 superfícies web |
| Falsos positivos esperados | 0 (detector é determinístico para tokens) |
| Manutenção | Atualizar `files:` patterns quando novas superfícies forem adicionadas |

---

## Checklist de Implementação

- [ ] Adicionar job `impeccable-design-quality` ao `.github/workflows/python-quality.yml`
- [ ] Adicionar `impeccable-design-quality` ao `needs:` do job `quality-gate`
- [ ] Testar em branch de feature antes de merge para `main`
- [ ] Validar que hooks locais (`.pre-commit-config.yaml`) e CI usam a mesma versão do Impeccable
- [ ] Documentar no `CONTRIBUTING.md` / `docs/guides/local-development.md` como rodar localmente

---

## Referências

- [Impeccable CLI](https://github.com/impeccable/impeccable) — detector de design quality
- `DESIGN.md` — Design tokens (cores, tipografia, espaçamento, sombras, raio)
- `src/design-system/tokens.css` — CSS custom properties (source of truth para runtime)
- `.pre-commit-config.yaml` — Hook local `impeccable-detect` (stages: [pre-commit])
- ADR-012 — Absolute Documentation Sync (contrato verificável de docs)

---

**Próximo passo**: Aprovar esta proposta → implementar no `python-quality.yml` → validar em PR de teste.