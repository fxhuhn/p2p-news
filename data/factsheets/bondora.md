---
platform: bondora
platform_name: Bondora
audit_date: '2026-10-08'
audit_version: '1.0'
audit_score:
  net_score: 61
  raw_score: 67
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
  rethink_p2p_score: 5.5
  rethink_p2p_rank: Platz 19
  rethink_p2p_red_flags: '0'
  p2p_game_score: 64
  p2p_game_rank: Platz 10 von 40
  p2p_empire_safety_score: 6.9
  p2p_empire_safety_band: Mittel
  p2p_empire_portfolio_perf: 72.6
  lars_wrobbel_score: 25
  lars_wrobbel_rank: Rang 9
pillars:
  pillar_1_regulation:
    score: 14
    max_score: 25
    band: Band_14_20
    rating: National reguliert
    evidence: National lizenziert als Kreditgeber in Estland; kein Wertpapierinstitut,
      kein gesetzlicher 20k Entschädigungsschutz.
  pillar_2_solvency:
    score: 22
    max_score: 25
    band: Band_21_25
    rating: Sehr gut / Testiert
    evidence: Konzernabschluss unabhängig durch KPMG testiert; solide Profitabilität.
  pillar_3_collateral:
    score: 13
    max_score: 25
    band: Band_8_14
    rating: Unbesichert mit Buyback
    evidence: Konsumentenkredite mit statistischer Streuung über >100.000 Einzeldarlehen;
      Go & Grow puffert Ausfälle über den Renditeabstand und interne Reserven ab.
  pillar_4_liquidity:
    score: 18
    max_score: 25
    band: Band_13_19
    rating: Hohe Alltagsliquidität (Reserve-Pool)
    evidence: Go & Grow Reserve-Pool bietet im Normalbetrieb tägliche Verfügbarkeit;
      vertragliche Teilauszahlungsklausel (Partial Payouts) als Sicherheitsventil
      im Krisenfall.
malus_deductions:
- type: term_mismatch
  name: Fristen-Mismatch-Malus
  penalty: -6
  trigger: Tägliche Verfügbarkeit im Go & Grow Pool trifft auf mehrjährige Konsumkreditlaufzeiten
    (Fristentransformation mit Teilauszahlungsrisiko).
  evidence: Tägliche Verfügbarkeit im Go & Grow Pool trifft auf mehrjährige Konsumkreditlaufzeiten
    (Fristentransformation mit Teilauszahlungsrisiko).
sources:
- source_type: curated_profile
  path: data/platforms/bondora/profile.yaml
- source_type: erfahrungen
  path: data/erfahrungen/p2p-empire/bondora.md
---

# Platform Audit Factsheet: Bondora

**Audit-Datum:** 2026-10-08 | **Klasse:** `MID RISK` | **Depot-Limit:** `5 - 8 %`

## 1. Executive Summary & Audit-Verdict

> [!IMPORTANT]
> **Finaler Netto-Score:** **61 / 100 Punkte** (Rohscore: 67 Pkt | Malus-Abschläge: -6 Pkt)
> **Allokationsempfehlung:** Solide Beimischung: Hohe Bonität/Historie, aber unbesicherte Konsumkredite oder Monokulturen.

## 2. Aufschlüsselung der 4 Säulen

| Säule | Kategorie | Punkte | Einstufung | Kern-Evidenz |
| :--- | :--- | :---: | :--- | :--- |
| **Säule 1** | Regulierung & Verwahrung | **14 / 25** | National reguliert | National lizenziert als Kreditgeber in Estland; kein Wertpapierinstitut, kein gesetzlicher 20k Entschädigungsschutz. |
| **Säule 2** | Solvenz & Governance | **22 / 25** | Sehr gut / Testiert | Konzernabschluss unabhängig durch KPMG testiert; solide Profitabilität. |
| **Säule 3** | Besicherung & Workout | **13 / 25** | Unbesichert mit Buyback | Konsumentenkredite mit statistischer Streuung über >100.000 Einzeldarlehen; Go & Grow puffert Ausfälle über den Renditeabstand und interne Reserven ab. |
| **Säule 4** | Liquidität & Zweitmarkt | **18 / 25** | Hohe Alltagsliquidität (Reserve-Pool) | Go & Grow Reserve-Pool bietet im Normalbetrieb tägliche Verfügbarkeit; vertragliche Teilauszahlungsklausel (Partial Payouts) als Sicherheitsventil im Krisenfall. |
| **SUMME** | **Rohscore (vor Mali)** | **67 / 100** | - | Theoretisches Maximum: 100 Pkt |

## 3. Malus-System (Strikte Risiko-Abschläge)

| Malus-Typ | Abzug | Auslöser / Kriterium | Beleg / Nachweis |
| :--- | :---: | :--- | :--- |
| **Fristen-Mismatch-Malus** | `-6 Pkt` | Tägliche Verfügbarkeit im Go & Grow Pool trifft auf mehrjährige Konsumkreditlaufzeiten (Fristentransformation mit Teilauszahlungsrisiko). | Tägliche Verfügbarkeit im Go & Grow Pool trifft auf mehrjährige Konsumkreditlaufzeiten (Fristentransformation mit Teilauszahlungsrisiko). |

## 4. Benchmark-Spiegel (Marktkonsens & Triangulierung)

| Externe Referenzquelle | Metrik / Wert | Interpretation |
| :--- | :---: | :--- |
| **re:think P2P Risk Score** | **5.5 / 10** (Platz 19) | Denny Neidhardt Sicherheitsranking (Red Flags: 0) |
| **P2P Game Rating** | **64 / 100** (Platz 10 von 40) | Thomas P2P Rating (von 40 Plattformen) |
| **P2P Empire Safety Score** | **6.9 / 10** (Mittel) | Unabhängiger Testbericht Jakub Krejci |
| **P2P Empire Portfolio Performance** | **72.6 %** | Reale Rückzahlungsquote im Portfolio |
| **Lars Wrobbel / Passives Einkommen** | **Rang 9** (25/40 Pkt) | Langzeit-Rating aus Community- & Blog-Erfahrung |

---
*Automatisch generiert durch das P2P Audit Scoring System am 2026-10-08.*