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
from dataclasses import dataclass
import logging
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass

from .config import (
    FEATURE_IMPACT_URL,
    KNOWN_RELEASES,
    RELEASES_DIR,
    ReleaseInfo,
)
from .generator import MarkdownGenerator
from .translator import TranslatorService
from .logger import setup_logging
from .i18n import generate_toggle_html  # noqa: F401  (re-export p/ compatibilidade de testes)
from .parser import (
    FeatureImpactParser,
)
from .scraper import SalesforceReleaseScraper
from .exceptions import GitHubError, LLMError, NotificationError
from .llm_service import LLMService
from .events import EventBus, get_event_bus
from .cache_manager import CacheManager

from .release_docs import (  # noqa: F401
    RELEASE_SECTION_HEADING,
    RELEASE_SEASONS,
    RELEASE_BASE_ID,
    RELEASE_BASE_YEAR,
    RELEASE_ID_STEP,
    TRANSLITERATE_MAP,
    _find_existing_releases,
    _build_release_name,
    _build_release_slug,
    _format_impact_report,
    _format_notification_digest,
    _slugify_category,
    RELEASE_BADGE_MARKER,
    _update_badge,
    _build_resource_footer,
    _generate_release_files,
    _generate_category_summary,
    _check,
    _format_entry_table,
    _format_entry,
    _update_readme_single,
    _update_release_history,
    _get_release_emoji,
    _build_release_block,
    _update_single_readme,
    _update_readme_all,
)

# Salesforce release naming/numbering scheme assumptions.
# Update these constants if Salesforce changes release cadence or ID progression.


logger = logging.getLogger(__name__)


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
        # No existing releases found. Process the latest known release,
        # but if it already exists (e.g. repo populated manually), fall back
        # to the next unseen release so we don't return an already-existing slug.
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


async def _process_release_triage(
    ai_service: Any,
    triager: Any,
    release: ReleaseInfo,
) -> None:
    """Triage and create GitHub Issue for a single release."""
    meta_path = Path(RELEASES_DIR) / release.slug / ".meta.json"
    if not meta_path.exists():
        return

    import json as _json

    meta = _json.loads(meta_path.read_text(encoding="utf-8"))
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


async def _generate_ai_reports_async(
    releases_to_process: list[ReleaseInfo],
    llm: LLMService | None = None,
) -> None:
    """Generate all AI reports concurrently."""
    if not releases_to_process:
        return
    try:
        from .ai_automation import AIAutomationService
        from .issue_triage import IssueTriager
        from .impact_analyzer import ImpactAnalyzer
        from .smart_notifications import SmartNotificationEngine

        ai_service = AIAutomationService()
        triager = IssueTriager(llm=llm)
        analyzer = ImpactAnalyzer(llm=llm)
        engine = SmartNotificationEngine(llm=llm)

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
        await asyncio.gather(
            *(_process_release_triage(ai_service, triager, r) for r in releases_to_process)
        )

        # Impact and Notification Reports
        await asyncio.gather(
            *(_process_release_analytics(analyzer, engine, r) for r in releases_to_process)
        )
        logger.info("All AI reports generated concurrently.")

    except ImportError as e:
        logger.error("Failed to import AI automation modules: %s", e)


def _parse_args() -> tuple[str | None, bool]:
    """Parse command line arguments.

    Returns:
        Tuple of (release_filter, dry_run).
    """
    args = sys.argv[1:]
    release_filter: str | None = None
    dry_run = False

    for i, arg in enumerate(args):
        if arg == "--release" and i + 1 < len(args):
            release_filter = args[i + 1]
        elif arg == "--dry-run":
            dry_run = True

    return release_filter, dry_run


async def _process_single_release(
    release: ReleaseInfo,
    scraper: SalesforceReleaseScraper,
    impact_parser: FeatureImpactParser,
    generator: MarkdownGenerator,
    translator: TranslatorService,
    dry_run: bool,
) -> bool:
    """Process a single release: fetch, parse, generate files.

    Returns:
        True if content was processed successfully, False otherwise.
    """
    logger.info("Processing release: %s (id=%d)", release.name, release.release_id)

    release_dir = Path(RELEASES_DIR) / release.slug
    release_dir.mkdir(parents=True, exist_ok=True)

    impact_url = FEATURE_IMPACT_URL.format(release_id=release.release_id)
    logger.info("Fetching feature impact: %s", impact_url)

    pdf_dest = release_dir / f"release-in-a-box-{release.slug}.pdf"
    pdf_task = asyncio.create_task(scraper.download_pdf_from_button(impact_url, pdf_dest))

    raw_text = await scraper.fetch_page_raw_text(impact_url)

    await pdf_task
    if dry_run:
        logger.info(
            "[DRY RUN] Conteudo obtido (%d chars). Nenhum arquivo sera gerado.",
            len(raw_text or ""),
        )
        return False

    if not raw_text:
        logger.warning(
            "No content for %s — falling back to existing release data",
            release.name,
        )
        return False

    categories = impact_parser.parse_text(raw_text)
    logger.info("Parsed %d categories from feature impact", len(categories))

    for locale in ["pt_BR", "en_US"]:
        await _generate_release_files(release, categories, generator, translator, locale=locale)
    _update_readme_single(release, categories)
    return True


async def _enrich_meta_with_classification(
    release: ReleaseInfo,
    classifier: Any | None = None,
) -> None:
    """Add feature classification to .meta.json."""
    try:
        from .feature_classifier import FeatureClassifier

        if classifier is None:
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
    except (LLMError, OSError) as e:
        logger.warning("Feature classification failed: %s", e)


@dataclass
class PipelineConfig:
    """Dependency injection container for the release notes pipeline.

    All fields have sensible defaults for production use.  Override any field
    in tests or when running with alternative implementations.

    Example::

        config = PipelineConfig(dry_run=True)
        await run_pipeline(config)
    """

    scraper: SalesforceReleaseScraper | None = None
    impact_parser: FeatureImpactParser | None = None
    generator: MarkdownGenerator | None = None
    translator: TranslatorService | None = None
    llm: LLMService | None = None
    cache: CacheManager | None = None
    event_bus: EventBus | None = None
    release_filter: str | None = None
    dry_run: bool = False

    def __post_init__(self) -> None:
        """Initialize defaults for fields left as None."""
        if self.cache is None:
            self.cache = CacheManager(cache_dir=Path("cache"), ttl_seconds=86400 * 7)
        if self.event_bus is None:
            self.event_bus = get_event_bus()
        if self.llm is None:
            self.llm = LLMService(cache=self.cache)
        if self.scraper is None:
            self.scraper = SalesforceReleaseScraper()
        if self.impact_parser is None:
            self.impact_parser = FeatureImpactParser()
        if self.generator is None:
            self.generator = MarkdownGenerator(base_dir=RELEASES_DIR)
        if self.translator is None:
            self.translator = TranslatorService(llm=self.llm)


async def run_pipeline(config: PipelineConfig | None = None) -> None:
    """Orquestrador: fetch feature impact + PDF, generate markdown for latest unseen release."""
    setup_logging()
    from .logger import new_correlation_id

    cid = new_correlation_id()
    logger.info("Starting pipeline (correlation_id=%s)", cid)

    from .health import set_pipeline_status

    set_pipeline_status("running")

    if config is None:
        release_filter, dry_run = _parse_args()
        config = PipelineConfig(release_filter=release_filter, dry_run=dry_run)

    scraper = config.scraper
    impact_parser = config.impact_parser
    generator = config.generator
    translator = config.translator
    llm = config.llm

    assert scraper is not None, "scraper must be initialized"
    assert impact_parser is not None, "impact_parser must be initialized"
    assert generator is not None, "generator must be initialized"
    assert translator is not None, "translator must be initialized"
    assert llm is not None, "llm must be initialized"

    if config.dry_run:
        logger.info("[DRY RUN] Modo simulacao ativado — nenhum arquivo sera escrito")

    releases_to_process: list[ReleaseInfo] = []
    bus = config.event_bus or get_event_bus()

    await bus.emit("pipeline.started", {"dry_run": config.dry_run}, source="run_pipeline")

    async with scraper:
        if release_filter:
            for r in KNOWN_RELEASES:
                if r.slug == release_filter:
                    releases_to_process.append(r)
                    break
            if not releases_to_process:
                logger.error("Release '%s' not found in KNOWN_RELEASES", release_filter)
                await bus.emit(
                    "pipeline.error", {"error": "release not found"}, source="run_pipeline"
                )
                return
        else:
            new_release = await detect_new_release(scraper)
            if new_release:
                releases_to_process.append(new_release)
                await bus.emit(
                    "release.detected",
                    {"slug": new_release.slug, "name": new_release.name},
                    source="run_pipeline",
                )
            else:
                logger.info("No new release detected. Updating README only.")
                await _update_readme_all()
                await bus.emit("pipeline.completed", {"new_releases": 0}, source="run_pipeline")
                return

        async with llm:
            for release in releases_to_process:
                await _process_single_release(
                    release, scraper, impact_parser, generator, translator, config.dry_run
                )
                await bus.emit(
                    "release.processed",
                    {"slug": release.slug, "name": release.name},
                    source="run_pipeline",
                )
                if not config.dry_run:
                    await _enrich_meta_with_classification(release, classifier=None)
                    await bus.emit(
                        "release.classified", {"slug": release.slug}, source="run_pipeline"
                    )

            await _update_readme_all()

            try:
                await _generate_ai_reports_async(releases_to_process, llm=llm)
            except (LLMError, GitHubError, NotificationError, OSError) as e:
                logger.warning("Failed to generate AI reports: %s", e)
                set_pipeline_status("completed_with_errors")
                await bus.emit("pipeline.error", {"error": str(e)}, source="run_pipeline")
            else:
                set_pipeline_status("completed")
                await bus.emit(
                    "pipeline.completed",
                    {"new_releases": len(releases_to_process)},
                    source="run_pipeline",
                )


def main() -> None:
    """Entrypoint do script."""
    asyncio.run(run_pipeline())


if __name__ == "__main__":  # pragma: no cover
    main()
