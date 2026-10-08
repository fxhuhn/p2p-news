---
platform: loanch
platform_name: Loanch
audit_date: '2026-10-08'
audit_version: '1.0'
audit_score:
  net_score: 47
  raw_score: 51
  risk_class: SPECULATIVE
  portfolio_limit: 0 % (Neuanlage-Stopp)
  recommendation: 'Neuanlage-Stopp: Intransparenz, Holding-Konstrukte, Restrukturierungen
    oder Pending Payments.'
flags:
  has_conflict: false
  conflict_notes: []
  data_gaps:
  - Keine unabhängig testierten Finanzberichte auffindbar (Säule 2 auf Minimalwert
    gesetzt).
evidence_metadata:
  sourcing_strategy: curated_profile_and_secondary_audits
  primary_crawled_pages: 4
  curated_profile_used: true
  secondary_reviews_count: 2
benchmarks:
  rethink_p2p_score: 3.9
  rethink_p2p_rank: Platz 25
  rethink_p2p_red_flags: '-10'
  p2p_game_score: 38
  p2p_game_rank: Platz 27 von 40
  p2p_empire_safety_score: 0.0
  p2p_empire_safety_band: Niedrig
  p2p_empire_portfolio_perf: 90.0
  lars_wrobbel_score: null
  lars_wrobbel_rank: Nicht gelistet
pillars:
  pillar_1_regulation:
    score: 8
    max_score: 25
    band: Band_6_13
    rating: Unreguliert (Abtretungsverträge)
    evidence: Unregulierter Marktplatz.
  pillar_2_solvency:
    score: 3
    max_score: 25
    band: Band_0_6
    rating: Keine testierten Finanzberichte
    evidence: Keine testierten Finanzberichte vorhanden (Vorsichtsprinzip).
  pillar_3_collateral:
    score: 16
    max_score: 25
    band: Band_8_14
    rating: Unbesichert mit Buyback
    evidence: Unbesicherte Kredite in Schwellenländern mit Währungsrisiko.
  pillar_4_liquidity:
    score: 24
    max_score: 25
    band: Band_20_25
    rating: Sehr liquide / Kurzläufer & Zweitmarkt
    evidence: Kurzläufer-Kredite mit gebührenfreiem Sekundärmarkt.
malus_deductions:
- type: monoculture
  name: Monokultur-Malus
  penalty: -4
  trigger: Hauptanbahner stellt 60.0 % des Portfolios (>50 %)
  evidence: 'Hohe Klumpenbildung: Über 60.0 % Abhängigkeit von einem Garantiekonzern.'
sources:
- source_type: curated_profile
  path: data/platforms/loanch/profile.yaml
- source_type: erfahrungen
  path: data/erfahrungen/p2p-empire/loanch.md
---

# Platform Audit Factsheet: Loanch

**Audit-Datum:** 2026-10-08 | **Klasse:** `SPECULATIVE` | **Depot-Limit:** `0 % (Neuanlage-Stopp)`

## 1. Executive Summary & Audit-Verdict

> [!IMPORTANT]
> **Finaler Netto-Score:** **47 / 100 Punkte** (Rohscore: 51 Pkt | Malus-Abschläge: -4 Pkt)
> **Allokationsempfehlung:** Neuanlage-Stopp: Intransparenz, Holding-Konstrukte, Restrukturierungen oder Pending Payments.

> [!NOTE]
> **Vorsichtsprinzip bei Datenlücken aktiv:**
> • Keine unabhängig testierten Finanzberichte auffindbar (Säule 2 auf Minimalwert gesetzt).

## 2. Aufschlüsselung der 4 Säulen

| Säule | Kategorie | Punkte | Einstufung | Kern-Evidenz |
| :--- | :--- | :---: | :--- | :--- |
| **Säule 1** | Regulierung & Verwahrung | **8 / 25** | Unreguliert (Abtretungsverträge) | Unregulierter Marktplatz. |
| **Säule 2** | Solvenz & Governance | **3 / 25** | Keine testierten Finanzberichte | Keine testierten Finanzberichte vorhanden (Vorsichtsprinzip). |
| **Säule 3** | Besicherung & Workout | **16 / 25** | Unbesichert mit Buyback | Unbesicherte Kredite in Schwellenländern mit Währungsrisiko. |
| **Säule 4** | Liquidität & Zweitmarkt | **24 / 25** | Sehr liquide / Kurzläufer & Zweitmarkt | Kurzläufer-Kredite mit gebührenfreiem Sekundärmarkt. |
| **SUMME** | **Rohscore (vor Mali)** | **51 / 100** | - | Theoretisches Maximum: 100 Pkt |

## 3. Malus-System (Strikte Risiko-Abschläge)

| Malus-Typ | Abzug | Auslöser / Kriterium | Beleg / Nachweis |
| :--- | :---: | :--- | :--- |
| **Monokultur-Malus** | `-4 Pkt` | Hauptanbahner stellt 60.0 % des Portfolios (>50 %) | Hohe Klumpenbildung: Über 60.0 % Abhängigkeit von einem Garantiekonzern. |

## 4. Benchmark-Spiegel (Marktkonsens & Triangulierung)

| Externe Referenzquelle | Metrik / Wert | Interpretation |
| :--- | :---: | :--- |
| **re:think P2P Risk Score** | **3.9 / 10** (Platz 25) | Denny Neidhardt Sicherheitsranking (Red Flags: -10) |
| **P2P Game Rating** | **38 / 100** (Platz 27 von 40) | Thomas P2P Rating (von 40 Plattformen) |
| **P2P Empire Safety Score** | **0.0 / 10** (Niedrig) | Unabhängiger Testbericht Jakub Krejci |
| **P2P Empire Portfolio Performance** | **90.0 %** | Reale Rückzahlungsquote im Portfolio |
| **Lars Wrobbel / Passives Einkommen** | **Nicht gelistet** (N/A/40 Pkt) | Langzeit-Rating aus Community- & Blog-Erfahrung |

---
*Automatisch generiert durch das P2P Audit Scoring System am 2026-10-08.*