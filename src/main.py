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
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import (
    BILINGUAL_TEMPLATES,
    ENGLISH_CATEGORY_NAMES,
    ENGLISH_CATEGORY_SLUGS,
    FEATURE_IMPACT_URL,
    KNOWN_RELEASES,
    RELEASES_DIR,
    ReleaseInfo,
)
from .i18n import generate_toggle_html
from .generator import MarkdownGenerator
from .translator import TranslatorService
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
        return None  # pragma: no cover — unreachable: latest is first in sorted list

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


async def _generate_ai_reports_async(releases_to_process: list[ReleaseInfo]) -> None:
    """Generate all AI reports concurrently."""
    if not releases_to_process:
        return
    try:
        from .ai_automation import AIAutomationService
        from .issue_triage import IssueTriager
        from .impact_analyzer import ImpactAnalyzer
        from .smart_notifications import SmartNotificationEngine, UserPreferences

        ai_service = AIAutomationService()
        triager = IssueTriager()
        analyzer = ImpactAnalyzer()
        engine = SmartNotificationEngine()

        # General reports
        changelog_task = ai_service.generate_changelog()
        quality_task = ai_service.generate_quality_report()

        # Comparison reports for the latest release
        current_slug = releases_to_process[-1].slug
        known_sorted = sorted(KNOWN_RELEASES, key=lambda x: x.release_id, reverse=True)
        current_idx = next((i for i, r in enumerate(known_sorted) if r.slug == current_slug), -1)

        previous_slug = None
        if current_idx >= 0 and current_idx + 1 < len(known_sorted):
            previous_slug = known_sorted[current_idx + 1].slug

        diff_tasks = []
        if previous_slug:
            diff_tasks = [
                ai_service.generate_regression_report(current_slug, previous_slug),
                ai_service.generate_diff_report(current_slug, previous_slug),
            ]

        # Gather general and diff reports
        all_initial_tasks = [changelog_task, quality_task] + diff_tasks
        all_results = await asyncio.gather(*all_initial_tasks)

        Path("CHANGELOG.md").write_text(all_results[0], encoding="utf-8")
        Path("QUALITY_REPORT.md").write_text(all_results[1], encoding="utf-8")

        if previous_slug:
            Path("REGRESSION_REPORT.md").write_text(all_results[2], encoding="utf-8")
            Path("DIFF_REPORT.md").write_text(all_results[3], encoding="utf-8")
            logger.info("Regression and Diff reports generated.")

        _update_badge(releases_to_process)

        # Per-release AI processing
        async def process_release_ai(release: ReleaseInfo) -> None:
            meta_path = Path(RELEASES_DIR) / release.slug / ".meta.json"
            if not meta_path.exists():
                return

            import json as _json

            meta = _json.loads(meta_path.read_text(encoding="utf-8"))
            cats = meta.get("categories", [])
            total = sum(c.get("count", 0) for c in cats)

            try:
                issue_title = f"Release: {release.name}"
                issue_body = (
                    f"Release {release.name} with {total} features across {len(cats)} categories."
                )
                await triager.triage_issue(issue_title, issue_body)
            except Exception as e:
                logger.warning("Issue triage failed: %s", e)

            issue_url = await ai_service.create_github_issue(release.name, total, len(cats))
            if issue_url:
                logger.info("GitHub Issue created: %s", issue_url)

        await asyncio.gather(*(process_release_ai(r) for r in releases_to_process))

        # Impact and Notification Reports
        async def process_analytics(release: ReleaseInfo) -> None:
            try:
                report = await analyzer.analyze(release.slug)
                if report:
                    impact_path = Path("IMPACT_REPORT.md")
                    impact_path.write_text(
                        _format_impact_report(report, release.name), encoding="utf-8"
                    )
            except Exception as e:
                logger.warning("Impact analysis failed: %s", e)

            try:
                notifs = await engine.generate_from_release(release.slug)
                if notifs:
                    default_user = UserPreferences(
                        user_id="pipeline", interests=["all"], categories=["all"]
                    )
                    digest = await engine.generate_digest(notifs, default_user)
                    notif_path = Path("NOTIFICATION_DIGEST.md")
                    notif_path.write_text(_format_notification_digest(digest), encoding="utf-8")
            except Exception as e:
                logger.warning("Notification digest failed: %s", e)

        await asyncio.gather(*(process_analytics(r) for r in releases_to_process))
        logger.info("All AI reports generated concurrently.")

    except ImportError as e:
        logger.error("Failed to import AI automation modules: %s", e)


async def run_pipeline() -> None:
    """Orquestrador: fetch feature impact + PDF, generate markdown for latest unseen release."""
    setup_logging()
    from .logger import new_correlation_id

    cid = new_correlation_id()
    logger.info("Starting pipeline (correlation_id=%s)", cid)

    from .health import set_pipeline_status

    set_pipeline_status("running")

    scraper = SalesforceReleaseScraper()
    impact_parser = FeatureImpactParser()
    generator = MarkdownGenerator(base_dir=RELEASES_DIR)
    translator = TranslatorService()

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
                await _update_readme_all()
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
                logger.warning(
                    "No content for %s — falling back to existing release data",
                    release.name,
                )
                continue

            categories = impact_parser.parse_text(raw_text)
            logger.info("Parsed %d categories from feature impact", len(categories))

            for locale in ["pt_BR", "en_US"]:
                await _generate_release_files(
                    release, categories, generator, translator, locale=locale
                )
            _update_readme_single(release, categories)

            # Classify features and enrich .meta.json
            try:
                from .feature_classifier import FeatureClassifier

                classifier = FeatureClassifier()
                classification = await classifier.classify_release(release.slug)
                if classification:
                    meta_path = Path(RELEASES_DIR) / release.slug / ".meta.json"
                    if meta_path.exists():
                        import json as _cli_json

                        meta = _cli_json.loads(meta_path.read_text(encoding="utf-8"))
                        avg_conf = (
                            sum(f.confidence for f in classification.features)
                            / len(classification.features)
                            if classification.features
                            else 0.0
                        )
                        meta["classification_summary"] = {
                            "total_classified": classification.total_features,
                            "avg_confidence": round(avg_conf, 2),
                            "by_impact": classification.by_impact,
                            "by_type": classification.by_type,
                        }
                        meta_path.write_text(
                            _cli_json.dumps(meta, indent=2, ensure_ascii=False),
                            encoding="utf-8",
                        )
                        logger.info("Feature classification added to .meta.json")
            except Exception as e:
                logger.warning("Feature classification failed: %s", e)

    await _update_readme_all()

    try:
        await _generate_ai_reports_async(releases_to_process)
    except Exception as e:
        logger.warning("Failed to generate AI reports: %s", e)
        set_pipeline_status("completed_with_errors")
    else:
        set_pipeline_status("completed")


def _format_impact_report(report: object, release_name: str) -> str:
    """Format an ImpactReport into Markdown."""
    lines = [f"# Impact Report: {release_name}\n"]
    if hasattr(report, "total_features"):
        lines.append(f"**Total features analyzed:** {report.total_features}\n")
    if hasattr(report, "breaking_changes") and report.breaking_changes:
        lines.append(f"## Breaking Changes ({len(report.breaking_changes)})\n")
        for item in report.breaking_changes:
            lines.append(f"- {item}")
        lines.append("")
    if hasattr(report, "security_fixes") and report.security_fixes:
        lines.append(f"## Security Fixes ({len(report.security_fixes)})\n")
        for item in report.security_fixes:
            lines.append(f"- {item}")
        lines.append("")
    if hasattr(report, "risk_score"):
        lines.append(f"## Risk Score: {report.risk_score}\n")
    return "\n".join(lines)


def _format_notification_digest(digest: object) -> str:
    """Format a NotificationDigest into Markdown."""
    lines = ["# Notification Digest\n"]
    if hasattr(digest, "summary"):
        lines.append(f"{digest.summary}\n")
    if hasattr(digest, "notifications"):
        for notif in digest.notifications:
            priority = getattr(notif, "priority", "info")
            title = getattr(notif, "title", "Update")
            message = getattr(notif, "message", "")
            lines.append(f"### [{priority}] {title}\n")
            if message:
                lines.append(f"{message}\n")
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
            if data.get("categories"):
                if latest_meta is None or data.get("release_id", 0) > latest_meta.get(
                    "release_id", 0
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


async def _generate_release_files(
    release: ReleaseInfo,
    categories: list[FeatureImpactCategory],
    generator: MarkdownGenerator,
    translator: TranslatorService,
    locale: str = "pt_BR",
) -> list[Path]:
    """Generate per-category .md files for a release in a specific locale."""

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
            for entry in cat.entries:
                entry.name = await translator.translate_feature(entry.name, "pt_BR", "en_US")
            for sub_entries in cat.subcategories.values():
                for entry in sub_entries:
                    entry.name = await translator.translate_feature(entry.name, "pt_BR", "en_US")

        toggle_html = generate_toggle_html(locale, slug, release.slug)

        lines: list[str] = [toggle_html]

        # 1. Category heading
        lines.append(f"## {cat_name}\n")

        # 2. Feature count
        lines.append(f"> **{total} {templates['category_count_suffix']}**\n")

        # 3. Optional description
        if cat.description:
            lines.append(f"{cat.description}\n")

        # 4. Feature table (main entries)
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
        lang_param = "pt_BR" if locale == "pt_BR" else "en_US"
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
    docs_link = f" [🔗]({docs_url})" if docs_url else ""
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

    if meta_path.exists():
        existing = json.loads(meta_path.read_text(encoding="utf-8"))
        if existing.get("categories"):
            logger.debug("Skipping .meta.json write for %s (already has data)", release.slug)
            return

    total_features = 0
    total_confidence = 0.0
    cat_list: list[dict[str, object]] = []
    for cat in categories:
        count = cat.total_features
        total_features += count
        total_confidence += cat.avg_confidence * count
        cat_list.append({"name": cat.name, "count": count})

    avg_confidence = total_confidence / total_features if total_features else 0.0

    meta: dict[str, object] = {
        "name": release.name,
        "slug": release.slug,
        "release_id": release.release_id,
        "total_features": total_features,
        "avg_confidence": round(avg_confidence, 3),
        "generated_at": datetime.now(tz=timezone.utc).isoformat(),
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
        "processed_at": datetime.now(tz=timezone.utc).isoformat(),
    }

    existing_idx = next((i for i, h in enumerate(history) if h.get("slug") == release.slug), -1)
    if existing_idx >= 0:
        history[existing_idx] = entry
    else:
        history.append(entry)

    history.sort(key=lambda h: int(str(h.get("release_id", 0))), reverse=True)
    history_path.write_text(_json.dumps(history, ensure_ascii=False, indent=2), encoding="utf-8")


async def _update_readme_all() -> None:
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

    def get_release_emoji(name: str) -> str:
        name_lower = name.lower()
        if "winter" in name_lower:
            return "❄️"
        elif "summer" in name_lower:
            return "☀️"
        return "🌸"

    async def build_release_block(metas: list[dict[str, Any]], lang: str) -> str:
        """Build release section for a specific language.

        Latest release: fully expanded (all categories open).
        Old releases: entire section collapsed, with individual topic toggles inside.
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
            emoji = get_release_emoji(name)
            is_latest = idx == 0

            categories = meta.get("categories", [])
            active = [c for c in categories if c.get("count", 0) > 0]

            summary = await summarizer.summarize(slug)
            summary_text = ""
            if summary:
                if lang == "pt_BR":
                    summary_text = f"> 📊 **Resumo Executivo:** {summary.summary_text[:200]}...\n"
                else:
                    summary_text = f"> 📊 **Executive Summary:** {summary.summary_text[:200]}...\n"

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

                cat_lines.append("\n<details>")
                cat_lines.append(
                    f"<summary><b>📄 {display_name} ({count} {count_label})</b></summary>\n"
                )
                cat_lines.append(f"> 📄 {details_label}: [{link}]({link})\n")
                cat_lines.append("</details>\n")

            if is_latest:
                # Latest release: open as whole, categories closed by default
                lines.append(f"\n### {emoji} {name}\n")
                if summary_text:
                    lines.append(summary_text)
                lines.extend(cat_lines)
            else:
                # Old releases: entire section collapsed
                lines.append("\n<details>\n")
                lines.append(f"<summary><h3>{emoji} {name}</h3></summary>\n")
                if summary_text:
                    lines.append(summary_text)
                lines.extend(cat_lines)
                lines.append("</details>\n")

            lines.append("")

        return "\n".join(lines)

    # Generate pt_BR README
    readme_path = Path("README.md")
    if readme_path.exists():
        original = readme_path.read_text(encoding="utf-8")
        if RELEASE_SECTION_HEADING in original:
            heading_idx = original.index(RELEASE_SECTION_HEADING)
            next_heading = original.find("\n## ", heading_idx + len(RELEASE_SECTION_HEADING))
            if next_heading == -1:
                next_heading = len(original)
            new_block = await build_release_block(metas, "pt_BR")
            updated = original[:heading_idx] + new_block + original[next_heading:]
            readme_path.write_text(updated, encoding="utf-8")
            logger.info("README.md atualizado (pt_BR)")

    # Generate en_US README
    readme_en_path = Path("README.en.md")
    if readme_en_path.exists():
        original_en = readme_en_path.read_text(encoding="utf-8")
        if RELEASE_SECTION_HEADING in original_en:
            heading_idx = original_en.index(RELEASE_SECTION_HEADING)
            next_heading = original_en.find("\n## ", heading_idx + len(RELEASE_SECTION_HEADING))
            if next_heading == -1:
                next_heading = len(original_en)
            new_block = await build_release_block(metas, "en_US")
            updated_en = original_en[:heading_idx] + new_block + original_en[next_heading:]
            readme_en_path.write_text(updated_en, encoding="utf-8")
            logger.info("README.en.md atualizado (en_US)")
        else:
            # Create en_US README from pt_BR if it doesn't exist
            pt_readme = readme_path.read_text(encoding="utf-8")
            en_readme = pt_readme.replace("Português", "English")
            en_readme = en_readme.replace("pt_BR", "en_US")
            readme_en_path.write_text(en_readme, encoding="utf-8")
            logger.info("README.en.md criado")


def main() -> None:
    """Entrypoint do script."""
    asyncio.run(run_pipeline())


if __name__ == "__main__":  # pragma: no cover
    main()
