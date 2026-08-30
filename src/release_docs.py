"""Release documentation generation and formatting helpers.

This module owns the pure formatting and Markdown/README rendering
responsibilities that used to live inside ``src.main``. Splitting them out
keeps the pipeline orchestration in ``src.main`` separate from document
rendering.
"""

from __future__ import annotations

import logging
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

from .config import (
    BILINGUAL_TEMPLATES,
    ENGLISH_CATEGORY_NAMES,
    ENGLISH_CATEGORY_SLUGS,
    RELEASES_DIR,
    ReleaseInfo,
)
from .feature_enricher import CategoryEnrichment
from .generator import MarkdownGenerator
from .i18n import generate_toggle_html
from .parser import FeatureImpactCategory, FeatureImpactEntry
from .translator import TranslatorService

if TYPE_CHECKING:
    from .impact_analyzer import ImpactReport
    from .smart_notifications import NotificationDigest

logger = logging.getLogger(__name__)

RELEASE_SECTION_HEADING = "## 📋 Releases Disponíveis"

# Known heading variants used in README remodels. The pipeline auto-detects
# whichever heading is present, so future renames won't break the automation.
_RELEASE_HEADING_VARIANTS: tuple[str, ...] = (
    "## 📋 Releases Disponíveis",
    "## 📦 Releases Catalogadas",
    "## 📦 Available Releases",
    "## 📋 Available Releases",
)

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


def _find_existing_releases() -> set[str]:
    """Return slugs for release dirs that already exist in releases/."""
    releases_dir = Path(RELEASES_DIR)
    if not releases_dir.exists():
        return set()
    return {d.name for d in releases_dir.iterdir() if d.is_dir() and (d / ".meta.json").exists()}


def _build_release_name(release_id: int) -> str:
    # Salesforce release IDs start at RELEASE_BASE_ID and increment by RELEASE_ID_STEP.
    # There are currently len(RELEASE_SEASONS) releases per year.
    # This is robust to gaps in the numbering: we derive the step from the
    # difference between the requested release_id and the base, so even if
    # Salesforce changes numbering the season/year mapping stays consistent.
    if release_id < RELEASE_BASE_ID:
        # Fallback for unexpected IDs: use base season/year.
        step = 0
    else:
        step = (release_id - RELEASE_BASE_ID) // RELEASE_ID_STEP
    season_count = len(RELEASE_SEASONS)
    season = RELEASE_SEASONS[step % season_count]
    year = RELEASE_BASE_YEAR + step // season_count
    if season == "Winter":
        year += 1
    return f"{season} '{year}"


def _build_release_slug(release_id: int) -> str:
    name = _build_release_name(release_id)
    season, year = name.split()
    clean_year = year.replace("'", "")
    return f"{season.lower()}_{clean_year}"


def _format_impact_report(report: ImpactReport, release_name: str) -> str:
    """Format an ImpactReport into Markdown."""
    lines = [f"# Impact Report: {release_name}\n"]
    lines.append(f"**Total features analyzed:** {report.total_features}\n")
    if report.breaking_changes:
        lines.append(f"## Breaking Changes ({len(report.breaking_changes)})\n")
        for item in report.breaking_changes:
            lines.append(f"- {item}")
        lines.append("")
    if report.security_fixes:
        lines.append(f"## Security Fixes ({len(report.security_fixes)})\n")
        for item in report.security_fixes:
            lines.append(f"- {item}")
        lines.append("")
    lines.append(f"## Risk Score: {report.risk_score}\n")
    return "\n".join(lines)


def _format_notification_digest(digest: NotificationDigest) -> str:
    """Format a NotificationDigest into Markdown."""
    lines = ["# Notification Digest\n"]
    if digest.summary_text:
        lines.append(f"{digest.summary_text}\n")
    for notif in digest.notifications:
        priority_str = (
            notif.priority.value if hasattr(notif.priority, "value") else str(notif.priority)
        )
        lines.append(f"### [{priority_str}] {notif.title}\n")
        if notif.body:
            lines.append(f"{notif.body}\n")
    return "\n".join(lines)


def _slugify_category(name: str) -> str:
    """Transliterate Portuguese characters and slugify a category name."""
    lowered = name.lower()
    for char, replacement in TRANSLITERATE_MAP.items():
        lowered = lowered.replace(char, replacement)
    return re.sub(r"[^a-z0-9]+", "_", lowered).strip("_")


RELEASE_BADGE_MARKER = "<!-- RELEASE_BADGE -->"


def _update_badge(releases_to_process: list[ReleaseInfo]) -> None:
    """Update the dynamic release badge in README.md."""
    readme_path = Path("README.md")
    if not readme_path.exists():
        return

    import json as _json

    readme = readme_path.read_text(encoding="utf-8")
    if RELEASE_BADGE_MARKER not in readme:
        return

    releases_dir = Path(RELEASES_DIR)
    latest_meta = None
    for d in releases_dir.iterdir():
        meta_path = d / ".meta.json"
        if meta_path.exists():
            data = _json.loads(meta_path.read_text(encoding="utf-8"))
            if data.get("categories") and (
                latest_meta is None or data.get("release_id", 0) > latest_meta.get("release_id", 0)
            ):
                latest_meta = data

    if not latest_meta:
        return

    from .ai_automation import generate_dynamic_badge

    name = latest_meta["name"]
    total = sum(c.get("count", 0) for c in latest_meta.get("categories", []))
    badge = generate_dynamic_badge(name, total)

    new_line = f"{RELEASE_BADGE_MARKER}\n{badge}"
    lines = readme.split("\n")
    for i, line in enumerate(lines):
        if RELEASE_BADGE_MARKER in line:
            if i + 1 < len(lines) and lines[i + 1].startswith("!["):
                lines[i + 1] = badge
            else:
                lines[i] = new_line
            break

    readme_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Badge updated: %s (%d features)", name, total)


def _build_resource_footer(
    release: ReleaseInfo, templates: dict[str, str], locale: str
) -> list[str]:
    """Build the resource footer section for a category file."""
    lang_param = "pt_BR" if locale == "pt_BR" else "en_US"
    lines: list[str] = []
    lines.append(f"{templates['resources_section']}\n")
    lines.append(f"- [{templates['resource_pdf']}](./release-in-a-box.pdf)")
    lines.append(
        f"- [{templates['resource_feature_impact']}]"
        f"(https://help.salesforce.com/s/articleView?"
        f"id=release-notes.rn_feature_impact.htm&release={release.release_id}"
        f"&type=5&language={lang_param})"
    )
    lines.append(
        f"- [{templates['resource_release_notes']}]"
        f"(https://help.salesforce.com/s/articleView?"
        f"id=release-notes.rn_release_notes.htm&release={release.release_id}"
        f"&type=5&language={lang_param})"
    )
    lines.append("")
    return lines


async def _generate_release_files(
    release: ReleaseInfo,
    categories: list[FeatureImpactCategory],
    generator: MarkdownGenerator,
    translator: TranslatorService,
    locale: str = "pt_BR",
    enrichments: dict[str, CategoryEnrichment] | None = None,
) -> list[Path]:
    """Generate per-category .md files for a release in a specific locale.

    Args:
        enrichments: Optional dict of category slug -> CategoryEnrichment.
            When provided, adds AI-generated descriptions and impact levels.
    """

    from .salesforce import generate_category_trailhead_section

    templates = BILINGUAL_TEMPLATES[locale]
    release_dir = Path(RELEASES_DIR) / release.slug / locale
    release_dir.mkdir(parents=True, exist_ok=True)
    generated: list[Path] = []

    for cat in categories:
        slug = _slugify_category(cat.name)
        if locale == "en_US":
            slug = ENGLISH_CATEGORY_SLUGS.get(cat.name, slug)

        file_path = release_dir / f"{slug}.md"

        total = cat.total_features
        cat_name = cat.name if locale == "pt_BR" else ENGLISH_CATEGORY_NAMES.get(cat.name, cat.name)

        if locale == "en_US" and translator:
            import copy

            cat = copy.deepcopy(cat)
            for entry in cat.entries:
                entry.name = await translator.translate_feature(entry.name, "pt_BR", "en_US")
            for sub_entries in cat.subcategories.values():
                for entry in sub_entries:
                    entry.name = await translator.translate_feature(entry.name, "pt_BR", "en_US")

        toggle_html = generate_toggle_html(locale, slug, release.slug)

        lines: list[str] = [toggle_html]

        # 1. Category heading
        lines.append(f"## {cat_name}\n")

        # 2. Feature count (enriched with impact breakdown if available)
        enrichment = enrichments.get(slug) if enrichments else None
        if enrichment and enrichment.high_impact_count:
            impact_summary = (
                f"> **{total} {templates['category_count_suffix']}** "
                f"| 🔴 {enrichment.high_impact_count} alto impacto "
                f"| 🟡 {enrichment.medium_impact_count} médio "
                f"| 🟢 {enrichment.low_impact_count} baixo\n"
            )
            lines.append(impact_summary)
        else:
            lines.append(f"> **{total} {templates['category_count_suffix']}**\n")

        # 3. AI-generated introduction (if enrichment available)
        if enrichment and enrichment.introduction:
            lines.append(f"{enrichment.introduction}\n")
        elif cat.description:
            lines.append(f"{cat.description}\n")

        # 4. Feature table (enriched or standard)
        if enrichment and enrichment.features:
            # Enriched table with descriptions and impact
            lines.append(f"| {templates['features_header']} | Descrição | Impacto |")
            lines.append("| :--- | :--- | :---: |")
            for ef in enrichment.features:
                lines.append(ef.to_markdown_row())
            lines.append("")
        else:
            # Standard table (no enrichment)
            table_headers = (
                f"| {templates['features_header']} | {templates['users_header']} "
                f"| {templates['admins_header']} | {templates['config_header']} "
                f"| {templates['contact_header']} | {templates['docs_header']} |"
            )
            table_separator = "| :--- | :---: | :---: | :---: | :---: | :---: |"
            if cat.entries:
                lines.append(table_headers)
                lines.append(table_separator)
                for entry in cat.entries:
                    lines.append(_format_entry_table(entry))
                lines.append("")

        # 5. Subcategory tables
        for sub_name, sub_entries in cat.subcategories.items():
            if sub_entries:
                lines.append(f"### {sub_name}\n")
                if not (enrichment and enrichment.features):
                    table_headers = (
                        f"| {templates['features_header']} | {templates['users_header']} "
                        f"| {templates['admins_header']} | {templates['config_header']} "
                        f"| {templates['contact_header']} | {templates['docs_header']} |"
                    )
                    table_separator = "| :--- | :---: | :---: | :---: | :---: | :---: |"
                    lines.append(table_headers)
                    lines.append(table_separator)
                    for entry in sub_entries:
                        lines.append(_format_entry_table(entry))
                    lines.append("")

        # 6. Category-specific Trailhead (after content)
        trailhead_section = generate_category_trailhead_section(
            cat.name, release.slug, locale=locale
        )
        lines.append(trailhead_section)

        # 7. Resources footer
        lines.extend(_build_resource_footer(release, templates, locale))

        body = "\n".join(lines) if lines else f"_{templates['empty_category']}_\n"
        file_path.write_text(body, encoding="utf-8")
        generated.append(file_path)
        logger.info("Generated: %s (%d features)", file_path, len(cat.entries))

    return generated


def _generate_category_summary(category: FeatureImpactCategory) -> str:
    """Generate a brief summary for a category."""
    total = category.total_features
    high_impact = sum(1 for e in category.entries if e.confidence >= 0.7)

    if total == 0:
        return ""

    summary = f"{total} features"
    if high_impact > 0:
        summary += f", {high_impact} with high confidence"

    return summary


def _check(conf: bool) -> str:
    return "✅" if conf else "❌"


def _format_entry_table(entry: FeatureImpactEntry, docs_url: str = "") -> str:
    flag = ""
    if entry.confidence < 0.7:
        flag = " ⚠️"
    # Use entry's docs_url if available, otherwise use the parameter
    url = entry.docs_url if entry.docs_url else docs_url
    docs_link = f" [🔗]({url})" if url else ""
    return (
        f"| **{entry.name}**{flag} "
        f"| {_check(entry.available_users)} "
        f"| {_check(entry.available_admins)} "
        f"| {_check(entry.requires_config)} "
        f"| {_check(entry.contact_sf)} "
        f"|{docs_link} |"
    )


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

    total_features = 0
    total_confidence = 0.0
    cat_list: list[dict[str, object]] = []
    for cat in categories:
        count = cat.total_features
        total_features += count
        total_confidence += cat.avg_confidence * count
        cat_list.append({"name": cat.name, "count": count})

    avg_confidence = total_confidence / total_features if total_features else 0.0

    # Semantic version: major.minor.patch
    #   major = Salesforce release generation (increments yearly)
    #   minor = release within current generation (season index 0-2)
    #   patch = revision of the same release data (0 = first scrape)
    _season_index = {"Spring": 0, "Summer": 1, "Winter": 2}
    _season_part = release.name.split(" ")[0] if " " in release.name else "Spring"
    _year_part = 25  # default
    try:
        _year_part = int(release.name.split("'")[1])
    except (IndexError, ValueError):
        pass
    _major = _year_part - 24  # 2025 = v1.x.x
    _minor = _season_index.get(_season_part, 0)
    _patch = 0
    if meta_path.exists():
        try:
            _prev = json.loads(meta_path.read_text(encoding="utf-8"))
            _prev_ver = _prev.get("version", "1.0.0")
            _prev_patch = int(_prev_ver.split(".")[2])
            _patch = _prev_patch + 1
        except (json.JSONDecodeError, OSError, IndexError, ValueError):
            pass
    version = f"{_major}.{_minor}.{_patch}"

    meta: dict[str, object] = {
        "name": release.name,
        "slug": release.slug,
        "release_id": release.release_id,
        "version": version,
        "total_features": total_features,
        "avg_confidence": round(avg_confidence, 3),
        "generated_at": datetime.now(tz=UTC).isoformat(),
        "categories": cat_list,
    }

    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    _update_release_history(release, total_features, len(cat_list))


def _update_release_history(release: ReleaseInfo, total_features: int, category_count: int) -> None:
    """Append to release history tracker at releases/history.json."""
    import json as _json

    history_path = Path(RELEASES_DIR) / "history.json"
    history: list[dict[str, object]] = []
    if history_path.exists():
        history = _json.loads(history_path.read_text(encoding="utf-8"))

    entry = {
        "slug": release.slug,
        "name": release.name,
        "release_id": release.release_id,
        "total_features": total_features,
        "category_count": category_count,
        "processed_at": datetime.now(tz=UTC).isoformat(),
    }

    existing_idx = next((i for i, h in enumerate(history) if h.get("slug") == release.slug), -1)
    if existing_idx >= 0:
        history[existing_idx] = entry
    else:
        history.append(entry)

    history.sort(key=lambda h: int(str(h.get("release_id", 0))), reverse=True)
    history_path.write_text(_json.dumps(history, ensure_ascii=False, indent=2), encoding="utf-8")


def _get_release_emoji(name: str) -> str:
    """Get emoji for a release based on season name."""
    name_lower = name.lower()
    if "winter" in name_lower:
        return "❄️"
    elif "summer" in name_lower:
        return "☀️"
    return "🌸"


def _strip_markdown_headings(text: str) -> str:
    """Remove leading markdown heading markers (#, ##, ###) and trailing whitespace."""
    lines = text.splitlines()
    result_lines: list[str] = []
    for line in lines:
        stripped = line.lstrip("#").strip()
        result_lines.append(stripped)
    return "\n".join(result_lines)


def _has_meaningful_content(chunk: str) -> bool:
    """Check if a release block has real content beyond just a heading.

    Returns True only if:
    - The block is wrapped in <details> tags (curated content), OR
    - The block has at least 2 non-empty lines after stripping heading markers
    """
    if "<details>" in chunk:
        return True
    stripped = _strip_markdown_headings(chunk)
    non_empty = [ln for ln in stripped.splitlines() if ln.strip()]
    return len(non_empty) >= 2


def _detect_existing_release_chunk(text: str, release_name: str) -> str | None:
    """Return the markdown chunk for ``release_name`` already present in ``text``.

    Used to preserve manual edits when re-running the pipeline.
    """
    season_map = {
        "Spring": "spring",
        "Summer": "summer",
        "Winter": "winter",
    }
    parts = release_name.split("'")
    if len(parts) != 2:
        return None
    season_raw, year_raw = parts[0].strip(), parts[1].strip()
    season = season_map.get(season_raw)
    if not season or not year_raw.isdigit():
        return None

    pat = re.compile(
        r"(?:^|\n)(?P<chunk>(?:\s*<details>\s*\n\s*<summary><h3>[^<]*?"
        + re.escape(release_name)
        + r"[^<]*?</h3>.*?</details>)|(?:\s*###\s+[^\n]*?"
        + re.escape(release_name)
        + r"[^\n]*?(?:\n|$)(?:(?!^###\s).|\n)*?))",
        re.MULTILINE | re.DOTALL,
    )
    m = pat.search(text)
    if m:
        return m.group("chunk").lstrip("\n")
    return None


async def _build_release_block(
    metas: list[dict[str, Any]],
    lang: str,
    summarizer: Any,
    existing_text: str = "",
) -> str:
    """Build release section for a specific language.

    Latest release: fully expanded (all categories open).
    Old releases: entire section collapsed, with individual topic toggles inside.

    When ``existing_text`` is provided, the function reuses manually-curated
    blocks (categories intros, executive summaries) for releases that are
    already present in the README, instead of regenerating them from scratch.
    """
    lines: list[str] = [f"\n{RELEASE_SECTION_HEADING}\n"]

    # Language toggle
    if lang == "pt_BR":
        toggle = (
            '<div style="padding:12px;margin-bottom:20px;'
            'border:1px solid #d0d7de;border-radius:6px;background:#f6f8fa;text-align:center;">'
            "<strong>🌐 Idioma / Language:</strong> "
            "<strong>🇧🇷 Português</strong> | "
            '<a href="./README.en.md">🇺🇸 English</a>'
            "</div>"
        )
    else:
        toggle = (
            '<div style="padding:12px;margin-bottom:20px;'
            'border:1px solid #d0d7de;border-radius:6px;background:#f6f8fa;text-align:center;">'
            "<strong>🌐 Language / Idioma:</strong> "
            "<strong>🇺🇸 English</strong> | "
            '<a href="./README.md">🇧🇷 Português</a>'
            "</div>"
        )
    lines.append(toggle)

    for idx, meta in enumerate(metas):
        slug = meta["slug"]
        name = meta["name"]
        emoji = _get_release_emoji(name)
        is_latest = idx == 0

        existing_chunk = (
            _detect_existing_release_chunk(existing_text, name) if existing_text else None
        )
        if existing_chunk is not None and existing_chunk.strip():
            has_real_content = _has_meaningful_content(existing_chunk)
            if has_real_content:
                logger.info(
                    "README: reusing existing curated block for %s (preserves manual edits)",
                    slug,
                )
                lines.append("\n" + existing_chunk.rstrip() + "\n")
                lines.append("")
                continue
            logger.info(
                "README: detected empty block for %s — will regenerate",
                slug,
            )

        categories = meta.get("categories", [])
        active = [c for c in categories if c.get("count", 0) > 0]

        summary = await summarizer.summarize(slug)
        summary_text = ""
        themes_text = ""
        impact_text = ""
        migration_text = ""
        cat_summaries: dict[str, str] = {}
        if summary:
            # Validate summary against meta to avoid showing bad data
            meta_total = meta.get("total_features", 0)
            meta_cat_count = len(meta.get("categories", []))
            summary_is_valid = True

            if meta_total > 0 and "0 novos recursos" in summary.executive_summary:
                logger.warning(
                    "README: summary for %s says '0 recursos' but meta has %d — using fallback",
                    slug,
                    meta_total,
                )
                summary_is_valid = False

            if meta_cat_count > 0 and len(summary.category_summaries) == 0:
                logger.warning(
                    "README: summary for %s has 0 category_summaries but meta has %d — using fallback",
                    slug,
                    meta_cat_count,
                )
                summary_is_valid = False

            if summary_is_valid:
                if lang == "pt_BR":
                    summary_text = (
                        f"> 📊 **Resumo Executivo:** {summary.executive_summary[:5000]}\n"
                    )
                else:
                    summary_text = (
                        f"> 📊 **Executive Summary:** {summary.executive_summary[:5000]}\n"
                    )
                cat_summaries = summary.category_summaries

                if summary.business_impact:
                    if lang == "pt_BR":
                        impact_text = (
                            f"\n> 🎯 **Impacto Estratégico:** {summary.business_impact[:2000]}\n"
                        )
                    else:
                        impact_text = (
                            f"\n> 🎯 **Strategic Impact:** {summary.business_impact[:2000]}\n"
                        )

                if summary.strategic_themes:
                    themes = [t for t in summary.strategic_themes if t][:5]
                    if themes:
                        if lang == "pt_BR":
                            themes_text = f"\n> 📌 **Temas-Chave:** {' • '.join(themes)}\n"
                        else:
                            themes_text = f"\n> 📌 **Key Themes:** {' • '.join(themes)}\n"

                if summary.migration_notes and not summary.migration_notes.lower().startswith(
                    ("nenhuma", "none")
                ):
                    if lang == "pt_BR":
                        migration_text = (
                            f"\n> ⚠️ **Notas de Migração:** {summary.migration_notes[:2000]}\n"
                        )
                    else:
                        migration_text = (
                            f"\n> ⚠️ **Migration Notes:** {summary.migration_notes[:2000]}\n"
                        )

        # Build category details
        cat_lines: list[str] = []
        for cat in active:
            cat_name = cat["name"]
            count = cat["count"]
            cat_slug = _slugify_category(cat_name)
            link = f"./releases/{slug}/{lang}/{cat_slug}.md"

            if lang == "en_US":
                display_name = ENGLISH_CATEGORY_NAMES.get(cat_name, cat_name)
                count_label = "features"
                details_label = "Full details"
            else:
                display_name = cat_name
                count_label = "recursos"
                details_label = "Detalhes completos"

            cat_summary_text = ""
            if cat_name in cat_summaries:
                raw_summary = cat_summaries[cat_name]
                # Validate: don't show summary that says 1 feature when meta says more
                cat_meta_count = count  # from meta.categories[].count
                if cat_meta_count > 5 and "1 novos recursos" in raw_summary:
                    logger.warning(
                        "README: skipping invalid cat summary for %s (says 1 but meta has %d)",
                        cat_name,
                        cat_meta_count,
                    )
                else:
                    cat_summary_text = f"\n> {raw_summary[:1000]}\n"

            cat_lines.append("\n<details>")
            cat_lines.append(
                f"<summary><b>📄 {display_name} ({count} {count_label})</b></summary>\n"
            )
            if cat_summary_text:
                cat_lines.append(cat_summary_text)
            cat_lines.append(f"> 📄 {details_label}: [{link}]({link})\n")
            cat_lines.append("</details>\n")

        if is_latest:
            lines.append(f"\n### {emoji} {name}\n")
            if summary_text:
                lines.append(summary_text)
            if themes_text:
                lines.append(themes_text)
            if impact_text:
                lines.append(impact_text)
            if migration_text:
                lines.append(migration_text)
            lines.extend(cat_lines)
        else:
            lines.append("\n<details>\n")
            lines.append(f"<summary><h3>{emoji} {name}</h3></summary>\n")
            if summary_text:
                lines.append(summary_text)
            if themes_text:
                lines.append(themes_text)
            if impact_text:
                lines.append(impact_text)
            if migration_text:
                lines.append(migration_text)
            lines.extend(cat_lines)
            lines.append("</details>\n")
            lines.append("")
            lines.append("")

        lines.append("")

    return "\n".join(lines)


def _find_release_heading(text: str) -> str | None:
    """Find the releases section heading in README text.

    Searches known variants first (exact match), then falls back to
    detecting any ``## `` heading containing release-related keywords
    near the badge marker. Returns the heading string if found, else None.
    """
    for heading in _RELEASE_HEADING_VARIANTS:
        if heading in text:
            return heading

    # Fallback: look for a ## heading with release-related keywords
    # within 500 chars after the badge marker.
    badge_idx = text.find(RELEASE_BADGE_MARKER)
    if badge_idx == -1:
        return None

    search_window = text[badge_idx : badge_idx + 2000]
    match = re.search(r"^## .+$", search_window, re.MULTILINE)
    if match:
        heading = match.group(0).strip()
        lower = heading.lower()
        if any(kw in lower for kw in ("release", "releases", "catalog")):
            return heading

    return None


async def _update_single_readme(
    readme_path: Path,
    metas: list[dict[str, Any]],
    lang: str,
    summarizer: Any,
) -> None:
    """Update a single README file with release sections.

    Idempotent: preserves existing curated release blocks (executive summaries,
    category descriptions) for releases already present in the README, and
    only inserts newly-detected releases. Content before/after the releases
    section is left untouched.
    """
    if not readme_path.exists():
        return

    original = readme_path.read_text(encoding="utf-8")
    heading = _find_release_heading(original)
    if heading is None:
        logger.warning(
            "README %s: nenhuma seção de releases encontrada — skip",
            readme_path.name,
        )
        return

    heading_idx = original.index(heading)
    # Safety: only replace content AFTER the releases heading, never before it.
    # Content before this heading (e.g., Guia Completo, project description) is preserved.
    next_heading = original.find("\n## ", heading_idx + len(heading))
    if next_heading == -1:
        logger.warning(
            "README %s: nenhum heading '## ' encontrado após releases — skip para preservar conteúdo",
            readme_path.name,
        )
        return
    existing_block = original[heading_idx:next_heading]
    new_block = await _build_release_block(metas, lang, summarizer, existing_text=existing_block)
    updated = original[:heading_idx] + new_block + original[next_heading:]
    readme_path.write_text(updated, encoding="utf-8")
    logger.info("README atualizado (%s) — heading='%s'", lang, heading)


async def update_readme_all() -> None:
    """Generate bilingual README files (pt_BR and en_US) with release sections."""
    releases_dir = Path(RELEASES_DIR)
    if not releases_dir.exists():
        return

    import json

    metas: list[dict[str, Any]] = []
    for d in releases_dir.iterdir():
        meta_path = d / ".meta.json"
        if meta_path.exists():
            data = json.loads(meta_path.read_text(encoding="utf-8"))
            if data.get("categories"):
                metas.append(data)

    if not metas:
        logger.warning("No releases with categories found, skipping README update")
        return

    metas.sort(key=lambda m: m.get("release_id", 0), reverse=True)

    from .release_summarizer import ReleaseSummarizer

    summarizer = ReleaseSummarizer(str(releases_dir))

    # Generate pt_BR README
    await _update_single_readme(Path("README.md"), metas, "pt_BR", summarizer)

    # Generate en_US README
    readme_en_path = Path("README.en.md")
    if readme_en_path.exists():
        original_en = readme_en_path.read_text(encoding="utf-8")
        if _find_release_heading(original_en) is not None:
            await _update_single_readme(readme_en_path, metas, "en_US", summarizer)
        else:
            # Create en_US README from pt_BR if heading not found
            pt_readme = Path("README.md").read_text(encoding="utf-8")
            en_readme = pt_readme.replace("Português", "English")
            en_readme = en_readme.replace("pt_BR", "en_US")
            readme_en_path.write_text(en_readme, encoding="utf-8")
            logger.info("README.en.md recriado a partir do pt_BR")
