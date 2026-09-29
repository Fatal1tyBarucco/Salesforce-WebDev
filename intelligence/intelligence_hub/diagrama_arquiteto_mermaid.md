```mermaid
graph TD
    subgraph Fontes_Oficiais_Salesforce[Fontes Oficiais Salesforce]
        A[Salesforce Status<br>https://status.salesforce.com/]
        B[Change Log<br>release-notes.rn_change_log.htm<br>release=264]
        C[Release Notes Home<br>release-notes.salesforce_release_notes.htm<br>release=264]
    end

    subgraph Pipeline_Extracao_Defensiva[Pipeline de Extração Defensiva — Python]
        D[Scraper: SalesforceStatusScraperEngineDefensive]
        E[Parser: ChangeLogDefensiveParserEngine]
        F[Parser: ReleaseNotesHomeDefensiveParserEngine]
    end

    subgraph Validacao_e_Construcao[Validação + Construção — SoC]
        G[Builder: SalesforceReleaseManualBuilderDefensive]
        H[Builder: SalesforceOrgPreparationGuideDefensiveBuilder]
    end

    subgraph Artefatos_Gerados[Artefatos Gerados — Pages/GitHub]
        I[release_pdfs/Release_264_Manual.pdf]
        J[deploy_manuals/Release_264_Deploy_Guide.md]
        K[sandbox_preview_schedules/Release_264_Sandbox.md]
        L[org_preparation_guides/Release_264_Org_Prep.md]
        M[release_readiness/Release_264_Readiness.md]
    end

    subgraph Publicacao_Pages[Publicação — GitHub Pages]
        N[assets/pages/index.html]<br>--- links ---
    end

    subgraph Automacao_README[Automação de README — Injeção Isolada]
        O[Injector: ReadmeDefensiveLinkInjectorEngine]
        P[README.md — PT-BR]
        Q[README-us.md — EN-US]
    end

    A -->|HTTP defensivo| D
    B -->|Parse defensivo| E
    C -->|Parse defensivo| F

    D -->|release_identifier| G
    E -->|nodes HTML validados| G
    F -->|language + release| G

    G --> I
    G --> J
    G --> K
    G --> L
    H --> M

    I -->|push Pages| N
    J -->|push Pages| N
    K -->|push Pages| N
    L -->|push Pages| N
    M -->|push Pages| N

    N -->|links validados| O
    O --> P
    O --> Q
```
