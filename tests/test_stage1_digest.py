"""
Unit-Tests für Stufe 1 (Selektion, Gemini-Schemas, Verifier 1 & Roh-Archivierung).
Prüft insbesondere Kriterium B3 (Verhinderung von Negations-Lücken) und Offline-Ausführung.
"""

from __future__ import annotations

import gzip
import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock

from digest_extractor import DigestExtractor
from digest_schemas import ExtractedFact, FactEvidence, TopicCluster, WeeklyDigestSchema
from item_models import NewsItem
from item_store import ItemStore
from verifier_stage1 import Stage1Verifier
from watermark_manager import (
    WatermarkManager,
    get_previous_iso_week,
    load_previous_newsletter_mentions,
)


class TestWatermarkManager(unittest.TestCase):
    def test_get_previous_iso_week(self) -> None:
        self.assertEqual(get_previous_iso_week("2026-W41"), "2026-W40")
        self.assertEqual(get_previous_iso_week("2026-W40"), "2026-W39")
        self.assertEqual(get_previous_iso_week("2026-W01"), "2025-W52")
        with self.assertRaises(ValueError):
            get_previous_iso_week("invalid-week")

    def test_load_previous_newsletter_mentions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            base = Path(tmp_dir)
            digests_dir = base / "digests"
            digests_dir.mkdir(parents=True)
            manifest = digests_dir / "digest-2026-W40.manifest.json"
            manifest.write_text(
                json.dumps(
                    {
                        "inputs": {
                            "item_hashes": {"item-id-123": "hash123"},
                        }
                    }
                ),
                encoding="utf-8",
            )
            digest = digests_dir / "digest-2026-W40.json"
            digest.write_text(
                json.dumps(
                    {
                        "clusters": [
                            {
                                "source_items": [
                                    {
                                        "item_id": "item-id-456",
                                        "url": "https://test.com/from-digest",
                                    }
                                ]
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            nl_dir = base / "newsletters"
            nl_dir.mkdir(parents=True)
            (nl_dir / "newsletter-2026-W40.md").write_text(
                "# W40\n\n- [Titel](https://test.com/from-nl)\n", encoding="utf-8"
            )

            ids, urls = load_previous_newsletter_mentions(base, "2026-W40")
            self.assertIn("item-id-123", ids)
            self.assertIn("item-id-456", ids)
            self.assertIn("https://test.com/from-digest", urls)
            self.assertIn("https://test.com/from-nl", urls)

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

    def test_select_items_nachzuegler_und_alter_ausschluss(self) -> None:
        """
        Prüft:
        - Meldung aus Zielwoche W (2026-W41) wird selektiert
        - Nachzügler aus W-1 (2026-W40) wird selektiert, WENN noch nicht im W40 Newsletter erwähnt
        - Vorwochen-Meldung aus W-1 wird IGNORIERT, wenn bereits im W40 Newsletter erwähnt
        - Veraltete Meldungen (W-2 oder älter, z. B. KW 35) werden STRIKT ausgeschlossen
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            base_dir = Path(tmp_dir)
            wm_file = base_dir / "watermark.json"
            wm_mgr = WatermarkManager(watermark_path=wm_file)
            store = ItemStore(items_dir=base_dir / "items")

            # Vorherigen Newsletter für W40 anlegen
            nl_dir = base_dir / "newsletters"
            nl_dir.mkdir(parents=True)
            (nl_dir / "newsletter-2026-W40.md").write_text(
                "# Newsletter KW 40\n\n"
                "- [Erwähnte Vorwochenmeldung](https://test.com/w40-already-covered)\n",
                encoding="utf-8",
            )

            # Item 1: Aktuelle Woche (2026-W41)
            item_w41 = NewsItem(
                item_id="item-w41",
                provider="p2p-game",
                source_tier="primary",
                url="https://p2p-game.com/p2p-news/2026-10-12-estateguru.html",
                title="EstateGuru Update W41",
                published_date="2026-10-12",  # KW 42 bzw. W41
                first_seen_at="2026-10-12T10:00:00+00:00",
                last_seen_at="2026-10-12T10:00:00+00:00",
                item_content_hash="h-w41",
                page_snapshot_hash="s-w41",
                content_plain="Text W41",
            )
            # Item 2: Nachzügler aus W40 (2026-10-02), NICHT im Newsletter
            item_w40_nachzuegler = NewsItem(
                item_id="item-w40-late",
                provider="nectaro",
                source_tier="primary",
                url="https://nectaro.eu/blog/late-update",
                title="Nectaro Nachzügler W40",
                published_date="2026-10-02",  # 2026-W40
                first_seen_at="2026-10-05T08:00:00+00:00",
                last_seen_at="2026-10-05T08:00:00+00:00",
                item_content_hash="h-w40-late",
                page_snapshot_hash="s-w40-late",
                content_plain="Text W40 Nachzügler",
            )
            # Item 3: W40 Meldung, die BEREITS im W40 Newsletter war
            item_w40_already = NewsItem(
                item_id="item-w40-covered",
                provider="rethink-p2p",
                source_tier="secondary",
                url="https://test.com/w40-already-covered",
                title="Bereits erwähnte Meldung",
                published_date="2026-10-01",  # 2026-W40
                first_seen_at="2026-10-01T10:00:00+00:00",
                last_seen_at="2026-10-01T10:00:00+00:00",
                item_content_hash="h-w40-cov",
                page_snapshot_hash="s-w40-cov",
                content_plain="Text W40 Already",
            )
            # Item 4: Uralt-Meldung aus KW 35 (2026-08-24) -> MUSS ausgeschlossen werden
            item_w35_old = NewsItem(
                item_id="item-w35-old",
                provider="passives-einkommen",
                source_tier="secondary",
                url="https://passives-einkommen-mit-p2p.de/p2p-kredite-35-26-ventus/",
                title="Ventus Reorganisation KW 35",
                published_date="2026-08-24",  # 2026-W35
                first_seen_at="2026-10-05T08:00:00+00:00",
                last_seen_at="2026-10-05T08:00:00+00:00",
                item_content_hash="h-w35",
                page_snapshot_hash="s-w35",
                content_plain="Text W35 Alt",
            )

            store.upsert_item(item_w41)
            store.upsert_item(item_w40_nachzuegler)
            store.upsert_item(item_w40_already)
            store.upsert_item(item_w35_old)

            # Prüfe Zielwoche 2026-W41 (Woche von 2026-10-05 bis 2026-10-11)
            # Montag 2026-10-05 ist KW 41. Erstellen wir ein echtes KW 41 Item:
            item_kw41_real = NewsItem(
                item_id="item-kw41-real",
                provider="mintos",
                source_tier="primary",
                url="https://mintos.com/blog/w41-update",
                title="Mintos KW41 Update",
                published_date="2026-10-07",  # 2026-W41
                first_seen_at="2026-10-07T10:00:00+00:00",
                last_seen_at="2026-10-07T10:00:00+00:00",
                item_content_hash="h-kw41",
                page_snapshot_hash="s-kw41",
                content_plain="Text Mintos KW41",
            )
            store.upsert_item(item_kw41_real)

            selected = wm_mgr.select_items_for_run(
                store=store,
                iso_week="2026-W41",
            )

            selected_ids = {x.item_id for x in selected}
            # 1. KW 41 Item muss enthalten sein
            self.assertIn("item-kw41-real", selected_ids)
            # 2. W40 Nachzügler muss enthalten sein
            self.assertIn("item-w40-late", selected_ids)
            # 3. Bereits erwähnte W40 Meldung darf NICHT enthalten sein
            self.assertNotIn("item-w40-covered", selected_ids)
            # 4. KW 35 Uralt-Meldung darf KEINESFALLS enthalten sein
            self.assertNotIn("item-w35-old", selected_ids)


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

    def test_build_prompt_includes_topics_and_severity(self) -> None:
        item = NewsItem(
            item_id="item-meta-test",
            provider="rethink-p2p",
            source_tier="secondary",
            url="https://rethink-p2p.de/news#test",
            title="Kritisches Update",
            published_date="2026-10-05",
            first_seen_at="2026-10-05T10:00:00+00:00",
            last_seen_at="2026-10-05T10:00:00+00:00",
            item_content_hash="h-meta",
            page_snapshot_hash="s-meta",
            platforms=["ventus"],
            topics=["risiko_ausfaelle", "regulierung_legal"],
            sentiment="negative",
            severity="high",
            content_plain="Restrukturierung und BaFin-Warnung bei Ventus.",
        )
        extractor = DigestExtractor(api_key="mock-key")
        prompt = extractor.build_prompt([item], iso_week="2026-W41")

        self.assertIn("- Themen-Tags: risiko_ausfaelle, regulierung_legal", prompt)
        self.assertIn("- Dringlichkeit: high (Sentiment: negative)", prompt)
        self.assertIn("Nutzung von Vorab-Tags & Dringlichkeit", prompt)

    def test_severity_prioritization_sorting(self) -> None:
        items = [
            NewsItem(
                item_id="item-low",
                provider="p2p-game",
                source_tier="secondary",
                url="https://p2p-game.com/1",
                title="Low item",
                published_date="2026-10-06",
                first_seen_at="2026-10-06T10:00:00Z",
                last_seen_at="2026-10-06T10:00:00Z",
                item_content_hash="h1",
                page_snapshot_hash="s1",
                severity="low",
                content_plain="Allgemeine Info.",
            ),
            NewsItem(
                item_id="item-high",
                provider="rethink-p2p",
                source_tier="secondary",
                url="https://rethink-p2p.com/2",
                title="High item",
                published_date="2026-10-04",
                first_seen_at="2026-10-04T10:00:00Z",
                last_seen_at="2026-10-04T10:00:00Z",
                item_content_hash="h2",
                page_snapshot_hash="s2",
                severity="high",
                content_plain="Insolvenzrisiko gemeldet.",
            ),
            NewsItem(
                item_id="item-med",
                provider="p2p-empire",
                source_tier="secondary",
                url="https://p2pempire.com/3",
                title="Medium item",
                published_date="2026-10-05",
                first_seen_at="2026-10-05T10:00:00Z",
                last_seen_at="2026-10-05T10:00:00Z",
                item_content_hash="h3",
                page_snapshot_hash="s3",
                severity="medium",
                content_plain="Zinssenkung angekündigt.",
            ),
        ]
        severity_order = {"high": 0, "medium": 1, "low": 2}
        sorted_items = sorted(
            items,
            key=lambda it: (
                severity_order.get(it.severity, 2),
                -(
                    datetime.fromisoformat(it.published_date).timestamp()
                    if it.published_date
                    else 0
                ),
            ),
        )
        self.assertEqual(
            [it.item_id for it in sorted_items],
            ["item-high", "item-med", "item-low"],
        )

    def test_digest_extractor_default_model(self) -> None:
        extractor = DigestExtractor(api_key="mock")
        self.assertEqual(extractor.model_name, "gemini-3.8-flash")

    def test_digest_extractor_prompt_diet(self) -> None:
        item = NewsItem(
            item_id="item-diet",
            provider="nectaro",
            source_tier="primary",
            url="https://nectaro.eu/blog/long-url-with-slug",
            title="Title",
            published_date="2026-10-12",
            first_seen_at="2026-10-12T10:00:00+00:00",
            last_seen_at="2026-10-12T10:00:00+00:00",
            item_content_hash="h1",
            page_snapshot_hash="s1",
            content_plain="A" * 5000,
        )
        extractor = DigestExtractor(api_key="mock")
        prompt = extractor.build_prompt([item], iso_week="2026-W42")
        self.assertNotIn("- URL:", prompt)
        self.assertIn("[... gekürzt für Prompt-Effizienz ...]", prompt)

    def test_digest_extractor_404_fallthrough(self) -> None:
        item = NewsItem(
            item_id="item-404-test",
            provider="nectaro",
            source_tier="primary",
            url="https://nectaro.eu/stats",
            title="Nectaro Stats",
            published_date="2026-10-02",
            first_seen_at="2026-10-02T10:00:00+00:00",
            last_seen_at="2026-10-02T10:00:00+00:00",
            item_content_hash="h-404",
            page_snapshot_hash="s-404",
            content_plain="Nectaro vergab 1.000.000 Euro Kredite.",
        )
        mock_response_json = {
            "schema_version": "2.2",
            "iso_week": "2026-W40",
            "clusters": [
                {
                    "cluster_id": "c-nectaro",
                    "topic": "zahlen_statistik",
                    "platforms": ["nectaro"],
                    "title": "Nectaro Zahlen",
                    "facts": [
                        {
                            "fact_id": "f-01",
                            "statement": "Nectaro vergab 1.000.000 Euro an Krediten.",
                            "evidence": [
                                {
                                    "item_id": "item-404-test",
                                    "evidence_quote": "Nectaro vergab 1.000.000 Euro Kredite.",
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
        mock_resp = MagicMock()
        mock_resp.text = json.dumps(mock_response_json)
        mock_resp.model_version = "gemini-flash-latest"
        mock_resp.usage_metadata = None

        mock_client.models.generate_content.side_effect = [
            Exception("404 NOT_FOUND: model not available"),
            mock_resp,
        ]

        with tempfile.TemporaryDirectory() as tmp_dir:
            extractor = DigestExtractor(
                api_key="mock",
                runs_dir=Path(tmp_dir) / "runs",
                digests_dir=Path(tmp_dir) / "digests",
            )
            digest, path, metrics = extractor.extract_digest(
                items=[item],
                iso_week="2026-W40",
                run_id="test_404_run",
                custom_client=mock_client,
            )
            self.assertEqual(metrics["facts_verified"], 1)
            self.assertEqual(mock_client.models.generate_content.call_count, 2)


if __name__ == "__main__":
    unittest.main()
