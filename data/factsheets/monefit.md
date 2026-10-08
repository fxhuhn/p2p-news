---
platform: monefit
platform_name: Monefit SmartSaver
audit_date: '2026-10-08'
audit_version: '1.0'
audit_score:
  net_score: 16
  raw_score: 41
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
  rethink_p2p_score: 4.8
  rethink_p2p_rank: Platz 23
  rethink_p2p_red_flags: '0'
  p2p_game_score: 50
  p2p_game_rank: Platz 21 von 40
  p2p_empire_safety_score: 0.0
  p2p_empire_safety_band: Niedrig
  p2p_empire_portfolio_perf: 70.0
  lars_wrobbel_score: 16
  lars_wrobbel_rank: Rang 14
pillars:
  pillar_1_regulation:
    score: 8
    max_score: 25
    band: Band_6_13
    rating: Unreguliert (Abtretungsverträge)
    evidence: Völlig unreguliertes Produkt; keine Einlagensicherung, keine Treuhandkonten.
  pillar_2_solvency:
    score: 17
    max_score: 25
    band: Band_14_20
    rating: Solide / Lokaler Abschluss
    evidence: Erhebliche Einreichungsverzögerungen bei Bilanzen; Pending Payments
      auf Mintos und Lendermarket.
  pillar_3_collateral:
    score: 14
    max_score: 25
    band: Band_8_14
    rating: Unbesichert mit Buyback
    evidence: Völlig unbesichert; Rückzahlung hängt allein von der Solvenz der Creditstar
      Group ab.
  pillar_4_liquidity:
    score: 2
    max_score: 25
    band: Band_0_5
    rating: Liquiditätsstau / Warteschlange
    evidence: Verspricht tägliche Auszahlung (Tagesgeld-Ähnlich), geriet jedoch wiederholt
      in Auszahlungsverzug.
malus_deductions:
- type: monoculture
  name: Monokultur-Malus
  penalty: -8
  trigger: Creditstar Group AS stellt 100.0 % des Portfolios (>50 %)
  evidence: 'Hohe Klumpenbildung: Über 100.0 % Abhängigkeit von einem Garantiekonzern.'
- type: term_mismatch
  name: Fristen-Mismatch-Malus
  penalty: -7
  trigger: Tägliche/flexible Auszahlung versprochen, aber durch langlaufende, illiquide
    Kredite hinterlegt.
  evidence: Tägliche/flexible Auszahlung versprochen, aber durch langlaufende, illiquide
    Kredite hinterlegt.
- type: related_party
  name: Related-Party- & Opazitäts-Malus
  penalty: -10
  trigger: Plattform dient rein der Refinanzierung des Schwesterkonzerns Creditstar.
  evidence: Plattform dient rein der Refinanzierung des Schwesterkonzerns Creditstar.
sources:
- source_type: curated_profile
  path: data/platforms/monefit/profile.yaml
- source_type: erfahrungen
  path: data/erfahrungen/p2p-empire/monefit.md
---

# Platform Audit Factsheet: Monefit SmartSaver

**Audit-Datum:** 2026-10-08 | **Klasse:** `DISTRESSED` | **Depot-Limit:** `0 % (Kapitalabzug & Recovery)`

## 1. Executive Summary & Audit-Verdict

> [!IMPORTANT]
> **Finaler Netto-Score:** **16 / 100 Punkte** (Rohscore: 41 Pkt | Malus-Abschläge: -25 Pkt)
> **Allokationsempfehlung:** Kapitalabzug & Workout: Notleidende Portfolios (NPL >40%), blockierte Zweitmärkte, Moratorien.

## 2. Aufschlüsselung der 4 Säulen

| Säule | Kategorie | Punkte | Einstufung | Kern-Evidenz |
| :--- | :--- | :---: | :--- | :--- |
| **Säule 1** | Regulierung & Verwahrung | **8 / 25** | Unreguliert (Abtretungsverträge) | Völlig unreguliertes Produkt; keine Einlagensicherung, keine Treuhandkonten. |
| **Säule 2** | Solvenz & Governance | **17 / 25** | Solide / Lokaler Abschluss | Erhebliche Einreichungsverzögerungen bei Bilanzen; Pending Payments auf Mintos und Lendermarket. |
| **Säule 3** | Besicherung & Workout | **14 / 25** | Unbesichert mit Buyback | Völlig unbesichert; Rückzahlung hängt allein von der Solvenz der Creditstar Group ab. |
| **Säule 4** | Liquidität & Zweitmarkt | **2 / 25** | Liquiditätsstau / Warteschlange | Verspricht tägliche Auszahlung (Tagesgeld-Ähnlich), geriet jedoch wiederholt in Auszahlungsverzug. |
| **SUMME** | **Rohscore (vor Mali)** | **41 / 100** | - | Theoretisches Maximum: 100 Pkt |

## 3. Malus-System (Strikte Risiko-Abschläge)

| Malus-Typ | Abzug | Auslöser / Kriterium | Beleg / Nachweis |
| :--- | :---: | :--- | :--- |
| **Monokultur-Malus** | `-8 Pkt` | Creditstar Group AS stellt 100.0 % des Portfolios (>50 %) | Hohe Klumpenbildung: Über 100.0 % Abhängigkeit von einem Garantiekonzern. |
| **Fristen-Mismatch-Malus** | `-7 Pkt` | Tägliche/flexible Auszahlung versprochen, aber durch langlaufende, illiquide Kredite hinterlegt. | Tägliche/flexible Auszahlung versprochen, aber durch langlaufende, illiquide Kredite hinterlegt. |
| **Related-Party- & Opazitäts-Malus** | `-10 Pkt` | Plattform dient rein der Refinanzierung des Schwesterkonzerns Creditstar. | Plattform dient rein der Refinanzierung des Schwesterkonzerns Creditstar. |

## 4. Benchmark-Spiegel (Marktkonsens & Triangulierung)

| Externe Referenzquelle | Metrik / Wert | Interpretation |
| :--- | :---: | :--- |
| **re:think P2P Risk Score** | **4.8 / 10** (Platz 23) | Denny Neidhardt Sicherheitsranking (Red Flags: 0) |
| **P2P Game Rating** | **50 / 100** (Platz 21 von 40) | Thomas P2P Rating (von 40 Plattformen) |
| **P2P Empire Safety Score** | **0.0 / 10** (Niedrig) | Unabhängiger Testbericht Jakub Krejci |
| **P2P Empire Portfolio Performance** | **70.0 %** | Reale Rückzahlungsquote im Portfolio |
| **Lars Wrobbel / Passives Einkommen** | **Rang 14** (16/40 Pkt) | Langzeit-Rating aus Community- & Blog-Erfahrung |

---
*Automatisch generiert durch das P2P Audit Scoring System am 2026-10-08.*