"""Main orchestrator for Salesforce release notes extraction (web scraping).

Strategy:
  1. Detect new releases by probing Salesforce for unseen release IDs
  2. Scrape only new releases (not already in releases/ dir)
  3. Deep-scrape each article for summaries (pt-BR)
  4. Generate Markdown artifacts per topic
  5. Update README organized chronologically (newest on top)
"""

from __future__ import annotations

import asyncio
import logging
import re
import sys
from pathlib import Path
from typing import Any

from .config import (
    FEATURE_IMPACT_URL,
    KNOWN_RELEASES,
    RELEASES_DIR,
    ReleaseInfo,
)
from .generator import MarkdownGenerator
from .logger import setup_logging
from .parser import (
    FeatureImpactCategory,
    FeatureImpactEntry,
    FeatureImpactParser,
)
from .scraper import SalesforceReleaseScraper

README_INDEX_START_MARKER = "{% comment %} RELEASE_INDEX_START {% endcomment %}"
README_INDEX_END_MARKER = "{% comment %} RELEASE_INDEX_END {% endcomment %}"

logger = logging.getLogger(__name__)


def _find_existing_releases() -> set[str]:
    """Return slugs for release dirs that already exist in releases/."""
    releases_dir = Path(RELEASES_DIR)
    if not releases_dir.exists():
        return set()
    return {d.name for d in releases_dir.iterdir() if d.is_dir() and any(d.glob("*.md"))}


async def detect_new_release(scraper: SalesforceReleaseScraper) -> ReleaseInfo | None:
    """Detect if a new release is available by comparing page content.

    If no releases exist in the repo, returns the latest known release.
    If releases exist, compares current vs next to detect new ones.
    """
    existing_slugs = _find_existing_releases()
    known_sorted = sorted(KNOWN_RELEASES, key=lambda x: x.release_id, reverse=True)

    current = None
    for r in known_sorted:
        if r.slug in existing_slugs:
            current = r
            break

    if current is None:
        latest = known_sorted[0]
        if latest.slug not in existing_slugs:
            logger.info("No releases in repo, processing latest known: %s", latest.name)
            return latest
        return None

    next_id = current.release_id + 2
    next_info = ReleaseInfo(
        name=_build_release_name(next_id),
        release_id=next_id,
        slug=_build_release_slug(next_id),
    )

    if next_info.slug in existing_slugs:
        return None

    current_url = FEATURE_IMPACT_URL.format(release_id=current.release_id)
    next_url = FEATURE_IMPACT_URL.format(release_id=next_id)

    logger.info(
        "Comparing content: %s (id=%d) vs %s (id=%d)",
        current.name,
        current.release_id,
        next_info.name,
        next_id,
    )

    current_text = await scraper.fetch_page_raw_text(current_url)
    next_text = await scraper.fetch_page_raw_text(next_url)

    if not current_text or not next_text:
        logger.info("Could not fetch pages for comparison")
        return None

    if len(current_text) == len(next_text) and current_text[:500] == next_text[:500]:
        logger.info(
            "Release %s not yet available (content identical to %s)", next_info.name, current.name
        )
        return None

    logger.info("New release detected: %s (content differs from %s)", next_info.name, current.name)
    return next_info


def _build_release_name(release_id: int) -> str:
    SEASONS = ("Spring", "Summer", "Winter")
    BASE_ID = 254
    BASE_YEAR = 25
    step = (release_id - BASE_ID) // 2
    season = SEASONS[step % 3]
    year = BASE_YEAR + step // 3
    if season == "Winter":
        year += 1
    return f"{season} '{year}"


def _build_release_slug(release_id: int) -> str:
    name = _build_release_name(release_id)
    season, year = name.split()
    clean_year = year.replace("'", "")
    return f"{season.lower()}_{clean_year}"


async def run_pipeline() -> None:
    """Orquestrador: fetch feature impact + PDF, generate markdown for latest unseen release."""
    setup_logging()
    logger.info("Starting Salesforce Release Notes extraction (feature impact).")

    scraper = SalesforceReleaseScraper()
    impact_parser = FeatureImpactParser()
    generator = MarkdownGenerator(base_dir=RELEASES_DIR)

    args = sys.argv[1:]
    release_filter: str | None = None

    for i, arg in enumerate(args):
        if arg == "--release" and i + 1 < len(args):
            release_filter = args[i + 1]

    releases_to_process: list[ReleaseInfo] = []

    async with scraper:
        if release_filter:
            for r in KNOWN_RELEASES:
                if r.slug == release_filter:
                    releases_to_process.append(r)
                    break
            if not releases_to_process:
                logger.error("Release '%s' not found in KNOWN_RELEASES", release_filter)
                return
        else:
            new_release = await detect_new_release(scraper)
            if new_release:
                releases_to_process.append(new_release)
            else:
                logger.info("No new release detected. Updating README only.")

    async with scraper:
        for release in releases_to_process:
            logger.info("Processing release: %s (id=%d)", release.name, release.release_id)

            release_dir = Path(RELEASES_DIR) / release.slug
            release_dir.mkdir(parents=True, exist_ok=True)

            impact_url = FEATURE_IMPACT_URL.format(release_id=release.release_id)
            logger.info("Fetching feature impact: %s", impact_url)

            pdf_dest = release_dir / f"release-in-a-box-{release.slug}.pdf"
            await scraper.download_pdf_from_button(impact_url, pdf_dest)

            raw_text = await scraper.fetch_page_raw_text(impact_url)
            if not raw_text:
                logger.warning("No content for %s feature impact", release.name)
                continue

            categories = impact_parser.parse_text(raw_text)
            logger.info("Parsed %d categories from feature impact", len(categories))

            _generate_release_files(release, categories, generator)
            _update_readme_single(release, categories)

    _update_readme_all()


def _slugify_category(name: str) -> str:
    """Transliterate Portuguese characters and slugify a category name."""
    transliterate_map: dict[str, str] = {
        "ç": "c",
        "ã": "a",
        "õ": "o",
        "á": "a",
        "é": "e",
        "í": "i",
        "ó": "o",
        "ú": "u",
        "ê": "e",
        "ô": "o",
        "à": "a",
    }
    lowered = name.lower()
    for char, replacement in transliterate_map.items():
        lowered = lowered.replace(char, replacement)
    return re.sub(r"[^a-z0-9]+", "_", lowered).strip("_")


def _generate_release_files(
    release: ReleaseInfo,
    categories: list[FeatureImpactCategory],
    generator: MarkdownGenerator,
) -> list[Path]:
    """Generate per-category .md files for a release."""

    release_dir = Path(RELEASES_DIR) / release.slug
    release_dir.mkdir(parents=True, exist_ok=True)
    generated: list[Path] = []

    for cat in categories:
        slug = _slugify_category(cat.name)
        file_path = release_dir / f"{slug}.md"

        lines: list[str] = []
        lines.append(f"## {cat.name}\n")
        if cat.description:
            lines.append(f"{cat.description}\n")

        for entry in cat.entries:
            lines.append(_format_entry(entry))

        for sub_name, sub_entries in cat.subcategories.items():
            if sub_entries:
                lines.append(f"### {sub_name}\n")
                for entry in sub_entries:
                    lines.append(_format_entry(entry))

        body = "\n".join(lines) if lines else "_Sem recursos nesta categoria._\n"
        file_path.write_text(body, encoding="utf-8")
        generated.append(file_path)
        logger.info("Generated: %s (%d features)", file_path, len(cat.entries))

    return generated


def _format_entry(entry: FeatureImpactEntry) -> str:
    flags: list[str] = []
    if entry.available_users:
        flags.append("Disponível para usuários")
    if entry.available_admins:
        flags.append("Disponível para admins/devs")
    if entry.requires_config:
        flags.append("Requer configuração")
    if entry.contact_sf:
        flags.append("Contatar Salesforce")

    flag_text = f" — _{' · '.join(flags)}_" if flags else ""
    return f"* **{entry.name}**{flag_text}\n"


def _update_readme_single(
    release: ReleaseInfo,
    categories: list[FeatureImpactCategory],
) -> None:
    """Write per-category .md and cache metadata for later README generation."""

    meta_path = Path(RELEASES_DIR) / release.slug / ".meta.json"

    import json

    if meta_path.exists():
        existing = json.loads(meta_path.read_text(encoding="utf-8"))
        if existing.get("categories"):
            logger.debug("Skipping .meta.json write for %s (already has data)", release.slug)
            return

    cat_list: list[dict[str, object]] = []
    meta: dict[str, object] = {
        "name": release.name,
        "slug": release.slug,
        "release_id": release.release_id,
        "categories": cat_list,
    }
    for cat in categories:
        total = len(cat.entries) + sum(len(e) for e in cat.subcategories.values())
        cat_list.append({"name": cat.name, "count": total})

    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")


def _create_readme_with_markers(readme_path: Path) -> None:
    """Create README.md with proper formatting and release index markers."""
    content = (
        """![Salesforce Release Intelligence](./assets/banner.png)

# 🚀 Salesforce Release Notes Intelligence

Pipeline automatizado para extração, classificação e versionamento das **Salesforce Release Notes** como artefatos Markdown estruturados (*Knowledge-as-Code*).

### ⚙️ CI/CD Status & Conformidade

[![Python Quality & Validation](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/actions/workflows/python-quality.yml/badge.svg)](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/actions/workflows/python-quality.yml)
![Python](https://img.shields.io/badge/Python-3.14-blue.svg?logo=python&logoColor=white) 
![Playwright](https://img.shields.io/badge/Playwright-Headless_SPA-green.svg?logo=playwright&logoColor=white) 
![Mypy](https://img.shields.io/badge/Mypy-Strict_Mode-blue.svg) 
![Ruff](https://img.shields.io/badge/Ruff-Linter-black.svg) 
![Black](https://img.shields.io/badge/Formatter-Black-000000.svg)

| Tecnologia / Ferramenta | Descrição | Status no Pipeline |
| :--- | :--- | :---: |
| 🐍 **Python 3.14** | Ambiente de execução principal | `Conforme` |
| 🎭 **Playwright** | Scraper Headless para aplicações SPA do Salesforce Help | `Ativo` |
| 🧪 **Pytest** | Suíte de testes unitários automatizados | `100% Cobertura` |
| 🔍 **Mypy** | Verificação estática de tipos com modo estrito | `Strict` |
| ⚡ **Ruff & Black** | Linter e formatação estrita de código (line-length = 100) | `Conforme` |

---

## 📌 Visão Geral

Este repositório atua como uma **Base de Conhecimento Dinâmica (Knowledge Base)** que captura, estrutura e documenta as funcionalidades, atualizações de segurança e alterações arquiteturais (como Apex, LWC, Flow e Integrações) introduzidas nas releases periódicas da Salesforce.

A estrutura é desenhada para suportar revisões rápidas por Arquitetos e Desenvolvedores, mantendo um log histórico em formato legível (Markdown) nativo do repositório.

## ⚙️ Arquitetura de Atualização Dinâmica

A governança do repositório é mantida por meio de processos automatizados que garantem que as últimas releases sejam extraídas, transformadas e carregadas (ETL) no repositório sem intervenção manual, assegurando a integridade da documentação.

```mermaid
graph TD
    A[Salesforce Release Notes] -->|Web Scraping / API| B(GitHub Actions Workflow)
    B -->|Markdown Generator| C{Processamento de Dados}
    C -->|Parse Categorias| D[Diretórios /releases/]
    C -->|Update Dinâmico| E[README.md Index]
    D --> F((Commit Automático))
    E --> F
    F --> G[Repositório Atualizado]
    
    classDef salesforce fill:#00A1E0,stroke:#fff,stroke-width:2px,color:#fff;
    class A salesforce;

```

---

## 📋 Releases Disponíveis

"""
        + f"{README_INDEX_START_MARKER}\n{README_INDEX_END_MARKER}"
        + """

---

## 🛠️ Stack Tecnológico & Automação

O controle de versão e extração de dados utiliza as seguintes ferramentas:

* **GitHub Actions:** Orquestração de rotinas diárias/semanais (Cron Jobs) para verificar novas atualizações.
* **Markdown:** Estruturação "Enterprise-grade" visando leitura técnica otimizada.
* **Python (Playwright):** Extração defensiva de dados do ecossistema oficial Salesforce com renderização SPA headless.

## 🤝 Como Contribuir

1. Faça o **Fork** do projeto
2. Crie uma nova branch com a sua feature: `git checkout -b feature/minha-feature`
3. Faça o commit de forma detalhada e técnica: `git commit -m 'feat: Implementação de parser para novos limites de governor limits no Apex'`
4. Envie a branch: `git push origin feature/minha-feature`
5. Abra um **Pull Request** detalhando a arquitetura ou correção proposta.

---
"""
    )
    readme_path.write_text(content, encoding="utf-8")
    logger.info("README.md criado com marcadores.")


def _update_readme_all() -> None:
    """Replace the index block in README.md with per-release tables."""
    readme_path = Path("README.md")
    releases_dir = Path(RELEASES_DIR)
    if not releases_dir.exists():
        return

    import json

    if not readme_path.exists():
        _create_readme_with_markers(readme_path)

    original = readme_path.read_text(encoding="utf-8")

    if README_INDEX_START_MARKER not in original:
        _create_readme_with_markers(readme_path)
        original = readme_path.read_text(encoding="utf-8")

    metas: list[dict[str, Any]] = []
    for d in releases_dir.iterdir():
        meta_path = d / ".meta.json"
        if meta_path.exists():
            metas.append(json.loads(meta_path.read_text(encoding="utf-8")))

    metas.sort(key=lambda m: m.get("release_id", 0), reverse=True)

    def get_release_emoji(name: str) -> str:
        name_lower = name.lower()
        if "winter" in name_lower:
            return "❄️"
        elif "summer" in name_lower:
            return "☀️"
        return "🌸"

    lines: list[str] = ["\n"]

    for meta in metas:
        slug = meta["slug"]
        name = meta["name"]
        emoji = get_release_emoji(name)

        categories = meta.get("categories", [])
        active = [c for c in categories if c.get("count", 0) > 0]

        lines.append(f"### {emoji} {name}\n\n")
        lines.append("| Módulo / Cloud | Recursos | Link para Documentação |")
        lines.append("| --- | ---: | --- |")

        for cat in active:
            cat_name = cat["name"]
            count = cat["count"]
            cat_slug = _slugify_category(cat_name)
            link = f"./releases/{slug}/{cat_slug}.md"
            lines.append(f"| **{cat_name}** | {count} " f"| [📄 Visualizar]({link}) |")

        lines.append("")

    new_block = "\n".join(lines)

    start_idx = original.index(README_INDEX_START_MARKER) + len(README_INDEX_START_MARKER)
    end_idx = original.index(README_INDEX_END_MARKER)

    updated = original[:start_idx] + new_block + original[end_idx:]

    readme_path.write_text(updated, encoding="utf-8")
    logger.info("README.md atualizado com tabelas (%d releases).", len(metas))


def main() -> None:
    """Entrypoint do script."""
    asyncio.run(run_pipeline())


if __name__ == "__main__":
    main()
