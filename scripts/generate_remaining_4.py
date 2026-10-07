from pathlib import Path

import yaml

REMAINING = {
    "hive5": {
        "platform": "hive5",
        "platform_name": "hive5",
        "founding_year": 2022,
        "headquarters": "Zagreb, Kroatien / Vilnius, Litauen",
        "sourcing_strategy": "curated_profile_and_secondary_audits",
        "regulation": {
            "type": "unregulated",
            "regulator": None,
            "license_number": None,
            "custody": "Externe Zahlungsabwicklung via Paysera",
            "investor_compensation": False,
            "contract_structure": "Kroatische Abtretungsverträge (hive5 d.o.o.)",
            "notes": "Operiert über kroatisches SPV (hive5 d.o.o.) mit Abtretungsverträgen. Keine MiFID II / ECSP-Lizenz.",
        },
        "governance_and_solvency": {
            "guarantor_group": "Hive Finance Gruppe (Rupex, Tengo, Ekspres Pozyczka)",
            "auditor": None,
            "audit_opinion": "Ungeprüft",
            "profitability": "Management berichtet Profitabilität im rasanten Wachstum",
            "equity_ratio_pct": 20.0,
            "interest_coverage_ratio": 2.5,
            "notes": "Gehört zur Hive Finance Gruppe. Starkes Wachstum, Management berichtet Profitabilität, jedoch noch kein unabhängiges Big-Four / Tier-2 Testat.",
        },
        "collateral_and_workout": {
            "primary_asset_type": "Konsumentenkredite & Kurzzeit-Darlehen",
            "security_type": "60-Tage Buyback-Garantie der Anbahner",
            "ltv_max_pct": None,
            "historical_loss_pct": 0.0,
            "current_npl_pct": 3.0,
            "buyback_grace_period_days": 60,
            "notes": "Unbesicherte Payday- und Konsumentenkredite der Konzerngesellschaften (Rupex, Tengo). Rückkaufverpflichtung nach 60 Tagen.",
        },
        "liquidity_and_marketplace": {
            "secondary_market": False,
            "secondary_market_fee_pct": None,
            "secondary_market_waiting_days": None,
            "primary_loan_duration_days_avg": 45,
            "withdrawal_queue_days": 0,
            "notes": "Sehr kurze Laufzeiten (meist 30-90 Tage) sorgen für stetigen Rückfluss ohne zwingenden Sekundärmarkt. Zügige Auszahlungen.",
        },
        "malus_triggers": {
            "monoculture_pct": 90.0,
            "monoculture_originator": "Hive Finance Gruppe (Rupex / Tengo)",
            "term_mismatch": False,
            "related_party_opacity": False,
            "distressed_workout": False,
        },
        "benchmarks": {
            "p2p_empire_safety_score": 5.0,
            "p2p_empire_safety_band": "Mittel",
            "p2p_empire_portfolio_perf": 95.0,
            "lars_wrobbel_score": 15,
            "lars_wrobbel_rank": "Rang 18",
        },
        "data_gaps": [
            "Unabhängig testierter Konzernabschluss der Hive Finance Gruppe steht noch aus"
        ],
        "has_conflict": False,
        "conflict_notes": [],
    },
    "fagura": {
        "platform": "fagura",
        "platform_name": "Fagura",
        "founding_year": 2019,
        "headquarters": "Bukarest, Rumänien / Chișinău, Moldau",
        "sourcing_strategy": "curated_profile_and_secondary_audits",
        "regulation": {
            "type": "licensed_ecsp",
            "regulator": "ASF Rumänien (Autoritatea de Supraveghere Financiară)",
            "license_number": "ECSP Lizenz 2023",
            "custody": "Lemonway Treuhandkonten",
            "investor_compensation": False,
            "contract_structure": "ECSP Crowdfunding",
            "notes": "Seit 2023 voll ECSP-lizenziert durch die rumänische Finanzaufsicht (ASF). Gelder liegen segregiert bei Lemonway.",
        },
        "governance_and_solvency": {
            "guarantor_group": "Fagura Marketplace SRL / Fagura AS",
            "auditor": "Lokaler Wirtschaftsprüfer",
            "audit_opinion": "Unqualified",
            "profitability": "Venture-finanziert (SeedBlink Kampagnen), Fokus auf Wachstum/Breakeven",
            "equity_ratio_pct": 25.0,
            "interest_coverage_ratio": 1.2,
            "notes": "Venture-finanziertes Crowdfunding-Fintech. Wachstumsphase mit moderaten Verlusten/Breakeven-Fokus.",
        },
        "collateral_and_workout": {
            "primary_asset_type": "P2P-Konsumentenkredite & KMU-Darlehen",
            "security_type": "Unbesichert mit Bonitätsscoring & Provision Fund",
            "ltv_max_pct": None,
            "historical_loss_pct": 2.5,
            "current_npl_pct": 8.0,
            "buyback_grace_period_days": None,
            "notes": "Echte Peer-to-Peer Direktvergabe an Kreditnehmer in Moldau/Rumänien ohne Buyback, dafür mit Risikoklassen.",
        },
        "liquidity_and_marketplace": {
            "secondary_market": True,
            "secondary_market_fee_pct": 1.0,
            "secondary_market_waiting_days": 0,
            "primary_loan_duration_days_avg": 720,
            "withdrawal_queue_days": 0,
            "notes": "Funktionierender Sekundärmarkt vorhanden; Laufzeiten der Kredite betragen 12 bis 36 Monate.",
        },
        "malus_triggers": {
            "monoculture_pct": 0.0,
            "monoculture_originator": None,
            "term_mismatch": False,
            "related_party_opacity": False,
            "distressed_workout": False,
        },
        "benchmarks": {
            "p2p_empire_safety_score": 6.0,
            "p2p_empire_safety_band": "Mittel",
            "p2p_empire_portfolio_perf": 85.0,
            "lars_wrobbel_score": 12,
            "lars_wrobbel_rank": "Rang 22",
        },
        "data_gaps": [
            "Langfristige Ausfallraten nach Ausweitung auf Rumänien noch in Konsolidierung"
        ],
        "has_conflict": False,
        "conflict_notes": [],
    },
    "stockestate": {
        "platform": "stockestate",
        "platform_name": "Stockestate",
        "founding_year": 2020,
        "headquarters": "Bukarest, Rumänien",
        "sourcing_strategy": "curated_profile_and_secondary_audits",
        "regulation": {
            "type": "national_special",
            "regulator": "Nationale rumänische Vorgaben",
            "license_number": None,
            "custody": "Treuhandkonten bei rumänischen Geschäftsbanken",
            "investor_compensation": False,
            "contract_structure": "Immobilien-Crowdfunding Darlehensverträge",
            "notes": "Immobilien-Crowdfunding in Rumänien unter nationaler Regulierung; Verwahrung über getrennte Konten.",
        },
        "governance_and_solvency": {
            "guarantor_group": "Stockestate S.R.L.",
            "auditor": None,
            "audit_opinion": "Ungeprüft",
            "profitability": "Geringes Volumen, regionaler Entwicklerfokus",
            "equity_ratio_pct": 20.0,
            "interest_coverage_ratio": 1.5,
            "notes": "Kleine Betreibergesellschaft mit überschaubarem Track-Record und begrenzter Publizität unabhängiger Bilanzen.",
        },
        "collateral_and_workout": {
            "primary_asset_type": "Immobilienprojekte in Rumänien",
            "security_type": "1st-Rank Hypothek im Grundbuch",
            "ltv_max_pct": 68.0,
            "historical_loss_pct": 0.0,
            "current_npl_pct": 6.0,
            "buyback_grace_period_days": None,
            "notes": "Grundbuchlich besicherte Immobilienkredite in Rumänien mit Hypotheken und LTV meist zwischen 60 und 70%.",
        },
        "liquidity_and_marketplace": {
            "secondary_market": False,
            "secondary_market_fee_pct": None,
            "secondary_market_waiting_days": None,
            "primary_loan_duration_days_avg": 540,
            "withdrawal_queue_days": 0,
            "notes": "Kein Sekundärmarkt vorhanden; Kapitalbindung über 12 bis 24 Monate bis Projektabschluss.",
        },
        "malus_triggers": {
            "monoculture_pct": 45.0,
            "monoculture_originator": "Lokale Bauträger",
            "term_mismatch": False,
            "related_party_opacity": False,
            "distressed_workout": False,
        },
        "benchmarks": {
            "p2p_empire_safety_score": 4.5,
            "p2p_empire_safety_band": "Niedrig",
            "p2p_empire_portfolio_perf": 80.0,
            "lars_wrobbel_score": 8,
            "lars_wrobbel_rank": "Rang 26",
        },
        "data_gaps": [
            "Unabhängige Bilanzen der Betreibergesellschaft nicht öffentlich einsehbar"
        ],
        "has_conflict": False,
        "conflict_notes": [],
    },
    "asterra": {
        "platform": "asterra",
        "platform_name": "Asterra Estate",
        "founding_year": 2023,
        "headquarters": "Valencia, Spanien",
        "sourcing_strategy": "curated_profile_and_secondary_audits",
        "regulation": {
            "type": "unregulated",
            "regulator": None,
            "license_number": None,
            "custody": "Firmenkonten / Unklar getrennt",
            "investor_compensation": False,
            "contract_structure": "Nachrang- und Darlehensabtretung",
            "notes": "Sehr junge spanische Immobilienplattform; operiert ohne vollwertige ECSP-Lizenz über SPVs.",
        },
        "governance_and_solvency": {
            "guarantor_group": "Asterra Group",
            "auditor": None,
            "audit_opinion": "Ungeprüft",
            "profitability": "Minimaler Track-Record, Vorfinanzierungsphase",
            "equity_ratio_pct": 10.0,
            "interest_coverage_ratio": 1.0,
            "notes": "Keine testierten Finanzberichte vorhanden; minimaler Track-Record und Datenhistorie (Vorsichtsprinzip).",
        },
        "collateral_and_workout": {
            "primary_asset_type": "Immobilienentwicklungsprojekte",
            "security_type": "Nachrangdarlehen / Vorfinanzierung",
            "ltv_max_pct": 75.0,
            "historical_loss_pct": 0.0,
            "current_npl_pct": 12.0,
            "buyback_grace_period_days": None,
            "notes": "Nachrang- oder Vorfinanzierungsdarlehen im spanischen Immobilienmarkt; unvollständige dingliche Absicherungsnachweise.",
        },
        "liquidity_and_marketplace": {
            "secondary_market": False,
            "secondary_market_fee_pct": None,
            "secondary_market_waiting_days": None,
            "primary_loan_duration_days_avg": 365,
            "withdrawal_queue_days": 0,
            "notes": "Kein Sekundärmarkt; Kapital ist vollständig bis Projektende gebunden.",
        },
        "malus_triggers": {
            "monoculture_pct": 85.0,
            "monoculture_originator": "Lokale Bauträger-Partner",
            "term_mismatch": False,
            "related_party_opacity": False,
            "distressed_workout": False,
        },
        "benchmarks": {
            "p2p_empire_safety_score": 2.5,
            "p2p_empire_safety_band": "Niedrig",
            "p2p_empire_portfolio_perf": 70.0,
            "lars_wrobbel_score": 5,
            "lars_wrobbel_rank": "Rang 29",
        },
        "data_gaps": [
            "Fehlende Publizität von Betreiberfinanzen und Verwertungsnachweisen"
        ],
        "has_conflict": True,
        "conflict_notes": [
            "Unklare Regulierung und fehlende Nachweise für Treuhandsegregierung"
        ],
    },
}

for name, prof in REMAINING.items():
    p_dir = Path("data/platforms") / name
    p_dir.mkdir(parents=True, exist_ok=True)
    out_file = p_dir / "profile.yaml"
    with open(out_file, "w", encoding="utf-8") as f:
        yaml.dump(prof, f, allow_unicode=True, sort_keys=False)
    print(f"✓ Erstellt: {out_file}")

print("\nAlle 4 restlichen Plattform-Profile erfolgreich aktualisiert!")
