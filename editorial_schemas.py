"""
Pydantic Schemas für Stufe 2: Redaktionelle Aufbereitung via Gemini (response_schema).

Gewährleistet:
- Absatz-Trennung nach Plattformen / Themen zur optimalen UX & Lesbarkeit
- Satzweise Bindung an fact_ids aus dem Dossier
- Keine freien URLs im Fließtext
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class EditorialSentence(BaseModel):
    """Einzelner redaktioneller Satz mit verpflichtender Bindung an fact_ids."""

    text: str = Field(
        description="Präzise formulierter deutscher Satz im professionellen Finanzjournalismus-Ton. Anbieternamen bei Ersterwähnung fett schreiben (**Plattform**)."
    )
    fact_ids: list[str] = Field(
        description="Mindestens eine referenzierte fact_id aus dem Dossier (z. B. ['f-robo-02'])",
        min_length=1,
    )


class EditorialParagraph(BaseModel):
    """Absatz zu einer konkreten Plattform oder einem zusammenhängenden Vorgang."""

    platform: str = Field(
        description="Name der behandelten Plattform (z. B. 'Indemo', 'LANDE', 'Revest')"
    )
    sentences: list[EditorialSentence] = Field(
        description="Sätze zu dieser Plattform bzw. diesem Vorgang", min_length=1
    )


class EditorialSection(BaseModel):
    """Thematischer Abschnitt des Newsletters."""

    headline: str = Field(description="Aussagekräftige Überschrift des Abschnitts")
    category: str = Field(
        description="Kategorie, z. B. 'zinsen_aktionen', 'zahlen_statistik', 'regulierung_legal', 'plattform_features'"
    )
    platform_tags: list[str] = Field(description="Im Abschnitt behandelte Plattformen")
    paragraphs: list[EditorialParagraph] = Field(
        default_factory=list,
        description="Getrennte Absätze nach Plattformen/Vorgängen zur optimalen Lesbarkeit (UX)",
    )
    sentences: list[EditorialSentence] = Field(
        default_factory=list,
        description="Optionale flache Satzliste für Rückwärtskompatibilität",
    )


class EditorialNewsletterSchema(BaseModel):
    """Gesamtes redaktionelles Newsletter-Konstrukt."""

    title: str = Field(
        description="Haupttitel der Ausgabe, z. B. 'P2P Kredite Wochenrückblick KW 40/2026'"
    )
    summary_lead: str = Field(
        description="Kurzer Einleitungssatz / Management Summary der wichtigsten Ereignisse"
    )
    sections: list[EditorialSection] = Field(
        description="Themenabschnitte des Newsletters", min_length=1
    )
