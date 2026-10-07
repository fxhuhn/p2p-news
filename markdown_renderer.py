"""
Deterministischer Markdown-Renderer für Stufe 2.

Baut aus dem validierten EditorialNewsletterSchema das finale Markdown-Dokument.
Wichtig: Das LLM schreibt niemals URLs oder Quellenlisten selbst!
Alle Links werden deterministisch aus den verifizierten fact_ids und NewsItems gerendert.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any

from digest_schemas import WeeklyDigestSchema
from editorial_schemas import EditorialNewsletterSchema, EditorialSentence
from item_models import NewsItem


class MarkdownRenderer:
    """Rendert verifizierte redaktionelle Newsletter in druckreifes Markdown."""

    @staticmethod
    def _ensure_platform_bolded(text: str, platform: str) -> str:
        """Stellt sicher, dass der Plattformname bei Ersterwähnung fett (**Plattform**) formatiert ist."""
        if not platform or not text:
            return text
        plat = platform.strip()
        escaped = re.escape(plat)
        # Wenn bereits gefettet, unverändert lassen
        if re.search(rf"\*\*{escaped}\*\*", text, flags=re.IGNORECASE):
            return text
        pattern = rf"(?<!\*)\b({escaped})\b(?!\*)"
        if not re.search(r"^\w", plat) or not re.search(r"\w$", plat):
            pattern = rf"(?<!\*)({escaped})(?!\*)"
        return re.sub(pattern, r"**\1**", text, count=1, flags=re.IGNORECASE)

    def render(
        self,
        newsletter: EditorialNewsletterSchema,
        digest: WeeklyDigestSchema,
        items_map: dict[str, NewsItem],
        run_id: str = "",
        iso_week: str = "",
        verified_facts_count: int = 0,
        verified_sentences_count: int = 0,
    ) -> str:
        # Erstelle Mapping von fact_id zu Liste von NewsItems
        fact_to_items: dict[str, list[NewsItem]] = {}
        fact_to_cluster: dict[str, Any] = {}
        for cluster in digest.clusters:
            for fact in cluster.facts:
                fact_to_cluster[fact.fact_id] = cluster
                items_for_fact: list[NewsItem] = []
                for ev in fact.evidence:
                    item = items_map.get(ev.item_id)
                    if item and item not in items_for_fact:
                        items_for_fact.append(item)
                fact_to_items[fact.fact_id] = items_for_fact

        # 1. YAML Frontmatter
        frontmatter = [
            "---",
            f"title: '{newsletter.title}'",
            f"iso_week: '{iso_week}'",
            f"generated_at: '{datetime.now(timezone.utc).isoformat()}'",
            f"run_id: '{run_id}'",
            f"verified_facts_count: {verified_facts_count}",
            f"verified_sentences_count: {verified_sentences_count}",
            "schema_version: '2.2'",
            "---",
            "",
        ]

        # 2. Header & Einleitung
        body = [
            f"# {newsletter.title}",
            "",
            f"> **Kompakt-Briefing:** {newsletter.summary_lead}",
            "",
            "---",
            "",
        ]

        # 3. Abschnitte
        for sec in newsletter.sections:
            body.append(f"## {sec.headline}")
            tags = ", ".join(sec.platform_tags) if sec.platform_tags else "Allgemein"
            body.append(f"*Kategorie: `{sec.category}` | Plattformen: **{tags}***\n")

            # Sammle alle Sätze für Quellen- und Konfliktreferenzierung
            all_sentences: list[EditorialSentence] = []

            # Fließtext: Getrennte Absätze nach Plattformen/Vorgängen (UX)
            if sec.paragraphs:
                for para in sec.paragraphs:
                    p_text = " ".join(s.text.strip() for s in para.sentences)
                    if para.platform:
                        p_text = self._ensure_platform_bolded(p_text, para.platform)
                    body.append(f"{p_text}\n")
                    all_sentences.extend(para.sentences)
            elif sec.sentences:
                paragraph_text = " ".join(s.text.strip() for s in sec.sentences)
                body.append(f"{paragraph_text}\n")
                all_sentences.extend(sec.sentences)

            # Relevante Items und Quellen sammeln
            used_items: list[NewsItem] = []
            section_conflicts: list[str] = []

            for s in all_sentences:
                for f_id in s.fact_ids:
                    cluster_obj = fact_to_cluster.get(f_id)
                    if cluster_obj and cluster_obj.conflicts:
                        for c in cluster_obj.conflicts:
                            if c not in section_conflicts:
                                section_conflicts.append(c)

                    for itm in fact_to_items.get(f_id, []):
                        if itm not in used_items:
                            used_items.append(itm)

            # Widersprüche / Abweichungen anzeigen
            if section_conflicts:
                body.append("> ⚠️ **Abweichende Berichte zwischen Quellen:**")
                for c in section_conflicts:
                    body.append(f"> - {c}")
                body.append("")

            # Quellenverzeichnis deterministisch rendern
            if used_items:
                body.append("**Geprüfte Quellen:**")
                for itm in used_items:
                    tier_badge = (
                        "Primärquelle"
                        if itm.source_tier == "primary"
                        else "Sekundärquelle"
                    )
                    body.append(
                        f"- [{itm.title}]({itm.url}) *({itm.provider}, {tier_badge})*"
                    )
                body.append("")

            body.append("---\n")

        # 4. Fußzeile & Revisionshinweis
        footer = [
            "### Revisions- & Prüfnachweis",
            f"- **Woche:** {iso_week} | **Run-ID:** `{run_id}`",
            f"- **Verifizierte Fakten:** {verified_facts_count} (alle durch Roh-Snapshots belegt)",
            "- **Integrität:** Deterministisch gerendert aus schema-validierten Fakten.",
            "- *Hinweis: Dieser Newsletter dient ausschließlich Informationszwecken und stellt keine Anlageberatung dar.*",
            "",
        ]

        return "\n".join(frontmatter + body + footer)
