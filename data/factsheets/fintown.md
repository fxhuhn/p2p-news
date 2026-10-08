---
platform: fintown
platform_name: Fintown
audit_date: '2026-10-08'
audit_version: '1.0'
audit_score:
  net_score: 29
  raw_score: 44
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
  rethink_p2p_score: 5.5
  rethink_p2p_rank: Platz 19
  rethink_p2p_red_flags: '0'
  p2p_game_score: 18
  p2p_game_rank: Platz 34 von 40
  p2p_empire_safety_score: 7.3
  p2p_empire_safety_band: Mittel
  p2p_empire_portfolio_perf: 100.0
  lars_wrobbel_score: 19
  lars_wrobbel_rank: Rang 13
pillars:
  pillar_1_regulation:
    score: 8
    max_score: 25
    band: Band_6_13
    rating: Unreguliert (Abtretungsverträge)
    evidence: Unreguliert nach tschechischem Recht.
  pillar_2_solvency:
    score: 17
    max_score: 25
    band: Band_14_20
    rating: Solide / Lokaler Abschluss
    evidence: 100 % Abhängigkeit von der Vihorev Group (Immobilienentwickler in Prag).
  pillar_3_collateral:
    score: 3
    max_score: 25
    band: Band_0_7
    rating: Unbesichert ohne Rückkauf / Hochrisiko
    evidence: Keine erstrangige Grundschuld für Privatanleger; Kredite sind qualifiziert
      nachrangig.
  pillar_4_liquidity:
    score: 16
    max_score: 25
    band: Band_13_19
    rating: Gute Liquidität
    evidence: Kapital ist langjährig gebunden; vorzeitiger Ausstieg nur mit empfindlichem
      Abschlag.
malus_deductions:
- type: monoculture
  name: Monokultur-Malus
  penalty: -8
  trigger: Vihorev Group stellt 100.0 % des Portfolios (>50 %)
  evidence: 'Hohe Klumpenbildung: Über 100.0 % Abhängigkeit von einem Garantiekonzern.'
- type: term_mismatch
  name: Fristen-Mismatch-Malus
  penalty: -7
  trigger: Tägliche Zinsauszahlung versprochen, aber durch langfristige Hotelimmobilien
    hinterlegt.
  evidence: Tägliche Zinsauszahlung versprochen, aber durch langfristige Hotelimmobilien
    hinterlegt.
sources:
- source_type: curated_profile
  path: data/platforms/fintown/profile.yaml
- source_type: erfahrungen
  path: data/erfahrungen/p2p-empire/fintown.md
---

# Platform Audit Factsheet: Fintown

**Audit-Datum:** 2026-10-08 | **Klasse:** `DISTRESSED` | **Depot-Limit:** `0 % (Kapitalabzug & Recovery)`

## 1. Executive Summary & Audit-Verdict

> [!IMPORTANT]
> **Finaler Netto-Score:** **29 / 100 Punkte** (Rohscore: 44 Pkt | Malus-Abschläge: -15 Pkt)
> **Allokationsempfehlung:** Kapitalabzug & Workout: Notleidende Portfolios (NPL >40%), blockierte Zweitmärkte, Moratorien.

## 2. Aufschlüsselung der 4 Säulen

| Säule | Kategorie | Punkte | Einstufung | Kern-Evidenz |
| :--- | :--- | :---: | :--- | :--- |
| **Säule 1** | Regulierung & Verwahrung | **8 / 25** | Unreguliert (Abtretungsverträge) | Unreguliert nach tschechischem Recht. |
| **Säule 2** | Solvenz & Governance | **17 / 25** | Solide / Lokaler Abschluss | 100 % Abhängigkeit von der Vihorev Group (Immobilienentwickler in Prag). |
| **Säule 3** | Besicherung & Workout | **3 / 25** | Unbesichert ohne Rückkauf / Hochrisiko | Keine erstrangige Grundschuld für Privatanleger; Kredite sind qualifiziert nachrangig. |
| **Säule 4** | Liquidität & Zweitmarkt | **16 / 25** | Gute Liquidität | Kapital ist langjährig gebunden; vorzeitiger Ausstieg nur mit empfindlichem Abschlag. |
| **SUMME** | **Rohscore (vor Mali)** | **44 / 100** | - | Theoretisches Maximum: 100 Pkt |

## 3. Malus-System (Strikte Risiko-Abschläge)

| Malus-Typ | Abzug | Auslöser / Kriterium | Beleg / Nachweis |
| :--- | :---: | :--- | :--- |
| **Monokultur-Malus** | `-8 Pkt` | Vihorev Group stellt 100.0 % des Portfolios (>50 %) | Hohe Klumpenbildung: Über 100.0 % Abhängigkeit von einem Garantiekonzern. |
| **Fristen-Mismatch-Malus** | `-7 Pkt` | Tägliche Zinsauszahlung versprochen, aber durch langfristige Hotelimmobilien hinterlegt. | Tägliche Zinsauszahlung versprochen, aber durch langfristige Hotelimmobilien hinterlegt. |

## 4. Benchmark-Spiegel (Marktkonsens & Triangulierung)

| Externe Referenzquelle | Metrik / Wert | Interpretation |
| :--- | :---: | :--- |
| **re:think P2P Risk Score** | **5.5 / 10** (Platz 19) | Denny Neidhardt Sicherheitsranking (Red Flags: 0) |
| **P2P Game Rating** | **18 / 100** (Platz 34 von 40) | Thomas P2P Rating (von 40 Plattformen) |
| **P2P Empire Safety Score** | **7.3 / 10** (Mittel) | Unabhängiger Testbericht Jakub Krejci |
| **P2P Empire Portfolio Performance** | **100.0 %** | Reale Rückzahlungsquote im Portfolio |
| **Lars Wrobbel / Passives Einkommen** | **Rang 13** (19/40 Pkt) | Langzeit-Rating aus Community- & Blog-Erfahrung |

---
*Automatisch generiert durch das P2P Audit Scoring System am 2026-10-08.*