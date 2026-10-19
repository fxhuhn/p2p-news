---
platform: monefit
platform_name: Monefit SmartSaver
audit_date: '2026-10-19'
audit_version: '1.0'
audit_score:
  net_score: 38
  raw_score: 59
  risk_class: DISTRESSED
  portfolio_limit: 0 % (Kapitalabzug & Recovery)
  recommendation: 'Kapitalabzug & Workout: Notleidende Portfolios (NPL >40%), blockierte
    Zweitmärkte, Moratorien.'
flags:
  has_conflict: true
  conflict_notes:
  - 'NPL-Diskrepanz: Profil weist 12.0 % NPL aus, Benchmark-Performance indiziert
    30.0 % Rückstand.'
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
  lars_wrobbel_score: 17
  lars_wrobbel_rank: Rang 20
pillars:
  pillar_1_regulation:
    score: 10
    max_score: 25
    band: Band_6_13
    rating: Unreguliert (Abtretungsverträge)
    evidence: Die Muttergesellschaft Creditstar Group AS ist als Kreditgeber durch
      die estnische Finantsinspektsioon beaufsichtigt; SmartSaver selbst operiert
      als unreguliertes Darlehenskonstrukt ohne Einlagensicherung oder Treuhandsegregation.
  pillar_2_solvency:
    score: 17
    max_score: 25
    band: Band_14_20
    rating: Solide / Lokaler Abschluss
    evidence: Erhebliche Einreichungsverzögerungen bei Bilanzen; Pending Payments
      von Creditstar auf Mintos und Lendermarket.
  pillar_3_collateral:
    score: 14
    max_score: 25
    band: Band_8_14
    rating: Unbesichert mit Buyback
    evidence: Völlig unbesichert; Rückzahlung hängt allein vom operativen Cashflow
      und der Solvenz der Creditstar Group ab.
  pillar_4_liquidity:
    score: 18
    max_score: 25
    band: Band_13_19
    rating: Hohe Alltagsliquidität (Reserve-Pool)
    evidence: SmartSaver Flex bietet im regulären Betrieb tägliche Liquidität (1-3
      Werktage Auszahlungsdauer); bisher unterbrechungsfreie Bedienung von Abhebungen.
malus_deductions:
- type: monoculture
  name: Klumpen- & Konzentrations-Malus
  penalty: -10
  trigger: Direktbilanz-Darlehen ohne Realsicherheit oder Verlustpuffer (100 % Klumpen)
  evidence: 'Hohe Klumpenbildung: Über 100.0 % Abhängigkeit von einem Garantiekonzern
    oder Einzelschuldner.'
- type: term_mismatch
  name: Fristen-Mismatch-Malus
  penalty: -5
  trigger: Tägliche Verfügbarkeit im SmartSaver Flex trifft auf mehrmonatige bis mehrjährige
    Kreditlinien und Konsumentendarlehen (asymmetrische Fristentransformation).
  evidence: Tägliche Verfügbarkeit im SmartSaver Flex trifft auf mehrmonatige bis
    mehrjährige Kreditlinien und Konsumentendarlehen (asymmetrische Fristentransformation).
- type: cashflow_drag
  name: Cashflow- & Verzugs-Malus
  penalty: -6
  trigger: Laufende Verzugs-/NPL-Quote von 12.0 % (>=5 %)
  evidence: Cash Drag durch 12.0 % überfällige Kredite im Portfolio.
sources:
- source_type: curated_profile
  path: data/platforms/monefit/profile.yaml
- source_type: erfahrungen
  path: data/erfahrungen/p2p-empire/monefit.md
---

# Platform Audit Factsheet: Monefit SmartSaver

**Audit-Datum:** 2026-10-19 | **Klasse:** `DISTRESSED` | **Depot-Limit:** `0 % (Kapitalabzug & Recovery)`

## 1. Executive Summary & Audit-Verdict

> [!IMPORTANT]
> **Finaler Netto-Score:** **38 / 100 Punkte** (Rohscore: 59 Pkt | Malus-Abschläge: -21 Pkt)
> **Allokationsempfehlung:** Kapitalabzug & Workout: Notleidende Portfolios (NPL >40%), blockierte Zweitmärkte, Moratorien.

> [!WARNING]
> **Achtung - Widersprüchliche Angaben identifiziert:**
> • NPL-Diskrepanz: Profil weist 12.0 % NPL aus, Benchmark-Performance indiziert 30.0 % Rückstand.

## 2. Aufschlüsselung der 4 Säulen

| Säule | Kategorie | Punkte | Einstufung | Kern-Evidenz |
| :--- | :--- | :---: | :--- | :--- |
| **Säule 1** | Regulierung & Verwahrung | **10 / 25** | Unreguliert (Abtretungsverträge) | Die Muttergesellschaft Creditstar Group AS ist als Kreditgeber durch die estnische Finantsinspektsioon beaufsichtigt; SmartSaver selbst operiert als unreguliertes Darlehenskonstrukt ohne Einlagensicherung oder Treuhandsegregation. |
| **Säule 2** | Solvenz & Governance | **17 / 25** | Solide / Lokaler Abschluss | Erhebliche Einreichungsverzögerungen bei Bilanzen; Pending Payments von Creditstar auf Mintos und Lendermarket. |
| **Säule 3** | Besicherung & Workout | **14 / 25** | Unbesichert mit Buyback | Völlig unbesichert; Rückzahlung hängt allein vom operativen Cashflow und der Solvenz der Creditstar Group ab. |
| **Säule 4** | Liquidität & Zweitmarkt | **18 / 25** | Hohe Alltagsliquidität (Reserve-Pool) | SmartSaver Flex bietet im regulären Betrieb tägliche Liquidität (1-3 Werktage Auszahlungsdauer); bisher unterbrechungsfreie Bedienung von Abhebungen. |
| **SUMME** | **Rohscore (vor Mali)** | **59 / 100** | - | Theoretisches Maximum: 100 Pkt |

## 3. Malus-System (Strikte Risiko-Abschläge)

| Malus-Typ | Abzug | Auslöser / Kriterium | Beleg / Nachweis |
| :--- | :---: | :--- | :--- |
| **Klumpen- & Konzentrations-Malus** | `-10 Pkt` | Direktbilanz-Darlehen ohne Realsicherheit oder Verlustpuffer (100 % Klumpen) | Hohe Klumpenbildung: Über 100.0 % Abhängigkeit von einem Garantiekonzern oder Einzelschuldner. |
| **Fristen-Mismatch-Malus** | `-5 Pkt` | Tägliche Verfügbarkeit im SmartSaver Flex trifft auf mehrmonatige bis mehrjährige Kreditlinien und Konsumentendarlehen (asymmetrische Fristentransformation). | Tägliche Verfügbarkeit im SmartSaver Flex trifft auf mehrmonatige bis mehrjährige Kreditlinien und Konsumentendarlehen (asymmetrische Fristentransformation). |
| **Cashflow- & Verzugs-Malus** | `-6 Pkt` | Laufende Verzugs-/NPL-Quote von 12.0 % (>=5 %) | Cash Drag durch 12.0 % überfällige Kredite im Portfolio. |

## 4. Benchmark-Spiegel (Marktkonsens & Triangulierung)

| Externe Referenzquelle | Metrik / Wert | Interpretation |
| :--- | :---: | :--- |
| **re:think P2P Risk Score** | **4.8 / 10** (Platz 23) | Denny Neidhardt Sicherheitsranking (Red Flags: 0) |
| **P2P Game Rating** | **50 / 100** (Platz 21 von 40) | Thomas P2P Rating (von 40 Plattformen) |
| **P2P Empire Safety Score** | **0.0 / 10** (Niedrig) | Unabhängiger Testbericht Jakub Krejci |
| **P2P Empire Portfolio Performance** | **70.0 %** | Reale Rückzahlungsquote im Portfolio |
| **Lars Wrobbel / Passives Einkommen** | **Rang 20** (17/40 Pkt) | Langzeit-Rating aus Community- & Blog-Erfahrung |

---
*Automatisch generiert durch das P2P Audit Scoring System am 2026-10-19.*