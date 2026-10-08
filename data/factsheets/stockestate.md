---
platform: stockestate
platform_name: Stockestate
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
  data_gaps:
  - Unabhängige Bilanzen der Betreibergesellschaft nicht öffentlich einsehbar
evidence_metadata:
  sourcing_strategy: curated_profile_and_secondary_audits
  primary_crawled_pages: 4
  curated_profile_used: true
  secondary_reviews_count: 2
benchmarks:
  rethink_p2p_score: null
  rethink_p2p_rank: Nicht gelistet
  rethink_p2p_red_flags: null
  p2p_game_score: null
  p2p_game_rank: Nicht gelistet
  p2p_empire_safety_score: 4.5
  p2p_empire_safety_band: Niedrig
  p2p_empire_portfolio_perf: 80.0
  lars_wrobbel_score: 8
  lars_wrobbel_rank: Rang 26
pillars:
  pillar_1_regulation:
    score: 17
    max_score: 25
    band: Band_14_20
    rating: National reguliert
    evidence: Immobilien-Crowdfunding in Rumänien unter nationaler Regulierung; Verwahrung
      über getrennte Konten.
  pillar_2_solvency:
    score: 17
    max_score: 25
    band: Band_14_20
    rating: Solide / Lokaler Abschluss
    evidence: Kleine Betreibergesellschaft mit überschaubarem Track-Record und begrenzter
      Publizität unabhängiger Bilanzen.
  pillar_3_collateral:
    score: 23
    max_score: 25
    band: Band_21_25
    rating: Erststellige Realsicherheiten
    evidence: Grundbuchlich besicherte Immobilienkredite in Rumänien mit Hypotheken
      und LTV meist zwischen 60 und 70%.
  pillar_4_liquidity:
    score: 9
    max_score: 25
    band: Band_6_12
    rating: Illiquide / Langläufer ohne Zweitmarkt
    evidence: Kein Sekundärmarkt vorhanden; Kapitalbindung über 12 bis 24 Monate bis
      Projektabschluss.
malus_deductions: []
sources:
- source_type: curated_profile
  path: data/platforms/stockestate/profile.yaml
- source_type: erfahrungen
  path: data/erfahrungen/p2p-empire/stockestate.md
---

# Platform Audit Factsheet: Stockestate

**Audit-Datum:** 2026-10-08 | **Klasse:** `MID RISK` | **Depot-Limit:** `5 - 8 %`

## 1. Executive Summary & Audit-Verdict

> [!IMPORTANT]
> **Finaler Netto-Score:** **66 / 100 Punkte** (Rohscore: 66 Pkt | Malus-Abschläge: 0 Pkt)
> **Allokationsempfehlung:** Solide Beimischung: Hohe Bonität/Historie, aber unbesicherte Konsumkredite oder Monokulturen.

> [!NOTE]
> **Vorsichtsprinzip bei Datenlücken aktiv:**
> • Unabhängige Bilanzen der Betreibergesellschaft nicht öffentlich einsehbar

## 2. Aufschlüsselung der 4 Säulen

| Säule | Kategorie | Punkte | Einstufung | Kern-Evidenz |
| :--- | :--- | :---: | :--- | :--- |
| **Säule 1** | Regulierung & Verwahrung | **17 / 25** | National reguliert | Immobilien-Crowdfunding in Rumänien unter nationaler Regulierung; Verwahrung über getrennte Konten. |
| **Säule 2** | Solvenz & Governance | **17 / 25** | Solide / Lokaler Abschluss | Kleine Betreibergesellschaft mit überschaubarem Track-Record und begrenzter Publizität unabhängiger Bilanzen. |
| **Säule 3** | Besicherung & Workout | **23 / 25** | Erststellige Realsicherheiten | Grundbuchlich besicherte Immobilienkredite in Rumänien mit Hypotheken und LTV meist zwischen 60 und 70%. |
| **Säule 4** | Liquidität & Zweitmarkt | **9 / 25** | Illiquide / Langläufer ohne Zweitmarkt | Kein Sekundärmarkt vorhanden; Kapitalbindung über 12 bis 24 Monate bis Projektabschluss. |
| **SUMME** | **Rohscore (vor Mali)** | **66 / 100** | - | Theoretisches Maximum: 100 Pkt |

## 3. Malus-System (Strikte Risiko-Abschläge)

Keine Malus-Abschläge wirksam. Das Portfolio weist weder unzulässige Monokulturen (>50 %), noch Fristen-Mismatches oder Governance-Opazität auf.

## 4. Benchmark-Spiegel (Marktkonsens & Triangulierung)

| Externe Referenzquelle | Metrik / Wert | Interpretation |
| :--- | :---: | :--- |
| **re:think P2P Risk Score** | **N/A / 10** (Nicht gelistet) | Denny Neidhardt Sicherheitsranking  |
| **P2P Game Rating** | **N/A / 100** (Nicht gelistet) | Thomas P2P Rating (von 40 Plattformen) |
| **P2P Empire Safety Score** | **4.5 / 10** (Niedrig) | Unabhängiger Testbericht Jakub Krejci |
| **P2P Empire Portfolio Performance** | **80.0 %** | Reale Rückzahlungsquote im Portfolio |
| **Lars Wrobbel / Passives Einkommen** | **Rang 26** (8/40 Pkt) | Langzeit-Rating aus Community- & Blog-Erfahrung |

---
*Automatisch generiert durch das P2P Audit Scoring System am 2026-10-08.*