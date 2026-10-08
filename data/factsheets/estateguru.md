---
platform: estateguru
platform_name: EstateGuru
audit_date: '2026-10-08'
audit_version: '1.0'
audit_score:
  net_score: 27
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
  rethink_p2p_score: 3.8
  rethink_p2p_rank: Platz 26
  rethink_p2p_red_flags: '-17'
  p2p_game_score: 48
  p2p_game_rank: Platz 22 von 40
  p2p_empire_safety_score: 0.0
  p2p_empire_safety_band: Niedrig
  p2p_empire_portfolio_perf: 40.7
  lars_wrobbel_score: null
  lars_wrobbel_rank: Ausgesetzt
pillars:
  pillar_1_regulation:
    score: 25
    max_score: 25
    band: Band_21_25
    rating: ECSP lizenziert
    evidence: Reguliert unter europäischer Crowdfunding-Lizenz (ECSP) durch die estnische
      Finantsinspektsioon. Lemonway Verwahrung.
  pillar_2_solvency:
    score: 17
    max_score: 25
    band: Band_14_20
    rating: Solide / Lokaler Abschluss
    evidence: Erhebliche bilanzielle Belastungen durch Kreditausfälle im Deutschland-Portfolio.
  pillar_3_collateral:
    score: 3
    max_score: 25
    band: Band_0_7
    rating: Notleidend (NPL >30 %)
    evidence: Massiver Workout-Stau; 59,3 % des Portfolios notleidend oder in gerichtlicher
      Verwertung (insb. Deutsches Portfolio).
  pillar_4_liquidity:
    score: 2
    max_score: 25
    band: Band_0_5
    rating: Liquiditätsstau / Warteschlange
    evidence: Sekundärmarkt für notleidende Kredite blockiert/deaktiviert. Liquiditätsabzug
      massiv eingeschränkt.
malus_deductions:
- type: distressed
  name: Distressed- & Ausfall-Malus
  penalty: -20
  trigger: Portfolio-NPL >40% (aktuell 59,3%), Ventos Energy Restrukturierung, Zweitmarkt
    für Problemkredite blockiert.
  evidence: Portfolio-NPL >40% (aktuell 59,3%), Ventos Energy Restrukturierung, Zweitmarkt
    für Problemkredite blockiert.
sources:
- source_type: curated_profile
  path: data/platforms/estateguru/profile.yaml
- source_type: erfahrungen
  path: data/erfahrungen/p2p-empire/estateguru.md
---

# Platform Audit Factsheet: EstateGuru

**Audit-Datum:** 2026-10-08 | **Klasse:** `DISTRESSED` | **Depot-Limit:** `0 % (Kapitalabzug & Recovery)`

## 1. Executive Summary & Audit-Verdict

> [!IMPORTANT]
> **Finaler Netto-Score:** **27 / 100 Punkte** (Rohscore: 47 Pkt | Malus-Abschläge: -20 Pkt)
> **Allokationsempfehlung:** Kapitalabzug & Workout: Notleidende Portfolios (NPL >40%), blockierte Zweitmärkte, Moratorien.

## 2. Aufschlüsselung der 4 Säulen

| Säule | Kategorie | Punkte | Einstufung | Kern-Evidenz |
| :--- | :--- | :---: | :--- | :--- |
| **Säule 1** | Regulierung & Verwahrung | **25 / 25** | ECSP lizenziert | Reguliert unter europäischer Crowdfunding-Lizenz (ECSP) durch die estnische Finantsinspektsioon. Lemonway Verwahrung. |
| **Säule 2** | Solvenz & Governance | **17 / 25** | Solide / Lokaler Abschluss | Erhebliche bilanzielle Belastungen durch Kreditausfälle im Deutschland-Portfolio. |
| **Säule 3** | Besicherung & Workout | **3 / 25** | Notleidend (NPL >30 %) | Massiver Workout-Stau; 59,3 % des Portfolios notleidend oder in gerichtlicher Verwertung (insb. Deutsches Portfolio). |
| **Säule 4** | Liquidität & Zweitmarkt | **2 / 25** | Liquiditätsstau / Warteschlange | Sekundärmarkt für notleidende Kredite blockiert/deaktiviert. Liquiditätsabzug massiv eingeschränkt. |
| **SUMME** | **Rohscore (vor Mali)** | **47 / 100** | - | Theoretisches Maximum: 100 Pkt |

## 3. Malus-System (Strikte Risiko-Abschläge)

| Malus-Typ | Abzug | Auslöser / Kriterium | Beleg / Nachweis |
| :--- | :---: | :--- | :--- |
| **Distressed- & Ausfall-Malus** | `-20 Pkt` | Portfolio-NPL >40% (aktuell 59,3%), Ventos Energy Restrukturierung, Zweitmarkt für Problemkredite blockiert. | Portfolio-NPL >40% (aktuell 59,3%), Ventos Energy Restrukturierung, Zweitmarkt für Problemkredite blockiert. |

## 4. Benchmark-Spiegel (Marktkonsens & Triangulierung)

| Externe Referenzquelle | Metrik / Wert | Interpretation |
| :--- | :---: | :--- |
| **re:think P2P Risk Score** | **3.8 / 10** (Platz 26) | Denny Neidhardt Sicherheitsranking (Red Flags: -17) |
| **P2P Game Rating** | **48 / 100** (Platz 22 von 40) | Thomas P2P Rating (von 40 Plattformen) |
| **P2P Empire Safety Score** | **0.0 / 10** (Niedrig) | Unabhängiger Testbericht Jakub Krejci |
| **P2P Empire Portfolio Performance** | **40.7 %** | Reale Rückzahlungsquote im Portfolio |
| **Lars Wrobbel / Passives Einkommen** | **Ausgesetzt** (N/A/40 Pkt) | Langzeit-Rating aus Community- & Blog-Erfahrung |

---
*Automatisch generiert durch das P2P Audit Scoring System am 2026-10-08.*