# Enhanced Search

The Salesforce Release Notes documentation site features an enhanced search system built on top of MkDocs Material's Lunr.js integration.

## Features

### 1. **Fuzzy Matching**
Typo-tolerant search powered by Levenshtein distance. Try searching for:
- `apex` → matches "Apex", "Apache", "APE"
- `flow builder` → matches "Flow", "Builder", "Flows"

### 2. **Salesforce Synonym Expansion**
The search automatically expands queries using Salesforce terminology:

| Term | Expands to |
|------|------------|
| `lwc` | Lightning Web Components, Lightning |
| `apex` | Apex Code, Salesforce Apex |
| `flow` | Salesforce Flow, Process Builder |
| `einstein` | AI, Copilot, Einstein |
| `tableau` | BI, Business Intelligence, Analytics |
| `mulesoft` | Mule, Integration |
| `experience cloud` | Community Cloud, Communities, Portal |
| `agentforce` | Agent Force, Einstein Agents |

### 3. **Keyboard Shortcuts**
- `/` — Focus search
- `Esc` — Blur search
- `Enter` — Execute search and save to history

### 4. **Recent Searches**
The 5 most recent searches are saved in `localStorage` and displayed as placeholders.

### 5. **Result Highlighting**
Matching terms are highlighted in both titles and teaser text using the `<mark>` tag.

## How It Works

```
User Input → Debounce (200ms)
    ↓
Expand with Synonyms
    ↓
Fuzzy Match (Levenshtein)
    ↓
Score + Sort
    ↓
Display with Fuzzy Indicator (★)
```

## Configuration

Search configuration is in `mkdocs.yml`:

```yaml
plugins:
  - search:
      separator: "[\s\-\.\,\:\/\(\)\[\]]+"
      lang:
        - en
        - pt
      prebuild_index:
        enabled: true
        method: "local"
```

## Customization

To add more Salesforce synonyms, edit `docs/assets/javascripts/enhanced_search.js`:

```javascript
const SF_SYNONYMS = {
  // Add your custom mappings here
  myTerm: ["synonym1", "synonym2"],
};
```

## Performance

- **Index size**: ~50-200KB (depends on doc size)
- **Search time**: <50ms for typical queries
- **Debounce**: 200ms (prevents excessive computation)
- **Fuzzy threshold**: 0.75 (75% similarity required)

## Files

- `docs/assets/javascripts/enhanced_search.js` — Search logic
- `docs/assets/stylesheets/enhanced_search.css` — Visual styling
- `mkdocs.yml` — Plugin configuration
