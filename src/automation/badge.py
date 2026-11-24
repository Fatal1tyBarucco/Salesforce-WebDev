"""Stub badge module for backward compatibility."""

from __future__ import annotations


def generate_dynamic_badge(version: str, color: str = "blue") -> str:
    """Generate a dynamic badge."""
    return f"![{version}]({color})"


def get_latest_release_badge() -> str:
    """Get latest release badge."""
    return "![latest](blue)"


def generate_category_badges(categories: list[str]) -> str:
    """Generate category badges."""
    return " ".join(f"![{cat}](blue)" for cat in categories)


def generate_release_header_badges(version: str, date: str) -> str:
    """Generate release header badges."""
    return f"![{version}](blue) ![{date}](green)"
