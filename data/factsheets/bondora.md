---
platform: bondora
platform_name: Bondora
audit_date: '2026-10-08'
audit_version: '1.0'
audit_score:
  net_score: 44
  raw_score: 59
  risk_class: SPECULATIVE
  portfolio_limit: 0 % (Neuanlage-Stopp)
  recommendation: 'Neuanlage-Stopp: Intransparenz, Holding-Konstrukte, Restrukturierungen
    oder Pending Payments.'
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
    score: 17
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
    score: 11
    max_score: 25
    band: Band_8_14
    rating: Unbesichert mit Buyback
    evidence: Konsumentenkredite mit strukturellen Ausfällen; Go & Grow puffert diese
      über Renditeabstand ab.
  pillar_4_liquidity:
    score: 9
    max_score: 25
    band: Band_6_12
    rating: Illiquide / Langläufer ohne Zweitmarkt
    evidence: Go & Grow verspricht tägliche Verfügbarkeit, behält sich jedoch vertraglich
      Teilabhebungen im Krisenfall vor.
malus_deductions:
- type: monoculture
  name: Monokultur-Malus
  penalty: -8
  trigger: Bondora AS stellt 100.0 % des Portfolios (>50 %)
  evidence: 'Hohe Klumpenbildung: Über 100.0 % Abhängigkeit von einem Garantiekonzern.'
- type: term_mismatch
  name: Fristen-Mismatch-Malus
  penalty: -7
  trigger: Tägliche Verfügbarkeit versprochen, aber durch langlaufende unbesicherte
    Konsumkredite (bis 5 Jahre) hinterlegt.
  evidence: Tägliche Verfügbarkeit versprochen, aber durch langlaufende unbesicherte
    Konsumkredite (bis 5 Jahre) hinterlegt.
sources:
- source_type: curated_profile
  path: data/platforms/bondora/profile.yaml
- source_type: erfahrungen
  path: data/erfahrungen/p2p-empire/bondora.md
---

# Platform Audit Factsheet: Bondora

**Audit-Datum:** 2026-10-08 | **Klasse:** `SPECULATIVE` | **Depot-Limit:** `0 % (Neuanlage-Stopp)`

## 1. Executive Summary & Audit-Verdict

> [!IMPORTANT]
> **Finaler Netto-Score:** **44 / 100 Punkte** (Rohscore: 59 Pkt | Malus-Abschläge: -15 Pkt)
> **Allokationsempfehlung:** Neuanlage-Stopp: Intransparenz, Holding-Konstrukte, Restrukturierungen oder Pending Payments.

## 2. Aufschlüsselung der 4 Säulen

| Säule | Kategorie | Punkte | Einstufung | Kern-Evidenz |
| :--- | :--- | :---: | :--- | :--- |
| **Säule 1** | Regulierung & Verwahrung | **17 / 25** | National reguliert | National lizenziert als Kreditgeber in Estland; kein Wertpapierinstitut, kein gesetzlicher 20k Entschädigungsschutz. |
| **Säule 2** | Solvenz & Governance | **22 / 25** | Sehr gut / Testiert | Konzernabschluss unabhängig durch KPMG testiert; solide Profitabilität. |
| **Säule 3** | Besicherung & Workout | **11 / 25** | Unbesichert mit Buyback | Konsumentenkredite mit strukturellen Ausfällen; Go & Grow puffert diese über Renditeabstand ab. |
| **Säule 4** | Liquidität & Zweitmarkt | **9 / 25** | Illiquide / Langläufer ohne Zweitmarkt | Go & Grow verspricht tägliche Verfügbarkeit, behält sich jedoch vertraglich Teilabhebungen im Krisenfall vor. |
| **SUMME** | **Rohscore (vor Mali)** | **59 / 100** | - | Theoretisches Maximum: 100 Pkt |

## 3. Malus-System (Strikte Risiko-Abschläge)

| Malus-Typ | Abzug | Auslöser / Kriterium | Beleg / Nachweis |
| :--- | :---: | :--- | :--- |
| **Monokultur-Malus** | `-8 Pkt` | Bondora AS stellt 100.0 % des Portfolios (>50 %) | Hohe Klumpenbildung: Über 100.0 % Abhängigkeit von einem Garantiekonzern. |
| **Fristen-Mismatch-Malus** | `-7 Pkt` | Tägliche Verfügbarkeit versprochen, aber durch langlaufende unbesicherte Konsumkredite (bis 5 Jahre) hinterlegt. | Tägliche Verfügbarkeit versprochen, aber durch langlaufende unbesicherte Konsumkredite (bis 5 Jahre) hinterlegt. |

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