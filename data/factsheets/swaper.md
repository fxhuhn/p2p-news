---
platform: swaper
platform_name: Swaper
audit_date: '2026-10-07'
audit_version: '1.0'
audit_score:
  net_score: 28
  raw_score: 46
  risk_class: DISTRESSED
  portfolio_limit: 0 % (Kapitalabzug & Recovery)
  recommendation: 'Kapitalabzug & Workout: Notleidende Portfolios (NPL >40%), blockierte
    Zweitmärkte, Moratorien.'
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
  rethink_p2p_score: null
  rethink_p2p_rank: Nicht gelistet
  rethink_p2p_red_flags: null
  p2p_game_score: 36
  p2p_game_rank: Platz 29 von 40
  p2p_empire_safety_score: 1.1
  p2p_empire_safety_band: Niedrig
  p2p_empire_portfolio_perf: 80.0
  lars_wrobbel_score: null
  lars_wrobbel_rank: Kein Rating
pillars:
  pillar_1_regulation:
    score: 8
    max_score: 25
    band: Band_6_13
    rating: Unreguliert (Abtretungsverträge)
    evidence: Völlig unreguliert über Estland operierend.
  pillar_2_solvency:
    score: 3
    max_score: 25
    band: Band_0_6
    rating: Keine testierten Finanzberichte
    evidence: Keine unabhängig testierten Konzernberichte öffentlich verfügbar (Vorsichtsprinzip).
  pillar_3_collateral:
    score: 11
    max_score: 25
    band: Band_8_14
    rating: Unbesichert mit Buyback
    evidence: Konsumkredite gestützt auf Rückkaufversprechen der Wandoo Finance.
  pillar_4_liquidity:
    score: 24
    max_score: 25
    band: Band_20_25
    rating: Sehr liquide / Kurzläufer & Zweitmarkt
    evidence: Hohe Fungibilität durch 30-Tage-Kredite und Sekundärmarkt.
malus_deductions:
- type: monoculture
  name: Monokultur-Malus
  penalty: -8
  trigger: Wandoo Finance Group stellt 100.0 % des Portfolios (>50 %)
  evidence: 'Hohe Klumpenbildung: Über 100.0 % Abhängigkeit von einem Garantiekonzern.'
- type: related_party
  name: Related-Party- & Opazitäts-Malus
  penalty: -10
  trigger: Fehlende testierte Jahresabschlüsse und Intransparenz der Holding-Eigentümer.
  evidence: Fehlende testierte Jahresabschlüsse und Intransparenz der Holding-Eigentümer.
sources:
- source_type: curated_profile
  path: data/platforms/swaper/profile.yaml
- source_type: erfahrungen
  path: data/erfahrungen/p2p-empire/swaper.md
---

# Platform Audit Factsheet: Swaper

**Audit-Datum:** 2026-10-07 | **Klasse:** `DISTRESSED` | **Depot-Limit:** `0 % (Kapitalabzug & Recovery)`

## 1. Executive Summary & Audit-Verdict

> [!IMPORTANT]
> **Finaler Netto-Score:** **28 / 100 Punkte** (Rohscore: 46 Pkt | Malus-Abschläge: -18 Pkt)
> **Allokationsempfehlung:** Kapitalabzug & Workout: Notleidende Portfolios (NPL >40%), blockierte Zweitmärkte, Moratorien.

> [!NOTE]
> **Vorsichtsprinzip bei Datenlücken aktiv:**
> • Keine unabhängig testierten Finanzberichte auffindbar (Säule 2 auf Minimalwert gesetzt).

## 2. Aufschlüsselung der 4 Säulen

| Säule | Kategorie | Punkte | Einstufung | Kern-Evidenz |
| :--- | :--- | :---: | :--- | :--- |
| **Säule 1** | Regulierung & Verwahrung | **8 / 25** | Unreguliert (Abtretungsverträge) | Völlig unreguliert über Estland operierend. |
| **Säule 2** | Solvenz & Governance | **3 / 25** | Keine testierten Finanzberichte | Keine unabhängig testierten Konzernberichte öffentlich verfügbar (Vorsichtsprinzip). |
| **Säule 3** | Besicherung & Workout | **11 / 25** | Unbesichert mit Buyback | Konsumkredite gestützt auf Rückkaufversprechen der Wandoo Finance. |
| **Säule 4** | Liquidität & Zweitmarkt | **24 / 25** | Sehr liquide / Kurzläufer & Zweitmarkt | Hohe Fungibilität durch 30-Tage-Kredite und Sekundärmarkt. |
| **SUMME** | **Rohscore (vor Mali)** | **46 / 100** | - | Theoretisches Maximum: 100 Pkt |

## 3. Malus-System (Strikte Risiko-Abschläge)

| Malus-Typ | Abzug | Auslöser / Kriterium | Beleg / Nachweis |
| :--- | :---: | :--- | :--- |
| **Monokultur-Malus** | `-8 Pkt` | Wandoo Finance Group stellt 100.0 % des Portfolios (>50 %) | Hohe Klumpenbildung: Über 100.0 % Abhängigkeit von einem Garantiekonzern. |
| **Related-Party- & Opazitäts-Malus** | `-10 Pkt` | Fehlende testierte Jahresabschlüsse und Intransparenz der Holding-Eigentümer. | Fehlende testierte Jahresabschlüsse und Intransparenz der Holding-Eigentümer. |

## 4. Benchmark-Spiegel (Marktkonsens & Triangulierung)

| Externe Referenzquelle | Metrik / Wert | Interpretation |
| :--- | :---: | :--- |
| **re:think P2P Risk Score** | **N/A / 10** (Nicht gelistet) | Denny Neidhardt Sicherheitsranking  |
| **P2P Game Rating** | **36 / 100** (Platz 29 von 40) | Thomas P2P Rating (von 40 Plattformen) |
| **P2P Empire Safety Score** | **1.1 / 10** (Niedrig) | Unabhängiger Testbericht Jakub Krejci |
| **P2P Empire Portfolio Performance** | **80.0 %** | Reale Rückzahlungsquote im Portfolio |
| **Lars Wrobbel / Passives Einkommen** | **Kein Rating** (N/A/40 Pkt) | Langzeit-Rating aus Community- & Blog-Erfahrung |

---
*Automatisch generiert durch das P2P Audit Scoring System am 2026-10-07.*