"""
Zentraler Pipeline-Orchestrierer für den revisionssicheren P2P-Newsletter.

Verbindet alle Stufen (0, 1, 2) zu einem einzigen, benutzerfreundlichen Workflow:
- Optional: Web-Scraping & Item-Extraktion (Stufe 0)
- Stufe 1: Fakten-Dossier Extraktion & Verifier 1 (Gemini 3.8 Flash)
- Stufe 2: Redaktionelle Erstellung & Verifier 2
- Governance & Lifecycle: --draft (Standard), --publish --approve, --verify

Beispiele:
  # 1. Neuen Entwurf für die aktuelle Woche generieren:
  python pipeline_orchestrator.py --draft

  # 2. Entwurf nach menschlicher Durchsicht freigeben und versiegeln:
  python pipeline_orchestrator.py --publish --approve

  # 3. Integrität und Revisions-Hashes überprüfen:
  python pipeline_orchestrator.py --verify
"""

from __future__ import annotations

import argparse
import logging
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from digest_extractor import run_stage1_pipeline
from digest_schemas import WeeklyDigestSchema
from item_extractor import process_all_scraped_news
from manifest_manager import ManifestManager
from newsletter_generator import NewsletterGenerator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)-7s] %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("pipeline")


def get_current_iso_week() -> str:
    now = datetime.now(timezone.utc)
    return f"{now.isocalendar().year}-W{now.isocalendar().week:02d}"


def get_target_newsletter_week(dt: datetime | None = None) -> str:
    """
    Ermittelt die relevante Kalenderwoche für den Newsletter.
    An Montagen wird die gerade beendete Vorwoche ausgewertet (lückenlose Wochenrückschau).
    An allen anderen Tagen wird die aktuelle Kalenderwoche verwendet.
    """
    now = dt or datetime.now(timezone.utc)
    if now.weekday() == 0:
        target_dt = now - timedelta(days=1)
    else:
        target_dt = now
    return f"{target_dt.isocalendar().year}-W{target_dt.isocalendar().week:02d}"


def run_pipeline(
    week: str | None = None,
    data_dir: Path | str = "data",
    do_scrape: bool = False,
    do_extract: bool = False,
    include_baseline: bool = False,
    is_publish: bool = False,
    is_approved: bool = False,
    force_revision: bool = False,
    verify_only: bool = False,
    limit: int | None = None,
    ignore_draft: bool = False,
) -> int:
    base = Path(data_dir)
    target_week = week or get_target_newsletter_week()

    # Modus 1: Revisionsprüfung
    if verify_only:
        logger.info(
            "=== Führe Revisions-Integritätsprüfung für %s durch ===", target_week
        )
        manifest_mgr = ManifestManager(digests_dir=base / "digests")
        mf_path = base / "digests" / f"digest-{target_week}.manifest.json"
        is_valid, errors = manifest_mgr.verify_integrity(mf_path)
        if is_valid:
            print(
                f"VERIFICATION PASSED: Alle Hashes für {target_week} sind intakt und manipulationssicher."
            )
            return 0
        else:
            print(
                "VERIFICATION FAILED: Manipulation erkannt!\n"
                + "\n".join(f"- {e}" for e in errors)
            )
            return 1

    logger.info("==================================================================")
    logger.info("Starte P2P Newsletter Pipeline für Kalenderwoche: %s", target_week)
    logger.info(
        "Modus: %s", "RELEASE (Write-Once)" if is_publish else "DRAFT (Entwurf)"
    )
    logger.info("==================================================================")

    # 0. Plattform-Profile Integritätscheck
    from run_audit_scoring import ensure_platform_profiles

    ensure_platform_profiles(data_dir=base)

    # Stufe 0: Optionales Scraping & Item-Extraktion
    if do_scrape:
        logger.info("--- Stufe 0: Web-Scraping wird ausgeführt ---")
        from p2p_news_scraper import (
            P2PNewsScraper,
            ScraperConfig,
            load_classifier_from_yaml,
            load_providers_from_yaml,
        )

        providers_map = load_providers_from_yaml("providers.yaml")
        classifier = load_classifier_from_yaml("providers.yaml")
        scraper = P2PNewsScraper(
            config=ScraperConfig(output_dir=base), classifier=classifier
        )
        scraper.run(providers=list(providers_map.values()))
        do_extract = True

    if do_extract:
        logger.info("--- Stufe 0: Extrahiere diskrete Items in %s/items/ ---", base)
        files_cnt, items_cnt = process_all_scraped_news(
            data_dir=base, is_baseline=include_baseline
        )
        logger.info(
            "Stufe 0 abgeschlossen: %d Dateien verarbeitet, %d Items im Store.",
            files_cnt,
            items_cnt,
        )

    # Vorab-Prüfung: Falls Veröffentlichung gewünscht, aber Datei bereits existiert (Write-Once)
    target_file = base / "newsletters" / f"newsletter-{target_week}.md"
    if is_publish and not force_revision and target_file.exists():
        logger.warning(
            "Newsletter für Woche %s existiert bereits (%s). "
            "Write-Once Schutz aktiv: Bestehende Veröffentlichung bleibt unverändert.",
            target_week,
            target_file,
        )
        return 0

    # Stufe 1: Fakten-Dossier (falls noch nicht vorhanden oder falls neue Meldungen hinzugekommen sind)
    digest_path = base / "digests" / f"digest-{target_week}.json"
    needs_digest = not digest_path.exists()
    if not needs_digest:
        # Prüfe, ob neue Items für die Zielwoche im Store vorliegen, die im bestehenden Digest noch fehlen
        try:
            from item_store import ItemStore
            from watermark_manager import WatermarkManager

            store = ItemStore(items_dir=base / "items")
            wm_mgr = WatermarkManager(watermark_path=base / "watermark.json")
            selected_items = wm_mgr.select_items_for_run(
                store=store, iso_week=target_week, include_baseline=include_baseline
            )
            existing_digest = WeeklyDigestSchema.model_validate_json(
                digest_path.read_text(encoding="utf-8")
            )
            referenced_ids = {
                ev.item_id
                for c in existing_digest.clusters
                for f in c.facts
                for ev in f.evidence
            }
            current_ids = {itm.item_id for itm in selected_items}
            if not current_ids.issubset(referenced_ids) and len(current_ids) > len(
                referenced_ids
            ):
                logger.info(
                    "Neue Meldungen für %s gefunden (%d aktuell vs. %d im Dossier). Aktualisiere Fakten-Dossier...",
                    target_week,
                    len(current_ids),
                    len(referenced_ids),
                )
                needs_digest = True
        except Exception as exc:
            logger.debug(
                "Konnte Item-Differenz für %s nicht ermitteln: %s", target_week, exc
            )

    if needs_digest:
        logger.info("--- Stufe 1: Erzeuge Fakten-Dossier mit Gemini & Verifier 1 ---")
        _, digest_path, metrics = run_stage1_pipeline(
            iso_week=target_week,
            data_dir=base,
            include_baseline=include_baseline,
            limit=limit,
        )
        logger.info(
            "Stufe 1 abgeschlossen: %d Fakten verifiziert.", metrics["facts_verified"]
        )
        # Sobald ein neues Fakten-Dossier erzeugt wurde, ist jeder vorherige Entwurf obsolet!
        draft_file = (
            base / "newsletters" / "drafts" / f"newsletter-{target_week}.draft.md"
        )
        if draft_file.exists():
            try:
                draft_file.unlink()
                logger.info(
                    "Veralteten Entwurf nach neuem Fakten-Dossier entfernt: %s",
                    draft_file,
                )
            except Exception as exc:
                logger.warning(
                    "Konnte veralteten Entwurf %s nicht entfernen: %s", draft_file, exc
                )
        ignore_draft = True
    else:
        logger.info(
            "--- Stufe 1: Verwende vorliegendes Fakten-Dossier %s (0 Tokens) ---",
            digest_path,
        )

    # Lade Fakten-Dossier
    digest = WeeklyDigestSchema.model_validate_json(
        digest_path.read_text(encoding="utf-8")
    )

    # Stufe 2: Redaktionelle Erstellung & Verifier 2
    logger.info("--- Stufe 2: Redaktionelle Erstellung & Verifier 2 ---")
    generator = NewsletterGenerator(data_dir=base)
    out_file, metrics = generator.generate(
        digest=digest,
        is_publish=is_publish,
        is_approved=is_approved,
        force_revision=force_revision,
        ignore_draft=ignore_draft,
    )

    logger.info("==================================================================")
    if is_publish:
        logger.info("ERFOLG: Finaler Newsletter versiegelt und veröffentlicht!")
        logger.info("Pfad: %s", out_file)
        manifest_file = base / "digests" / f"digest-{target_week}.manifest.json"
        logger.info("Manifest: %s", manifest_file)

        from git_publisher import publish_changes

        publish_changes(
            files=[out_file],
            commit_message=f"chore(newsletter): publish newsletter {target_week}",
            data_dir=base,
        )

        try:
            from telegram_publisher import send_newsletter_notification

            send_newsletter_notification(out_file)
        except Exception as exc:
            logger.warning(
                "Telegram-Benachrichtigung für Newsletter fehlgeschlagen: %s", exc
            )
    else:
        logger.info("ERFOLG: Entwurf (Draft) erstellt zur menschlichen Durchsicht!")
        logger.info("Pfad: %s", out_file)
        logger.info("Zur Freigabe und Veröffentlichung ausführen:")
        logger.info(
            "  python pipeline_orchestrator.py --week %s --publish --approve",
            target_week,
        )
    logger.info("==================================================================")
    return 0


def main() -> int:
    current_week = get_current_iso_week()
    parser = argparse.ArgumentParser(
        description="P2P News Pipeline Orchestrierer (End-to-End)"
    )
    parser.add_argument(
        "--week", default=current_week, help=f"ISO-Woche (Standard: {current_week})"
    )
    parser.add_argument("--data-dir", default="data", help="Pfad zum Datenverzeichnis")
    parser.add_argument(
        "--scrape", action="store_true", help="Führt vorab den Web-Scraper aus"
    )
    parser.add_argument(
        "--extract-items",
        action="store_true",
        help="Führt vorab die Item-Extraktion aus",
    )
    parser.add_argument(
        "--include-baseline",
        action="store_true",
        help="Bezieht auch historische Baseline-Items ein",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Begrenzt die Anzahl an Items für Stufe 1",
    )
    parser.add_argument(
        "--draft", action="store_true", help="Erstellt einen Entwurf (Standard)"
    )
    parser.add_argument(
        "--publish",
        action="store_true",
        help="Veröffentlicht das finale Release (Write-Once)",
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
        "--ignore-draft",
        action="store_true",
        help="Ignoriert bestehende Entwürfe und erzwingt Neu-Generierung",
    )
    args = parser.parse_args()

    # Standard-Modus ist --draft falls weder publish noch verify gewählt wurde
    is_publish = args.publish

    try:
        return run_pipeline(
            week=args.week,
            data_dir=args.data_dir,
            do_scrape=args.scrape,
            do_extract=args.extract_items,
            include_baseline=args.include_baseline,
            is_publish=is_publish,
            is_approved=args.approve,
            force_revision=args.force_revision,
            verify_only=args.verify,
            limit=args.limit,
            ignore_draft=args.ignore_draft,
        )
    except Exception as exc:
        logger.error("Pipeline fehlgeschlagen: %s", exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())
