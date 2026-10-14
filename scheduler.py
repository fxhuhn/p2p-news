"""
Autarker Zeitplan-Daemon für periodische P2P-News-Pipelines via 'schedule'.

Führt drei periodische Hintergrund-Jobs aus:
1. Täglich (jeden Tag um 06:00 Uhr Berliner Zeit):
   Quellen-Ingestion (Stage 0: Web-Scraping, RSS-Feeds & Item-Extraktion in den Flat-File Store).
   Läuft rein deterministisch ohne LLM-Aufrufe / Tokens, damit News aus RSS-Feeds lückenlos erhalten bleiben.
2. Wöchentlich (Montag um 06:30 Uhr Berliner Zeit):
   Scraping, Fakten-Clustering & Newsletter-Release (pipeline_orchestrator.py).
3. Monatlich (am 1. Tag des Monats um 07:00 Uhr Berliner Zeit):
   Vollständiges 4-Säulen-Audit-Scoring & Plattform-Rankings (run_audit_scoring.py).

Unterstützt sauberes Signal-Handling (SIGTERM, SIGINT) für Graceful Shutdown in Containern.
"""

from __future__ import annotations

import argparse
import logging
import os
import signal
import sys
import time
from datetime import datetime
from pathlib import Path
from types import FrameType

import schedule

from pipeline_orchestrator import get_target_newsletter_week, run_pipeline
from run_audit_scoring import ensure_platform_profiles, run_full_audit

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)-7s] %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("scheduler")

_running: bool = True


def handle_shutdown(signum: int, frame: FrameType | None) -> None:
    """Fängt Terminationssignale ab und signalisiert dem Scheduler das Beenden."""
    global _running
    sig_name = signal.Signals(signum).name
    logger.info(
        "Signal %s (%d) empfangen. Beende Scheduler geordnet...", sig_name, signum
    )
    _running = False


def job_daily_ingestion(data_dir: Path | str = "data") -> bool:
    """
    Führt den täglichen Quellen-Ingestion-Lauf durch (Stage 0: Scraping, RSS-Feeds & Item-Extraktion).

    Arbeitet rein lokal/deterministisch (Trafilatura, ElementTree, SHA-256 Hashing)
    ohne jegliche LLM-Kosten oder Token-Verbrauch. Sichert Artikel aus Feeds mit
    Limitierung (z. B. 10 Beiträge) lückenlos in den Flat-File Store (data/items/).
    """
    base = Path(data_dir)
    logger.info("=== [SCHEDULER] Starte täglichen Ingestion-Lauf (Stage 0) ===")
    try:
        from item_extractor import process_all_scraped_news
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
        files_cnt, items_cnt = process_all_scraped_news(data_dir=base)
        logger.info(
            "=== [SCHEDULER] Täglicher Ingestion-Lauf erfolgreich abgeschlossen: "
            "%d Dateien verarbeitet, %d Items im Store ===",
            files_cnt,
            items_cnt,
        )
        return True
    except Exception as exc:
        logger.exception(
            "=== [SCHEDULER] Unerwarteter Fehler im täglichen Ingestion-Lauf: %s ===",
            exc,
        )
        return False


def job_weekly_newsletter(
    data_dir: Path | str = "data",
    force: bool = False,
    force_revision: bool = False,
) -> bool:
    """Führt den wöchentlichen Scraping- und Newsletter-Lauf durch (direkte finale Veröffentlichung)."""
    is_force = force or force_revision
    logger.info(
        "=== [SCHEDULER] Starte wöchentlichen News- & Newsletter-Lauf%s ===",
        " (FORCE / neue Revision)" if is_force else "",
    )
    try:
        if is_force:
            ret = run_pipeline(
                data_dir=data_dir,
                do_scrape=True,
                is_publish=True,
                is_approved=True,
                force_revision=True,
            )
        else:
            ret = run_pipeline(
                data_dir=data_dir,
                do_scrape=True,
                is_publish=True,
                is_approved=True,
            )
        if ret == 0:
            logger.info(
                "=== [SCHEDULER] Wöchentlicher Lauf erfolgreich abgeschlossen ==="
            )
            return True
        logger.error(
            "=== [SCHEDULER] Wöchentlicher Lauf mit Returncode %d beendet ===", ret
        )
        return False
    except FileExistsError as exc:
        logger.warning(
            "=== [SCHEDULER] Newsletter für Zielwoche existiert bereits (%s). Write-Once Schutz aktiv. ===",
            exc,
        )
        return True
    except Exception as exc:
        logger.exception(
            "=== [SCHEDULER] Unerwarteter Fehler im wöchentlichen Lauf: %s ===", exc
        )
        return False


def job_monthly_scoring(data_dir: Path | str = "data", force: bool = False) -> bool:
    """Führt das monatliche Plattform-Audit-Scoring durch (nur am 1. Tag des Monats)."""
    now = datetime.now()
    if not force and now.day != 1:
        logger.debug(
            "[SCHEDULER] Monatlicher Job geprüft: Tag ist %d (nicht der 1.), wird übersprungen.",
            now.day,
        )
        return False

    logger.info("=== [SCHEDULER] Starte monatliches Audit-Scoring & Rankings ===")
    try:
        scored_count, ranking_path = run_full_audit(data_dir=data_dir)
        logger.info(
            "=== [SCHEDULER] Monatliches Audit abgeschlossen: %d Plattformen gescored, Ranking unter %s ===",
            scored_count,
            ranking_path,
        )
        return True
    except Exception as exc:
        logger.exception(
            "=== [SCHEDULER] Unerwarteter Fehler im monatlichen Scoring-Lauf: %s ===",
            exc,
        )
        return False


def setup_schedule(
    daily_time: str = "06:00",
    weekly_time: str = "06:30",
    monthly_time: str = "07:00",
    data_dir: Path | str = "data",
    force_weekly: bool = False,
) -> None:
    """Registriert alle periodischen Jobs in 'schedule'."""
    schedule.clear()
    schedule.every().day.at(daily_time).do(job_daily_ingestion, data_dir=data_dir)
    schedule.every().monday.at(weekly_time).do(
        job_weekly_newsletter, data_dir=data_dir, force=force_weekly
    )
    schedule.every().day.at(monthly_time).do(
        job_monthly_scoring, data_dir=data_dir, force=False
    )
    logger.info(
        "Zeitplan initialisiert: Täglich um %s (Ingestion) | Wöchentlich montags um %s%s | Monatlich am 1. um %s (Europe/Berlin)",
        daily_time,
        weekly_time,
        " (force_weekly aktiv)" if force_weekly else "",
        monthly_time,
    )


def initial_startup_check_and_sync(data_dir: Path | str = "data") -> None:
    """
    Führt beim Container-Start einen initialen Check und eine Quellen-Aktualisierung durch:
    1. Datenbank- & Plattform-Check (Profil-Integrität & Initial-Ranking).
    2. Quellen direkt aktualisieren (Scraping & Item-Extraktion).
    3. Konsistenzprüfung für Reports (stets verfügbare Rankings und Newsletter).
    """
    base = Path(data_dir)
    logger.info(
        "=== [STARTUP] Starte initialen System-Check & Quellen-Aktualisierung ==="
    )

    # 1. Plattform-Profile prüfen und ggf. seeden
    profiles = ensure_platform_profiles(data_dir=base)
    logger.info("[STARTUP] Plattform-Profile geprüft: %d Profile aktiv.", len(profiles))

    # 2. Prüfen, ob bereits ein Plattform-Ranking existiert
    rankings_dir = base / "rankings"
    has_ranking = rankings_dir.exists() and bool(list(rankings_dir.glob("*.md")))
    if not has_ranking:
        logger.info(
            "[STARTUP] Kein bestehendes Ranking gefunden. Erzeuge initiales Master-Ranking..."
        )
        try:
            run_full_audit(data_dir=base)
            logger.info(
                "✓ [STARTUP] Initiales Plattform-Ranking erfolgreich generiert."
            )
        except Exception as exc:
            logger.warning(
                "[STARTUP] Initiales Ranking konnte nicht erzeugt werden: %s", exc
            )
    else:
        logger.info("✓ [STARTUP] Bestehendes Plattform-Ranking vorhanden.")

    # 3. Quellen direkt aktualisieren (Web-Scraping & Item-Extraktion via Ingestion-Job)
    logger.info(
        "[STARTUP] Aktualisiere Quellen (Multi-Provider Scraper & RSS-Ingestion)..."
    )
    job_daily_ingestion(data_dir=base)

    # 4. Report-Verfügbarkeit prüfen: Existiert bereits ein finaler Newsletter für die Zielwoche?
    target_week = get_target_newsletter_week()
    published_file = base / "newsletters" / f"newsletter-{target_week}.md"

    if not published_file.exists():
        logger.info(
            "[STARTUP] Kein veröffentlichter Newsletter für Zielwoche %s vorhanden. Erzeuge finale Ausgabe...",
            target_week,
        )
        try:
            run_pipeline(
                week=target_week,
                data_dir=base,
                do_scrape=False,
                is_publish=True,
                is_approved=True,
            )
            logger.info(
                "✓ [STARTUP] Finaler Newsletter für %s erfolgreich erzeugt.",
                target_week,
            )
        except Exception as exc:
            logger.warning(
                "[STARTUP] Finaler Newsletter konnte nicht erzeugt werden: %s",
                exc,
            )
    else:
        logger.info(
            "✓ [STARTUP] Newsletter-Bericht für Woche %s ist einsatzbereit.",
            target_week,
        )

    logger.info(
        "=== [STARTUP] Initialer Check abgeschlossen. Alle Reports sind betriebsbereit. ==="
    )


def run_scheduler_loop(poll_interval_seconds: float = 1.0) -> None:
    """Hauptschleife des Schedulers."""
    global _running
    signal.signal(signal.SIGTERM, handle_shutdown)
    signal.signal(signal.SIGINT, handle_shutdown)

    logger.info("Scheduler-Daemon aktiv. Warte auf anstehende Jobs...")
    while _running:
        schedule.run_pending()
        time.sleep(poll_interval_seconds)

    logger.info("Scheduler-Hauptschleife sauber beendet.")


def main(argv: list[str] | None = None) -> int:
    """CLI-Einstiegspunkt für den Scheduler."""
    parser = argparse.ArgumentParser(
        description="Periodischer P2P-News & Audit-Scoring Scheduler Daemon"
    )
    parser.add_argument(
        "--data-dir",
        default="data",
        help="Pfad zum Datenverzeichnis (Standard: data)",
    )
    parser.add_argument(
        "--daily-time",
        default=os.environ.get("DAILY_TIME", "06:00"),
        help="Uhrzeit für den täglichen Ingestion-Lauf (HH:MM, Standard: 06:00)",
    )
    parser.add_argument(
        "--weekly-time",
        default=os.environ.get("WEEKLY_TIME", "06:30"),
        help="Uhrzeit für den wöchentlichen Montags-Lauf (HH:MM, Standard: 06:30)",
    )
    parser.add_argument(
        "--monthly-time",
        default=os.environ.get("MONTHLY_TIME", "07:00"),
        help="Uhrzeit für den monatlichen Lauf am 1. (HH:MM, Standard: 07:00)",
    )
    parser.add_argument(
        "--run-daily-now",
        action="store_true",
        help="Führt den täglichen Ingestion-Job sofort einmal aus und beendet",
    )
    parser.add_argument(
        "--run-weekly-now",
        action="store_true",
        help="Führt den wöchentlichen Job sofort einmal aus und beendet",
    )
    parser.add_argument(
        "--run-monthly-now",
        action="store_true",
        help="Führt den monatlichen Job sofort einmal aus und beendet",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Erzwingt Ausführung / neue Revisionsstufe bei sofortigem Lauf (--run-weekly-now)",
    )
    parser.add_argument(
        "--force-weekly",
        action="store_true",
        default=os.environ.get("FORCE_WEEKLY", "").lower() in ("true", "1", "yes"),
        help="Erzwingt bei jedem wöchentlichen Lauf eine neue Revisionsstufe (.v2.md etc.)",
    )
    parser.add_argument(
        "--skip-startup-sync",
        action="store_true",
        help="Überspringt den initialen Startup-Check und Quell-Aktualisierung",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Initialisiert den Zeitplan, gibt anstehende Jobs aus und beendet sofort",
    )
    args = parser.parse_args(argv)

    if args.run_daily_now:
        success = job_daily_ingestion(data_dir=args.data_dir)
        return 0 if success else 1

    if args.run_weekly_now:
        success = job_weekly_newsletter(
            data_dir=args.data_dir, force=args.force or args.force_weekly
        )
        return 0 if success else 1

    if args.run_monthly_now:
        success = job_monthly_scoring(data_dir=args.data_dir, force=True)
        return 0 if success else 1

    setup_schedule(
        daily_time=args.daily_time,
        weekly_time=args.weekly_time,
        monthly_time=args.monthly_time,
        data_dir=args.data_dir,
        force_weekly=args.force_weekly,
    )

    if args.dry_run:
        jobs = schedule.get_jobs()
        logger.info("Dry-Run: %d Jobs erfolgreich registriert:", len(jobs))
        for j in jobs:
            logger.info(" - %s (nächster Lauf: %s)", j, j.next_run)
        return 0

    if not args.skip_startup_sync:
        initial_startup_check_and_sync(data_dir=args.data_dir)

    run_scheduler_loop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
