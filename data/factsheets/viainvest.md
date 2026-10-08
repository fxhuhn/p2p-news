---
platform: viainvest
platform_name: Viainvest
audit_date: '2026-10-08'
audit_version: '1.0'
audit_score:
  net_score: 64
  raw_score: 72
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
  rethink_p2p_score: 5.4
  rethink_p2p_rank: Platz 21
  rethink_p2p_red_flags: '-5'
  p2p_game_score: 70
  p2p_game_rank: Platz 9 von 40
  p2p_empire_safety_score: 0.8
  p2p_empire_safety_band: Niedrig
  p2p_empire_portfolio_perf: 82.0
  lars_wrobbel_score: 29
  lars_wrobbel_rank: Rang 6
pillars:
  pillar_1_regulation:
    score: 25
    max_score: 25
    band: Band_21_25
    rating: MiFID II / IBF lizenziert
    evidence: Reguliert als Investment Brokerage Firm (IBF) unter Aufsicht der Latvijas
      Banka.
  pillar_2_solvency:
    score: 18
    max_score: 25
    band: Band_21_25
    rating: Sehr gut / Testiert
    evidence: 100 % Abhängigkeit vom börsennotierten Mutterkonzern VIA SMS Group.
  pillar_3_collateral:
    score: 13
    max_score: 25
    band: Band_8_14
    rating: Unbesichert mit Buyback
    evidence: Konsumkredite mit Buyback-Verpflichtung der VIA SMS Tochtergesellschaften.
  pillar_4_liquidity:
    score: 16
    max_score: 25
    band: Band_13_19
    rating: Gute Liquidität
    evidence: Kein Sekundärmarkt; Liquidität primär durch kurze Kreditlaufzeiten (30-180
      Tage).
malus_deductions:
- type: monoculture
  name: Monokultur-Malus
  penalty: -8
  trigger: VIA SMS Group JSC stellt 100.0 % des Portfolios (>50 %)
  evidence: 'Hohe Klumpenbildung: Über 100.0 % Abhängigkeit von einem Garantiekonzern.'
sources:
- source_type: curated_profile
  path: data/platforms/viainvest/profile.yaml
- source_type: erfahrungen
  path: data/erfahrungen/p2p-empire/viainvest.md
---

# Platform Audit Factsheet: Viainvest

**Audit-Datum:** 2026-10-08 | **Klasse:** `MID RISK` | **Depot-Limit:** `5 - 8 %`

## 1. Executive Summary & Audit-Verdict

> [!IMPORTANT]
> **Finaler Netto-Score:** **64 / 100 Punkte** (Rohscore: 72 Pkt | Malus-Abschläge: -8 Pkt)
> **Allokationsempfehlung:** Solide Beimischung: Hohe Bonität/Historie, aber unbesicherte Konsumkredite oder Monokulturen.

## 2. Aufschlüsselung der 4 Säulen

| Säule | Kategorie | Punkte | Einstufung | Kern-Evidenz |
| :--- | :--- | :---: | :--- | :--- |
| **Säule 1** | Regulierung & Verwahrung | **25 / 25** | MiFID II / IBF lizenziert | Reguliert als Investment Brokerage Firm (IBF) unter Aufsicht der Latvijas Banka. |
| **Säule 2** | Solvenz & Governance | **18 / 25** | Sehr gut / Testiert | 100 % Abhängigkeit vom börsennotierten Mutterkonzern VIA SMS Group. |
| **Säule 3** | Besicherung & Workout | **13 / 25** | Unbesichert mit Buyback | Konsumkredite mit Buyback-Verpflichtung der VIA SMS Tochtergesellschaften. |
| **Säule 4** | Liquidität & Zweitmarkt | **16 / 25** | Gute Liquidität | Kein Sekundärmarkt; Liquidität primär durch kurze Kreditlaufzeiten (30-180 Tage). |
| **SUMME** | **Rohscore (vor Mali)** | **72 / 100** | - | Theoretisches Maximum: 100 Pkt |

## 3. Malus-System (Strikte Risiko-Abschläge)

| Malus-Typ | Abzug | Auslöser / Kriterium | Beleg / Nachweis |
| :--- | :---: | :--- | :--- |
| **Monokultur-Malus** | `-8 Pkt` | VIA SMS Group JSC stellt 100.0 % des Portfolios (>50 %) | Hohe Klumpenbildung: Über 100.0 % Abhängigkeit von einem Garantiekonzern. |

## 4. Benchmark-Spiegel (Marktkonsens & Triangulierung)

| Externe Referenzquelle | Metrik / Wert | Interpretation |
| :--- | :---: | :--- |
| **re:think P2P Risk Score** | **5.4 / 10** (Platz 21) | Denny Neidhardt Sicherheitsranking (Red Flags: -5) |
| **P2P Game Rating** | **70 / 100** (Platz 9 von 40) | Thomas P2P Rating (von 40 Plattformen) |
| **P2P Empire Safety Score** | **0.8 / 10** (Niedrig) | Unabhängiger Testbericht Jakub Krejci |
| **P2P Empire Portfolio Performance** | **82.0 %** | Reale Rückzahlungsquote im Portfolio |
| **Lars Wrobbel / Passives Einkommen** | **Rang 6** (29/40 Pkt) | Langzeit-Rating aus Community- & Blog-Erfahrung |

---
*Automatisch generiert durch das P2P Audit Scoring System am 2026-10-08.*