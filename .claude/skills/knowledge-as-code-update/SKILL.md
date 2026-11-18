---
name: knowledge-as-code-update
description: Rodar pipeline completo de release notes e revisar diff gerado. Inclui: execução manual, validação de saída, comparação com release anterior, commit/push se aprovado.
---

# Skill: knowledge-as-code-update

## Quando Usar
- Nova release Salesforce detectada (schedule ou manual)
- Validar pipeline antes de merge de mudanças no scraper/parser/LLM
- Revisar diff gerado pelo pipeline (novidades, mudanças, remoções)

## Passos

### 1. Execução Local (dry-run)
```bash
# Dry-run: não escreve em releases/, só mostra o que faria
uv run python -m src.main --dry-run --release winter_27

# Execução real (escreve em releases/, README*, relatórios IA)
uv run python -m src.main --release winter_27
```

### 2. Validar Saída
```bash
# Verificar arquivos gerados
ls -la releases/winter_27/pt_BR/
ls -la releases/winter_27/en_US/
cat releases/winter_27/.meta.json
cat releases/winter_27/.summary_cache.json

# Diff com release anterior (se existir)
diff -u releases/spring_26/.meta.json releases/winter_27/.meta.json
```

### 3. Revisar Relatórios IA
```bash
# Relatórios gerados na raiz (ou tmp_path se dry-run)
# NOTA: IMPACT_REPORT.md e NOTIFICATION_DIGEST.md são artifacts de teste (não commitados — AGENTS.md:101)
cat CHANGELOG.md
cat QUALITY_REPORT.md
cat REGRESSION_REPORT.md
cat DIFF_REPORT.md
# cat IMPACT_REPORT.md          # artifact de teste
# cat NOTIFICATION_DIGEST.md    # artifact de teste
```

### 4. Validação de Gates
```bash
uv run ruff check . && uv run ruff format --check . && uv run mypy src/ --ignore-missing-imports && uv run pytest tests/ --cov=src --cov-fail-under=95
```

### 5. Commit + Push (se aprovado)
```bash
git add releases/ README.md README.en.md CHANGELOG.md QUALITY_REPORT.md REGRESSION_REPORT.md DIFF_REPORT.md IMPACT_REPORT.md NOTIFICATION_DIGEST.md
git commit -m "feat(release): winter_27 release notes pipeline output"
git push
# Release-please criará Release PR automaticamente
```

### 6. Docs Sync (obrigatório se docs alteradas)
```bash
python3 .github/scripts/docs_sync_engine.py reconcile
git add docs/
git commit -m "docs(sync): reconcile documentation"
git push
```

## Checklist de Validação
- [ ] `.meta.json` tem `total_features`, `categories`, `version`, `release_id`
- [ ] `.summary_cache.json` válido (executive_summary, category_summaries)
- [ ] `.md` pt_BR e en_US gerados para cada categoria
- [ ] README.md + README.en.md atualizados
- [ ] Relatórios IA coerentes (sem placeholders, sem alucinações óbvias)
- [ ] Gates passando
- [ ] Docs reconcile rodado

## Não Faça
- Não force push (use release-please flow)
- Não edite CHANGELOG.md manualmente
- Não pule docs reconcile
