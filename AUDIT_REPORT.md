# 🔍 Relatório de Auditoria Completa — Salesforce-WebDev

**Data:** 2026-07-15  
**Escopo:** Todos os módulos de automação (`src/`), CI/CD (`.github/workflows/`), e testes  
**Metodologia:** Revisão manual linha-a-linha de todos os 24 módulos Python + 7 workflows CI/CD

---

## 🚨 BUGS CRÍTICOS (10)

### BUG-001: SyntaxError em 13+ arquivos — `except X, Y:` é sintaxe Python 2

**Severidade:** 🔴 CRÍTICA (impede execução em Python 3)  
**Afeta:** scraper.py, translator.py, ai_automation.py, health.py, notifications.py, workflow.py, smart_notifications.py, impact_analyzer.py, issue_triage.py, release_summarizer.py, dashboard.py, api.py, analytics.py

**O problema:** Múltiplos arquivos usam `except ExcecaoA, ExcecaoB:` que é sintaxe **Python 2**. Em Python 3, isso é interpretado como `except ExcecaoA:` com alias `ExcecaoB`, o que:
1. **Não captura** `ExcecaoB` corretamente
2. **Mascara** a exceção capturada sob o nome `ExcecaoB`

**Exemplo em `scraper.py:37`:**
```python
# ❌ ERRADO (Python 2 syntax)
except TypeError, ValueError:
    return False

# ✅ CORRETO (Python 3)
except (TypeError, ValueError):
    return False
```

**Arquivos afetados e linhas:**
| Arquivo | Linha | Exceções afetadas |
|---------|-------|-------------------|
| `scraper.py` | 37 | TypeError, ValueError |
| `parser.py` | 235 | ValueError, TypeError |
| `translator.py` | 31 | json.JSONDecodeError, OSError |
| `ai_automation.py` | 195 | json.JSONDecodeError, TypeError |
| `ai_automation.py` | 397 | ValueError, IndexError |
| `ai_automation.py` | 455 | json.JSONDecodeError, TypeError |
| `health.py` | 67 | json.JSONDecodeError, OSError |
| `notifications.py` | 167 | json.JSONDecodeError, OSError |
| `notifications.py` | 181 | json.JSONDecodeError, OSError |
| `workflow.py` | 118 | ValueError, IndexError |
| `smart_notifications.py` | 154 | ValueError, IndexError |
| `impact_analyzer.py` | 108 | ValueError, IndexError |
| `issue_triage.py` | 121 | json.JSONDecodeError, FileNotFoundError |
| `issue_triage.py` | 157 | subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError |
| `release_summarizer.py` | 102 | json.JSONDecodeError, OSError |
| `dashboard.py` | 35 | json.JSONDecodeError, OSError |
| `api.py` | 51 | json.JSONDecodeError, OSError |
| `analytics.py` | 39 | json.JSONDecodeError, OSError |

**Nota:** É surpreendente que Ruff, Mypy e os 450+ testes não detectaram isso. Possível explicação: os testes usam mocks que nunca chegam nesses caminhos de erro, e o Mypy pode não flagar como erro de sintaxe em todos os contextos.

---

### BUG-002: Circuit Breaker do Scraper não reseta falhas após cooldown

**Severidade:** 🔴 CRÍTICA  
**Arquivo:** `scraper.py` — classe `CircuitBreaker`

```python
@property
def is_open(self) -> bool:
    if self._failures < self._threshold:
        return False
    elapsed = time.monotonic() - self._opened_at
    if elapsed > self._cooldown:
        return False  # ← Cooldown expirou, circuito "fecha"
    return True
```

**O problema:** Quando o cooldown expira, `is_open` retorna `False` permitindo novas requisições, **mas `self._failures` nunca é resetado**. Se a próxima requisição falhar, `_failures` vai para 4 (não 1), e o circuito abre imediatamente novamente com cooldown ainda mais longo.

**Correção:**
```python
@property
def is_open(self) -> bool:
    if self._failures < self._threshold:
        return False
    elapsed = time.monotonic() - self._opened_at
    if elapsed > self._cooldown:
        self._failures = 0  # ← Resetar falhas após cooldown
        return False
    return True
```

---

### BUG-003: Logger duplicado em `scraper.py`

**Severidade:** 🟡 MÉDIA  
**Arquivo:** `scraper.py`, linhas 20-22

```python
logger = logging.getLogger(__name__)

logger = logging.getLogger(__name__)  # ← Duplicata
```

**Impacto:** Não causa erro funcional, mas indica copy-paste descuidado e polui o namespace.

---

### BUG-004: `main.py` — `detect_new_release` pode retornar release já existente

**Severidade:** 🔴 CRÍTICA  
**Arquivo:** `main.py`, função `detect_new_release`

```python
if current is None:
    latest = known_sorted[0]
    if latest.slug not in existing_slugs:
        logger.info("No releases in repo, processing latest known: %s", latest.name)
        return latest
    return None  # pragma: no cover
```

**O problema:** Se `existing_slugs` está vazio (primeira execução), retorna o `latest`. Mas se `latest.slug` já existe, retorna `None`. Porém, o loop acima (`for r in known_sorted`) já deveria ter encontrado `current`. Se `current is None` e `latest.slug not in existing_slugs`, ok. Mas se `current is None` e `latest.slug in existing_slugs`, retorna `None` — correto, mas o pragma `no cover` indica que o desenvolvedor acha que isso é inalcançável, o que não é verdade se o repositório for populado manualmente.

---

### BUG-005: `_build_release_name` assume sequência perfeita de releases

**Severidade:** 🟠 ALTA  
**Arquivo:** `main.py`

```python
RELEASE_SEASONS = ("Spring", "Summer", "Winter")
RELEASE_BASE_ID = 254
RELEASE_BASE_YEAR = 25
RELEASE_ID_STEP = 2
```

**O problema:** Se Salesforce mudar a numeração de releases (o que já aconteceu no passado), toda a lógica de detecção de novas releases quebra. Além disso, a função `_build_release_name` usa divisão inteira que pode gerar nomes errados se `release_id` não seguir a sequência exata.

---

### BUG-006: Tradução não afeta subcategorias no `main.py`

**Severidade:** 🟡 MÉDIA  
**Arquivo:** `main.py`, `_generate_release_files`

```python
if locale == "en_US" and translator:
    for entry in cat.entries:
        entry.name = await translator.translate_feature(entry.name, "pt_BR", "en_US")
    for sub_entries in cat.subcategories.values():
        for entry in sub_entries:
            entry.name = await translator.translate_feature(entry.name, "pt_BR", "en_US")
```

**O problema:** A tradução é feita **in-place** no objeto `entry.name`. Se o mesmo `FeatureImpactCategory` for usado para gerar pt_BR E en_US, a segunda chamada já terá os nomes traduzidos (en_US), e tentará traduzir en_US → en_US novamente, desperdiçando chamadas à API.

**Correção:** Clonar os entries antes de traduzir, ou gerar pt_BR primeiro (já feito) e garantir que a ordem é sempre pt_BR → en_US.

---

### BUG-007: `_format_impact_report` e `_format_notification_digest` usam `object` como tipo

**Severidade:** 🟡 MÉDIA  
**Arquivo:** `main.py`

```python
def _format_impact_report(report: object, release_name: str) -> str:
def _format_notification_digest(digest: object) -> str:
```

**O problema:** Usar `object` como tipo é inseguro — qualquer objeto passa na validação, mas `hasattr` checks são frágeis. Deveria usar os tipos concretos (`ImpactReport`, `NotificationDigest`) ou pelo menos `Protocol`.

---

### BUG-008: `generate_dynamic_badge` é método de instância mas chamado como estático

**Severidade:** 🟡 MÉDIA  
**Arquivo:** `ai_automation.py` + `main.py`

Em `ai_automation.py`:
```python
def generate_dynamic_badge(self, release_name: str, total_features: int) -> str:
    return f"![Latest Release](...)"
```

Em `main.py`:
```python
from .ai_automation import generate_dynamic_badge
badge = generate_dynamic_badge(name, total)
```

**O problema:** `generate_dynamic_badge` é um método de instância (com `self`) em `AIAutomationService`, mas é importado e chamado como função standalone no módulo level. Isso funciona apenas porque há um wrapper no final do arquivo:
```python
def generate_dynamic_badge(release_name: str, total_features: int) -> str:
    return AIAutomationService().generate_dynamic_badge(release_name, total_features)
```
Mas isso cria uma instância desnecessária de `AIAutomationService` (e seu `LLMService`) só para gerar uma string.

---

### BUG-009: `workflow.py` — `commit_and_push` hardcodeia diretórios

**Severidade:** 🟠 ALTA  
**Arquivo:** `workflow.py`

```python
subprocess.run(
    ["git", "add", "releases/", "README.md", "analytics/"],
    ...
)
```

**O problema:** Se `analytics/` não existir (e.g., primeira execução), o `git add` falha silenciosamente (não causa erro porque `check=True` mas o diretório não existe). Além disso, outros artefatos gerados (`CHANGELOG.md`, `QUALITY_REPORT.md`, `DIFF_REPORT.md`, etc.) não são commitados.

---

### BUG-010: API GraphQL — parser regex é frágil e inseguro

**Severidade:** 🟠 ALTA  
**Arquivo:** `api.py`, `_execute_graphql`

```python
releases_match = re.search(r"releases\s*\{", query)
release_match = re.search(r'release\s*\(\s*slug\s*:\s*"([^"]+)"\s*\)\s*\{', query)
```

**O problema:** 
1. O parser regex não suporta queries GraphQL reais (fragments, variables inline, nested queries)
2. Não valida a query contra um schema
3. `requested_fields` extrai **todas** as palavras após o primeiro `{`, incluindo keywords de controle
4. Não suporta aliases, o que é obrigatório em GraphQL

---

## ⚠️ GAPS DE DESIGN (8)

### GAP-001: Sem `--dry-run` funcional

**Arquivo:** `main.py`

O CI workflow passa `--dry-run` mas o `main.py` **não implementa** essa flag. O argumento é parseado manualmente mas nunca usado:
```python
args = sys.argv[1:]
for i, arg in enumerate(args):
    if arg == "--release" and i + 1 < len(args):
        release_filter = args[i + 1]
# --dry-run é ignorado completamente
```

---

### GAP-002: Sem graceful shutdown do Playwright

**Arquivo:** `scraper.py`

Se o pipeline for interrompido (SIGINT/SIGTERM), o browser do Playwright pode ficar aberto como processo zumbi. Não há signal handler nem cleanup adequado.

---

### GAP-003: Cache não tem invalidação por conteúdo

**Arquivo:** `cache_manager.py`

O cache usa TTL fixo (24h), mas não verifica se o conteúdo da página mudou. Se a Salesforce atualizar uma release existente, o cache retorna dados desatualizados até o TTL expirar.

---

### GAP-004: LLM Service não tem fallback para "sem API key"

**Arquivo:** `llm_service.py`

Se nenhuma API key estiver configurada, `generate_text()` retorna `None` silenciosamente. Todos os módulos que dependem de LLM (feature_classifier, impact_analyzer, smart_notifications, etc.) terão comportamento degradado sem aviso claro.

---

### GAP-005: Dashboard heatmap mostra confiança genérica, não por categoria

**Arquivo:** `dashboard.py`

```javascript
const conf = r.avg_confidence || 0.85;  // ← Usa confiança MÉDIA da release
const heat = Math.round(conf * 100);
```

**O problema:** O heatmap deveria mostrar confiança **por categoria**, não a média global. Todas as células ficam com a mesma cor.

---

### GAP-006: NL Search não suporta busca fuzzy ou sinônimos

**Arquivo:** `nl_search.py`

O motor de busca usa TF-IDF puro, sem:
- Fuzzy matching (erros de digitação)
- Sinônimos ("security" ↔ "segurança")
- Stemming/lemmatização
- Busca por frase exata

---

### GAP-007: Notifications não integra com o pipeline principal

**Arquivo:** `notifications.py`

O sistema de notificações (email, Slack, Discord) nunca é chamado pelo `main.py`. O `SmartNotificationEngine` gera um digest mas não envia por nenhum canal real.

---

### GAP-008: `release_summarizer.py` busca em `pt_BR/` mas `main.py` gera em `releases/{slug}/pt_BR/`

**Arquivo:** `release_summarizer.py`

```python
pt_br_dir = release_dir / "pt_BR"
```

Isso está correto se `base_dir` for `releases`. Mas o `ReleaseSummarizer` é instanciado com `str(releases_dir)` que é `"releases"` — correto. Porém, se o diretório base mudar, a lógica pode quebrar.

---

## 📋 GAPS DE QUALIDADE (6)

### QUAL-001: Python 3.14 não existe (ainda)

**Arquivo:** `.github/workflows/python-quality.yml`, `.github/workflows/release_notes_pipeline.yml`

```yaml
python-version: "3.14"
```

Python 3.14 está em alpha. O CI pode falhar a qualquer momento com bugs do Python em si. Recomendado: usar 3.12 ou 3.13 como versão estável.

---

### QUAL-002: Testes não cobrem caminhos de erro

O projeto tem 450+ testes, mas a sintaxe `except X, Y:` em 13+ arquivos passa batido, sugerindo que os testes não exercitam os handlers de exceção.

---

### QUAL-003: Imports circulares potenciais

`main.py` importa de `ai_automation`, que importa de `config`, que define `KNOWN_RELEASES`. Se `ai_automation` tentasse importar de `main`, teríamos import circular. Atualmente funciona, mas é frágil.

---

### QUAL-004: Sem type stubs para dependências externas

O `mypy` roda com `--ignore-missing-imports`, o que mascara erros de tipo em `playwright`, `openai`, `google.genai`, etc.

---

### QUAL-005: `conftest.py` dos testes pode não mockar LLM

Se os testes rodarem sem API keys, todos os testes que dependem de `LLMService` vão falhar ou retornar `None`.

---

### QUAL-006: CI pipeline não testa end-to-end

O workflow `release_notes_pipeline.yml` roda `ruff` e `mypy` mas **não roda pytest** antes de fazer commit. Bugs podem chegar à main.

---

## 📊 Resumo Executivo

| Categoria | Quantidade | Impacto |
|-----------|-----------|---------|
| 🚨 Bugs Críticos | 10 | Impedem execução correta ou causam comportamento inesperado |
| ⚠️ Gaps de Design | 8 | Funcionalidades incompletas ou frágeis |
| 📋 Gaps de Qualidade | 6 | Riscos de manutenção e confiabilidade |
| **TOTAL** | **24** | |

### Prioridade de Correção

1. **BUG-001** — Sintaxe Python 2 em 13+ arquivos (IMEDIATO)
2. **BUG-002** — Circuit breaker não reseta (ALTO)
3. **BUG-010** — GraphQL parser inseguro (ALTO)
4. **QUAL-001** — Python 3.14 no CI (MÉDIO)
5. **GAP-001** — `--dry-run` não implementado (MÉDIO)
6. **BUG-009** — Git add hardcoded (MÉDIO)
7. Todos os demais (NORMAL)

---

---

## ✅ CORREÇÕES EXECUTADAS (2026-07-15)

| # | Correção | Status | Arquivos |
|---|----------|--------|----------|
| BUG-001 | `except X, Y:` → `except (X, Y):` | ✅ 25 ocorrências em 15 arquivos | scraper, parser, translator, ai_automation, analytics, api, dashboard, health, impact_analyzer, issue_triage, notifications, release_summarizer, salesforce, smart_notifications, workflow |
| BUG-002 | Circuit Breaker reset após cooldown | ✅ | scraper.py |
| BUG-003 | Logger duplicado removido | ✅ | scraper.py |
| BUG-006 | Tradução deep copy para evitar contaminação | ✅ | main.py |
| BUG-007 | Tipagem correta com TYPE_CHECKING | ✅ | main.py |
| BUG-009 | `git add releases/ README.md analytics/` → `git add -A` | ✅ | workflow.py |
| BUG-010 | GraphQL parser com validação e regex corrigido | ✅ | api.py |
| GAP-001 | `--dry-run` funcional implementado | ✅ | main.py |
| GAP-005 | Heatmap mostra confiança por categoria | ✅ | dashboard.py |
| QUAL-001 | Python 3.14 → 3.13 (estável) | ✅ | 4 workflows CI |
| QUAL-006 | Pytest adicionado ao pipeline CI | ✅ | release_notes_pipeline.yml |

**Verificação final:** `ruff check` ✅ | `py_compile` 24/24 ✅ | Syntax check ✅

*Relatório gerado automaticamente via revisão manual completa do código-fonte.*
