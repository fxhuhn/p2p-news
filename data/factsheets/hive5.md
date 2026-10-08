---
platform: hive5
platform_name: hive5
audit_date: '2026-10-08'
audit_version: '1.0'
audit_score:
  net_score: 57
  raw_score: 63
  risk_class: WATCHLIST
  portfolio_limit: 0 - 3 %
  recommendation: 'Taktische Position unter Vorbehalt: Schwächen bei LTV, fehlende
    Testate oder Governance-Risse.'
flags:
  has_conflict: false
  conflict_notes: []
  data_gaps:
  - Unabhängig testierter Konzernabschluss der Hive Finance Gruppe steht noch aus
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
  lars_wrobbel_score: 15
  lars_wrobbel_rank: Rang 18
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
    score: 17
    max_score: 25
    band: Band_14_20
    rating: Solide / Lokaler Abschluss
    evidence: Gehört zur Hive Finance Gruppe. Starkes Wachstum, Management berichtet
      Profitabilität, jedoch noch kein unabhängiges Big-Four / Tier-2 Testat.
  pillar_3_collateral:
    score: 16
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
  name: Monokultur-Malus
  penalty: -6
  trigger: Hive Finance Gruppe (Rupex / Tengo) stellt 90.0 % des Portfolios (>50 %)
  evidence: 'Hohe Klumpenbildung: Über 90.0 % Abhängigkeit von einem Garantiekonzern.'
sources:
- source_type: curated_profile
  path: data/platforms/hive5/profile.yaml
- source_type: erfahrungen
  path: data/erfahrungen/p2p-empire/hive5.md
---

# Platform Audit Factsheet: hive5

**Audit-Datum:** 2026-10-08 | **Klasse:** `WATCHLIST` | **Depot-Limit:** `0 - 3 %`

## 1. Executive Summary & Audit-Verdict

> [!IMPORTANT]
> **Finaler Netto-Score:** **57 / 100 Punkte** (Rohscore: 63 Pkt | Malus-Abschläge: -6 Pkt)
> **Allokationsempfehlung:** Taktische Position unter Vorbehalt: Schwächen bei LTV, fehlende Testate oder Governance-Risse.

> [!NOTE]
> **Vorsichtsprinzip bei Datenlücken aktiv:**
> • Unabhängig testierter Konzernabschluss der Hive Finance Gruppe steht noch aus

## 2. Aufschlüsselung der 4 Säulen

| Säule | Kategorie | Punkte | Einstufung | Kern-Evidenz |
| :--- | :--- | :---: | :--- | :--- |
| **Säule 1** | Regulierung & Verwahrung | **10 / 25** | Unreguliert (Abtretungsverträge) | Operiert über kroatisches SPV (hive5 d.o.o.) mit Abtretungsverträgen. Externe Zahlungsabwicklung über lizenziertes EMI (Paysera). Keine MiFID II / ECSP-Lizenz. |
| **Säule 2** | Solvenz & Governance | **17 / 25** | Solide / Lokaler Abschluss | Gehört zur Hive Finance Gruppe. Starkes Wachstum, Management berichtet Profitabilität, jedoch noch kein unabhängiges Big-Four / Tier-2 Testat. |
| **Säule 3** | Besicherung & Workout | **16 / 25** | Unbesichert mit Buyback | Unbesicherte Payday- und Konsumentenkredite der Konzerngesellschaften (Rupex, Tengo). Rückkaufverpflichtung nach 60 Tagen. |
| **Säule 4** | Liquidität & Zweitmarkt | **20 / 25** | Sehr liquide / Kurzläufer & Zweitmarkt | Sehr kurze Laufzeiten (meist 30-90 Tage, Ø 45 Tage) kombiniert mit dem im Oktober 2026 (KW 41) eingeführten gebührenfreien Sekundärmarkt. Zügige Auszahlungen. |
| **SUMME** | **Rohscore (vor Mali)** | **63 / 100** | - | Theoretisches Maximum: 100 Pkt |

## 3. Malus-System (Strikte Risiko-Abschläge)

| Malus-Typ | Abzug | Auslöser / Kriterium | Beleg / Nachweis |
| :--- | :---: | :--- | :--- |
| **Monokultur-Malus** | `-6 Pkt` | Hive Finance Gruppe (Rupex / Tengo) stellt 90.0 % des Portfolios (>50 %) | Hohe Klumpenbildung: Über 90.0 % Abhängigkeit von einem Garantiekonzern. |

## 4. Benchmark-Spiegel (Marktkonsens & Triangulierung)

| Externe Referenzquelle | Metrik / Wert | Interpretation |
| :--- | :---: | :--- |
| **re:think P2P Risk Score** | **1.2 / 10** (Platz 30) | Denny Neidhardt Sicherheitsranking (Red Flags: -34) |
| **P2P Game Rating** | **N/A / 100** (Nicht gelistet) | Thomas P2P Rating (von 40 Plattformen) |
| **P2P Empire Safety Score** | **5.0 / 10** (Mittel) | Unabhängiger Testbericht Jakub Krejci |
| **P2P Empire Portfolio Performance** | **95.0 %** | Reale Rückzahlungsquote im Portfolio |
| **Lars Wrobbel / Passives Einkommen** | **Rang 18** (15/40 Pkt) | Langzeit-Rating aus Community- & Blog-Erfahrung |

---
*Automatisch generiert durch das P2P Audit Scoring System am 2026-10-08.*