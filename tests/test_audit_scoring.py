"""
Unit Tests für das P2P Audit Scoring System
Prüft:
- Säulen-Berechnung & Modifikatoren
- Malus-Abzüge (Monokultur, Fristen-Mismatch, Related-Party, Distressed)
- Risikoklassen-Zuordnung & Depot-Limits
- SQLite-Persistierung & Delta-Berechnung
"""

import shutil
import tempfile
import unittest
from pathlib import Path

from platform_scorer import PlatformScorer
from scoring_models import determine_risk_class
from storage_sqlite import SQLiteStore


class TestAuditScoring(unittest.TestCase):
    def setUp(self):
        self.scorer = PlatformScorer()
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test_audit.db"
        self.store = SQLiteStore(str(self.db_path))

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_risk_class_assignment(self):
        self.assertEqual(determine_risk_class(90), "TOP TIER")
        self.assertEqual(determine_risk_class(70), "TOP TIER")
        self.assertEqual(determine_risk_class(69), "MID RISK")
        self.assertEqual(determine_risk_class(60), "MID RISK")
        self.assertEqual(determine_risk_class(55), "WATCHLIST")
        self.assertEqual(determine_risk_class(51), "WATCHLIST")
        self.assertEqual(determine_risk_class(50), "SPECULATIVE")
        self.assertEqual(determine_risk_class(40), "SPECULATIVE")
        self.assertEqual(determine_risk_class(39), "DISTRESSED")
        self.assertEqual(determine_risk_class(10), "DISTRESSED")

    def test_esketit_audit_benchmark(self):
        profile = {
            "platform": "esketit",
            "platform_name": "Esketit",
            "regulation": {
                "type": "unregulated_with_pipeline",
                "custody": "Segregierte Bankkonten bei EU-Banken",
                "notes": "Kroatische Abtretungsverträge; IBF-Lizenz für Schwester IBC Invest erteilt.",
            },
            "governance_and_solvency": {
                "auditor": "BDO (unabhängig testiert)",
                "audit_opinion": "Unqualified",
                "equity_ratio_pct: ": 28.5,
                "notes": "Creamfinance Gruppe hochprofitabel.",
            },
            "collateral_and_workout": {
                "primary_asset_type": "Konsumkredite",
                "security_type": "Buyback-Garantie (60 Tage)",
                "historical_loss_pct": 0.0,
                "current_npl_pct": 4.0,
            },
            "liquidity_and_marketplace": {
                "secondary_market": True,
                "primary_loan_duration_days_avg": 45,
            },
            "malus_triggers": {
                "monoculture_pct": 82.0,
                "monoculture_originator": "Creamfinance",
            },
        }
        res = self.scorer.score_platform(profile)
        self.assertEqual(res["pillar_1"].final_score, 13)  # 9 + 2 + 2
        self.assertEqual(res["pillar_3"].final_score, 16)  # 11 + 3 + 2
        self.assertEqual(res["pillar_4"].final_score, 20)  # 22 - 2
        self.assertEqual(res["malus_total"], -6)  # 70-85% = -6
        self.assertIn(res["net_score"], [64, 65, 66])  # Im Zielbereich Mid Risk
        self.assertEqual(res["risk_class"], "MID RISK")

    def test_peerberry_audit_benchmark(self):
        profile = {
            "platform": "peerberry",
            "platform_name": "PeerBerry",
            "regulation": {
                "type": "unregulated",
                "custody": "Getrennte Firmenkonten (keine individuellen IBANs)",
                "notes": "Unreguliert über Kroatien/Litauen; Abtretungsverträge.",
            },
            "governance_and_solvency": {
                "auditor": "BDO / Grant Thornton (testierte Konzernabschlüsse)",
                "audit_opinion": "Unqualified / Ohne Einschränkung",
                "equity_ratio_pct": 31.0,
                "interest_coverage_ratio": 4.2,
                "notes": "Wirtschaftlich getragen durch hochprofitable Aventus Group (H1 2026 Nettogewinn 49,1 Mio. €, EK 264,2 Mio. €).",
            },
            "collateral_and_workout": {
                "primary_asset_type": "Kurzfristige Konsumentenkredite & Immobilienkredite",
                "security_type": "60-Tage Rückkaufgarantie + Gruppengarantie",
                "historical_loss_pct": 0.0,
                "current_npl_pct": 0.0,
                "notes": "0 % realisierter Kapitalverlust. 100 % Rückzahlung aller Kriegs-Kredite (über 50 Mio. €) aus Konzerngewinn.",
            },
            "liquidity_and_marketplace": {
                "secondary_market": True,
                "secondary_market_fee_pct": 0.0,
                "secondary_market_waiting_days": 0,
                "primary_loan_duration_days_avg": 30,
            },
            "malus_triggers": {
                "monoculture_pct": 88.0,
                "monoculture_originator": "Aventus Group",
            },
        }
        res = self.scorer.score_platform(profile)
        self.assertEqual(res["pillar_1"].final_score, 8)  # Base 8
        self.assertEqual(res["pillar_2"].final_score, 22)  # Base 20 + EK>30% 2
        self.assertEqual(res["pillar_3"].final_score, 17)  # Base 11 + 3 + 2 + 1
        self.assertEqual(res["pillar_4"].final_score, 24)  # Base 22 + Fee=0/<=30d 2
        self.assertEqual(res["malus_total"], -6)  # 70-90% Monokultur = -6
        self.assertEqual(res["raw_score"], 71)
        self.assertEqual(res["net_score"], 65)
        self.assertEqual(res["risk_class"], "MID RISK")

    def test_inrento_top_tier(self):
        profile = {
            "platform": "inrento",
            "platform_name": "InRento",
            "regulation": {
                "type": "licensed_ecsp",
                "custody": "Paysera Treuhandkonto",
            },
            "governance_and_solvency": {
                "auditor": "Grant Thornton",
                "audit_opinion": "Unqualified",
                "equity_ratio_pct": 42.0,
            },
            "collateral_and_workout": {
                "security_type": "1st-Rank Hypothek",
                "ltv_max_pct": 55.0,
                "historical_loss_pct": 0.0,
            },
            "liquidity_and_marketplace": {
                "secondary_market": True,
                "secondary_market_fee_pct": 2.0,
                "primary_loan_duration_days_avg": 720,
            },
            "malus_triggers": {
                "monoculture_pct": 10.0,
            },
        }
        res = self.scorer.score_platform(profile)
        self.assertEqual(res["pillar_1"].final_score, 25)  # ECSP 23 + Paysera 2
        self.assertEqual(res["pillar_3"].final_score, 25)  # 1st-Rank 23 + LTV 55% 2
        self.assertEqual(res["malus_total"], 0)
        self.assertGreaterEqual(res["net_score"], 85)
        self.assertEqual(res["risk_class"], "TOP TIER")

    def test_estateguru_distressed_malus(self):
        profile = {
            "platform": "estateguru",
            "platform_name": "EstateGuru",
            "regulation": {"type": "licensed_ecsp"},
            "governance_and_solvency": {"auditor": "lokal"},
            "collateral_and_workout": {
                "security_type": "Grundschuld",
                "current_npl_pct": 59.3,  # Auslöser für Notlage
            },
            "liquidity_and_marketplace": {
                "secondary_market": False,
                "withdrawal_queue_days": 14,  # Liquiditätsstau
            },
            "malus_triggers": {
                "distressed_workout": True,
                "distressed_notes": "59,3 % NPL, Restrukturierung, Zweitmarkt blockiert",
            },
        }
        res = self.scorer.score_platform(profile)
        self.assertEqual(res["pillar_3"].final_score, 3)  # Band 0-7 Basis 3
        self.assertEqual(res["pillar_4"].final_score, 2)  # Warteschlange Band 0-5
        self.assertEqual(res["malus_total"], -20)  # Distressed-Malus
        self.assertLess(res["net_score"], 40)
        self.assertEqual(res["risk_class"], "DISTRESSED")

    def test_sqlite_persistence_and_delta(self):
        # 1. Erster Monat: 60 Punkte
        s1 = {
            "platform": "testplat",
            "audit_date": "2026-09-01",
            "raw_score": 68,
            "net_score": 60,
            "risk_class": "MID RISK",
            "pillar_1": 15,
            "pillar_2": 20,
            "pillar_3": 15,
            "pillar_4": 18,
            "malus_total": -8,
            "malus_json": "[]",
            "has_conflict": False,
            "sourcing_strategy": "curated_profile_and_secondary_audits",
            "factsheet_path": "data/factsheets/testplat.md",
        }
        self.store.save_platform_score(s1)

        # 2. Zweiter Monat: 66 Punkte (Upgrade um +6)
        s2 = dict(s1)
        s2["audit_date"] = "2026-10-01"
        s2["net_score"] = 66
        self.store.save_platform_score(s2)

        # Abfragen
        latest = self.store.get_latest_platform_score("testplat")
        self.assertEqual(latest["net_score"], 66)

        prev = self.store.get_previous_platform_score(
            "testplat", before_date="2026-10-01"
        )
        self.assertIsNotNone(prev)
        self.assertEqual(prev["net_score"], 60)
        delta = latest["net_score"] - prev["net_score"]
        self.assertEqual(delta, 6)

    def test_ensure_platform_profiles_auto_seeding(self):
        """Prüft, dass bei leerem platforms-Verzeichnis automatisch aus seed_platforms initialisiert wird."""
        from run_audit_scoring import ensure_platform_profiles

        empty_data_dir = Path(self.temp_dir) / "empty_data"
        empty_data_dir.mkdir(parents=True, exist_ok=True)

        profiles = ensure_platform_profiles(data_dir=empty_data_dir)
        self.assertGreaterEqual(len(profiles), 20)
        self.assertTrue(
            (empty_data_dir / "platforms" / "mintos" / "profile.yaml").exists()
        )

    def test_ensure_platform_profiles_auto_sync_on_restart(self):
        """Prüft, dass veraltete Profile auf gemounteten Volumes autark aktualisiert werden."""
        from run_audit_scoring import ensure_platform_profiles

        test_data_dir = Path(self.temp_dir) / "test_sync_data"
        test_data_dir.mkdir(parents=True, exist_ok=True)

        # 1. Initialisiere
        ensure_platform_profiles(data_dir=test_data_dir)
        mintos_profile = test_data_dir / "platforms" / "mintos" / "profile.yaml"
        self.assertTrue(mintos_profile.exists())

        # 2. Veralteten Inhalt simulieren
        mintos_profile.write_text(
            "platform: mintos\noutdated: true\n", encoding="utf-8"
        )
        self.assertIn("outdated: true", mintos_profile.read_text(encoding="utf-8"))

        # 3. Autarker Sync bei Restart
        ensure_platform_profiles(data_dir=test_data_dir, auto_sync=True)
        updated_content = mintos_profile.read_text(encoding="utf-8")
        self.assertNotIn("outdated: true", updated_content)
        self.assertIn("founding_year: 2015", updated_content)

    def test_ensure_platform_profiles_sync_disabled(self):
        """Prüft, dass bei auto_sync=False bestehende Profile nicht überschrieben werden."""
        from run_audit_scoring import ensure_platform_profiles

        test_data_dir = Path(self.temp_dir) / "test_no_sync_data"
        test_data_dir.mkdir(parents=True, exist_ok=True)

        ensure_platform_profiles(data_dir=test_data_dir)
        mintos_profile = test_data_dir / "platforms" / "mintos" / "profile.yaml"
        mintos_profile.write_text(
            "platform: mintos\ncustom_user_edit: true\n", encoding="utf-8"
        )

        ensure_platform_profiles(data_dir=test_data_dir, auto_sync=False)
        self.assertIn(
            "custom_user_edit: true", mintos_profile.read_text(encoding="utf-8")
        )

    def test_ranking_generator_clean_sections_no_redundant_migration_report(
        self,
    ) -> None:
        """Prüft, dass RankingGenerator keine redundante Migration-Sektion rendert und die Abschnitte sauber nummeriert sind."""
        from ranking_generator import RankingGenerator

        # Score in Test-DB anlegen
        s = {
            "platform": "mintos",
            "audit_date": "2026-10-08",
            "raw_score": 84,
            "net_score": 84,
            "risk_class": "TOP TIER",
            "pillar_1": 25,
            "pillar_2": 22,
            "pillar_3": 17,
            "pillar_4": 20,
            "malus_total": 0,
            "malus_json": "[]",
            "has_conflict": False,
            "sourcing_strategy": "curated_profile",
            "factsheet_path": "data/factsheets/mintos.md",
        }
        self.store.save_platform_score(s)

        out_dir = Path(self.temp_dir) / "rankings"
        gen = RankingGenerator(db_path=self.db_path, output_dir=str(out_dir))
        rank_file = gen.generate_monthly_ranking("2026-10-08")
        content = rank_file.read_text(encoding="utf-8")

        # Frontmatter enthält Metadaten
        self.assertTrue(content.startswith("---\n"))
        self.assertIn("audit_date: '2026-10-08'", content)
        self.assertIn("platforms_count: 1", content)
        self.assertNotIn("**Stichtag:**", content)
        self.assertNotIn("**Geprüfte Plattformen:**", content)

        # Tabelle enthält Δ Vormonat
        self.assertIn("Δ Vormonat", content)
        # Redundanter Delta-Report entfällt
        self.assertNotIn("## 2. Rating-Migrationen & Delta-Report", content)
        self.assertNotIn("### 🔼 Aufwertungen", content)
        self.assertNotIn("### 🔽 Herabstufungen", content)
        # Nummerierung der Folgeabschnitte ist konsistent
        self.assertIn("## 2. Akute Watchlist- & Risiko-Warnungen", content)
        self.assertIn(
            "## 3. Portfoliogewichtung für ein 100.000 € Musterdepot", content
        )
        self.assertIn(
            "## 4. Markt-Triangulierung & Benchmark-Vergleichsspiegel", content
        )


if __name__ == "__main__":
    unittest.main()
