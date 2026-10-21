---
platform: fagura
platform_name: Fagura
audit_date: '2026-10-21'
audit_version: '1.0'
audit_score:
  net_score: 68
  raw_score: 71
  risk_class: MID RISK
  portfolio_limit: 5 - 8 %
  recommendation: 'Solide Beimischung: Hohe Bonität/Historie, aber unbesicherte Konsumkredite
    oder Monokulturen.'
flags:
  has_conflict: true
  conflict_notes:
  - 'NPL-Diskrepanz: Profil weist 8.0 % NPL aus, Benchmark-Performance indiziert 15.0
    % Rückstand.'
  data_gaps: []
evidence_metadata:
  sourcing_strategy: curated_profile_and_secondary_audits
  primary_crawled_pages: 4
  curated_profile_used: true
  secondary_reviews_count: 2
benchmarks:
  rethink_p2p_score: null
  rethink_p2p_rank: Nicht gelistet
  rethink_p2p_red_flags: null
  p2p_game_score: null
  p2p_game_rank: Nicht gelistet
  p2p_empire_safety_score: 6.0
  p2p_empire_safety_band: Mittel
  p2p_empire_portfolio_perf: 85.0
  lars_wrobbel_score: null
  lars_wrobbel_rank: Nicht gelistet
  p2pdash_community_score: null
  p2pdash_median_xirr: null
  p2pdash_investors_count: null
pillars:
  pillar_1_regulation:
    score: 25
    max_score: 25
    band: Band_21_25
    rating: ECSP lizenziert
    evidence: Seit 2023 voll ECSP-lizenziert durch die rumänische Finanzaufsicht (ASF).
      Gelder liegen segregiert bei Lemonway.
  pillar_2_solvency:
    score: 17
    max_score: 25
    band: Band_14_20
    rating: Solide / Lokaler Abschluss
    evidence: Venture-finanziertes Crowdfunding-Fintech. Wachstumsphase mit moderaten
      Verlusten/Breakeven-Fokus.
  pillar_3_collateral:
    score: 11
    max_score: 25
    band: Band_8_14
    rating: Unbesichert mit Buyback
    evidence: Echte Peer-to-Peer Direktvergabe an Kreditnehmer in Moldau/Rumänien
      ohne Buyback, dafür mit Risikoklassen.
  pillar_4_liquidity:
    score: 18
    max_score: 25
    band: Band_13_19
    rating: Gute Liquidität
    evidence: Funktionierender Sekundärmarkt vorhanden; Laufzeiten der Kredite betragen
      12 bis 36 Monate.
malus_deductions:
- type: cashflow_drag
  name: Cashflow- & Verzugs-Malus
  penalty: -3
  trigger: Laufende Verzugs-/NPL-Quote von 8.0 % (>=5 %)
  evidence: Cash Drag durch 8.0 % überfällige Kredite im Portfolio.
sources:
- source_type: curated_profile
  path: data/platforms/fagura/profile.yaml
- source_type: erfahrungen
  path: data/erfahrungen/p2p-empire/fagura.md
---

# Platform Audit Factsheet: Fagura

**Audit-Datum:** 2026-10-21 | **Klasse:** `MID RISK` | **Depot-Limit:** `5 - 8 %`

## 1. Executive Summary & Audit-Verdict

> [!IMPORTANT]
> **Finaler Netto-Score:** **68 / 100 Punkte** (Rohscore: 71 Pkt | Malus-Abschläge: -3 Pkt)
> **Allokationsempfehlung:** Solide Beimischung: Hohe Bonität/Historie, aber unbesicherte Konsumkredite oder Monokulturen.

> [!WARNING]
> **Achtung - Widersprüchliche Angaben identifiziert:**
> • NPL-Diskrepanz: Profil weist 8.0 % NPL aus, Benchmark-Performance indiziert 15.0 % Rückstand.

## 2. Aufschlüsselung der 4 Säulen

| Säule | Kategorie | Punkte | Einstufung | Kern-Evidenz |
| :--- | :--- | :---: | :--- | :--- |
| **Säule 1** | Regulierung & Verwahrung | **25 / 25** | ECSP lizenziert | Seit 2023 voll ECSP-lizenziert durch die rumänische Finanzaufsicht (ASF). Gelder liegen segregiert bei Lemonway. |
| **Säule 2** | Solvenz & Governance | **17 / 25** | Solide / Lokaler Abschluss | Venture-finanziertes Crowdfunding-Fintech. Wachstumsphase mit moderaten Verlusten/Breakeven-Fokus. |
| **Säule 3** | Besicherung & Workout | **11 / 25** | Unbesichert mit Buyback | Echte Peer-to-Peer Direktvergabe an Kreditnehmer in Moldau/Rumänien ohne Buyback, dafür mit Risikoklassen. |
| **Säule 4** | Liquidität & Zweitmarkt | **18 / 25** | Gute Liquidität | Funktionierender Sekundärmarkt vorhanden; Laufzeiten der Kredite betragen 12 bis 36 Monate. |
| **SUMME** | **Rohscore (vor Mali)** | **71 / 100** | - | Theoretisches Maximum: 100 Pkt |

## 3. Malus-System (Strikte Risiko-Abschläge)

| Malus-Typ | Abzug | Auslöser / Kriterium | Beleg / Nachweis |
| :--- | :---: | :--- | :--- |
| **Cashflow- & Verzugs-Malus** | `-3 Pkt` | Laufende Verzugs-/NPL-Quote von 8.0 % (>=5 %) | Cash Drag durch 8.0 % überfällige Kredite im Portfolio. |

## 4. Benchmark-Spiegel (Marktkonsens & Triangulierung)

| Externe Referenzquelle | Metrik / Wert | Interpretation |
| :--- | :---: | :--- |
| **re:think P2P Risk Score** | **N/A / 10** (Nicht gelistet) | Denny Neidhardt Sicherheitsranking  |
| **P2P Game Rating** | **N/A / 100** (Nicht gelistet) | Thomas P2P Rating (von 40 Plattformen) |
| **P2P Empire Safety Score** | **6.0 / 10** (Mittel) | Unabhängiger Testbericht Jakub Krejci |
| **P2P Empire Portfolio Performance** | **85.0 %** | Reale Rückzahlungsquote im Portfolio |
| **Lars Wrobbel / Passives Einkommen** | **Nicht gelistet** (N/A/40 Pkt) | Langzeit-Rating aus Community- & Blog-Erfahrung |
| **P2P Dash Community Score** | **N/A / 100** | Empirischer Community Trust Score (p2pdash.com) |

### Externe Analysen & Testberichte

- [https://p2pempire.com/de/bewertung/fagura](https://p2pempire.com/de/bewertung/fagura)
- [https://passives-einkommen-mit-p2p.de/fagura-erfahrungen/](https://passives-einkommen-mit-p2p.de/fagura-erfahrungen/)
- [https://p2pmarketdata.com/platforms/fagura](https://p2pmarketdata.com/platforms/fagura)

---
*Automatisch generiert durch das P2P Audit Scoring System am 2026-10-21.*