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
    README_INDEX_END_MARKER,
    README_INDEX_START_MARKER,
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


async def detect_new_releases(scraper: SalesforceReleaseScraper) -> list[ReleaseInfo]:
    """Probe Salesforce for the next release ID beyond what we know.

    Only checks the immediate next release (base_id + 2).
    The feature impact page returns content for any ID, so we limit
    to a single probe to avoid detecting non-existent future releases.
    """
    existing_slugs = _find_existing_releases()
    base_id = _highest_known_id()
    candidate_id = base_id + 2
    info = build_release_info(candidate_id)

    if info.slug in existing_slugs:
        return []

    url = FEATURE_IMPACT_URL.format(release_id=candidate_id)
    logger.info("Probing for new release: %s (id=%d)", info.name, candidate_id)

    text = await scraper.fetch_page_raw_text(url)
    if text and len(text) > 500:
        logger.info("New release found: %s", info.name)
        return [info]

    logger.info("Release %s not found (id=%d)", info.name, candidate_id)
    return []


async def run_pipeline() -> None:
    """Orquestrador: detect releases, fetch feature impact + PDF, generate markdown."""
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
            existing_slugs = _find_existing_releases()

            new_releases = await detect_new_releases(scraper)
            for r in new_releases:
                if r.slug not in [x.slug for x in KNOWN_RELEASES]:
                    KNOWN_RELEASES.append(r)
                    logger.info("Added new release to KNOWN_RELEASES: %s", r.name)

            for r in sorted(KNOWN_RELEASES, key=lambda x: x.release_id, reverse=True):
                if r.slug not in existing_slugs:
                    releases_to_process.append(r)
                    break

            if not releases_to_process:
                logger.info("No new releases detected. Updating README only.")
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
    """Replace the index block in README.md with per-release tables."""
    readme_path = Path("README.md")
    releases_dir = Path(RELEASES_DIR)
    if not releases_dir.exists():
        return

    import json

    if not readme_path.exists():
        return

    original = readme_path.read_text(encoding="utf-8")

    if README_INDEX_START_MARKER not in original:
        logger.warning("README markers not found, skipping update")
        return

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
