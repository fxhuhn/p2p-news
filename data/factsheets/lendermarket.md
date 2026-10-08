---
platform: lendermarket
platform_name: Lendermarket
audit_date: '2026-10-08'
audit_version: '1.0'
audit_score:
  net_score: 24
  raw_score: 38
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
  rethink_p2p_score: 6.4
  rethink_p2p_rank: Platz 8
  rethink_p2p_red_flags: '-12'
  p2p_game_score: 61
  p2p_game_rank: Platz 11 von 40
  p2p_empire_safety_score: 5.8
  p2p_empire_safety_band: Mittel
  p2p_empire_portfolio_perf: 78.0
  lars_wrobbel_score: null
  lars_wrobbel_rank: Nicht gelistet
pillars:
  pillar_1_regulation:
    score: 8
    max_score: 25
    band: Band_6_13
    rating: Unreguliert (Abtretungsverträge)
    evidence: Unregulierter Marktplatz; keine Segregation durch lizenziertes Institut.
  pillar_2_solvency:
    score: 17
    max_score: 25
    band: Band_14_20
    rating: Solide / Lokaler Abschluss
    evidence: Chronische Pending Payments bei Creditstar-Krediten über viele Monate.
  pillar_3_collateral:
    score: 11
    max_score: 25
    band: Band_8_14
    rating: Unbesichert mit Buyback
    evidence: Rückkaufgarantie wurde in der Vergangenheit wiederholt ausgesetzt oder
      verzögert bedient.
  pillar_4_liquidity:
    score: 2
    max_score: 25
    band: Band_0_5
    rating: Liquiditätsstau / Warteschlange
    evidence: Kein Sekundärmarkt; erhebliche Auszahlungsverzögerungen bei fälligen
      Geldern.
malus_deductions:
- type: monoculture
  name: Monokultur-Malus
  penalty: -4
  trigger: Creditstar Group AS stellt 65.0 % des Portfolios (>50 %)
  evidence: 'Hohe Klumpenbildung: Über 65.0 % Abhängigkeit von einem Garantiekonzern.'
- type: related_party
  name: Related-Party- & Opazitäts-Malus
  penalty: -10
  trigger: Verflechtung zwischen Lendermarket-Betreibern und Creditstar Management.
  evidence: Verflechtung zwischen Lendermarket-Betreibern und Creditstar Management.
sources:
- source_type: curated_profile
  path: data/platforms/lendermarket/profile.yaml
- source_type: erfahrungen
  path: data/erfahrungen/p2p-empire/lendermarket.md
---

# Platform Audit Factsheet: Lendermarket

**Audit-Datum:** 2026-10-08 | **Klasse:** `DISTRESSED` | **Depot-Limit:** `0 % (Kapitalabzug & Recovery)`

## 1. Executive Summary & Audit-Verdict

> [!IMPORTANT]
> **Finaler Netto-Score:** **24 / 100 Punkte** (Rohscore: 38 Pkt | Malus-Abschläge: -14 Pkt)
> **Allokationsempfehlung:** Kapitalabzug & Workout: Notleidende Portfolios (NPL >40%), blockierte Zweitmärkte, Moratorien.

## 2. Aufschlüsselung der 4 Säulen

| Säule | Kategorie | Punkte | Einstufung | Kern-Evidenz |
| :--- | :--- | :---: | :--- | :--- |
| **Säule 1** | Regulierung & Verwahrung | **8 / 25** | Unreguliert (Abtretungsverträge) | Unregulierter Marktplatz; keine Segregation durch lizenziertes Institut. |
| **Säule 2** | Solvenz & Governance | **17 / 25** | Solide / Lokaler Abschluss | Chronische Pending Payments bei Creditstar-Krediten über viele Monate. |
| **Säule 3** | Besicherung & Workout | **11 / 25** | Unbesichert mit Buyback | Rückkaufgarantie wurde in der Vergangenheit wiederholt ausgesetzt oder verzögert bedient. |
| **Säule 4** | Liquidität & Zweitmarkt | **2 / 25** | Liquiditätsstau / Warteschlange | Kein Sekundärmarkt; erhebliche Auszahlungsverzögerungen bei fälligen Geldern. |
| **SUMME** | **Rohscore (vor Mali)** | **38 / 100** | - | Theoretisches Maximum: 100 Pkt |

## 3. Malus-System (Strikte Risiko-Abschläge)

| Malus-Typ | Abzug | Auslöser / Kriterium | Beleg / Nachweis |
| :--- | :---: | :--- | :--- |
| **Monokultur-Malus** | `-4 Pkt` | Creditstar Group AS stellt 65.0 % des Portfolios (>50 %) | Hohe Klumpenbildung: Über 65.0 % Abhängigkeit von einem Garantiekonzern. |
| **Related-Party- & Opazitäts-Malus** | `-10 Pkt` | Verflechtung zwischen Lendermarket-Betreibern und Creditstar Management. | Verflechtung zwischen Lendermarket-Betreibern und Creditstar Management. |

## 4. Benchmark-Spiegel (Marktkonsens & Triangulierung)

| Externe Referenzquelle | Metrik / Wert | Interpretation |
| :--- | :---: | :--- |
| **re:think P2P Risk Score** | **6.4 / 10** (Platz 8) | Denny Neidhardt Sicherheitsranking (Red Flags: -12) |
| **P2P Game Rating** | **61 / 100** (Platz 11 von 40) | Thomas P2P Rating (von 40 Plattformen) |
| **P2P Empire Safety Score** | **5.8 / 10** (Mittel) | Unabhängiger Testbericht Jakub Krejci |
| **P2P Empire Portfolio Performance** | **78.0 %** | Reale Rückzahlungsquote im Portfolio |
| **Lars Wrobbel / Passives Einkommen** | **Nicht gelistet** (N/A/40 Pkt) | Langzeit-Rating aus Community- & Blog-Erfahrung |

---
*Automatisch generiert durch das P2P Audit Scoring System am 2026-10-08.*