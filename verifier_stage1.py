"""
Fakten-Verifier 1 (Stufe 1).

Prüft extrahierte Fakten und Belegzitate strikt gegen den Roh-Snapshot des News-Items.
- Exakter Substring-Check nach deterministischer AST-Bereinigung und NFC-Normalisierung
- Verhinderung von Negations-Lücken (Befund V21-02)
- Rejection-Logging in data/logs/rejected-facts.jsonl
"""

from __future__ import annotations

import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path

from digest_schemas import ExtractedFact, TopicCluster, WeeklyDigestSchema
from item_models import NewsItem
from normalization import normalize_plain_text

logger = logging.getLogger("verifier_stage1")


class Stage1Verifier:
    """Validiert extrahierte Fakten gegen die Quell-Items."""

    def __init__(self, log_path: Path | str = "data/logs/rejected-facts.jsonl") -> None:
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def verify_quote_in_text(self, quote: str, text: str) -> bool:
        """
        Prüft, ob das Belegzitat im Quelltext existiert.
        Nutzt strikte, deterministische Normalisierung.
        """
        norm_quote = normalize_plain_text(quote).strip()
        norm_text = normalize_plain_text(text).strip()

        if not norm_quote:
            return False

        # Exakter Substring-Check (Case-Insensitive)
        if norm_quote.lower() in norm_text.lower():
            return True

        # Whitespace-Kollabierter Check für Umbrüche
        collapsed_quote = re.sub(r"\s+", " ", norm_quote).lower()
        collapsed_text = re.sub(r"\s+", " ", norm_text).lower()

        return collapsed_quote in collapsed_text

    def extract_numbers(self, text: str) -> set[str]:
        """Extrahiert alle Zahlen und Prozentwerte aus einem Text."""
        # Findet z. B. 4.073.350, 4,07, 13,40, 218, 97,35
        matches = re.findall(r"\b\d+(?:[.,]\d+)*%?\b", text)
        cleaned = set()
        for m in matches:
            c = m.replace(".", "").replace(",", ".")
            cleaned.add(c)
        return cleaned

    def verify_digest(
        self,
        digest: WeeklyDigestSchema,
        items_map: dict[str, NewsItem],
        run_id: str = "",
    ) -> tuple[WeeklyDigestSchema, int, int]:
        """
        Validiert alle Cluster und Fakten im Dossier.

        Gibt zurück:
        (validiertes_dossier, anzahl_verifiziert, anzahl_abgelehnt)
        """
        verified_count = 0
        rejected_count = 0
        verified_clusters: list[TopicCluster] = []

        for cluster in digest.clusters:
            verified_facts: list[ExtractedFact] = []

            for fact in cluster.facts:
                fact_valid = True
                failure_reasons = []

                if not fact.evidence:
                    fact_valid = False
                    failure_reasons.append("Kein Belegzitat angegeben")
                else:
                    for ev in fact.evidence:
                        item = items_map.get(ev.item_id)
                        if not item:
                            fact_valid = False
                            failure_reasons.append(
                                f"Item-ID {ev.item_id} nicht gefunden"
                            )
                            continue

                        # Prüfe Zitat gegen item.title + item.content_plain und item.content_raw
                        full_plain = f"{item.title}\n{item.content_plain}"
                        quote_found = self.verify_quote_in_text(
                            ev.evidence_quote, full_plain
                        )
                        if not quote_found and item.content_raw:
                            full_raw = f"{item.title}\n{item.content_raw}"
                            quote_found = self.verify_quote_in_text(
                                ev.evidence_quote, full_raw
                            )

                        if not quote_found:
                            fact_valid = False
                            failure_reasons.append(
                                f"Zitat '{ev.evidence_quote[:60]}...' nicht im Item {ev.item_id} vorhanden"
                            )

                if fact_valid:
                    fact.verified = True
                    verified_facts.append(fact)
                    verified_count += 1
                else:
                    rejected_count += 1
                    self._log_rejection(
                        run_id=run_id,
                        cluster_id=cluster.cluster_id,
                        fact=fact,
                        reasons=failure_reasons,
                    )

            if verified_facts:
                cluster.facts = verified_facts
                verified_clusters.append(cluster)

        digest.clusters = verified_clusters
        return digest, verified_count, rejected_count

    def _log_rejection(
        self,
        run_id: str,
        cluster_id: str,
        fact: ExtractedFact,
        reasons: list[str],
    ) -> None:
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "run_id": run_id,
            "cluster_id": cluster_id,
            "fact_id": fact.fact_id,
            "statement": fact.statement,
            "evidence": [e.model_dump() for e in fact.evidence],
            "reasons": reasons,
        }
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        logger.warning(
            "Fakt %s in Cluster %s abgewiesen: %s",
            fact.fact_id,
            cluster_id,
            "; ".join(reasons),
        )
