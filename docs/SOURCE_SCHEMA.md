# SOURCE_SCHEMA.md — Salesforce Help Portal DOM Reference

> **Status:** Living document — maintained as a contract between the scraper (`src/scraper.py`) and the Salesforce Help portal DOM structure.
>
> **Last validated:** 2026-09-01
>
> **Purpose:** Single source of truth for all CSS selectors, classes, HTML attributes, and expected DOM structures used by the pipeline. When Salesforce changes its portal, this document is updated **before** the code is patched.

---

## 1. Overview

The Salesforce-WebDev pipeline scrapes three main pages from `https://help.salesforce.com`:

| Page | URL Pattern | Purpose |
|------|-------------|---------|
| **Release Notes Index** | `/s/articleView?id=release-notes.salesforce_release_notes.htm&release=<id>&type=5` | Topic hierarchy (ToC) |
| **Feature Impact** | `/s/articleView?id=release-notes.rn_feature_impact.htm&release=<id>&type=5` | All features with availability flags |
| **Individual Article** | `/s/articleView?id=release-notes.<topic>.htm&release=<id>&type=5` | Deep-dive into a feature |

All requests include the `&language=pt_BR` parameter to retrieve localized content.

---

## 2. Selectors Catalog

### 2.1 ToC Container (Table of Contents)

The portal renders the navigation tree inside one of these containers. Selectors are tried in order (see `src/parser.py:24-30` and `src/scraper.py:332-337`):

```css
.toc-container          /* Primary */
ul.tree                 /* Secondary */
[role="tree"]           /* ARIA fallback */
nav.toc                 /* Semantic fallback */
.slds-tree__group       /* SLDS framework */
```

### 2.2 Tree Items (Navigation Nodes)

Each node in the ToC uses ARIA roles for accessibility:

```html
<li role="treeitem" aria-level="1">  <!-- Root (ignored by parser) -->
  <ul>
    <li role="treeitem" aria-level="2">  <!-- Top-level category -->
      <span class="tree-item-label">Desenvolvimento</span>
      <ul>
        <li role="treeitem" aria-level="3">  <!-- Subcategory or article -->
          <div class="slds-tree__item" data-is-link="true" data-node-id="rn_apex">
            <a href="/s/articleView?id=release-notes.rn_apex.htm&...">Apex</a>
          </div>
        </li>
      </ul>
    </li>
  </ul>
</li>
```

**Key attributes:**

| Attribute | Meaning | Used by |
|-----------|---------|---------|
| `role="treeitem"` | ARIA tree item | All parsers |
| `aria-level="N"` | Hierarchy depth (1=root, 2+=content) | `ReleaseNotesParser` |
| `aria-expanded="false"` | Collapsed node | `_expand_toc_nodes()` |
| `data-is-link="true"` | Leaf article (not a category) | `_build_node()` |
| `data-node-id="rn_*"` | Unique ID for the node (e.g. `rn_apex`) | `_get_node_id()` |

### 2.3 Feature Impact Page Structure

The feature impact page renders all features with availability flags in a table:

```html
<table>
  <thead>
    <tr>
      <th>RECURSO</th>
      <th>USUÁRIOS</th>
      <th>ADMS</th>
      <th>CONFIG</th>
      <th>CONTATO</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><a href="/s/articleView?id=release-notes.rn_apex_rest.htm">Apex REST Annotations</a></td>
      <td>Yes</td>
      <td>Yes</td>
      <td>No</td>
      <td>No</td>
    </tr>
  </tbody>
</table>
```

**Tab-separated format (extracted via `inner_text`):**

```
Plataforma
Enhanced Flow Builder\tYes\tYes\tNo\tNo
New API Versioning\tYes\tYes\tYes\tNo
```

**Flag columns (in order):**

| Column | Field | Boolean when value is "Yes" |
|--------|-------|----------------------------|
| 1 | `available_users` | `Yes` |
| 2 | `available_admins` | `Yes` |
| 3 | `requires_config` | `Yes` |
| 4 | `contact_sf` | `Yes` |

### 2.4 Article Content (Per-Feature Page)

Individual article pages use semantic HTML for the main content:

```html
<article>
  <h1>Feature Name</h1>
  <h2>Why is this important?</h2>  <!-- English: "Why" -->
  <p>Summary text...</p>
  <h3>Where</h3>
  <p>Setup instructions...</p>
</article>
```

**Content selectors (in priority order, see `src/parser.py:115-117`):**

```css
article                  /* Semantic main content */
#articleViewContent      /* Salesforce legacy ID */
div.content              /* Generic fallback */
```

**Summary detection (see `src/parser.py:108-110`):**

The parser looks for these header texts (case-insensitive) to extract a feature summary:

| Locale | Header Text |
|--------|-------------|
| `pt-BR` | "Por que essa alteração é importante", "Por que" |
| `en` | "Why" |

---

## 3. Section Headers

The Feature Impact page organizes features by category using section headers. These are recognized by `FeatureImpactParser` (see `src/parser.py:569-570`):

**Known section headers (portuguese):**

```python
SECTION_HEADERS = {
    "Plataforma",
    "Desenvolvimento",
    "Vendas",
    "Serviço",
    "Marketing",
    "Commerce",
    "Automação",
    "Análise de dados",
    "Data 360",
    "Experience Cloud",
    "Field Service",
    "Hyperforce",
    "Setores",
    "MuleSoft",
    "Aplicativo móvel",
    "OmniStudio",
    "Partner Cloud",
    "Gerenciamento de receita",
    "Integrações do Salesforce para Slack",
    "Segurança, identidade e privacidade",
    "Outros produtos e serviços do Salesforce",
    "Documentação legal",
    "Salesforce geral",
    "Agentforce",
    "Personalização",
}
```

**Table header detection (see `src/parser.py:583-584`):**

A line is considered a table header when it contains both `"RECURSO"` and `"ATIVADO"` (or `"USUÁRIOS"` for the new format).

---

## 4. Excluded Navigation Nodes

Some ToC nodes are parsed but then filtered out by `EXCLUDED_NODE_SLUGS` in `src/config.py:61-68`. These are administrative pages, not feature content:

```python
EXCLUDED_NODE_SLUGS = {
    "features_released_monthly",  # "Recursos lançados mensalmente"
    "change_log",                 # "Log de mudanças"
    "feature_impact",             # "Impacto das features" (we have a separate parser)
    "previous_release_notes",     # "Notas de releases anteriores"
}
```

---

## 5. URL Patterns

### 5.1 Release Notes Index

```
https://help.salesforce.com/s/articleView
  ?id=release-notes.salesforce_release_notes.htm
  &release={release_id}
  &type=5
  &language=pt_BR
```

Defined in `src/config.py:25-31` as `BASE_URL`.

### 5.2 Feature Impact

```
https://help.salesforce.com/s/articleView
  ?id=release-notes.rn_feature_impact.htm
  &release={release_id}
  &type=5
  &language=pt_BR
```

Defined in `src/config.py:33-39` as `FEATURE_IMPACT_URL`.

### 5.3 Release-in-a-Box PDF

```
https://www.salesforce.com/en-us/wp-content/uploads/sites/4/
  documents/PDF/release-in-a-box-{season}-{year_short}-v{version}.pdf
```

Defined in `src/config.py:41-44` as `PDF_URL_TEMPLATE`.

---

## 6. Release ID Mapping

The Salesforce portal uses integer `release_id` parameters that follow a predictable pattern (see `src/config.py:177-184`):

| Release Name | `release_id` | Slug |
|--------------|--------------|------|
| Spring '25 | 254 | `spring_25` |
| Summer '25 | 256 | `summer_25` |
| Winter '26 | 258 | `winter_26` |
| Spring '26 | 260 | `spring_26` |
| Summer '26 | 262 | `summer_26` |
| Winter '27 | 264 | `winter_27` |

**Pattern:** Each release increments by 2. The pattern is `254 + (step * 2)` where `step` follows Spring/Summer/Winter rotation.

---

## 7. Resilience Strategies

The scraper implements several resilience patterns to handle DOM changes gracefully:

### 7.1 Multi-Selector Fallback

Before failing, the parser tries multiple CSS selectors for the same element (see `src/parser.py:131-135` and `src/scraper.py:332-349`).

### 7.2 Link Extraction Strategies

For feature impact pages, the scraper uses three strategies in order (`src/scraper.py:485-548`):

1. **Table rows** — find `<tr>` with `<td>` cells, extract name + link
2. **List items** — find `<li>` with links containing `release-notes`
3. **Any anchor** — find any `<a>` with `release-notes` in href

### 7.3 Safe Element Access

All `query_selector` calls are followed by `None` checks (`src/scraper.py:340-341`):

```python
element = await page.query_selector(selector)
if element is None:
    continue
```

### 7.4 Optional Chaining in JavaScript Evaluation

When extracting content via `page.evaluate()`, optional chaining (`?.`) is used (`src/scraper.py:178-185`):

```javascript
return Array.from(document.querySelectorAll('.feature-item')).map(item => ({
    name: item.querySelector('.feature-name')?.textContent?.trim(),
    description: item.querySelector('.feature-description')?.textContent?.trim(),
    category: item.querySelector('.feature-category')?.textContent?.trim()
}));
```

---

## 8. Validation

### 8.1 Snapshot Tests

The pipeline includes snapshot tests in `tests/test_snapshot.py` that capture expected parser output. When the DOM changes, these tests will fail and require snapshot regeneration:

```bash
uv run pytest tests/test_snapshot.py           # Run snapshots
uv run pytest tests/test_snapshot.py --snapshot-update  # Update after intentional changes
```

### 8.2 Circuit Breaker

The scraper includes a circuit breaker (`src/circuit_breaker.py`) that:
- Opens after **3 consecutive failures**
- Stays open for **60 seconds** before allowing a retry
- Returns stale cache (if available) when open

### 8.3 Rate Limiting

The scraper uses a `RateLimiter` (referenced in `src/scraper.py:578`) that throttles requests to avoid IP blocks. Default configuration: **2 requests/second**.

---

## 9. Change Log

| Date | Salesforce Change | Pipeline Adaptation |
|------|-------------------|---------------------|
| 2025-XX-XX | Initial implementation | First 5 releases supported |
| 2026-09-01 | Snapshot tests added | `tests/test_snapshot.py` + `tests/__snapshots__/` |

---

## 10. Maintenance

When Salesforce updates its portal:

1. **Run a probe** to detect new failures:
   ```bash
   uv run pytest tests/test_snapshot.py -v
   ```

2. **Inspect the failure** — read the diff in the test output

3. **Update selectors** in `src/parser.py` and `src/scraper.py`

4. **Update this document** with the new selectors/structure

5. **Regenerate snapshots**:
   ```bash
   uv run pytest tests/test_snapshot.py --snapshot-update
   ```

6. **Validate** end-to-end:
   ```bash
   uv run ruff check . && uv run black --check . && uv run mypy src/ && uv run pytest
   ```

7. **Commit** with a `fix(scraper):` or `fix(parser):` conventional commit message.

---

## Related Files

- `src/scraper.py` — Playwright-based scraper with all DOM access logic
- `src/parser.py` — BeautifulSoup-based parser with ToC extraction
- `src/config.py` — Configuration constants (URLs, selectors, release IDs)
- `src/circuit_breaker.py` — Failure tracking and circuit breaker
- `tests/test_snapshot.py` — Snapshot tests for regression detection
- `tests/__snapshots__/test_snapshot.ambr` — Saved snapshot data
