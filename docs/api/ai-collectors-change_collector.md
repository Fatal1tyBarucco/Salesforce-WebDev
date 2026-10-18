# Ai Collectors — Change Collector

Módulo determinístico (`src/ai/collectors/change_collector.py`): coleta contexto bruto de mudanças desde a última ref processada (git log, diffs, conventional commits, PRs mesclados via `gh` CLI). Não usa IA — fornece contexto estruturado para o LLM.

## Uso

```python
from src.ai.collectors.change_collector import collect_changes
raw = collect_changes(since_ref="HEAD~10")
```

## Arquivos ignorados

`IGNORE_GLOBS` em `change_collector.py` exclui locks, gerados, `.md` produzidos pelo pipeline, e `.github/ai-docs-ignore`.
