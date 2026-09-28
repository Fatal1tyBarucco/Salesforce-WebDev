"""Testes para build_disambiguation_prompt (SFEL prompts)."""

from src.automation.ledger.prompts import build_disambiguation_prompt


def test_build_disambiguation_prompt_contains_all_fields() -> None:
    prompt = build_disambiguation_prompt(
        prev_name="Flow Builder",
        prev_category="Plataforma",
        prev_snippet="Flow Builder permite criar fluxos visuais.",
        curr_name="Flow Builder Novo",
        curr_category="Plataforma",
        curr_snippet="Flow Builder Novo com novas funcionalidades.",
        previous_slug="spring_26",
        current_slug="summer_26",
    )
    assert "spring_26" in prompt
    assert "summer_26" in prompt
    assert "Flow Builder" in prompt
    assert "Plataforma" in prompt
    assert "same_feature" in prompt  # estrutura JSON esperada
    assert "Português Brasileiro" in prompt or "pt-BR" in prompt


def test_build_disambiguation_prompt_truncates_snippet() -> None:
    long_snippet = "x" * 500
    prompt = build_disambiguation_prompt(
        prev_name="X",
        prev_category="Y",
        prev_snippet=long_snippet,
        curr_name="Z",
        curr_category="W",
        curr_snippet="short",
        previous_slug="a",
        current_slug="b",
    )
    # O snippet deve ser truncado para 300 caracteres
    assert "x" * 300 in prompt
    assert "x" * 301 not in prompt or prompt.count("x" * 301) == 0


def test_build_disambiguation_prompt_minimal() -> None:
    prompt = build_disambiguation_prompt(
        prev_name="A",
        prev_category="B",
        prev_snippet="",
        curr_name="C",
        curr_category="D",
        curr_snippet="",
        previous_slug="x",
        current_slug="y",
    )
    assert "x" in prompt
    assert "y" in prompt
    assert "A" in prompt
    assert "C" in prompt
