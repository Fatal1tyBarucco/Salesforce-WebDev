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

RELEASE_SECTION_HEADING = "## 📋 Releases Disponíveis"

# Salesforce release naming/numbering scheme assumptions.
# Update these constants if Salesforce changes release cadence or ID progression.
RELEASE_SEASONS = ("Spring", "Summer", "Winter")
RELEASE_BASE_ID = 254  # release_id for Spring '25 — first release in this numbering scheme
RELEASE_BASE_YEAR = 25  # two-digit year for Spring '25
RELEASE_ID_STEP = 2  # release_id increments by 2 per release

TRANSLITERATE_MAP: dict[str, str] = {
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

logger = logging.getLogger(__name__)


def _find_existing_releases() -> set[str]:
    """Return slugs for release dirs that already exist in releases/."""
    releases_dir = Path(RELEASES_DIR)
    if not releases_dir.exists():
        return set()
    return {d.name for d in releases_dir.iterdir() if d.is_dir() and any(d.glob("*.md"))}


async def detect_new_release(scraper: SalesforceReleaseScraper) -> ReleaseInfo | None:
    """Detect whether there is a new release candidate to process.

    Returns:
        - ReleaseInfo for the latest known release when the repo has no release artifacts yet.
        - ReleaseInfo for the next release when its page content differs from the current release.
        - None when no new release should be processed, including when:
          * all known releases already exist in the repo,
          * the next release slug already exists,
          * page fetch/comparison fails,
          * compared content indicates the next release is not yet available.
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

    current_text, next_text = await asyncio.gather(
        scraper.fetch_page_raw_text(current_url),
        scraper.fetch_page_raw_text(next_url),
    )

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
    # Salesforce release IDs start at RELEASE_BASE_ID and increment by RELEASE_ID_STEP.
    # There are currently len(RELEASE_SEASONS) releases per year.
    step = (release_id - RELEASE_BASE_ID) // RELEASE_ID_STEP
    season = RELEASE_SEASONS[step % len(RELEASE_SEASONS)]
    year = RELEASE_BASE_YEAR + step // len(RELEASE_SEASONS)
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
                _update_readme_all()
                return

        for release in releases_to_process:
            logger.info("Processing release: %s (id=%d)", release.name, release.release_id)

            release_dir = Path(RELEASES_DIR) / release.slug
            release_dir.mkdir(parents=True, exist_ok=True)

            impact_url = FEATURE_IMPACT_URL.format(release_id=release.release_id)
            logger.info("Fetching feature impact: %s", impact_url)

            pdf_dest = release_dir / f"release-in-a-box-{release.slug}.pdf"
            pdf_task = asyncio.create_task(scraper.download_pdf_from_button(impact_url, pdf_dest))

            raw_text = await scraper.fetch_page_raw_text(impact_url)

            await pdf_task
            if not raw_text:
                logger.warning("No content for %s feature impact", release.name)
                continue

            categories = impact_parser.parse_text(raw_text)
            logger.info("Parsed %d categories from feature impact", len(categories))

            _generate_release_files(release, categories, generator)
            _update_readme_single(release, categories)

    _update_readme_all()

    # Generate AI reports
    try:
        from .ai_automation import generate_changelog, generate_quality_report

        changelog = generate_changelog()
        Path("CHANGELOG.md").write_text(changelog, encoding="utf-8")

        quality = generate_quality_report()
        Path("QUALITY_REPORT.md").write_text(quality, encoding="utf-8")

        logger.info("AI reports generated: CHANGELOG.md, QUALITY_REPORT.md")
    except Exception as e:
        logger.warning("Failed to generate AI reports: %s", e)


def _slugify_category(name: str) -> str:
    """Transliterate Portuguese characters and slugify a category name."""
    lowered = name.lower()
    for char, replacement in TRANSLITERATE_MAP.items():
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
    """Replace the release section in README.md with details/summary blocks."""
    readme_path = Path("README.md")
    releases_dir = Path(RELEASES_DIR)
    if not releases_dir.exists():
        return

    import json

    if not readme_path.exists():
        logger.warning("README.md not found, skipping update")
        return

    original = readme_path.read_text(encoding="utf-8")

    if RELEASE_SECTION_HEADING not in original:
        logger.warning(
            "Release heading '%s' not found in README.md, skipping update", RELEASE_SECTION_HEADING
        )
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

    lines: list[str] = [f"\n{RELEASE_SECTION_HEADING}\n"]

    for meta in metas:
        slug = meta["slug"]
        name = meta["name"]
        emoji = get_release_emoji(name)

        categories = meta.get("categories", [])
        active = [c for c in categories if c.get("count", 0) > 0]

        lines.append(f"\n### {emoji} {name}\n")

        for cat in active:
            cat_name = cat["name"]
            count = cat["count"]
            cat_slug = _slugify_category(cat_name)
            link = f"./releases/{slug}/{cat_slug}.md"

            lines.append("\n<details>")
            lines.append(f"<summary><b>📄 {cat_name} ({count} recursos)</b></summary>\n")
            lines.append(f"> 📄 Detalhes completos: [{link}]({link})\n")
            lines.append("</details>\n")

        lines.append("")

    new_block = "\n".join(lines)

    heading_idx = original.index(RELEASE_SECTION_HEADING)
    next_heading = original.find("\n## ", heading_idx + len(RELEASE_SECTION_HEADING))
    if next_heading == -1:
        next_heading = len(original)

    updated = original[:heading_idx] + new_block + original[next_heading:]

    readme_path.write_text(updated, encoding="utf-8")
    logger.info("README.md atualizado com details/summary (%d releases).", len(metas))


def main() -> None:
    """Entrypoint do script."""
    asyncio.run(run_pipeline())


if __name__ == "__main__":
    main()
