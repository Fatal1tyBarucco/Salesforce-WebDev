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
