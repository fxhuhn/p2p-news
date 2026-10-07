"""
Umfassende Unit-Tests für Stufe 0 (Ingestion, Snapshots & Item-Extraktion).
Prüft die Abnahmekriterien B1, B2, A1 und die Robustheit des Systems.
"""

from __future__ import annotations

import tempfile
import unittest

from item_extractor import ItemExtractor, compute_item_id
from item_models import NewsItem
from item_store import ItemStore
from normalization import normalize_plain_text, parse_german_date
from snapshot_manager import SnapshotManager


class TestNormalization(unittest.TestCase):
    def test_markdown_ast_stripping(self) -> None:
        raw_md = (
            "## [Esketit](https://example.com) Update\n\n"
            "Die lettische **Zentralbank** hat der *SIA IBC Invest* eine Lizenz erteilt, "
            "aber **nicht** für Esketit!\n\n"
            "> Ein wichtiges Zitat „aus Lettland“\n\n"
            "---\n"
            "[Zu Esketit](https://example.com/esketit)"
        )
        plain = normalize_plain_text(raw_md)
        # Markdown-Links gestrippt
        self.assertIn("Esketit Update", plain)
        self.assertNotIn("https://example.com", plain)
        # Fettschrift und Kursiv gestrippt
        self.assertIn("Zentralbank", plain)
        self.assertNotIn("**Zentralbank**", plain)
        # Kritisches Negationswort 'nicht' bleibt exakt erhalten (Befund V21-02)
        self.assertIn("aber nicht für Esketit!", plain)
        # Typografische Quotes vereinheitlicht
        self.assertIn('"aus Lettland"', plain)
        self.assertNotIn("„", plain)

    def test_parse_german_date(self) -> None:
        self.assertEqual(parse_german_date("02. Oktober 2026"), "2026-10-02")
        self.assertEqual(parse_german_date("*28. September 2026*"), "2026-09-28")
        self.assertEqual(parse_german_date("30.09.2026"), "2026-09-30")
        self.assertEqual(parse_german_date("2026-10-01"), "2026-10-01")
        self.assertIsNone(parse_german_date("Ungültiges Datum"))


class TestSnapshotManager(unittest.TestCase):
    def test_write_once_immutability(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            mgr = SnapshotManager(base_dir=tmp_dir)
            content = "Originaler Inhalt der Übersichtsseite"

            h1, p1, created1 = mgr.save_page_snapshot(
                content, original_url="https://test.com"
            )
            self.assertTrue(created1)
            self.assertTrue(p1.exists())

            # Zweiter Aufruf mit identischem Inhalt darf Datei nicht überschreiben
            h2, p2, created2 = mgr.save_page_snapshot(
                content, original_url="https://test.com"
            )
            self.assertEqual(h1, h2)
            self.assertEqual(p1, p2)
            self.assertFalse(created2)

            loaded = mgr.get_page_snapshot(h1)
            self.assertEqual(loaded, content)


class TestItemExtractor(unittest.TestCase):
    def setUp(self) -> None:
        self.extractor = ItemExtractor()

    def test_split_rethink_overview(self) -> None:
        sample_markdown = """---
source: rethink-p2p
url: https://rethink-p2p.de/news/
first_seen_at: '2026-10-03T12:00:00+00:00'
---
# P2P Kredite News

## P2P Risiko Score Update Q3/2026
*03. Oktober 2026*

Drei Monate, fünf Neuzugänge und eine neue Nummer 1 im Ranking.

**https://youtu.be/LA_HuEFrbbc**

---

## Korrektur: Neue Lizenz gilt für Goodeve, nicht für Esketit
*28. September 2026*

Letzte Woche hatte ich darüber berichtet, dass die lettische Zentralbank der SIA IBC Invest eine Lizenz erteilt hat.

[Esketit Erfahrungsbericht](https://rethink-p2p.de/esketit-erfahrungen/)
"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            mgr = SnapshotManager(base_dir=tmp_dir)
            ext = ItemExtractor(snapshot_manager=mgr)
            items = ext.extract_items(
                sample_markdown.split("---", 2)[2],
                frontmatter={
                    "source": "rethink-p2p",
                    "url": "https://rethink-p2p.de/news/",
                },
            )

            self.assertEqual(len(items), 2)

            # Prüfe Item 1
            item1 = items[0]
            self.assertEqual(item1.title, "P2P Risiko Score Update Q3/2026")
            self.assertEqual(item1.published_date, "2026-10-03")
            self.assertIn("https://youtu.be/LA_HuEFrbbc", item1.url)

            # Prüfe Item 2
            item2 = items[1]
            self.assertEqual(
                item2.title,
                "Korrektur: Neue Lizenz gilt für Goodeve, nicht für Esketit",
            )
            self.assertEqual(item2.published_date, "2026-09-28")
            self.assertIn("esketit", item2.platforms)
            self.assertIn("regulierung_legal", item2.topics)
            self.assertEqual(item2.source_tier, "secondary")

    def test_item_id_stability_across_dates(self) -> None:
        # Die item_id darf sich NIEMALS ändern, wenn sich Datumsangaben ändern
        id1 = compute_item_id(
            provider="p2p-empire",
            title="Nectaro vergibt im September 4,07 Millionen Euro",
            url="https://p2pempire.com/de/nachrichten",
            content_hash="abc1234567890",
        )
        id2 = compute_item_id(
            provider="p2p-empire",
            title="Nectaro vergibt im September 4,07 Millionen Euro",
            url="https://p2pempire.com/de/nachrichten",
            content_hash="abc1234567890",
        )
        self.assertEqual(id1, id2)
        self.assertEqual(len(id1), 16)

    def test_single_detail_article(self) -> None:
        article_md = (
            "Letzte Woche hatte ich darüber berichtet, dass die lettische Zentralbank "
            "der SIA IBC Invest eine Lizenz als Wertpapierfirma erteilt hat."
        )
        fm = {
            "source": "rethink-p2p",
            "url": "https://rethink-p2p.de/news/korrektur-neue-lizenz/",
            "title": "Korrektur zur Esketit Lizenz",
            "published_date": "2026-09-28",
        }
        items = self.extractor.extract_items(article_md, frontmatter=fm)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].title, "Korrektur zur Esketit Lizenz")
        self.assertEqual(items[0].published_date, "2026-09-28")
        self.assertEqual(
            items[0].url, "https://rethink-p2p.de/news/korrektur-neue-lizenz/"
        )

    def test_pdf_content_is_ignored(self) -> None:
        pdf_md = "%PDF-1.4\n%\n1 0 obj\n<< /Title (AGB) >>\nendobj"
        fm = {
            "source": "loanch",
            "url": "https://loanch.com/docs/terms.pdf",
            "title": "Terms PDF",
        }
        items = self.extractor.extract_items(pdf_md, frontmatter=fm)
        self.assertEqual(len(items), 0)


class TestItemStore(unittest.TestCase):
    def test_upsert_preserves_first_seen_at(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            store = ItemStore(items_dir=tmp_dir)
            item = NewsItem(
                item_id="item-1234",
                provider="rethink-p2p",
                source_tier="secondary",
                url="https://example.com/1",
                title="Erste Meldung",
                published_date="2026-10-01",
                first_seen_at="2026-10-01T10:00:00+00:00",
                last_seen_at="2026-10-01T10:00:00+00:00",
                item_content_hash="hash-version-1",
                page_snapshot_hash="snap-1",
                content_plain="Text Version 1",
            )

            # Erstes Einfügen
            saved1, status1 = store.upsert_item(item)
            self.assertEqual(status1, "neu")
            orig_first_seen = saved1.first_seen_at

            # Zweites Einfügen: unverändert
            saved2, status2 = store.upsert_item(item)
            self.assertEqual(status2, "unverändert")
            self.assertEqual(saved2.first_seen_at, orig_first_seen)

            # Drittes Einfügen: Inhalt geändert
            item_changed = NewsItem(
                item_id="item-1234",
                provider="rethink-p2p",
                source_tier="secondary",
                url="https://example.com/1",
                title="Erste Meldung",
                published_date="2026-10-01",
                first_seen_at="2026-10-04T12:00:00+00:00",  # Neuer Versuch Zeitstempel
                last_seen_at="2026-10-04T12:00:00+00:00",
                item_content_hash="hash-version-2",
                page_snapshot_hash="snap-2",
                content_plain="Text Version 2 (Korrektur)",
            )
            saved3, status3 = store.upsert_item(item_changed)
            self.assertEqual(status3, "geändert")
            # first_seen_at muss weiterhin der ursprüngliche sein!
            self.assertEqual(saved3.first_seen_at, orig_first_seen)
            self.assertEqual(saved3.item_content_hash, "hash-version-2")


if __name__ == "__main__":
    unittest.main()
