---
platform: hive5
platform_name: hive5
audit_date: '2026-10-19'
audit_version: '1.0'
audit_score:
  net_score: 39
  raw_score: 49
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
  rethink_p2p_score: 1.2
  rethink_p2p_rank: Platz 30
  rethink_p2p_red_flags: '-34'
  p2p_game_score: null
  p2p_game_rank: Nicht gelistet
  p2p_empire_safety_score: 5.0
  p2p_empire_safety_band: Mittel
  p2p_empire_portfolio_perf: 95.0
  lars_wrobbel_score: null
  lars_wrobbel_rank: Nicht gelistet
pillars:
  pillar_1_regulation:
    score: 10
    max_score: 25
    band: Band_6_13
    rating: Unreguliert (Abtretungsverträge)
    evidence: Operiert über kroatisches SPV (hive5 d.o.o.) mit Abtretungsverträgen.
      Externe Zahlungsabwicklung über lizenziertes EMI (Paysera). Keine MiFID II /
      ECSP-Lizenz.
  pillar_2_solvency:
    score: 5
    max_score: 25
    band: Band_0_6
    rating: Keine testierten Finanzberichte
    evidence: Gehört zur Hive Finance Gruppe. Starkes Wachstum, Management berichtet
      Profitabilität, jedoch noch kein unabhängiges Big-Four / Tier-2 Testat.
  pillar_3_collateral:
    score: 14
    max_score: 25
    band: Band_8_14
    rating: Unbesichert mit Buyback
    evidence: Unbesicherte Payday- und Konsumentenkredite der Konzerngesellschaften
      (Rupex, Tengo). Rückkaufverpflichtung nach 60 Tagen.
  pillar_4_liquidity:
    score: 20
    max_score: 25
    band: Band_20_25
    rating: Sehr liquide / Kurzläufer & Zweitmarkt
    evidence: Sehr kurze Laufzeiten (meist 30-90 Tage, Ø 45 Tage) kombiniert mit dem
      im Oktober 2026 (KW 41) eingeführten gebührenfreien Sekundärmarkt. Zügige Auszahlungen.
malus_deductions:
- type: monoculture
  name: Klumpen- & Konzentrations-Malus
  penalty: -10
  trigger: Hive Finance Gruppe (Rupex / Tengo) stellt 90.0 % des Portfolios (>=30
    %)
  evidence: 'Hohe Klumpenbildung: Über 90.0 % Abhängigkeit von einem Garantiekonzern
    oder Einzelschuldner.'
sources:
- source_type: curated_profile
  path: data/platforms/hive5/profile.yaml
- source_type: erfahrungen
  path: data/erfahrungen/p2p-empire/hive5.md
---

# Platform Audit Factsheet: hive5

**Audit-Datum:** 2026-10-19 | **Klasse:** `DISTRESSED` | **Depot-Limit:** `0 % (Kapitalabzug & Recovery)`

## 1. Executive Summary & Audit-Verdict

> [!IMPORTANT]
> **Finaler Netto-Score:** **39 / 100 Punkte** (Rohscore: 49 Pkt | Malus-Abschläge: -10 Pkt)
> **Allokationsempfehlung:** Kapitalabzug & Workout: Notleidende Portfolios (NPL >40%), blockierte Zweitmärkte, Moratorien.

> [!NOTE]
> **Vorsichtsprinzip bei Datenlücken aktiv:**
> • Keine unabhängig testierten Finanzberichte auffindbar (Säule 2 auf Minimalwert gesetzt).

## 2. Aufschlüsselung der 4 Säulen

| Säule | Kategorie | Punkte | Einstufung | Kern-Evidenz |
| :--- | :--- | :---: | :--- | :--- |
| **Säule 1** | Regulierung & Verwahrung | **10 / 25** | Unreguliert (Abtretungsverträge) | Operiert über kroatisches SPV (hive5 d.o.o.) mit Abtretungsverträgen. Externe Zahlungsabwicklung über lizenziertes EMI (Paysera). Keine MiFID II / ECSP-Lizenz. |
| **Säule 2** | Solvenz & Governance | **5 / 25** | Keine testierten Finanzberichte | Gehört zur Hive Finance Gruppe. Starkes Wachstum, Management berichtet Profitabilität, jedoch noch kein unabhängiges Big-Four / Tier-2 Testat. |
| **Säule 3** | Besicherung & Workout | **14 / 25** | Unbesichert mit Buyback | Unbesicherte Payday- und Konsumentenkredite der Konzerngesellschaften (Rupex, Tengo). Rückkaufverpflichtung nach 60 Tagen. |
| **Säule 4** | Liquidität & Zweitmarkt | **20 / 25** | Sehr liquide / Kurzläufer & Zweitmarkt | Sehr kurze Laufzeiten (meist 30-90 Tage, Ø 45 Tage) kombiniert mit dem im Oktober 2026 (KW 41) eingeführten gebührenfreien Sekundärmarkt. Zügige Auszahlungen. |
| **SUMME** | **Rohscore (vor Mali)** | **49 / 100** | - | Theoretisches Maximum: 100 Pkt |

## 3. Malus-System (Strikte Risiko-Abschläge)

| Malus-Typ | Abzug | Auslöser / Kriterium | Beleg / Nachweis |
| :--- | :---: | :--- | :--- |
| **Klumpen- & Konzentrations-Malus** | `-10 Pkt` | Hive Finance Gruppe (Rupex / Tengo) stellt 90.0 % des Portfolios (>=30 %) | Hohe Klumpenbildung: Über 90.0 % Abhängigkeit von einem Garantiekonzern oder Einzelschuldner. |

## 4. Benchmark-Spiegel (Marktkonsens & Triangulierung)

| Externe Referenzquelle | Metrik / Wert | Interpretation |
| :--- | :---: | :--- |
| **re:think P2P Risk Score** | **1.2 / 10** (Platz 30) | Denny Neidhardt Sicherheitsranking (Red Flags: -34) |
| **P2P Game Rating** | **N/A / 100** (Nicht gelistet) | Thomas P2P Rating (von 40 Plattformen) |
| **P2P Empire Safety Score** | **5.0 / 10** (Mittel) | Unabhängiger Testbericht Jakub Krejci |
| **P2P Empire Portfolio Performance** | **95.0 %** | Reale Rückzahlungsquote im Portfolio |
| **Lars Wrobbel / Passives Einkommen** | **Nicht gelistet** (N/A/40 Pkt) | Langzeit-Rating aus Community- & Blog-Erfahrung |

---
*Automatisch generiert durch das P2P Audit Scoring System am 2026-10-19.*