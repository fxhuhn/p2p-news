"""
Unit Tests für TelegramPublisher (tests/test_telegram_publisher.py)

Prüft:
- Deaktivierter Modus (TELEGRAM_NOTIFY_ENABLED=false)
- Fehlende Konfiguration (Token / Chat-ID)
- Erfolgreicher Versand via HTTP-POST (gemockt)
- Fehlerbehandlung bei HTTP-Fehlern
- Formatierung des Rankings (Top-5, Absteiger, Stopps, keine Emojis/Linien)
- Formatierung des Newsletters (Intro + Kategorien, keine Emojis/Linien, Entfall Prüfzeile)
- 100 % Offline-Ausführung ohne externe Netzwerkaufrufe
"""

from __future__ import annotations

import io
import json
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import MagicMock, patch

from telegram_publisher import (
    format_newsletter_messages,
    format_ranking_message,
    send_newsletter_notification,
    send_ranking_notification,
    send_telegram_message,
)

SAMPLE_RANKING_MD = """---
title: 'P2P Platform Audit Ranking – 2026-10'
audit_date: '2026-10-19'
year_month: '2026-10'
platforms_count: 5
---

# P2P Platform Audit Ranking – 2026-10

## 1. Master-Rangliste aller Plattformen

| Rang | Plattform | Netto-Score | Δ Vormonat | Risikoklasse | Depot-Limit | P1 (Reg) | P2 (Solv) | P3 (Asset) | P4 (Liq) | Malus | Flags |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1** | [Inrento](../factsheets/inrento.md) | **90** | `±0` | `TOP TIER` | 8-15 % | 25 | 24 | 25 | 16 | 0 | ✅ Valide |
| **2** | [Crowdpear](../factsheets/crowdpear.md) | **86** | `±0` | `TOP TIER` | 8-15 % | 25 | 22 | 23 | 16 | 0 | ⚠️ Konflikt |
| **3** | [Indemo](../factsheets/indemo.md) | **83** | `±0` | `TOP TIER` | 8-15 % | 25 | 22 | 25 | 11 | 0 | ✅ Valide |
| **4** | [Lande](../factsheets/lande.md) | **81** | `-6` | `TOP TIER` | 8-15 % | 23 | 21 | 25 | 18 | `-6 Pkt` | ✅ Valide |
| **5** | [Monefit](../factsheets/monefit.md) | **38** | `-16` | `DISTRESSED` | 0 % | 10 | 17 | 14 | 18 | `-21 Pkt` | ⚠️ Konflikt |

## 2. Akute Watchlist- & Risiko-Warnungen

> [!CAUTION]
> **Kapitalabzug & Neuanlage-Stopp für folgende Plattformen aktiv:**
> • **Revest** (SPECULATIVE, Score: 49): Malus-Abzug -8 Pkt.
> • **Monefit** (DISTRESSED, Score: 38): Malus-Abzug -21 Pkt.
"""

SAMPLE_NEWSLETTER_MD = """---
title: 'P2P Kredite Wochenrückblick KW 42/2026'
iso_week: '2026-W42'
verified_facts_count: 24
verified_sentences_count: 27
---

# P2P Kredite Wochenrückblick KW 42/2026

> **Kompakt-Briefing:** Die europäische P2P-Branche meldet fundamentale Neuigkeiten: TWINO erhält MiCA-Lizenz.

---

## Volumen, Meilensteine & Portfoliorückflüsse
*Kategorie: `zahlen_statistik` | Plattformen: **LANDE, Loanch***

**LANDE** finanzierte im September 2026 ein Volumen von 2.060.500 EUR.

Auf **Loanch** investierten Anleger im September 9,6 Mio. EUR in Kredite.

> ⚠️ **Abweichende Berichte zwischen Quellen:**
> - Diff 1

**Geprüfte Quellen:**
- [Quelle 1](https://example.com)

---

## Plattform-Features & Produktneuheiten
*Kategorie: `plattform_features` | Plattformen: **Debitum***

**Debitum** hat das neue Produkt Debitum Flow angekündigt.

**Geprüfte Quellen:**
- [Quelle 2](https://example.com)

---

### Revisions- & Prüfnachweis
- **Integrität:** 24 Fakten geprüft • 27 Verifiersätze
"""


class TestTelegramPublisher(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base_dir = Path(self.temp_dir.name)

        self.ranking_file = self.base_dir / "audit-ranking-2026-10.md"
        self.ranking_file.write_text(SAMPLE_RANKING_MD, encoding="utf-8")

        self.newsletter_file = self.base_dir / "newsletter-2026-W42.md"
        self.newsletter_file.write_text(SAMPLE_NEWSLETTER_MD, encoding="utf-8")

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_disabled_publisher(self) -> None:
        """Prüft, dass bei deaktivierter Notification keine HTTP-Anfrage erfolgt."""
        with patch.dict("os.environ", {"TELEGRAM_NOTIFY_ENABLED": "false"}):
            with patch("urllib.request.urlopen") as mock_urlopen:
                res = send_telegram_message("Test")
                self.assertTrue(res)
                mock_urlopen.assert_not_called()

    def test_missing_credentials(self) -> None:
        """Prüft Rückgabe von False wenn Token oder Chat-ID fehlen."""
        with patch.dict(
            "os.environ",
            {
                "TELEGRAM_TOKEN": "",
                "TELEGRAM_CHAT_ID": "",
                "TELEGRAM_NOTIFY_ENABLED": "true",
            },
        ):
            res = send_telegram_message("Test")
            self.assertFalse(res)

    @patch("urllib.request.urlopen")
    def test_send_telegram_message_success(self, mock_urlopen: MagicMock) -> None:
        """Prüft erfolgreichen HTTP-Post mit HTML parse_mode."""
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps(
            {"ok": True, "result": {"message_id": 99}}
        ).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        res = send_telegram_message(
            text="<b>Hallo</b>",
            token="123:ABC",
            chat_id="456",
        )
        self.assertTrue(res)
        mock_urlopen.assert_called_once()
        req = mock_urlopen.call_args[0][0]
        self.assertEqual(
            req.get_full_url(), "https://api.telegram.org/bot123:ABC/sendMessage"
        )
        payload = json.loads(req.data.decode("utf-8"))
        self.assertEqual(payload["chat_id"], "456")
        self.assertEqual(payload["text"], "<b>Hallo</b>")
        self.assertEqual(payload["parse_mode"], "HTML")
        self.assertTrue(payload["disable_web_page_preview"])

    @patch("urllib.request.urlopen")
    def test_send_telegram_message_http_error(self, mock_urlopen: MagicMock) -> None:
        """Prüft saubere Fehlerbehandlung bei HTTP-Error."""
        err = urllib.error.HTTPError(
            url="https://api.telegram.org",
            code=400,
            msg="Bad Request",
            hdrs={},  # type: ignore[arg-type]
            fp=io.BytesIO(b'{"ok": false, "description": "Chat not found"}'),
        )
        mock_urlopen.side_effect = err
        res = send_telegram_message("Test", token="123", chat_id="456")
        self.assertFalse(res)

    def test_format_ranking_message(self) -> None:
        """Prüft das Format des Rankings ohne Emojis oder horizontale Linien."""
        msg = format_ranking_message(
            self.ranking_file, repo="owner/repo", branch="main"
        )

        # Titel & Inhalt vorhanden
        self.assertIn("<b>P2P Platform Audit Ranking – 2026-10</b>", msg)
        self.assertIn("Top 5 Plattformen (Netto-Score / 100):", msg)
        self.assertIn("1. Inrento – 90 Pkt (±0) [Top Tier]", msg)
        self.assertIn("5. Monefit – 38 Pkt (-16) [Distressed]", msg)

        # Größte Veränderungen
        self.assertIn("Größte Veränderungen:", msg)
        self.assertIn("Monefit: 38 Pkt (-16)", msg)

        # Neuanlage-Stopps
        self.assertIn("Neuanlage-Stopp (0 % Depot-Limit):", msg)
        self.assertIn("Revest, Monefit", msg)

        # GitHub-Link
        self.assertIn(
            "https://github.com/owner/repo/blob/main/data/rankings/audit-ranking-2026-10.md",
            msg,
        )

        # Keine Emojis oder Trennlinien
        for prohibited in ["📊", "🥇", "🥈", "🚜", "⚠️", "🛑", "━━━━", "───"]:
            self.assertNotIn(prohibited, msg)

    def test_format_newsletter_messages(self) -> None:
        """Prüft Aufteilung nach Kategorien, Entfall von Emojis, Linien und Prüfzeile."""
        msgs = format_newsletter_messages(
            self.newsletter_file, repo="owner/repo", branch="main"
        )

        # 3 Nachrichten erwartet: Intro, Volumen, Features
        self.assertEqual(len(msgs), 3)

        # Nachricht 1: Intro
        self.assertIn("P2P Kredite Wochenrückblick KW 42/2026", msgs[0])
        self.assertIn("Kompakt-Briefing:", msgs[0])
        self.assertIn("TWINO erhält MiCA-Lizenz", msgs[0])

        # Nachricht 2: Volumen
        self.assertIn("<b>Volumen &amp; Statistiken</b>", msgs[1])
        self.assertIn("<b>LANDE</b> finanzierte im September", msgs[1])
        self.assertIn("Auf <b>Loanch</b> investierten", msgs[1])
        # Keine Quellenliste oder Konflikte
        self.assertNotIn("Geprüfte Quellen", msgs[1])
        self.assertNotIn("Diff 1", msgs[1])

        # Nachricht 3: Features & Abschluss
        self.assertIn("<b>Features &amp; Gesamtreport</b>", msgs[2])
        self.assertIn("<b>Debitum</b> hat das neue Produkt", msgs[2])
        self.assertIn(
            "https://github.com/owner/repo/blob/main/data/newsletters/newsletter-2026-W42.md",
            msgs[2],
        )

        # Keine Prüfzeile ("24 Fakten geprüft")
        for m in msgs:
            self.assertNotIn("24 Fakten geprüft", m)
            self.assertNotIn("Verifiersätze", m)
            for prohibited in ["📬", "📊", "🚜", "⚖️", "⚠️", "🎁", "━━━━", "───"]:
                self.assertNotIn(prohibited, m)

    @patch("telegram_publisher.send_telegram_message")
    def test_send_ranking_notification(self, mock_send: MagicMock) -> None:
        """Prüft End-to-End Aufruf für Ranking."""
        mock_send.return_value = True
        ok = send_ranking_notification(self.ranking_file)
        self.assertTrue(ok)
        mock_send.assert_called_once()

    @patch("telegram_publisher.send_telegram_message")
    def test_send_newsletter_notification(self, mock_send: MagicMock) -> None:
        """Prüft End-to-End Aufruf für Newsletter."""
        mock_send.return_value = True
        ok = send_newsletter_notification(self.newsletter_file, sleep_interval=0.0)
        self.assertTrue(ok)
        self.assertEqual(mock_send.call_count, 3)


if __name__ == "__main__":
    unittest.main()
