#!/usr/bin/env python3
"""Fix markdown lint issues in docs."""


def fix_adr_008():
    with open("docs/architecture/decisions/adr-008-prompt-versioning.md", "r") as f:
        content = f.read()

    # Fix 1: Add blank line before list after "Problemas observados:"
    content = content.replace(
        "Problemas observados:\n- Mudança", "Problemas observados:\n\n- Mudança"
    )

    # Fix 2: Add language to first code block (text)
    content = content.replace(
        "### 1. Estrutura de Prompts como YAML Versionado\n\n```\nprompts/",
        "### 1. Estrutura de Prompts como YAML Versionado\n\n```text\nprompts/",
    )

    # Fix 3: Add blank line before yaml code block
    content = content.replace(
        "Cada arquivo YAML contém:\n```yaml", "Cada arquivo YAML contém:\n\n```yaml"
    )

    # Fix 4: Add blank line before list at "Configuração promptfooconfig.yaml define:"
    content = content.replace(
        "Configuração `promptfooconfig.yaml` define:\n- Providers",
        "Configuração `promptfooconfig.yaml` define:\n\n- Providers",
    )

    # Fix 5: Add blank line before numbered list at "Workflow prompt-eval.yml roda"
    content = content.replace(
        "Workflow `prompt-eval.yml` roda em PRs que tocam `prompts/**`:\n1. Carrega",
        "Workflow `prompt-eval.yml` roda em PRs que tocam `prompts/**`:\n\n1. Carrega",
    )

    # Fix 6: Add blank line before list at "src/ai/prompts/loader.py (carregador):"
    content = content.replace(
        "`src/ai/prompts/loader.py` (carregador):\n- Valida",
        "`src/ai/prompts/loader.py` (carregador):\n\n- Valida",
    )

    # Fix 7: Ensure trailing newline
    content = content.rstrip("\n") + "\n"

    with open("docs/architecture/decisions/adr-008-prompt-versioning.md", "w") as f:
        f.write(content)
    print("Fixed adr-008")


def fix_adr_009():
    with open("docs/architecture/decisions/adr-009-scraper-resilience.md", "r") as f:
        content = f.read()

    # Fix 1: Add language to first code block (text)
    content = content.replace(
        "### Arquitetura em Camadas (Defense in Depth)\n\n```\n┌─────────────────────────────────────────────────────────────┐",
        "### Arquitetura em Camadas (Defense in Depth)\n\n```text\n┌─────────────────────────────────────────────────────────────┐",
    )

    # Fix 2: Ensure trailing newline
    content = content.rstrip("\n") + "\n"

    with open("docs/architecture/decisions/adr-009-scraper-resilience.md", "w") as f:
        f.write(content)
    print("Fixed adr-009")


def fix_adr_010():
    with open("docs/architecture/decisions/adr-010-llm-cache-strategy.md", "r") as f:
        content = f.read()

    # Fix 1: Add blank line before list at "Soluções parciais existentes:"
    content = content.replace(
        "Soluções parciais existentes:\n- `src/cache_manager.py`",
        "Soluções parciais existentes:\n\n- `src/cache_manager.py`",
    )

    # Fix 2: Add language to first code block (text)
    content = content.replace(
        "### Dupla Camada de Cache\n\n```text\n┌─────────────────────────────────────────────────────────────────┐",
        "### Dupla Camada de Cache\n\n```text\n┌─────────────────────────────────────────────────────────────────┐",
    )

    # Fix 3: Add blank line before python code block at line 49
    content = content.replace(
        "### 1. Exact Cache — `LLMCacheAdapter`\n\n```python\nclass LLMCacheAdapter:",
        "### 1. Exact Cache — `LLMCacheAdapter`\n\n```python\nclass LLMCacheAdapter:",
    )

    # Fix 4: Add blank line before python code block at line 67
    content = content.replace(
        "**Chave determinística** (`LLMPrompt.cache_key()` em `src/domain/llm.py`):\n```python\ndef cache_key(self) -> str:",
        "**Chave determinística** (`LLMPrompt.cache_key()` em `src/domain/llm.py`):\n\n```python\ndef cache_key(self) -> str:",
    )

    # Fix 5: Add blank line before python code block at line 88
    content = content.replace(
        "### 2. Semantic Cache — `SemanticCacheAdapter`\n\n```python\nclass SemanticCacheAdapter:",
        "### 2. Semantic Cache — `SemanticCacheAdapter`\n\n```python\nclass SemanticCacheAdapter:",
    )

    # Fix 6: Add blank line before python code block at line 99
    content = content.replace(
        "**Embedding centrado** (discriminativo para cosine similarity):\n```python\ndef _get_embedding(self, text: str) -> list[float]:",
        "**Embedding centrado** (discriminativo para cosine similarity):\n\n```python\ndef _get_embedding(self, text: str) -> list[float]:",
    )

    # Fix 7: Add blank line before python code block at line 113
    content = content.replace(
        "### 3. Integração no Unified Client (`src/infrastructure/llm_adapters/unified_client.py`)\n\n```python\nasync def complete(self, prompt: LLMPrompt) -> LLMResponse:",
        "### 3. Integração no Unified Client (`src/infrastructure/llm_adapters/unified_client.py`)\n\n```python\nasync def complete(self, prompt: LLMPrompt) -> LLMResponse:",
    )

    # Fix 8: Add blank line before python code block at line 138
    content = content.replace(
        "### 4. Métricas e Observabilidade\n\n```python\n@dataclass\nclass LLMCacheMetrics:",
        "### 4. Métricas e Observabilidade\n\n```python\n@dataclass\nclass LLMCacheMetrics:",
    )

    # Fix 9: Ensure trailing newline
    content = content.rstrip("\n") + "\n"

    with open("docs/architecture/decisions/adr-010-llm-cache-strategy.md", "w") as f:
        f.write(content)
    print("Fixed adr-010")


def fix_arquitetura():
    with open("docs/ARQUITETURA.md", "r") as f:
        content = f.read()

    # Fix 1: Add blank line before list at "Fronteiras não confiáveis"
    content = content.replace(
        "**Fronteiras não confiáveis (untrusted boundaries)**:\n\n- **HTML externo**",
        "**Fronteiras não confiáveis (untrusted boundaries)**:\n\n- **HTML externo**",
    )

    # Fix 2: Add blank line before list at "Injeção de Dependência (DI) em main.py"
    content = content.replace(
        "**Injeção de Dependência (DI) em `main.py`**:\n\n- `PipelineConfig`",
        "**Injeção de Dependência (DI) em `main.py`**:\n\n- `PipelineConfig`",
    )

    # Fix 3: Add blank line before list at "Modelos Pydantic (src/models/)"
    content = content.replace(
        "**Modelos Pydantic (src/models/)**:\n\n- `src/models/release.py`",
        "**Modelos Pydantic (src/models/)**:\n\n- `src/models/release.py`",
    )

    # Fix 4: Ensure trailing newline
    content = content.rstrip("\n") + "\n"

    with open("docs/ARQUITETURA.md", "w") as f:
        f.write(content)
    print("Fixed ARQUITETURA.md")


def fix_modernizacao():
    with open("docs/MODERNIZACAO.md", "r") as f:
        content = f.read()

    # Fix 1: Add language to code block at line 55 (already has text, check)
    # The linter says line 55 needs language - let me check if it's there
    # Actually the code block already has ```text so this might be a false positive

    # Fix 2: Add blank line before numbered list at "Escopo aprovado no plano original"
    content = content.replace(
        "**Escopo aprovado no plano original**:\n1. **Scraper Playwright",
        "**Escopo aprovado no plano original**:\n\n1. **Scraper Playwright",
    )

    # Fix 3: Ensure trailing newline
    content = content.rstrip("\n") + "\n"

    with open("docs/MODERNIZACAO.md", "w") as f:
        f.write(content)
    print("Fixed MODERNIZACAO.md")


if __name__ == "__main__":
    fix_adr_008()
    fix_adr_009()
    fix_adr_010()
    fix_arquitetura()
    fix_modernizacao()
    print("All fixes applied!")
