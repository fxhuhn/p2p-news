"""
Unit-Tests für Stufe 2 (Editorial-Schemas, Verifier 2, Markdown-Renderer, Manifest & Lifecycle).
Prüft insbesondere die Abnahmekriterien B4, B5, B6.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from digest_schemas import ExtractedFact, FactEvidence, TopicCluster, WeeklyDigestSchema
from editorial_schemas import (
    EditorialNewsletterSchema,
    EditorialParagraph,
    EditorialSection,
    EditorialSentence,
)
from item_models import NewsItem
from manifest_manager import ManifestManager
from markdown_renderer import MarkdownRenderer
from newsletter_generator import NewsletterGenerator
from verifier_stage2 import Stage2Verifier


class TestStage2Verifier(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.log_file = Path(self.tmp_dir.name) / "rejected-sentences.jsonl"
        self.verifier = Stage2Verifier(log_path=self.log_file)

        # Basis-Dossier mit verifiziertem Fakt
        self.fact1 = ExtractedFact(
            fact_id="f-01",
            statement="Nectaro vergab im September 4.073.350 Euro Kredite bei einem Zinssatz von 13,40 Prozent.",
            evidence=[
                FactEvidence(
                    item_id="item-01",
                    evidence_quote="Nectaro vergab im September 2026 Kredite im Wert von 4.073.350 € mit 13,40 % Zinsen.",
                )
            ],
            verified=True,
        )
        self.digest = WeeklyDigestSchema(
            iso_week="2026-W40",
            clusters=[
                TopicCluster(
                    cluster_id="c-01",
                    topic="zahlen_statistik",
                    platforms=["nectaro"],
                    title="Nectaro Zahlen",
                    facts=[self.fact1],
                )
            ],
        )

    def tearDown(self) -> None:
        self.tmp_dir.cleanup()

    def test_b4_valid_sentence_accepted(self) -> None:
        """Kriterium B4: Satz mit gedeckten Zahlen und gültiger fact_id wird akzeptiert."""
        sentence = EditorialSentence(
            text="Im September erzielte Nectaro ein Volumen von 4.073.350 Euro bei durchschnittlich 13,40 Prozent Zinsen.",
            fact_ids=["f-01"],
        )
        newsletter = EditorialNewsletterSchema(
            title="P2P Briefing",
            summary_lead="Übersicht",
            sections=[
                EditorialSection(
                    headline="Nectaro Wachstum",
                    category="zahlen_statistik",
                    platform_tags=["nectaro"],
                    sentences=[sentence],
                )
            ],
        )

        v_nl, v_count, r_count = self.verifier.verify_newsletter(
            newsletter, self.digest
        )
        self.assertEqual(v_count, 1)
        self.assertEqual(r_count, 0)
        self.assertEqual(len(v_nl.sections), 1)

    def test_b4_unsupported_number_rejected(self) -> None:
        """Kriterium B4: Satz mit erfundener Zahl wird abgewiesen."""
        bad_sentence = EditorialSentence(
            text="Nectaro erzielte ein Volumen von 9.999.999 Euro bei 29 Prozent Zinsen.",  # Erfundene Zahlen!
            fact_ids=["f-01"],
        )
        newsletter = EditorialNewsletterSchema(
            title="P2P Briefing",
            summary_lead="Übersicht",
            sections=[
                EditorialSection(
                    headline="Nectaro Wachstum",
                    category="zahlen_statistik",
                    platform_tags=["nectaro"],
                    sentences=[bad_sentence],
                )
            ],
        )

        v_nl, v_count, r_count = self.verifier.verify_newsletter(
            newsletter, self.digest
        )
        self.assertEqual(v_count, 0)
        self.assertEqual(r_count, 1)
        self.assertEqual(len(v_nl.sections), 0)

        # Prüfe Log
        log_content = self.log_file.read_text(encoding="utf-8")
        self.assertIn("nicht durch Fakten", log_content)

    def test_invalid_fact_id_rejected(self) -> None:
        """Satz mit nicht existierender fact_id wird abgewiesen."""
        sentence = EditorialSentence(
            text="Eine Aussage ohne gültige Referenz.",
            fact_ids=["f-non-existent"],
        )
        newsletter = EditorialNewsletterSchema(
            title="P2P Briefing",
            summary_lead="Übersicht",
            sections=[
                EditorialSection(
                    headline="Thema",
                    category="allgemein",
                    platform_tags=["nectaro"],
                    sentences=[sentence],
                )
            ],
        )
        v_nl, v_count, r_count = self.verifier.verify_newsletter(
            newsletter, self.digest
        )
        self.assertEqual(v_count, 0)
        self.assertEqual(r_count, 1)

    def test_paragraph_validation_accepted(self) -> None:
        """Prüft, dass Absätze (EditorialParagraph) korrekt validiert und synchronisiert werden."""
        sentence = EditorialSentence(
            text="Nectaro vergab im September 4.073.350 Euro Kredite bei einem Zinssatz von 13,40 Prozent.",
            fact_ids=["f-01"],
        )
        para = EditorialParagraph(platform="Nectaro", sentences=[sentence])
        newsletter = EditorialNewsletterSchema(
            title="P2P Briefing",
            summary_lead="Übersicht",
            sections=[
                EditorialSection(
                    headline="Monatszahlen",
                    category="zahlen_statistik",
                    platform_tags=["nectaro"],
                    paragraphs=[para],
                )
            ],
        )

        v_nl, v_count, r_count = self.verifier.verify_newsletter(
            newsletter, self.digest
        )
        self.assertEqual(v_count, 1)
        self.assertEqual(r_count, 0)
        self.assertEqual(len(v_nl.sections), 1)
        self.assertEqual(len(v_nl.sections[0].paragraphs), 1)
        self.assertEqual(len(v_nl.sections[0].sentences), 1)
        self.assertEqual(v_nl.sections[0].paragraphs[0].platform, "Nectaro")

    def test_paragraph_unsupported_number_filtered(self) -> None:
        """Prüft, dass ungültige Sätze innerhalb eines Absatzes abgelehnt, gültige beibehalten werden."""
        good_sentence = EditorialSentence(
            text="Nectaro vergab im September 4.073.350 Euro Kredite bei einem Zinssatz von 13,40 Prozent.",
            fact_ids=["f-01"],
        )
        bad_sentence = EditorialSentence(
            text="Nectaro meldete 88.888.888 Euro Fantasievolumen.",
            fact_ids=["f-01"],
        )
        para = EditorialParagraph(
            platform="Nectaro", sentences=[good_sentence, bad_sentence]
        )
        newsletter = EditorialNewsletterSchema(
            title="P2P Briefing",
            summary_lead="Übersicht",
            sections=[
                EditorialSection(
                    headline="Monatszahlen",
                    category="zahlen_statistik",
                    platform_tags=["nectaro"],
                    paragraphs=[para],
                )
            ],
        )

        v_nl, v_count, r_count = self.verifier.verify_newsletter(
            newsletter, self.digest
        )
        self.assertEqual(v_count, 1)
        self.assertEqual(r_count, 1)
        self.assertEqual(len(v_nl.sections[0].paragraphs), 1)
        self.assertEqual(len(v_nl.sections[0].paragraphs[0].sentences), 1)
        self.assertEqual(
            v_nl.sections[0].paragraphs[0].sentences[0].text, good_sentence.text
        )


class TestMarkdownRenderer(unittest.TestCase):
    def test_b5_deterministic_links_rendered(self) -> None:
        """Kriterium B5: Renderer baut Links aus den Quell-Items, nicht aus LLM-URLs."""
        fact = ExtractedFact(
            fact_id="f-01",
            statement="Esketit Gründer starten Goodeve.",
            evidence=[
                FactEvidence(item_id="item-goodeve", evidence_quote="Goodeve gestartet")
            ],
            verified=True,
        )
        digest = WeeklyDigestSchema(
            iso_week="2026-W40",
            clusters=[
                TopicCluster(
                    cluster_id="c-goodeve",
                    topic="regulierung_legal",
                    platforms=["esketit"],
                    title="Goodeve Plattform",
                    facts=[fact],
                    conflicts=["Rolle von Ieva Narbute unterschiedlich angegeben"],
                )
            ],
        )
        item = NewsItem(
            item_id="item-goodeve",
            provider="rethink-p2p",
            source_tier="secondary",
            url="https://rethink-p2p.de/news/goodeve/",
            title="Goodeve Lizenz Analyse",
            published_date="2026-09-28",
            first_seen_at="2026-09-28T10:00:00+00:00",
            last_seen_at="2026-09-28T10:00:00+00:00",
            item_content_hash="h1",
            page_snapshot_hash="s1",
            content_plain="Goodeve gestartet",
        )
        items_map = {"item-goodeve": item}

        sentence = EditorialSentence(
            text="Die Gründer von Esketit haben mit Goodeve eine zweite Plattform angekündigt.",
            fact_ids=["f-01"],
        )
        newsletter = EditorialNewsletterSchema(
            title="P2P Briefing KW 40",
            summary_lead="Die wichtigsten Entwicklungen der Woche.",
            sections=[
                EditorialSection(
                    headline="Goodeve Neuigkeit",
                    category="regulierung_legal",
                    platform_tags=["esketit"],
                    sentences=[sentence],
                )
            ],
        )

        renderer = MarkdownRenderer()
        md = renderer.render(
            newsletter=newsletter,
            digest=digest,
            items_map=items_map,
            run_id="run_test",
            iso_week="2026-W40",
            verified_facts_count=1,
            verified_sentences_count=1,
        )

        # Prüfe, ob deterministische Links und Badges korrekt gerendert wurden
        self.assertIn(
            "[Goodeve Lizenz Analyse](https://rethink-p2p.de/news/goodeve/)", md
        )
        self.assertIn("Sekundärquelle", md)
        self.assertIn("Abweichende Berichte zwischen Quellen", md)
        self.assertIn("Rolle von Ieva Narbute unterschiedlich angegeben", md)

        # Prüfe, dass Footer keine Header-Doppelungen enthält
        self.assertIn("### Revisions- & Prüfnachweis", md)
        self.assertNotIn("- **Woche:**", md)
        self.assertNotIn("- **Verifizierte Fakten:**", md)
        self.assertIn("- **Integrität:** Deterministisch gerendert", md)

    def test_clean_source_title_and_footer_deduplication(self) -> None:
        """Prüft, dass fett formatierte Quelltitel bereinigt werden und keine Doppelungen im Footer landen."""
        fact = ExtractedFact(
            fact_id="f-aiffin",
            statement="Lendermarket nimmt Aiffin auf.",
            evidence=[
                FactEvidence(item_id="i-aiffin", evidence_quote="Aiffin Autoleasing")
            ],
            verified=True,
        )
        digest = WeeklyDigestSchema(
            iso_week="2026-W41",
            clusters=[
                TopicCluster(
                    cluster_id="c-lendermarket",
                    topic="plattform_features",
                    platforms=["lendermarket"],
                    title="Lendermarket Neuer Anbahner",
                    facts=[fact],
                )
            ],
        )
        item = NewsItem(
            item_id="i-aiffin",
            provider="lendermarket",
            source_tier="primary",
            url="https://lendermarket.com/blog/aiffin/#why-aiffin-is-different",
            title="**Why Aiffin Is Different**",
            published_date="2026-10-08",
            first_seen_at="2026-10-08T10:00:00Z",
            last_seen_at="2026-10-08T10:00:00Z",
            item_content_hash="h-aiffin",
            page_snapshot_hash="s-aiffin",
            content_plain="Aiffin Autoleasing für Unternehmen.",
        )
        items_map = {"i-aiffin": item}

        sentence = EditorialSentence(
            text="Lendermarket hat mit Aiffin einen neuen Anbahner gelistet.",
            fact_ids=["f-aiffin"],
        )
        newsletter = EditorialNewsletterSchema(
            title="P2P Briefing KW 41",
            summary_lead="Übersicht KW 41.",
            sections=[
                EditorialSection(
                    headline="Lendermarket Neuigkeit",
                    category="plattform_features",
                    platform_tags=["lendermarket"],
                    sentences=[sentence],
                )
            ],
        )

        renderer = MarkdownRenderer()
        # Test helper directly
        self.assertEqual(
            renderer._clean_source_title("**Why Aiffin Is Different**"),
            "Why Aiffin Is Different",
        )
        self.assertEqual(
            renderer._clean_source_title("__Why Aiffin Is Different__"),
            "Why Aiffin Is Different",
        )
        self.assertEqual(
            renderer._clean_source_title("*Why Aiffin Is Different*"),
            "Why Aiffin Is Different",
        )

        md = renderer.render(
            newsletter=newsletter,
            digest=digest,
            items_map=items_map,
            run_id="run_2026-W41_test",
            iso_week="2026-W41",
            verified_facts_count=17,
            verified_sentences_count=18,
        )

        # Quell-Link darf nicht fett formatiert sein
        self.assertIn(
            "[Why Aiffin Is Different](https://lendermarket.com/blog/aiffin/#why-aiffin-is-different)",
            md,
        )
        self.assertNotIn("[**Why Aiffin Is Different**]", md)

        # Frontmatter enthält Metadaten, aber Footer wiederholt sie nicht
        self.assertIn("iso_week: '2026-W41'", md)
        self.assertIn("verified_facts_count: 17", md)
        self.assertIn("run_id: 'run_2026-W41_test'", md)

        self.assertIn("### Revisions- & Prüfnachweis", md)
        self.assertNotIn("- **Woche:** 2026-W41", md)
        self.assertNotIn("- **Verifizierte Fakten:** 17", md)
        self.assertIn(
            "- **Integrität:** Deterministisch gerendert aus schema-validierten Fakten.",
            md,
        )
        self.assertIn(
            "- *Hinweis: Dieser Newsletter dient ausschließlich Informationszwecken und stellt keine Anlageberatung dar.*",
            md,
        )

    def test_paragraph_separation_and_platform_bolding(self) -> None:
        """Prüft, dass mehrere Absätze mit Leerzeilen getrennt und Plattformnamen fett gerendert werden."""
        f1 = ExtractedFact(
            fact_id="f-indemo-01",
            statement="Indemo startet Cashback.",
            evidence=[
                FactEvidence(item_id="i-indemo", evidence_quote="Indemo Cashback")
            ],
            verified=True,
        )
        f2 = ExtractedFact(
            fact_id="f-lande-01",
            statement="LANDE zahlt Cashback.",
            evidence=[FactEvidence(item_id="i-lande", evidence_quote="LANDE Cashback")],
            verified=True,
        )
        digest = WeeklyDigestSchema(
            iso_week="2026-W40",
            clusters=[
                TopicCluster(
                    cluster_id="c-aktionen",
                    topic="zinsen_aktionen",
                    platforms=["indemo", "lande"],
                    title="Aktionen",
                    facts=[f1, f2],
                )
            ],
        )
        items_map = {
            "i-indemo": NewsItem(
                item_id="i-indemo",
                provider="indemo",
                source_tier="primary",
                url="https://indemo.eu",
                title="Indemo News",
                published_date="2026-10-01",
                first_seen_at="2026-10-01T00:00:00Z",
                last_seen_at="2026-10-01T00:00:00Z",
                item_content_hash="h1",
                page_snapshot_hash="s1",
                content_plain="Indemo Cashback",
            ),
            "i-lande": NewsItem(
                item_id="i-lande",
                provider="lande",
                source_tier="primary",
                url="https://lande.finance",
                title="LANDE News",
                published_date="2026-10-01",
                first_seen_at="2026-10-01T00:00:00Z",
                last_seen_at="2026-10-01T00:00:00Z",
                item_content_hash="h2",
                page_snapshot_hash="s2",
                content_plain="LANDE Cashback",
            ),
        }

        # Ein Absatz bereits mit ** gefettet, einer ungekettet -> beide müssen ** haben!
        p1 = EditorialParagraph(
            platform="Indemo",
            sentences=[
                EditorialSentence(
                    text="Zur Oktober-Aktion bei Indemo divergieren die Sätze.",
                    fact_ids=["f-indemo-01"],
                )
            ],
        )
        p2 = EditorialParagraph(
            platform="LANDE",
            sentences=[
                EditorialSentence(
                    text="**LANDE** zahlt vom 1. bis 18. Oktober Cashback.",
                    fact_ids=["f-lande-01"],
                )
            ],
        )

        newsletter = EditorialNewsletterSchema(
            title="P2P Briefing",
            summary_lead="Übersicht",
            sections=[
                EditorialSection(
                    headline="Aktionen & Zinsen",
                    category="zinsen_aktionen",
                    platform_tags=["indemo", "lande"],
                    paragraphs=[p1, p2],
                )
            ],
        )

        renderer = MarkdownRenderer()
        md = renderer.render(
            newsletter=newsletter,
            digest=digest,
            items_map=items_map,
            run_id="run_test",
            iso_week="2026-W40",
            verified_facts_count=2,
            verified_sentences_count=2,
        )

        # 1. Beide Plattformen müssen fett sein
        self.assertIn("**Indemo**", md)
        self.assertIn("**LANDE**", md)
        self.assertNotIn("****LANDE****", md)  # Keine Doppel-Fettung

        # 2. Absätze müssen getrennt vorliegen
        self.assertIn(
            "Zur Oktober-Aktion bei **Indemo** divergieren die Sätze.\n\n**LANDE** zahlt",
            md,
        )


class TestManifestAndLifecycle(unittest.TestCase):
    def test_b6_tamper_detection(self) -> None:
        """Kriterium B6: Nachträgliche Manipulation an Dateien wird sofort erkannt."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            base = Path(tmp_dir)
            digests_dir = base / "digests"
            news_dir = base / "newsletters"
            digests_dir.mkdir(parents=True)
            news_dir.mkdir(parents=True)

            digest_file = digests_dir / "digest-2026-W40.json"
            digest_file.write_text('{"iso_week": "2026-W40"}', encoding="utf-8")

            newsletter_file = news_dir / "newsletter-2026-W40.md"
            newsletter_file.write_text("# Originaler Inhalt", encoding="utf-8")

            mgr = ManifestManager(digests_dir=digests_dir)
            mf_path = mgr.create_manifest(
                iso_week="2026-W40",
                run_id="run_test_01",
                watermark_previous=None,
                watermark_current="2026-10-04T12:00:00+00:00",
                digest_path=digest_file,
                newsletter_path=newsletter_file,
                item_hashes={"item1": "hash1"},
                metrics={},
            )

            # 1. Unveränderte Prüfung -> Valid
            is_valid, errors = mgr.verify_integrity(mf_path)
            self.assertTrue(is_valid)
            self.assertEqual(len(errors), 0)

            # 2. Manipulation an der Newsletter-Datei
            newsletter_file.write_text(
                "# Manipulierter Inhalt (Hacker edit)", encoding="utf-8"
            )

            # 3. Zweite Prüfung -> MUSS FEHLSCHLAGEN!
            is_valid_after, errors_after = mgr.verify_integrity(mf_path)
            self.assertFalse(is_valid_after)
            self.assertEqual(len(errors_after), 1)
            self.assertIn("Newsletter manipuliert!", errors_after[0])

    def test_write_once_lifecycle_protection(self) -> None:
        """Schutz vor unbeabsichtigtem Überschreiben von Veröffentlichungen."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            gen = NewsletterGenerator(data_dir=tmp_dir)

            fact = ExtractedFact(
                fact_id="f-01",
                statement="Fakt 1",
                evidence=[FactEvidence(item_id="i1", evidence_quote="Q1")],
                verified=True,
            )
            digest = WeeklyDigestSchema(
                iso_week="2026-W40",
                clusters=[
                    TopicCluster(
                        cluster_id="c-01",
                        topic="allgemein",
                        platforms=["test"],
                        title="Titel",
                        facts=[fact],
                    )
                ],
            )

            # Mock Client
            from unittest.mock import MagicMock

            mock_client = MagicMock()
            mock_resp = MagicMock()
            mock_resp.text = json.dumps(
                {
                    "title": "Titel",
                    "summary_lead": "Lead",
                    "sections": [
                        {
                            "headline": "Head",
                            "category": "cat",
                            "platform_tags": ["test"],
                            "sentences": [
                                {"text": "Satz ohne Zahlen.", "fact_ids": ["f-01"]}
                            ],
                        }
                    ],
                }
            )
            mock_resp.model_version = "mock-model"
            mock_resp.usage_metadata = None
            mock_client.models.generate_content.return_value = mock_resp

            # 1. Publish ohne --approve schlägt fehl
            with self.assertRaises(ValueError):
                gen.generate(
                    digest,
                    is_publish=True,
                    is_approved=False,
                    custom_client=mock_client,
                )

            # 2. Publish mit --approve gelingt
            out_path, _ = gen.generate(
                digest, is_publish=True, is_approved=True, custom_client=mock_client
            )
            self.assertTrue(out_path.exists())

            # 3. Zweiter Publish ohne --force-revision wirft FileExistsError (Write-Once Schutz!)
            with self.assertRaises(FileExistsError):
                gen.generate(
                    digest,
                    is_publish=True,
                    is_approved=True,
                    force_revision=False,
                    custom_client=mock_client,
                )

            # 4. Zweiter Publish mit --force-revision legt .v2.md an
            v2_path, _ = gen.generate(
                digest,
                is_publish=True,
                is_approved=True,
                force_revision=True,
                custom_client=mock_client,
            )
            self.assertTrue(v2_path.name.endswith(".v2.md"))
            self.assertTrue(v2_path.exists())


if __name__ == "__main__":
    unittest.main()
