---
platform: esketit
platform_name: Esketit
audit_date: '2026-10-07'
audit_version: '1.0'
audit_score:
  net_score: 64
  raw_score: 70
  risk_class: MID RISK
  portfolio_limit: 5 - 8 %
  recommendation: 'Solide Beimischung: Hohe Bonität/Historie, aber unbesicherte Konsumkredite
    oder Monokulturen.'
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
  rethink_p2p_red_flags: '-5'
  p2p_game_score: 29
  p2p_game_rank: Platz 31 von 40
  p2p_empire_safety_score: 6.2
  p2p_empire_safety_band: Mittel
  p2p_empire_portfolio_perf: 100.0
  lars_wrobbel_score: 20
  lars_wrobbel_rank: Rang 12
pillars:
  pillar_1_regulation:
    score: 13
    max_score: 25
    band: Band_6_13
    rating: Unreguliert / Lizenzübergang
    evidence: Operiert unreguliert über kroatische Abtretungsverträge. Die neu erteilte
      IBF-Lizenz der Schwestergesellschaft SIA IBC Invest schafft einen klaren Migrationspfad
      (+2 Pkt.), schützt Bestandsanlagen aber rechtlich noch nicht.
  pillar_2_solvency:
    score: 21
    max_score: 25
    band: Band_21_25
    rating: Sehr gut / Testiert
    evidence: Wirtschaftlich gestützt durch die hochprofitable Creamfinance-Gruppe
      mit testierten Zahlen.
  pillar_3_collateral:
    score: 16
    max_score: 25
    band: Band_8_14
    rating: Unbesichert mit Buyback
    evidence: Kurzfristige Konsumentenkredite mit funktionierendem 60-Tage-Rückkauf;
      keine dingliche Immobiliensicherung.
  pillar_4_liquidity:
    score: 20
    max_score: 25
    band: Band_20_25
    rating: Sehr liquide / Kurzläufer & Zweitmarkt
    evidence: Hohe Fungibilität durch Payday-Kurzläufer und gebührenfreien, funktionierenden
      Sekundärmarkt.
malus_deductions:
- type: monoculture
  name: Monokultur-Malus
  penalty: -6
  trigger: Creamfinance Gruppe stellt 82.0 % des Portfolios (>50 %)
  evidence: 'Hohe Klumpenbildung: Über 82.0 % Abhängigkeit von einem Garantiekonzern.'
sources:
- source_type: curated_profile
  path: data/platforms/esketit/profile.yaml
- source_type: erfahrungen
  path: data/erfahrungen/p2p-empire/esketit.md
---

# Platform Audit Factsheet: Esketit

**Audit-Datum:** 2026-10-07 | **Klasse:** `MID RISK` | **Depot-Limit:** `5 - 8 %`

## 1. Executive Summary & Audit-Verdict

> [!IMPORTANT]
> **Finaler Netto-Score:** **64 / 100 Punkte** (Rohscore: 70 Pkt | Malus-Abschläge: -6 Pkt)
> **Allokationsempfehlung:** Solide Beimischung: Hohe Bonität/Historie, aber unbesicherte Konsumkredite oder Monokulturen.

## 2. Aufschlüsselung der 4 Säulen

| Säule | Kategorie | Punkte | Einstufung | Kern-Evidenz |
| :--- | :--- | :---: | :--- | :--- |
| **Säule 1** | Regulierung & Verwahrung | **13 / 25** | Unreguliert / Lizenzübergang | Operiert unreguliert über kroatische Abtretungsverträge. Die neu erteilte IBF-Lizenz der Schwestergesellschaft SIA IBC Invest schafft einen klaren Migrationspfad (+2 Pkt.), schützt Bestandsanlagen aber rechtlich noch nicht. |
| **Säule 2** | Solvenz & Governance | **21 / 25** | Sehr gut / Testiert | Wirtschaftlich gestützt durch die hochprofitable Creamfinance-Gruppe mit testierten Zahlen. |
| **Säule 3** | Besicherung & Workout | **16 / 25** | Unbesichert mit Buyback | Kurzfristige Konsumentenkredite mit funktionierendem 60-Tage-Rückkauf; keine dingliche Immobiliensicherung. |
| **Säule 4** | Liquidität & Zweitmarkt | **20 / 25** | Sehr liquide / Kurzläufer & Zweitmarkt | Hohe Fungibilität durch Payday-Kurzläufer und gebührenfreien, funktionierenden Sekundärmarkt. |
| **SUMME** | **Rohscore (vor Mali)** | **70 / 100** | - | Theoretisches Maximum: 100 Pkt |

## 3. Malus-System (Strikte Risiko-Abschläge)

| Malus-Typ | Abzug | Auslöser / Kriterium | Beleg / Nachweis |
| :--- | :---: | :--- | :--- |
| **Monokultur-Malus** | `-6 Pkt` | Creamfinance Gruppe stellt 82.0 % des Portfolios (>50 %) | Hohe Klumpenbildung: Über 82.0 % Abhängigkeit von einem Garantiekonzern. |

## 4. Benchmark-Spiegel (Marktkonsens & Triangulierung)

| Externe Referenzquelle | Metrik / Wert | Interpretation |
| :--- | :---: | :--- |
| **re:think P2P Risk Score** | **4.8 / 10** (Platz 23) | Denny Neidhardt Sicherheitsranking (Red Flags: -5) |
| **P2P Game Rating** | **29 / 100** (Platz 31 von 40) | Thomas P2P Rating (von 40 Plattformen) |
| **P2P Empire Safety Score** | **6.2 / 10** (Mittel) | Unabhängiger Testbericht Jakub Krejci |
| **P2P Empire Portfolio Performance** | **100.0 %** | Reale Rückzahlungsquote im Portfolio |
| **Lars Wrobbel / Passives Einkommen** | **Rang 12** (20/40 Pkt) | Langzeit-Rating aus Community- & Blog-Erfahrung |

---
*Automatisch generiert durch das P2P Audit Scoring System am 2026-10-07.*