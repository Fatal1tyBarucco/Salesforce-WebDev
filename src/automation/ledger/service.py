"""Salesforce Feature Evolution Ledger Service.

Gera o diff em nível de feature entre duas releases consecutivas e mantém
histórico consultável de cada feature através de todas as releases indexadas.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from src.cache_manager import CacheManager
from src.config import RELEASES_DIR
from src.events import get_event_bus

from . import linker
from .models import (
    FeatureHistoryEntry,
    FeatureLink,
    FeatureSnapshot,
    LedgerDiff,
    LedgerStats,
    LifecycleStatus,
    LinkageMethod,
)

logger = logging.getLogger(__name__)

# Namespace e TTL dentro do CacheManager existente do projeto.
LEDGER_NAMESPACE = "sfel"
LEDGER_TTL_SECONDS = 3600  # 1 hora — recompute após cada pipeline run


class FeatureEvolutionLedgerService:
    """Orquestra geração e consulta do Feature Evolution Ledger.

    Responsabilidades:
    1. Extrair features brutas de um release (nome + categoria + snippet).
    2. Linkar features entre duas releases consecutivas via ``linker.FeatureLinker``.
    3. Gerar ``LedgerDiff`` + ``LedgerStats`` e persistir em cache.
    4. Fornecer consulta por nome de feature (histórico completo).
    5. Emitir eventos no ``EventBus`` para dashboard e notificações.
    """

    def __init__(
        self,
        releases_dir: str = RELEASES_DIR,
        cache_dir: str | None = None,
        linker_instance: linker.FeatureLinker | None = None,
        llm_service: Any = None,
    ) -> None:
        """Inicializa o serviço do ledger.

        Args:
            releases_dir: Diretório raiz das releases (padrão: RELEASES_DIR).
            cache_dir: Diretório do cache. Se None, usa ``<releases_dir>/../cache``.
            linker_instance: Instância de FeatureLinker customizada. Se None,
                cria uma nova (com llm_service opcional).
            llm_service: Serviço LLM opcional para desambiguação no linker.
        """
        self._releases_dir = Path(releases_dir)
        cache_path = Path(cache_dir) if cache_dir else self._releases_dir.parent / "cache"
        self._cache = CacheManager(
            cache_dir=cache_path,
            ttl_seconds=LEDGER_TTL_SECONDS,
        )
        self._linker = linker_instance or linker.FeatureLinker(llm_service=llm_service)
        self._bus = get_event_bus()

    # ── Extração ───────────────────────────────────────────────────────

    def _extract_features(self, release_slug: str) -> list[dict[str, Any]]:
        """Extrai features brutas de um release a partir dos arquivos .md.

        Args:
            release_slug: Nome do diretório da release (ex: "summer_26").

        Returns:
            Lista de dicts com as chaves: name, raw_name, category, snippet,
            feature_type, impact.
        """
        release_dir = self._releases_dir / release_slug
        if not release_dir.is_dir():
            return []

        features: list[dict[str, Any]] = []
        for md_path in sorted(release_dir.glob("*.md")):
            if md_path.name.startswith("."):
                continue
            try:
                content = md_path.read_text(encoding="utf-8")
            except OSError:
                logger.warning("Não foi possível ler %s, pulando.", md_path)
                continue

            category = self._extract_category(content)
            for line in content.split("\n"):
                stripped = line.strip()
                if not (stripped.startswith("- ") or stripped.startswith("* ")):
                    continue
                raw_name = stripped[2:].strip()
                if len(raw_name) < 4:
                    continue
                features.append(
                    {
                        "name": self._normalize_name(raw_name),
                        "raw_name": raw_name,
                        "category": category,
                        "snippet": content[:200],
                        "feature_type": "other",
                        "impact": "low",
                    }
                )

        return features

    @staticmethod
    def _extract_category(content: str) -> str:
        """Extrai o nome da primeira categoria (primeiro ## sem emoji).

        Args:
            content: Conteúdo markdown do arquivo.

        Returns:
            Nome da categoria, ou "geral" se não encontrada.
        """
        for line in content.split("\n"):
            stripped = line.strip()
            if stripped.startswith("## ") and not stripped.startswith("## 🔗"):
                return stripped[3:].strip()
        return "geral"

    @staticmethod
    def _normalize_name(name: str) -> str:
        """Normaliza nome de feature para comparação.

        Converte para minúsculas, remove espaços extras e pontuação final.

        Args:
            name: Nome bruto da feature.

        Returns:
            Nome normalizado.
        """
        return name.lower().strip().rstrip(".,;:!?)")

    # ── Geração do Ledger ──────────────────────────────────────────────

    async def generate_ledger(
        self,
        current_slug: str,
        previous_slug: str,
        current_meta: dict[str, Any] | None = None,
        previous_meta: dict[str, Any] | None = None,
    ) -> LedgerDiff:
        """Gera o LedgerDiff entre duas releases consecutivas.

        Extrai features de ambas as releases, executa o linkage e agrega
        os resultados em um LedgerDiff + LedgerStats persistidos em cache.

        Args:
            current_slug: Slug da release mais recente.
            previous_slug: Slug da release anterior.
            current_meta: Metadados opcionais (evita re-leitura do .meta.json).
            previous_meta: Metadados opcionais da release anterior.

        Returns:
            LedgerDiff populado.
        """
        current_features = self._extract_features(current_slug)
        previous_features = self._extract_features(previous_slug)

        now = datetime.now(timezone.utc).isoformat()

        # Converte para FeatureSnapshot
        current_snaps = [
            FeatureSnapshot(
                name=f["name"],
                release_slug=current_slug,
                category=f["category"],
                snippet=f["snippet"],
                feature_type=f["feature_type"],
                impact=f["impact"],
                first_seen=now,
                last_seen=now,
            )
            for f in current_features
        ]
        previous_snaps = [
            FeatureSnapshot(
                name=f["name"],
                release_slug=previous_slug,
                category=f["category"],
                snippet=f["snippet"],
                feature_type=f["feature_type"],
                impact=f["impact"],
                first_seen=now,
                last_seen=now,
            )
            for f in previous_features
        ]

        # Executa o linkage
        links = self._linker.link(
            current_snaps,
            previous_snaps,
            current_meta or {},
            previous_meta or {},
        )

        # Agrega por status
        born: list[FeatureSnapshot] = []
        alive: list[FeatureSnapshot] = []
        renamed: list[FeatureLink] = []
        category_changed: list[FeatureLink] = []
        deprecated: list[FeatureSnapshot] = []
        removed: list[FeatureSnapshot] = []
        method_counts: dict[str, int] = {}
        linked_current_names: set[str] = set()
        linked_previous_names: set[str] = set()

        for link in links:
            linked_current_names.add(link.feature_a.name)
            linked_previous_names.add(link.feature_b.name)
            method_counts[link.linkage_method.value] = (
                method_counts.get(
                    link.linkage_method.value,
                    0,
                )
                + 1
            )

            status = link.status
            if status == LifecycleStatus.BORN:
                born.append(link.feature_a)
            elif status == LifecycleStatus.ALIVE:
                alive.append(link.feature_a)
            elif status == LifecycleStatus.RENAMED:
                renamed.append(link)
            elif status == LifecycleStatus.CATEGORY_CHANGED:
                category_changed.append(link)
            elif status == LifecycleStatus.DEPRECATED:
                deprecated.append(link.feature_b)
            elif status == LifecycleStatus.REMOVED:
                removed.append(link.feature_b)

        # Features não linkadas = born (current) ou removed (previous)
        for snap in current_snaps:
            if snap.name not in linked_current_names:
                born.append(snap)
        for snap in previous_snaps:
            if snap.name not in linked_previous_names:
                removed.append(snap)

        # Determina os nomes exibidos
        if current_meta:
            current_name = current_meta.get("name", current_slug)
        else:
            current_name = current_slug
        if previous_meta:
            previous_name = previous_meta.get("name", previous_slug)
        else:
            previous_name = previous_slug

        diff = LedgerDiff(
            current_slug=current_slug,
            previous_slug=previous_slug,
            current_name=current_name,
            previous_name=previous_name,
            born=born,
            alive=alive,
            renamed=renamed,
            category_changed=category_changed,
            deprecated=deprecated,
            removed=removed,
            total_current_features=len(current_snaps),
            total_previous_features=len(previous_snaps),
            generated_at=now,
        )

        stats = LedgerStats(
            current_slug=current_slug,
            previous_slug=previous_slug,
            total_features_current=diff.total_current_features,
            total_features_previous=diff.total_previous_features,
            born_count=len(born),
            alive_count=len(alive),
            renamed_count=len(renamed),
            category_changed_count=len(category_changed),
            deprecated_count=len(deprecated),
            removed_count=len(removed),
            linkage_method_counts=method_counts,
            unlinked_previous=[
                s.name for s in previous_snaps if s.name not in linked_previous_names
            ],
            unlinked_current=[s.name for s in current_snaps if s.name not in linked_current_names],
        )

        # Persiste em cache
        cache_key = f"{current_slug}..{previous_slug}"
        try:
            self._cache.set(
                cache_key,
                diff.model_dump(),
                namespace=LEDGER_NAMESPACE,
            )
        except Exception:
            logger.warning(
                "Falha ao cachear ledger %s..%s — prosseguindo sem cache.",
                current_slug,
                previous_slug,
            )

        stats_key = f"stats:{cache_key}"
        try:
            self._cache.set(
                stats_key,
                stats.model_dump(),
                namespace=LEDGER_NAMESPACE,
            )
        except Exception:
            logger.warning(
                "Falha ao cachear stats %s..%s — prosseguindo.",
                current_slug,
                previous_slug,
            )

        # Emite evento
        try:
            await self._bus.emit(
                "ledger.generated",
                {
                    "current_slug": current_slug,
                    "previous_slug": previous_slug,
                    "born": len(born),
                    "removed": len(removed),
                    "renamed": len(renamed),
                    "category_changed": len(category_changed),
                },
                source="sfel",
            )
        except Exception:
            # O EventBus pode não estar configurado em todos os ambientes.
            logger.debug(
                "Falha ao emitir evento ledger.generated — ignorando.",
            )

        return diff

    # ── Cache lookup ──────────────────────────────────────────────────

    def get_cached_ledger(
        self,
        current_slug: str,
        previous_slug: str,
    ) -> LedgerDiff | None:
        """Retorna o LedgerDiff em cache, ou None se expirado/inválido.

        Args:
            current_slug: Slug da release mais recente.
            previous_slug: Slug da release anterior.

        Returns:
            LedgerDiff deserializado, ou None.
        """
        cache_key = f"{current_slug}..{previous_slug}"
        data = self._cache.get(cache_key, namespace=LEDGER_NAMESPACE)
        if data is None:
            return None

        try:
            return LedgerDiff.model_validate(data)
        except ValidationError:
            logger.warning(
                "Ledger em cache para %s..%s está inválido — regenerando.",
                current_slug,
                previous_slug,
            )
            self._cache.invalidate(cache_key, namespace=LEDGER_NAMESPACE)
            return None

    def get_cached_stats(
        self,
        current_slug: str,
        previous_slug: str,
    ) -> LedgerStats | None:
        """Retorna as estatísticas do ledger em cache, ou None.

        Args:
            current_slug: Slug da release mais recente.
            previous_slug: Slug da release anterior.

        Returns:
            LedgerStats deserializado, ou None.
        """
        stats_key = f"stats:{current_slug}..{previous_slug}"
        data = self._cache.get(stats_key, namespace=LEDGER_NAMESPACE)
        if data is None:
            return None
        try:
            return LedgerStats.model_validate(data)
        except ValidationError:
            logger.warning(
                "Stats em cache para %s..%s inválido — regenerando.",
                current_slug,
                previous_slug,
            )
            self._cache.invalidate(stats_key, namespace=LEDGER_NAMESPACE)
            return None

    # ── Histórico de uma feature ──────────────────────────────────────

    async def get_feature_history(self, feature_name: str) -> FeatureHistoryEntry:
        """Retorna o histórico completo de uma feature através de todas as releases.

        Percorre releases em ordem cronológica (release_id) e constroí a
        timeline completa da feature.

        Args:
            feature_name: Nome da feature (será normalizado internamente).

        Returns:
            FeatureHistoryEntry com a timeline completa.
        """
        norm = self._normalize_name(feature_name)
        all_metas = self._load_all_metas_sorted()
        entries: list[FeatureSnapshot] = []
        tracked_name = norm

        for meta in all_metas:
            slug = meta.get("slug", "")
            if not slug:
                continue
            features = self._extract_features(slug)
            matched = [f for f in features if f["name"] == tracked_name]
            if not matched and entries:
                # Nome sumiu desta release — tenta seguir uma renomeação.
                matched = self._follow_rename(features, entries[-1], slug, meta)
            for f in matched:
                ts = meta.get("generated_at", "") or now_iso()
                tracked_name = str(f["name"])
                entries.append(
                    FeatureSnapshot(
                        name=str(f["name"]),
                        release_slug=slug,
                        category=f["category"],
                        snippet=f["snippet"],
                        feature_type=f["feature_type"],
                        impact=f["impact"],
                        first_seen=ts,
                        last_seen=ts,
                    ),
                )

        total_seen = len(entries)
        current_status: LifecycleStatus = LifecycleStatus.ALIVE
        removed_in: str | None = None

        if total_seen == 0:
            return FeatureHistoryEntry(
                feature_name=feature_name,
                entries=[],
                current_status=LifecycleStatus.REMOVED,
                total_releases_seen=0,
                removed_in=None,
            )

        # Determina status atual comparando os dois últimos snapshots
        if total_seen >= 2:
            prev = entries[-2]
            curr = entries[-1]
            # Se o nome mudou entre os dois últimos registros → RENAMED
            if prev.name != curr.name:
                current_status = LifecycleStatus.RENAMED
            # Se nome igual mas categoria mudou → CATEGORY_CHANGED
            elif prev.category != curr.category:
                current_status = LifecycleStatus.CATEGORY_CHANGED
            # Senão → ALIVE (pode ser BORN se for o primeiro release, mas
            # escolhemos ALIVE por padrão pois é o comportamento mais seguro)
            else:
                current_status = LifecycleStatus.ALIVE
        # Se só há 1 registro e não é no último release → REMOVED
        last_slug = all_metas[-1].get("slug", "") if all_metas else ""
        if total_seen == 1 and entries[0].release_slug != last_slug:
            removed_in = entries[0].release_slug
            current_status = LifecycleStatus.REMOVED

        return FeatureHistoryEntry(
            feature_name=feature_name,
            entries=entries,
            current_status=current_status,
            total_releases_seen=total_seen,
            removed_in=removed_in,
        )

    def _follow_rename(
        self,
        features: list[dict[str, Any]],
        previous: FeatureSnapshot,
        slug: str,
        meta: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Tenta seguir uma renomeação da feature rastreada.

        Quando o nome normalizado não aparece em uma release, pergunta ao
        ``FeatureLinker`` se a feature foi renomeada. Só aceita matches
        FUZZY (Jaccard >= 0.5 e mesma categoria), a mesma regra que
        ``generate_ledger`` usa para classificar uma transição como
        RENAMED — matches heurísticos de baixa confiança são ignorados.

        Args:
            features: Features extraídas da release atual.
            previous: Último snapshot conhecido da feature rastreada.
            slug: Slug da release atual.
            meta: Metadados da release atual.

        Returns:
            Features da release atual que dão continuidade à feature
            rastreada, ou lista vazia se nenhuma renomeação foi detectada.
        """
        ts = meta.get("generated_at", "") or now_iso()
        current_snaps = [
            FeatureSnapshot(
                name=f["name"],
                release_slug=slug,
                category=f["category"],
                snippet=f["snippet"],
                feature_type=f["feature_type"],
                impact=f["impact"],
                first_seen=ts,
                last_seen=ts,
            )
            for f in features
        ]
        for link in self._linker.link(current_snaps, [previous], meta, {}):
            if link.linkage_method == LinkageMethod.FUZZY:
                return [f for f in features if f["name"] == link.feature_a.name]
        return []

    def _load_all_metas_sorted(self) -> list[dict[str, Any]]:
        """Carrega .meta.json de todos os releases ordenados por release_id.

        Returns:
            Lista de dicts com os metadados, cada um com a chave 'slug' adicionada.
        """
        metas: list[dict[str, Any]] = []
        base = self._releases_dir
        if not base.is_dir():
            return metas

        for d in sorted(base.iterdir()):
            if not d.is_dir():
                continue
            meta_path = d / ".meta.json"
            if meta_path.is_file():
                try:
                    meta: dict[str, Any] = json.loads(
                        meta_path.read_text(encoding="utf-8"),
                    )
                    meta["slug"] = d.name
                    metas.append(meta)
                except (json.JSONDecodeError, OSError):
                    logger.debug(
                        "Não foi possível carregar %s, pulando.",
                        meta_path,
                    )
                    continue

        metas.sort(key=lambda m: m.get("release_id", 0))
        return metas

    # ── Invalidação ────────────────────────────────────────────────────

    def invalidate(self, current_slug: str, previous_slug: str) -> None:
        """Remove do cache o ledger e os stats para um pair de releases.

        Args:
            current_slug: Slug da release mais recente.
            previous_slug: Slug da release anterior.
        """
        cache_key = f"{current_slug}..{previous_slug}"
        self._cache.invalidate(cache_key, namespace=LEDGER_NAMESPACE)
        self._cache.invalidate(
            f"stats:{cache_key}",
            namespace=LEDGER_NAMESPACE,
        )

    def clear_all(self) -> int:
        """Remove todo o cache do ledger.

        Returns:
            Número de entries removidos.
        """
        return self._cache.invalidate_namespace(LEDGER_NAMESPACE)


# ── Helper ──────────────────────────────────────────────────────────────


def now_iso() -> str:
    """Retorna timestamp ISO atual com timezone UTC."""
    return datetime.now(timezone.utc).isoformat()
