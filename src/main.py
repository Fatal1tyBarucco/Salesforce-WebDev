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

from bs4 import BeautifulSoup

from .config import (
    BASE_URL,
    FEATURE_IMPACT_URL,
    KNOWN_RELEASES,
    RELEASES_DIR,
    ReleaseInfo,
    build_release_info,
)
from .generator import MarkdownGenerator
from .logger import setup_logging
from .parser import (
    FeatureImpactCategory,
    FeatureImpactEntry,
    FeatureImpactParser,
    ReleaseNotesParser,
)
from .scraper import SalesforceReleaseScraper

logger = logging.getLogger(__name__)


def _find_existing_releases() -> set[str]:
    """Return slugs for release dirs that already exist in releases/."""
    releases_dir = Path(RELEASES_DIR)
    if not releases_dir.exists():
        return set()
    return {d.name for d in releases_dir.iterdir() if d.is_dir() and any(d.glob("*.md"))}


def _highest_known_id() -> int:
    return max(r.release_id for r in KNOWN_RELEASES)


async def detect_new_releases(
    scraper: SalesforceReleaseScraper, parser: ReleaseNotesParser
) -> list[ReleaseInfo]:
    """Probe Salesforce for release IDs beyond what we know. Return new ones."""
    existing_slugs = _find_existing_releases()
    base_id = _highest_known_id()
    new_releases: list[ReleaseInfo] = []

    for offset in range(2, 20, 2):
        candidate_id = base_id + offset
        info = build_release_info(candidate_id)
        if info.slug in existing_slugs:
            logger.info("Release %s already exists locally, skipping probe", info.slug)
            continue

        url = BASE_URL.format(release_id=candidate_id)
        logger.info("Probing for new release: %s (id=%d)", info.name, candidate_id)

        html = await scraper.fetch_page(url, expand_toc=False)
        if not html or len(html) < 2000:
            logger.info("Release %s not found (id=%d)", info.name, candidate_id)
            break

        soup = BeautifulSoup(html, "lxml")
        topics = parser.extract_topic_tree(soup)
        if topics:
            logger.info("New release found: %s (%d topics)", info.name, len(topics))
            new_releases.append(info)
        else:
            logger.info("Release %s exists but no topics extracted", info.name)
            break

    return new_releases


async def run_pipeline() -> None:
    """Orquestrador: feature impact page + PDF download (1 fetch vs 1226)."""
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

    if release_filter:
        for r in KNOWN_RELEASES:
            if r.slug == release_filter:
                releases_to_process.append(r)
                break
        if not releases_to_process:
            logger.error("Release '%s' not found in KNOWN_RELEASES", release_filter)
            return
    else:
        existing_slugs = _find_existing_releases()
        for r in sorted(KNOWN_RELEASES, key=lambda x: x.release_id, reverse=True):
            if r.slug not in existing_slugs:
                releases_to_process.append(r)
                break
        if not releases_to_process:
            logger.info("No new releases detected. Updating README only.")

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


def _update_readme_all() -> None:
    """Regenerate README.md from all release metadata in releases/."""
    readme_path = Path("README.md")
    releases_dir = Path(RELEASES_DIR)
    if not releases_dir.exists():
        return

    import json

    metas: list[dict[str, Any]] = []
    for d in releases_dir.iterdir():
        meta_path = d / ".meta.json"
        if meta_path.exists():
            metas.append(json.loads(meta_path.read_text(encoding="utf-8")))

    metas.sort(key=lambda m: m.get("release_id", 0), reverse=True)

    content: list[str] = [
        "![Salesforce Release Intelligence](./assets/banner.png)\n\n",
        "# 🚀 Salesforce Release Notes Intelligence\n\n",
        "Pipeline automatizado para extração, classificação e versionamento das "
        "**Salesforce Release Notes** como artefatos Markdown estruturados "
        "(*Knowledge-as-Code*).\n\n",
        "### ⚙️ CI/CD Status & Conformidade\n\n",
        "[![Python Quality & Validation]"
        "(https://github.com/Fatal1tyBarucco/Salesforce-WebDev/actions/workflows/"
        "python-quality.yml/badge.svg)]"
        "(https://github.com/Fatal1tyBarucco/Salesforce-WebDev/actions/workflows/"
        "python-quality.yml)\n",
        "![Python](https://img.shields.io/badge/Python-3.14-blue.svg?"
        "logo=python&logoColor=white) \n",
        "![Playwright](https://img.shields.io/badge/Playwright-Headless_SPA-green.svg?"
        "logo=playwright&logoColor=white) \n",
        "![Mypy](https://img.shields.io/badge/Mypy-Strict_Mode-blue.svg) \n",
        "![Ruff](https://img.shields.io/badge/Ruff-Linter-black.svg) \n",
        "![Black](https://img.shields.io/badge/Formatter-Black-000000.svg)\n\n",
        "| Tecnologia / Ferramenta | Descrição | Status no Pipeline |\n",
        "| :--- | :--- | :---: |\n",
        "| 🐍 **Python 3.14** | Ambiente de execução principal | `Conforme` |\n",
        "| 🎭 **Playwright** | Scraper Headless para aplicações SPA do Salesforce Help | `Ativo` |\n",
        "| 🧪 **Pytest** | Suíte de testes unitários automatizados | `100% Cobertura` |\n",
        "| 🔍 **Mypy** | Verificação estática de tipos com modo estrito | `Strict` |\n",
        "| ⚡ **Ruff & Black** | Linter e formatação estrita de código (line-length = 100) | `Conforme` |\n\n",
        "---\n\n",
        "## 📋 Notas de Release e Resumos por Tópico\n\n",
    ]

    def get_release_emoji(name: str) -> str:
        name_lower = name.lower()
        if "winter" in name_lower:
            return "❄️"
        elif "summer" in name_lower:
            return "☀️"
        return "🌸"

    for meta in metas:
        slug = meta["slug"]
        name = meta["name"]
        emoji = get_release_emoji(name)

        content.append(f"### {emoji} {name}\n\n")

        categories = meta.get("categories", [])
        for cat in categories:
            cat_name = cat["name"]
            count = cat["count"]
            cat_slug = _slugify_category(cat_name)

            if count > 0:
                plural = "recursos" if count > 1 else "recurso"
                content.append("<details>\n")
                content.append(
                    f"<summary><b>📄 {cat_name} " f"({count} {plural})</b></summary>\n\n"
                )
                content.append(
                    f"> 📄 Detalhes completos: "
                    f"[./releases/{slug}/{cat_slug}.md]"
                    f"(./releases/{slug}/{cat_slug}.md)\n\n"
                )
                content.append("</details>\n\n")
            else:
                content.append(f"* 📄 **{cat_name}** — Sem recursos nesta release.\n")

        content.append("\n---\n\n")

    readme_path.write_text("".join(content), encoding="utf-8")
    logger.info("README.md atualizado com painel moderno (%d releases).", len(metas))


def main() -> None:
    """Entrypoint do script."""
    asyncio.run(run_pipeline())


if __name__ == "__main__":
    main()
