"""
Unit-Tests für die SQLite-Speicherarchitektur (Option 1: Hybrider Platin-Store).
Prüft SQLiteStore, ItemStore-Integration und SnapshotManager-Integration.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from item_models import NewsItem
from item_store import ItemStore
from snapshot_manager import SnapshotManager
from storage_sqlite import SQLiteStore


class TestSQLiteStore(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.tmp_dir.name) / "test_archive.db"
        self.store = SQLiteStore(self.db_path)

    def tearDown(self) -> None:
        self.tmp_dir.cleanup()

    def test_item_lifecycle_and_revisions(self) -> None:
        item = NewsItem(
            item_id="item-test-1",
            provider="rethink-p2p",
            source_tier="secondary",
            url="https://rethink-p2p.de/news/1",
            title="Erste Meldung",
            published_date="2026-10-01",
            first_seen_at="2026-10-01T10:00:00+00:00",
            last_seen_at="2026-10-01T10:00:00+00:00",
            item_content_hash="hash-1",
            page_snapshot_hash="snap-1",
            content_plain="Inhalt Version 1",
        )

        # 1. Neu einfügen
        saved1, status1 = self.store.upsert_item(item)
        self.assertEqual(status1, "neu")
        self.assertTrue(self.store.exists_item("item-test-1"))

        loaded = self.store.get_item("item-test-1")
        self.assertIsNotNone(loaded)
        assert loaded is not None
        self.assertEqual(loaded.title, "Erste Meldung")
        self.assertEqual(loaded.first_seen_at, "2026-10-01T10:00:00+00:00")

        # 2. Zweiter Scan: unverändert
        saved2, status2 = self.store.upsert_item(item)
        self.assertEqual(status2, "unverändert")
        self.assertEqual(saved2.first_seen_at, "2026-10-01T10:00:00+00:00")

        # 3. Dritter Scan: geändert
        item_changed = NewsItem(
            item_id="item-test-1",
            provider="rethink-p2p",
            source_tier="secondary",
            url="https://rethink-p2p.de/news/1",
            title="Erste Meldung (Aktualisiert)",
            published_date="2026-10-01",
            first_seen_at="2026-10-05T08:00:00+00:00",
            last_seen_at="2026-10-05T08:00:00+00:00",
            item_content_hash="hash-2",
            page_snapshot_hash="snap-2",
            content_plain="Inhalt Version 2",
        )
        saved3, status3 = self.store.upsert_item(item_changed)
        self.assertEqual(status3, "geändert")
        # first_seen_at muss unverändert die ursprüngliche Zeit tragen!
        self.assertEqual(saved3.first_seen_at, "2026-10-01T10:00:00+00:00")
        self.assertEqual(saved3.item_content_hash, "hash-2")

    def test_snapshot_compression_and_write_once(self) -> None:
        content = (
            "Umfangreicher Rohinhalt der P2P Webseite mit vielen Wiederholungen. " * 50
        )
        content_hash = SnapshotManager.compute_hash(content)

        # 1. Neu anlegen
        created1 = self.store.save_snapshot(
            snapshot_hash=content_hash,
            content=content,
            original_url="https://test.com",
        )
        self.assertTrue(created1)
        self.assertTrue(self.store.exists_snapshot(content_hash))

        # 2. Write-Once: erneut speichern schlägt nicht fehl, gibt False zurück
        created2 = self.store.save_snapshot(
            snapshot_hash=content_hash,
            content=content,
            original_url="https://test.com",
        )
        self.assertFalse(created2)

        # 3. Dekomprimieren und prüfen
        retrieved = self.store.get_snapshot(content_hash)
        self.assertEqual(retrieved, content)

    def test_runs_storage(self) -> None:
        self.store.save_run(
            run_id="run_2026-W40_test",
            stage=2,
            iso_week="2026-W40",
            model_version="gemini-3.8-flash",
            duration_s=12.5,
            usage={"total_token_count": 5000},
            prompt="Test Prompt",
            raw_response='{"status": "ok"}',
        )

        run = self.store.get_run("run_2026-W40_test", stage=2)
        self.assertIsNotNone(run)
        assert run is not None
        self.assertEqual(run["iso_week"], "2026-W40")
        self.assertEqual(run["duration_seconds"], 12.5)
        self.assertEqual(run["usage"]["total_token_count"], 5000)

        all_runs = self.store.get_all_runs()
        self.assertEqual(len(all_runs), 1)

    def test_get_items_for_period(self) -> None:
        item1 = NewsItem(
            item_id="i1",
            provider="nectaro",
            source_tier="primary",
            url="https://nectaro.eu/1",
            title="Item 1",
            published_date="2026-10-01",
            first_seen_at="2026-10-01T10:00:00+00:00",
            last_seen_at="2026-10-01T10:00:00+00:00",
            item_content_hash="h1",
            page_snapshot_hash="s1",
            content_plain="text 1",
        )
        item2 = NewsItem(
            item_id="i2",
            provider="nectaro",
            source_tier="primary",
            url="https://nectaro.eu/2",
            title="Item 2",
            published_date="2026-10-03",
            first_seen_at="2026-10-03T10:00:00+00:00",
            last_seen_at="2026-10-03T10:00:00+00:00",
            item_content_hash="h2",
            page_snapshot_hash="s2",
            content_plain="text 2",
        )
        item3 = NewsItem(
            item_id="i3",
            provider="nectaro",
            source_tier="primary",
            url="https://nectaro.eu/3",
            title="Item 3",
            published_date="2026-10-05",
            first_seen_at="2026-10-05T10:00:00+00:00",
            last_seen_at="2026-10-05T10:00:00+00:00",
            item_content_hash="h3",
            page_snapshot_hash="s3",
            content_plain="text 3",
        )
        self.store.batch_upsert_items([item1, item2, item3])

        # Fenster von 2026-10-01T12:00:00 bis 2026-10-04T00:00:00 -> nur item2
        period_items = self.store.get_items_for_period(
            watermark_from_iso="2026-10-01T12:00:00+00:00",
            watermark_to_iso="2026-10-04T00:00:00+00:00",
        )
        self.assertEqual(len(period_items), 1)
        self.assertEqual(period_items[0].item_id, "i2")


class TestStoreSQLiteIntegration(unittest.TestCase):
    def test_item_store_with_sqlite_backend(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_file = Path(tmp_dir) / "archive.db"
            store = ItemStore(items_dir=Path(tmp_dir) / "items", db_path=db_file)

            item = NewsItem(
                item_id="it-01",
                provider="swaper",
                source_tier="primary",
                url="https://swaper.com/news/1",
                title="Swaper News",
                published_date="2026-10-02",
                first_seen_at="2026-10-02T10:00:00+00:00",
                last_seen_at="2026-10-02T10:00:00+00:00",
                item_content_hash="sh1",
                page_snapshot_hash="ss1",
                content_plain="plain content",
            )
            saved, status = store.upsert_item(item)
            self.assertEqual(status, "neu")

            # Aus SQLite über ItemStore geladen
            loaded = store.get_item("it-01")
            self.assertIsNotNone(loaded)
            assert loaded is not None
            self.assertEqual(loaded.title, "Swaper News")

    def test_snapshot_manager_with_sqlite_backend(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_file = Path(tmp_dir) / "archive.db"
            mgr = SnapshotManager(base_dir=Path(tmp_dir) / "snapshots", db_path=db_file)

            content = "Rohdaten der Plattform"
            h, p, created = mgr.save_page_snapshot(content, "https://swaper.com")
            self.assertTrue(created)

            # Zweiter Durchlauf
            h2, p2, created2 = mgr.save_page_snapshot(content, "https://swaper.com")
            self.assertFalse(created2)

            retrieved = mgr.get_page_snapshot(h)
            self.assertEqual(retrieved, content)


if __name__ == "__main__":
    unittest.main()
