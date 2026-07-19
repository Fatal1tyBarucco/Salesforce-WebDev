"""Content deduplication and hashing."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Optional

from .models import ContentHash, DeduplicationResult


def _get_releases_dir() -> Path:
    from ..config import RELEASES_DIR

    return Path(RELEASES_DIR)


def calculate_file_hash(file_path: Path) -> ContentHash:
    """Calculate MD5 hash of a file's content."""
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
    """Load content cache from file."""
    if not cache_path.exists():
        return {}
    try:
        data = json.loads(cache_path.read_text(encoding="utf-8"))
        return {k: ContentHash(**v) for k, v in data.items()}
    except (json.JSONDecodeError, TypeError):
        return {}


def save_content_cache(cache_path: Path, cache: dict[str, ContentHash]) -> None:
    """Save content cache to file."""
    data = {k: vars(v) for k, v in cache.items()}
    cache_path.write_text(json.dumps(data, indent=2), encoding="utf-8")


async def analyze_content_changes(release_slug: str) -> DeduplicationResult:
    """Analyze content changes in a release directory."""
    release_dir = _get_releases_dir() / release_slug
    cache_path = release_dir / ".content_cache.json"

    if not release_dir.exists():
        return DeduplicationResult([], [], [], [], 0, 0.0)

    current_hashes: dict[str, ContentHash] = {}
    for f in release_dir.iterdir():
        if f.is_file() and f.suffix == ".md":
            current_hashes[str(f)] = calculate_file_hash(f)

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
    """Get the MD5 hash of a file's content."""
    path = Path(file_path)
    if not path.exists():
        return None
    content = path.read_bytes()
    return hashlib.md5(content).hexdigest()


async def is_content_unchanged(file_path: str, expected_hash: str) -> bool:
    """Check if a file's content matches the expected hash."""
    current_hash = await get_content_hash(file_path)
    return current_hash == expected_hash if current_hash else False


async def generate_deduplication_report(release_slug: str) -> str:
    """Generate a formatted deduplication report in Markdown."""
    result = await analyze_content_changes(release_slug)

    lines = [
        "# Relatório de Deduplicação de Conteúdo\n",
        f"## Release: {release_slug}\n",
        f"**Taxa de acerto do cache:** {result.cache_hit_rate:.0%}\n",
        f"**Economia total:** {result.total_savings_bytes:,} bytes\n",
    ]

    if result.unchanged_files:
        lines.append(f"## ✅ Arquivos Inalterados ({len(result.unchanged_files)})\n")
        for f in result.unchanged_files:
            lines.append(f"- `{Path(f).name}`")
        lines.append("")

    if result.changed_files:
        lines.append(f"## 🔄 Arquivos Alterados ({len(result.changed_files)})\n")
        for f in result.changed_files:
            lines.append(f"- `{Path(f).name}`")
        lines.append("")

    if result.new_files:
        lines.append(f"## 🆕 Arquivos Novos ({len(result.new_files)})\n")
        for f in result.new_files:
            lines.append(f"- `{Path(f).name}`")
        lines.append("")

    if result.removed_files:
        lines.append(f"## 🗑️ Arquivos Removidos ({len(result.removed_files)})\n")
        for f in result.removed_files:
            lines.append(f"- `{Path(f).name}`")
        lines.append("")

    lines.extend(["---", "*Relatório gerado automaticamente pelo módulo de AI Automation*"])
    return "\n".join(lines)
