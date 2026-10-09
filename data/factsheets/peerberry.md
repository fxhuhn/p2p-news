---
platform: peerberry
platform_name: PeerBerry
audit_date: '2026-10-09'
audit_version: '1.0'
audit_score:
  net_score: 65
  raw_score: 71
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
  rethink_p2p_score: 7.6
  rethink_p2p_rank: Platz 5
  rethink_p2p_red_flags: '0'
  p2p_game_score: 44
  p2p_game_rank: Platz 23 von 40
  p2p_empire_safety_score: 8.8
  p2p_empire_safety_band: Hoch
  p2p_empire_portfolio_perf: 100.0
  lars_wrobbel_score: 30
  lars_wrobbel_rank: Rang 9
pillars:
  pillar_1_regulation:
    score: 8
    max_score: 25
    band: Band_6_13
    rating: Unreguliert (Abtretungsverträge)
    evidence: Unreguliert über Kroatien/Litauen, aber getrennt geführte Bankkonten.
      Keine gesetzliche Anlegerentschädigung.
  pillar_2_solvency:
    score: 22
    max_score: 25
    band: Band_21_25
    rating: Sehr gut / Testiert
    evidence: Wirtschaftlich getragen durch hochprofitable Aventus Group (H1 2026
      Nettogewinn 49,1 Mio. €, Eigenkapital 264,2 Mio. €). Ausstehendes Portfolio
      übersteigt 155 Mio. € bei 120.000 Investoren (91 % Loyalty-Konzentration). 100
      % Rückzahlung aller Kriegs-Kredite centgenau aus Konzerngewinnen.
  pillar_3_collateral:
    score: 17
    max_score: 25
    band: Band_8_14
    rating: Unbesichert mit Buyback
    evidence: 0 % realisierter Kapitalverlust seit Launch 2017. 100 % Rückzahlung
      aller kriegsbetroffenen Kredite (über 50 Mio. €) aus operativen Konzerngewinnen
      der Aventus Group.
  pillar_4_liquidity:
    score: 24
    max_score: 25
    band: Band_20_25
    rating: Sehr liquide / Kurzläufer & Zweitmarkt
    evidence: Sehr kurze originäre Kreditlaufzeiten (>70 % unter 60 Tagen, Ø 30 Tage)
      kombiniert mit seit 15. Januar 2026 aktivem, gebührenfreiem Sekundärmarkt ohne
      Mindesthaltedauer.
malus_deductions:
- type: monoculture
  name: Monokultur-Malus
  penalty: -6
  trigger: Aventus Group stellt 88.0 % des Portfolios (>50 %)
  evidence: 'Hohe Klumpenbildung: Über 88.0 % Abhängigkeit von einem Garantiekonzern.'
sources:
- source_type: curated_profile
  path: data/platforms/peerberry/profile.yaml
- source_type: erfahrungen
  path: data/erfahrungen/p2p-empire/peerberry.md
---

# Platform Audit Factsheet: PeerBerry

**Audit-Datum:** 2026-10-09 | **Klasse:** `MID RISK` | **Depot-Limit:** `5 - 8 %`

## 1. Executive Summary & Audit-Verdict

> [!IMPORTANT]
> **Finaler Netto-Score:** **65 / 100 Punkte** (Rohscore: 71 Pkt | Malus-Abschläge: -6 Pkt)
> **Allokationsempfehlung:** Solide Beimischung: Hohe Bonität/Historie, aber unbesicherte Konsumkredite oder Monokulturen.

## 2. Aufschlüsselung der 4 Säulen

| Säule | Kategorie | Punkte | Einstufung | Kern-Evidenz |
| :--- | :--- | :---: | :--- | :--- |
| **Säule 1** | Regulierung & Verwahrung | **8 / 25** | Unreguliert (Abtretungsverträge) | Unreguliert über Kroatien/Litauen, aber getrennt geführte Bankkonten. Keine gesetzliche Anlegerentschädigung. |
| **Säule 2** | Solvenz & Governance | **22 / 25** | Sehr gut / Testiert | Wirtschaftlich getragen durch hochprofitable Aventus Group (H1 2026 Nettogewinn 49,1 Mio. €, Eigenkapital 264,2 Mio. €). Ausstehendes Portfolio übersteigt 155 Mio. € bei 120.000 Investoren (91 % Loyalty-Konzentration). 100 % Rückzahlung aller Kriegs-Kredite centgenau aus Konzerngewinnen. |
| **Säule 3** | Besicherung & Workout | **17 / 25** | Unbesichert mit Buyback | 0 % realisierter Kapitalverlust seit Launch 2017. 100 % Rückzahlung aller kriegsbetroffenen Kredite (über 50 Mio. €) aus operativen Konzerngewinnen der Aventus Group. |
| **Säule 4** | Liquidität & Zweitmarkt | **24 / 25** | Sehr liquide / Kurzläufer & Zweitmarkt | Sehr kurze originäre Kreditlaufzeiten (>70 % unter 60 Tagen, Ø 30 Tage) kombiniert mit seit 15. Januar 2026 aktivem, gebührenfreiem Sekundärmarkt ohne Mindesthaltedauer. |
| **SUMME** | **Rohscore (vor Mali)** | **71 / 100** | - | Theoretisches Maximum: 100 Pkt |

## 3. Malus-System (Strikte Risiko-Abschläge)

| Malus-Typ | Abzug | Auslöser / Kriterium | Beleg / Nachweis |
| :--- | :---: | :--- | :--- |
| **Monokultur-Malus** | `-6 Pkt` | Aventus Group stellt 88.0 % des Portfolios (>50 %) | Hohe Klumpenbildung: Über 88.0 % Abhängigkeit von einem Garantiekonzern. |

## 4. Benchmark-Spiegel (Marktkonsens & Triangulierung)

| Externe Referenzquelle | Metrik / Wert | Interpretation |
| :--- | :---: | :--- |
| **re:think P2P Risk Score** | **7.6 / 10** (Platz 5) | Denny Neidhardt Sicherheitsranking (Red Flags: 0) |
| **P2P Game Rating** | **44 / 100** (Platz 23 von 40) | Thomas P2P Rating (von 40 Plattformen) |
| **P2P Empire Safety Score** | **8.8 / 10** (Hoch) | Unabhängiger Testbericht Jakub Krejci |
| **P2P Empire Portfolio Performance** | **100.0 %** | Reale Rückzahlungsquote im Portfolio |
| **Lars Wrobbel / Passives Einkommen** | **Rang 9** (30/40 Pkt) | Langzeit-Rating aus Community- & Blog-Erfahrung |

---
*Automatisch generiert durch das P2P Audit Scoring System am 2026-10-09.*