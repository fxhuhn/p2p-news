---
platform: modena
platform_name: Modena
audit_date: '2026-10-07'
audit_version: '1.0'
audit_score:
  net_score: 56
  raw_score: 64
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
  rethink_p2p_score: 5.6
  rethink_p2p_rank: Platz 18
  rethink_p2p_red_flags: '0'
  p2p_game_score: 51
  p2p_game_rank: Platz 20 von 40
  p2p_empire_safety_score: 8.5
  p2p_empire_safety_band: Hoch
  p2p_empire_portfolio_perf: 100.0
  lars_wrobbel_score: null
  lars_wrobbel_rank: Kein Rating
pillars:
  pillar_1_regulation:
    score: 11
    max_score: 25
    band: Band_6_13
    rating: Unreguliert / Lizenzübergang
    evidence: Estnisches Fintech, unreguliert über Abtretungsverträge.
  pillar_2_solvency:
    score: 25
    max_score: 25
    band: Band_21_25
    rating: Sehr gut / Testiert
    evidence: Finanziell solide aufgestellt mit Fokus auf Mobilitätsfinanzierung.
  pillar_3_collateral:
    score: 17
    max_score: 25
    band: Band_15_20
    rating: Dinglich besichert (Mobiliar)
    evidence: Dinglich besichert über Fahrzeugpfandrechte im estnischen Verkehrsregister.
  pillar_4_liquidity:
    score: 11
    max_score: 25
    band: Band_6_12
    rating: Planbare Tilgung
    evidence: Kein Sekundärmarkt, planbare monatliche Leasing- und Tilgungsraten.
malus_deductions:
- type: monoculture
  name: Monokultur-Malus
  penalty: -8
  trigger: Modena Mobility OÜ stellt 100.0 % des Portfolios (>50 %)
  evidence: 'Hohe Klumpenbildung: Über 100.0 % Abhängigkeit von einem Garantiekonzern.'
sources:
- source_type: curated_profile
  path: data/platforms/modena/profile.yaml
- source_type: erfahrungen
  path: data/erfahrungen/p2p-empire/modena.md
---

# Platform Audit Factsheet: Modena

**Audit-Datum:** 2026-10-07 | **Klasse:** `WATCHLIST` | **Depot-Limit:** `0 - 3 %`

## 1. Executive Summary & Audit-Verdict

> [!IMPORTANT]
> **Finaler Netto-Score:** **56 / 100 Punkte** (Rohscore: 64 Pkt | Malus-Abschläge: -8 Pkt)
> **Allokationsempfehlung:** Taktische Position unter Vorbehalt: Schwächen bei LTV, fehlende Testate oder Governance-Risse.

## 2. Aufschlüsselung der 4 Säulen

| Säule | Kategorie | Punkte | Einstufung | Kern-Evidenz |
| :--- | :--- | :---: | :--- | :--- |
| **Säule 1** | Regulierung & Verwahrung | **11 / 25** | Unreguliert / Lizenzübergang | Estnisches Fintech, unreguliert über Abtretungsverträge. |
| **Säule 2** | Solvenz & Governance | **25 / 25** | Sehr gut / Testiert | Finanziell solide aufgestellt mit Fokus auf Mobilitätsfinanzierung. |
| **Säule 3** | Besicherung & Workout | **17 / 25** | Dinglich besichert (Mobiliar) | Dinglich besichert über Fahrzeugpfandrechte im estnischen Verkehrsregister. |
| **Säule 4** | Liquidität & Zweitmarkt | **11 / 25** | Planbare Tilgung | Kein Sekundärmarkt, planbare monatliche Leasing- und Tilgungsraten. |
| **SUMME** | **Rohscore (vor Mali)** | **64 / 100** | - | Theoretisches Maximum: 100 Pkt |

## 3. Malus-System (Strikte Risiko-Abschläge)

| Malus-Typ | Abzug | Auslöser / Kriterium | Beleg / Nachweis |
| :--- | :---: | :--- | :--- |
| **Monokultur-Malus** | `-8 Pkt` | Modena Mobility OÜ stellt 100.0 % des Portfolios (>50 %) | Hohe Klumpenbildung: Über 100.0 % Abhängigkeit von einem Garantiekonzern. |

## 4. Benchmark-Spiegel (Marktkonsens & Triangulierung)

| Externe Referenzquelle | Metrik / Wert | Interpretation |
| :--- | :---: | :--- |
| **re:think P2P Risk Score** | **5.6 / 10** (Platz 18) | Denny Neidhardt Sicherheitsranking (Red Flags: 0) |
| **P2P Game Rating** | **51 / 100** (Platz 20 von 40) | Thomas P2P Rating (von 40 Plattformen) |
| **P2P Empire Safety Score** | **8.5 / 10** (Hoch) | Unabhängiger Testbericht Jakub Krejci |
| **P2P Empire Portfolio Performance** | **100.0 %** | Reale Rückzahlungsquote im Portfolio |
| **Lars Wrobbel / Passives Einkommen** | **Kein Rating** (N/A/40 Pkt) | Langzeit-Rating aus Community- & Blog-Erfahrung |

---
*Automatisch generiert durch das P2P Audit Scoring System am 2026-10-07.*