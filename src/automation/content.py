"""Content deduplication and hashing.

Uses CacheManager for unified cache storage with content-hash support.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Optional

from ..cache_manager import CacheManager
from .models import ContentHash, DeduplicationResult


def _get_releases_dir() -> Path:
    """Return the releases directory path."""
    from ..config import RELEASES_DIR

    return Path(RELEASES_DIR)


def _get_cache_manager() -> CacheManager:
    """Return a CacheManager instance for content caching."""
    return CacheManager(cache_dir=_get_releases_dir(), ttl_seconds=86400 * 30)


def calculate_file_hash(file_path: Path) -> ContentHash:
    """Calculate MD5 hash and metadata for a file.

    Args:
        file_path: Path to the file.

    Returns:
        ContentHash with hash, size, and modification time.
    """
    content = file_path.read_bytes()
    content_hash = hashlib.md5(content).hexdigest()
    stat = file_path.stat()
    return ContentHash(
        file_path=str(file_path),
        content_hash=content_hash,
        size_bytes=stat.st_size,
        last_modified=stat.st_mtime,
    )


def load_content_cache(cache_path: Path) -> dict[str, ContentHash]:
    """Load content cache from file, returning ContentHash objects.

    Args:
        cache_path: Path to the cache JSON file.

    Returns:
        Dictionary mapping file paths to ContentHash objects.
    """
    cache_manager = _get_cache_manager()
    raw_cache = cache_manager.load_content_cache(cache_path)

    # Convert string hashes back to ContentHash objects for backward compatibility
    result: dict[str, ContentHash] = {}
    for file_path, content_hash in raw_cache.items():
        if content_hash:  # Skip empty hashes from migration
            path = Path(file_path)
            if path.exists():
                stat = path.stat()
                result[file_path] = ContentHash(
                    file_path=file_path,
                    content_hash=content_hash,
                    size_bytes=stat.st_size,
                    last_modified=stat.st_mtime,
                )
            else:
                result[file_path] = ContentHash(
                    file_path=file_path,
                    content_hash=content_hash,
                    size_bytes=0,
                    last_modified=0.0,
                )
    return result


def save_content_cache(cache_path: Path, cache: dict[str, ContentHash]) -> None:
    """Save content cache to file using CacheManager.

    Args:
        cache_path: Path to the cache JSON file.
        cache: Dictionary mapping file paths to ContentHash objects.
    """
    cache_manager = _get_cache_manager()
    # Convert ContentHash objects to simple hash strings
    simple_cache = {k: v.content_hash for k, v in cache.items()}
    cache_manager.save_content_cache(cache_path, simple_cache)


async def analyze_content_changes(release_slug: str) -> DeduplicationResult:
    """Analyze content changes in a release directory.

    Args:
        release_slug: The release slug to analyze.

    Returns:
        DeduplicationResult with unchanged, changed, new, and removed files.
    """
    release_dir = _get_releases_dir() / release_slug
    cache_path = release_dir / ".content_cache.json"

    if not release_dir.exists():
        return DeduplicationResult([], [], [], [], 0, 0.0)

    current_hashes: dict[str, ContentHash] = {}
    for file_path in release_dir.iterdir():
        if file_path.is_file() and file_path.suffix == ".md":
            current_hashes[str(file_path)] = calculate_file_hash(file_path)

    cached_hashes = load_content_cache(cache_path)
    unchanged, changed, new, savings = [], [], [], 0

    for path, current in current_hashes.items():
        if path in cached_hashes:
            if current.content_hash == cached_hashes[path].content_hash:
                unchanged.append(path)
                savings += current.size_bytes
            else:
                changed.append(path)
        else:
            new.append(path)

    removed = [path for path in cached_hashes if path not in current_hashes]
    total = len(current_hashes)
    hit_rate = len(unchanged) / total if total > 0 else 0.0

    save_content_cache(cache_path, current_hashes)

    return DeduplicationResult(
        unchanged_files=unchanged,
        changed_files=changed,
        new_files=new,
        removed_files=removed,
        total_savings_bytes=savings,
        cache_hit_rate=round(hit_rate, 2),
    )


async def get_content_hash(file_path: str) -> Optional[str]:
    """Get the MD5 hash of a file's content.

    Args:
        file_path: Path to the file as string.

    Returns:
        MD5 hex digest if file exists, ``None`` otherwise.
    """
    path = Path(file_path)
    if not path.exists():
        return None
    content = path.read_bytes()
    return hashlib.md5(content).hexdigest()


async def is_content_unchanged(file_path: str, expected_hash: str) -> bool:
    """Check if a file's content matches the expected hash.

    Args:
        file_path: Path to the file as string.
        expected_hash: Expected MD5 hex digest.

    Returns:
        ``True`` if file exists and hash matches.
    """
    current_hash = await get_content_hash(file_path)
    return current_hash == expected_hash if current_hash else False


async def generate_deduplication_report(release_slug: str) -> str:
    """Generate a formatted deduplication report in Markdown.

    Args:
        release_slug: The release slug to report on.

    Returns:
        Markdown formatted deduplication report.
    """
    result = await analyze_content_changes(release_slug)

    lines = [
        "# Relatório de Deduplicação de Conteúdo\n",
        f"## Release: {release_slug}\n",
        f"**Taxa de acerto do cache:** {result.cache_hit_rate:.0%}\n",
        f"**Economia total:** {result.total_savings_bytes:,} bytes\n",
    ]

    if result.unchanged_files:
        lines.append(f"## ✅ Arquivos Inalterados ({len(result.unchanged_files)})\n")
        for file_path in result.unchanged_files:
            lines.append(f"- `{Path(file_path).name}`")
        lines.append("")

    if result.changed_files:
        lines.append(f"## 🔄 Arquivos Alterados ({len(result.changed_files)})\n")
        for file_path in result.changed_files:
            lines.append(f"- `{Path(file_path).name}`")
        lines.append("")

    if result.new_files:
        lines.append(f"## 🆕 Arquivos Novos ({len(result.new_files)})\n")
        for file_path in result.new_files:
            lines.append(f"- `{Path(file_path).name}`")
        lines.append("")

    if result.removed_files:
        lines.append(f"## 🗑️ Arquivos Removidos ({len(result.removed_files)})\n")
        for file_path in result.removed_files:
            lines.append(f"- `{Path(file_path).name}`")
        lines.append("")

    lines.extend(["---", "*Relatório gerado automaticamente pelo módulo de AI Automation*"])
    return "\n".join(lines)
