"""Storage infrastructure — filesystem and GitHub storage adapters.

Implements the StorageAdapter contract for persisting release data.
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any

from src.models.enrichment import ReleaseEnrichment
from src.models.release import ReleaseMetadata

logger = logging.getLogger(__name__)


class StorageAdapter:
    """Abstract storage adapter interface."""

    async def save_release_metadata(self, release: ReleaseMetadata) -> None:
        raise NotImplementedError

    async def load_release_metadata(self, slug: str) -> ReleaseMetadata | None:
        raise NotImplementedError

    async def save_enrichment(self, enrichment: ReleaseEnrichment) -> None:
        raise NotImplementedError

    async def load_enrichment(self, slug: str) -> ReleaseEnrichment | None:
        raise NotImplementedError

    async def save_markdown(self, slug: str, category: str, content: str, locale: str) -> str:
        raise NotImplementedError

    async def load_markdown(self, slug: str, category: str, locale: str) -> str | None:
        raise NotImplementedError

    async def list_releases(self) -> list[str]:
        raise NotImplementedError


class FileSystemStorageAdapter(StorageAdapter):
    """Filesystem-based storage implementation.

    Stores release data in a directory structure:
    releases/
      {slug}/
        .meta.json          # ReleaseMetadata
        .enrichment.json    # ReleaseEnrichment
        {category}.pt_BR.md # Markdown files
        {category}.en_US.md
    """

    def __init__(self, base_dir: str = "releases") -> None:
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _release_dir(self, slug: str) -> Path:
        return self.base_dir / slug

    def _meta_path(self, slug: str) -> Path:
        return self._release_dir(slug) / ".meta.json"

    def _enrichment_path(self, slug: str) -> Path:
        return self._release_dir(slug) / ".enrichment.json"

    def _markdown_path(self, slug: str, category: str, locale: str) -> Path:
        safe_category = category.replace(" ", "_").replace("/", "_")
        return self._release_dir(slug) / f"{safe_category}.{locale}.md"

    async def save_release_metadata(self, release: ReleaseMetadata) -> None:
        """Save release metadata to .meta.json."""
        release_dir = self._release_dir(release.slug)
        release_dir.mkdir(parents=True, exist_ok=True)

        meta_path = self._meta_path(release.slug)
        data = release.to_dict()
        meta_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        logger.info("Saved metadata for %s", release.slug)

    async def load_release_metadata(self, slug: str) -> ReleaseMetadata | None:
        """Load release metadata from .meta.json."""
        meta_path = self._meta_path(slug)
        if not meta_path.exists():
            return None

        try:
            data = json.loads(meta_path.read_text(encoding="utf-8"))
            return ReleaseMetadata.from_dict(data)
        except Exception as e:
            logger.error("Failed to load metadata for %s: %s", slug, e)
            return None

    async def save_enrichment(self, enrichment: ReleaseEnrichment) -> None:
        """Save enrichment to .enrichment.json."""
        enrichment_path = self._enrichment_path(enrichment.release_slug)
        enrichment_path.parent.mkdir(parents=True, exist_ok=True)

        data = enrichment.to_dict()
        enrichment_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        logger.info("Saved enrichment for %s", enrichment.release_slug)

    async def load_enrichment(self, slug: str) -> ReleaseEnrichment | None:
        """Load enrichment from .enrichment.json."""
        enrichment_path = self._enrichment_path(slug)
        if not enrichment_path.exists():
            return None

        try:
            data = json.loads(enrichment_path.read_text(encoding="utf-8"))
            return ReleaseEnrichment.from_dict(data)
        except Exception as e:
            logger.error("Failed to load enrichment for %s: %s", slug, e)
            return None

    async def save_markdown(self, slug: str, category: str, content: str, locale: str) -> str:
        """Save markdown file for a category."""
        md_path = self._markdown_path(slug, category, locale)
        md_path.parent.mkdir(parents=True, exist_ok=True)
        md_path.write_text(content, encoding="utf-8")
        logger.info("Saved markdown: %s", md_path)
        return str(md_path)

    async def load_markdown(self, slug: str, category: str, locale: str) -> str | None:
        """Load markdown file for a category."""
        md_path = self._markdown_path(slug, category, locale)
        if not md_path.exists():
            return None
        return md_path.read_text(encoding="utf-8")

    async def list_releases(self) -> list[str]:
        """List all release slugs."""
        if not self.base_dir.exists():
            return []

        slugs = []
        for entry in self.base_dir.iterdir():
            if entry.is_dir() and (entry / ".meta.json").exists():
                slugs.append(entry.name)

        return sorted(slugs)

    async def delete_release(self, slug: str) -> bool:
        """Delete a release directory."""
        import shutil

        release_dir = self._release_dir(slug)
        if not release_dir.exists():
            return False

        try:
            shutil.rmtree(release_dir)
            logger.info("Deleted release: %s", slug)
            return True
        except Exception as e:
            logger.error("Failed to delete release %s: %s", slug, e)
            return False


class GitHubStorageAdapter(StorageAdapter):
    """GitHub-based storage using GitHub API (for production)."""

    def __init__(
        self,
        repo: str,
        token: str | None = None,
        branch: str = "main",
        base_path: str = "releases",
    ) -> None:
        self.repo = repo
        self.token = token or os.getenv("GITHUB_TOKEN")
        self.branch = branch
        self.base_path = base_path
        self._client: Any = None

    def _get_client(self) -> Any:
        if self._client is None:
            from github import Github

            self._client = Github(self.token) if self.token else Github()
        return self._client

    async def save_release_metadata(self, release: ReleaseMetadata) -> None:
        """Save metadata to GitHub."""
        # Implementation would use GitHub Contents API
        raise NotImplementedError("GitHub storage not fully implemented")

    async def load_release_metadata(self, slug: str) -> ReleaseMetadata | None:
        raise NotImplementedError

    async def save_enrichment(self, enrichment: ReleaseEnrichment) -> None:
        raise NotImplementedError

    async def load_enrichment(self, slug: str) -> ReleaseEnrichment | None:
        raise NotImplementedError

    async def save_markdown(self, slug: str, category: str, content: str, locale: str) -> str:
        raise NotImplementedError

    async def list_releases(self) -> list[str]:
        raise NotImplementedError
