---
platform: debitum
platform_name: Debitum Investments
audit_date: '2026-10-07'
audit_version: '1.0'
audit_score:
  net_score: 51
  raw_score: 68
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
  rethink_p2p_score: 6.0
  rethink_p2p_rank: Platz 14
  rethink_p2p_red_flags: '-19'
  p2p_game_score: 61
  p2p_game_rank: Platz 12 von 40
  p2p_empire_safety_score: 3.9
  p2p_empire_safety_band: Niedrig
  p2p_empire_portfolio_perf: 85.0
  lars_wrobbel_score: 31
  lars_wrobbel_rank: Rang 4
pillars:
  pillar_1_regulation:
    score: 25
    max_score: 25
    band: Band_21_25
    rating: MiFID II / IBF lizenziert
    evidence: Voll lizenzierte Wertpapierfirma (IBF) unter Aufsicht der Latvijas Banka
      mit Anlegerentschädigungsschutz.
  pillar_2_solvency:
    score: 21
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
- type: term_mismatch
  name: Fristen-Mismatch-Malus
  penalty: -7
  trigger: Debitum Flow verspricht flexible Liquidität bei 8 % Zins, ist aber durch
    5-jährige illiquide Notes mit 75 % Zuflussabhängigkeit hinterlegt.
  evidence: Debitum Flow verspricht flexible Liquidität bei 8 % Zins, ist aber durch
    5-jährige illiquide Notes mit 75 % Zuflussabhängigkeit hinterlegt.
- type: related_party
  name: Related-Party- & Opazitäts-Malus
  penalty: -10
  trigger: 'LFDF-Konstrukt: 81 % Käufe aus Familiennetzwerk mit ~50 % Aufschlag, unabhängige
    Gutachten verweigert.'
  evidence: 'LFDF-Konstrukt: 81 % Käufe aus Familiennetzwerk mit ~50 % Aufschlag,
    unabhängige Gutachten verweigert.'
sources:
- source_type: curated_profile
  path: data/platforms/debitum/profile.yaml
- source_type: erfahrungen
  path: data/erfahrungen/p2p-empire/debitum.md
---

# Platform Audit Factsheet: Debitum Investments

**Audit-Datum:** 2026-10-07 | **Klasse:** `WATCHLIST` | **Depot-Limit:** `0 - 3 %`

## 1. Executive Summary & Audit-Verdict

> [!IMPORTANT]
> **Finaler Netto-Score:** **51 / 100 Punkte** (Rohscore: 68 Pkt | Malus-Abschläge: -17 Pkt)
> **Allokationsempfehlung:** Taktische Position unter Vorbehalt: Schwächen bei LTV, fehlende Testate oder Governance-Risse.

## 2. Aufschlüsselung der 4 Säulen

| Säule | Kategorie | Punkte | Einstufung | Kern-Evidenz |
| :--- | :--- | :---: | :--- | :--- |
| **Säule 1** | Regulierung & Verwahrung | **25 / 25** | MiFID II / IBF lizenziert | Voll lizenzierte Wertpapierfirma (IBF) unter Aufsicht der Latvijas Banka mit Anlegerentschädigungsschutz. |
| **Säule 2** | Solvenz & Governance | **21 / 25** | Sehr gut / Testiert | Holding-Governance mit Belastungen durch Related-Party Transaktionen. |
| **Säule 3** | Besicherung & Workout | **11 / 25** | Unbesichert mit Buyback | Teils dinglich besichert (z. B. Forest/Sando Kredite), teils Handelsforderungen. |
| **Säule 4** | Liquidität & Zweitmarkt | **11 / 25** | Planbare Tilgung | Kein Sekundärmarkt vorhanden. Kapital über 6 bis 60 Monate gebunden. |
| **SUMME** | **Rohscore (vor Mali)** | **68 / 100** | - | Theoretisches Maximum: 100 Pkt |

## 3. Malus-System (Strikte Risiko-Abschläge)

| Malus-Typ | Abzug | Auslöser / Kriterium | Beleg / Nachweis |
| :--- | :---: | :--- | :--- |
| **Fristen-Mismatch-Malus** | `-7 Pkt` | Debitum Flow verspricht flexible Liquidität bei 8 % Zins, ist aber durch 5-jährige illiquide Notes mit 75 % Zuflussabhängigkeit hinterlegt. | Debitum Flow verspricht flexible Liquidität bei 8 % Zins, ist aber durch 5-jährige illiquide Notes mit 75 % Zuflussabhängigkeit hinterlegt. |
| **Related-Party- & Opazitäts-Malus** | `-10 Pkt` | LFDF-Konstrukt: 81 % Käufe aus Familiennetzwerk mit ~50 % Aufschlag, unabhängige Gutachten verweigert. | LFDF-Konstrukt: 81 % Käufe aus Familiennetzwerk mit ~50 % Aufschlag, unabhängige Gutachten verweigert. |

## 4. Benchmark-Spiegel (Marktkonsens & Triangulierung)

| Externe Referenzquelle | Metrik / Wert | Interpretation |
| :--- | :---: | :--- |
| **re:think P2P Risk Score** | **6.0 / 10** (Platz 14) | Denny Neidhardt Sicherheitsranking (Red Flags: -19) |
| **P2P Game Rating** | **61 / 100** (Platz 12 von 40) | Thomas P2P Rating (von 40 Plattformen) |
| **P2P Empire Safety Score** | **3.9 / 10** (Niedrig) | Unabhängiger Testbericht Jakub Krejci |
| **P2P Empire Portfolio Performance** | **85.0 %** | Reale Rückzahlungsquote im Portfolio |
| **Lars Wrobbel / Passives Einkommen** | **Rang 4** (31/40 Pkt) | Langzeit-Rating aus Community- & Blog-Erfahrung |

---
*Automatisch generiert durch das P2P Audit Scoring System am 2026-10-07.*