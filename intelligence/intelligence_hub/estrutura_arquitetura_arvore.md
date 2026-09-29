intelligence/intelligence_hub/
├── diagrama_arquiteto_mermaid.md
├── assets/
│   └── pages/
│       └── index.html                 # Índice publicado no GitHub Pages
├── release_pdfs/
│   └── Release_264_Manual.pdf         # PDF oficial da release (extraído/compilado)
├── deploy_manuals/
│   └── Release_264_Deploy_Guide.md    # Manual de implantação/deploy
├── sandbox_preview_schedules/
│   └── Release_264_Sandbox.md         # Cronograma de Sandbox Preview
├── release_readiness/
│   └── Release_264_Readiness.md       # Ações de Release Readiness
├── org_preparation_guides/
│   └── Release_264_Org_Prep.md        # Guia de preparação de Orgs (mitigação)
├── templates/
│   ├── deploy_manual_template.md
│   ├── sandbox_schedule_template.md
│   ├── readiness_template.md
│   └── org_prep_template.md
└── scripts/
    ├── scrapers/
    │   └── salesforce_defensive_scraper_engine.py      # Extração defensiva (Status, Change Log, Home)
    ├── builders/
    │   └── salesforce_release_defensive_builder.py     # Construção defensiva (PDF, manuais, cronogramas)
    └── readme_injectors/
        └── readme_defensive_injector_engine.py         # Injeção isolada em README.md / README-us.md
