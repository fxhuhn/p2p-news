---
platform: debitum
platform_name: Debitum Investments
audit_date: '2026-10-21'
audit_version: '1.0'
audit_score:
  net_score: 55
  raw_score: 66
  risk_class: WATCHLIST
  portfolio_limit: 0 - 3 %
  recommendation: 'Taktische Position unter Vorbehalt: Schwächen bei LTV, fehlende
    Testate oder Governance-Risse.'
flags:
  has_conflict: true
  conflict_notes:
  - 'NPL-Diskrepanz: Profil weist 8.5 % NPL aus, Benchmark-Performance indiziert 15.0
    % Rückstand.'
  data_gaps: []
evidence_metadata:
  sourcing_strategy: curated_profile_and_secondary_audits
  primary_crawled_pages: 4
  curated_profile_used: true
  secondary_reviews_count: 2
benchmarks:
  rethink_p2p_score: 6.0
  rethink_p2p_rank: Platz 14
  rethink_p2p_red_flags: '-19'
  p2p_game_score: 61
  p2p_game_rank: Platz 12 von 40
  p2p_empire_safety_score: 3.9
  p2p_empire_safety_band: Niedrig
  p2p_empire_portfolio_perf: 85.0
  lars_wrobbel_score: 31
  lars_wrobbel_rank: Rang 7
  p2pdash_community_score: 65
  p2pdash_median_xirr: 15.3
  p2pdash_investors_count: 928
pillars:
  pillar_1_regulation:
    score: 25
    max_score: 25
    band: Band_21_25
    rating: MiFID II / IBF lizenziert
    evidence: Voll lizenzierte Wertpapierfirma (IBF) unter Aufsicht der Latvijas Banka
      mit Anlegerentschädigungsschutz.
  pillar_2_solvency:
    score: 19
    max_score: 25
    band: Band_21_25
    rating: Sehr gut / Testiert
    evidence: Holding-Governance mit Belastungen durch Related-Party Transaktionen.
  pillar_3_collateral:
    score: 11
    max_score: 25
    band: Band_8_14
    rating: Unbesichert mit Buyback
    evidence: Teils dinglich besichert (z. B. Forest/Sando Kredite), teils Handelsforderungen.
  pillar_4_liquidity:
    score: 11
    max_score: 25
    band: Band_6_12
    rating: Planbare Tilgung
    evidence: Kein Sekundärmarkt vorhanden. Kapital über 6 bis 60 Monate gebunden.
malus_deductions:
- type: monoculture
  name: Klumpen- & Konzentrations-Malus
  penalty: -3
  trigger: Hauptkreditgeber stellt 45.0 % des Portfolios (>=30 %)
  evidence: 'Hohe Klumpenbildung: Über 45.0 % Abhängigkeit von einem Garantiekonzern
    oder Einzelschuldner.'
- type: related_party
  name: Related-Party- & Opazitäts-Malus
  penalty: -5
  trigger: 'LFDF-Konstrukt: Verflechtungen im Gesellschafterkreis und konzerninterne
    Transaktionen; aufsichtsrechtlich durch Latvijas Banka überwacht.'
  evidence: 'LFDF-Konstrukt: Verflechtungen im Gesellschafterkreis und konzerninterne
    Transaktionen; aufsichtsrechtlich durch Latvijas Banka überwacht.'
- type: cashflow_drag
  name: Cashflow- & Verzugs-Malus
  penalty: -3
  trigger: Laufende Verzugs-/NPL-Quote von 8.5 % (>=5 %)
  evidence: Cash Drag durch 8.5 % überfällige Kredite im Portfolio.
sources:
- source_type: curated_profile
  path: data/platforms/debitum/profile.yaml
- source_type: erfahrungen
  path: data/erfahrungen/p2p-empire/debitum.md
---

# Platform Audit Factsheet: Debitum Investments

**Audit-Datum:** 2026-10-21 | **Klasse:** `WATCHLIST` | **Depot-Limit:** `0 - 3 %`

## 1. Executive Summary & Audit-Verdict

> [!IMPORTANT]
> **Finaler Netto-Score:** **55 / 100 Punkte** (Rohscore: 66 Pkt | Malus-Abschläge: -11 Pkt)
> **Allokationsempfehlung:** Taktische Position unter Vorbehalt: Schwächen bei LTV, fehlende Testate oder Governance-Risse.

> [!WARNING]
> **Achtung - Widersprüchliche Angaben identifiziert:**
> • NPL-Diskrepanz: Profil weist 8.5 % NPL aus, Benchmark-Performance indiziert 15.0 % Rückstand.

## 2. Aufschlüsselung der 4 Säulen

| Säule | Kategorie | Punkte | Einstufung | Kern-Evidenz |
| :--- | :--- | :---: | :--- | :--- |
| **Säule 1** | Regulierung & Verwahrung | **25 / 25** | MiFID II / IBF lizenziert | Voll lizenzierte Wertpapierfirma (IBF) unter Aufsicht der Latvijas Banka mit Anlegerentschädigungsschutz. |
| **Säule 2** | Solvenz & Governance | **19 / 25** | Sehr gut / Testiert | Holding-Governance mit Belastungen durch Related-Party Transaktionen. |
| **Säule 3** | Besicherung & Workout | **11 / 25** | Unbesichert mit Buyback | Teils dinglich besichert (z. B. Forest/Sando Kredite), teils Handelsforderungen. |
| **Säule 4** | Liquidität & Zweitmarkt | **11 / 25** | Planbare Tilgung | Kein Sekundärmarkt vorhanden. Kapital über 6 bis 60 Monate gebunden. |
| **SUMME** | **Rohscore (vor Mali)** | **66 / 100** | - | Theoretisches Maximum: 100 Pkt |

## 3. Malus-System (Strikte Risiko-Abschläge)

| Malus-Typ | Abzug | Auslöser / Kriterium | Beleg / Nachweis |
| :--- | :---: | :--- | :--- |
| **Klumpen- & Konzentrations-Malus** | `-3 Pkt` | Hauptkreditgeber stellt 45.0 % des Portfolios (>=30 %) | Hohe Klumpenbildung: Über 45.0 % Abhängigkeit von einem Garantiekonzern oder Einzelschuldner. |
| **Related-Party- & Opazitäts-Malus** | `-5 Pkt` | LFDF-Konstrukt: Verflechtungen im Gesellschafterkreis und konzerninterne Transaktionen; aufsichtsrechtlich durch Latvijas Banka überwacht. | LFDF-Konstrukt: Verflechtungen im Gesellschafterkreis und konzerninterne Transaktionen; aufsichtsrechtlich durch Latvijas Banka überwacht. |
| **Cashflow- & Verzugs-Malus** | `-3 Pkt` | Laufende Verzugs-/NPL-Quote von 8.5 % (>=5 %) | Cash Drag durch 8.5 % überfällige Kredite im Portfolio. |

## 4. Benchmark-Spiegel (Marktkonsens & Triangulierung)

| Externe Referenzquelle | Metrik / Wert | Interpretation |
| :--- | :---: | :--- |
| **re:think P2P Risk Score** | **6.0 / 10** (Platz 14) | Denny Neidhardt Sicherheitsranking (Red Flags: -19) |
| **P2P Game Rating** | **61 / 100** (Platz 12 von 40) | Thomas P2P Rating (von 40 Plattformen) |
| **P2P Empire Safety Score** | **3.9 / 10** (Niedrig) | Unabhängiger Testbericht Jakub Krejci |
| **P2P Empire Portfolio Performance** | **85.0 %** | Reale Rückzahlungsquote im Portfolio |
| **Lars Wrobbel / Passives Einkommen** | **Rang 7** (31/40 Pkt) | Langzeit-Rating aus Community- & Blog-Erfahrung |
| **P2P Dash Community Score** | **65 / 100** (15.3 % XIRR) | 928 Investoren (Empirischer Schwarm-Score) |

---
*Automatisch generiert durch das P2P Audit Scoring System am 2026-10-21.*