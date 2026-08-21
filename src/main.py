"""Main orchestrator for Salesforce release notes extraction (web scraping).

Strategy:
  1. Detect new releases by probing Salesforce for unseen release IDs
  2. Scrape only new releases (not already in releases/ dir)
  3. Deep-scrape each article for summaries (pt-BR)
  4. Generate Markdown artifacts per topic
  5. Update README organized chronologically (newest on top)
  6. Generate summary cache for AI-generated content
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
from pathlib import Path
from typing import Any

from .config import (
    FEATURE_IMPACT_URL,
    KNOWN_RELEASES,
    RELEASES_DIR,
    ReleaseInfo,
)
from .exceptions import GitHubError, LLMError, NotificationError
from .generator import MarkdownGenerator
from .i18n import generate_toggle_html  # noqa: F401
from .llm_service import LLMService
from .logger import setup_logging
from .parser import (
    FeatureImpactParser,
)
from .release_docs import (  # noqa: F401
    RELEASE_BADGE_MARKER,
    RELEASE_BASE_ID,
    RELEASE_BASE_YEAR,
    RELEASE_ID_STEP,
    RELEASE_SEASONS,
    RELEASE_SECTION_HEADING,
    TRANSLITERATE_MAP,
    _build_release_block,
    _build_release_name,
    _build_release_slug,
    _build_resource_footer,
    _check,
    _find_existing_releases,
    _format_entry,
    _format_entry_table,
    _format_impact_report,
    _format_notification_digest,
    _generate_category_summary,
    _generate_release_files,
    _get_release_emoji,
    _slugify_category,
    _update_badge,
    _update_readme_single,
    _update_release_history,
    _update_single_readme,
    update_readme_all,
)
from .scraper import SalesforceReleaseScraper
from .translator import TranslatorService

logger = logging.getLogger(__name__)


async def detect_new_release(scraper: SalesforceReleaseScraper) -> ReleaseInfo | None:
    """Detect whether there is a new release candidate to process."""
    existing_slugs = _find_existing_releases()
    known_sorted = sorted(KNOWN_RELEASES, key=lambda x: x.release_id, reverse=True)

    current = None
    for r in known_sorted:
        if r.slug in existing_slugs:
            current = r
            break

    if current is None:
        for r in known_sorted:
            if r.slug not in existing_slugs:
                logger.info("No releases in repo, processing latest known: %s", r.name)
                return r
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

    results = await asyncio.gather(
        scraper.fetch_page_raw_text(current_url),
        scraper.fetch_page_raw_text(next_url),
        return_exceptions=True,
    )
    current_text = results[0] if not isinstance(results[0], BaseException) else None
    next_text = results[1] if not isinstance(results[1], BaseException) else None

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


async def _process_release_triage(
    ai_service: Any,
    triager: Any,
    release: ReleaseInfo,
) -> None:
    """Triage and create GitHub Issue for a single release."""
    meta_path = Path(RELEASES_DIR) / release.slug / ".meta.json"
    if not meta_path.exists():
        return

    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    cats = meta.get("categories", [])
    total = sum(c.get("count", 0) for c in cats)

    try:
        issue_title = f"Release: {release.name}"
        issue_body = f"Release {release.name} with {total} features across {len(cats)} categories."
        await triager.triage_issue(issue_title, issue_body)
    except (LLMError, GitHubError, OSError) as e:
        logger.warning("Issue triage failed: %s", e)

    issue_url = await ai_service.create_github_issue(release.name, total, len(cats))
    if issue_url:
        logger.info("GitHub Issue created: %s", issue_url)


async def _process_release_analytics(
    analyzer: Any,
    engine: Any,
    release: ReleaseInfo,
) -> None:
    """Generate impact report and notification digest for a single release."""
    try:
        report = await analyzer.analyze(release.slug)
        if report:
            impact_path = Path("IMPACT_REPORT.md")
            impact_path.write_text(_format_impact_report(report, release.name), encoding="utf-8")
    except (LLMError, OSError) as e:
        logger.warning("Impact analysis failed: %s", e)

    try:
        notifs = await engine.generate_from_release(release.slug)
        if notifs:
            from .smart_notifications import UserPreferences

            default_user = UserPreferences(
                user_id="pipeline", interests=["all"], categories=["all"]
            )
            digest = await engine.generate_digest(notifs, default_user)
            notif_path = Path("NOTIFICATION_DIGEST.md")
            notif_path.write_text(_format_notification_digest(digest), encoding="utf-8")
    except (NotificationError, LLMError, OSError) as e:
        logger.warning("Notification digest failed: %s", e)


def _load_meta_for_release(release_slug: str) -> dict[str, Any]:
    """Load .meta.json for a release as the source of truth."""
    meta_path = Path(RELEASES_DIR) / release_slug / ".meta.json"
    if meta_path.exists():
        try:
            result: dict[str, Any] = json.loads(meta_path.read_text(encoding="utf-8"))
            return result
        except (json.JSONDecodeError, OSError) as e:
            logger.warning("Could not read .meta.json for %s: %s", release_slug, e)
    return {}


def _validate_summary_cache(
    cache: dict[str, Any],
    meta: dict[str, Any],
    release_slug: str,
) -> bool:
    """Validate summary cache against .meta.json."""
    meta_total = meta.get("total_features", 0)
    meta_cats = meta.get("categories", [])
    meta_cat_count = len(meta_cats)

    exec_text = cache.get("executive_summary", "")
    cache_cats = cache.get("category_summaries", {})
    cache_cat_count = len(cache_cats)

    if meta_total > 0 and "0 novos recursos" in exec_text:
        logger.warning(
            "Cache validation failed for %s: says '0 recursos' but meta has %d",
            release_slug,
            meta_total,
        )
        return False

    if meta_cat_count > 0 and cache_cat_count == 0:
        logger.warning(
            "Cache validation failed for %s: 0 category_summaries but meta has %d categories",
            release_slug,
            meta_cat_count,
        )
        return False

    if meta_cat_count > 0 and cache_cat_count < meta_cat_count // 2:
        logger.warning(
            "Cache validation failed for %s: only %d/%d category summaries",
            release_slug,
            cache_cat_count,
            meta_cat_count,
        )
        return False

    if len(exec_text) < 100 and meta_total > 100:
        logger.warning(
            "Cache validation failed for %s: summary too short (%d chars) for %d features",
            release_slug,
            len(exec_text),
            meta_total,
        )
        return False

    return True


async def generate_summary_cache(
    release: ReleaseInfo,
    categories: list[Any],
    llm: LLMService | None = None,
) -> None:
    """Generate .summary_cache.json using the ReleaseSummarizer."""
    release_dir = Path(RELEASES_DIR) / release.slug
    summary_cache_path = release_dir / ".summary_cache.json"
    meta = _load_meta_for_release(release.slug)

    if llm is not None:
        try:
            from .release_summarizer import ReleaseSummarizer

            summarizer = ReleaseSummarizer(base_dir=str(RELEASES_DIR), llm=llm)
            summary = await summarizer.summarize(release.slug)

            if summary:
                ai_cache: dict[str, Any] = {
                    "executive_summary": summary.executive_summary,
                    "category_summaries": summary.category_summaries,
                    "business_impact": summary.business_impact,
                    "strategic_themes": summary.strategic_themes,
                    "migration_notes": summary.migration_notes,
                    "generated_at": str(Path.cwd()),
                }

                if _validate_summary_cache(ai_cache, meta, release.slug):
                    summary_cache_path.write_text(
                        json.dumps(ai_cache, indent=2, ensure_ascii=False),
                        encoding="utf-8",
                    )
                    logger.info("AI-generated summary cache saved to %s", summary_cache_path)
                    return
        except (LLMError, OSError, ImportError) as e:
            logger.warning("AI summary generation failed: %s", e)

    try:
        meta_cats = meta.get("categories", [])
        meta_total = meta.get("total_features", 0)

        if meta_cats:
            cat_source = meta_cats
            cat_total = meta_total
        elif categories:
            cat_source = categories
            cat_total = 0
        else:
            logger.error("No categories available (meta or memory) for %s", release.slug)
            return

        basic_summaries: dict[str, str] = {}
        computed_total = 0
        for category in cat_source:
            if isinstance(category, dict):
                category_name = category.get("name", "")
                count = category.get("count", 0)
            else:
                category_name = getattr(category, "name", "")
                count = getattr(category, "total_features", 0)
            computed_total += count
            basic_summaries[category_name] = (
                f"A categoria {category_name} reúne {count} recursos referentes a "
                f"{category_name.lower()}. Esta categoria abrange melhorias e "
                f"novas funcionalidades para {category_name.lower()}."
            )

        total = cat_total if cat_total > 0 else computed_total
        cat_count = len(cat_source)

        executive_summary = (
            f"A release {release.name} representa uma atualização significativa "
            f"do ecossistema Salesforce, com {total} novos recursos "
            f"distribuídos em {cat_count} categorias."
        )

        fallback_cache: dict[str, Any] = {
            "executive_summary": executive_summary,
            "category_summaries": basic_summaries,
            "generated_at": str(Path.cwd()),
            "fallback": True,
        }

        if _validate_summary_cache(fallback_cache, meta, release.slug):
            summary_cache_path.write_text(
                json.dumps(fallback_cache, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            logger.info("Fallback summary cache saved to %s", summary_cache_path)
        else:
            logger.error("Fallback summary also invalid for %s", release.slug)
    except (OSError, TypeError, ValueError) as e:
        logger.error("Failed to generate fallback summary cache: %s", e)


async def generate_ai_reports_async(
    releases_to_process: list[ReleaseInfo],
    llm: LLMService | None = None,
) -> None:
    """Generate all AI reports concurrently."""
    if not releases_to_process:
        return
    try:
        from .ai_automation import AIAutomationService
        from .impact_analyzer import ImpactAnalyzer
        from .issue_triage import IssueTriager
        from .smart_notifications import SmartNotificationEngine

        ai_service = AIAutomationService()
        triager = IssueTriager(llm=llm)
        analyzer = ImpactAnalyzer(llm=llm)
        engine = SmartNotificationEngine(llm=llm)

        await ai_service.generate_changelog()
        await ai_service.generate_quality_report()

        current_slug = releases_to_process[-1].slug
        known_sorted = sorted(KNOWN_RELEASES, key=lambda x: x.release_id, reverse=True)
        current_idx = next((i for i, r in enumerate(known_sorted) if r.slug == current_slug), -1)

        previous_slug = None
        if current_idx >= 0 and current_idx + 1 < len(known_sorted):
            previous_slug = known_sorted[current_idx + 1].slug

        if previous_slug:
            await ai_service.generate_regression_report(current_slug, previous_slug)
            await ai_service.generate_diff_report(current_slug, previous_slug)

        for release in releases_to_process:
            await _process_release_triage(ai_service, triager, release)
            await _process_release_analytics(analyzer, engine, release)
            _update_badge(release.slug)
    except ImportError as e:
        logger.warning("AI modules unavailable for report generation: %s", e)
    except Exception as e:
        logger.warning("Failed to generate AI reports: %s", e)


async def process_single_release(
    release: ReleaseInfo,
    scraper: SalesforceReleaseScraper,
    impact_parser: FeatureImpactParser,
    generator: MarkdownGenerator,
    translator: TranslatorService | None = None,
    dry_run: bool = False,
) -> bool:
    """Process a single Salesforce release."""
    url = FEATURE_IMPACT_URL.format(release_id=release.release_id)
    raw_text = await scraper.fetch_page_raw_text(url)
    if not raw_text:
        logger.warning("No text extracted for release %s", release.name)
        return False

    if dry_run:
        logger.info("[DRY RUN] Would process release %s", release.name)
        return False

    categories = impact_parser.parse_text(raw_text)
    if not categories:
        logger.warning("No categories parsed for release %s", release.name)
        return False

    await _generate_release_files(release, categories, generator, translator)
    _update_readme_single(release.slug)

    try:
        from .feature_enricher import FeatureEnricher

        enricher = FeatureEnricher()
        await enricher.enrich_release(release.slug)
    except Exception as e:
        logger.warning("Feature enrichment skipped for %s: %s", release.slug, e)

    return True


async def run_pipeline(
    release_filter: str | None = None,
    dry_run: bool = False,
) -> None:
    """Execute the release notes scraping and processing pipeline."""
    setup_logging()
    logger.info("Starting Salesforce Release Notes Pipeline...")

    async with SalesforceReleaseScraper() as scraper:
        impact_parser = FeatureImpactParser()
        generator = MarkdownGenerator()
        translator = TranslatorService()

        releases_to_process: list[ReleaseInfo] = []

        if release_filter:
            matched = [r for r in KNOWN_RELEASES if r.slug == release_filter]
            if matched:
                releases_to_process = matched
            else:
                logger.error("Release slug '%s' not found in KNOWN_RELEASES", release_filter)
                return
        else:
            new_rel = await detect_new_release(scraper)
            if new_rel:
                releases_to_process = [new_rel]
            else:
                existing = _find_existing_releases()
                unprocessed = [r for r in KNOWN_RELEASES if r.slug not in existing]
                if unprocessed:
                    releases_to_process = unprocessed
                else:
                    logger.info("All known releases have already been processed.")
                    return

        processed: list[ReleaseInfo] = []
        for rel in releases_to_process:
            success = await process_single_release(
                release=rel,
                scraper=scraper,
                impact_parser=impact_parser,
                generator=generator,
                translator=translator,
                dry_run=dry_run,
            )
            if success:
                processed.append(rel)

        if processed and not dry_run:
            await update_readme_all()
            await generate_ai_reports_async(processed)


def _parse_args() -> tuple[str | None, bool]:
    parser = argparse.ArgumentParser(description="Salesforce Release Notes Scraper")
    parser.add_argument("--release", type=str, help="Release slug to process (e.g., summer_26)")
    parser.add_argument(
        "--dry-run", action="store_true", help="Perform a dry run without writing files"
    )
    args, _ = parser.parse_known_args()
    return args.release, args.dry_run


def main() -> None:
    release_filter, dry_run = _parse_args()
    asyncio.run(run_pipeline(release_filter=release_filter, dry_run=dry_run))


if __name__ == "__main__":
    main()
