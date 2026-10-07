---
platform: nectaro
platform_name: Nectaro
audit_date: '2026-10-07'
audit_version: '1.0'
audit_score:
  net_score: 76
  raw_score: 82
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
  rethink_p2p_score: 8.0
  rethink_p2p_rank: Platz 2
  rethink_p2p_red_flags: '0'
  p2p_game_score: 58
  p2p_game_rank: Platz 16 von 40
  p2p_empire_safety_score: 8.5
  p2p_empire_safety_band: Hoch
  p2p_empire_portfolio_perf: 100.0
  lars_wrobbel_score: 22
  lars_wrobbel_rank: Rang 10
pillars:
  pillar_1_regulation:
    score: 25
    max_score: 25
    band: Band_21_25
    rating: MiFID II / IBF lizenziert
    evidence: Voll regulierte Wertpapierfirma (IBF) unter Aufsicht der Latvijas Banka.
      Gesetzlicher Entschädigungsfonds bis 20.000 € schützt Barguthaben.
  pillar_2_solvency:
    score: 25
    max_score: 25
    band: Band_21_25
    rating: Sehr gut / Testiert
    evidence: Substanzieller Konzernrückhalt durch DYNINNO Fintech-Sparte.
  pillar_3_collateral:
    score: 16
    max_score: 25
    band: Band_8_14
    rating: Unbesichert mit Buyback
    evidence: Strikte Due-Diligence der Dyninno-Kreditanbahner (z. B. EcoFinance).
  pillar_4_liquidity:
    score: 16
    max_score: 25
    band: Band_13_19
    rating: Gute Liquidität
    evidence: Kein Sekundärmarkt; Liquidität über planbare monatliche Tilgungen und
      Zinszuflüsse.
malus_deductions:
- type: monoculture
  name: Monokultur-Malus
  penalty: -6
  trigger: DYNINNO Group (EcoFinance) stellt 75.0 % des Portfolios (>50 %)
  evidence: 'Hohe Klumpenbildung: Über 75.0 % Abhängigkeit von einem Garantiekonzern.'
sources:
- source_type: curated_profile
  path: data/platforms/nectaro/profile.yaml
- source_type: erfahrungen
  path: data/erfahrungen/p2p-empire/nectaro.md
---

# Platform Audit Factsheet: Nectaro

**Audit-Datum:** 2026-10-07 | **Klasse:** `TOP TIER` | **Depot-Limit:** `8 - 15 %`

## 1. Executive Summary & Audit-Verdict

> [!IMPORTANT]
> **Finaler Netto-Score:** **76 / 100 Punkte** (Rohscore: 82 Pkt | Malus-Abschläge: -6 Pkt)
> **Allokationsempfehlung:** Kerninvestment: 1st-Rank Hypotheken, segregierte Treuhandkonten, 0 % Verlusthistorie.

## 2. Aufschlüsselung der 4 Säulen

| Säule | Kategorie | Punkte | Einstufung | Kern-Evidenz |
| :--- | :--- | :---: | :--- | :--- |
| **Säule 1** | Regulierung & Verwahrung | **25 / 25** | MiFID II / IBF lizenziert | Voll regulierte Wertpapierfirma (IBF) unter Aufsicht der Latvijas Banka. Gesetzlicher Entschädigungsfonds bis 20.000 € schützt Barguthaben. |
| **Säule 2** | Solvenz & Governance | **25 / 25** | Sehr gut / Testiert | Substanzieller Konzernrückhalt durch DYNINNO Fintech-Sparte. |
| **Säule 3** | Besicherung & Workout | **16 / 25** | Unbesichert mit Buyback | Strikte Due-Diligence der Dyninno-Kreditanbahner (z. B. EcoFinance). |
| **Säule 4** | Liquidität & Zweitmarkt | **16 / 25** | Gute Liquidität | Kein Sekundärmarkt; Liquidität über planbare monatliche Tilgungen und Zinszuflüsse. |
| **SUMME** | **Rohscore (vor Mali)** | **82 / 100** | - | Theoretisches Maximum: 100 Pkt |

## 3. Malus-System (Strikte Risiko-Abschläge)

| Malus-Typ | Abzug | Auslöser / Kriterium | Beleg / Nachweis |
| :--- | :---: | :--- | :--- |
| **Monokultur-Malus** | `-6 Pkt` | DYNINNO Group (EcoFinance) stellt 75.0 % des Portfolios (>50 %) | Hohe Klumpenbildung: Über 75.0 % Abhängigkeit von einem Garantiekonzern. |

## 4. Benchmark-Spiegel (Marktkonsens & Triangulierung)

| Externe Referenzquelle | Metrik / Wert | Interpretation |
| :--- | :---: | :--- |
| **re:think P2P Risk Score** | **8.0 / 10** (Platz 2) | Denny Neidhardt Sicherheitsranking (Red Flags: 0) |
| **P2P Game Rating** | **58 / 100** (Platz 16 von 40) | Thomas P2P Rating (von 40 Plattformen) |
| **P2P Empire Safety Score** | **8.5 / 10** (Hoch) | Unabhängiger Testbericht Jakub Krejci |
| **P2P Empire Portfolio Performance** | **100.0 %** | Reale Rückzahlungsquote im Portfolio |
| **Lars Wrobbel / Passives Einkommen** | **Rang 10** (22/40 Pkt) | Langzeit-Rating aus Community- & Blog-Erfahrung |

---
*Automatisch generiert durch das P2P Audit Scoring System am 2026-10-07.*