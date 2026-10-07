"""
Fakten-Verifier 2 (Stufe 2).

Prüft den redaktionell erstellten Newsletter satzweise gegen das Fakten-Dossier:
1. Existenz jeder referenzierten fact_id
2. Satzweiser Zahlen-Abgleich (alle Zahlen eines Satzes müssen in seinen referenzierten Fakten vorkommen)
3. Whitelist für strukturelle Metadaten (Jahreszahlen, Kalenderwochen)
"""

from __future__ import annotations

import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path

from digest_schemas import ExtractedFact, WeeklyDigestSchema
from editorial_schemas import (
    EditorialNewsletterSchema,
    EditorialParagraph,
    EditorialSection,
    EditorialSentence,
)

logger = logging.getLogger("verifier_stage2")

STRUCTURAL_WHITELIST_NUMBERS: set[str] = {
    # Typische Jahreszahlen
    "2023",
    "2024",
    "2025",
    "2026",
    "2027",
    "2028",
    # Kalendertage (1-31) und Zähler
    *(str(i) for i in range(1, 32)),
    # Typische Wochennummern (KW 1-53)
    *(str(i) for i in range(35, 54)),
}


def extract_numbers_from_text(text: str) -> set[str]:
    """
    Extrahiert Zahlen, Prozentwerte und Geldbeträge aus einem Text.
    Normalisiert Punkte und Kommas (z. B. '4.073.350' -> '4073350', '12,58' -> '12.58').
    Erkennt auch Datumsangaben (z. B. '18.08.2026') und extrahiert Tag, Monat und Jahr.
    """
    matches = re.findall(r"\b\d+(?:[.,]\d+)*%?\b", text)
    cleaned = set()
    for m in matches:
        raw = m.rstrip("%")
        # Datumserkennung: z. B. 18.08.2026 oder 24.09.2026
        date_parts = re.match(r"^(\d{1,2})\.(\d{1,2})\.(\d{2,4})$", raw)
        if date_parts:
            d, mo, yr = date_parts.groups()
            cleaned.add(d)
            cleaned.add(str(int(d)))
            cleaned.add(mo)
            cleaned.add(str(int(mo)))
            cleaned.add(yr)
            cleaned.add(raw)
            continue

        # Deutsche Tausenderpunkte entfernen: 4.073.350 -> 4073350
        if "." in raw and "," not in raw and len(raw.split(".")[-1]) == 3:
            norm = raw.replace(".", "")
        else:
            norm = raw.replace(".", "").replace(",", ".")
        cleaned.add(norm)
        cleaned.add(raw)  # Auch Rohform behalten
    return cleaned


class Stage2Verifier:
    """Validiert generierte redaktionelle Sätze gegen das Fakten-Dossier."""

    def __init__(
        self, log_path: Path | str = "data/logs/rejected-sentences.jsonl"
    ) -> None:
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def _validate_sentence(
        self,
        sentence: EditorialSentence,
        facts_map: dict[str, ExtractedFact],
        whitelist: set[str],
    ) -> tuple[bool, list[str]]:
        reasons: list[str] = []
        is_valid = True

        # 1. Fact-ID Prüfung
        if not sentence.fact_ids:
            is_valid = False
            reasons.append("Keine fact_ids referenziert")
            return is_valid, reasons

        referenced_facts: list[ExtractedFact] = []
        for f_id in sentence.fact_ids:
            fact_obj = facts_map.get(f_id)
            if not fact_obj:
                is_valid = False
                reasons.append(f"fact_id '{f_id}' existiert nicht im Dossier")
            else:
                referenced_facts.append(fact_obj)

        if not is_valid:
            return is_valid, reasons

        # 2. Satzweiser Zahlen-Abgleich
        sentence_numbers = extract_numbers_from_text(sentence.text)
        fact_numbers: set[str] = set()
        for rf in referenced_facts:
            fact_numbers.update(extract_numbers_from_text(rf.statement))
            for ev in rf.evidence:
                fact_numbers.update(extract_numbers_from_text(ev.evidence_quote))

        unsupported_numbers = []
        for s_num in sentence_numbers:
            if s_num not in fact_numbers and s_num not in whitelist:
                unsupported_numbers.append(s_num)

        if unsupported_numbers:
            is_valid = False
            reasons.append(
                f"Zahlen {unsupported_numbers} im Satz nicht durch Fakten {sentence.fact_ids} belegt"
            )

        return is_valid, reasons

    def verify_newsletter(
        self,
        newsletter: EditorialNewsletterSchema,
        digest: WeeklyDigestSchema,
        run_id: str = "",
        extra_whitelist_numbers: set[str] | None = None,
    ) -> tuple[EditorialNewsletterSchema, int, int]:
        """
        Validiert alle Sätze und Abschnitte des Newsletters.
        Unterstützt sowohl sec.paragraphs als auch sec.sentences.

        Gibt zurück:
        (validierter_newsletter, anzahl_verifiziert, anzahl_abgelehnt)
        """
        # Erstelle Fact-Lookup Map
        facts_map: dict[str, ExtractedFact] = {}
        for cluster in digest.clusters:
            for fact in cluster.facts:
                facts_map[fact.fact_id] = fact

        whitelist = STRUCTURAL_WHITELIST_NUMBERS.union(extra_whitelist_numbers or set())

        verified_sentences = 0
        rejected_sentences = 0
        verified_sections: list[EditorialSection] = []

        for sec in newsletter.sections:
            valid_paragraphs: list[EditorialParagraph] = []
            valid_sentences: list[EditorialSentence] = []

            if sec.paragraphs:
                for para in sec.paragraphs:
                    valid_para_sentences: list[EditorialSentence] = []
                    for sentence in para.sentences:
                        is_valid, reasons = self._validate_sentence(
                            sentence=sentence,
                            facts_map=facts_map,
                            whitelist=whitelist,
                        )
                        if is_valid:
                            valid_para_sentences.append(sentence)
                            verified_sentences += 1
                        else:
                            rejected_sentences += 1
                            self._log_rejection(
                                run_id=run_id,
                                headline=f"{sec.headline} ({para.platform})",
                                sentence=sentence,
                                reasons=reasons,
                            )
                    if valid_para_sentences:
                        para.sentences = valid_para_sentences
                        valid_paragraphs.append(para)
                        valid_sentences.extend(valid_para_sentences)
                sec.paragraphs = valid_paragraphs
                sec.sentences = valid_sentences
            else:
                for sentence in sec.sentences:
                    is_valid, reasons = self._validate_sentence(
                        sentence=sentence,
                        facts_map=facts_map,
                        whitelist=whitelist,
                    )
                    if is_valid:
                        valid_sentences.append(sentence)
                        verified_sentences += 1
                    else:
                        rejected_sentences += 1
                        self._log_rejection(
                            run_id=run_id,
                            headline=sec.headline,
                            sentence=sentence,
                            reasons=reasons,
                        )
                sec.sentences = valid_sentences
                if valid_sentences:
                    platform_default = (
                        sec.platform_tags[0] if sec.platform_tags else "Allgemein"
                    )
                    sec.paragraphs = [
                        EditorialParagraph(
                            platform=platform_default, sentences=valid_sentences
                        )
                    ]

            if valid_sentences:
                verified_sections.append(sec)

        newsletter.sections = verified_sections
        return newsletter, verified_sentences, rejected_sentences

    def _log_rejection(
        self,
        run_id: str,
        headline: str,
        sentence: EditorialSentence,
        reasons: list[str],
    ) -> None:
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "run_id": run_id,
            "headline": headline,
            "sentence": sentence.model_dump(),
            "reasons": reasons,
        }
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        logger.warning(
            "Satz in '%s' abgewiesen (%s): '%s'",
            headline,
            "; ".join(reasons),
            sentence.text[:60] + "...",
        )
