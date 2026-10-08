---
platform: afranga
platform_name: Afranga
audit_date: '2026-10-08'
audit_version: '1.0'
audit_score:
  net_score: 72
  raw_score: 80
  risk_class: TOP TIER
  portfolio_limit: 8 - 15 %
  recommendation: 'Kerninvestment: 1st-Rank Hypotheken, segregierte Treuhandkonten,
    0 % Verlusthistorie.'
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
  rethink_p2p_score: 6.4
  rethink_p2p_rank: Platz 8
  rethink_p2p_red_flags: '0'
  p2p_game_score: 60
  p2p_game_rank: Platz 14 von 40
  p2p_empire_safety_score: 7.3
  p2p_empire_safety_band: Mittel
  p2p_empire_portfolio_perf: 100.0
  lars_wrobbel_score: 21
  lars_wrobbel_rank: Rang 11
pillars:
  pillar_1_regulation:
    score: 23
    max_score: 25
    band: Band_21_25
    rating: ECSP lizenziert
    evidence: Regulierte paneuropäische Crowdfunding-Plattform (ECSP).
  pillar_2_solvency:
    score: 21
    max_score: 25
    band: Band_21_25
    rating: Sehr gut / Testiert
    evidence: Testierter Jahresabschluss der Stik Credit Gruppe.
  pillar_3_collateral:
    score: 16
    max_score: 25
    band: Band_8_14
    rating: Unbesichert mit Buyback
    evidence: Konsumkredite mit verlässlichem Rückkaufversprechen.
  pillar_4_liquidity:
    score: 20
    max_score: 25
    band: Band_20_25
    rating: Sehr liquide / Kurzläufer & Zweitmarkt
    evidence: Gebührenfreier Sekundärmarkt und kurze originäre Kreditlaufzeiten.
malus_deductions:
- type: monoculture
  name: Monokultur-Malus
  penalty: -8
  trigger: Stik Credit AD stellt 100.0 % des Portfolios (>50 %)
  evidence: 'Hohe Klumpenbildung: Über 100.0 % Abhängigkeit von einem Garantiekonzern.'
sources:
- source_type: curated_profile
  path: data/platforms/afranga/profile.yaml
- source_type: erfahrungen
  path: data/erfahrungen/p2p-empire/afranga.md
---

# Platform Audit Factsheet: Afranga

**Audit-Datum:** 2026-10-08 | **Klasse:** `TOP TIER` | **Depot-Limit:** `8 - 15 %`

## 1. Executive Summary & Audit-Verdict

> [!IMPORTANT]
> **Finaler Netto-Score:** **72 / 100 Punkte** (Rohscore: 80 Pkt | Malus-Abschläge: -8 Pkt)
> **Allokationsempfehlung:** Kerninvestment: 1st-Rank Hypotheken, segregierte Treuhandkonten, 0 % Verlusthistorie.

## 2. Aufschlüsselung der 4 Säulen

| Säule | Kategorie | Punkte | Einstufung | Kern-Evidenz |
| :--- | :--- | :---: | :--- | :--- |
| **Säule 1** | Regulierung & Verwahrung | **23 / 25** | ECSP lizenziert | Regulierte paneuropäische Crowdfunding-Plattform (ECSP). |
| **Säule 2** | Solvenz & Governance | **21 / 25** | Sehr gut / Testiert | Testierter Jahresabschluss der Stik Credit Gruppe. |
| **Säule 3** | Besicherung & Workout | **16 / 25** | Unbesichert mit Buyback | Konsumkredite mit verlässlichem Rückkaufversprechen. |
| **Säule 4** | Liquidität & Zweitmarkt | **20 / 25** | Sehr liquide / Kurzläufer & Zweitmarkt | Gebührenfreier Sekundärmarkt und kurze originäre Kreditlaufzeiten. |
| **SUMME** | **Rohscore (vor Mali)** | **80 / 100** | - | Theoretisches Maximum: 100 Pkt |

## 3. Malus-System (Strikte Risiko-Abschläge)

| Malus-Typ | Abzug | Auslöser / Kriterium | Beleg / Nachweis |
| :--- | :---: | :--- | :--- |
| **Monokultur-Malus** | `-8 Pkt` | Stik Credit AD stellt 100.0 % des Portfolios (>50 %) | Hohe Klumpenbildung: Über 100.0 % Abhängigkeit von einem Garantiekonzern. |

## 4. Benchmark-Spiegel (Marktkonsens & Triangulierung)

| Externe Referenzquelle | Metrik / Wert | Interpretation |
| :--- | :---: | :--- |
| **re:think P2P Risk Score** | **6.4 / 10** (Platz 8) | Denny Neidhardt Sicherheitsranking (Red Flags: 0) |
| **P2P Game Rating** | **60 / 100** (Platz 14 von 40) | Thomas P2P Rating (von 40 Plattformen) |
| **P2P Empire Safety Score** | **7.3 / 10** (Mittel) | Unabhängiger Testbericht Jakub Krejci |
| **P2P Empire Portfolio Performance** | **100.0 %** | Reale Rückzahlungsquote im Portfolio |
| **Lars Wrobbel / Passives Einkommen** | **Rang 11** (21/40 Pkt) | Langzeit-Rating aus Community- & Blog-Erfahrung |

---
*Automatisch generiert durch das P2P Audit Scoring System am 2026-10-08.*