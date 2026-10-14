"""
Tests für den autarken Zeitplan-Daemon (scheduler.py).
"""

from __future__ import annotations

import signal
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import schedule

import scheduler


def test_setup_schedule() -> None:
    """Prüft, ob setup_schedule drei Jobs mit korrekten Zeiten registriert."""
    schedule.clear()
    scheduler.setup_schedule(
        daily_time="05:30", weekly_time="06:30", monthly_time="07:45"
    )
    jobs = schedule.get_jobs()
    assert len(jobs) == 3
    # Ein Job wöchentlich, zwei Jobs täglich
    units = {j.unit for j in jobs}
    assert "weeks" in units
    assert "days" in units
    day_times = {
        j.at_time.strftime("%H:%M") for j in jobs if j.unit == "days" and j.at_time
    }
    assert "05:30" in day_times
    assert "07:45" in day_times


def test_setup_schedule_default_times() -> None:
    """Prüft, ob setup_schedule standardmäßig 06:00 (täglich), 06:30 (wöchentlich) und 07:00 (monatlich) setzt."""
    schedule.clear()
    scheduler.setup_schedule()
    jobs = schedule.get_jobs()
    assert len(jobs) == 3
    weekly_job = next(j for j in jobs if j.unit == "weeks")
    assert weekly_job.at_time is not None
    assert weekly_job.at_time.strftime("%H:%M") == "06:30"
    day_times = {
        j.at_time.strftime("%H:%M") for j in jobs if j.unit == "days" and j.at_time
    }
    assert "06:00" in day_times
    assert "07:00" in day_times


@patch("item_extractor.process_all_scraped_news")
@patch("p2p_news_scraper.P2PNewsScraper")
def test_job_daily_ingestion_success(
    mock_scraper_cls: MagicMock,
    mock_process_items: MagicMock,
) -> None:
    """Prüft den erfolgreichen Ablauf des täglichen Ingestion-Jobs (Stage 0)."""
    mock_process_items.return_value = (5, 25)
    result = scheduler.job_daily_ingestion(data_dir="data")
    assert result is True
    assert mock_scraper_cls.called
    mock_process_items.assert_called_once()


@patch("p2p_news_scraper.P2PNewsScraper")
def test_job_daily_ingestion_exception(mock_scraper_cls: MagicMock) -> None:
    """Prüft, dass Exceptions im täglichen Ingestion-Job abgefangen werden."""
    mock_scraper_cls.side_effect = RuntimeError("Scraper Fehler")
    result = scheduler.job_daily_ingestion(data_dir="data")
    assert result is False


@patch("scheduler.job_daily_ingestion")
def test_main_run_daily_now(mock_daily: MagicMock) -> None:
    """Prüft den CLI-Aufruf --run-daily-now."""
    mock_daily.return_value = True
    exit_code = scheduler.main(["--run-daily-now"])
    assert exit_code == 0
    mock_daily.assert_called_once_with(data_dir="data")


@patch("scheduler.run_pipeline")
def test_job_weekly_newsletter_success(mock_run_pipeline: MagicMock) -> None:
    """Prüft erfolgreichen Durchlauf des wöchentlichen Jobs."""
    mock_run_pipeline.return_value = 0
    result = scheduler.job_weekly_newsletter()
    assert result is True
    mock_run_pipeline.assert_called_once_with(
        data_dir="data", do_scrape=True, is_publish=True, is_approved=True
    )


@patch("scheduler.run_pipeline")
def test_job_weekly_newsletter_error_code(mock_run_pipeline: MagicMock) -> None:
    """Prüft Fehlerbehandlung bei Non-Zero Exitcode."""
    mock_run_pipeline.return_value = 1
    result = scheduler.job_weekly_newsletter()
    assert result is False


@patch("scheduler.run_pipeline")
def test_job_weekly_newsletter_exception(mock_run_pipeline: MagicMock) -> None:
    """Prüft, dass Exceptions abgefangen werden und False zurückliefern."""
    mock_run_pipeline.side_effect = RuntimeError("Netzwerkfehler")
    result = scheduler.job_weekly_newsletter()
    assert result is False


@patch("scheduler.run_pipeline")
def test_job_weekly_newsletter_file_exists_handled(
    mock_run_pipeline: MagicMock,
) -> None:
    """Prüft, dass FileExistsError bei Write-Once Schutz abgefangen wird und True liefert."""
    mock_run_pipeline.side_effect = FileExistsError("Datei existiert bereits")
    result = scheduler.job_weekly_newsletter()
    assert result is True


@patch("scheduler.run_pipeline")
def test_job_weekly_newsletter_forced(mock_run_pipeline: MagicMock) -> None:
    """Prüft, dass force=True force_revision=True an run_pipeline übergibt."""
    mock_run_pipeline.return_value = 0
    result = scheduler.job_weekly_newsletter(force=True)
    assert result is True
    mock_run_pipeline.assert_called_once_with(
        data_dir="data",
        do_scrape=True,
        is_publish=True,
        is_approved=True,
        force_revision=True,
    )


@patch("scheduler.run_full_audit")
def test_job_monthly_scoring_skipped_when_not_first(
    mock_run_full_audit: MagicMock,
) -> None:
    """Prüft, dass der monatliche Job an Nicht-1.-Tagen übersprungen wird."""
    with patch("scheduler.datetime") as mock_dt:
        mock_now = MagicMock()
        mock_now.day = 15
        mock_dt.now.return_value = mock_now

        result = scheduler.job_monthly_scoring(force=False)
        assert result is False
        mock_run_full_audit.assert_not_called()


@patch("scheduler.run_full_audit")
def test_job_monthly_scoring_runs_on_first_of_month(
    mock_run_full_audit: MagicMock,
) -> None:
    """Prüft, dass der monatliche Job am 1. des Monats ausgeführt wird."""
    mock_run_full_audit.return_value = (5, Path("data/rankings/test.md"))
    with patch("scheduler.datetime") as mock_dt:
        mock_now = MagicMock()
        mock_now.day = 1
        mock_dt.now.return_value = mock_now

        result = scheduler.job_monthly_scoring(force=False)
        assert result is True
        mock_run_full_audit.assert_called_once()


@patch("scheduler.run_full_audit")
def test_job_monthly_scoring_forced(mock_run_full_audit: MagicMock) -> None:
    """Prüft, dass force=True den Datums-Guard überschreibt."""
    mock_run_full_audit.return_value = (3, Path("data/rankings/test.md"))
    result = scheduler.job_monthly_scoring(force=True)
    assert result is True
    mock_run_full_audit.assert_called_once()


def test_handle_shutdown() -> None:
    """Prüft das Signal-Handling zur Deaktivierung der Hauptschleife."""
    scheduler._running = True
    scheduler.handle_shutdown(signal.SIGTERM, None)
    assert scheduler._running is False


def test_main_dry_run() -> None:
    """Prüft den CLI-Dry-Run-Modus."""
    exit_code = scheduler.main(["--dry-run"])
    assert exit_code == 0


@patch("scheduler.job_weekly_newsletter")
def test_main_run_weekly_now_force(mock_weekly: MagicMock) -> None:
    """Prüft, dass --run-weekly-now mit --force das Flag force=True übergibt."""
    mock_weekly.return_value = True
    exit_code = scheduler.main(["--run-weekly-now", "--force"])
    assert exit_code == 0
    mock_weekly.assert_called_once_with(data_dir="data", force=True)


def test_get_target_newsletter_week_monday() -> None:
    """Prüft, dass an Montagen die Vorwoche als Zielwoche gewählt wird (lückenlos)."""
    from datetime import datetime, timezone

    # 2026-10-12 ist ein Montag (W42) -> Ziel muss 2026-W41 sein
    monday_dt = datetime(2026, 10, 12, 6, 0, 0, tzinfo=timezone.utc)
    week = scheduler.get_target_newsletter_week(monday_dt)
    assert week == "2026-W41"


def test_get_target_newsletter_week_other_days() -> None:
    """Prüft, dass an Tagen Di-So die aktuelle Kalenderwoche gewählt wird."""
    from datetime import datetime, timezone

    # 2026-10-14 ist ein Mittwoch (W42) -> Ziel muss 2026-W42 sein
    wednesday_dt = datetime(2026, 10, 14, 12, 0, 0, tzinfo=timezone.utc)
    week = scheduler.get_target_newsletter_week(wednesday_dt)
    assert week == "2026-W42"


@patch("scheduler.run_pipeline")
@patch("item_extractor.process_all_scraped_news")
@patch("p2p_news_scraper.P2PNewsScraper")
@patch("scheduler.run_full_audit")
@patch("scheduler.ensure_platform_profiles")
def test_initial_startup_check_and_sync_bootstrap(
    mock_ensure_profiles: MagicMock,
    mock_run_audit: MagicMock,
    mock_scraper_cls: MagicMock,
    mock_process_items: MagicMock,
    mock_run_pipeline: MagicMock,
    tmp_path: Path,
) -> None:
    """Prüft, dass fehlende Plattformen, Rankings und Newsletter initial erzeugt werden."""
    mock_ensure_profiles.return_value = ["mintos", "peerberry"]
    mock_process_items.return_value = (10, 50)
    mock_run_pipeline.return_value = 0

    scheduler.initial_startup_check_and_sync(data_dir=tmp_path)

    mock_ensure_profiles.assert_called_once_with(data_dir=tmp_path)
    mock_run_audit.assert_called_once_with(data_dir=tmp_path)
    assert mock_scraper_cls.called
    mock_process_items.assert_called_once_with(data_dir=tmp_path)
    mock_run_pipeline.assert_called_once()


@patch("scheduler.run_pipeline")
@patch("item_extractor.process_all_scraped_news")
@patch("p2p_news_scraper.P2PNewsScraper")
@patch("scheduler.run_full_audit")
@patch("scheduler.ensure_platform_profiles")
def test_initial_startup_check_and_sync_existing_data(
    mock_ensure_profiles: MagicMock,
    mock_run_audit: MagicMock,
    mock_scraper_cls: MagicMock,
    mock_process_items: MagicMock,
    mock_run_pipeline: MagicMock,
    tmp_path: Path,
) -> None:
    """Prüft, dass bei bereits vorhandenen Rankings und Newslettern keine Duplikate erzeugt werden."""
    mock_ensure_profiles.return_value = ["mintos"]
    mock_process_items.return_value = (5, 20)

    # Ranking anlegen
    rankings_dir = tmp_path / "rankings"
    rankings_dir.mkdir(parents=True)
    (rankings_dir / "platform-ranking-2026-10.md").write_text(
        "# Ranking", encoding="utf-8"
    )

    # Finalen Newsletter anlegen
    target_week = scheduler.get_target_newsletter_week()
    newsletters_dir = tmp_path / "newsletters"
    newsletters_dir.mkdir(parents=True)
    (newsletters_dir / f"newsletter-{target_week}.md").write_text(
        "# Published Newsletter", encoding="utf-8"
    )

    scheduler.initial_startup_check_and_sync(data_dir=tmp_path)

    mock_ensure_profiles.assert_called_once()
    mock_run_audit.assert_not_called()
    assert mock_scraper_cls.called
    mock_process_items.assert_called_once()
    mock_run_pipeline.assert_not_called()


@patch("scheduler.run_pipeline")
@patch("scheduler.run_full_audit")
@patch("scheduler.ensure_platform_profiles")
@patch("scheduler.job_daily_ingestion")
def test_initial_startup_check_and_sync_executes_ingestion_first(
    mock_ingestion: MagicMock,
    mock_ensure_profiles: MagicMock,
    mock_run_audit: MagicMock,
    mock_run_pipeline: MagicMock,
    tmp_path: Path,
) -> None:
    """Prüft, dass der tägliche Ingestion-Lauf (Scraper & RSS) beim Startup als allererstes ausgeführt wird."""
    calls: list[str] = []

    def fake_ingestion(*args: object, **kwargs: object) -> bool:
        calls.append("ingestion")
        return True

    def fake_profiles(*args: object, **kwargs: object) -> list[str]:
        calls.append("profiles")
        return []

    def fake_audit(*args: object, **kwargs: object) -> tuple[int, Path]:
        calls.append("audit")
        return (0, Path("test"))

    mock_ingestion.side_effect = fake_ingestion
    mock_ensure_profiles.side_effect = fake_profiles
    mock_run_audit.side_effect = fake_audit

    scheduler.initial_startup_check_and_sync(data_dir=tmp_path)

    assert len(calls) >= 2
    assert calls[0] == "ingestion"
    assert calls[1] == "profiles"


def test_entrypoint_script_flag_delegation() -> None:
    """Prüft, dass entrypoint.sh CLI-Flags (-c) und explizite Python-Aufrufe korrekt delegiert."""
    entrypoint = Path(__file__).parent.parent / "entrypoint.sh"
    assert entrypoint.exists(), "entrypoint.sh muss im Repository-Root existieren"

    # Test -c Flag-Delegation (analog zum GitHub Actions Smoke-Test)
    res_flag = subprocess.run(
        ["bash", str(entrypoint), "-c", "import sys; sys.exit(0)"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert res_flag.returncode == 0, (
        f"entrypoint.sh mit -c fehlgeschlagen: {res_flag.stderr}"
    )

    # Test expliziten python -c Aufruf
    res_py = subprocess.run(
        ["bash", str(entrypoint), "python", "-c", "import sys; sys.exit(0)"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert res_py.returncode == 0, (
        f"entrypoint.sh mit python -c fehlgeschlagen: {res_py.stderr}"
    )
