"""Documentation service — public facade over ``release_docs`` internals.

``src.main`` previously imported 19 private (``_``-prefixed) functions from
``release_docs.py``, creating tight coupling between the orchestrator and
document-rendering implementation details.  This module exposes a clean,
public interface so that ``main.py`` only depends on abstractions, not on
private helpers.

Usage::

    from src.documentation_service import DocumentationService

    doc = DocumentationService()
    await doc.generate_release_files(release, categories, generator, translator, ...)
    doc.update_readme_single(release, categories)
    await doc.update_readme_all()
"""

from __future__ import annotations

import logging
from typing import Any

from .config import RELEASES_DIR, ReleaseInfo
from .parser import FeatureImpactCategory
from .release_docs import (
    _generate_release_files,
    _format_impact_report,
    _format_notification_digest,
    _update_badge,
    _update_readme_single,
    update_readme_all as _update_readme_all,
)
from .feature_enricher import CategoryEnrichment

logger = logging.getLogger(__name__)


class DocumentationService:
    """Public service for release-notes documentation generation and updates.

    Wraps the private helpers in ``release_docs.py`` so callers depend on a
    stable public interface rather than implementation details.
    """

    def __init__(self, releases_dir: str = RELEASES_DIR) -> None:
        self._releases_dir = releases_dir

    # ------------------------------------------------------------------
    # Release file generation
    # ------------------------------------------------------------------

    async def generate_release_files(
        self,
        release: ReleaseInfo,
        categories: list[FeatureImpactCategory],
        generator: Any,
        translator: Any,
        locale: str = "pt_BR",
        enrichments: dict[str, CategoryEnrichment] | None = None,
    ) -> list[str]:
        """Generate per-category Markdown files for a release in a locale.

        Delegates to ``release_docs._generate_release_files``.
        """
        paths = await _generate_release_files(
            release,
            categories,
            generator,
            translator,
            locale=locale,
            enrichments=enrichments,
        )
        return [str(p) for p in paths]

    # ------------------------------------------------------------------
    # README updates
    # ------------------------------------------------------------------

    def update_readme_single(
        self,
        release: ReleaseInfo,
        categories: list[FeatureImpactCategory],
    ) -> None:
        """Write per-category metadata and update the single-release README.

        Delegates to ``release_docs._update_readme_single``.
        """
        _update_readme_single(release, categories)

    async def update_readme_all(self) -> None:
        """Generate bilingual README files (pt_BR and en_US) with release sections.

        Delegates to ``release_docs.update_readme_all``.
        """
        await _update_readme_all()

    # ------------------------------------------------------------------
    # Badge management
    # ------------------------------------------------------------------

    def update_badge(self, releases_to_process: list[ReleaseInfo]) -> None:
        """Update the dynamic release badge in README.md.

        Delegates to ``release_docs._update_badge``.
        """
        _update_badge(releases_to_process)

    # ------------------------------------------------------------------
    # Report formatting
    # ------------------------------------------------------------------

    def format_impact_report(self, report: Any, release_name: str) -> str:
        """Format an ImpactReport into Markdown.

        Delegates to ``release_docs._format_impact_report``.
        """
        return _format_impact_report(report, release_name)

    def format_notification_digest(self, digest: Any) -> str:
        """Format a NotificationDigest into Markdown.

        Delegates to ``release_docs._format_notification_digest``.
        """
        return _format_notification_digest(digest)
