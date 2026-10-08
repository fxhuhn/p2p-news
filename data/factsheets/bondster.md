---
platform: bondster
platform_name: Bondster
audit_date: '2026-10-07'
audit_version: '1.0'
audit_score:
  net_score: 60
  raw_score: 60
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
  rethink_p2p_score: 1.3
  rethink_p2p_rank: Platz 29
  rethink_p2p_red_flags: '0'
  p2p_game_score: 43
  p2p_game_rank: Platz 24 von 40
  p2p_empire_safety_score: 0.0
  p2p_empire_safety_band: Niedrig
  p2p_empire_portfolio_perf: 65.0
  lars_wrobbel_score: null
  lars_wrobbel_rank: Kein Rating
pillars:
  pillar_1_regulation:
    score: 8
    max_score: 25
    band: Band_6_13
    rating: Unreguliert (Abtretungsverträge)
    evidence: Unregulierter tschechischer P2P-Marktplatz.
  pillar_2_solvency:
    score: 17
    max_score: 25
    band: Band_14_20
    rating: Solide / Lokaler Abschluss
    evidence: Wiederholte Ausfälle externer Kreditanbahner (Right Choice, Lime, EuroGroshi).
  pillar_3_collateral:
    score: 17
    max_score: 25
    band: Band_15_20
    rating: Dinglich besichert (Mobiliar)
    evidence: Ausfallquote überdurchschnittlich hoch; zersplitterter Workout-Prozess.
  pillar_4_liquidity:
    score: 18
    max_score: 25
    band: Band_13_19
    rating: Gute Liquidität
    evidence: Gebührenfreier Sekundärmarkt vorhanden.
malus_deductions: []
sources:
- source_type: curated_profile
  path: data/platforms/bondster/profile.yaml
- source_type: erfahrungen
  path: data/erfahrungen/p2p-empire/bondster.md
---

# Platform Audit Factsheet: Bondster

**Audit-Datum:** 2026-10-07 | **Klasse:** `MID RISK` | **Depot-Limit:** `5 - 8 %`

## 1. Executive Summary & Audit-Verdict

> [!IMPORTANT]
> **Finaler Netto-Score:** **60 / 100 Punkte** (Rohscore: 60 Pkt | Malus-Abschläge: 0 Pkt)
> **Allokationsempfehlung:** Solide Beimischung: Hohe Bonität/Historie, aber unbesicherte Konsumkredite oder Monokulturen.

## 2. Aufschlüsselung der 4 Säulen

| Säule | Kategorie | Punkte | Einstufung | Kern-Evidenz |
| :--- | :--- | :---: | :--- | :--- |
| **Säule 1** | Regulierung & Verwahrung | **8 / 25** | Unreguliert (Abtretungsverträge) | Unregulierter tschechischer P2P-Marktplatz. |
| **Säule 2** | Solvenz & Governance | **17 / 25** | Solide / Lokaler Abschluss | Wiederholte Ausfälle externer Kreditanbahner (Right Choice, Lime, EuroGroshi). |
| **Säule 3** | Besicherung & Workout | **17 / 25** | Dinglich besichert (Mobiliar) | Ausfallquote überdurchschnittlich hoch; zersplitterter Workout-Prozess. |
| **Säule 4** | Liquidität & Zweitmarkt | **18 / 25** | Gute Liquidität | Gebührenfreier Sekundärmarkt vorhanden. |
| **SUMME** | **Rohscore (vor Mali)** | **60 / 100** | - | Theoretisches Maximum: 100 Pkt |

## 3. Malus-System (Strikte Risiko-Abschläge)

Keine Malus-Abschläge wirksam. Das Portfolio weist weder unzulässige Monokulturen (>50 %), noch Fristen-Mismatches oder Governance-Opazität auf.

## 4. Benchmark-Spiegel (Marktkonsens & Triangulierung)

| Externe Referenzquelle | Metrik / Wert | Interpretation |
| :--- | :---: | :--- |
| **re:think P2P Risk Score** | **1.3 / 10** (Platz 29) | Denny Neidhardt Sicherheitsranking (Red Flags: 0) |
| **P2P Game Rating** | **43 / 100** (Platz 24 von 40) | Thomas P2P Rating (von 40 Plattformen) |
| **P2P Empire Safety Score** | **0.0 / 10** (Niedrig) | Unabhängiger Testbericht Jakub Krejci |
| **P2P Empire Portfolio Performance** | **65.0 %** | Reale Rückzahlungsquote im Portfolio |
| **Lars Wrobbel / Passives Einkommen** | **Kein Rating** (N/A/40 Pkt) | Langzeit-Rating aus Community- & Blog-Erfahrung |

---
*Automatisch generiert durch das P2P Audit Scoring System am 2026-10-07.*