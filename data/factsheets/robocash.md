---
platform: robocash
platform_name: Robocash
audit_date: '2026-10-19'
audit_version: '1.0'
audit_score:
  net_score: 56
  raw_score: 66
  risk_class: WATCHLIST
  portfolio_limit: 0 - 3 %
  recommendation: 'Taktische Position unter Vorbehalt: Schwächen bei LTV, fehlende
    Testate oder Governance-Risse.'
flags:
  has_conflict: false
  conflict_notes: []
  data_gaps: []
evidence_metadata:
  sourcing_strategy: curated_profile_and_secondary_audits
  primary_crawled_pages: 4
  curated_profile_used: true
  secondary_reviews_count: 2
benchmarks:
  rethink_p2p_score: 5.7
  rethink_p2p_rank: Platz 16
  rethink_p2p_red_flags: '-7'
  p2p_game_score: 39
  p2p_game_rank: Platz 26 von 40
  p2p_empire_safety_score: 4.6
  p2p_empire_safety_band: Niedrig
  p2p_empire_portfolio_perf: 100.0
  lars_wrobbel_score: 28
  lars_wrobbel_rank: Rang 11
  p2pdash_community_score: 40
  p2pdash_median_xirr: 10.2
  p2pdash_investors_count: 281
pillars:
  pillar_1_regulation:
    score: 8
    max_score: 25
    band: Band_6_13
    rating: Unreguliert (Abtretungsverträge)
    evidence: Unreguliert über Kroatien operierend.
  pillar_2_solvency:
    score: 20
    max_score: 25
    band: Band_21_25
    rating: Sehr gut / Testiert
    evidence: Mutterkonzern UnaFinancial profitabel, jedoch Klumpen in volatilen Schwellenländern
      und historische Russland-Wurzeln.
  pillar_3_collateral:
    score: 14
    max_score: 25
    band: Band_8_14
    rating: Unbesichert mit Buyback
    evidence: 0 % historischer Kapitalverlust für Anleger; 30-Tage Rückkauffrist.
  pillar_4_liquidity:
    score: 24
    max_score: 25
    band: Band_20_25
    rating: Sehr liquide / Kurzläufer & Zweitmarkt
    evidence: Sehr hohe Liquidität durch 30-Tage-Kurzläufer und gebührenfreien Sekundärmarkt.
malus_deductions:
- type: monoculture
  name: Klumpen- & Konzentrations-Malus
  penalty: -10
  trigger: UnaFinancial Holding stellt 100.0 % des Portfolios (>=30 %)
  evidence: 'Hohe Klumpenbildung: Über 100.0 % Abhängigkeit von einem Garantiekonzern
    oder Einzelschuldner.'
sources:
- source_type: curated_profile
  path: data/platforms/robocash/profile.yaml
- source_type: erfahrungen
  path: data/erfahrungen/p2p-empire/robocash.md
---

# Platform Audit Factsheet: Robocash

**Audit-Datum:** 2026-10-19 | **Klasse:** `WATCHLIST` | **Depot-Limit:** `0 - 3 %`

## 1. Executive Summary & Audit-Verdict

> [!IMPORTANT]
> **Finaler Netto-Score:** **56 / 100 Punkte** (Rohscore: 66 Pkt | Malus-Abschläge: -10 Pkt)
> **Allokationsempfehlung:** Taktische Position unter Vorbehalt: Schwächen bei LTV, fehlende Testate oder Governance-Risse.

## 2. Aufschlüsselung der 4 Säulen

| Säule | Kategorie | Punkte | Einstufung | Kern-Evidenz |
| :--- | :--- | :---: | :--- | :--- |
| **Säule 1** | Regulierung & Verwahrung | **8 / 25** | Unreguliert (Abtretungsverträge) | Unreguliert über Kroatien operierend. |
| **Säule 2** | Solvenz & Governance | **20 / 25** | Sehr gut / Testiert | Mutterkonzern UnaFinancial profitabel, jedoch Klumpen in volatilen Schwellenländern und historische Russland-Wurzeln. |
| **Säule 3** | Besicherung & Workout | **14 / 25** | Unbesichert mit Buyback | 0 % historischer Kapitalverlust für Anleger; 30-Tage Rückkauffrist. |
| **Säule 4** | Liquidität & Zweitmarkt | **24 / 25** | Sehr liquide / Kurzläufer & Zweitmarkt | Sehr hohe Liquidität durch 30-Tage-Kurzläufer und gebührenfreien Sekundärmarkt. |
| **SUMME** | **Rohscore (vor Mali)** | **66 / 100** | - | Theoretisches Maximum: 100 Pkt |

## 3. Malus-System (Strikte Risiko-Abschläge)

| Malus-Typ | Abzug | Auslöser / Kriterium | Beleg / Nachweis |
| :--- | :---: | :--- | :--- |
| **Klumpen- & Konzentrations-Malus** | `-10 Pkt` | UnaFinancial Holding stellt 100.0 % des Portfolios (>=30 %) | Hohe Klumpenbildung: Über 100.0 % Abhängigkeit von einem Garantiekonzern oder Einzelschuldner. |

## 4. Benchmark-Spiegel (Marktkonsens & Triangulierung)

| Externe Referenzquelle | Metrik / Wert | Interpretation |
| :--- | :---: | :--- |
| **re:think P2P Risk Score** | **5.7 / 10** (Platz 16) | Denny Neidhardt Sicherheitsranking (Red Flags: -7) |
| **P2P Game Rating** | **39 / 100** (Platz 26 von 40) | Thomas P2P Rating (von 40 Plattformen) |
| **P2P Empire Safety Score** | **4.6 / 10** (Niedrig) | Unabhängiger Testbericht Jakub Krejci |
| **P2P Empire Portfolio Performance** | **100.0 %** | Reale Rückzahlungsquote im Portfolio |
| **Lars Wrobbel / Passives Einkommen** | **Rang 11** (28/40 Pkt) | Langzeit-Rating aus Community- & Blog-Erfahrung |
| **P2P Dash Community Score** | **40 / 100** (10.2 % XIRR) | 281 Investoren (Empirischer Schwarm-Score) |

---
*Automatisch generiert durch das P2P Audit Scoring System am 2026-10-19.*