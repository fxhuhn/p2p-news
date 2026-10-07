"""
Digest-Extraktor für Stufe 1: Gemini 3.8 Flash Fakten-Extraktion mit Structured Output.

Verarbeitet ausgewählte NewsItems, ruft Gemini mit WeeklyDigestSchema auf,
archiviert Roh-Payloads und verifiziert alle Fakten über Verifier 1.
"""

from __future__ import annotations

import argparse
import gzip
import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from digest_schemas import WeeklyDigestSchema
from item_models import NewsItem
from item_store import ItemStore
from storage_sqlite import SQLiteStore
from verifier_stage1 import Stage1Verifier
from watermark_manager import WatermarkManager

load_dotenv()
logger = logging.getLogger("digest_extractor")


class DigestExtractor:
    """Orchestrierer für Stufe 1: Extraktion strukturierter Fakten-Dossiers."""

    def __init__(
        self,
        api_key: str | None = None,
        model_name: str = "gemini-3.8-flash",
        runs_dir: Path | str = "data/runs",
        digests_dir: Path | str = "data/digests",
        prompt_path: Path | str = "prompts/stage1_cluster_v1.md",
    ) -> None:
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model_name = model_name
        self.runs_dir = Path(runs_dir)
        self.digests_dir = Path(digests_dir)
        self.digests_dir.mkdir(parents=True, exist_ok=True)
        self.prompt_path = Path(prompt_path)
        self.verifier = Stage1Verifier()

    def build_prompt(self, items: list[NewsItem], iso_week: str) -> str:
        """Erstellt den Prompt für Gemini inklusive aller Quell-Items."""
        prompt_instruction = ""
        if self.prompt_path.exists():
            prompt_instruction = self.prompt_path.read_text(encoding="utf-8")

        items_text = []
        for idx, item in enumerate(items, start=1):
            items_text.append(
                f"### [ITEM {idx}] ID: {item.item_id}\n"
                f"- Quelle: {item.provider} (Tier: {item.source_tier})\n"
                f"- Titel: {item.title}\n"
                f"- Datum: {item.published_date or 'Unbekannt'}\n"
                f"- URL: {item.url}\n"
                f"- Plattformen: {', '.join(item.platforms) if item.platforms else 'allgemein'}\n"
                f"- Themen-Tags: {', '.join(item.topics) if item.topics else 'keine'}\n"
                f"- Dringlichkeit: {item.severity} (Sentiment: {item.sentiment})\n"
                f"- Inhalt:\n{item.content_plain}\n"
            )

        full_prompt = (
            f"{prompt_instruction}\n\n"
            f"# Zu verarbeitende Meldungen für Kalenderwoche {iso_week} ({len(items)} Items)\n\n"
            f"{'---\n'.join(items_text)}\n\n"
            f"Extrahiere nun das strukturierte Dossier im vorgegebenen JSON-Schema."
        )
        return full_prompt

    def extract_digest(
        self,
        items: list[NewsItem],
        iso_week: str,
        run_id: str | None = None,
        custom_client: Any | None = None,
    ) -> tuple[WeeklyDigestSchema, Path, dict[str, Any]]:
        """
        Führt die Faktenextraktion durch.

        Rückgabe: (verified_digest, digest_file_path, metrics)
        """
        active_run_id = (
            run_id
            or f"run_{iso_week}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
        )
        prompt = self.build_prompt(items, iso_week=iso_week)

        # Gemini Client initialisieren
        if custom_client is not None:
            client = custom_client
        else:
            if not self.api_key:
                raise ValueError(
                    "GEMINI_API_KEY ist weder im Environment noch übergeben."
                )
            from google import genai

            client = genai.Client(api_key=self.api_key)

        start_time = datetime.now(timezone.utc)
        logger.info(
            "[%s] Sende %d Items an Gemini (%s) mit response_schema...",
            active_run_id,
            len(items),
            self.model_name,
        )

        max_attempts = 4
        response = None
        for attempt in range(1, max_attempts + 1):
            try:
                response = client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config={
                        "response_mime_type": "application/json",
                        "response_schema": WeeklyDigestSchema,
                        "temperature": 0.0,
                    },
                )
                break
            except Exception as exc:
                exc_str = str(exc)
                is_transient = (
                    "503" in exc_str or "429" in exc_str or "UNAVAILABLE" in exc_str
                )
                if is_transient and attempt < max_attempts:
                    import re
                    import time

                    retry_match = re.search(
                        r"retry.*?(\d+(?:\.\d+)?)\s*s", exc_str, re.IGNORECASE
                    )
                    if retry_match:
                        sleep_time = int(float(retry_match.group(1))) + 2
                    elif "429" in exc_str:
                        sleep_time = 35 * attempt
                    else:
                        sleep_time = 3 * attempt

                    logger.warning(
                        "[%s] Transiente Gemini-Überlastung (%s). Wiederholung %d/%d in %ds...",
                        active_run_id,
                        exc,
                        attempt,
                        max_attempts,
                        sleep_time,
                    )
                    time.sleep(sleep_time)
                else:
                    raise

        duration_s = (datetime.now(timezone.utc) - start_time).total_seconds()

        resp_text = (
            str(response.text) if response and getattr(response, "text", None) else ""
        )

        # Roh-Antwort archivieren (Revisionssicherheit)
        self._archive_raw_llm(
            run_id=active_run_id,
            prompt=prompt,
            response_text=resp_text,
            model_version=getattr(response, "model_version", self.model_name),
            usage_metadata=getattr(response, "usage_metadata", None),
            duration_s=duration_s,
        )

        # JSON in Pydantic Schema parsen
        raw_digest = WeeklyDigestSchema.model_validate_json(resp_text)

        # Verifier 1 ausführen (strikte Zitatprüfung)
        items_map = {item.item_id: item for item in items}
        verified_digest, verified_facts, rejected_facts = self.verifier.verify_digest(
            digest=raw_digest,
            items_map=items_map,
            run_id=active_run_id,
        )

        # Speichere verifiziertes Dossier
        digest_file = self.digests_dir / f"digest-{iso_week}.json"
        digest_file.write_text(
            verified_digest.model_dump_json(indent=2),
            encoding="utf-8",
        )
        logger.info(
            "[%s] Dossier gespeichert: %s (%d Fakten verifiziert, %d abgelehnt)",
            active_run_id,
            digest_file,
            verified_facts,
            rejected_facts,
        )

        metrics = {
            "run_id": active_run_id,
            "iso_week": iso_week,
            "total_items": len(items),
            "clusters_count": len(verified_digest.clusters),
            "facts_verified": verified_facts,
            "facts_rejected": rejected_facts,
            "duration_s": duration_s,
        }
        return verified_digest, digest_file, metrics

    def _archive_raw_llm(
        self,
        run_id: str,
        prompt: str,
        response_text: str,
        model_version: str,
        usage_metadata: Any,
        duration_s: float,
    ) -> Path:
        """Archiviert die unveränderte LLM-Ein- und Ausgabe komprimiert als JSON.GZ."""
        llm_dir = self.runs_dir / run_id / "llm"
        llm_dir.mkdir(parents=True, exist_ok=True)
        raw_file = llm_dir / "stage1_raw.json.gz"

        usage_dict = {}
        if usage_metadata:
            usage_dict = {
                "prompt_token_count": getattr(
                    usage_metadata, "prompt_token_count", None
                ),
                "candidates_token_count": getattr(
                    usage_metadata, "candidates_token_count", None
                ),
                "total_token_count": getattr(usage_metadata, "total_token_count", None),
            }

        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "run_id": run_id,
            "stage": 1,
            "model_version": model_version,
            "duration_seconds": duration_s,
            "usage": usage_dict,
            "prompt": prompt,
            "raw_response": response_text,
        }

        compressed = gzip.compress(
            json.dumps(payload, ensure_ascii=False).encode("utf-8")
        )
        raw_file.write_bytes(compressed)

        # SQLite-Integration (Option 1)
        sqlite_db = self.runs_dir.parent / "p2p_archive.db"
        if sqlite_db.exists():
            try:
                store = SQLiteStore(sqlite_db)
                iso_week = run_id.split("_")[1] if "_" in run_id else ""
                store.save_run(
                    run_id=run_id,
                    stage=1,
                    iso_week=iso_week,
                    model_version=model_version,
                    duration_s=duration_s,
                    usage=usage_dict,
                    prompt=prompt,
                    raw_response=response_text,
                    created_at=str(payload["timestamp"]),
                )
            except Exception as exc:
                logger.warning("Konnte Run nicht in SQLite speichern: %s", exc)

        return raw_file


def run_stage1_pipeline(
    iso_week: str,
    data_dir: Path | str = "data",
    include_baseline: bool = True,
    limit: int | None = None,
) -> tuple[WeeklyDigestSchema, Path, dict[str, Any]]:
    """Convenience-Funktion zur Ausführung von Stufe 1."""
    base = Path(data_dir)
    store = ItemStore(items_dir=base / "items")
    wm_mgr = WatermarkManager(watermark_path=base / "watermark.json")

    # Wähle Items für die gegebene Woche
    selected_items = wm_mgr.select_items_for_run(
        store=store,
        iso_week=iso_week,
        include_baseline=include_baseline,
    )
    if not selected_items:
        logger.warning("Keine Items für Woche %s gefunden.", iso_week)
        all_items = store.get_all_items()
        selected_items = all_items[:15]
        logger.info("Verwende %d Fallback-Items für den Testlauf.", len(selected_items))

    # Obergrenze festlegen, um Token-Erschöpfung (Free-Tier Limit 250k TPM) zu verhindern
    max_items = limit
    if max_items is None:
        import os

        env_val = os.getenv("MAX_DIGEST_ITEMS")
        max_items = int(env_val) if env_val and env_val.isdigit() else 50

    if max_items > 0 and len(selected_items) > max_items:
        logger.info(
            "Begrenze ausgewählte Items auf die Top %d wichtigsten Meldungen (von %d) für Stufe 1.",
            max_items,
            len(selected_items),
        )
        selected_items = selected_items[:max_items]

    extractor = DigestExtractor(
        runs_dir=base / "runs",
        digests_dir=base / "digests",
    )
    return extractor.extract_digest(items=selected_items, iso_week=iso_week)


if __name__ == "__main__":
    now = datetime.now(timezone.utc)
    current_week = f"{now.isocalendar().year}-W{now.isocalendar().week:02d}"

    parser = argparse.ArgumentParser(
        description="P2P News Stufe 1: Fakten-Dossier Extraktion"
    )
    parser.add_argument(
        "--week",
        default=current_week,
        help=f"ISO-Woche (z. B. 2026-W40, Standard: {current_week})",
    )
    parser.add_argument("--data-dir", default="data", help="Pfad zum data Verzeichnis")
    parser.add_argument(
        "--include-baseline",
        action="store_true",
        help="Auch Baseline-Items einbeziehen",
    )
    parser.add_argument(
        "--limit", type=int, default=None, help="Maximale Anzahl Items für den Lauf"
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
    )
    digest, path, metrics = run_stage1_pipeline(
        iso_week=args.week,
        data_dir=args.data_dir,
        include_baseline=args.include_baseline,
        limit=args.limit,
    )
    print(
        f"Stufe 1 erfolgreich: {path} erstellt mit {metrics['facts_verified']} verifizierten Fakten."
    )
