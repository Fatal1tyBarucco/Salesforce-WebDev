"""AI-powered natural language search for release notes.

Indexes release content and allows searching with natural language queries,
returning ranked results with relevance scores.
"""

from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

from .config import RELEASES_DIR

# Stopwords for query processing
STOPWORDS: frozenset[str] = frozenset(
    {
        "a",
        "an",
        "the",
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
        "i",
        "me",
        "my",
        "we",
        "our",
        "you",
        "your",
        "he",
        "she",
        "they",
        "them",
        "what",
        "which",
        "who",
        "whom",
        "how",
        "when",
        "where",
        "why",
        "all",
        "each",
        "every",
        "both",
        "few",
        "more",
        "most",
        "other",
        "some",
        "such",
        "no",
        "nor",
        "not",
        "only",
        "own",
        "same",
        "so",
        "than",
        "too",
        "very",
        "just",
        "because",
        "as",
        "until",
        "while",
        "about",
        "between",
        "through",
        "during",
        "before",
        "after",
        "above",
        "below",
        "up",
        "down",
        "out",
        "off",
        "over",
        "under",
        "again",
        "further",
        "then",
        "once",
        # Portuguese stopwords
        "o",
        "a",
        "os",
        "as",
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
        "esse",
        "essa",
        "eu",
        "tu",
        "ele",
        "ela",
        "nós",
        "vocês",
        "eles",
        "elas",
        "foi",
        "ser",
        "ter",
        "estar",
        "poder",
        "dever",
        "fazer",
    }
)


@dataclass
class SearchResult:
    """A single search result."""

    release_slug: str
    file_name: str
    category: str
    text_snippet: str
    relevance_score: float
    matched_terms: list[str]


@dataclass
class SearchResults:
    """Aggregated search results."""

    query: str
    total_results: int
    results: list[SearchResult]
    search_time_ms: float


@dataclass
class _IndexedDocument:
    """Internal indexed document."""

    release_slug: str
    file_name: str
    category: str
    content: str
    terms: dict[str, int] = field(default_factory=dict)
    term_count: int = 0


class NLSearchEngine:
    """Natural language search engine for release notes."""

    def __init__(self, base_dir: str = RELEASES_DIR) -> None:
        self._base_dir = Path(base_dir)
        self._documents: list[_IndexedDocument] = []
        self._idf: dict[str, float] = {}

    def index_release(self, release_slug: str) -> int:
        """Index a release's content for searching.

        Args:
            release_slug: The release directory name.

        Returns:
            Number of documents indexed.
        """
        release_dir = self._base_dir / release_slug
        if not release_dir.is_dir():
            return 0

        count = 0
        for md_file in sorted(release_dir.glob("*.md")):
            if md_file.name.startswith("."):
                continue

            content = md_file.read_text(encoding="utf-8")
            category = self._extract_category(content, md_file.stem)
            terms = self._tokenize(content)

            doc = _IndexedDocument(
                release_slug=release_slug,
                file_name=md_file.name,
                category=category,
                content=content,
                terms=terms,
                term_count=sum(terms.values()),
            )
            self._documents.append(doc)
            count += 1

        # Rebuild IDF after indexing
        self._build_idf()
        return count

    def index_all(self) -> int:
        """Index all releases.

        Returns:
            Total number of documents indexed.
        """
        total = 0
        for release_dir in sorted(self._base_dir.iterdir()):
            if release_dir.is_dir():
                total += self.index_release(release_dir.name)
        return total

    def search(self, query: str, max_results: int = 10) -> SearchResults:
        """Search indexed content with a natural language query.

        Args:
            query: Natural language search query.
            max_results: Maximum number of results to return.

        Returns:
            SearchResults with ranked results.
        """
        import time

        start_time = time.time()

        query_terms = self._tokenize_query(query)
        if not query_terms:
            return SearchResults(
                query=query,
                total_results=0,
                results=[],
                search_time_ms=0.0,
            )

        # Score each document
        scored: list[tuple[_IndexedDocument, float, list[str]]] = []
        for doc in self._documents:
            score, matched = self._score_document(doc, query_terms)
            if score > 0:
                scored.append((doc, score, matched))

        # Sort by score descending
        scored.sort(key=lambda x: x[1], reverse=True)

        # Build results
        results: list[SearchResult] = []
        for doc, score, matched in scored[:max_results]:
            snippet = self._extract_snippet(doc.content, query_terms)
            results.append(
                SearchResult(
                    release_slug=doc.release_slug,
                    file_name=doc.file_name,
                    category=doc.category,
                    text_snippet=snippet,
                    relevance_score=score,
                    matched_terms=matched,
                )
            )

        search_time = (time.time() - start_time) * 1000

        return SearchResults(
            query=query,
            total_results=len(results),
            results=results,
            search_time_ms=search_time,
        )

    def _extract_category(self, content: str, fallback: str) -> str:
        """Extract category from markdown heading."""
        h2_category = None
        for line in content.split("\n"):
            line = line.strip()
            if line.startswith("## ") and not line.startswith("## 🔗"):
                h2_category = line[3:].strip()
                break
            if line.startswith("# ") and "Release" not in line and h2_category is None:
                h2_category = line[2:].strip()
        return h2_category or fallback.replace("_", " ").title()

    def _tokenize(self, text: str) -> dict[str, int]:
        """Tokenize text into term frequencies."""
        text = text.lower()
        text = re.sub(r"[^a-záàâãéèêíïóôõúüç\s]", " ", text)
        terms: Counter[str] = Counter()
        for word in text.split():
            if len(word) > 2 and word not in STOPWORDS:
                terms[word] += 1
        return dict(terms)

    def _tokenize_query(self, query: str) -> set[str]:
        """Tokenize query into meaningful terms."""
        query = query.lower()
        query = re.sub(r"[^a-záàâãéèêíïóôõúüç\s]", " ", query)
        return {w for w in query.split() if len(w) > 2 and w not in STOPWORDS}

    def _build_idf(self) -> None:
        """Build inverse document frequency scores."""
        n_docs = len(self._documents)
        if n_docs == 0:
            return

        doc_freq: Counter[str] = Counter()
        for doc in self._documents:
            for term in doc.terms:
                doc_freq[term] += 1

        self._idf = {}
        for term, freq in doc_freq.items():
            self._idf[term] = math.log(n_docs / (1 + freq))

    def _score_document(
        self, doc: _IndexedDocument, query_terms: set[str]
    ) -> tuple[float, list[str]]:
        """Score a document against query terms using TF-IDF."""
        if doc.term_count == 0:
            return 0.0, []

        score = 0.0
        matched: list[str] = []

        for term in query_terms:
            if term in doc.terms:
                tf = doc.terms[term] / doc.term_count
                idf = self._idf.get(term, 1.0)
                # Ensure IDF is positive for scoring
                idf = max(0.1, idf)
                score += tf * idf
                matched.append(term)

        # Boost for exact category match
        for term in query_terms:
            if term in doc.category.lower():
                score *= 1.2

        return score, matched

    def _extract_snippet(
        self, content: str, query_terms: set[str], context_chars: int = 100
    ) -> str:
        """Extract a relevant snippet from content."""
        content_lower = content.lower()

        # Find first occurrence of any query term
        best_pos = -1
        for term in query_terms:
            pos = content_lower.find(term)
            if pos != -1 and (best_pos == -1 or pos < best_pos):
                best_pos = pos

        if best_pos == -1:
            # Return first N characters
            return content[:200].strip() + "..."

        # Extract context around the match
        start = max(0, best_pos - context_chars)
        end = min(len(content), best_pos + context_chars)

        snippet = content[start:end].strip()
        if start > 0:
            snippet = "..." + snippet
        if end < len(content):
            snippet = snippet + "..."

        return snippet
