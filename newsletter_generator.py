"""
Newsletter-Generator für Stufe 2: Redaktionelle Erstellung, Verifier 2 & Release-Lifecycle.

Ablauf:
1. Lädt Fakten-Dossier aus data/digests/digest-YYYY-Wxx.json
2. Ruft Gemini mit EditorialNewsletterSchema auf
3. Führt satzweise Verifikation über Verifier 2 durch
4. Rendert Markdown deterministisch (keine halluzinierten URLs)
5. Verwaltet den Release-Lifecycle:
   - --draft: Entwurf unter data/newsletters/drafts/
   - --publish --approve: Versiegelte Write-Once Ausgabe + Manifest mit Hash-Kette
   - --verify: Prüfung der Revisions-Integrität (Tamper-Detection)
"""

from __future__ import annotations

import argparse
import gzip
import json
import logging
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from digest_schemas import WeeklyDigestSchema
from editorial_schemas import EditorialNewsletterSchema
from item_store import ItemStore
from manifest_manager import ManifestManager
from markdown_renderer import MarkdownRenderer
from storage_sqlite import SQLiteStore
from verifier_stage2 import Stage2Verifier
from watermark_manager import WatermarkManager

load_dotenv()
logger = logging.getLogger("newsletter_generator")


class NewsletterGenerator:
    """Orchestrierer für Stufe 2 der Pipeline."""

    def __init__(
        self,
        api_key: str | None = None,
        model_name: str = "gemini-flash-latest",
        data_dir: Path | str = "data",
        prompt_path: Path | str = "prompts/stage2_editorial_v1.md",
    ) -> None:
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model_name = os.getenv("GEMINI_MODEL") or model_name
        self.data_dir = Path(data_dir)
        self.newsletters_dir = self.data_dir / "newsletters"
        self.drafts_dir = self.newsletters_dir / "drafts"
        self.newsletters_dir.mkdir(parents=True, exist_ok=True)
        self.drafts_dir.mkdir(parents=True, exist_ok=True)
        self.prompt_path = Path(prompt_path)

        self.verifier = Stage2Verifier(
            log_path=self.data_dir / "logs" / "rejected-sentences.jsonl"
        )
        self.renderer = MarkdownRenderer()
        self.manifest_mgr = ManifestManager(digests_dir=self.data_dir / "digests")
        self.watermark_mgr = WatermarkManager(
            watermark_path=self.data_dir / "watermark.json"
        )
        self.item_store = ItemStore(items_dir=self.data_dir / "items")

    def build_prompt(self, digest: WeeklyDigestSchema) -> str:
        """Erstellt den Prompt aus dem Fakten-Dossier."""
        instruction = ""
        if self.prompt_path.exists():
            instruction = self.prompt_path.read_text(encoding="utf-8")

        dossier_text = []
        for cluster in digest.clusters:
            cluster_lines = [
                f"### Cluster: {cluster.cluster_id} (Kategorie: {cluster.topic})",
                f"- Plattformen: {', '.join(cluster.platforms)}",
                f"- Titel: {cluster.title}",
                "- Verifizierte Fakten:",
            ]
            for fact in cluster.facts:
                ev_quotes = [
                    f"'{ev.evidence_quote}' (Item: {ev.item_id})"
                    for ev in fact.evidence
                ]
                cluster_lines.append(
                    f"  * [{fact.fact_id}] {fact.statement}\n"
                    f"    Belege: {'; '.join(ev_quotes)}"
                )
            if cluster.conflicts:
                cluster_lines.append(
                    f"- Widersprüche / Differenzen: {'; '.join(cluster.conflicts)}"
                )
            dossier_text.append("\n".join(cluster_lines))

        full_prompt = (
            f"{instruction}\n\n"
            f"# Geprüftes Fakten-Dossier für {digest.iso_week} ({len(digest.clusters)} Cluster)\n\n"
            f"{'\n\n---\n\n'.join(dossier_text)}\n\n"
            f"Erstelle nun den professionellen Newsletter im vorgegebenen JSON-Schema."
        )
        return full_prompt

    def generate(
        self,
        digest: WeeklyDigestSchema,
        run_id: str | None = None,
        is_publish: bool = False,
        is_approved: bool = False,
        force_revision: bool = False,
        custom_client: Any | None = None,
        raw_path: Path | str | None = None,
    ) -> tuple[Path, dict[str, Any]]:
        """
        Führt den redaktionellen LLM-Aufruf, Verifier 2 und Rendering aus.
        """
        active_run_id = (
            run_id
            or f"run_{digest.iso_week}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
        )
        prompt = self.build_prompt(digest)

        all_items = self.item_store.get_all_items()
        items_map = {itm.item_id: itm for itm in all_items}
        total_facts = sum(len(c.facts) for c in digest.clusters)

        draft_file = self.drafts_dir / f"newsletter-{digest.iso_week}.draft.md"
        markdown_content = ""
        verified_sentences = 0
        rejected_sentences = 0
        duration_s = 0.0

        if raw_path is not None:
            raw_p = Path(raw_path)
            logger.info("[%s] Lade vorliegende Roh-Antwort: %s", active_run_id, raw_p)
            if raw_p.name.endswith(".gz"):
                raw_payload = json.loads(
                    gzip.decompress(raw_p.read_bytes()).decode("utf-8")
                )
            else:
                raw_payload = json.loads(raw_p.read_text(encoding="utf-8"))
            raw_text = (
                raw_payload.get("raw_response", "")
                if isinstance(raw_payload, dict)
                else str(raw_payload)
            )
            editorial_json = EditorialNewsletterSchema.model_validate_json(raw_text)
            verified_newsletter, verified_sentences, rejected_sentences = (
                self.verifier.verify_newsletter(
                    newsletter=editorial_json,
                    digest=digest,
                    run_id=active_run_id,
                )
            )
            markdown_content = self.renderer.render(
                newsletter=verified_newsletter,
                digest=digest,
                items_map=items_map,
                run_id=active_run_id,
                iso_week=digest.iso_week,
                verified_facts_count=total_facts,
                verified_sentences_count=verified_sentences,
            )
        elif is_publish and is_approved and draft_file.exists() and not custom_client:
            logger.info(
                "[%s] Verwende vorliegenden, geprüften Entwurf zur Versiegelung: %s",
                active_run_id,
                draft_file,
            )
            markdown_content = draft_file.read_text(encoding="utf-8")
            # Extrahiere Metriken aus Frontmatter
            for line in markdown_content.splitlines():
                if line.startswith("verified_sentences_count:"):
                    try:
                        verified_sentences = int(line.split(":")[-1].strip())
                    except ValueError:
                        pass
        else:
            # Gemini Client initialisieren und aufrufen
            if custom_client is not None:
                client = custom_client
            else:
                if not self.api_key:
                    raise ValueError("GEMINI_API_KEY fehlt.")
                from google import genai

                client = genai.Client(api_key=self.api_key)

            start_time = datetime.now(timezone.utc)
            logger.info(
                "[%s] Starte redaktionelle Aufbereitung mit Gemini (%s)...",
                active_run_id,
                self.model_name,
            )

            fallback_models = [self.model_name]
            for fb in ["gemini-flash-latest", "gemini-3.6-flash"]:
                if fb not in fallback_models:
                    fallback_models.append(fb)

            # Retry bei transienten Überlastungen
            max_attempts = 5
            backoff_delays = [3, 6, 12, 20, 30]
            response = None
            for attempt in range(1, max_attempts + 1):
                current_model = fallback_models[
                    min(attempt - 1, len(fallback_models) - 1)
                ]
                try:
                    response = client.models.generate_content(
                        model=current_model,
                        contents=prompt,
                        config={
                            "response_mime_type": "application/json",
                            "response_schema": EditorialNewsletterSchema,
                            "temperature": 0.2,
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

                        retry_match = re.search(
                            r"retry.*?(\d+(?:\.\d+)?)\s*s", exc_str, re.IGNORECASE
                        )
                        if retry_match:
                            sleep_time = int(float(retry_match.group(1))) + 2
                        elif "429" in exc_str:
                            sleep_time = 35 * attempt
                        else:
                            sleep_time = backoff_delays[attempt - 1]

                        next_model = fallback_models[
                            min(attempt, len(fallback_models) - 1)
                        ]
                        logger.warning(
                            "[%s] Transiente Gemini-Überlastung auf Modell %s (%s). Retry %d/%d mit Modell %s in %ds...",
                            active_run_id,
                            current_model,
                            exc,
                            attempt,
                            max_attempts,
                            next_model,
                            sleep_time,
                        )
                        time.sleep(sleep_time)
                    else:
                        raise

            duration_s = (datetime.now(timezone.utc) - start_time).total_seconds()

            resp_text = (
                str(response.text)
                if response and getattr(response, "text", None)
                else ""
            )

            # Roh-Antwort archivieren
            self._archive_raw_llm(
                run_id=active_run_id,
                prompt=prompt,
                response_text=resp_text,
                model_version=getattr(response, "model_version", self.model_name),
                usage_metadata=getattr(response, "usage_metadata", None),
                duration_s=duration_s,
            )

            # JSON validieren
            editorial_json = EditorialNewsletterSchema.model_validate_json(resp_text)

            # Verifier 2 ausführen
            verified_newsletter, verified_sentences, rejected_sentences = (
                self.verifier.verify_newsletter(
                    newsletter=editorial_json,
                    digest=digest,
                    run_id=active_run_id,
                )
            )

            total_facts = sum(len(c.facts) for c in digest.clusters)
            markdown_content = self.renderer.render(
                newsletter=verified_newsletter,
                digest=digest,
                items_map=items_map,
                run_id=active_run_id,
                iso_week=digest.iso_week,
                verified_facts_count=total_facts,
                verified_sentences_count=verified_sentences,
            )

        # Lifecycle-Handling
        if is_publish:
            if not is_approved:
                raise ValueError(
                    "Veröffentlichung erfordert explizite Bestätigung mit --approve!"
                )

            target_file = self.newsletters_dir / f"newsletter-{digest.iso_week}.md"
            if target_file.exists() and not force_revision:
                raise FileExistsError(
                    f"Datei {target_file} existiert bereits! Write-Once Schutz aktiv. "
                    f"Nutze --force-revision für eine neue Version."
                )
            if target_file.exists() and force_revision:
                # Finde nächste Versionsnummer
                v = 2
                while (
                    self.newsletters_dir / f"newsletter-{digest.iso_week}.v{v}.md"
                ).exists():
                    v += 1
                target_file = (
                    self.newsletters_dir / f"newsletter-{digest.iso_week}.v{v}.md"
                )

            target_file.write_text(markdown_content, encoding="utf-8")
            logger.info(
                "[%s] Finaler Newsletter veröffentlicht: %s", active_run_id, target_file
            )

            # Revisions-Manifest mit Hash-Kette schreiben
            digest_path = self.data_dir / "digests" / f"digest-{digest.iso_week}.json"
            referenced_ids = {
                ev.item_id
                for cluster in digest.clusters
                for fact in cluster.facts
                for ev in fact.evidence
            }
            item_hashes = {
                itm.item_id: itm.item_content_hash
                for itm in all_items
                if itm.item_id in referenced_ids
            }
            wm_prev = self.watermark_mgr.get_last_watermark()
            wm_now = datetime.now(timezone.utc).isoformat()

            manifest_metrics = {
                "facts_verified": total_facts,
                "sentences_verified": verified_sentences,
                "sentences_rejected": rejected_sentences,
                "duration_seconds": duration_s,
            }

            self.manifest_mgr.create_manifest(
                iso_week=digest.iso_week,
                run_id=active_run_id,
                watermark_previous=wm_prev,
                watermark_current=wm_now,
                digest_path=digest_path,
                newsletter_path=target_file,
                item_hashes=item_hashes,
                metrics=manifest_metrics,
            )

            # Watermark aktualisieren
            self.watermark_mgr.update_watermark(
                watermark_iso=wm_now,
                run_id=active_run_id,
                metadata={"newsletter": str(target_file)},
            )
        else:
            # Draft-Modus
            target_file = self.drafts_dir / f"newsletter-{digest.iso_week}.draft.md"
            target_file.write_text(markdown_content, encoding="utf-8")
            logger.info("[%s] Entwurf gespeichert: %s", active_run_id, target_file)

        metrics = {
            "run_id": active_run_id,
            "iso_week": digest.iso_week,
            "target_file": str(target_file),
            "is_publish": is_publish,
            "sentences_verified": verified_sentences,
            "sentences_rejected": rejected_sentences,
            "duration_s": duration_s,
        }
        return target_file, metrics

    def _archive_raw_llm(
        self,
        run_id: str,
        prompt: str,
        response_text: str,
        model_version: str,
        usage_metadata: Any,
        duration_s: float,
    ) -> Path:
        llm_dir = self.data_dir / "runs" / run_id / "llm"
        llm_dir.mkdir(parents=True, exist_ok=True)
        raw_file = llm_dir / "stage2_raw.json.gz"

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
            "stage": 2,
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
        sqlite_db = self.data_dir / "p2p_archive.db"
        if sqlite_db.exists():
            try:
                store = SQLiteStore(sqlite_db)
                # Extrahiere iso_week aus run_id (Format: run_YYYY-Wxx_...)
                iso_week = run_id.split("_")[1] if "_" in run_id else ""
                store.save_run(
                    run_id=run_id,
                    stage=2,
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


def main() -> int:
    now = datetime.now(timezone.utc)
    current_week = f"{now.isocalendar().year}-W{now.isocalendar().week:02d}"

    parser = argparse.ArgumentParser(
        description="P2P News Newsletter Generator (Stufe 2)"
    )
    parser.add_argument(
        "--week",
        default=current_week,
        help=f"ISO-Woche (z. B. 2026-W40, Standard: {current_week})",
    )
    parser.add_argument("--data-dir", default="data", help="Pfad zum data Verzeichnis")
    parser.add_argument(
        "--publish",
        action="store_true",
        help="Erstellt das finale Release (Write-Once)",
    )
    parser.add_argument(
        "--approve", action="store_true", help="Explizite Freigabe für --publish"
    )
    parser.add_argument(
        "--force-revision",
        action="store_true",
        help="Erzwingt neue Revisionsstufe (.v2.md)",
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Prüft die Revisions-Integrität des Manifests",
    )
    parser.add_argument(
        "--raw-path",
        default=None,
        help="Pfad zu einer gespeicherten Roh-Antwort (z. B. data/runs/.../stage2_raw.json.gz)",
    )
    parser.add_argument(
        "--model",
        default="gemini-3.8-flash",
        help="Zu verwendendes Gemini-Modell (Standard: gemini-3.8-flash)",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
    )

    base = Path(args.data_dir)
    manifest_mgr = ManifestManager(digests_dir=base / "digests")

    # Modus: Integritätsprüfung
    if args.verify:
        mf_path = base / "digests" / f"digest-{args.week}.manifest.json"
        is_valid, errors = manifest_mgr.verify_integrity(mf_path)
        if is_valid:
            print(
                f"VERIFICATION PASSED: Alle Hashes für {args.week} sind intakt und manipulationssicher."
            )
            return 0
        else:
            print(
                "VERIFICATION FAILED: Manipulation erkannt!\n"
                + "\n".join(f"- {e}" for e in errors)
            )
            return 1

    # Normaler Generierungslauf
    digest_file = base / "digests" / f"digest-{args.week}.json"
    if not digest_file.exists():
        logger.error(
            "Dossier %s existiert nicht. Bitte zuerst Stufe 1 ausführen!", digest_file
        )
        return 1

    digest = WeeklyDigestSchema.model_validate_json(
        digest_file.read_text(encoding="utf-8")
    )
    generator = NewsletterGenerator(data_dir=base, model_name=args.model)

    try:
        out_file, metrics = generator.generate(
            digest=digest,
            is_publish=args.publish,
            is_approved=args.approve,
            force_revision=args.force_revision,
            raw_path=args.raw_path,
        )
        print(
            f"Erfolg: {out_file} ({metrics['sentences_verified']} Sätze verifiziert)."
        )
        return 0
    except Exception as exc:
        logger.error("Fehler bei Generierung: %s", exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())
