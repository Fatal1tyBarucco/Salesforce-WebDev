Aqui está um **prompt robusto e detalhado** para implementação do **Salesforce-WebDev** por um modelo de IA como o **OpenCode**, alinhado com as melhores práticas de engenharia de software, resiliência, governança e expansão funcional descritos no documento.

---

### **Prompt para Implementação Robusta do Salesforce-WebDev**

**Contexto:**
Você é um **Arquiteto e Desenvolvedor Master (CTA-level)** especializado em **Salesforce, Python, ETL, e Automação de Documentação**. Seu objetivo é implementar um **pipeline ETL resiliente** para extrair, processar e versionar as notas de lançamento da Salesforce, transformando dados não estruturados em documentação estruturada e consumível via **MkDocs**.

O projeto deve seguir os **princípios do Salesforce Well-Architected**, **Apex Enterprise Patterns (Service, Domain, Selector)**, e ser **bulk-safe**, **governor-limit-friendly**, e **seguro contra falhas de referência nula**.

---

---

### **Requisitos Funcionais e Não Funcionais**

#### **1. Arquitetura e Design**
- **Princípio de Separação de Responsabilidades (SoC):**
  - Dividir o sistema em camadas isoladas:
    - **`scraper.py`**: Responsável por requisições HTTP e manipulação de conteúdo dinâmico via **Playwright**.
    - **`parser.py`**: Analisar o DOM, identificar e categorizar funcionalidades das notas de lançamento.
    - **`generator.py`**: Consolidar dados processados em arquivos **Markdown** para o **MkDocs**.
    - **`api.py`**: Expor uma **API REST** (FastAPI) para acesso programático aos dados.
    - **`notifications.py`**: Disparar alertas via **Slack/Discord** em falhas críticas.
    - **`analytics.py`**: Painel de monitoramento de saúde do pipeline.

- **Resiliência:**
  - Implementar:
    - **Limitador de taxa (Token Bucket)**: Máximo de **2 requisições/segundo** para evitar bloqueios de IP.
    - **Cache com TTL de 24h**: Armazenar resultados da raspagem para evitar retrabalho.
    - **Backoff exponencial com jitter**: Aumentar intervalo entre tentativas após falhas.
    - **Circuit Breaker**: Desativar requisições por **60 segundos** após **3 falhas consecutivas**.

- **Concorrência:**
  - Usar **`asyncio`** e **Playwright Async** para execução paralela de tarefas de I/O.

---

#### **2. Qualidade de Código e Governança**
- **Python 3.12+** com:
  - **Type hints** (mypy em modo rigoroso: `strict = true`).
  - **Formatação**: **Black** (limite de linha: 100 caracteres).
  - **Linting**: **Ruff** para detecção precoce de erros.
  - **Gerenciamento de dependências**: **`uv`** com arquivo de lock determinístico.
- **Testes:**
  - **pytest** com **>95% de cobertura**.
  - **Testes de snapshot** para `scraper.py` e `parser.py`:
    - Capturar **HTML bruto** e **JSON estruturado** como snapshots.
    - Comparar resultados atuais com snapshots salvos para detectar mudanças inesperadas.
  - **Test Data Factory** para geração de dados de teste realistas.
- **Documentação:**
  - **README.md**: Descrição clara do projeto, instruções de instalação, uso e contribuição.
  - **CONTRIBUTING.md**: Diretrizes para:
    - Abertura de **issues**.
    - Estrutura de **pull requests** (Conventional Commits: `feat(scope): ...`, `fix(scope): ...`).
    - Expectativas de **cobertura de testes** e **qualidade de código**.
  - **docs/SOURCE_SCHEMA.md**: Documentar a estrutura esperada do **DOM** do site da Salesforce (seletores CSS, classes, etc.).

---

#### **3. Fluxos de Trabalho e CI/CD**
- **Desenvolvimento Local:**
  - Comandos padronizados:
    ```bash
    git clone https://github.com/Fatal1tyBarucco/Salesforce-WebDev.git
    uv sync --extra dev
    uv run playwright install chromium
    uv run ruff check .
    uv run black --check .
    uv run mypy src/
    uv run pytest
    ```
- **GitHub Actions:**
  - Pipeline acionado em **push** ou **pull request** com:
    1. **Linting** (`Ruff`).
    2. **Formatação** (`Black`).
    3. **Checagem de tipos** (`mypy`).
    4. **Testes unitários** (`pytest`).
    5. **Execução do ETL** para gerar documentação.
    6. **Implantação automática** do site **MkDocs**.

---

#### **4. Expansão Funcional**
- **API REST (FastAPI):**
  - Endpoints para:
    - Recuperar notas de lançamento **filtradas por release, categoria ou palavra-chave**.
    - Suportar **OpenAPI/Swagger** para documentação automática.
  - Exemplo de uso:
    ```python
    @app.get("/releases/{release_name}/features")
    async def get_features(release_name: str, category: str = None):
        """Retorna funcionalidades de um release, opcionalmente filtradas por categoria."""
    ```
- **Melhorias na Documentação:**
  - **Pesquisa avançada**: Integração com **Lunr.js** ou **FlexSearch** para indexação e busca rápida.
  - **Filtros interativos**: Permitir comparação entre releases ou filtragem por categorias (ex: Apex, LWC).
- **Novas Fontes de Dados:**
  - **Blog da Salesforce Developer Relations**: Raspagem de artigos recentes.
  - **Trailblazer Community**: Extração de postagens populares.
  - **Referência da API Salesforce**: Monitoramento de mudanças.
  - **YouTube da Salesforce**: Extração de vídeos e transcrições.

---
---
### **Estrutura de Diretórios Proposta**
```plaintext
Salesforce-WebDev/
├── src/
│   ├── scraper.py          # Raspagem de dados (Playwright Async)
│   ├── parser.py           # Parsing do DOM e categorização
│   ├── generator.py        # Geração de Markdown para MkDocs
│   ├── api.py              # API REST (FastAPI)
│   ├── notifications.py    # Alertas (Slack/Discord)
│   ├── analytics.py        # Painel de monitoramento
│   └── __tests__/          # Testes unitários (pytest)
│       ├── test_scraper.py
│       ├── test_parser.py
│       └── test_api.py
├── docs/
│   ├── SOURCE_SCHEMA.md    # Estrutura esperada do DOM da Salesforce
│   └── releases/           # Documentação gerada (MkDocs)
├── .github/
│   └── workflows/          # GitHub Actions (CI/CD)
├── README.md               # Documentação principal
├── CONTRIBUTING.md         # Diretrizes de contribuição
└── pyproject.toml          # Dependências (uv)
```

---
---
### **Exemplo de Código para `scraper.py` (Resiliente e Bulk-Safe)**
```python
import asyncio
from typing import Optional, List, Dict
from playwright.async_api import async_playwright, Browser, Page
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from circuitbreaker import circuit
from cachetools import TTLCache

# Cache com TTL de 24h (86400 segundos)
cache = TTLCache(maxsize=100, ttl=86400)

# Circuit Breaker: 3 falhas consecutivas → 60 segundos de timeout
@circuit(failure_threshold=3, recovery_timeout=60)
@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception_type(Exception),
)
async def scrape_release_notes(release_url: str) -> Optional[List[Dict[str, str]]]:
    """
    Raspa as notas de lançamento de uma URL específica da Salesforce.

    Args:
        release_url: URL da página de notas de lançamento.

    Returns:
        Lista de dicionários com funcionalidades (nome, descrição, categoria) ou None em caso de falha.

    Raises:
        Exception: Se o circuit breaker estiver aberto ou após 5 tentativas com falha.
    """
    if release_url in cache:
        return cache[release_url]

    async with async_playwright() as p:
        browser: Browser = await p.chromium.launch()
        page: Page = await browser.new_page()

        try:
            await page.goto(release_url, timeout=10000)
            await page.wait_for_selector(".release-notes-container", timeout=5000)

            # Lógica para extrair funcionalidades (exemplo simplificado)
            features = await page.evaluate("""
                () => {
                    return Array.from(document.querySelectorAll('.feature-item')).map(item => ({
                        name: item.querySelector('.feature-name')?.textContent?.trim(),
                        description: item.querySelector('.feature-description')?.textContent?.trim(),
                        category: item.querySelector('.feature-category')?.textContent?.trim()
                    }));
                }
            """)

            cache[release_url] = features
            return features

        except Exception as e:
            print(f"Falha ao raspar {release_url}: {e}")
            raise
        finally:
            await browser.close()

# Exemplo de uso
async def main():
    release_url = "https://help.salesforce.com/s/articleView?id=sf.release_notes.winter27&type=5"
    features = await scrape_release_notes(release_url)
    if features:
        print(f"Encontradas {len(features)} funcionalidades.")

if __name__ == "__main__":
    asyncio.run(main())
```

---
---
### **Exemplo de Teste de Snapshot para `test_scraper.py`**
```python
import pytest
from scraper import scrape_release_notes

@pytest.mark.asyncio
async def test_scrape_release_notes_snapshot(snapshot):
    """Testa se a raspagem retorna resultados consistentes com o snapshot."""
    release_url = "https://help.salesforce.com/s/articleView?id=sf.release_notes.winter27&type=5"
    features = await scrape_release_notes(release_url)

    # Verifica se o resultado corresponde ao snapshot salvo
    assert features == snapshot

# Para gerar o snapshot pela primeira vez, execute:
# pytest --snapshot-update
```

---
---
### **Exemplo de API REST com FastAPI (`api.py`)**
```python
from fastapi import FastAPI, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from scraper import scrape_release_notes

app = FastAPI(title="Salesforce-WebDev API", version="1.0.0")

class Feature(BaseModel):
    name: str
    description: str
    category: str

@app.get("/releases/{release_name}/features", response_model=List[Feature])
async def get_features(
    release_name: str,
    category: Optional[str] = None,
    limit: int = 100
) -> List[Feature]:
    """
    Retorna funcionalidades de um release, opcionalmente filtradas por categoria.

    Args:
        release_name: Nome do release (ex: "winter27").
        category: Filtro por categoria (opcional).
        limit: Limite de resultados (padrão: 100).

    Returns:
        Lista de funcionalidades.
    """
    release_url = f"https://help.salesforce.com/s/articleView?id=sf.release_notes.{release_name}&type=5"
    features = await scrape_release_notes(release_url)

    if not features:
        raise HTTPException(status_code=404, detail="Release não encontrado ou falha na raspagem.")

    if category:
        features = [f for f in features if f.get("category", "").lower() == category.lower()]

    return features[:limit]
```

---
---
### **Checklist de Implementação**
| **Tarefa** | **Status** | **Prioridade** | **Dependências** |
|------------|------------|----------------|------------------|
| Implementar `scraper.py` com resiliência (cache, circuit breaker, retry) | ⬜ | Alta | Playwright, tenacity, circuitbreaker |
| Implementar `parser.py` para categorização de funcionalidades | ⬜ | Alta | BeautifulSoup4 ou lxml |
| Implementar `generator.py` para geração de Markdown | ⬜ | Alta | MkDocs |
| Configurar `api.py` com FastAPI | ⬜ | Média | FastAPI, Pydantic |
| Implementar `notifications.py` (Slack/Discord) | ⬜ | Média | requests, webhooks |
| Criar testes de snapshot para `scraper.py` e `parser.py` | ⬜ | Alta | pytest-snapshot |
| Configurar GitHub Actions (CI/CD) | ⬜ | Alta | GitHub Actions |
| Documentar `SOURCE_SCHEMA.md` | ⬜ | Média | - |
| Criar `CONTRIBUTING.md` | ⬜ | Baixa | - |
| Adicionar pesquisa avançada (Lunr.js) | ⬜ | Baixa | MkDocs + Lunr.js |
| Expandir para novas fontes de dados (Blog, Trailblazer) | ⬜ | Baixa | Playwright |

---
---
### **Comandos para Validação e Deploy**
```bash
# Instalar dependências
uv sync --extra dev

# Verificar qualidade de código
uv run ruff check .
uv run black --check .
uv run mypy src/

# Executar testes
uv run pytest --snapshot-update  # Gerar snapshots pela primeira vez
uv run pytest

# Executar pipeline ETL
uv run python -m src.main

# Iniciar API localmente
uv run uvicorn src.api:app --reload

# Gerar documentação com MkDocs
uv run mkdocs serve
```

---
---
### **Observações Finais**
- **Segurança**: Garantir que o código seja **à prova de falhas de referência nula** (usar `Optional` e `get()` em dicionários).
- **Performance**: Monitorar **tempo de execução** e **uso de memória** do pipeline.
- **Escalabilidade**: Avaliar a necessidade de **processamento em lote** para Large Data Volumes (LDV).
- **Comunidade**: Divulgar o projeto em **Salesforce Developers Community**, **Reddit (r/salesforce)**, e **Commons Community Sprints**.
