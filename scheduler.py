"""
Autarker Zeitplan-Daemon für periodische P2P-News-Pipelines via 'schedule'.

Führt zwei periodische Hintergrund-Jobs aus:
1. Wöchentlich (Montag um 06:00 Uhr Berliner Zeit):
   Scraping, Fakten-Clustering & Newsletter-Draft (pipeline_orchestrator.py).
2. Monatlich (am 1. Tag des Monats um 07:00 Uhr Berliner Zeit):
   Vollständiges 4-Säulen-Audit-Scoring & Plattform-Rankings (run_audit_scoring.py).

Unterstützt sauberes Signal-Handling (SIGTERM, SIGINT) für Graceful Shutdown in Containern.
"""

from __future__ import annotations

import argparse
import logging
import signal
import sys
import time
from datetime import datetime
from pathlib import Path
from types import FrameType

import schedule

from pipeline_orchestrator import run_pipeline
from run_audit_scoring import run_full_audit

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


def job_weekly_newsletter(data_dir: Path | str = "data") -> bool:
    """Führt den wöchentlichen Scraping- und Newsletter-Draft-Lauf durch."""
    logger.info("=== [SCHEDULER] Starte wöchentlichen News- & Newsletter-Lauf ===")
    try:
        ret = run_pipeline(data_dir=data_dir, do_scrape=True, is_publish=False)
        if ret == 0:
            logger.info(
                "=== [SCHEDULER] Wöchentlicher Lauf erfolgreich abgeschlossen ==="
            )
            return True
        logger.error(
            "=== [SCHEDULER] Wöchentlicher Lauf mit Returncode %d beendet ===", ret
        )
        return False
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
    weekly_time: str = "06:00",
    monthly_time: str = "07:00",
    data_dir: Path | str = "data",
) -> None:
    """Registriert alle periodischen Jobs in 'schedule'."""
    schedule.clear()
    schedule.every().monday.at(weekly_time).do(job_weekly_newsletter, data_dir=data_dir)
    schedule.every().day.at(monthly_time).do(job_monthly_scoring, force=False)
    logger.info(
        "Zeitplan initialisiert: Wöchentlich montags um %s | Monatlich am 1. um %s (Europe/Berlin)",
        weekly_time,
        monthly_time,
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
        "--weekly-time",
        default="06:00",
        help="Uhrzeit für den wöchentlichen Montags-Lauf (HH:MM, Standard: 06:00)",
    )
    parser.add_argument(
        "--monthly-time",
        default="07:00",
        help="Uhrzeit für den monatlichen Lauf am 1. (HH:MM, Standard: 07:00)",
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
        "--dry-run",
        action="store_true",
        help="Initialisiert den Zeitplan, gibt anstehende Jobs aus und beendet sofort",
    )
    args = parser.parse_args(argv)

    if args.run_weekly_now:
        success = job_weekly_newsletter()
        return 0 if success else 1

    if args.run_monthly_now:
        success = job_monthly_scoring(force=True)
        return 0 if success else 1

    setup_schedule(weekly_time=args.weekly_time, monthly_time=args.monthly_time)

    if args.dry_run:
        jobs = schedule.get_jobs()
        logger.info("Dry-Run: %d Jobs erfolgreich registriert:", len(jobs))
        for j in jobs:
            logger.info(" - %s (nächster Lauf: %s)", j, j.next_run)
        return 0

    run_scheduler_loop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
