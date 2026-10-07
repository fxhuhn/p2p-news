---
platform: peerberry
platform_name: PeerBerry
audit_date: '2026-10-07'
audit_version: '1.0'
audit_score:
  net_score: 58
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
  rethink_p2p_score: 7.6
  rethink_p2p_rank: Platz 5
  rethink_p2p_red_flags: '0'
  p2p_game_score: 44
  p2p_game_rank: Platz 23 von 40
  p2p_empire_safety_score: 8.8
  p2p_empire_safety_band: Hoch
  p2p_empire_portfolio_perf: 100.0
  lars_wrobbel_score: 30
  lars_wrobbel_rank: Rang 5
pillars:
  pillar_1_regulation:
    score: 11
    max_score: 25
    band: Band_6_13
    rating: Unreguliert (Abtretungsverträge)
    evidence: Unreguliert über Kroatien/Litauen, aber getrennt geführte Bankkonten.
  pillar_2_solvency:
    score: 25
    max_score: 25
    band: Band_21_25
    rating: Sehr gut / Testiert
    evidence: Wirtschaftlich getragen durch hochprofitable Aventus Group. 100 % Rückzahlung
      aller Kriegs-Kredite (Ukraine/Russland) bis Ende 2024 ohne Anlegerverlust.
  pillar_3_collateral:
    score: 14
    max_score: 25
    band: Band_8_14
    rating: Unbesichert mit Buyback
    evidence: 0 % Kapitalverlust über 8 Jahre Geschäftsbetrieb trotz Krisen.
  pillar_4_liquidity:
    score: 16
    max_score: 25
    band: Band_13_19
    rating: Gute Liquidität
    evidence: Sehr kurze originäre Kreditlaufzeiten (<30-60 Tage). Sekundärmarkt mit
      6 Monaten Haltedauer.
malus_deductions:
- type: monoculture
  name: Monokultur-Malus
  penalty: -8
  trigger: Aventus Group stellt 88.0 % des Portfolios (>50 %)
  evidence: 'Hohe Klumpenbildung: Über 88.0 % Abhängigkeit von einem Garantiekonzern.'
sources:
- source_type: curated_profile
  path: data/platforms/peerberry/profile.yaml
- source_type: erfahrungen
  path: data/erfahrungen/p2p-empire/peerberry.md
---

# Platform Audit Factsheet: PeerBerry

**Audit-Datum:** 2026-10-07 | **Klasse:** `WATCHLIST` | **Depot-Limit:** `0 - 3 %`

## 1. Executive Summary & Audit-Verdict

> [!IMPORTANT]
> **Finaler Netto-Score:** **58 / 100 Punkte** (Rohscore: 66 Pkt | Malus-Abschläge: -8 Pkt)
> **Allokationsempfehlung:** Taktische Position unter Vorbehalt: Schwächen bei LTV, fehlende Testate oder Governance-Risse.

## 2. Aufschlüsselung der 4 Säulen

| Säule | Kategorie | Punkte | Einstufung | Kern-Evidenz |
| :--- | :--- | :---: | :--- | :--- |
| **Säule 1** | Regulierung & Verwahrung | **11 / 25** | Unreguliert (Abtretungsverträge) | Unreguliert über Kroatien/Litauen, aber getrennt geführte Bankkonten. |
| **Säule 2** | Solvenz & Governance | **25 / 25** | Sehr gut / Testiert | Wirtschaftlich getragen durch hochprofitable Aventus Group. 100 % Rückzahlung aller Kriegs-Kredite (Ukraine/Russland) bis Ende 2024 ohne Anlegerverlust. |
| **Säule 3** | Besicherung & Workout | **14 / 25** | Unbesichert mit Buyback | 0 % Kapitalverlust über 8 Jahre Geschäftsbetrieb trotz Krisen. |
| **Säule 4** | Liquidität & Zweitmarkt | **16 / 25** | Gute Liquidität | Sehr kurze originäre Kreditlaufzeiten (<30-60 Tage). Sekundärmarkt mit 6 Monaten Haltedauer. |
| **SUMME** | **Rohscore (vor Mali)** | **66 / 100** | - | Theoretisches Maximum: 100 Pkt |

## 3. Malus-System (Strikte Risiko-Abschläge)

| Malus-Typ | Abzug | Auslöser / Kriterium | Beleg / Nachweis |
| :--- | :---: | :--- | :--- |
| **Monokultur-Malus** | `-8 Pkt` | Aventus Group stellt 88.0 % des Portfolios (>50 %) | Hohe Klumpenbildung: Über 88.0 % Abhängigkeit von einem Garantiekonzern. |

## 4. Benchmark-Spiegel (Marktkonsens & Triangulierung)

| Externe Referenzquelle | Metrik / Wert | Interpretation |
| :--- | :---: | :--- |
| **re:think P2P Risk Score** | **7.6 / 10** (Platz 5) | Denny Neidhardt Sicherheitsranking (Red Flags: 0) |
| **P2P Game Rating** | **44 / 100** (Platz 23 von 40) | Thomas P2P Rating (von 40 Plattformen) |
| **P2P Empire Safety Score** | **8.8 / 10** (Hoch) | Unabhängiger Testbericht Jakub Krejci |
| **P2P Empire Portfolio Performance** | **100.0 %** | Reale Rückzahlungsquote im Portfolio |
| **Lars Wrobbel / Passives Einkommen** | **Rang 5** (30/40 Pkt) | Langzeit-Rating aus Community- & Blog-Erfahrung |

---
*Automatisch generiert durch das P2P Audit Scoring System am 2026-10-07.*