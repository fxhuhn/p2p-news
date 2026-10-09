---
platform: revest
platform_name: Revest
audit_date: '2026-10-09'
audit_version: '1.0'
audit_score:
  net_score: 51
  raw_score: 57
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
  rethink_p2p_score: null
  rethink_p2p_rank: Nicht gelistet
  rethink_p2p_red_flags: null
  p2p_game_score: 38
  p2p_game_rank: Platz 28 von 40
  p2p_empire_safety_score: 5.4
  p2p_empire_safety_band: Mittel
  p2p_empire_portfolio_perf: 100.0
  lars_wrobbel_score: null
  lars_wrobbel_rank: Nicht gelistet
pillars:
  pillar_1_regulation:
    score: 8
    max_score: 25
    band: Band_6_13
    rating: Unreguliert (Abtretungsverträge)
    evidence: Unreguliert nach estnischem/österreichischem Recht.
  pillar_2_solvency:
    score: 17
    max_score: 25
    band: Band_14_20
    rating: Solide / Lokaler Abschluss
    evidence: Eigentümergeführtes Immobilien-Startup.
  pillar_3_collateral:
    score: 23
    max_score: 25
    band: Band_21_25
    rating: Erststellige Realsicherheiten
    evidence: Immobilienentwicklungsprojekte mit höherem Fertigstellungsrisiko.
  pillar_4_liquidity:
    score: 9
    max_score: 25
    band: Band_6_12
    rating: Illiquide / Langläufer ohne Zweitmarkt
    evidence: Kein Sekundärmarkt, Kapital bis zur Projektfertigstellung gebunden.
malus_deductions:
- type: monoculture
  name: Monokultur-Malus
  penalty: -6
  trigger: Revest Group stellt 80.0 % des Portfolios (>50 %)
  evidence: 'Hohe Klumpenbildung: Über 80.0 % Abhängigkeit von einem Garantiekonzern.'
sources:
- source_type: curated_profile
  path: data/platforms/revest/profile.yaml
- source_type: erfahrungen
  path: data/erfahrungen/p2p-empire/revest.md
---

# Platform Audit Factsheet: Revest

**Audit-Datum:** 2026-10-09 | **Klasse:** `WATCHLIST` | **Depot-Limit:** `0 - 3 %`

## 1. Executive Summary & Audit-Verdict

> [!IMPORTANT]
> **Finaler Netto-Score:** **51 / 100 Punkte** (Rohscore: 57 Pkt | Malus-Abschläge: -6 Pkt)
> **Allokationsempfehlung:** Taktische Position unter Vorbehalt: Schwächen bei LTV, fehlende Testate oder Governance-Risse.

## 2. Aufschlüsselung der 4 Säulen

| Säule | Kategorie | Punkte | Einstufung | Kern-Evidenz |
| :--- | :--- | :---: | :--- | :--- |
| **Säule 1** | Regulierung & Verwahrung | **8 / 25** | Unreguliert (Abtretungsverträge) | Unreguliert nach estnischem/österreichischem Recht. |
| **Säule 2** | Solvenz & Governance | **17 / 25** | Solide / Lokaler Abschluss | Eigentümergeführtes Immobilien-Startup. |
| **Säule 3** | Besicherung & Workout | **23 / 25** | Erststellige Realsicherheiten | Immobilienentwicklungsprojekte mit höherem Fertigstellungsrisiko. |
| **Säule 4** | Liquidität & Zweitmarkt | **9 / 25** | Illiquide / Langläufer ohne Zweitmarkt | Kein Sekundärmarkt, Kapital bis zur Projektfertigstellung gebunden. |
| **SUMME** | **Rohscore (vor Mali)** | **57 / 100** | - | Theoretisches Maximum: 100 Pkt |

## 3. Malus-System (Strikte Risiko-Abschläge)

| Malus-Typ | Abzug | Auslöser / Kriterium | Beleg / Nachweis |
| :--- | :---: | :--- | :--- |
| **Monokultur-Malus** | `-6 Pkt` | Revest Group stellt 80.0 % des Portfolios (>50 %) | Hohe Klumpenbildung: Über 80.0 % Abhängigkeit von einem Garantiekonzern. |

## 4. Benchmark-Spiegel (Marktkonsens & Triangulierung)

| Externe Referenzquelle | Metrik / Wert | Interpretation |
| :--- | :---: | :--- |
| **re:think P2P Risk Score** | **N/A / 10** (Nicht gelistet) | Denny Neidhardt Sicherheitsranking  |
| **P2P Game Rating** | **38 / 100** (Platz 28 von 40) | Thomas P2P Rating (von 40 Plattformen) |
| **P2P Empire Safety Score** | **5.4 / 10** (Mittel) | Unabhängiger Testbericht Jakub Krejci |
| **P2P Empire Portfolio Performance** | **100.0 %** | Reale Rückzahlungsquote im Portfolio |
| **Lars Wrobbel / Passives Einkommen** | **Nicht gelistet** (N/A/40 Pkt) | Langzeit-Rating aus Community- & Blog-Erfahrung |

---
*Automatisch generiert durch das P2P Audit Scoring System am 2026-10-09.*