---
platform: ventus
platform_name: Ventus Energy
audit_date: '2026-10-07'
audit_version: '1.0'
audit_score:
  net_score: 0
  raw_score: 16
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
  p2p_game_score: 0
  p2p_game_rank: Platz 40 von 40
  p2p_empire_safety_score: 0.0
  p2p_empire_safety_band: Niedrig
  p2p_empire_portfolio_perf: 50.0
  lars_wrobbel_score: null
  lars_wrobbel_rank: Kein Rating
pillars:
  pillar_1_regulation:
    score: 8
    max_score: 25
    band: Band_6_13
    rating: Unreguliert (Abtretungsverträge)
    evidence: Unregulierter Energie-Crowdfunder.
  pillar_2_solvency:
    score: 3
    max_score: 25
    band: Band_0_6
    rating: Keine testierten Finanzberichte
    evidence: Zahlungsstopps und laufende Sanierungsverhandlungen mit Gläubigern.
  pillar_3_collateral:
    score: 3
    max_score: 25
    band: Band_0_7
    rating: Unbesichert ohne Rückkauf / Hochrisiko
    evidence: Projekte in Verzug oder gerichtlich anhängig.
  pillar_4_liquidity:
    score: 2
    max_score: 25
    band: Band_0_5
    rating: Liquiditätsstau / Warteschlange
    evidence: Auszahlungen de facto gestoppt oder blockiert.
malus_deductions:
- type: monoculture
  name: Monokultur-Malus
  penalty: -8
  trigger: Ventus Energy stellt 100.0 % des Portfolios (>50 %)
  evidence: 'Hohe Klumpenbildung: Über 100.0 % Abhängigkeit von einem Garantiekonzern.'
- type: related_party
  name: Related-Party- & Opazitäts-Malus
  penalty: -10
  trigger: Intransparente Mittelverwendung und verweigerte Gutachten.
  evidence: Intransparente Mittelverwendung und verweigerte Gutachten.
- type: distressed
  name: Distressed- & Ausfall-Malus
  penalty: -20
  trigger: Akutes Sanierungsverfahren, Auszahlungsstopps, 65 % NPL.
  evidence: Akutes Sanierungsverfahren, Auszahlungsstopps, 65 % NPL.
sources:
- source_type: curated_profile
  path: data/platforms/ventus/profile.yaml
- source_type: erfahrungen
  path: data/erfahrungen/p2p-empire/ventus.md
---

# Platform Audit Factsheet: Ventus Energy

**Audit-Datum:** 2026-10-07 | **Klasse:** `DISTRESSED` | **Depot-Limit:** `0 % (Kapitalabzug & Recovery)`

## 1. Executive Summary & Audit-Verdict

> [!IMPORTANT]
> **Finaler Netto-Score:** **0 / 100 Punkte** (Rohscore: 16 Pkt | Malus-Abschläge: -38 Pkt)
> **Allokationsempfehlung:** Kapitalabzug & Workout: Notleidende Portfolios (NPL >40%), blockierte Zweitmärkte, Moratorien.

> [!NOTE]
> **Vorsichtsprinzip bei Datenlücken aktiv:**
> • Keine unabhängig testierten Finanzberichte auffindbar (Säule 2 auf Minimalwert gesetzt).

## 2. Aufschlüsselung der 4 Säulen

| Säule | Kategorie | Punkte | Einstufung | Kern-Evidenz |
| :--- | :--- | :---: | :--- | :--- |
| **Säule 1** | Regulierung & Verwahrung | **8 / 25** | Unreguliert (Abtretungsverträge) | Unregulierter Energie-Crowdfunder. |
| **Säule 2** | Solvenz & Governance | **3 / 25** | Keine testierten Finanzberichte | Zahlungsstopps und laufende Sanierungsverhandlungen mit Gläubigern. |
| **Säule 3** | Besicherung & Workout | **3 / 25** | Unbesichert ohne Rückkauf / Hochrisiko | Projekte in Verzug oder gerichtlich anhängig. |
| **Säule 4** | Liquidität & Zweitmarkt | **2 / 25** | Liquiditätsstau / Warteschlange | Auszahlungen de facto gestoppt oder blockiert. |
| **SUMME** | **Rohscore (vor Mali)** | **16 / 100** | - | Theoretisches Maximum: 100 Pkt |

## 3. Malus-System (Strikte Risiko-Abschläge)

| Malus-Typ | Abzug | Auslöser / Kriterium | Beleg / Nachweis |
| :--- | :---: | :--- | :--- |
| **Monokultur-Malus** | `-8 Pkt` | Ventus Energy stellt 100.0 % des Portfolios (>50 %) | Hohe Klumpenbildung: Über 100.0 % Abhängigkeit von einem Garantiekonzern. |
| **Related-Party- & Opazitäts-Malus** | `-10 Pkt` | Intransparente Mittelverwendung und verweigerte Gutachten. | Intransparente Mittelverwendung und verweigerte Gutachten. |
| **Distressed- & Ausfall-Malus** | `-20 Pkt` | Akutes Sanierungsverfahren, Auszahlungsstopps, 65 % NPL. | Akutes Sanierungsverfahren, Auszahlungsstopps, 65 % NPL. |

## 4. Benchmark-Spiegel (Marktkonsens & Triangulierung)

| Externe Referenzquelle | Metrik / Wert | Interpretation |
| :--- | :---: | :--- |
| **re:think P2P Risk Score** | **N/A / 10** (Nicht gelistet) | Denny Neidhardt Sicherheitsranking  |
| **P2P Game Rating** | **0 / 100** (Platz 40 von 40) | Thomas P2P Rating (von 40 Plattformen) |
| **P2P Empire Safety Score** | **0.0 / 10** (Niedrig) | Unabhängiger Testbericht Jakub Krejci |
| **P2P Empire Portfolio Performance** | **50.0 %** | Reale Rückzahlungsquote im Portfolio |
| **Lars Wrobbel / Passives Einkommen** | **Kein Rating** (N/A/40 Pkt) | Langzeit-Rating aus Community- & Blog-Erfahrung |

---
*Automatisch generiert durch das P2P Audit Scoring System am 2026-10-07.*