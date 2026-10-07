"""
Unit-Tests für den Multi-Provider P2P News Scraper (5 Anbieter).
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from p2p_news_scraper import (
    ArticleItem,
    ContentType,
    KeywordClassifier,
    MarkdownStorageManager,
    NectaroPlatformProvider,
    P2PAnlageProvider,
    P2PEmpireProvider,
    P2PGameProvider,
    PassivesEinkommenProvider,
    PlatformProvider,
    RethinkP2PProvider,
    compute_sha256_hash,
    decode_cloudflare_email,
    detect_provider_for_url,
    load_classifier_from_yaml,
    load_providers_from_yaml,
    normalize_text,
    parse_markdown_with_frontmatter,
    sanitize_cloudflare_artifacts,
    serialize_markdown_with_frontmatter,
)


class TestTextNormalizationAndHashing(unittest.TestCase):
    def test_unicode_nfc_normalization(self) -> None:
        decomposed = "e\u0301"
        precomposed = "\u00e9"
        self.assertNotEqual(decomposed, precomposed)
        self.assertEqual(normalize_text(decomposed), normalize_text(precomposed))
        self.assertEqual(
            compute_sha256_hash(decomposed), compute_sha256_hash(precomposed)
        )

    def test_whitespace_collapsing(self) -> None:
        raw_text_1 = "  Titel \t\n mit  vielen   Leerzeichen. \n\nAbsatz 2.  "
        raw_text_2 = "Titel mit vielen Leerzeichen. Absatz 2."
        self.assertEqual(normalize_text(raw_text_1), raw_text_2)
        self.assertEqual(
            compute_sha256_hash(raw_text_1), compute_sha256_hash(raw_text_2)
        )

    def test_dynamic_timestamp_normalization(self) -> None:
        text_at_1212 = "# Performance statistics\nLast update at 03-10-2026 12:12 UTC\nTotal: €3 743 287"
        text_at_1345 = "# Performance statistics\nLast update at 03-10-2026 13:45 UTC\nTotal: €3 743 287"
        text_changed = "# Performance statistics\nLast update at 03-10-2026 13:45 UTC\nTotal: €3 800 000"

        # Gleiche Daten, aber unterschiedliche Zeitstempel dürfen keinen Hash-Unterschied erzeugen
        self.assertEqual(
            compute_sha256_hash(text_at_1212), compute_sha256_hash(text_at_1345)
        )
        # Veränderte Daten müssen zu einem geänderten Hash führen
        self.assertNotEqual(
            compute_sha256_hash(text_at_1212), compute_sha256_hash(text_changed)
        )


class TestCloudflareDeobfuscation(unittest.TestCase):
    def test_decode_cloudflare_email(self) -> None:
        cf_hex = "50232520203f222410313622313e37317e333f3d"
        self.assertEqual(decode_cloudflare_email(cf_hex), "support@afranga.com")

    def test_sanitize_cloudflare_artifacts(self) -> None:
        html_sample = (
            '<p>Kontakt: <a class="__cf_email__" href="/cdn-cgi/l/email-protection#50232520203f222410313622313e37317e333f3d" '
            'data-cfemail="50232520203f222410313622313e37317e333f3d">[email&#160;protected]</a></p>'
        )
        cleaned = sanitize_cloudflare_artifacts(html_sample)
        self.assertIn("support@afranga.com", cleaned)
        self.assertNotIn("data-cfemail", cleaned)


class TestProviderImplementations(unittest.TestCase):
    def setUp(self) -> None:
        self.p2p_empire = P2PEmpireProvider()
        self.p2p_game = P2PGameProvider()
        self.rethink_p2p = RethinkP2PProvider()
        self.passives_einkommen = PassivesEinkommenProvider()
        self.p2p_anlage = P2PAnlageProvider()

    def test_detect_all_providers(self) -> None:
        self.assertEqual(
            detect_provider_for_url("https://p2pempire.com/de/nachrichten").name,
            "p2p-empire",
        )
        self.assertEqual(
            detect_provider_for_url(
                "https://p2p-game.com/p2p-kredite-plattform-news"
            ).name,
            "p2p-game",
        )
        self.assertEqual(
            detect_provider_for_url("https://rethink-p2p.de/news/").name, "rethink-p2p"
        )
        self.assertEqual(
            detect_provider_for_url(
                "https://passives-einkommen-mit-p2p.de/p2p-kredite-news/"
            ).name,
            "passives-einkommen",
        )
        self.assertEqual(
            detect_provider_for_url("https://p2p-anlage.de/").name, "p2p-anlage"
        )

    def test_p2p_empire_provider(self) -> None:
        url_review = "https://p2pempire.com/de/erfahrungen/nectaro"
        self.assertEqual(
            self.p2p_empire.classify_content_type(url_review), ContentType.ERFAHRUNGEN
        )
        self.assertEqual(self.p2p_empire.extract_platform_name(url_review), "nectaro")

    def test_p2p_empire_extract_content_h2(self) -> None:
        sample_html = """
        <html>
        <head><title>P2P News | Aktuelle Neuigkeiten</title></head>
        <body>
        <div class="news-box-wrapper">
            <div class="news-date"><span>02. Oktober 2026</span></div>
            <div class="news-title">
                <h2>Nectaro vergibt im September 4,07 Millionen Euro über 218 Kredite</h2>
                <p>Nectaro vergab im September 2026 Kredite im Wert von 4.073.350 € über 218 Kredite.</p>
            </div>
            <div class="news-second-row">
                <div class="review-link"><a href="/de/erfahrungen/nectaro">Zu Nectaro</a></div>
            </div>
        </div>
        </body>
        </html>
        """
        from p2p_news_scraper import ContentExtractor

        res = self.p2p_empire.extract_content(
            sample_html, "https://p2pempire.com/de/nachrichten", ContentExtractor()
        )
        self.assertIsNotNone(res)
        assert res is not None
        content, title, date, author = res
        self.assertIn(
            "## Nectaro vergibt im September 4,07 Millionen Euro über 218 Kredite",
            content,
        )
        self.assertIn("*02. Oktober 2026*", content)
        self.assertIn(
            "[Zu Nectaro](https://p2pempire.com/de/erfahrungen/nectaro)", content
        )

    def test_p2p_game_provider(self) -> None:
        url_review = "https://p2p-game.com/nectaro-erfahrungen"
        self.assertEqual(
            self.p2p_game.classify_content_type(url_review), ContentType.ERFAHRUNGEN
        )
        self.assertEqual(self.p2p_game.extract_platform_name(url_review), "nectaro")

    def test_rethink_p2p_provider(self) -> None:
        url_news = "https://rethink-p2p.de/news/bondora-update/"
        self.assertEqual(
            self.rethink_p2p.classify_content_type(url_news), ContentType.NEWS
        )

        url_review = "https://rethink-p2p.de/loanch-erfahrungen/"
        self.assertEqual(
            self.rethink_p2p.classify_content_type(url_review), ContentType.ERFAHRUNGEN
        )
        self.assertEqual(self.rethink_p2p.extract_platform_name(url_review), "loanch")

    def test_rethink_p2p_extract_content_full_text(self) -> None:
        sample_html = """
        <html>
        <head><title>P2P Kredite News | re:think P2P</title></head>
        <body>
        <div data-nf='{"posts":[{"cat":"","date":"28. September 2026","title":"Korrektur: Neue Lizenz gilt f\u00fcr Goodeve, nicht f\u00fcr Esketit","content":"<p>Letzte Woche hatte ich dar\u00fcber berichtet... Stattdessen entsteht offenbar eine zweite, parallele Plattform derselben Gesellschafter.</p><p>Wie einem Bericht zu entnehmen ist, steht hinter der Lizenz eine neue P2P Plattform namens Goodeve.</p>","platform":"https://rethink-p2p.de/esketit-erfahrungen/","platform_name":"Esketit"}]}'>
            <article class="nf-card">
                <h2 class="nf-card-title"><a class="nf-card-permalink" href="https://rethink-p2p.de/news/korrektur-neue-lizenz-gilt-fuer-goodeve-nicht-fuer-esketit/">Korrektur...</a></h2>
                <div class="nf-excerpt"><p>Letzte Woche hatte ich darüber berichtet, dass die lettische Zentralbank der SIA IBC Invest eine Lizenz als Wertpapierfirma erteilt hat. Meine Einordnung, dass Esketit damit auf ein reguliertes Fundament gestellt …</p></div>
            </article>
        </div>
        </body>
        </html>
        """
        from p2p_news_scraper import ContentExtractor

        res = self.rethink_p2p.extract_content(
            sample_html, "https://rethink-p2p.de/news/", ContentExtractor()
        )
        self.assertIsNotNone(res)
        assert res is not None
        content, title, date, author = res
        self.assertIn(
            "## Korrektur: Neue Lizenz gilt für Goodeve, nicht für Esketit", content
        )
        self.assertIn(
            "Stattdessen entsteht offenbar eine zweite, parallele Plattform derselben Gesellschafter.",
            content,
        )
        self.assertIn("Goodeve", content)
        self.assertIn(
            "[Esketit Erfahrungsbericht](https://rethink-p2p.de/esketit-erfahrungen/)",
            content,
        )
        self.assertEqual(date, "28. September 2026")
        self.assertEqual(author, "Denny Neidhardt")

    def test_passives_einkommen_provider(self) -> None:
        url_news = "https://passives-einkommen-mit-p2p.de/p2p-kredite-39-26-news/"
        self.assertEqual(
            self.passives_einkommen.classify_content_type(url_news), ContentType.NEWS
        )

        url_review = "https://passives-einkommen-mit-p2p.de/nectaro-erfahrungen/"
        self.assertEqual(
            self.passives_einkommen.classify_content_type(url_review),
            ContentType.ERFAHRUNGEN,
        )
        self.assertEqual(
            self.passives_einkommen.extract_platform_name(url_review), "nectaro"
        )

    def test_p2p_anlage_provider(self) -> None:
        url_news = "https://p2p-anlage.de/2026/09/zahlen-bericht/"
        self.assertEqual(
            self.p2p_anlage.classify_content_type(url_news), ContentType.NEWS
        )

        url_review = "https://p2p-anlage.de/2026/09/mypeak-erfahrungen/"
        self.assertEqual(
            self.p2p_anlage.classify_content_type(url_review), ContentType.ERFAHRUNGEN
        )
        self.assertEqual(self.p2p_anlage.extract_platform_name(url_review), "mypeak")


class TestMarkdownSerialization(unittest.TestCase):
    def test_serialize_and_parse_roundtrip(self) -> None:
        frontmatter = {
            "source": "rethink-p2p",
            "content_type": "erfahrungen",
            "platform": "loanch",
            "url": "https://rethink-p2p.de/loanch-erfahrungen/",
            "title": "Loanch Erfahrungen",
            "scan_count": 1,
            "status": "neu",
        }
        body = "## Loanch Test\nInhalt."
        serialized = serialize_markdown_with_frontmatter(frontmatter, body)
        parsed_fm, parsed_body = parse_markdown_with_frontmatter(serialized)
        self.assertEqual(parsed_fm["source"], "rethink-p2p")
        self.assertEqual(parsed_fm["platform"], "loanch")
        self.assertEqual(parsed_body, body)


class TestMultiProviderStorageManager(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.output_dir = Path(self.temp_dir.name)
        self.storage = MarkdownStorageManager(output_dir=self.output_dir)
        self.rethink = RethinkP2PProvider()
        self.lars = PassivesEinkommenProvider()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_multi_provider_paths(self) -> None:
        # Rethink News
        news_rethink = ArticleItem(
            url="https://rethink-p2p.de/news/creditstar-news/",
            title="Creditstar News",
            published_date="2026-07-03",
            author="Denny",
            content="Rethink Content",
            content_hash=compute_sha256_hash("Rethink Content"),
            scanned_at="2026-10-01T10:00:00Z",
        )
        res_rethink = self.storage.record_scan(news_rethink, self.rethink)
        self.assertEqual(
            res_rethink.file_path,
            self.output_dir / "news" / "rethink-p2p" / "creditstar-news.md",
        )
        self.assertTrue(res_rethink.file_path.exists())

        # Lars Wrobbel Review
        review_lars = ArticleItem(
            url="https://passives-einkommen-mit-p2p.de/nectaro-erfahrungen/",
            title="Nectaro Lars",
            published_date="2026-09-30",
            author="Lars",
            content="Lars Content",
            content_hash=compute_sha256_hash("Lars Content"),
            scanned_at="2026-10-01T10:00:00Z",
        )
        res_lars = self.storage.record_scan(review_lars, self.lars)
        self.assertEqual(
            res_lars.file_path,
            self.output_dir / "erfahrungen" / "passives-einkommen" / "nectaro.md",
        )
        self.assertTrue(res_lars.file_path.exists())

    def test_platform_storage_and_frontmatter(self) -> None:
        nectaro = NectaroPlatformProvider()

        # Statistik-Seite
        stats_item = ArticleItem(
            url="https://nectaro.eu/statistics/",
            title="Performance statistics",
            published_date=None,
            author=None,
            content="# Performance statistics\nLast update at 03-10-2026 12:12 UTC\nTotal: €3 743 287",
            content_hash=compute_sha256_hash("stats"),
            scanned_at="2026-10-03T12:12:00Z",
        )
        res_stats = self.storage.record_scan(stats_item, nectaro)
        expected_stats_path = (
            self.output_dir / "platforms" / "nectaro" / "statistics.md"
        )
        self.assertEqual(res_stats.file_path, expected_stats_path)
        self.assertTrue(expected_stats_path.exists())

        # Frontmatter prüfen
        fm, _ = parse_markdown_with_frontmatter(
            expected_stats_path.read_text(encoding="utf-8")
        )
        self.assertEqual(fm["source"], "nectaro")
        self.assertEqual(fm["content_type"], "platform")
        self.assertEqual(fm["category"], "statistics")
        self.assertEqual(fm["platform"], "nectaro")

        # Blog-Post
        blog_item = ArticleItem(
            url="https://nectaro.eu/blog/summer-splash-campaign/",
            title="Summer Splash",
            published_date="2026-06-01",
            author="Nectaro Team",
            content="Summer Splash cashback!",
            content_hash=compute_sha256_hash("blog content"),
            scanned_at="2026-10-03T12:12:00Z",
        )
        res_blog = self.storage.record_scan(blog_item, nectaro)
        expected_blog_path = (
            self.output_dir
            / "platforms"
            / "nectaro"
            / "blog"
            / "summer-splash-campaign.md"
        )
        self.assertEqual(res_blog.file_path, expected_blog_path)
        self.assertTrue(expected_blog_path.exists())

        fm_blog, _ = parse_markdown_with_frontmatter(
            expected_blog_path.read_text(encoding="utf-8")
        )
        self.assertEqual(fm_blog["category"], "blog")


class TestPlatformProvider(unittest.TestCase):
    def setUp(self) -> None:
        self.nectaro = NectaroPlatformProvider()

    def test_detect_nectaro(self) -> None:
        provider = detect_provider_for_url("https://nectaro.eu")
        self.assertEqual(provider.name, "nectaro")
        self.assertTrue(provider.is_platform)

    def test_nectaro_categories(self) -> None:
        self.assertEqual(
            self.nectaro.classify_content_type("https://nectaro.eu"),
            ContentType.PLATFORM,
        )
        self.assertEqual(
            self.nectaro.classify_category("https://nectaro.eu"), "overview"
        )
        self.assertEqual(
            self.nectaro.classify_category("https://nectaro.eu/statistics/"),
            "statistics",
        )
        self.assertEqual(
            self.nectaro.classify_category("https://nectaro.eu/documents/"), "documents"
        )
        self.assertEqual(
            self.nectaro.classify_category("https://nectaro.eu/lending-companies/"),
            "lending-companies",
        )
        self.assertEqual(
            self.nectaro.classify_category("https://nectaro.eu/blog/"), "blog"
        )
        self.assertEqual(
            self.nectaro.classify_category("https://nectaro.eu/blog/post-1/"), "blog"
        )

    def test_nectaro_target_paths(self) -> None:
        base = Path("/dummy/data")

        def item_for(u: str) -> ArticleItem:
            return ArticleItem(u, "T", None, None, "C", "H", "S")

        self.assertEqual(
            self.nectaro.get_target_path(base, item_for("https://nectaro.eu")),
            base / "platforms" / "nectaro" / "main.md",
        )
        self.assertEqual(
            self.nectaro.get_target_path(
                base, item_for("https://nectaro.eu/statistics/")
            ),
            base / "platforms" / "nectaro" / "statistics.md",
        )
        self.assertEqual(
            self.nectaro.get_target_path(
                base, item_for("https://nectaro.eu/documents/")
            ),
            base / "platforms" / "nectaro" / "documents.md",
        )
        self.assertEqual(
            self.nectaro.get_target_path(
                base, item_for("https://nectaro.eu/lending-companies/")
            ),
            base / "platforms" / "nectaro" / "lending-companies.md",
        )
        self.assertEqual(
            self.nectaro.get_target_path(base, item_for("https://nectaro.eu/blog/")),
            base / "platforms" / "nectaro" / "blog" / "index.md",
        )
        self.assertEqual(
            self.nectaro.get_target_path(
                base, item_for("https://nectaro.eu/blog/introducing-autopilot/")
            ),
            base / "platforms" / "nectaro" / "blog" / "introducing-autopilot.md",
        )

    def test_nectaro_extract_links(self) -> None:
        mock_html = """
        <html>
            <body>
                <a href="/statistics/">Stats</a>
                <a href="/blog/summer-splash-campaign/">Summer Splash</a>
                <a href="/blog/autopilot/">Autopilot</a>
                <a href="https://other.com/foo">External</a>
            </body>
        </html>
        """
        links = self.nectaro.extract_links(mock_html)
        self.assertIn("https://nectaro.eu/statistics/", links)
        self.assertIn("https://nectaro.eu/documents/", links)
        self.assertIn("https://nectaro.eu/lending-companies/", links)
        self.assertIn("https://nectaro.eu/blog/", links)
        self.assertIn("https://nectaro.eu/blog/summer-splash-campaign/", links)
        self.assertIn("https://nectaro.eu/blog/autopilot/", links)

    def test_add_new_platform_via_yaml_without_code(self) -> None:
        """Verifiziert, dass beliebige Plattformen rein über YAML ohne Python-Code geladen werden."""
        yaml_content = """
platforms:
  mintos:
    base_url: "https://www.mintos.com"
    subpages:
      - "/en/statistics"
      - "/en/about-us"
    blog_path: "/en/blog/"
  peerberry:
    base_url: "https://peerberry.com"
    subpages:
      - "/statistics/"
    blog_path: "/news/"
"""
        with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            temp_yaml = Path(f.name)

        try:
            providers = load_providers_from_yaml(temp_yaml)
            self.assertIn("mintos", providers)
            self.assertIn("peerberry", providers)

            mintos = providers["mintos"]
            self.assertIsInstance(mintos, PlatformProvider)
            self.assertEqual(mintos.name, "mintos")
            self.assertEqual(mintos.base_url, "https://www.mintos.com")
            self.assertTrue(mintos.is_platform)

            # Prüfe Link-Generierung
            mintos_links = mintos.extract_links("<html></html>")
            self.assertIn("https://www.mintos.com/en/statistics", mintos_links)
            self.assertIn("https://www.mintos.com/en/about-us", mintos_links)
            self.assertIn("https://www.mintos.com/en/blog/", mintos_links)

            # Prüfe Zielpfad
            dummy_item = ArticleItem(
                url="https://www.mintos.com/en/statistics",
                title="Mintos Stats",
                published_date=None,
                author=None,
                content="Stats",
                content_hash="h1",
                scanned_at="2026-10-03",
            )
            base_dir = Path("/tmp/data")
            self.assertEqual(
                mintos.get_target_path(base_dir, dummy_item),
                base_dir / "platforms" / "mintos" / "en" / "statistics.md",
            )
        finally:
            temp_yaml.unlink(missing_ok=True)

    def test_detect_unknown_platform_url_dynamically(self) -> None:
        """Verifiziert, dass eine unbekannte URL on-the-fly als PlatformProvider erkannt wird."""
        url = "https://www.random-p2p-lending.com/invest"
        provider = detect_provider_for_url(url)
        self.assertIsInstance(provider, PlatformProvider)
        self.assertEqual(provider.name, "random-p2p-lending")
        self.assertEqual(provider.base_url, "https://www.random-p2p-lending.com")
        self.assertTrue(provider.is_platform)


class TestKeywordClassifier(unittest.TestCase):
    def setUp(self) -> None:
        self.classifier = KeywordClassifier()

    def test_platform_detection(self) -> None:
        text = "Mintos und Nectaro verzeichnen starke Zuwächse, während Peerberry stabil bleibt."
        res = self.classifier.classify(title="P2P Update", content=text)
        self.assertIn("mintos", res.platforms)
        self.assertIn("nectaro", res.platforms)
        self.assertIn("peerberry", res.platforms)
        self.assertNotIn("bondora", res.platforms)

    def test_topic_detection(self) -> None:
        # Zinsen & Aktionen
        res_zinsen = self.classifier.classify(
            title="Neue Cashback Aktion",
            content="Die Plattform bietet 2% Bonus und höhere Zinsen.",
        )
        self.assertIn("zinsen_aktionen", res_zinsen.topics)

        # Risiko & Ausfälle
        res_risiko = self.classifier.classify(
            title="Insolvenz eines Kreditanbahners",
            content="Es droht ein Zahlungsausfall und Totalverlust für Anleger.",
        )
        self.assertIn("risiko_ausfaelle", res_risiko.topics)

        # Kreditanbahner
        res_lender = self.classifier.classify(
            title="Neuer Loan Originator an Bord",
            content="Der Kreditanbahner aus Spanien vergibt Konsumkredite mit Rückkaufgarantie.",
        )
        self.assertIn("kreditanbahner", res_lender.topics)

        # Regulierung
        res_legal = self.classifier.classify(
            title="BaFin Lizenz erteilt",
            content="Die Plattform agiert nun als lizenzierter Broker unter Aufsicht.",
        )
        self.assertIn("regulierung_legal", res_legal.topics)

    def test_sentiment_and_severity(self) -> None:
        # Positiv & Low Severity
        res_pos = self.classifier.classify(
            title="Rekordmonat und starkes Wachstum",
            content="Erfolgreicher Launch des neuen Features und hervorragende Rendite.",
        )
        self.assertEqual(res_pos.sentiment, "positiv")
        self.assertEqual(res_pos.severity, "low")

        # Negativ & High Severity (Insolvenz / Betrug)
        res_crit = self.classifier.classify(
            title="Verdacht auf Scam und Betrug",
            content="Die Plattform meldet Insolvenz an und Konten wurden gesperrt.",
        )
        self.assertEqual(res_crit.sentiment, "negativ")
        self.assertEqual(res_crit.severity, "high")

        # Negativ & Medium Severity (Verspätung)
        res_med = self.classifier.classify(
            title="Zahlungsverzug bei Rückzahlungen",
            content="Mehrere Kredite befinden sich in Verzug. Kritik von Investoren.",
        )
        self.assertEqual(res_med.sentiment, "negativ")
        self.assertEqual(res_med.severity, "medium")

    def test_storage_writes_classification_to_frontmatter(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            storage = MarkdownStorageManager(
                output_dir=tmp_dir, classifier=self.classifier
            )
            prov = P2PEmpireProvider()
            item = ArticleItem(
                url="https://p2pempire.com/de/news/mintos-cashback-deal",
                title="Mintos startet 3% Cashback Aktion",
                published_date="2026-10-01",
                author="Lars",
                content="Mintos bietet aktuell einen attraktiven Bonus und Cashback auf Konsumkredite.",
                content_hash=compute_sha256_hash("mintos cashback"),
                scanned_at="2026-10-03T12:00:00Z",
            )
            res = storage.record_scan(item, prov)
            self.assertIsNotNone(res.classification)
            assert res.classification is not None
            self.assertIn("mintos", res.classification.platforms)
            self.assertIn("zinsen_aktionen", res.classification.topics)

            # Prüfe, dass classification im YAML Frontmatter der Markdown-Datei gespeichert ist
            fm, _ = parse_markdown_with_frontmatter(
                res.file_path.read_text(encoding="utf-8")
            )
            self.assertIn("classification", fm)
            self.assertEqual(fm["classification"]["sentiment"], "positiv")
            self.assertIn("mintos", fm["classification"]["platforms"])
            self.assertIn("zinsen_aktionen", fm["classification"]["topics"])

    def test_configurable_dictionary_extension_via_yaml(self) -> None:
        """Verifiziert, dass neue Themen, Plattformen, Sentiment und Severity flexibel per YAML geladen werden."""
        custom_yaml = """
platforms:
  custom-platform-a:
    base_url: "https://custom-a.com"

classification:
  platforms:
    - superpeer
  topics:
    neue_kategorie:
      - ki-kredite
      - algorithmus
    zinsen_aktionen:
      - mega-bonus
  sentiment:
    positive:
      - überflieger
  severity:
    high:
      - super-gau
"""
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", suffix=".yaml", delete=False
        ) as f:
            f.write(custom_yaml)
            temp_path = Path(f.name)

        try:
            custom_classifier = load_classifier_from_yaml(
                temp_path, merge_defaults=True
            )

            # Prüfe Plattform-Erweiterung (custom-platform-a aus platforms + superpeer aus classification.platforms + defaults)
            self.assertIn("custom-platform-a", custom_classifier.platforms)
            self.assertIn("superpeer", custom_classifier.platforms)
            self.assertIn("mintos", custom_classifier.platforms)

            # Prüfe neue Kategorie
            res_custom = custom_classifier.classify(
                title="Einsatz von KI",
                content="Wir vergeben nun ki-kredite vollautomatisch über einen Algorithmus.",
            )
            self.assertIn("neue_kategorie", res_custom.topics)

            # Prüfe erweitertes bestehendes Topic (mega-bonus)
            res_bonus = custom_classifier.classify(
                title="Aktion",
                content="Investoren erhalten einen exklusiven mega-bonus.",
            )
            self.assertIn("zinsen_aktionen", res_bonus.topics)

            # Prüfe erweitertes Sentiment und Severity
            res_sentiment = custom_classifier.classify(
                title="Plattform ist ein Überflieger",
                content="Alles läuft super.",
            )
            self.assertEqual(res_sentiment.sentiment, "positiv")

            res_sev = custom_classifier.classify(
                title="Warnung",
                content="Das Unternehmen erlebt einen absoluten super-gau.",
            )
            self.assertEqual(res_sev.severity, "high")
        finally:
            temp_path.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
