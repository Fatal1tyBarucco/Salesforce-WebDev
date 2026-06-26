"""AI-powered release summarizer.

Generates intelligent executive summaries from release notes files.
Uses NLP-inspired text analysis (TF-IDF, keyword extraction, sentence scoring)
without external dependencies — pure stdlib implementation.
"""

from __future__ import annotations

import json
import math
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .config import RELEASES_DIR

# ---------------------------------------------------------------------------
# Stopwords for Portuguese and English
# ---------------------------------------------------------------------------

STOPWORDS: frozenset[str] = frozenset(
    {
        # Portuguese
        "a",
        "as",
        "o",
        "os",
        "um",
        "uma",
        "de",
        "do",
        "da",
        "dos",
        "das",
        "em",
        "no",
        "na",
        "nos",
        "nas",
        "por",
        "para",
        "com",
        "sem",
        "sob",
        "sobre",
        "entre",
        "até",
        "desde",
        "durante",
        "antes",
        "após",
        "e",
        "ou",
        "mas",
        "que",
        "se",
        "não",
        "mais",
        "muito",
        "já",
        "este",
        "esta",
        "estes",
        "estas",
        "esse",
        "essa",
        "esses",
        "essas",
        "aquele",
        "aquela",
        "aqueles",
        "aquelas",
        "isto",
        "isso",
        "aquilo",
        "eu",
        "tu",
        "ele",
        "ela",
        "nós",
        "vocês",
        "eles",
        "elas",
        "meu",
        "minha",
        "teu",
        "tua",
        "seu",
        "sua",
        "nosso",
        "nossa",
        "foi",
        "ser",
        "ter",
        "estar",
        "poder",
        "dever",
        "fazer",
        # English
        "the",
        "a",
        "an",
        "and",
        "or",
        "but",
        "in",
        "on",
        "at",
        "to",
        "for",
        "of",
        "with",
        "by",
        "from",
        "is",
        "are",
        "was",
        "were",
        "be",
        "been",
        "being",
        "have",
        "has",
        "had",
        "do",
        "does",
        "did",
        "will",
        "would",
        "could",
        "should",
        "may",
        "might",
        "can",
        "shall",
        "this",
        "that",
        "these",
        "those",
        "it",
        "its",
        "they",
        "them",
        # Common release words (low info)
        "feature",
        "release",
        "update",
        "new",
        "version",
        "salesforce",
        "release",
        "notes",
        "summer",
        "winter",
        "spring",
    }
)

# High-value category keywords (boosted in summaries)
CATEGORY_KEYWORDS: frozenset[str] = frozenset(
    {
        "security",
        "segurança",
        "performance",
        "breaking",
        "migration",
        "deprecation",
        "deprecated",
        "new feature",
        "improvement",
        "bug fix",
        "correção",
        "automação",
        "flow",
        "api",
        "lightning",
        "agentforce",
        "data cloud",
        "einstein",
        "mulesoft",
        "slack",
    }
)


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


@dataclass
class _SentenceScore:
    """Internal scoring for a sentence."""

    text: str
    score: float
    position: int


class ReleaseSummarizer:
    """Generates executive summaries from release markdown files."""

    def __init__(self, base_dir: str = RELEASES_DIR) -> None:
        self._base_dir = Path(base_dir)

    def summarize(self, release_slug: str) -> ReleaseSummary | None:
        """Generate a summary for a release.

        Args:
            release_slug: The release directory name (e.g., 'summer_26').

        Returns:
            ReleaseSummary or None if release not found.
        """
        release_dir = self._base_dir / release_slug
        if not release_dir.is_dir():
            return None

        meta = self._load_meta(release_dir)
        all_sentences: list[str] = []
        category_counts: dict[str, int] = {}

        for md_file in sorted(release_dir.glob("*.md")):
            if md_file.name.startswith("."):
                continue
            content = md_file.read_text(encoding="utf-8")
            category_name = self._extract_category_name(content, md_file.stem)
            sentences = self._extract_sentences(content)
            all_sentences.extend(sentences)

            feature_count = self._count_features(content)
            if category_name:
                category_counts[category_name] = feature_count

        if not all_sentences:
            return None

        # Score and rank sentences
        scored = self._score_sentences(all_sentences)

        # Build summary
        top_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        highlights = [s.text for s in scored[:5]]
        total_features = sum(category_counts.values())

        # Generate executive summary text
        summary_text = self._build_summary_text(
            release_slug, total_features, top_categories, highlights
        )

        return ReleaseSummary(
            release_slug=release_slug,
            release_name=meta.get("release_name", release_slug),
            total_features=total_features,
            top_categories=top_categories,
            key_highlights=highlights,
            summary_text=summary_text,
            confidence=min(1.0, total_features / 100),
        )

    def _load_meta(self, release_dir: Path) -> dict[str, Any]:
        """Load .meta.json if it exists."""
        meta_file = release_dir / ".meta.json"
        if meta_file.exists():
            try:
                result: dict[str, Any] = json.loads(meta_file.read_text(encoding="utf-8"))
                return result
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

    def _extract_sentences(self, content: str) -> list[str]:
        """Extract meaningful sentences from markdown content."""
        sentences: list[str] = []
        for line in content.split("\n"):
            line = line.strip()
            # Skip headings, links, empty lines
            if not line or line.startswith("#") or line.startswith("[") or line.startswith("---"):
                continue
            if line.startswith(">"):
                line = line[1:].strip()
            # Split on sentence boundaries
            for sent in re.split(r"[.!?]+", line):
                sent = sent.strip()
                if len(sent) > 20 and not sent.startswith("|"):
                    sentences.append(sent)
        return sentences

    def _count_features(self, content: str) -> int:
        """Count feature entries in markdown."""
        count = 0
        for line in content.split("\n"):
            line = line.strip()
            if line.startswith("- ") or line.startswith("* "):
                count += 1
            elif "|" in line and "RECURSO" not in line and "---" not in line:
                # Table row
                parts = [p.strip() for p in line.split("|") if p.strip()]
                if len(parts) >= 2:
                    count += 1
        return count

    def _score_sentences(self, sentences: list[str]) -> list[_SentenceScore]:
        """Score sentences using TF-IDF-inspired scoring."""
        # Build document frequency
        doc_freq: Counter[str] = Counter()
        doc_sentences: list[set[str]] = []

        for sent in sentences:
            words = self._tokenize(sent)
            doc_sentences.append(words)
            for word in words:
                doc_freq[word] += 1

        n_docs = len(sentences)

        # Score each sentence
        scored: list[_SentenceScore] = []
        for i, (sent, words) in enumerate(zip(sentences, doc_sentences)):
            # TF-IDF score
            tf = Counter(words)
            score = 0.0
            for word, count in tf.items():
                tf_val = count / len(words)
                idf_val = math.log(n_docs / (1 + doc_freq.get(word, 0)))
                score += tf_val * idf_val

            # Boost for category keywords
            for word in words:
                if word in CATEGORY_KEYWORDS:
                    score *= 1.5

            # Position bonus (earlier sentences often more important)
            position_bonus = 1.0 / (1 + i * 0.1)
            score *= position_bonus

            # Length bonus (medium-length sentences preferred)
            word_count = len(words)
            if 5 <= word_count <= 20:
                score *= 1.2

            scored.append(_SentenceScore(text=sent, score=score, position=i))

        scored.sort(key=lambda s: s.score, reverse=True)
        return scored

    def _tokenize(self, text: str) -> set[str]:
        """Tokenize text into meaningful words."""
        text = text.lower()
        text = re.sub(r"[^a-záàâãéèêíïóôõúüç\s]", " ", text)
        words = set(text.split())
        return {w for w in words if len(w) > 2 and w not in STOPWORDS}

    def _build_summary_text(
        self,
        release_slug: str,
        total_features: int,
        top_categories: list[tuple[str, int]],
        highlights: list[str],
    ) -> str:
        """Build the final summary text."""
        name = release_slug.replace("_", " ").title()

        lines = [
            f"## 📊 Executive Summary: {name}",
            "",
            f"**{total_features}** features across **{len(top_categories)}** categories.",
            "",
            "### 🏆 Top Categories",
            "",
        ]

        for cat, count in top_categories:
            bar = "█" * min(count // 5, 20)
            lines.append(f"- **{cat}**: {count} features {bar}")

        lines.extend(["", "### 🔑 Key Highlights", ""])

        for i, highlight in enumerate(highlights[:5], 1):
            lines.append(f"{i}. {highlight}")

        lines.extend(
            [
                "",
                "---",
                f"*Auto-generated by ReleaseSummarizer from {total_features} feature entries.*",
            ]
        )

        return "\n".join(lines)
