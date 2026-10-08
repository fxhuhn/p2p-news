---
platform: asterra
platform_name: Asterra Estate
audit_date: '2026-10-08'
audit_version: '1.0'
audit_score:
  net_score: 13
  raw_score: 19
  risk_class: DISTRESSED
  portfolio_limit: 0 % (Kapitalabzug & Recovery)
  recommendation: 'Kapitalabzug & Workout: Notleidende Portfolios (NPL >40%), blockierte
    Zweitmärkte, Moratorien.'
flags:
  has_conflict: true
  conflict_notes:
  - Unklare Regulierung und fehlende Nachweise für Treuhandsegregierung
  data_gaps:
  - Keine unabhängig testierten Finanzberichte auffindbar (Säule 2 auf Minimalwert
    gesetzt).
  - Fehlende Publizität von Betreiberfinanzen und Verwertungsnachweisen
evidence_metadata:
  sourcing_strategy: curated_profile_and_secondary_audits
  primary_crawled_pages: 4
  curated_profile_used: true
  secondary_reviews_count: 2
benchmarks:
  rethink_p2p_score: null
  rethink_p2p_rank: Nicht gelistet
  rethink_p2p_red_flags: null
  p2p_game_score: 14
  p2p_game_rank: Platz 36 von 40
  p2p_empire_safety_score: 2.5
  p2p_empire_safety_band: Niedrig
  p2p_empire_portfolio_perf: 70.0
  lars_wrobbel_score: 9
  lars_wrobbel_rank: Rang 24
pillars:
  pillar_1_regulation:
    score: 2
    max_score: 25
    band: Band_0_5
    rating: Völlig unreguliert / Offshore
    evidence: Sehr junge spanische Immobilienplattform; operiert ohne vollwertige
      ECSP-Lizenz über SPVs.
  pillar_2_solvency:
    score: 3
    max_score: 25
    band: Band_0_6
    rating: Keine testierten Finanzberichte
    evidence: Keine testierten Finanzberichte vorhanden; minimaler Track-Record und
      Datenhistorie (Vorsichtsprinzip).
  pillar_3_collateral:
    score: 3
    max_score: 25
    band: Band_0_7
    rating: Unbesichert ohne Rückkauf / Hochrisiko
    evidence: Nachrang- oder Vorfinanzierungsdarlehen im spanischen Immobilienmarkt;
      unvollständige dingliche Absicherungsnachweise.
  pillar_4_liquidity:
    score: 11
    max_score: 25
    band: Band_6_12
    rating: Planbare Tilgung
    evidence: Kein Sekundärmarkt; Kapital ist vollständig bis Projektende gebunden.
malus_deductions:
- type: monoculture
  name: Monokultur-Malus
  penalty: -6
  trigger: Lokale Bauträger-Partner stellt 85.0 % des Portfolios (>50 %)
  evidence: 'Hohe Klumpenbildung: Über 85.0 % Abhängigkeit von einem Garantiekonzern.'
sources:
- source_type: curated_profile
  path: data/platforms/asterra/profile.yaml
- source_type: erfahrungen
  path: data/erfahrungen/p2p-empire/asterra.md
---

# Platform Audit Factsheet: Asterra Estate

**Audit-Datum:** 2026-10-08 | **Klasse:** `DISTRESSED` | **Depot-Limit:** `0 % (Kapitalabzug & Recovery)`

## 1. Executive Summary & Audit-Verdict

> [!IMPORTANT]
> **Finaler Netto-Score:** **13 / 100 Punkte** (Rohscore: 19 Pkt | Malus-Abschläge: -6 Pkt)
> **Allokationsempfehlung:** Kapitalabzug & Workout: Notleidende Portfolios (NPL >40%), blockierte Zweitmärkte, Moratorien.

> [!WARNING]
> **Achtung - Widersprüchliche Angaben identifiziert:**
> • Unklare Regulierung und fehlende Nachweise für Treuhandsegregierung

> [!NOTE]
> **Vorsichtsprinzip bei Datenlücken aktiv:**
> • Keine unabhängig testierten Finanzberichte auffindbar (Säule 2 auf Minimalwert gesetzt).
> • Fehlende Publizität von Betreiberfinanzen und Verwertungsnachweisen

## 2. Aufschlüsselung der 4 Säulen

| Säule | Kategorie | Punkte | Einstufung | Kern-Evidenz |
| :--- | :--- | :---: | :--- | :--- |
| **Säule 1** | Regulierung & Verwahrung | **2 / 25** | Völlig unreguliert / Offshore | Sehr junge spanische Immobilienplattform; operiert ohne vollwertige ECSP-Lizenz über SPVs. |
| **Säule 2** | Solvenz & Governance | **3 / 25** | Keine testierten Finanzberichte | Keine testierten Finanzberichte vorhanden; minimaler Track-Record und Datenhistorie (Vorsichtsprinzip). |
| **Säule 3** | Besicherung & Workout | **3 / 25** | Unbesichert ohne Rückkauf / Hochrisiko | Nachrang- oder Vorfinanzierungsdarlehen im spanischen Immobilienmarkt; unvollständige dingliche Absicherungsnachweise. |
| **Säule 4** | Liquidität & Zweitmarkt | **11 / 25** | Planbare Tilgung | Kein Sekundärmarkt; Kapital ist vollständig bis Projektende gebunden. |
| **SUMME** | **Rohscore (vor Mali)** | **19 / 100** | - | Theoretisches Maximum: 100 Pkt |

## 3. Malus-System (Strikte Risiko-Abschläge)

| Malus-Typ | Abzug | Auslöser / Kriterium | Beleg / Nachweis |
| :--- | :---: | :--- | :--- |
| **Monokultur-Malus** | `-6 Pkt` | Lokale Bauträger-Partner stellt 85.0 % des Portfolios (>50 %) | Hohe Klumpenbildung: Über 85.0 % Abhängigkeit von einem Garantiekonzern. |

## 4. Benchmark-Spiegel (Marktkonsens & Triangulierung)

| Externe Referenzquelle | Metrik / Wert | Interpretation |
| :--- | :---: | :--- |
| **re:think P2P Risk Score** | **N/A / 10** (Nicht gelistet) | Denny Neidhardt Sicherheitsranking  |
| **P2P Game Rating** | **14 / 100** (Platz 36 von 40) | Thomas P2P Rating (von 40 Plattformen) |
| **P2P Empire Safety Score** | **2.5 / 10** (Niedrig) | Unabhängiger Testbericht Jakub Krejci |
| **P2P Empire Portfolio Performance** | **70.0 %** | Reale Rückzahlungsquote im Portfolio |
| **Lars Wrobbel / Passives Einkommen** | **Rang 24** (9/40 Pkt) | Langzeit-Rating aus Community- & Blog-Erfahrung |

---
*Automatisch generiert durch das P2P Audit Scoring System am 2026-10-08.*