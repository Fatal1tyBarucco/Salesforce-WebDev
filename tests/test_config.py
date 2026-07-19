from src.config import (
    ENGLISH_CATEGORY_NAMES,
    ENGLISH_CATEGORY_SLUGS,
    ReleaseInfo,
    TopicNode,
    build_release_info,
)


def test_english_category_slugs_has_all_keys() -> None:
    assert len(ENGLISH_CATEGORY_SLUGS) == 24


def test_english_category_names_has_all_keys() -> None:
    assert len(ENGLISH_CATEGORY_NAMES) == 24


def test_english_category_slugs_keys_match_names_keys() -> None:
    assert set(ENGLISH_CATEGORY_SLUGS.keys()) == set(ENGLISH_CATEGORY_NAMES.keys())


def test_english_category_slugs_values_are_kebab_case() -> None:
    for slug in ENGLISH_CATEGORY_SLUGS.values():
        assert slug == slug.lower(), f"Slug '{slug}' must be lowercase"
        assert " " not in slug, f"Slug '{slug}' contains spaces"


def test_english_category_names_are_title_case() -> None:
    for pt_name, en_name in ENGLISH_CATEGORY_NAMES.items():
        assert en_name[0].isupper(), f"Name '{en_name}' must start with uppercase"


def test_agentforce_mappings() -> None:
    assert ENGLISH_CATEGORY_SLUGS["Agentforce"] == "agentforce"
    assert ENGLISH_CATEGORY_NAMES["Agentforce"] == "Agentforce"


def test_sales_mappings() -> None:
    assert ENGLISH_CATEGORY_SLUGS["Vendas"] == "sales"
    assert ENGLISH_CATEGORY_NAMES["Vendas"] == "Sales"


def test_release_info_dataclass() -> None:
    info = ReleaseInfo(name="Summer '26", release_id=262, slug="summer_26")
    assert info.name == "Summer '26"
    assert info.release_id == 262
    assert info.slug == "summer_26"


def test_build_release_info() -> None:
    info = build_release_info(262)
    assert info.name == "Summer '26"
    assert info.slug == "summer_26"


def test_topic_node_is_leaf() -> None:
    leaf = TopicNode(slug="rn_dev", display_name="Dev", level=2, url="https://x")
    assert leaf.is_leaf() is True


def test_topic_node_not_leaf() -> None:
    child = TopicNode(slug="rn_sub", display_name="Sub", level=3, url="")
    parent = TopicNode(slug="rn_parent", display_name="Parent", level=2, url="", children=[child])
    assert parent.is_leaf() is False


def test_topic_node_all_articles() -> None:
    leaf = TopicNode(
        slug="rn_leaf",
        display_name="Leaf",
        level=3,
        url="",
        articles=[{"title": "A1", "url": "https://a1"}],
    )
    parent = TopicNode(
        slug="rn_parent",
        display_name="Parent",
        level=2,
        url="",
        children=[leaf],
        articles=[{"title": "P1", "url": "https://p1"}],
    )
    all_arts = parent.all_articles()
    assert len(all_arts) == 2
    assert all_arts[0]["title"] == "P1"
    assert all_arts[1]["title"] == "A1"


def test_build_release_info_winter() -> None:
    """build_release_info correctly handles Winter season (year += 1)."""
    info = build_release_info(258)
    assert info.name == "Winter '26"
    assert info.slug == "winter_26"
    assert info.release_id == 258


def test_id_to_season() -> None:
    """_id_to_season returns correct season for each release_id."""
    from src.config import _id_to_season

    assert _id_to_season(254) == "Spring"
    assert _id_to_season(256) == "Summer"
    assert _id_to_season(258) == "Winter"


def test_topic_node_topic_file_slug() -> None:
    """TopicNode.topic_file_slug returns the slug."""
    node = TopicNode(slug="rn_dev", display_name="Dev", level=2, url="")
    assert node.topic_file_slug() == "rn_dev"
