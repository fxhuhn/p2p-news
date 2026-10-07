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


if __name__ == "__main__":
    unittest.main()
