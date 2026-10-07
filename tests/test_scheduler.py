"""
Tests für den autarken Zeitplan-Daemon (scheduler.py).
"""

from __future__ import annotations

import signal
from pathlib import Path
from unittest.mock import MagicMock, patch

import schedule

import scheduler


def test_setup_schedule() -> None:
    """Prüft, ob setup_schedule zwei Jobs mit korrekten Zeiten registriert."""
    schedule.clear()
    scheduler.setup_schedule(weekly_time="06:30", monthly_time="07:45")
    jobs = schedule.get_jobs()
    assert len(jobs) == 2
    # Ein Job wöchentlich, ein Job täglich
    units = {j.unit for j in jobs}
    assert "weeks" in units
    assert "days" in units


@patch("scheduler.run_pipeline")
def test_job_weekly_newsletter_success(mock_run_pipeline: MagicMock) -> None:
    """Prüft erfolgreichen Durchlauf des wöchentlichen Jobs."""
    mock_run_pipeline.return_value = 0
    result = scheduler.job_weekly_newsletter()
    assert result is True
    mock_run_pipeline.assert_called_once_with(
        data_dir="data", do_scrape=True, is_publish=False
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
