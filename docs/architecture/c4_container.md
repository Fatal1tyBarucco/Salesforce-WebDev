# C4 Container Diagram

## Containers

| Container | Responsibility |
|---|---|
| GitHub Actions | Pipeline orchestration |
| Python Scraper Engine | Release retrieval |
| Semantic Parser | Section extraction |
| Topic Classifier | Technical categorization |
| Markdown Generator | Artifact generation |
| MkDocs | Documentation publishing |

## Data Flow

```text
GitHub Actions
    ↓
Scraper Engine
    ↓
Semantic Parser
    ↓
Topic Classifier
    ↓
Markdown Generator
    ↓
MkDocs Portal
```
