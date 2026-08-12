"""Salesforce metadata analyzer for release impact assessment.

Connects to Salesforce org metadata to identify custom objects, triggers,
flows, and permissions that may be impacted by release changes.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class OrgMetadata:
    """Metadata snapshot from a Salesforce org."""

    custom_objects: list[str] = field(default_factory=list)
    triggers: list[str] = field(default_factory=list)
    flows: list[str] = field(default_factory=list)
    permission_sets: list[str] = field(default_factory=list)
    connected_apps: list[str] = field(default_factory=list)
    apex_classes: list[str] = field(default_factory=list)
    lwc_components: list[str] = field(default_factory=list)


@dataclass
class AdoptionSuggestion:
    """A suggestion for adopting a new feature in the context of an org."""

    feature_name: str
    suggestion: str
    priority: str  # "alta", "média", "baixa"
    affected_components: list[str] = field(default_factory=list)


class SalesforceAnalyzer:
    """Analyzes Salesforce org metadata to enrich release analysis.

    Can work with:
    - simple-salesforce library (live connection)
    - Metadata API snapshots
    - Offline metadata dumps (JSON)

    Args:
        sf_connection: Optional simple-salesforce Salesforce instance.
        metadata_cache: Optional pre-loaded metadata dict.
    """

    def __init__(
        self,
        sf_connection: Any | None = None,
        metadata_cache: dict[str, Any] | None = None,
    ) -> None:
        self._sf = sf_connection
        self._cache = metadata_cache or {}
        self._metadata: OrgMetadata | None = None

    async def load_metadata(self) -> OrgMetadata:
        """Load metadata from the org or cache.

        Returns:
            OrgMetadata snapshot.
        """
        if self._metadata:
            return self._metadata

        if self._cache:
            self._metadata = self._parse_cached_metadata(self._cache)
        elif self._sf:
            self._metadata = await self._fetch_metadata_from_org()
        else:
            logger.warning("No Salesforce connection or cache provided")
            self._metadata = OrgMetadata()

        return self._metadata

    async def suggest_adoption(
        self,
        release_features: list[dict[str, Any]],
    ) -> list[AdoptionSuggestion]:
        """Suggest how to adopt release features based on org metadata.

        Args:
            release_features: List of feature dicts with 'name', 'description',
                optionally 'affected_objects', 'category'.

        Returns:
            List of adoption suggestions.
        """
        metadata = await self.load_metadata()
        suggestions: list[AdoptionSuggestion] = []

        for feature in release_features:
            feature_name = feature.get("name", "Unknown")
            affected = feature.get("affected_objects", [])
            category = feature.get("category", "").lower()

            # Check if feature affects custom objects
            impacted_objects = [obj for obj in affected if obj in metadata.custom_objects]

            # Check if feature affects triggers or flows
            impacted_triggers = [t for t in metadata.triggers if any(obj in t for obj in affected)]
            impacted_flows = [f for f in metadata.flows if any(obj in f for obj in affected)]

            affected_components = impacted_objects + impacted_triggers + impacted_flows

            if affected_components:
                suggestions.append(
                    AdoptionSuggestion(
                        feature_name=feature_name,
                        suggestion=(
                            f"Testar em sandbox antes de aplicar em produção. "
                            f"Componentes afetados: {', '.join(affected_components[:5])}"
                        ),
                        priority="alta",
                        affected_components=affected_components,
                    )
                )
            elif category in ("security", "segurança"):
                suggestions.append(
                    AdoptionSuggestion(
                        feature_name=feature_name,
                        suggestion="Revisar configurações de segurança e permissões em sandbox.",
                        priority="alta",
                    )
                )
            elif category in ("api", "development", "desenvolvimento"):
                suggestions.append(
                    AdoptionSuggestion(
                        feature_name=feature_name,
                        suggestion="Verificar integrações e código Apex/LWC que possam ser impactados.",
                        priority="média",
                    )
                )

        return suggestions

    async def generate_impact_report(
        self,
        release_features: list[dict[str, Any]],
    ) -> str:
        """Generate a Markdown impact report for the org.

        Args:
            release_features: List of feature dicts.

        Returns:
            Markdown report string.
        """
        metadata = await self.load_metadata()
        suggestions = await self.suggest_adoption(release_features)

        lines = [
            "# 📊 Relatório de Impacto na Org\n",
            "## Metadados da Org\n",
            f"- **Objetos customizados:** {len(metadata.custom_objects)}",
            f"- **Triggers:** {len(metadata.triggers)}",
            f"- **Flows:** {len(metadata.flows)}",
            f"- **Permission Sets:** {len(metadata.permission_sets)}",
            f"- **Classes Apex:** {len(metadata.apex_classes)}",
            f"- **Componentes LWC:** {len(metadata.lwc_components)}",
            "",
        ]

        if suggestions:
            alta = [s for s in suggestions if s.priority == "alta"]
            media = [s for s in suggestions if s.priority == "média"]
            baixa = [s for s in suggestions if s.priority == "baixa"]

            lines.append("## 🎯 Sugestões de Adoção\n")

            if alta:
                lines.append("### 🔴 Prioridade Alta\n")
                for s in alta:
                    lines.append(f"- **{s.feature_name}**: {s.suggestion}")
                lines.append("")

            if media:
                lines.append("### 🟡 Prioridade Média\n")
                for s in media:
                    lines.append(f"- **{s.feature_name}**: {s.suggestion}")
                lines.append("")

            if baixa:
                lines.append("### 🟢 Prioridade Baixa\n")
                for s in baixa:
                    lines.append(f"- **{s.feature_name}**: {s.suggestion}")
                lines.append("")
        else:
            lines.append("## ✅ Nenhum impacto direto detectado na org\n")

        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Private methods
    # ------------------------------------------------------------------

    def _parse_cached_metadata(self, cache: dict[str, Any]) -> OrgMetadata:
        """Parse cached metadata dict into OrgMetadata."""
        return OrgMetadata(
            custom_objects=cache.get("custom_objects", []),
            triggers=cache.get("triggers", []),
            flows=cache.get("flows", []),
            permission_sets=cache.get("permission_sets", []),
            connected_apps=cache.get("connected_apps", []),
            apex_classes=cache.get("apex_classes", []),
            lwc_components=cache.get("lwc_components", []),
        )

    async def _fetch_metadata_from_org(self) -> OrgMetadata:
        """Fetch metadata from a live Salesforce org via simple-salesforce."""
        if not self._sf:
            return OrgMetadata()

        try:
            # Custom objects
            obj_result = self._sf.query(
                "SELECT QualifiedApiName FROM EntityDefinition "
                "WHERE IsCustomSetting = false AND IsStandardObjectDefinition = false"
            )
            custom_objects = [r["QualifiedApiName"] for r in obj_result.get("records", [])]

            # Apex classes
            class_result = self._sf.query("SELECT Name FROM ApexClass WHERE Status = 'Active'")
            apex_classes = [r["Name"] for r in class_result.get("records", [])]

            # Triggers
            trigger_result = self._sf.query(
                "SELECT Name, TableEnumOrId FROM ApexTrigger WHERE Status = 'Active'"
            )
            triggers = [
                f"{r['Name']} ({r['TableEnumOrId']})" for r in trigger_result.get("records", [])
            ]

            # Flows
            flow_result = self._sf.query(
                "SELECT MasterLabel FROM FlowDefinitionView WHERE IsActive = true"
            )
            flows = [r["MasterLabel"] for r in flow_result.get("records", [])]

            # Permission sets
            ps_result = self._sf.query(
                "SELECT Name FROM PermissionSet WHERE IsOwnedByProfile = false"
            )
            permission_sets = [r["Name"] for r in ps_result.get("records", [])]

            return OrgMetadata(
                custom_objects=custom_objects,
                triggers=triggers,
                flows=flows,
                permission_sets=permission_sets,
                apex_classes=apex_classes,
            )

        except Exception as e:
            logger.error("Failed to fetch metadata from org: %s", e)
            return OrgMetadata()
