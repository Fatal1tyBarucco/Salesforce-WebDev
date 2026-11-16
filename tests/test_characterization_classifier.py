"""Testes de caracterização do classificador heurístico (fallback do LLM).

`HeuristicFeatureClassifier.classify_text()` é 100% determinístico (regex sobre
_keywords ordenadas, empate decidido pela ordem das regras). Congela em
`tests/golden/classifier/heuristic_labels.json` o par texto → {impact, type,
confidence} para uma bateria que cobre: vazio, cada regra, empate de
confiança, múltiplas regras casando (maior confiança vence) e o default.

Regenerar goldens:
CHAR_GOLDEN_UPDATE=1 uv run pytest tests/test_characterization_classifier.py
"""

from __future__ import annotations

from src.heuristic_classifier import HeuristicFeatureClassifier
from tests.test_characterization_golden import assert_matches_golden_json

CLASSIFICATION_TEXTS: list[str] = [
    "",
    "   ",
    "Critical security vulnerability CVE-2026-1234 authentication bypass",
    "Performance optimization reduces latency in the cache layer",
    "Deprecated feature removal triggers breaking change migration",
    "Bug fix patch for reported issue",
    "Fresh new feature launch introduction",
    "User interface design refresh for Lightning experience",
    "Agentforce Einstein AI model now generally available",
    "This API integration webhook endpoint update",
    "Fluxo de aprovacao melhorado para times de vendas",
    "New AI security feature with authentication hardening",
    "Upgrade required: incompatible schema migration",
    "Melhoria geral de UX na interface do Lightning",
]


def test_heuristic_classification_labels_match_golden() -> None:
    """Congela os rótulos atuais do classificador heurístico para textos fixos."""
    classifier = HeuristicFeatureClassifier()
    payload = [
        {"text": text, "result": classifier.classify_text(text)} for text in CLASSIFICATION_TEXTS
    ]
    assert_matches_golden_json(payload, "classifier/heuristic_labels.json")
