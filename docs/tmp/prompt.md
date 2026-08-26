> O workflow atual é essencialmente um build/deploy de MkDocs. Ele não é um mecanismo de sincronização documental.



O workflow atual só dispara quando determinados caminhos são alterados (docs/**, mkdocs.yml, src/**, releases/**, README etc.) e então executa mkdocs build --strict e publica o resultado.

Isso deixa uma lacuna: uma alteração no código pode não produzir uma atualização documental adequada, mesmo que o código tenha mudado.

Além disso, o mkdocs.yml possui uma estrutura documental extensa, incluindo Architecture, Auto-Healing, Refatoração, Maintenance, Observability, Runbooks, Roadmap e API Reference.


---

1. Arquitetura que recomendo

Eu não transformaria simplesmente documentation-build.yml em um workflow gigantesco.

Recomendo separar responsabilidades:

flowchart TD
    A[Git Push / Schedule / Manual] --> B[Documentation Intelligence]

    B --> C[Repository Inventory]
    B --> D[Git History / Diff]
    B --> E[Current Documentation]
    B --> F[Architecture / Configuration Analysis]

    C --> G[Canonical Repository State]
    D --> G
    E --> H[Documentation Drift Analysis]
    F --> G

    G --> I[AI Documentation Reconciliation]
    H --> I

    I --> J{Changes Required?}

    J -->|No| K[Validation Only]
    J -->|Yes| L[Update Markdown Documentation]

    L --> M[Validate Links / Structure]
    M --> N[mkdocs build --strict]

    N --> O[Git Diff Validation]
    O --> P[Commit Documentation]
    P --> Q[Deploy GitHub Pages]

    K --> Q

O ponto fundamental é:

GitHub Repository = Source of Truth

A documentação não deve ser tratada como fonte de verdade.

A hierarquia deve ser:

Código/configuração/estrutura atual
             ↓
       Repository State
             ↓
     AI Documentation Analysis
             ↓
       docs/**/*.md
             ↓
          MkDocs
             ↓
       GitHub Pages

Assim, GitHub Pages é apenas a projeção publicada do estado atual do repositório.


---

2. Problema atual do workflow

O workflow atual possui alguns pontos que eu alteraria.

2.1 Trigger baseado em paths

Atualmente:

push:
  branches: ["main"]
  paths:
    - "docs/**"
    - "mkdocs.yml"
    - "src/**"
    - ...

Isso é inadequado para o objetivo novo.

Por exemplo:

src/foo.py
    ↓
documentação de foo.py deveria mudar

Mas:

docs/foo.md

pode não existir ou estar desatualizado.

A solução não é simplesmente adicionar mais paths.

2.2 O workflow não possui reconciliação

Hoje:

Repository
   ↓
MkDocs
   ↓
HTML

O novo modelo precisa ser:

Repository
   ↓
Inventory
   ↓
Diff
   ↓
Documentation Drift
   ↓
AI
   ↓
Documentation
   ↓
MkDocs


---

3. Particularidade importante do seu repositório

Há uma questão particularmente relevante no seu projeto.

O pyproject.toml declara:

Google GenAI

OpenAI-compatible client

OpenCode

OpenRouter

dependências específicas para documentação.


Porém, o LLMService atual documenta explicitamente uma cadeia:

1. Gemini
2. OpenCode
3. OpenRouter

e utiliza gemini-3.6-flash como modelo padrão do Gemini.

Isso é exatamente o que eu utilizaria na nova arquitetura.

Não criaria outro mecanismo de IA dentro do workflow.

O workflow deve reutilizar:

LLMService
    ↓
Gemini
    ↓ fallback
OpenCode
    ↓ fallback
OpenRouter

Isso evita duplicação da lógica de providers.


---

4. O que o novo sistema deve analisar

O agente não deve simplesmente "ler os arquivos Markdown".

Ele precisa construir um Repository Knowledge Graph / Repository Inventory.

Deve analisar

Área	Analisar

Python	.py
Configuração	.yml, .yaml, .toml, .json
GitHub Actions	.github/workflows/**
Scripts	.github/scripts/**
Documentação	docs/**
README	README.md, README.en.md
Arquitetura	architecture/**
APIs	src/**
Testes	tests/**
Docker	Dockerfile, compose etc.
Dependências	pyproject.toml, lockfiles
ADRs	architecture/decisions/**
Runbooks	runbooks/**
Roadmap	roadmap/**
Observability	observability/**


O tree atual do repositório confirma uma estrutura considerável, incluindo workflows, scripts, documentação, Dockerfile, relatórios, README e diversos artefatos.


---

5. Não recomendo enviar o repositório inteiro para o LLM

Esse é um ponto arquitetural importante.

Não faça:

700 arquivos
   ↓
LLM
   ↓
"gere toda documentação"

Isso será caro, lento e propenso a regressões.

Recomendo um pipeline incremental:

flowchart LR
    A[Git SHA] --> B[File Inventory]
    B --> C[SHA / Hash]
    C --> D{Alterado?}

    D -->|Não| E[Skip]
    D -->|Sim| F[Semantic Analysis]

    F --> G[Affected Documentation]
    G --> H[LLM Reconciliation]


---

6. Manifesto de documentação

Eu adicionaria um artefato interno:

docs/.documentation-manifest.json

Por exemplo:

{
  "repository_sha": "...",
  "generated_at": "...",
  "files": {
    "src/llm_service.py": {
      "sha": "...",
      "documentation": [
        "docs/api/llm_service.md"
      ]
    }
  }
}

Isso permite descobrir:

arquivo alterado
arquivo removido
arquivo criado
documentação órfã
documentação desatualizada

E principalmente:

Código removido
      ↓
manifest detecta ausência
      ↓
documentação relacionada
      ↓
remover/atualizar

Isso atende diretamente ao requisito de impedir documentação obsoleta.


---

7. Detecção de documentação órfã

Esse deve ser um requisito obrigatório.

Exemplo:

src/parser.py

gera:

docs/api/parser.md

Se:

src/parser.py

for excluído:

Git diff
   ↓
DELETE src/parser.py
   ↓
find references
   ↓
docs/api/parser.md
   ↓
DELETE ou REWRITE

Mas eu colocaria uma regra adicional:

> Nunca apagar documentação apenas porque o nome de um arquivo desapareceu.



O agente deve confirmar semanticamente que a documentação representa aquele componente.


---

8. Prompt principal de execução

O prompt deve ser bastante mais rígido do que um simples "atualize a documentação".

Abaixo está a versão que recomendo incorporar ao workflow/agente.

Documentation Intelligence — Repository Reconciliation Agent

Role

You are the Documentation Intelligence Agent for the "Fatal1tyBarucco/Salesforce-WebDev" repository.

Your responsibility is to maintain the repository documentation as an accurate, current and verifiable representation of the actual repository state.

The Git repository is the single source of truth.

GitHub Pages is only the published representation of the documentation generated from the repository.

Never treat existing documentation as authoritative when it conflicts with the current repository state.

---

Primary Objective

Perform a complete documentation reconciliation between:

1. The current repository state.
2. The Git history and current Git diff.
3. Existing documentation under "docs/".
4. "README.md".
5. "README.en.md".
6. "mkdocs.yml".
7. Source code under "src/".
8. Tests under "tests/".
9. GitHub Actions under ".github/workflows/".
10. Automation scripts under ".github/scripts/".
11. Configuration files.
12. Dependency definitions.
13. Docker configuration.
14. Architecture documentation.
15. ADRs.
16. Runbooks.
17. Roadmaps.
18. Observability documentation.
19. API documentation.
20. Any other repository artifact that materially describes system behavior.

---

Source-of-Truth Rule

The repository state always has priority.

Use this precedence:

1. Current source code.
2. Current configuration.
3. Current GitHub Actions.
4. Current dependency definitions.
5. Current tests.
6. Current repository structure.
7. Git history and diff.
8. Existing documentation.

If documentation contradicts the repository, update the documentation.

Never modify source code merely to make it consistent with documentation.

---

Repository Investigation

Before changing documentation:

1. Build a complete repository inventory

Identify:

- files
- directories
- source modules
- classes
- functions
- public APIs
- configuration
- workflows
- scripts
- tests
- dependencies
- documentation
- architecture artifacts
- ADRs
- runbooks
- roadmaps
- generated artifacts

Exclude:

- ".git"
- virtual environments
- caches
- build output
- temporary files
- secrets
- API keys
- credentials
- binary files unless their existence materially affects documentation.

---

Git Analysis

Inspect:

- current branch
- current commit SHA
- changed files
- added files
- modified files
- deleted files
- renamed files
- relevant recent commits

Determine the semantic impact of every relevant change.

Do not assume that a changed filename necessarily means documentation must change.

Analyze the actual content and behavioral impact.

---

Documentation Drift Detection

For every documentation artifact determine:

- Is the referenced component still present?
- Does the documented behavior still exist?
- Are filenames correct?
- Are paths correct?
- Are APIs correct?
- Are function/class names correct?
- Are configuration values correct?
- Are workflows correct?
- Are model/provider names correct?
- Are dependencies correct?
- Are architecture diagrams accurate?
- Are commands still valid?
- Are links valid?
- Are examples compatible with the current implementation?
- Does the documentation describe removed functionality?
- Does the documentation omit newly introduced functionality?

Classify each finding as:

- "CURRENT"
- "STALE"
- "MISSING"
- "ORPHANED"
- "CONTRADICTORY"
- "STRUCTURALLY_INVALID"
- "REQUIRES_REVIEW"

---

AI Analysis

Use the repository's existing LLM infrastructure.

Do not introduce a new provider architecture.

Use the existing provider chain and configured credentials/models.

Preferred provider order:

1. Google Gemini
2. OpenCode
3. OpenRouter

Respect the provider/model configuration already implemented by the repository.

Do not hard-code new API keys.

Do not expose credentials in logs, commits or generated documentation.

---

Documentation Generation Rules

When documentation requires modification:

1. Preserve the existing documentation structure where possible.
2. Preserve useful historical context when it remains accurate.
3. Remove statements that are no longer true.
4. Add missing current functionality.
5. Update obsolete examples.
6. Update obsolete commands.
7. Update obsolete paths.
8. Update obsolete architecture descriptions.
9. Update workflow descriptions.
10. Update dependency information.
11. Update provider/model information.
12. Update diagrams when architecture changed.
13. Update navigation when files are added or removed.
14. Remove documentation for functionality that no longer exists.
15. Never invent functionality.
16. Never infer undocumented behavior without evidence from the repository.
17. Never fabricate metrics, test coverage or performance results.

---

Deletion Rules

When a repository component is deleted:

1. Find documentation referring to it.
2. Determine whether the documentation describes exclusively the deleted component.
3. If exclusively obsolete, remove the documentation.
4. If partially obsolete, rewrite it to represent the remaining functionality.
5. Remove obsolete navigation entries from "mkdocs.yml".
6. Remove obsolete references from README files.
7. Remove obsolete cross-links.
8. Remove obsolete diagrams or update them.

Never leave dead documentation simply because it existed previously.

---

New Component Rules

When a new relevant component is detected:

1. Determine whether documentation already exists.
2. If not, create the appropriate documentation.
3. Place it in the correct documentation domain.
4. Add it to "mkdocs.yml" when appropriate.
5. Cross-reference related documentation.
6. Include usage examples when supported by repository evidence.
7. Include architecture implications when applicable.

---

README Synchronization

Verify that README files accurately represent:

- project purpose
- current architecture
- current capabilities
- current release information
- installation
- execution
- supported providers
- current workflows
- documentation links
- project structure

Do not preserve obsolete marketing or technical claims.

---

MkDocs Validation

After documentation reconciliation:

1. Validate all referenced files.
2. Validate internal links.
3. Validate navigation.
4. Validate Markdown.
5. Run:

"uv run mkdocs build --strict"

Treat build errors as blocking.

---

Quality Gate

Before committing:

Documentation correctness

- No obsolete file references.
- No references to deleted components.
- No missing documentation for important new components.
- No contradictory architecture statements.
- No obsolete provider/model claims.
- No broken navigation.
- No broken internal links.
- No fabricated information.

Repository consistency

The generated documentation must describe the repository as it exists at the current commit.

---

Change Detection

Do not commit changes when:

- no documentation drift exists;
- generated content is identical;
- only insignificant timestamps changed;
- analysis produced no actionable differences.

If documentation changed, produce a concise summary containing:

- changed documentation files;
- created documentation files;
- deleted documentation files;
- updated navigation;
- detected stale documentation;
- detected orphaned documentation;
- validation result.

---

Commit Safety

Documentation changes must be isolated from source-code changes.

Do not modify application/source code.

Do not modify secrets.

Do not modify workflow behavior unless explicitly instructed by the workflow implementation itself.

Do not overwrite unrelated developer changes.

---

Final Objective

At the end of every successful execution:

"Current Repository State == Current Documentation State == Published GitHub Pages State"

The documentation must never describe a previous version of the repository as if it were current.
---

9. Workflow recomendado

Eu dividiria o atual documentation-build.yml em dois conceitos:

A. documentation-sync.yml

Responsável por:

detect
 ↓
analyze
 ↓
reconcile
 ↓
modify docs
 ↓
validate
 ↓
commit

B. documentation-build.yml

Responsável exclusivamente por:

docs
 ↓
MkDocs
 ↓
GitHub Pages

Isso melhora bastante o SoC.


---

10. Triggers

Eu utilizaria três mecanismos simultaneamente.

Trigger 1 — Push

on:
  push:
    branches:
      - main

Não usaria paths para a sincronização inteligente.

O agente decide se precisa trabalhar.


---

Trigger 2 — Schedule

Recomendação:

schedule:
  - cron: "17 */6 * * *"

Ou seja:

> a cada 6 horas



Não usaria exatamente 0 */6 * * *, porque horários de hora cheia tendem a concentrar execuções de Actions.


---

Trigger 3 — Manual

workflow_dispatch:

Com possibilidade futura de parâmetros:

mode:
  incremental
  full
  audit


---

11. Minha recomendação de frequência

Frequência	Avaliação

A cada 15 min	Desnecessário
A cada 1h	Muito agressivo
A cada 3h	Bom
A cada 6h	Recomendado
A cada 12h	Aceitável
Diário	Insuficiente para projeto ativo
Sem schedule	Não recomendado


Minha escolha

Push → imediato
Schedule → 6h
Manual → disponível

Assim:

Developer commit
       ↓
documentation-sync
       ↓
atualiza docs
       ↓
Pages

+ 

6h safety reconciliation
       ↓
detecta qualquer drift
       ↓
corrige


---

12. Evitar loop infinito

Esse é um dos pontos mais importantes.

Imagine:

push main
 ↓
documentation-sync
 ↓
modifica docs
 ↓
commit
 ↓
push main
 ↓
documentation-sync
 ↓
...

O workflow precisa detectar commits automatizados.

Por exemplo:

docs(sync): reconcile documentation [skip ci]

ou usar uma condição:

if: github.actor != 'github-actions[bot]'

Mas eu prefiro não depender exclusivamente do actor.

Criaria uma estratégia baseada em commit metadata:

documentation-sync

e também em um lock/marker.


---

13. Melhor arquitetura: incremental + full audit

Eu faria dois modos.

Incremental

Executado em:

push

Analisa somente:

changed files
+
affected documentation
+
related architecture

Muito barato.

Full Audit

Executado:

a cada 6h

Analisa:

TODO repository

e compara contra:

TODO docs

Isso cria uma segunda camada de proteção.


---

14. Fluxo ideal

flowchart TD
    A[Push main] --> B[Incremental Analysis]

    C[Every 6 hours] --> D[Full Documentation Audit]

    E[workflow_dispatch] --> F{Mode}

    F -->|incremental| B
    F -->|full| D
    F -->|audit| D

    B --> G[Repository Inventory]
    D --> G

    G --> H[Git Diff]
    H --> I[Documentation Manifest]
    I --> J[Drift Detection]

    J --> K[LLM Analysis]

    K --> L{Drift?}

    L -->|No| M[Validation]
    L -->|Yes| N[Update Documentation]

    N --> O[Update MkDocs Navigation]
    O --> M

    M --> P[mkdocs build --strict]

    P --> Q{Valid?}

    Q -->|No| R[Fail Workflow]
    Q -->|Yes| S{Changes?}

    S -->|No| T[Finish]
    S -->|Yes| U[Commit Documentation]

    U --> V[Pages Deployment]


---

15. Um ponto ainda mais importante: IA não deve decidir tudo

Eu usaria uma arquitetura híbrida.

Determinístico

Use código para detectar:

file created
file deleted
file renamed
SHA changed
broken links
missing nav
missing files
invalid YAML
invalid Markdown

IA

Use LLM para:

semantic impact
architecture interpretation
documentation reconciliation
summary
cross-reference analysis
determining affected docs
rewriting prose
updating explanations

Isso reduz drasticamente hallucination.


---

16. Exemplo de decisão

Imagine:

src/llm_service.py

mudou de:

Gemini
OpenCode
OpenRouter

para:

Gemini
OpenAI

O mecanismo determinístico identifica:

src/llm_service.py changed

O LLM analisa:

Which documentation references providers?

e encontra:

docs/api/llm_service.md
docs/architecture/overview.md
docs/internal/AGENT_DIRECTIVE.md
README.md

Atualiza somente esses artefatos.


---

17. Outro caso: exclusão

Se:

src/translator.py

for removido:

DELETE src/translator.py

o sistema procura:

docs/api/translator.md
mkdocs.yml
README.md
architecture/*

e corrige todos os impactos.

Isso é muito superior ao atual sistema baseado somente em paths.


---

18. Uma alteração que eu faria no próprio MkDocs

Atualmente existe uma API Reference explícita:

Pipeline Principal
Scraper
Parser
LLM Service
Classifier
Translator
Notifications
Cache Manager

conforme o mkdocs.yml.

Isso é um ótimo candidato para automação.

O agente pode verificar:

nav API Reference
       ↓
corresponding source module
       ↓
exists?
       ↓
documented?
       ↓
accurate?

Assim, o mkdocs.yml passa a ser validado semanticamente.


---

19. O que eu mudaria no workflow atual

Atual

documentation-build.yml
 ├── checkout
 ├── uv
 ├── python
 ├── dependencies
 ├── mkdocs build
 ├── upload
 └── deploy

Novo

documentation-sync.yml
 ├── checkout
 ├── repository inventory
 ├── git diff
 ├── documentation manifest
 ├── deterministic drift detection
 ├── LLM semantic analysis
 ├── documentation reconciliation
 ├── validation
 └── commit

documentation-build.yml
 ├── checkout
 ├── uv
 ├── python
 ├── dependencies
 ├── mkdocs build --strict
 ├── upload
 └── deploy


---

20. Segurança

Eu também manteria a separação de permissões.

O workflow de análise precisa de:

permissions:
  contents: write

somente porque ele precisa atualizar documentação.

Já o workflow de Pages pode continuar com:

permissions:
  contents: read
  pages: write
  id-token: write

como atualmente.

Idealmente:

AI analysis
    ↓
documentation branch/commit
    ↓
build
    ↓
deploy

E nunca permitir que a IA tenha autorização para modificar:

src/**
tests/**
secrets


---

21. Minha recomendação final

Sim, faria a modificação.

Mas não faria apenas uma alteração no cron do workflow atual.

Eu transformaria o sistema em uma verdadeira:

> Continuous Documentation Reconciliation Pipeline



com quatro características:

1. Git como source of truth


2. detecção determinística de drift


3. IA para análise semântica


4. auditoria completa periódica

A arquitetura que considero mais adequada para o seu repositório é:
                 ┌───────────────────┐
                 │ Git Repository    │
                 │ Source of Truth   │
                 └─────────┬─────────┘
                           │
             ┌─────────────┴─────────────┐
             │                           │
          Push                         6 hours
             │                           │
             ▼                           ▼
      Incremental Audit            Full Audit
             │                           │
             └─────────────┬─────────────┘
                           ▼
                 Repository Inventory
                           │
                           ▼
                  Deterministic Diff
                           │
                           ▼
                 Documentation Drift
                           │
                           ▼
                    LLM Analysis
                           │
                Gemini → OpenCode
                     → OpenRouter
                           │
                           ▼
                 Documentation Update
                           │
                           ▼
                 mkdocs --strict
                           │
                           ▼
                    Git Commit
                           │
                           ▼
                    GitHub Pages
Agendamento recomendado
Push imediato + auditoria completa a cada 6 horas + execução manual.
Isso oferece um equilíbrio muito bom entre atualidade, custo de IA, tempo de execução e proteção contra documentação obsoleta.
Há ainda uma inconsistência que vale corrigir durante a refatoração: o pyproject.toml exige Python >=3.13,<3.14, enquanto o README atualmente exibe um badge de Python 3.12+; isso é exatamente o tipo de drift que o novo mecanismo deverá detectar automaticamente.
Próxima etapa recomendada: criar uma Issue/ADR de arquitetura e, depois, implementar documentation-sync.yml + documentation-manifest + motor de drift, mantendo documentation-build.yml focado exclusivamente em build/deploy.

