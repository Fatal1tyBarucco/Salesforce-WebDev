"""Tests for src/release_docs.py — 100% coverage target."""

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from src.config import ReleaseInfo, BILINGUAL_TEMPLATES


class TestBuildReleaseName:
    """_build_release_name: maps release IDs to seasonal names."""

    def test_fallback_for_unexpected_id(self) -> None:
        from src.release_docs import _build_release_name

        name = _build_release_name(200)
        assert "Spring" in name or "Summer" in name or "Winter" in name


class TestBuildReleaseSlug:
    """_build_release_slug: produces URL-safe slugs."""

    def test_slug_is_lowercase_with_underscore(self) -> None:
        from src.release_docs import _build_release_slug

        slug = _build_release_slug(262)
        assert "_" in slug
        assert slug.islower()


class TestFindExistingReleases:
    """_find_existing_releases: scans RELEASES_DIR for subdirs with .meta.json."""

    def test_empty_when_dir_missing(self, tmp_path: Path) -> None:
        from src.release_docs import _find_existing_releases

        with patch("src.release_docs.RELEASES_DIR", str(tmp_path / "nope")):
            assert _find_existing_releases() == set()

    def test_returns_slugs(self, tmp_path: Path) -> None:
        from src.release_docs import _find_existing_releases

        d = tmp_path / "summer_26"
        d.mkdir()
        (d / ".meta.json").write_text('{"name": "Summer 26"}')

        with patch("src.release_docs.RELEASES_DIR", str(tmp_path)):
            result = _find_existing_releases()
        assert "summer_26" in result


class TestSlugifyCategory:
    """_slugify_category: ASCII-safe slug generation."""

    def test_pt_br_lowercases_and_replaces_spaces(self) -> None:
        from src.release_docs import _slugify_category

        assert _slugify_category("Análise de dados") == "analise_de_dados"

    def test_ascii_passthrough(self) -> None:
        from src.release_docs import _slugify_category

        assert _slugify_category("Security") == "security"


class TestGetReleaseEmoji:
    """_get_release_emoji: maps season names to emoji."""

    def test_summer(self) -> None:
        from src.release_docs import _get_release_emoji

        assert "☀" in _get_release_emoji("Summer '26")

    def test_spring(self) -> None:
        from src.release_docs import _get_release_emoji

        assert "🌸" in _get_release_emoji("Spring '26")

    def test_winter(self) -> None:
        from src.release_docs import _get_release_emoji

        assert "❄" in _get_release_emoji("Winter '26")

    def test_unknown_defaults_to_spring(self) -> None:
        from src.release_docs import _get_release_emoji

        assert "🌸" in _get_release_emoji("Unknown '26")


class TestBuildResourceFooter:
    """_build_resource_footer: generates markdown link list."""

    def test_returns_non_empty_list(self) -> None:
        from src.release_docs import _build_resource_footer

        release = ReleaseInfo(name="Summer '26", release_id=262, slug="summer_26")
        templates = BILINGUAL_TEMPLATES.get("pt_BR", BILINGUAL_TEMPLATES["en_US"])
        footer = _build_resource_footer(release, templates, "pt_BR")
        assert isinstance(footer, list)
        assert len(footer) > 0


class TestDetectExistingReleaseChunk:
    """_detect_existing_release_chunk: preserves curated release blocks.

    Critical for ensuring that re-running the pipeline does not reformat
    the README — manual edits and AI-curated summaries must survive.
    """

    def test_finds_collapsed_block(self) -> None:
        from src.release_docs import _detect_existing_release_chunk

        text = (
            "## 📋 Releases Disponíveis\n\n"
            "<details>\n<summary><h3>☀️ Summer '26</h3></summary>\n\n"
            "> 📊 **Resumo Executivo:** Custom curated text.\n"
            "</details>\n"
        )
        chunk = _detect_existing_release_chunk(text, "Summer '26")
        assert chunk is not None
        assert "Custom curated text" in chunk
        assert "Summer '26" in chunk

    def test_finds_expanded_block(self) -> None:
        from src.release_docs import _detect_existing_release_chunk

        text = (
            "## 📋 Releases Disponíveis\n\n"
            "### 🌸 Spring '26\n\n"
            "> 📊 **Resumo Executivo:** Preserved intro.\n\n"
            "<details><summary>Category 1</summary></details>\n"
            "\n### Next\n"
        )
        chunk = _detect_existing_release_chunk(text, "Spring '26")
        assert chunk is not None
        assert "Spring '26" in chunk

    def test_returns_none_for_missing(self) -> None:
        from src.release_docs import _detect_existing_release_chunk

        text = "## 📋 Releases\n\n### Summer '26\n"
        assert _detect_existing_release_chunk(text, "Winter '27") is None

    def test_returns_none_for_invalid_name(self) -> None:
        from src.release_docs import _detect_existing_release_chunk

        assert _detect_existing_release_chunk("any text", "NotARelease") is None

    def test_returns_none_for_unknown_season(self) -> None:
        from src.release_docs import _detect_existing_release_chunk

        assert _detect_existing_release_chunk("any text", "Invalid'26") is None


class TestBuildReleaseBlockPreservesExisting:
    """_build_release_block with existing_text reuses curated chunks."""

    def test_preserves_curated_block(self) -> None:
        import asyncio

        from src.release_docs import _build_release_block, RELEASE_SECTION_HEADING

        curated = (
            "<details>\n<summary><h3>☀️ Summer '26</h3></summary>\n\n"
            "> 📊 **Resumo Executivo:** Curated intro that must be kept.\n"
            "</details>"
        )
        existing = f"{RELEASE_SECTION_HEADING}\n\n{curated}\n"

        metas = [{"name": "Summer '26", "slug": "summer_26", "release_id": 262, "categories": []}]

        class _StubSummarizer:
            async def summarize(self, slug: str):
                return None

        result = asyncio.run(
            _build_release_block(metas, "pt_BR", _StubSummarizer(), existing_text=existing)
        )
        assert "Curated intro that must be kept" in result
        assert "Summer '26" in result


class TestUpdateSingleReadmeIdempotent:
    """_update_single_readme preserves content outside the releases block."""

    def test_preserves_pre_heading_content(self, tmp_path: Path) -> None:
        import asyncio

        from src.release_docs import (
            _update_single_readme,
            RELEASE_SECTION_HEADING,
        )

        curated = (
            "<details>\n<summary><h3>☀️ Summer '26</h3></summary>\n\n"
            "> 📊 **Resumo Executivo:** Curated manual edit.\n"
            "</details>"
        )
        readme_text = (
            "# Title\n"
            "\nSome manual intro that must not be touched.\n"
            "\n"
            f"{RELEASE_SECTION_HEADING}\n\n"
            f"{curated}\n"
            "\n## 🏗️ Como Funciona\n\nArchitecture content.\n"
        )
        readme = tmp_path / "README.md"
        readme.write_text(readme_text, encoding="utf-8")

        metas = [
            {
                "name": "Summer '26",
                "slug": "summer_26",
                "release_id": 262,
                "categories": [],
            }
        ]

        class _StubSummarizer:
            async def summarize(self, slug: str):
                return None

        asyncio.run(_update_single_readme(readme, metas, "pt_BR", _StubSummarizer()))

        result = readme.read_text(encoding="utf-8")
        assert "Some manual intro that must not be touched." in result
        assert "Curated manual edit" in result
        assert "Architecture content." in result

    def test_inserts_new_release_without_reformatting_existing(self, tmp_path: Path) -> None:
        import asyncio

        from src.release_docs import (
            _update_single_readme,
            RELEASE_SECTION_HEADING,
        )

        existing = (
            "<details>\n<summary><h3>❄️ Winter '26</h3></summary>\n\n"
            "> 📊 **Resumo Executivo:** Manual curated intro.\n"
            "</details>"
        )
        readme_text = f"{RELEASE_SECTION_HEADING}\n\n" f"{existing}\n" "\n## Next Section\n"
        readme = tmp_path / "README.md"
        readme.write_text(readme_text, encoding="utf-8")

        metas = [
            {"name": "Summer '26", "slug": "summer_26", "release_id": 262, "categories": []},
            {
                "name": "Winter '26",
                "slug": "winter_26",
                "release_id": 258,
                "categories": [],
            },
        ]

        class _StubSummarizer:
            async def summarize(self, slug: str):
                return None

        asyncio.run(_update_single_readme(readme, metas, "pt_BR", _StubSummarizer()))

        result = readme.read_text(encoding="utf-8")
        assert "Manual curated intro" in result
        assert "Summer '26" in result
        assert "Next Section" in result

    def test_no_heading_skips_safely(self, tmp_path: Path) -> None:
        import asyncio

        from src.release_docs import _update_single_readme

        readme = tmp_path / "README.md"
        readme.write_text("# Title\n\nNo releases section here.\n", encoding="utf-8")

        metas = [{"name": "Summer '26", "slug": "summer_26", "release_id": 262, "categories": []}]

        class _StubSummarizer:
            async def summarize(self, slug: str):
                return None

        asyncio.run(_update_single_readme(readme, metas, "pt_BR", _StubSummarizer()))

        assert readme.read_text(encoding="utf-8") == "# Title\n\nNo releases section here.\n"

    def test_no_next_heading_after_release_section_warns(self, tmp_path: Path) -> None:
        import asyncio

        from src.release_docs import _update_single_readme, RELEASE_SECTION_HEADING

        readme = tmp_path / "README.md"
        readme.write_text(
            f"# Title\n{RELEASE_SECTION_HEADING}\n\nrelease block content with no following heading",
            encoding="utf-8",
        )

        metas = [{"name": "Summer '26", "slug": "summer_26", "release_id": 262, "categories": []}]

        class _StubSummarizer:
            async def summarize(self, slug: str):
                return None

        asyncio.run(_update_single_readme(readme, metas, "pt_BR", _StubSummarizer()))

        assert "no following heading" in readme.read_text(encoding="utf-8")

    def test_readme_not_exists_skips(self, tmp_path: Path) -> None:
        import asyncio

        from src.release_docs import _update_single_readme

        readme = tmp_path / "NotThere.md"
        metas = [{"name": "Summer '26", "slug": "summer_26", "release_id": 262, "categories": []}]

        class _StubSummarizer:
            async def summarize(self, slug: str):
                return None

        asyncio.run(_update_single_readme(readme, metas, "pt_BR", _StubSummarizer()))


class TestUpdateBadge:
    """_update_badge: idempotent badge refresh."""

    def test_no_readme(self, tmp_path: Path) -> None:
        from src.release_docs import _update_badge

        with patch("src.release_docs.Path") as MockPath:
            mock_readme = MagicMock()
            mock_readme.exists.return_value = False
            MockPath.return_value = mock_readme
            _update_badge([])
            mock_readme.exists.assert_called_once()

    def test_no_marker(self, tmp_path: Path) -> None:
        from src.release_docs import _update_badge

        with patch("src.release_docs.Path") as MockPath:
            mock_readme = MagicMock()
            mock_readme.exists.return_value = True
            mock_readme.read_text.return_value = "# Plain readme without marker\n"
            MockPath.return_value = mock_readme
            _update_badge([])
            mock_readme.write_text.assert_not_called()

    def test_updates_badge_when_marker_present(self, tmp_path: Path, monkeypatch) -> None:
        from src.release_docs import _update_badge, RELEASE_BADGE_MARKER

        existing = (
            "# Title\n"
            f"\n{RELEASE_BADGE_MARKER}\n"
            "![old-badge](https://img.shields.io/badge/old)\n"
            "\n## Releases\n"
        )
        readme = tmp_path / "README.md"
        readme.write_text(existing, encoding="utf-8")

        releases_dir = tmp_path / "releases" / "summer_26"
        releases_dir.mkdir(parents=True)
        (releases_dir / ".meta.json").write_text(
            '{"name": "Summer \'26", "release_id": 262, "categories": [{"name": "X", "count": 5}]}',
            encoding="utf-8",
        )

        monkeypatch.chdir(tmp_path)

        with (
            patch("src.release_docs.RELEASES_DIR", str(tmp_path / "releases")),
            patch("src.ai_automation.generate_dynamic_badge", return_value="![new-badge](x)"),
        ):
            release = ReleaseInfo(name="Summer '26", release_id=262, slug="summer_26")
            _update_badge([release])

        result = readme.read_text(encoding="utf-8")
        assert "new-badge" in result
        assert "old-badge" not in result

    def test_inserts_badge_after_marker_when_no_image(self, tmp_path: Path, monkeypatch) -> None:
        from src.release_docs import _update_badge, RELEASE_BADGE_MARKER

        existing = (
            "# Title\n"
            f"\n{RELEASE_BADGE_MARKER}\n"
            "\n## Releases\n"
        )
        readme = tmp_path / "README.md"
        readme.write_text(existing, encoding="utf-8")

        releases_dir = tmp_path / "releases" / "summer_26"
        releases_dir.mkdir(parents=True)
        (releases_dir / ".meta.json").write_text(
            '{"name": "Summer \'26", "release_id": 262, "categories": [{"name": "X", "count": 3}]}',
            encoding="utf-8",
        )

        monkeypatch.chdir(tmp_path)

        with (
            patch("src.release_docs.RELEASES_DIR", str(tmp_path / "releases")),
            patch("src.ai_automation.generate_dynamic_badge", return_value="![inserted](y)"),
        ):
            release = ReleaseInfo(name="Summer '26", release_id=262, slug="summer_26")
            _update_badge([release])

        result = readme.read_text(encoding="utf-8")
        assert "inserted" in result

    def test_no_latest_meta_returns(self, tmp_path: Path, monkeypatch) -> None:
        from src.release_docs import _update_badge, RELEASE_BADGE_MARKER

        readme = tmp_path / "README.md"
        readme.write_text(f"# Title\n{RELEASE_BADGE_MARKER}\n", encoding="utf-8")

        empty_releases = tmp_path / "releases"
        empty_releases.mkdir()
        monkeypatch.chdir(tmp_path)

        with patch("src.release_docs.RELEASES_DIR", str(empty_releases)):
            _update_badge([])

        assert "old" not in readme.read_text(encoding="utf-8")


class TestUpdateReadmeSingle:
    """_update_readme_single: writes meta.json and history."""

    def test_writes_meta_and_history(self, tmp_path: Path) -> None:
        import json

        from src.release_docs import _update_readme_single

        release = ReleaseInfo(name="Spring '26", release_id=260, slug="spring_26")
        (tmp_path / "spring_26").mkdir()

        cat1 = MagicMock()
        cat1.name = "A"
        cat1.total_features = 5
        cat1.avg_confidence = 0.8
        cat1.subcategories = {}
        cat2 = MagicMock()
        cat2.name = "B"
        cat2.total_features = 3
        cat2.avg_confidence = 0.9
        cat2.subcategories = {}

        with (
            patch("src.release_docs.RELEASES_DIR", str(tmp_path)),
            patch("src.release_docs._update_release_history") as mock_hist,
        ):
            _update_readme_single(release, [cat1, cat2])

        meta = json.loads((tmp_path / "spring_26" / ".meta.json").read_text(encoding="utf-8"))
        assert meta["name"] == "Spring '26"
        assert meta["total_features"] == 8
        assert len(meta["categories"]) == 2
        mock_hist.assert_called_once()

    def test_increments_patch_version(self, tmp_path: Path) -> None:
        import json

        from src.release_docs import _update_readme_single

        release = ReleaseInfo(name="Spring '26", release_id=260, slug="spring_26")
        (tmp_path / "spring_26").mkdir()
        (tmp_path / "spring_26" / ".meta.json").write_text(
            json.dumps({"name": "Spring '26", "version": "1.0.2"}),
            encoding="utf-8",
        )

        cat = MagicMock()
        cat.name = "A"
        cat.total_features = 1
        cat.avg_confidence = 0.5
        cat.subcategories = {}

        with patch("src.release_docs.RELEASES_DIR", str(tmp_path)):
            _update_readme_single(release, [cat])

        meta = json.loads((tmp_path / "spring_26" / ".meta.json").read_text(encoding="utf-8"))
        assert meta["version"] == "2.0.3"

    def test_winter_year_increment(self) -> None:
        from src.release_docs import _build_release_name

        assert _build_release_name(258) == "Winter '26"

    def test_corrupt_prev_meta_falls_back(self, tmp_path: Path) -> None:
        import json

        from src.release_docs import _update_readme_single

        release = ReleaseInfo(name="Spring '26", release_id=260, slug="spring_26")
        (tmp_path / "spring_26").mkdir()
        (tmp_path / "spring_26" / ".meta.json").write_text("not-json", encoding="utf-8")

        cat = MagicMock()
        cat.name = "A"
        cat.total_features = 1
        cat.avg_confidence = 0.5
        cat.subcategories = {}

        with patch("src.release_docs.RELEASES_DIR", str(tmp_path)):
            _update_readme_single(release, [cat])

        meta = json.loads((tmp_path / "spring_26" / ".meta.json").read_text(encoding="utf-8"))
        assert meta["version"].startswith("2.")

    def test_invalid_release_name_version(self, tmp_path: Path) -> None:
        import json

        from src.release_docs import _update_readme_single

        release = ReleaseInfo(name="Invalid", release_id=260, slug="spring_26")
        (tmp_path / "spring_26").mkdir()

        cat = MagicMock()
        cat.name = "A"
        cat.total_features = 1
        cat.avg_confidence = 0.5
        cat.subcategories = {}

        with patch("src.release_docs.RELEASES_DIR", str(tmp_path)):
            _update_readme_single(release, [cat])

        meta = json.loads((tmp_path / "spring_26" / ".meta.json").read_text(encoding="utf-8"))
        assert meta["version"] == "1.0.0"

    def test_history_sorted_order(self, tmp_path: Path) -> None:
        import json

        from src.release_docs import _update_release_history

        r1 = ReleaseInfo(name="Winter '26", release_id=258, slug="winter_26")
        r2 = ReleaseInfo(name="Spring '26", release_id=260, slug="spring_26")
        (tmp_path / "history.json").write_text(
            json.dumps(
                [
                    {"slug": "winter_26", "name": "Winter '26", "release_id": 258, "total_features": 10, "category_count": 3},
                ]
            ),
            encoding="utf-8",
        )

        with patch("src.release_docs.RELEASES_DIR", str(tmp_path)):
            _update_release_history(r1, 10, 3)
            _update_release_history(r2, 5, 2)

        history = json.loads((tmp_path / "history.json").read_text(encoding="utf-8"))
        assert history[0]["slug"] == "spring_26"
        assert history[1]["slug"] == "winter_26"

    def test_en_file_from_pt_recreated(self, tmp_path: Path, monkeypatch) -> None:
        import asyncio

        from src.release_docs import update_readme_all, RELEASE_SECTION_HEADING

        (tmp_path / "summer_26").mkdir()
        (tmp_path / "summer_26" / ".meta.json").write_text(
            '{"name": "Summer \'26", "slug": "summer_26", "release_id": 262, "categories": [{"name": "X", "count": 1}]}',
            encoding="utf-8",
        )

        monkeypatch.chdir(tmp_path)
        (tmp_path / "README.md").write_text(
            f"# Title\n\n{RELEASE_SECTION_HEADING}\n\n🇧🇷 Português content\n\n## 🏗️ Next\n",
            encoding="utf-8",
        )
        (tmp_path / "README.en.md").write_text("# Title EN\n\nNo releases here\n", encoding="utf-8")

        with (
            patch("src.release_docs.RELEASES_DIR", str(tmp_path)),
            patch("src.release_docs._update_single_readme", new=AsyncMock()),
        ):
            asyncio.run(update_readme_all())

        en_content = (tmp_path / "README.en.md").read_text(encoding="utf-8")
        assert "English" in en_content
        assert "🇧🇷 Português" not in en_content

    def test_new_release_regenerates_with_categories(self) -> None:
        import asyncio

        from src.release_docs import _build_release_block, RELEASE_SECTION_HEADING

        metas = [
            {
                "name": "Winter '26",
                "slug": "winter_26",
                "release_id": 258,
                "categories": [{"name": "X", "count": 2}],
            },
            {
                "name": "Spring '26",
                "slug": "spring_26",
                "release_id": 260,
                "categories": [{"name": "Y", "count": 1}],
            },
        ]
        existing = f"{RELEASE_SECTION_HEADING}\n\n"

        summary_mock = MagicMock()
        summary_mock.executive_summary = "Some summary"
        summary_mock.category_summaries = {"X": "X desc"}

        class _Summarizer:
            async def summarize(self, slug: str):
                return summary_mock

        result = asyncio.run(_build_release_block(metas, "pt_BR", _Summarizer(), existing_text=existing))
        assert "Winter '26" in result
        assert "Spring '26" in result
        assert "Some summary" in result

    def test_find_heading_fallback_no_marker(self) -> None:
        from src.release_docs import _find_release_heading

        text = "## Custom Releases Section\nbody"
        assert _find_release_heading(text) is None


class TestUpdateReleaseHistory:
    """_update_release_history: appends/updates releases/history.json."""

    def test_creates_history(self, tmp_path: Path) -> None:
        import json

        from src.release_docs import _update_release_history

        release = ReleaseInfo(name="Spring '26", release_id=260, slug="spring_26")

        with patch("src.release_docs.RELEASES_DIR", str(tmp_path)):
            _update_release_history(release, 100, 5)

        history = json.loads((tmp_path / "history.json").read_text(encoding="utf-8"))
        assert len(history) == 1
        assert history[0]["slug"] == "spring_26"

    def test_updates_existing_entry(self, tmp_path: Path) -> None:
        import json

        from src.release_docs import _update_release_history

        release = ReleaseInfo(name="Spring '26", release_id=260, slug="spring_26")
        (tmp_path / "history.json").write_text(
            json.dumps(
                [
                    {
                        "slug": "spring_26",
                        "name": "Spring '26",
                        "release_id": 260,
                        "total_features": 50,
                        "category_count": 3,
                    }
                ]
            ),
            encoding="utf-8",
        )

        with patch("src.release_docs.RELEASES_DIR", str(tmp_path)):
            _update_release_history(release, 100, 5)

        history = json.loads((tmp_path / "history.json").read_text(encoding="utf-8"))
        assert len(history) == 1
        assert history[0]["total_features"] == 100


class TestFormatImpactReport:
    """_format_impact_report: formats impact reports as Markdown."""

    def test_full_report(self) -> None:
        from src.release_docs import _format_impact_report

        report = MagicMock()
        report.total_features = 100
        report.breaking_changes = ["API removed"]
        report.security_fixes = ["XSS fix"]
        report.risk_score = 0.7

        out = _format_impact_report(report, "Spring '26")
        assert "Impact Report: Spring '26" in out
        assert "Breaking Changes" in out
        assert "Security Fixes" in out
        assert "Risk Score: 0.7" in out

    def test_minimal_report(self) -> None:
        from src.release_docs import _format_impact_report

        report = MagicMock()
        report.total_features = 0
        report.breaking_changes = []
        report.security_fixes = []
        report.risk_score = 0.1

        out = _format_impact_report(report, "Spring '26")
        assert "Impact Report" in out
        assert "Breaking Changes" not in out
        assert "Security Fixes" not in out


class TestFormatNotificationDigest:
    """_format_notification_digest: renders digest as Markdown."""

    def test_with_summary(self) -> None:
        from src.release_docs import _format_notification_digest

        notif = MagicMock()
        notif.priority.value = "high"
        notif.title = "Deploy"
        notif.body = "Deployed v2"
        digest = MagicMock()
        digest.summary_text = "Weekly summary"
        digest.notifications = [notif]

        out = _format_notification_digest(digest)
        assert "Notification Digest" in out
        assert "Weekly summary" in out
        assert "[high] Deploy" in out
        assert "Deployed v2" in out

    def test_without_summary(self) -> None:
        from src.release_docs import _format_notification_digest

        notif = MagicMock()
        notif.priority = "low"
        notif.title = "T"
        notif.body = ""
        digest = MagicMock()
        digest.summary_text = ""
        digest.notifications = [notif]

        out = _format_notification_digest(digest)
        assert "[low] T" in out


class TestGenerateReleaseFiles:
    """_generate_release_files: writes per-category .md."""

    def test_pt_br_path(self, tmp_path: Path) -> None:
        import asyncio

        from src.release_docs import _generate_release_files

        release = ReleaseInfo(name="Spring '26", release_id=260, slug="spring_26")

        cat = MagicMock()
        cat.name = "Análise de dados"
        cat.total_features = 3
        cat.description = "Some desc"
        cat.entries = []
        cat.subcategories = {}

        gen = MagicMock()
        translator = MagicMock()
        translator.translate_feature = MagicMock(side_effect=lambda x, *_: asyncio.sleep(0) or x)

        with (
            patch("src.release_docs.RELEASES_DIR", str(tmp_path)),
            patch(
                "src.salesforce.generate_category_trailhead_section",
                return_value="## Trailhead",
            ),
        ):
            paths = asyncio.run(
                _generate_release_files(release, [cat], gen, translator, locale="pt_BR")
            )

        assert len(paths) == 1
        assert paths[0].exists()
        assert "Análise de dados" in paths[0].read_text(encoding="utf-8")

    def test_en_us_path_with_translator(self, tmp_path: Path) -> None:
        import asyncio

        from src.release_docs import _generate_release_files
        from src.parser import FeatureImpactEntry, FeatureImpactCategory

        release = ReleaseInfo(name="Spring '26", release_id=260, slug="spring_26")

        entry = FeatureImpactEntry(
            name="Feature A",
            docs_url="",
            available_users=True,
            available_admins=False,
            requires_config=False,
            contact_sf=False,
            confidence=0.9,
        )

        cat = FeatureImpactCategory(name="X", description="")
        cat.entries = [entry]
        cat.subcategories = {}

        gen = MagicMock()
        translator = AsyncMock()
        translator.translate_feature = AsyncMock(side_effect=lambda x, *_: f"translated-{x}")

        with (
            patch("src.release_docs.RELEASES_DIR", str(tmp_path)),
            patch(
                "src.salesforce.generate_category_trailhead_section",
                return_value="## Trailhead",
            ),
        ):
            paths = asyncio.run(
                _generate_release_files(release, [cat], gen, translator, locale="en_US")
            )

        assert len(paths) == 1
        content = paths[0].read_text(encoding="utf-8")
        # translator is called with "Feature A" (and "SubFeat" for sub)
        # at least the table must be rendered
        assert "Feature A" in content or "translated" in content

    def test_en_us_translation_deepcopy(self, tmp_path: Path) -> None:
        import asyncio

        from src.release_docs import _generate_release_files
        from src.parser import FeatureImpactEntry, FeatureImpactCategory

        release = ReleaseInfo(name="Spring '26", release_id=260, slug="spring_26")

        sub_entry = FeatureImpactEntry(
            name="SubFeat",
            docs_url="",
            available_users=True,
            available_admins=False,
            requires_config=False,
            contact_sf=False,
            confidence=0.9,
        )

        cat = FeatureImpactCategory(name="X", description="")
        cat.entries = []
        cat.subcategories = {"Sub1": [sub_entry]}

        gen = MagicMock()
        translator = AsyncMock()
        translator.translate_feature = AsyncMock(side_effect=lambda x, *_: f"t-{x}")

        with (
            patch("src.release_docs.RELEASES_DIR", str(tmp_path)),
            patch(
                "src.salesforce.generate_category_trailhead_section",
                return_value="## Trailhead",
            ),
        ):
            paths = asyncio.run(
                _generate_release_files(release, [cat], gen, translator, locale="en_US")
            )

        assert len(paths) == 1

    def test_enriched_table_path(self, tmp_path: Path) -> None:
        import asyncio

        from src.release_docs import _generate_release_files

        release = ReleaseInfo(name="Spring '26", release_id=260, slug="spring_26")

        cat = MagicMock()
        cat.name = "X"
        cat.total_features = 1
        cat.description = ""
        cat.entries = []
        cat.subcategories = {}

        gen = MagicMock()
        translator = MagicMock()
        translator.translate_feature = MagicMock(side_effect=lambda x, *_: asyncio.sleep(0) or x)

        enriched_feat = MagicMock()
        enriched_feat.to_markdown_row.return_value = "| A | Desc | High |"

        enrichment = MagicMock()
        enrichment.high_impact_count = 1
        enrichment.medium_impact_count = 0
        enrichment.low_impact_count = 0
        enrichment.introduction = "> Enriched intro"
        enrichment.features = [enriched_feat]

        with (
            patch("src.release_docs.RELEASES_DIR", str(tmp_path)),
            patch(
                "src.salesforce.generate_category_trailhead_section",
                return_value="## Trailhead",
            ),
        ):
            paths = asyncio.run(
                _generate_release_files(
                    release, [cat], gen, translator, locale="pt_BR", enrichments={"x": enrichment}
                )
            )

        assert len(paths) == 1
        content = paths[0].read_text(encoding="utf-8")
        assert "Enriched intro" in content
        assert "alto impacto" in content

    def test_cat_description_fallback(self, tmp_path: Path) -> None:
        import asyncio

        from src.release_docs import _generate_release_files

        release = ReleaseInfo(name="Spring '26", release_id=260, slug="spring_26")

        cat = MagicMock()
        cat.name = "X"
        cat.total_features = 1
        cat.description = "Catalog description text"
        cat.entries = []
        cat.subcategories = {}

        gen = MagicMock()
        translator = MagicMock()

        with (
            patch("src.release_docs.RELEASES_DIR", str(tmp_path)),
            patch(
                "src.salesforce.generate_category_trailhead_section",
                return_value="## Trailhead",
            ),
        ):
            paths = asyncio.run(
                _generate_release_files(release, [cat], gen, translator, locale="pt_BR")
            )

        content = paths[0].read_text(encoding="utf-8")
        assert "Catalog description text" in content

    def test_non_enriched_subcategory_table(self, tmp_path: Path) -> None:
        import asyncio

        from src.release_docs import _generate_release_files

        release = ReleaseInfo(name="Spring '26", release_id=260, slug="spring_26")

        sub_e = MagicMock()
        sub_e.name = "SubFeat"
        sub_e.confidence = 0.5
        sub_e.docs_url = ""
        sub_e.available_users = True
        sub_e.available_admins = False
        sub_e.requires_config = False
        sub_e.contact_sf = False

        cat = MagicMock()
        cat.name = "X"
        cat.total_features = 1
        cat.description = ""
        cat.entries = []
        cat.subcategories = {"SubGroup": [sub_e]}

        gen = MagicMock()
        translator = MagicMock()
        translator.translate_feature = MagicMock(side_effect=lambda x, *_: asyncio.sleep(0) or x)

        with (
            patch("src.release_docs.RELEASES_DIR", str(tmp_path)),
            patch(
                "src.salesforce.generate_category_trailhead_section",
                return_value="## Trailhead",
            ),
        ):
            paths = asyncio.run(
                _generate_release_files(release, [cat], gen, translator, locale="pt_BR")
            )

        content = paths[0].read_text(encoding="utf-8")
        assert "SubGroup" in content
        assert "SubFeat" in content


class TestUpdateReadmeAll:
    """update_readme_all: orchestrator for bilingual READMEs."""

    def test_no_releases_dir(self, tmp_path: Path) -> None:
        import asyncio

        from src.release_docs import update_readme_all

        with patch("src.release_docs.RELEASES_DIR", str(tmp_path / "nope")):
            asyncio.run(update_readme_all())

    def test_no_metas(self, tmp_path: Path) -> None:
        import asyncio

        from src.release_docs import update_readme_all

        (tmp_path / "empty").mkdir()
        with patch("src.release_docs.RELEASES_DIR", str(tmp_path)):
            asyncio.run(update_readme_all())

    def test_en_missing_heading_recreated(self, tmp_path: Path, monkeypatch) -> None:
        import asyncio

        from src.release_docs import update_readme_all, RELEASE_SECTION_HEADING

        (tmp_path / "summer_26").mkdir()
        (tmp_path / "summer_26" / ".meta.json").write_text(
            '{"name": "Summer \'26", "slug": "summer_26", "release_id": 262, "categories": [{"name": "X", "count": 1}]}',
            encoding="utf-8",
        )

        monkeypatch.chdir(tmp_path)
        (tmp_path / "README.md").write_text(
            f"# Title\n\n{RELEASE_SECTION_HEADING}\n\n🇧🇷 Português toggle\n\n## 🏗️ Next\n",
            encoding="utf-8",
        )
        (tmp_path / "README.en.md").write_text("# Title EN\n\nNo releases here\n", encoding="utf-8")

        with (
            patch("src.release_docs.RELEASES_DIR", str(tmp_path)),
            patch("src.release_docs._update_single_readme", new=AsyncMock()),
        ):
            asyncio.run(update_readme_all())

        en_content = (tmp_path / "README.en.md").read_text(encoding="utf-8")
        assert "English" in en_content
        assert "🇧🇷 Português" not in en_content

    def test_pt_readme_called(self, tmp_path: Path, monkeypatch) -> None:
        import asyncio

        from src.release_docs import update_readme_all, RELEASE_SECTION_HEADING

        (tmp_path / "summer_26").mkdir()
        (tmp_path / "summer_26" / ".meta.json").write_text(
            '{"name": "Summer \'26", "slug": "summer_26", "release_id": 262, "categories": [{"name": "X", "count": 1}]}',
            encoding="utf-8",
        )

        monkeypatch.chdir(tmp_path)
        (tmp_path / "README.md").write_text(
            f"# Title\n\n{RELEASE_SECTION_HEADING}\n\ntext\n\n## 🏗️ Next\n",
            encoding="utf-8",
        )

        with (
            patch("src.release_docs.RELEASES_DIR", str(tmp_path)),
            patch("src.release_docs._update_single_readme", new=AsyncMock()) as mock_update,
        ):
            asyncio.run(update_readme_all())

        assert mock_update.call_count >= 1

    def test_en_heading_present_calls_update(self, tmp_path: Path, monkeypatch) -> None:
        import asyncio

        from src.release_docs import update_readme_all, RELEASE_SECTION_HEADING

        (tmp_path / "summer_26").mkdir()
        (tmp_path / "summer_26" / ".meta.json").write_text(
            '{"name": "Summer \'26", "slug": "summer_26", "release_id": 262, "categories": [{"name": "X", "count": 1}]}',
            encoding="utf-8",
        )

        monkeypatch.chdir(tmp_path)
        (tmp_path / "README.md").write_text(
            f"# Title\n\n{RELEASE_SECTION_HEADING}\n\ntext\n\n## Next\n",
            encoding="utf-8",
        )
        (tmp_path / "README.en.md").write_text(
            f"# Title EN\n\n{RELEASE_SECTION_HEADING}\n\ntext\n\n## Next\n",
            encoding="utf-8",
        )

        with (
            patch("src.release_docs.RELEASES_DIR", str(tmp_path)),
            patch("src.release_docs._update_single_readme", new=AsyncMock()) as mock_update,
        ):
            asyncio.run(update_readme_all())

        assert mock_update.call_count == 2


class TestFindReleaseHeading:
    """_find_release_heading: detects heading variants and fallback."""

    def test_finds_known_variant(self) -> None:
        from src.release_docs import _find_release_heading, RELEASE_BADGE_MARKER

        text = f"intro\n{RELEASE_BADGE_MARKER}\n## 📋 Releases Disponíveis\nbody"
        assert _find_release_heading(text) == "## 📋 Releases Disponíveis"

    def test_finds_known_variant_alternative(self) -> None:
        from src.release_docs import _find_release_heading, RELEASE_BADGE_MARKER

        text = f"intro\n{RELEASE_BADGE_MARKER}\n## 📦 Available Releases\nbody"
        assert _find_release_heading(text) == "## 📦 Available Releases"

    def test_fallback_regex_match(self) -> None:
        from src.release_docs import _find_release_heading, RELEASE_BADGE_MARKER

        text = f"intro\n{RELEASE_BADGE_MARKER}\n" "## Custom Releases Header\nbody"
        assert _find_release_heading(text) == "## Custom Releases Header"

    def test_no_marker_no_heading(self) -> None:
        from src.release_docs import _find_release_heading

        assert _find_release_heading("plain text without anything") is None

    def test_no_heading_after_marker(self) -> None:
        from src.release_docs import _find_release_heading, RELEASE_BADGE_MARKER

        text = f"{RELEASE_BADGE_MARKER}\njust text no heading"
        assert _find_release_heading(text) is None


class TestBuildReleaseBlockLanguages:
    """_build_release_block: language toggle + summary branches."""

    def test_en_us_toggle_and_summary(self) -> None:
        import asyncio

        from src.release_docs import _build_release_block, RELEASE_SECTION_HEADING

        metas = [{"name": "Summer '26", "slug": "summer_26", "release_id": 262, "categories": []}]
        existing = f"{RELEASE_SECTION_HEADING}\n\nempty\n"

        summary = MagicMock()
        summary.executive_summary = "EN summary"
        summary.category_summaries = {"X": "cat desc"}

        class _Summarizer:
            async def summarize(self, slug: str):
                return summary

        result = asyncio.run(
            _build_release_block(metas, "en_US", _Summarizer(), existing_text=existing)
        )
        assert "🇺🇸 English" in result
        assert "Executive Summary" in result

    def test_invalid_summary_uses_fallback(self) -> None:
        import asyncio

        from src.release_docs import _build_release_block, RELEASE_SECTION_HEADING

        metas = [
            {
                "name": "Summer '26",
                "slug": "summer_26",
                "release_id": 262,
                "total_features": 10,
                "categories": [{"name": "X", "count": 10}],
            }
        ]
        existing = f"{RELEASE_SECTION_HEADING}\n\nempty\n"

        bad_summary = MagicMock()
        bad_summary.executive_summary = "0 novos recursos"
        bad_summary.category_summaries = {"X": "ok"}

        class _Summarizer:
            async def summarize(self, slug: str):
                return bad_summary

        result = asyncio.run(
            _build_release_block(metas, "pt_BR", _Summarizer(), existing_text=existing)
        )
        assert "Summer '26" in result

    def test_invalid_category_summary_skipped(self) -> None:
        import asyncio

        from src.release_docs import _build_release_block, RELEASE_SECTION_HEADING

        metas = [
            {
                "name": "Summer '26",
                "slug": "summer_26",
                "release_id": 262,
                "total_features": 10,
                "categories": [{"name": "BigCat", "count": 10}],
            }
        ]
        existing = f"{RELEASE_SECTION_HEADING}\n\nempty\n"

        summary = MagicMock()
        summary.executive_summary = "OK summary"
        summary.category_summaries = {"BigCat": "1 novos recursos"}

        class _Summarizer:
            async def summarize(self, slug: str):
                return summary

        result = asyncio.run(
            _build_release_block(metas, "pt_BR", _Summarizer(), existing_text=existing)
        )
        assert "1 novos recursos" not in result

    def test_new_release_generated_with_summary_and_categories(self) -> None:
        import asyncio

        from src.release_docs import _build_release_block, RELEASE_SECTION_HEADING

        metas = [
            {
                "name": "Summer '26",
                "slug": "summer_26",
                "release_id": 262,
                "total_features": 5,
                "categories": [
                    {"name": "X", "count": 3},
                    {"name": "Y", "count": 2},
                ],
            }
        ]
        existing = f"{RELEASE_SECTION_HEADING}\n\n"

        summary = MagicMock()
        summary.executive_summary = "Executive summary text"
        summary.category_summaries = {"X": "X description"}

        class _Summarizer:
            async def summarize(self, slug: str):
                return summary

        result = asyncio.run(
            _build_release_block(metas, "pt_BR", _Summarizer(), existing_text=existing)
        )
        assert "Summer '26" in result
        assert "Executive summary text" in result
        assert "X" in result
        assert "Y" in result

    def test_warning_on_invalid_summary(self) -> None:
        import asyncio

        from src.release_docs import _build_release_block, RELEASE_SECTION_HEADING

        metas = [
            {
                "name": "Summer '26",
                "slug": "summer_26",
                "release_id": 262,
                "total_features": 5,
                "categories": [{"name": "X", "count": 5}],
            }
        ]
        existing = f"{RELEASE_SECTION_HEADING}\n\n"

        bad = MagicMock()
        bad.executive_summary = "0 novos recursos"
        bad.category_summaries = []

        class _Summarizer:
            async def summarize(self, slug: str):
                return bad

        result = asyncio.run(_build_release_block(metas, "pt_BR", _Summarizer(), existing_text=existing))
        assert "Summer '26" in result

    def test_en_us_categories_rendered(self) -> None:
        import asyncio

        from src.release_docs import _build_release_block, RELEASE_SECTION_HEADING

        metas = [
            {
                "name": "Summer '26",
                "slug": "summer_26",
                "release_id": 262,
                "categories": [{"name": "Salesforce geral", "count": 5}],
            }
        ]
        existing = f"{RELEASE_SECTION_HEADING}\n\n"

        class _Summarizer:
            async def summarize(self, slug: str):
                return None

        result = asyncio.run(_build_release_block(metas, "en_US", _Summarizer(), existing_text=existing))
        assert "features" in result
        assert "Full details" in result


class TestFormatEntryTable:
    """_format_entry_table / _format_entry / _check."""

    def test_check(self) -> None:
        from src.release_docs import _check

        assert _check(True) == "✅"
        assert _check(False) == "❌"

    def test_format_entry_no_flags(self) -> None:
        from src.release_docs import _format_entry

        entry = MagicMock()
        entry.name = "Feat"
        entry.available_users = False
        entry.available_admins = False
        entry.requires_config = False
        entry.contact_sf = False
        out = _format_entry(entry)
        assert "Feat" in out
        assert "_" not in out

    def test_format_entry_with_flags(self) -> None:
        from src.release_docs import _format_entry

        entry = MagicMock()
        entry.name = "Feat"
        entry.available_users = True
        entry.available_admins = True
        entry.requires_config = True
        entry.contact_sf = True
        out = _format_entry(entry)
        assert "Disponível para usuários" in out
        assert "Disponível para admins/devs" in out
        assert "Requer configuração" in out
        assert "Contatar Salesforce" in out

    def test_format_entry_table(self) -> None:
        from src.release_docs import _format_entry_table

        entry = MagicMock()
        entry.name = "Feat"
        entry.confidence = 0.9
        entry.docs_url = ""
        entry.available_users = True
        entry.available_admins = False
        entry.requires_config = False
        entry.contact_sf = False
        out = _format_entry_table(entry)
        assert "Feat" in out
        assert "✅" in out
        assert "❌" in out

    def test_format_entry_table_low_confidence(self) -> None:
        from src.release_docs import _format_entry_table

        entry = MagicMock()
        entry.name = "Feat"
        entry.confidence = 0.5
        entry.docs_url = "https://example.com"
        entry.available_users = False
        entry.available_admins = False
        entry.requires_config = False
        entry.contact_sf = False
        out = _format_entry_table(entry)
        assert "⚠️" in out
        assert "https://example.com" in out


class TestGenerateCategorySummary:
    """_generate_category_summary: brief summary for a category."""

    def test_zero_features(self) -> None:
        from src.release_docs import _generate_category_summary

        cat = MagicMock()
        cat.total_features = 0
        cat.entries = []
        assert _generate_category_summary(cat) == ""

    def test_with_high_impact(self) -> None:
        from src.release_docs import _generate_category_summary

        e = MagicMock()
        e.confidence = 0.9
        cat = MagicMock()
        cat.total_features = 5
        cat.entries = [e]
        out = _generate_category_summary(cat)
        assert "5 features" in out
        assert "high confidence" in out

    def test_without_high_impact(self) -> None:
        from src.release_docs import _generate_category_summary

        e = MagicMock()
        e.confidence = 0.3
        cat = MagicMock()
        cat.total_features = 3
        cat.entries = [e]
        out = _generate_category_summary(cat)
        assert "3 features" in out
        assert "high confidence" not in out
