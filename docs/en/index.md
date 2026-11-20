# Salesforce Release Intelligence — English

English surface of the Salesforce Release Intelligence documentation site.
The repository is the single source of truth; this page is part of the
verifiable documentation contract (ADR-012).

## Overview

Salesforce-WebDev is an ETL pipeline that extracts, classifies, and versions
Salesforce Release Notes as structured Markdown artifacts (Knowledge-as-Code),
with AI-powered analysis and cross-release feature tracking (SFEL).

- Repository: [Fatal1tyBarucco/Salesforce-WebDev](https://github.com/Fatal1tyBarucco/Salesforce-WebDev)
- English README: [README.en.md](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/blob/main/README.en.md)
- Portuguese documentation: [Home](../index.md)

## Release notes in English

Bilingual release artifacts are versioned under `releases/` in the repository
(`pt_BR` and `en_US` surfaces, kept at parity by the contract validator):

| Release | English artifacts |
| :--- | :--- |
| Winter '27 | [releases/winter_27/en_US](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/tree/main/releases/winter_27/en_US) |
| Summer '26 | [releases/summer_26/en_US](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/tree/main/releases/summer_26/en_US) |
| Spring '26 | [releases/spring_26/en_US](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/tree/main/releases/spring_26/en_US) |
| Winter '26 | [releases/winter_26/en_US](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/tree/main/releases/winter_26/en_US) |

## Language coverage

The full technical documentation is authored in pt-BR. English prose is
expanded by the AI documentation pipeline (`ai-docs.yml`), whose output must
pass the same contract gates (manifest fidelity, markdown lint, link checker,
`mkdocs build --strict`) before publication. Parity between the pt-BR and
English surfaces is verified deterministically by
`.github/scripts/docs_contract.py parity`.
