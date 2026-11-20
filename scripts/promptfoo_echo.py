"""Deterministic echo provider for promptfoo (ADR-012, requisito 4.2).

Keyless provider used to evaluate PROMPT fidelity (asserts inspect the
rendered prompt, not the model answer).  Returns a fixed, schema-valid
ClassificationOutput JSON regardless of input, so the classification
json-schema test also runs without API keys.  Live model evaluation remains
available via the real providers in .promptfoo.yaml.
"""

from __future__ import annotations

import json
import sys


def main() -> None:
    # Accept the prompt via stdin or argv (provider convention agnostic).
    if not sys.stdin.isatty():
        sys.stdin.read()
    print(
        json.dumps(
            {
                "type": "new_feature",
                "impact": "médio",
                "audience": "ambos",
                "priority": "importante",
                "justification": ("Deterministic echo provider for prompt-fidelity evaluation."),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
