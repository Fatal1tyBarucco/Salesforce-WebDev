"""Algoritmo de linkage de features para o Salesforce Feature Evolution Ledger.

Nível de match (aplicados em ordem, first-match-wins):
  1. EXACT      — nome normalizado idêntico E mesma categoria
  2. CATEGORY_CHANGE — mesmo nome, categorias diferentes → CATEGORY_CHANGED
  3. FUZZY      — Jaccard(nome_tokens_A, nome_tokens_B) >= 0.5 E mesma categoria
  4. HEURISTIC  — diferentes nomes, mesma categoria, par mais próximo mútuo
  5. LLM        — similaridade 0.2–0.5, desambiguação via LLM (opcional)
"""

from __future__ import annotations

import logging
from typing import Any

from .models import (
    FeatureLink,
    FeatureSnapshot,
    LinkageMethod,
    LifecycleStatus,
)

logger = logging.getLogger(__name__)

# Thresholds
FUZZY_THRESHOLD = 0.5
LLM_THRESHOLD_LOW = 0.2  # abaixo disso, não tenta nem LLM


# ── Helpers ─────────────────────────────────────────────────────────────


def _jaccard(set_a: set[str], set_b: set[str]) -> float:
    """Similaridade Jaccard entre dois conjuntos."""
    if not set_a and not set_b:
        return 0.0
    intersection = len(set_a & set_b)
    union = len(set_a | set_b)
    return intersection / union if union > 0 else 0.0


def _tokenize_name(name: str) -> set[str]:
    """Tokeniza nome normalizado em conjunto de palavras."""
    return set(name.split())


# ── Linker ──────────────────────────────────────────────────────────────


class FeatureLinker:
    """Liga features entre duas releases usando similaridade de nomes e categoria.

    Não depende de LLM. O uso de LLM para desambiguação é opcional: basta
    passar um objeto que implemente ``disambiguate_feature(cs, ps, cur_meta, prev_meta)``
    (assíncrono, retorna str com a desambiguação ou None).
    """

    def __init__(self, llm_service: Any = None) -> None:
        """Inicializa o linker.

        Args:
            llm_service: Opcional. Objeto que provê
                ``disambiguate_feature(current_snap, prev_snap, cur_meta, prev_meta) -> str | None``.
                Se não fornecido, o passo LLM é pulado.
        """
        self._llm = llm_service

    def link(
        self,
        current_snaps: list[FeatureSnapshot],
        previous_snaps: list[FeatureSnapshot],
        current_meta: dict[str, Any],
        previous_meta: dict[str, Any],
    ) -> list[FeatureLink]:
        """Retorna a lista de FeatureLink representando o diff cross-release.

        Args:
            current_snaps: Features da release mais recente.
            previous_snaps: Features da release anterior.
            current_meta: Metadados da release atual (para nome exibido, etc.).
            previous_meta: Metadados da release anterior.

        Returns:
            Lista de FeatureLink (pode estar vazia se uma das releases não tiver features).
        """
        links: list[FeatureLink] = []
        used_current: set[int] = set()
        used_previous: set[int] = set()

        cur_tokens = [_tokenize_name(s.name) for s in current_snaps]
        prev_tokens = [_tokenize_name(s.name) for s in previous_snaps]

        # ── Passo 1: EXACT — nome e categoria idênticos ──────────────
        for ci, cs in enumerate(current_snaps):
            if ci in used_current:
                continue
            for pi, ps in enumerate(previous_snaps):
                if pi in used_previous:
                    continue
                if cs.name == ps.name and cs.category == ps.category:
                    links.append(
                        FeatureLink(
                            feature_a=cs,
                            feature_b=ps,
                            status=LifecycleStatus.ALIVE,
                            linkage_method=LinkageMethod.EXACT,
                            similarity_score=1.0,
                            notes="Nome e categoria idênticos em ambas as releases.",
                        )
                    )
                    used_current.add(ci)
                    used_previous.add(pi)
                    break

        # ── Passo 2: CATEGORY_CHANGED — mesmo nome, categoria diferente ─
        for ci, cs in enumerate(current_snaps):
            if ci in used_current:
                continue
            for pi, ps in enumerate(previous_snaps):
                if pi in used_previous:
                    continue
                if cs.name == ps.name and cs.category != ps.category:
                    links.append(
                        FeatureLink(
                            feature_a=cs,
                            feature_b=ps,
                            status=LifecycleStatus.CATEGORY_CHANGED,
                            linkage_method=LinkageMethod.EXACT,
                            similarity_score=1.0,
                            notes=(f"Categoria mudou de " f"'{ps.category}' para '{cs.category}'."),
                        )
                    )
                    used_current.add(ci)
                    used_previous.add(pi)
                    break

        # ── Passo 3: FUZZY — Jaccard >= threshold, mesma categoria ───
        for ci, cs in enumerate(current_snaps):
            if ci in used_current:
                continue
            best_score = 0.0
            best_pi: int | None = None
            for pi, ps in enumerate(previous_snaps):
                if pi in used_previous:
                    continue
                score = _jaccard(cur_tokens[ci], prev_tokens[pi])
                if score > best_score and score >= FUZZY_THRESHOLD:
                    if cs.category == ps.category:
                        best_score = score
                        best_pi = pi
            if best_pi is not None:
                ps = previous_snaps[best_pi]
                status: LifecycleStatus = (
                    LifecycleStatus.RENAMED if cs.name != ps.name else LifecycleStatus.ALIVE
                )
                links.append(
                    FeatureLink(
                        feature_a=cs,
                        feature_b=ps,
                        status=status,
                        linkage_method=LinkageMethod.FUZZY,
                        similarity_score=best_score,
                        notes=(
                            f"Match fuzzy (Jaccard={best_score:.2f}) "
                            f"na categoria '{cs.category}'."
                        ),
                    )
                )
                used_current.add(ci)
                used_previous.add(best_pi)

        # ── Passo 4: HEURISTIC — categoria-only, par mais próximo ────
        remaining_cur = [i for i in range(len(current_snaps)) if i not in used_current]
        remaining_prev = [i for i in range(len(previous_snaps)) if i not in used_previous]

        for ci in remaining_cur:
            cs = current_snaps[ci]
            h_best_score = 0.0
            h_best_pi: int | None = None
            for pi in remaining_prev:
                ps = previous_snaps[pi]
                score = _jaccard(cur_tokens[ci], prev_tokens[pi])
                if score > h_best_score:
                    h_best_score = score
                    h_best_pi = pi
            if h_best_pi is not None and h_best_score >= LLM_THRESHOLD_LOW:
                if cs.category == previous_snaps[h_best_pi].category:
                    links.append(
                        FeatureLink(
                            feature_a=cs,
                            feature_b=previous_snaps[h_best_pi],
                            status=LifecycleStatus.RENAMED,
                            linkage_method=LinkageMethod.HEURISTIC,
                            similarity_score=h_best_score,
                            notes=("Match heurístico por categoria e " "similaridade parcial."),
                        )
                    )
                    used_current.add(ci)
                    used_previous.add(h_best_pi)

        # ── Passo 5: LLM — desambiguação para similaridade 0.2–0.5 ───
        if self._llm is not None:
            for ci in range(len(current_snaps)):
                if ci in used_current:
                    continue
                cs = current_snaps[ci]
                for pi in range(len(previous_snaps)):
                    if pi in used_previous:
                        continue
                    ps = previous_snaps[pi]
                    score = _jaccard(cur_tokens[ci], prev_tokens[pi])
                    if LLM_THRESHOLD_LOW <= score < FUZZY_THRESHOLD:
                        try:
                            disambiguation: str | None = self._llm.disambiguate_feature(
                                cs,
                                ps,
                                current_meta,
                                previous_meta,
                            )
                        except AttributeError:
                            # O objeto llm não tem o método esperado — pula.
                            disambiguation = None
                        except Exception as exc:
                            logger.debug(
                                "LLM disambiguation falhou para %s vs %s: %s",
                                cs.name,
                                ps.name,
                                exc,
                            )
                            disambiguation = None

                        if disambiguation:
                            status = (
                                LifecycleStatus.RENAMED
                                if cs.name != ps.name
                                else LifecycleStatus.ALIVE
                            )
                            links.append(
                                FeatureLink(
                                    feature_a=cs,
                                    feature_b=ps,
                                    status=status,
                                    linkage_method=LinkageMethod.LLM,
                                    similarity_score=score,
                                    notes=disambiguation,
                                )
                            )
                            used_current.add(ci)
                            used_previous.add(pi)
                            break

        return links
