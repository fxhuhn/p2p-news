---
platform: twino
platform_name: Twino
audit_date: '2026-10-07'
audit_version: '1.0'
audit_score:
  net_score: 69
  raw_score: 75
  risk_class: MID RISK
  portfolio_limit: 3 - 8 %
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
  rethink_p2p_score: 6.5
  rethink_p2p_rank: Platz 6
  rethink_p2p_red_flags: '0'
  p2p_game_score: 57
  p2p_game_rank: Platz 17 von 40
  p2p_empire_safety_score: 6.2
  p2p_empire_safety_band: Mittel
  p2p_empire_portfolio_perf: 96.5
  lars_wrobbel_score: 30
  lars_wrobbel_rank: Rang 5
pillars:
  pillar_1_regulation:
    score: 25
    max_score: 25
    band: Band_21_25
    rating: MiFID II / IBF lizenziert
    evidence: Lizenzierte Wertpapierfirma (IBF) unter Aufsicht der Latvijas Banka
      mit gesetzlichem Entschädigungsschutz.
  pillar_2_solvency:
    score: 21
    max_score: 25
    band: Band_21_25
    rating: Sehr gut / Testiert
    evidence: Unabhängig testierte Jahresabschlüsse durch BDO.
  pillar_3_collateral:
    score: 13
    max_score: 25
    band: Band_8_14
    rating: Unbesichert mit Buyback
    evidence: Verlässliche Rückkaufgarantie für reguläre Notes.
  pillar_4_liquidity:
    score: 16
    max_score: 25
    band: Band_13_19
    rating: Gute Liquidität
    evidence: Kein Sekundärmarkt, jedoch kurze originäre Kreditlaufzeiten (1 bis 3
      Monate).
malus_deductions:
- type: monoculture
  name: Monokultur-Malus
  penalty: -6
  trigger: TWINO Gruppe stellt 85.0 % des Portfolios (>50 %)
  evidence: 'Hohe Klumpenbildung: Über 85.0 % Abhängigkeit von einem Garantiekonzern.'
sources:
- source_type: curated_profile
  path: data/platforms/twino/profile.yaml
- source_type: erfahrungen
  path: data/erfahrungen/p2p-empire/twino.md
---

# Platform Audit Factsheet: Twino

**Audit-Datum:** 2026-10-07 | **Klasse:** `MID RISK` | **Depot-Limit:** `3 - 8 %`

## 1. Executive Summary & Audit-Verdict

> [!IMPORTANT]
> **Finaler Netto-Score:** **69 / 100 Punkte** (Rohscore: 75 Pkt | Malus-Abschläge: -6 Pkt)
> **Allokationsempfehlung:** Solide Beimischung: Hohe Bonität/Historie, aber unbesicherte Konsumkredite oder Monokulturen.

## 2. Aufschlüsselung der 4 Säulen

| Säule | Kategorie | Punkte | Einstufung | Kern-Evidenz |
| :--- | :--- | :---: | :--- | :--- |
| **Säule 1** | Regulierung & Verwahrung | **25 / 25** | MiFID II / IBF lizenziert | Lizenzierte Wertpapierfirma (IBF) unter Aufsicht der Latvijas Banka mit gesetzlichem Entschädigungsschutz. |
| **Säule 2** | Solvenz & Governance | **21 / 25** | Sehr gut / Testiert | Unabhängig testierte Jahresabschlüsse durch BDO. |
| **Säule 3** | Besicherung & Workout | **13 / 25** | Unbesichert mit Buyback | Verlässliche Rückkaufgarantie für reguläre Notes. |
| **Säule 4** | Liquidität & Zweitmarkt | **16 / 25** | Gute Liquidität | Kein Sekundärmarkt, jedoch kurze originäre Kreditlaufzeiten (1 bis 3 Monate). |
| **SUMME** | **Rohscore (vor Mali)** | **75 / 100** | - | Theoretisches Maximum: 100 Pkt |

## 3. Malus-System (Strikte Risiko-Abschläge)

| Malus-Typ | Abzug | Auslöser / Kriterium | Beleg / Nachweis |
| :--- | :---: | :--- | :--- |
| **Monokultur-Malus** | `-6 Pkt` | TWINO Gruppe stellt 85.0 % des Portfolios (>50 %) | Hohe Klumpenbildung: Über 85.0 % Abhängigkeit von einem Garantiekonzern. |

## 4. Benchmark-Spiegel (Marktkonsens & Triangulierung)

| Externe Referenzquelle | Metrik / Wert | Interpretation |
| :--- | :---: | :--- |
| **re:think P2P Risk Score** | **6.5 / 10** (Platz 6) | Denny Neidhardt Sicherheitsranking (Red Flags: 0) |
| **P2P Game Rating** | **57 / 100** (Platz 17 von 40) | Thomas P2P Rating (von 40 Plattformen) |
| **P2P Empire Safety Score** | **6.2 / 10** (Mittel) | Unabhängiger Testbericht Jakub Krejci |
| **P2P Empire Portfolio Performance** | **96.5 %** | Reale Rückzahlungsquote im Portfolio |
| **Lars Wrobbel / Passives Einkommen** | **Rang 5** (30/40 Pkt) | Langzeit-Rating aus Community- & Blog-Erfahrung |

---
*Automatisch generiert durch das P2P Audit Scoring System am 2026-10-07.*