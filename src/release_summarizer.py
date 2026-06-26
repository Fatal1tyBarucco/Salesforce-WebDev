"""AI-powered release summarizer.

Generates intelligent executive summaries from release notes files using a resilient LLM service.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

from .config import RELEASES_DIR
from .llm_service import LLMService


@dataclass
class ReleaseSummary:
    """Generated summary for a release."""

    release_slug: str
    release_name: str
    total_features: int
    top_categories: list[tuple[str, int]]
    key_highlights: list[str]
    summary_text: str
    confidence: float


class ReleaseSummarizer:
    """Generates executive summaries from release markdown files using LLM."""

    def __init__(self, base_dir: str = RELEASES_DIR) -> None:
        self._base_dir = Path(base_dir)
        self._llm = LLMService()

    async def summarize(self, release_slug: str) -> ReleaseSummary | None:
        """Generate a summary for a release using an LLM.

        Args:
            release_slug: The release directory name (e.g., 'summer_26').

        Returns:
            ReleaseSummary or None if release not found.
        """
        release_dir = self._base_dir / release_slug
        if not release_dir.is_dir():
            return None

        meta = self._load_meta(release_dir)
        content_fragments: list[str] = []
        category_counts: dict[str, int] = {}

        # Look for .md files in pt_BR subdirectory
        pt_br_dir = release_dir / "pt_BR"
        if pt_br_dir.is_dir():
            for md_file in sorted(pt_br_dir.glob("*.md")):
                if md_file.name.startswith("."):
                    continue
                content = md_file.read_text(encoding="utf-8")

                # Extract category name and count features for metadata
                category_name = self._extract_category_name(content, md_file.stem)
                category_counts[category_name] = self._count_features(content)

                # Only keep a fragment of content for the LLM to avoid token limits
                content_fragments.append(f"Category {category_name}:\n{content[:2000]}")

        if not content_fragments:
            return None

        # Construct a comprehensive prompt for the LLM
        full_content = "\n\n---\n\n".join(content_fragments)
        system_prompt = (
            "You are an expert technical writer. Summarize the following Salesforce release notes. "
            "Provide a concise, one-sentence executive summary in Portuguese (pt-BR) a highlighting "
            "the most impactful changes. Focus on value and business impact."
        )
        user_prompt = f"Release: {release_slug}\n\nContent:\n{full_content}"

        summary_text = await self._llm.generate_text(user_prompt, system_prompt)

        if not summary_text or summary_text == "Not Found" or "error" in summary_text.lower():
            # Generate a rich fallback summary based on metadata
            top_cats = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            total = sum(category_counts.values())
            
            highlights = []
            for cat_name, count in top_cats:
                highlights.append(f"**{cat_name}** ({count} recursos)")
            
            if total > 1000:
                scale = "maior"
            elif total > 500:
                scale = "significativa"
            else:
                scale = "moderada"
            
            summary_text = (
                f"A release {meta.get('name', release_slug)} apresenta uma {scale} atualização "
                f"com **{total} recursos** distribuídos em **{len(category_counts)} categorias**. "
                f"Destaques: {', '.join(highlights)}. "
                f"Explore cada categoria para detalhes completos sobre as novidades."
            )

        top_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        total_features = sum(category_counts.values())

        return ReleaseSummary(
            release_slug=release_slug,
            release_name=meta.get("release_name", release_slug),
            total_features=total_features,
            top_categories=top_categories,
            key_highlights=[],  # LLM could be expanded to provide these as a list
            summary_text=summary_text,
            confidence=1.0 if summary_text else 0.0,
        )

    def _load_meta(self, release_dir: Path) -> dict[str, Any]:
        """Load .meta.json if it exists."""
        meta_file = release_dir / ".meta.json"
        if meta_file.exists():
            try:
                return cast(dict[str, Any], json.loads(meta_file.read_text(encoding="utf-8")))
            except json.JSONDecodeError, OSError:
                pass

        return {}

    def _extract_category_name(self, content: str, fallback: str) -> str:
        """Extract category name from markdown heading."""
        for line in content.split("\n"):
            line = line.strip()
            if line.startswith("## ") and not line.startswith("## 🔗"):
                return line[3:].strip()
            if line.startswith("# ") and "Release" not in line:
                return line[2:].strip()
        return fallback.replace("_", " ").title()

    def _count_features(self, content: str) -> int:
        """Count feature entries in markdown."""
        count = 0
        for line in content.split("\n"):
            line = line.strip()
            if line.startswith("- ") or line.startswith("* "):
                count += 1
            elif "|" in line and "RECURSO" not in line and "---" not in line:
                parts = [p.strip() for p in line.split("|") if p.strip()]
                if len(parts) >= 2:
                    count += 1
        return count
