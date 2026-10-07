"""
P2P Platform Audit Scoring System - Pydantic Datenmodelle

Implementiert das mathematische Nettomodell:
- 4 Basissäulen (je 0-25 Punkte = max 100 Punkte Rohscore)
- Deterministische Modifikatoren-Matrix innerhalb der Bänder
- Strikte Malus-Abschläge (Monokultur, Fristen-Mismatch, Related-Party, Distressed)
- Risikoklassen & Allokationsmatrix
- Transparenz-Flags (Option 1 & 4, Vorsichtsprinzip bei Konflikten & Datenlücken)
- Externe Benchmark-Metriken (P2P Empire, Lars Wrobbel) zur Triangulierung
"""

from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field

# ==============================================================================
# 1. Risikoklassen & Allokation
# ==============================================================================

RiskClass = Literal["TOP TIER", "MID RISK", "WATCHLIST", "SPECULATIVE", "DISTRESSED"]

RISK_CLASS_LIMITS: Dict[RiskClass, str] = {
    "TOP TIER": "8 - 15 %",
    "MID RISK": "5 - 8 %",
    "WATCHLIST": "0 - 3 %",
    "SPECULATIVE": "0 % (Neuanlage-Stopp)",
    "DISTRESSED": "0 % (Kapitalabzug & Recovery)",
}

RISK_CLASS_RECOMMENDATIONS: Dict[RiskClass, str] = {
    "TOP TIER": "Kerninvestment: 1st-Rank Hypotheken, segregierte Treuhandkonten, 0 % Verlusthistorie.",
    "MID RISK": "Solide Beimischung: Hohe Bonität/Historie, aber unbesicherte Konsumkredite oder Monokulturen.",
    "WATCHLIST": "Taktische Position unter Vorbehalt: Schwächen bei LTV, fehlende Testate oder Governance-Risse.",
    "SPECULATIVE": "Neuanlage-Stopp: Intransparenz, Holding-Konstrukte, Restrukturierungen oder Pending Payments.",
    "DISTRESSED": "Kapitalabzug & Workout: Notleidende Portfolios (NPL >40%), blockierte Zweitmärkte, Moratorien.",
}


def determine_risk_class(net_score: int) -> RiskClass:
    """Weist dem Netto-Score die regulatorische Risikoklasse zu."""
    if net_score >= 70:
        return "TOP TIER"
    if net_score >= 60:
        return "MID RISK"
    if net_score >= 51:
        return "WATCHLIST"
    if net_score >= 40:
        return "SPECULATIVE"
    return "DISTRESSED"


# ==============================================================================
# 2. Externe Benchmark-Metriken (Triangulierung)
# ==============================================================================


class BenchmarkMetrics(BaseModel):
    """Externe Experten-Ratings zur Triangulierung und Plausibilitätsprüfung."""

    p2p_empire_safety_score: Optional[float] = Field(
        None, description="P2P Empire Safety Score (0.0 - 10.0)"
    )
    p2p_empire_safety_band: Optional[str] = Field(
        None, description="Hoch, Mittel, Niedrig"
    )
    p2p_empire_portfolio_perf: Optional[float] = Field(
        None, description="Aktuelle Portfolio Performance in %"
    )
    p2p_empire_avg_return: Optional[str] = Field(
        None, description="Historische Ø Rendite"
    )
    p2p_game_score: Optional[int] = Field(
        None, description="P2P-Game Gesamtscore (0 - 100)"
    )
    p2p_game_rank: Optional[str] = Field(
        None, description="Platzierung im P2P-Game Rating (z. B. Platz 1 von 40)"
    )
    rethink_p2p_score: Optional[float] = Field(
        None, description="re:think P2P Risk Score (z. B. 8.4 / 10)"
    )
    rethink_p2p_rank: Optional[str] = Field(
        None, description="Platzierung im re:think P2P Sicherheitsranking"
    )
    rethink_p2p_red_flags: Optional[str] = Field(
        None, description="re:think P2P Risikofaktoren / Malus Abzug (z. B. -19)"
    )
    lars_wrobbel_score: Optional[int] = Field(
        None, description="Lars Wrobbel Gesamtpunkte (0 - 40)"
    )
    lars_wrobbel_rank: Optional[str] = Field(
        None, description="Rangliste bei Passives Einkommen"
    )
    external_review_urls: List[str] = Field(
        default_factory=list, description="Links zu externen Analysen"
    )


# ==============================================================================
# 3. Transparenz-Flags & Audit-Metadaten
# ==============================================================================

SourcingStrategy = Literal[
    "auto_crawled", "hybrid_primary_secondary", "curated_profile_and_secondary_audits"
]


class EvidenceMetadata(BaseModel):
    """Offenlegung der Datengrundlage gemäß Nutzerentscheidung Option 1 & 4."""

    sourcing_strategy: SourcingStrategy = Field(
        default="curated_profile_and_secondary_audits",
        description="Verwendete Evidenz-Methode: [AUTO], [HYBRID] oder [CURATED]",
    )
    primary_crawled_pages: int = Field(
        default=0, description="Anzahl direkt gecrawlter Plattformseiten"
    )
    curated_profile_used: bool = Field(
        default=False, description="Wurde ein kuratiertes profile.yaml verwendet?"
    )
    secondary_reviews_count: int = Field(
        default=0, description="Anzahl einbezogener Blogger-Erfahrungsberichte"
    )
    spa_detected: bool = Field(
        default=False, description="Wurde clientseitiges JavaScript-Rendering erkannt?"
    )
    spa_handling_note: Optional[str] = Field(
        default=None, description="Erläuterung zur SPA-Faktenbasis"
    )


class AuditFlags(BaseModel):
    """Vorsichtsprinzip-Flags bei Unklarheiten und Datenlücken."""

    has_conflict: bool = Field(
        default=False, description="Liegen widersprüchliche Angaben vor?"
    )
    conflict_notes: List[str] = Field(
        default_factory=list,
        description="Erläuterung der Widersprüche (z. B. Treuhand unklar)",
    )
    data_gaps: List[str] = Field(
        default_factory=list,
        description="Fehlende Belege, die zum Minimalpunktwert führten",
    )
    sourcing_strategy: str = Field(
        default="curated_profile_and_secondary_audits", description="Sourcing-Strategie"
    )


# ==============================================================================
# 4. Extrahierte Plattform-Fakten (LLM Extraktions-Schema)
# ==============================================================================


class ModifierEvaluation(BaseModel):
    """Einzelner Zu- oder Abschlag innerhalb eines Säulen-Bandes."""

    name: str = Field(..., description="Kurzbezeichnung des Kriteriums")
    points: int = Field(..., description="Delta (+2, -2, -3 etc.)")
    condition_met: bool = Field(..., description="Kriterium erfüllt?")
    rationale: str = Field(..., description="Begründung und Belegstelle")


class PillarFactExtract(BaseModel):
    """Strukturierte Faktenbasis für eine Säule."""

    band_id: str = Field(
        ..., description="Identifiziertes Band (z. B. 'Band_21_25', 'Band_6_13')"
    )
    base_score: int = Field(..., description="Fixer Median-Basiswert des Bandes")
    modifiers: List[ModifierEvaluation] = Field(
        default_factory=list, description="Angewendete Modifikatoren"
    )
    final_score: int = Field(..., description="Berechneter Säulenwert (0-25)")
    rating_label: str = Field(
        ..., description="Verbale Bewertung (z. B. 'Sehr gut', 'Unreguliert')"
    )
    evidence_text: str = Field(
        ..., description="Zusammenfassung mit Belegen und Zitaten"
    )


# ==============================================================================
# 5. Malus-Abzüge
# ==============================================================================

MalusType = Literal["monoculture", "term_mismatch", "related_party", "distressed"]


class MalusItem(BaseModel):
    """Strukturierter Punktabzug aus dem Malus-System."""

    type: MalusType = Field(..., description="Typ des Malus")
    name: str = Field(..., description="Vollständiger Name des Malus")
    penalty: int = Field(..., description="Negativer Punktwert (-4 bis -20)")
    trigger_detected: bool = Field(
        ..., description="Wurde der Schwellenwert überschritten?"
    )
    trigger_detail: str = Field(
        ..., description="Konkreter Auslöser (z. B. 'Aventus >85% des Volumens')"
    )
    evidence_quote: str = Field(..., description="Wörtliches Zitat oder Datenquelle")


# ==============================================================================
# 6. Factsheet-Gesamtschema (YAML Frontmatter & Ingestion)
# ==============================================================================


class FactsheetFrontmatter(BaseModel):
    """Vollständiges Schema für das maschinenlesbare YAML Frontmatter eines Factsheets."""

    platform: str = Field(..., description="Eindeutige Plattform-ID (z. B. 'esketit')")
    platform_name: str = Field(..., description="Offizieller Name (z. B. 'Esketit')")
    audit_date: str = Field(..., description="Audit-Datum im Format YYYY-MM-DD")
    audit_version: str = Field("1.0", description="Schema-Version")

    # Gesamt-Score & Klassifikation
    audit_score: Dict[str, Any] = Field(
        ...,
        description="net_score, raw_score, risk_class, portfolio_limit, recommendation",
    )

    flags: AuditFlags = Field(default_factory=lambda: AuditFlags())
    evidence_metadata: EvidenceMetadata = Field(
        default_factory=lambda: EvidenceMetadata()
    )
    benchmarks: Optional[BenchmarkMetrics] = None

    # Die 4 Säulen
    pillars: Dict[str, PillarFactExtract] = Field(
        ...,
        description="pillar_1_regulation, pillar_2_solvency, pillar_3_collateral, pillar_4_liquidity",
    )

    # Malus-Abzüge
    malus_deductions: List[MalusItem] = Field(default_factory=list)

    # Quellenverzeichnis
    sources: List[Dict[str, str]] = Field(default_factory=list)


# ==============================================================================
# 7. Ranking Snapshot (für SQLite & Master-Ranking)
# ==============================================================================


class PlatformAuditSnapshot(BaseModel):
    """Historischer Audit-Datensatz für die SQLite-Tabelle platform_audit_scores."""

    platform: str
    audit_date: str
    raw_score: int
    net_score: int
    risk_class: RiskClass
    pillar_1: int
    pillar_2: int
    pillar_3: int
    pillar_4: int
    malus_total: int
    malus_json: str
    has_conflict: bool
    conflict_notes: Optional[str] = None
    data_gaps_json: Optional[str] = None
    sourcing_strategy: str
    factsheet_path: str
