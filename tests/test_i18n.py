from __future__ import annotations

import asyncio
from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import MagicMock

if TYPE_CHECKING:
    import pytest

from src.i18n import detect_locale, get_user_locale, generate_toggle_html, LOCALIZATION_MAP


def test_detect_locale_pt_br() -> None:
    headers = {"Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8"}
    assert detect_locale(headers) == "pt_BR"


def test_detect_locale_en_us() -> None:
    headers = {"Accept-Language": "en-US,en;q=0.9"}
    assert detect_locale(headers) == "en_US"


def test_detect_locale_default() -> None:
    headers = {"Accept-Language": "fr-FR,fr;q=0.9"}
    assert detect_locale(headers) == "pt_BR"


def test_detect_locale_no_header() -> None:
    assert detect_locale({}) == "pt_BR"


def test_get_user_locale_pt_br() -> None:
    assert get_user_locale("pt-BR,pt;q=0.9,en;q=0.8") == "pt_BR"


def test_get_user_locale_en_us() -> None:
    assert get_user_locale("en-US,en;q=0.9") == "en_US"


def test_get_user_locale_default() -> None:
    assert get_user_locale("fr-FR") == "pt_BR"


def test_generate_toggle_html_pt_br() -> None:
    html = generate_toggle_html("pt_BR", "agentforce", "summer_26")
    assert "en_US/agentforce.md" in html
    assert "English" in html


def test_generate_toggle_html_en_us() -> None:
    html = generate_toggle_html("en_US", "agentforce", "summer_26")
    assert "pt_BR/agentforce.md" in html
    assert "Portugu" in html


def test_localization_map_has_both_locales() -> None:
    assert "pt_BR" in LOCALIZATION_MAP
    assert "en_US" in LOCALIZATION_MAP


def test_localization_map_has_required_keys() -> None:
    for locale in ["pt_BR", "en_US"]:
        assert "resources" in LOCALIZATION_MAP[locale]
        assert "category_count" in LOCALIZATION_MAP[locale]


def test_toggle_in_generated_file(tmp_path: Path) -> None:
    from src.main import _generate_release_files
    from src.config import ReleaseInfo
    from src.parser import FeatureImpactCategory, FeatureImpactEntry
    from src.generator import MarkdownGenerator

    release = ReleaseInfo(name="Summer '26", release_id=260, slug="summer_26")
    cat = FeatureImpactCategory(name="Agentforce")
    cat.entries = [
        FeatureImpactEntry(
            name="Voice feature",
            available_users=True,
            available_admins=True,
            requires_config=False,
            contact_sf=False,
            confidence=0.9,
        )
    ]

    generator = MarkdownGenerator(base_dir=str(tmp_path))
    translator = MagicMock()
    files = asyncio.run(
        _generate_release_files(release, [cat], generator, translator, locale="pt_BR")
    )

    assert len(files) > 0
    content = files[0].read_text(encoding="utf-8")
    assert "en_US/" in content
    assert "English" in content


def test_bilingual_readme_toggle(tmp_path: Path, monkeypatch: "pytest.MonkeyPatch") -> None:
    import json
    from unittest.mock import patch
    from src.main import _update_readme_all

    readme_path = tmp_path / "README.md"
    readme_path.write_text(
        "# Test\n\n## 📋 Releases Disponíveis\n\nOld content\n\n## Next Section\n",
        encoding="utf-8",
    )

    releases_dir = tmp_path / "summer_26"
    releases_dir.mkdir()
    (releases_dir / ".meta.json").write_text(
        json.dumps(
            {
                "slug": "summer_26",
                "name": "Summer '26",
                "release_id": 260,
                "categories": [{"name": "Agentforce", "count": 5}],
            }
        )
    )

    monkeypatch.chdir(tmp_path)
    with patch("src.main.RELEASES_DIR", str(tmp_path)):
        asyncio.run(_update_readme_all())

    content = readme_path.read_text(encoding="utf-8")
    assert "Summer '26" in content
    assert "Agentforce" in content
    assert "data-lang" in content
    assert "switchLang" in content
