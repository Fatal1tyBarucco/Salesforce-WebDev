# 📋 Salesforce Release Notes — Automação Knowledge-as-Code

> Pipeline automatizado para extração, segmentação e versionamento das
> **Release Notes do Salesforce**, organizado por tópicos arquiteturais.

---

## 🚀 Como Funciona

```
GitHub Actions (Cron Semanal)
  └── scraper.py    → Busca HTML com retry exponencial
      └── parser.py → Segmenta por tópico (Apex, LWC, Flow, Security, Integrations)
          └── generator.py     → Gera /releases/{slug}/{topico}.md
              └── readme_updater.py → Atualiza este índice automaticamente
```

## ⚙️ Execução Manual

```bash
# Instalar dependências
pip install -r requirements.txt

# Processar todas as releases
python src/main.py

# Processar apenas uma release específica
python src/main.py --release summer_26

# Simular sem escrever arquivos
python src/main.py --dry-run
```

## 🗂️ Tópicos Monitorados

| Slug | Tópico |
| --- | --- |
| `apex` | Apex, Triggers, Batch, Queueable, SOQL |
| `lwc` | Lightning Web Components, Aura |
| `flow` | Flow Builder, Automações declarativas |
| `security` | Segurança, Permissões, Shield |
| `integrations` | REST/SOAP/Bulk API, Platform Events |

## ➕ Adicionando Novos Tópicos

Edite **apenas** `src/config.py` — adicione um novo `TopicConfig` à lista
`MONITORED_TOPICS`. Nenhuma outra alteração é necessária.

```python
TopicConfig(
    slug="data_cloud",
    display_name="Data Cloud",
    keywords=["data cloud", "cdp", "data stream", "calculated insight"],
),
```

---

## 📦 Índice de Releases

<!-- RELEASE_INDEX_START -->
<!-- RELEASE_INDEX_END -->

---

## 🛠️ Tecnologias

- **Python 3.12** — requests, BeautifulSoup4, lxml
- **GitHub Actions** — Cron, Workflow Dispatch, auto-commit
- **Ruff + Mypy** — Lint e type checking estrito

## 📁 Estrutura do Repositório

```
├── .github/workflows/release_notes_pipeline.yml
├── releases/
│   ├── summer_25/
│   ├── winter_26/
│   ├── spring_26/
│   └── summer_26/
├── src/
│   ├── config.py
│   ├── scraper.py
│   ├── parser.py
│   ├── generator.py
│   ├── readme_updater.py
│   └── main.py
└── requirements.txt
```
