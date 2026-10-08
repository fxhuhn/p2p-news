---
platform: income
platform_name: Income Marketplace
audit_date: '2026-10-08'
audit_version: '1.0'
audit_score:
  net_score: 66
  raw_score: 66
  risk_class: MID RISK
  portfolio_limit: 5 - 8 %
  recommendation: 'Solide Beimischung: Hohe Bonität/Historie, aber unbesicherte Konsumkredite
    oder Monokulturen.'
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
  rethink_p2p_score: 6.2
  rethink_p2p_rank: Platz 11
  rethink_p2p_red_flags: '0'
  p2p_game_score: 52
  p2p_game_rank: Platz 19 von 40
  p2p_empire_safety_score: 8.1
  p2p_empire_safety_band: Mittel
  p2p_empire_portfolio_perf: 98.0
  lars_wrobbel_score: 25
  lars_wrobbel_rank: Rang 9
pillars:
  pillar_1_regulation:
    score: 13
    max_score: 25
    band: Band_6_13
    rating: Unreguliert / Lizenzübergang
    evidence: Operiert derzeit unreguliert über Abtretungsverträge, bietet aber institutionelle
      Schutzmechanismen (Junior Share, Cashflow Buffer).
  pillar_2_solvency:
    score: 21
    max_score: 25
    band: Band_21_25
    rating: Sehr gut / Testiert
    evidence: Testierte Finanzberichte und hohe Transparenz bei Anbahner-Bilanzen.
  pillar_3_collateral:
    score: 16
    max_score: 25
    band: Band_8_14
    rating: Unbesichert mit Buyback
    evidence: 'Innovativer Junior Share Mechanismus: Kreditanbahner trägt erste Verluste
      vor Anlegern.'
  pillar_4_liquidity:
    score: 16
    max_score: 25
    band: Band_13_19
    rating: Gute Liquidität
    evidence: Kein Sekundärmarkt, Liquidität über kurze originäre Kreditlaufzeiten.
malus_deductions: []
sources:
- source_type: curated_profile
  path: data/platforms/income/profile.yaml
- source_type: erfahrungen
  path: data/erfahrungen/p2p-empire/income.md
---

# Platform Audit Factsheet: Income Marketplace

**Audit-Datum:** 2026-10-08 | **Klasse:** `MID RISK` | **Depot-Limit:** `5 - 8 %`

## 1. Executive Summary & Audit-Verdict

> [!IMPORTANT]
> **Finaler Netto-Score:** **66 / 100 Punkte** (Rohscore: 66 Pkt | Malus-Abschläge: 0 Pkt)
> **Allokationsempfehlung:** Solide Beimischung: Hohe Bonität/Historie, aber unbesicherte Konsumkredite oder Monokulturen.

## 2. Aufschlüsselung der 4 Säulen

| Säule | Kategorie | Punkte | Einstufung | Kern-Evidenz |
| :--- | :--- | :---: | :--- | :--- |
| **Säule 1** | Regulierung & Verwahrung | **13 / 25** | Unreguliert / Lizenzübergang | Operiert derzeit unreguliert über Abtretungsverträge, bietet aber institutionelle Schutzmechanismen (Junior Share, Cashflow Buffer). |
| **Säule 2** | Solvenz & Governance | **21 / 25** | Sehr gut / Testiert | Testierte Finanzberichte und hohe Transparenz bei Anbahner-Bilanzen. |
| **Säule 3** | Besicherung & Workout | **16 / 25** | Unbesichert mit Buyback | Innovativer Junior Share Mechanismus: Kreditanbahner trägt erste Verluste vor Anlegern. |
| **Säule 4** | Liquidität & Zweitmarkt | **16 / 25** | Gute Liquidität | Kein Sekundärmarkt, Liquidität über kurze originäre Kreditlaufzeiten. |
| **SUMME** | **Rohscore (vor Mali)** | **66 / 100** | - | Theoretisches Maximum: 100 Pkt |

## 3. Malus-System (Strikte Risiko-Abschläge)

Keine Malus-Abschläge wirksam. Das Portfolio weist weder unzulässige Monokulturen (>50 %), noch Fristen-Mismatches oder Governance-Opazität auf.

## 4. Benchmark-Spiegel (Marktkonsens & Triangulierung)

| Externe Referenzquelle | Metrik / Wert | Interpretation |
| :--- | :---: | :--- |
| **re:think P2P Risk Score** | **6.2 / 10** (Platz 11) | Denny Neidhardt Sicherheitsranking (Red Flags: 0) |
| **P2P Game Rating** | **52 / 100** (Platz 19 von 40) | Thomas P2P Rating (von 40 Plattformen) |
| **P2P Empire Safety Score** | **8.1 / 10** (Mittel) | Unabhängiger Testbericht Jakub Krejci |
| **P2P Empire Portfolio Performance** | **98.0 %** | Reale Rückzahlungsquote im Portfolio |
| **Lars Wrobbel / Passives Einkommen** | **Rang 9** (25/40 Pkt) | Langzeit-Rating aus Community- & Blog-Erfahrung |

---
*Automatisch generiert durch das P2P Audit Scoring System am 2026-10-08.*