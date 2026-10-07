"""
Unit-Tests für Stufe 1 (Selektion, Gemini-Schemas, Verifier 1 & Roh-Archivierung).
Prüft insbesondere Kriterium B3 (Verhinderung von Negations-Lücken) und Offline-Ausführung.
"""

from __future__ import annotations

import gzip
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock

from digest_extractor import DigestExtractor
from digest_schemas import ExtractedFact, FactEvidence, TopicCluster, WeeklyDigestSchema
from item_models import NewsItem
from item_store import ItemStore
from verifier_stage1 import Stage1Verifier
from watermark_manager import WatermarkManager


class TestWatermarkManager(unittest.TestCase):
    def test_watermark_update_and_selection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            wm_file = Path(tmp_dir) / "watermark.json"
            wm_mgr = WatermarkManager(watermark_path=wm_file)

            self.assertIsNone(wm_mgr.get_last_watermark())

            wm_mgr.update_watermark("2026-09-28T00:00:00+00:00", run_id="run_1")
            self.assertEqual(wm_mgr.get_last_watermark(), "2026-09-28T00:00:00+00:00")

            # Erstelle ItemStore mit zwei Items
            items_dir = Path(tmp_dir) / "items"
            store = ItemStore(items_dir=items_dir)

            item_old = NewsItem(
                item_id="item-old",
                provider="rethink-p2p",
                source_tier="secondary",
                url="https://test.com/old",
                title="Alte News",
                published_date="2026-09-20",
                first_seen_at="2026-09-20T10:00:00+00:00",
                last_seen_at="2026-09-20T10:00:00+00:00",
                item_content_hash="h1",
                page_snapshot_hash="s1",
                content_plain="Text alt",
            )
            item_new = NewsItem(
                item_id="item-new",
                provider="rethink-p2p",
                source_tier="secondary",
                url="https://test.com/new",
                title="Neue News",
                published_date="2026-10-01",
                first_seen_at="2026-10-01T10:00:00+00:00",
                last_seen_at="2026-10-01T10:00:00+00:00",
                item_content_hash="h2",
                page_snapshot_hash="s2",
                content_plain="Text neu",
            )
            store.upsert_item(item_old)
            store.upsert_item(item_new)

            # Exactly-Once Selektion: Nur item_new darf selektiert werden
            selected = wm_mgr.select_items_for_run(
                store=store,
                current_run_time_iso="2026-10-04T12:00:00+00:00",
            )
            self.assertEqual(len(selected), 1)
            self.assertEqual(selected[0].item_id, "item-new")


class TestStage1Verifier(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.log_file = Path(self.tmp_dir.name) / "rejected-facts.jsonl"
        self.verifier = Stage1Verifier(log_path=self.log_file)

    def tearDown(self) -> None:
        self.tmp_dir.cleanup()

    def test_b3_negation_tampering_is_rejected(self) -> None:
        """Kriterium B3: Zitat mit entferntem 'nicht' MUSS abgelehnt werden."""
        original_text = (
            "Letzte Woche hatte ich darüber berichtet, dass die lettische Zentralbank "
            "der SIA IBC Invest eine Lizenz als Wertpapierfirma erteilt hat. "
            "Meine Einordnung, dass Esketit damit auf ein reguliertes Fundament gestellt wird, "
            "war allerdings nicht korrekt."
        )
        item = NewsItem(
            item_id="item-esketit",
            provider="rethink-p2p",
            source_tier="secondary",
            url="https://rethink-p2p.de/news/korrektur/",
            title="Korrektur Esketit",
            published_date="2026-09-28",
            first_seen_at="2026-09-28T12:00:00+00:00",
            last_seen_at="2026-09-28T12:00:00+00:00",
            item_content_hash="h-esketit",
            page_snapshot_hash="s-esketit",
            content_plain=original_text,
        )
        items_map = {"item-esketit": item}

        # 1. Valider Fakt mit exaktem Zitat -> Akzeptiert
        valid_fact = ExtractedFact(
            fact_id="f-01",
            statement="Die Einordnung bezüglich Esketit war nicht korrekt.",
            evidence=[
                FactEvidence(
                    item_id="item-esketit",
                    evidence_quote="war allerdings nicht korrekt.",
                )
            ],
        )
        digest = WeeklyDigestSchema(
            iso_week="2026-W40",
            clusters=[
                TopicCluster(
                    cluster_id="c-01",
                    topic="regulierung_legal",
                    platforms=["esketit"],
                    title="Esketit Lizenz",
                    facts=[valid_fact],
                )
            ],
        )
        v_digest, v_count, r_count = self.verifier.verify_digest(digest, items_map)
        self.assertEqual(v_count, 1)
        self.assertEqual(r_count, 0)
        self.assertEqual(len(v_digest.clusters[0].facts), 1)

        # 2. Manipulierter Fakt: 'nicht' wurde entfernt -> MUSS ABGELEHNT WERDEN!
        manipulated_fact = ExtractedFact(
            fact_id="f-02",
            statement="Die Einordnung bezüglich Esketit war korrekt.",
            evidence=[
                FactEvidence(
                    item_id="item-esketit",
                    evidence_quote="war allerdings korrekt.",  # 'nicht' fehlt!
                )
            ],
        )
        bad_digest = WeeklyDigestSchema(
            iso_week="2026-W40",
            clusters=[
                TopicCluster(
                    cluster_id="c-01",
                    topic="regulierung_legal",
                    platforms=["esketit"],
                    title="Esketit Lizenz",
                    facts=[manipulated_fact],
                )
            ],
        )
        bad_v_digest, bad_v_count, bad_r_count = self.verifier.verify_digest(
            bad_digest, items_map
        )
        self.assertEqual(bad_v_count, 0)
        self.assertEqual(bad_r_count, 1)
        # Cluster hat keine gültigen Fakten mehr
        self.assertEqual(len(bad_v_digest.clusters), 0)

        # Prüfe Rejection-Log
        self.assertTrue(self.log_file.exists())
        log_content = self.log_file.read_text(encoding="utf-8")
        self.assertIn("f-02", log_content)
        self.assertIn("nicht im Item item-esketit vorhanden", log_content)


class TestDigestExtractorOffline(unittest.TestCase):
    def test_mock_gemini_extraction_and_raw_archiving(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            runs_dir = Path(tmp_dir) / "runs"
            digests_dir = Path(tmp_dir) / "digests"

            item = NewsItem(
                item_id="item-mock-1",
                provider="nectaro",
                source_tier="primary",
                url="https://nectaro.eu/blog/stats",
                title="Nectaro Monatsbericht",
                published_date="2026-10-02",
                first_seen_at="2026-10-02T10:00:00+00:00",
                last_seen_at="2026-10-02T10:00:00+00:00",
                item_content_hash="h-nectaro",
                page_snapshot_hash="s-nectaro",
                content_plain="Nectaro vergab im September 4.073.350 Euro Kredite.",
            )

            mock_response_json = {
                "schema_version": "2.2",
                "iso_week": "2026-W40",
                "clusters": [
                    {
                        "cluster_id": "c-nectaro-stats",
                        "topic": "zahlen_statistik",
                        "platforms": ["nectaro"],
                        "title": "Nectaro Monatszahlen September",
                        "facts": [
                            {
                                "fact_id": "f-01",
                                "statement": "Nectaro vergab im September 4.073.350 Euro an Krediten.",
                                "evidence": [
                                    {
                                        "item_id": "item-mock-1",
                                        "evidence_quote": "Nectaro vergab im September 4.073.350 Euro Kredite.",
                                    }
                                ],
                                "verified": True,
                            }
                        ],
                        "conflicts": [],
                    }
                ],
            }

            mock_client = MagicMock()
            mock_model_response = MagicMock()
            mock_model_response.text = json.dumps(mock_response_json)
            mock_model_response.model_version = "gemini-3.8-flash-mock"
            mock_model_response.usage_metadata = MagicMock(
                prompt_token_count=120,
                candidates_token_count=85,
                total_token_count=205,
            )
            mock_client.models.generate_content.return_value = mock_model_response

            extractor = DigestExtractor(
                api_key="mock-key",
                runs_dir=runs_dir,
                digests_dir=digests_dir,
            )

            verified_digest, digest_path, metrics = extractor.extract_digest(
                items=[item],
                iso_week="2026-W40",
                run_id="test_run_123",
                custom_client=mock_client,
            )

            # 1. Prüfe, ob das Dossier korrekt geschrieben wurde
            self.assertTrue(digest_path.exists())
            self.assertEqual(metrics["facts_verified"], 1)
            self.assertEqual(metrics["facts_rejected"], 0)

            # 2. Prüfe, ob Roh-Archiv (.json.gz) existiert
            raw_archive = runs_dir / "test_run_123" / "llm" / "stage1_raw.json.gz"
            self.assertTrue(raw_archive.exists())

            # Decompress and check archive content
            archived_data = json.loads(
                gzip.decompress(raw_archive.read_bytes()).decode("utf-8")
            )
            self.assertEqual(archived_data["model_version"], "gemini-3.8-flash-mock")
            self.assertEqual(archived_data["usage"]["total_token_count"], 205)


if __name__ == "__main__":
    unittest.main()
