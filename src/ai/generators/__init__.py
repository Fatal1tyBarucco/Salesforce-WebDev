"""Visual Markdown generators for reports and dashboards."""

from .badges import (
    Badge,
    api_version_badge,
    category_badge,
    category_header_badges,
    feature_count_badge,
    impact_badge,
    release_badge,
    release_meta_badges,
    status_badge,
)
from .code import (
    CodeSnippet,
    build_code_generation_prompt,
    generate_code_section,
    generate_template_snippet,
    parse_code_response,
)
from .markdown import MarkdownGenerator

__all__ = [
    "Badge",
    "CodeSnippet",
    "MarkdownGenerator",
    "api_version_badge",
    "build_code_generation_prompt",
    "category_badge",
    "category_header_badges",
    "feature_count_badge",
    "generate_code_section",
    "generate_template_snippet",
    "impact_badge",
    "parse_code_response",
    "release_badge",
    "release_meta_badges",
    "status_badge",
]
