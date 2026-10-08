---
platform: debitum
platform_name: Debitum Investments
audit_date: '2026-10-08'
audit_version: '1.0'
audit_score:
  net_score: 61
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
- type: related_party
  name: Related-Party- & Opazitäts-Malus
  penalty: -5
  trigger: 'LFDF-Konstrukt: Verflechtungen im Gesellschafterkreis und konzerninterne
    Transaktionen; aufsichtsrechtlich durch Latvijas Banka überwacht.'
  evidence: 'LFDF-Konstrukt: Verflechtungen im Gesellschafterkreis und konzerninterne
    Transaktionen; aufsichtsrechtlich durch Latvijas Banka überwacht.'
sources:
- source_type: curated_profile
  path: data/platforms/debitum/profile.yaml
- source_type: erfahrungen
  path: data/erfahrungen/p2p-empire/debitum.md
---

# Platform Audit Factsheet: Debitum Investments

**Audit-Datum:** 2026-10-08 | **Klasse:** `MID RISK` | **Depot-Limit:** `5 - 8 %`

## 1. Executive Summary & Audit-Verdict

> [!IMPORTANT]
> **Finaler Netto-Score:** **61 / 100 Punkte** (Rohscore: 66 Pkt | Malus-Abschläge: -5 Pkt)
> **Allokationsempfehlung:** Solide Beimischung: Hohe Bonität/Historie, aber unbesicherte Konsumkredite oder Monokulturen.

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
| **Related-Party- & Opazitäts-Malus** | `-5 Pkt` | LFDF-Konstrukt: Verflechtungen im Gesellschafterkreis und konzerninterne Transaktionen; aufsichtsrechtlich durch Latvijas Banka überwacht. | LFDF-Konstrukt: Verflechtungen im Gesellschafterkreis und konzerninterne Transaktionen; aufsichtsrechtlich durch Latvijas Banka überwacht. |

## 4. Benchmark-Spiegel (Marktkonsens & Triangulierung)

| Externe Referenzquelle | Metrik / Wert | Interpretation |
| :--- | :---: | :--- |
| **re:think P2P Risk Score** | **6.0 / 10** (Platz 14) | Denny Neidhardt Sicherheitsranking (Red Flags: -19) |
| **P2P Game Rating** | **61 / 100** (Platz 12 von 40) | Thomas P2P Rating (von 40 Plattformen) |
| **P2P Empire Safety Score** | **3.9 / 10** (Niedrig) | Unabhängiger Testbericht Jakub Krejci |
| **P2P Empire Portfolio Performance** | **85.0 %** | Reale Rückzahlungsquote im Portfolio |
| **Lars Wrobbel / Passives Einkommen** | **Rang 7** (31/40 Pkt) | Langzeit-Rating aus Community- & Blog-Erfahrung |

---
*Automatisch generiert durch das P2P Audit Scoring System am 2026-10-08.*