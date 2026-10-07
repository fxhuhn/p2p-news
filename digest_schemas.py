"""
Pydantic Schemas für Stufe 1: Strukturierte Fakten-Extraktion via Gemini (response_schema).
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class FactEvidence(BaseModel):
    """Belegzitat für einen Fakt aus einem konkreten News-Item."""

    item_id: str = Field(description="ID des referenzierten News-Items")
    evidence_quote: str = Field(
        description="Wörtliches Zitat aus dem Quell-Item, das die Aussage belegt"
    )


class ExtractedFact(BaseModel):
    """Einzelner, belegter Fakt."""

    fact_id: str = Field(description="Eindeutige ID des Fakts, z. B. 'f-01'")
    statement: str = Field(description="Präzise, faktenbasierte Kernaussage")
    evidence: list[FactEvidence] = Field(
        description="Liste von Zitaten zur Untermauerung", min_length=1
    )
    verified: bool = Field(default=True, description="Wird von Verifier 1 gesetzt")


class TopicCluster(BaseModel):
    """Thematischer Cluster, der mehrere Meldungen zusammenfasst."""

    cluster_id: str = Field(
        description="Eindeutige ID des Clusters, z. B. 'c-esketit-goodeve'"
    )
    topic: str = Field(
        description="Haupt-Themenkategorie, z. B. 'regulierung_legal', 'zinsen_aktionen', 'risiko_ausfaelle', 'zahlen_statistik'"
    )
    platforms: list[str] = Field(description="Betroffene P2P-Plattformen")
    title: str = Field(description="Aussagekräftige Überschrift des Clusters")
    facts: list[ExtractedFact] = Field(
        description="Extrahierte Fakten zu diesem Cluster", min_length=1
    )
    conflicts: list[str] = Field(
        default_factory=list,
        description="Erkannte Widersprüche oder Abweichungen zwischen Quellen",
    )


class WeeklyDigestSchema(BaseModel):
    """Gesamt-Dossier aller extrahierten Fakten einer Woche / Periode."""

    schema_version: str = Field(default="2.2", description="Version des Schemas")
    iso_week: str = Field(description="Kalenderwoche, z. B. '2026-W40'")
    clusters: list[TopicCluster] = Field(description="Liste thematischer Cluster")
