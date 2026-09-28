"""Heuristic fallback for dependency graph building when LLM is unavailable.

Uses rule-based analysis of release notes metadata and markdown files to
construct a basic dependency graph without LLM calls.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.config import RELEASES_DIR
from .models import DependencyEdge, DependencyGraphResponse

logger = logging.getLogger(__name__)


class DependencyHeuristicFallback:
    """Fallback mechanism when LLM is unavailable or rate-limited."""

    def build(self, release_slug: str) -> DependencyGraphResponse:
        release_dir = Path(RELEASES_DIR) / release_slug
        meta_path = release_dir / ".meta.json"
        meta: dict[str, Any] = {}
        if meta_path.exists():
            try:
                meta = json.loads(meta_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                pass

        features = self._extract_feature_names(release_dir, meta)
        if not features:
            return DependencyGraphResponse(
                release_slug=release_slug,
                nodes=[],
                edges=[],
                graph_statistics={"nodes": 0, "edges": 0},
                generated_at="",
                source="heuristic",
            )

        edges: list[DependencyEdge] = []
        for feature_name in features:
            if self._has_api_dependency(feature_name):
                edges.append(
                    DependencyEdge(
                        source_feature=feature_name,
                        target_feature=feature_name,
                        dependency_type="api",
                        confidence=1.0,
                        evidence="",
                    )
                )

        return DependencyGraphResponse(
            release_slug=release_slug,
            nodes=features,
            edges=edges,
            graph_statistics={"nodes": len(features), "edges": len(edges)},
            generated_at=datetime.now(timezone.utc).isoformat(),
            source="heuristic",
        )

    def _extract_feature_names(self, release_dir: Path, meta: dict[str, Any]) -> list[str]:
        features: list[str] = []

        # Tenta extrair de categorias no meta
        for cat in meta.get("categories", []):
            name = cat.get("name", "")
            if isinstance(name, str) and name and not name.startswith("##"):
                slug = name.replace(" ", "_").lower()
                if slug not in features:
                    features.append(slug)

        # Se não há categorias, tenta extrair de arquivos markdown
        if not features:
            for md_file in sorted(release_dir.glob("*.md")):
                if md_file.name.startswith("."):
                    continue
                try:
                    content = md_file.read_text(encoding="utf-8")
                    features.extend(self._extract_features_from_markdown(content))
                except OSError:
                    continue

        return list(dict.fromkeys(features))

    def _extract_features_from_markdown(self, content: str) -> list[str]:
        features: list[str] = []
        in_table = False
        for line in content.splitlines():
            stripped = line.strip()
            if stripped.startswith("| Recurso") or stripped.startswith("| Feature"):
                in_table = True
                continue
            if in_table and (stripped.startswith("|--") or stripped.startswith("---")):
                in_table = False
                continue
            if in_table and stripped.startswith("|"):
                cells = [c.strip() for c in stripped.split("|")]
                if len(cells) >= 2:
                    name = cells[0].strip()
                    name = name.replace("**", "").replace("*", "").strip()
                    if name and name not in {"Feature", "Recurso"}:
                        features.append(name)
        return features

    def _has_api_dependency(self, feature_name: str) -> bool:
        """Verifica se há evidência de dependência de API no nome da feature."""
        if not feature_name:
            return False
        name_lower = feature_name.lower()
        indicators = ["api", "endpoint", "rest", "http", "https", "get", "post", "put", "delete"]
        return any(indicator in name_lower for indicator in indicators)
