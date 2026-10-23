---
platform: lendermarket
platform_name: Lendermarket
audit_date: '2026-10-23'
audit_version: '1.0'
audit_score:
  net_score: 22
  raw_score: 47
  risk_class: DISTRESSED
  portfolio_limit: 0 % (Kapitalabzug & Recovery)
  recommendation: 'Kapitalabzug & Workout: Notleidende Portfolios (NPL >40%), blockierte
    Zweitmärkte, Moratorien.'
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
  rethink_p2p_red_flags: '-12'
  p2p_game_score: 61
  p2p_game_rank: Platz 11 von 40
  p2p_empire_safety_score: 5.8
  p2p_empire_safety_band: Mittel
  p2p_empire_portfolio_perf: 78.0
  lars_wrobbel_score: null
  lars_wrobbel_rank: Nicht gelistet
  p2pdash_community_score: 57
  p2pdash_median_xirr: 17.2
  p2pdash_investors_count: 432
pillars:
  pillar_1_regulation:
    score: 8
    max_score: 25
    band: Band_6_13
    rating: Unreguliert (Abtretungsverträge)
    evidence: Unregulierter Marktplatz; keine Segregation durch lizenziertes Institut.
  pillar_2_solvency:
    score: 12
    max_score: 25
    band: Band_7_13
    rating: Befriedigend / Governance-Schwächen
    evidence: Chronische Pending Payments bei Creditstar-Krediten über viele Monate.
  pillar_3_collateral:
    score: 11
    max_score: 25
    band: Band_8_14
    rating: Unbesichert mit Buyback
    evidence: Rückkaufgarantie wurde in der Vergangenheit wiederholt ausgesetzt oder
      verzögert bedient.
  pillar_4_liquidity:
    score: 16
    max_score: 25
    band: Band_13_19
    rating: Gute Liquidität
    evidence: Sekundärmarkt vorhanden mit 180 Tagen Haltedauer; Auszahlungsstau bei
      fälligen Krediten (Pending Payments).
malus_deductions:
- type: monoculture
  name: Klumpen- & Konzentrations-Malus
  penalty: -5
  trigger: Creditstar Group AS stellt 65.0 % des Portfolios (>=30 %)
  evidence: 'Hohe Klumpenbildung: Über 65.0 % Abhängigkeit von einem Garantiekonzern
    oder Einzelschuldner.'
- type: related_party
  name: Related-Party- & Opazitäts-Malus
  penalty: -10
  trigger: Verflechtung zwischen Lendermarket-Betreibern und Creditstar Management.
  evidence: Verflechtung zwischen Lendermarket-Betreibern und Creditstar Management.
- type: cashflow_drag
  name: Cashflow- & Verzugs-Malus
  penalty: -10
  trigger: Laufende Verzugs-/NPL-Quote von 22.0 % (>=5 %)
  evidence: Cash Drag durch 22.0 % überfällige Kredite im Portfolio.
sources:
- source_type: curated_profile
  path: data/platforms/lendermarket/profile.yaml
- source_type: erfahrungen
  path: data/erfahrungen/p2p-empire/lendermarket.md
---

# Platform Audit Factsheet: Lendermarket

**Audit-Datum:** 2026-10-23 | **Klasse:** `DISTRESSED` | **Depot-Limit:** `0 % (Kapitalabzug & Recovery)`

## 1. Executive Summary & Audit-Verdict

> [!IMPORTANT]
> **Finaler Netto-Score:** **22 / 100 Punkte** (Rohscore: 47 Pkt | Malus-Abschläge: -25 Pkt)
> **Allokationsempfehlung:** Kapitalabzug & Workout: Notleidende Portfolios (NPL >40%), blockierte Zweitmärkte, Moratorien.

## 2. Aufschlüsselung der 4 Säulen

| Säule | Kategorie | Punkte | Einstufung | Kern-Evidenz |
| :--- | :--- | :---: | :--- | :--- |
| **Säule 1** | Regulierung & Verwahrung | **8 / 25** | Unreguliert (Abtretungsverträge) | Unregulierter Marktplatz; keine Segregation durch lizenziertes Institut. |
| **Säule 2** | Solvenz & Governance | **12 / 25** | Befriedigend / Governance-Schwächen | Chronische Pending Payments bei Creditstar-Krediten über viele Monate. |
| **Säule 3** | Besicherung & Workout | **11 / 25** | Unbesichert mit Buyback | Rückkaufgarantie wurde in der Vergangenheit wiederholt ausgesetzt oder verzögert bedient. |
| **Säule 4** | Liquidität & Zweitmarkt | **16 / 25** | Gute Liquidität | Sekundärmarkt vorhanden mit 180 Tagen Haltedauer; Auszahlungsstau bei fälligen Krediten (Pending Payments). |
| **SUMME** | **Rohscore (vor Mali)** | **47 / 100** | - | Theoretisches Maximum: 100 Pkt |

## 3. Malus-System (Strikte Risiko-Abschläge)

| Malus-Typ | Abzug | Auslöser / Kriterium | Beleg / Nachweis |
| :--- | :---: | :--- | :--- |
| **Klumpen- & Konzentrations-Malus** | `-5 Pkt` | Creditstar Group AS stellt 65.0 % des Portfolios (>=30 %) | Hohe Klumpenbildung: Über 65.0 % Abhängigkeit von einem Garantiekonzern oder Einzelschuldner. |
| **Related-Party- & Opazitäts-Malus** | `-10 Pkt` | Verflechtung zwischen Lendermarket-Betreibern und Creditstar Management. | Verflechtung zwischen Lendermarket-Betreibern und Creditstar Management. |
| **Cashflow- & Verzugs-Malus** | `-10 Pkt` | Laufende Verzugs-/NPL-Quote von 22.0 % (>=5 %) | Cash Drag durch 22.0 % überfällige Kredite im Portfolio. |

## 4. Benchmark-Spiegel (Marktkonsens & Triangulierung)

| Externe Referenzquelle | Metrik / Wert | Interpretation |
| :--- | :---: | :--- |
| **re:think P2P Risk Score** | **6.4 / 10** (Platz 8) | Denny Neidhardt Sicherheitsranking (Red Flags: -12) |
| **P2P Game Rating** | **61 / 100** (Platz 11 von 40) | Thomas P2P Rating (von 40 Plattformen) |
| **P2P Empire Safety Score** | **5.8 / 10** (Mittel) | Unabhängiger Testbericht Jakub Krejci |
| **P2P Empire Portfolio Performance** | **78.0 %** | Reale Rückzahlungsquote im Portfolio |
| **Lars Wrobbel / Passives Einkommen** | **Nicht gelistet** (N/A/40 Pkt) | Langzeit-Rating aus Community- & Blog-Erfahrung |
| **P2P Dash Community Score** | **57 / 100** (17.2 % XIRR) | 432 Investoren (Empirischer Schwarm-Score) |

---
*Automatisch generiert durch das P2P Audit Scoring System am 2026-10-23.*