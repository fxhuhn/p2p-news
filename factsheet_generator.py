"""
P2P Platform Factsheet Generator

Erstellt strukturierte Factsheets unter data/factsheets/<platform>.md
Enthält:
- YAML Frontmatter (maschinenlesbar, Pydantic-konform)
- Markdown Fließtext (narratives Audit, Begründungen, Evidenz-Zitate, Benchmark-Spiegel)
"""

import datetime
from pathlib import Path
from typing import Any, Dict

import yaml


class FactsheetGenerator:
    """Generiert vollständige Audit-Factsheets in data/factsheets/<platform>.md."""

    def __init__(self, output_dir: str = "data/factsheets") -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_factsheet(
        self, score_res: Dict[str, Any], sources: list[dict[str, str]] | None = None
    ) -> Path:
        platform_id = score_res["platform"]
        platform_name = score_res["platform_name"]
        audit_date = datetime.date.today().isoformat()

        # Frontmatter aufbauen
        frontmatter_data = {
            "platform": platform_id,
            "platform_name": platform_name,
            "audit_date": audit_date,
            "audit_version": "1.0",
            "audit_score": {
                "net_score": score_res["net_score"],
                "raw_score": score_res["raw_score"],
                "risk_class": score_res["risk_class"],
                "portfolio_limit": score_res["portfolio_limit"],
                "recommendation": score_res["recommendation"],
            },
            "flags": {
                "has_conflict": score_res["flags"].has_conflict,
                "conflict_notes": score_res["flags"].conflict_notes,
                "data_gaps": score_res["flags"].data_gaps,
            },
            "evidence_metadata": {
                "sourcing_strategy": score_res["flags"].sourcing_strategy,
                "primary_crawled_pages": 4,
                "curated_profile_used": True,
                "secondary_reviews_count": 2,
            },
            "benchmarks": {
                "rethink_p2p_score": score_res["benchmarks"].rethink_p2p_score,
                "rethink_p2p_rank": score_res["benchmarks"].rethink_p2p_rank,
                "rethink_p2p_red_flags": score_res["benchmarks"].rethink_p2p_red_flags,
                "p2p_game_score": score_res["benchmarks"].p2p_game_score,
                "p2p_game_rank": score_res["benchmarks"].p2p_game_rank,
                "p2p_empire_safety_score": score_res[
                    "benchmarks"
                ].p2p_empire_safety_score,
                "p2p_empire_safety_band": score_res[
                    "benchmarks"
                ].p2p_empire_safety_band,
                "p2p_empire_portfolio_perf": score_res[
                    "benchmarks"
                ].p2p_empire_portfolio_perf,
                "lars_wrobbel_score": score_res["benchmarks"].lars_wrobbel_score,
                "lars_wrobbel_rank": score_res["benchmarks"].lars_wrobbel_rank,
            },
            "pillars": {
                "pillar_1_regulation": {
                    "score": score_res["pillar_1"].final_score,
                    "max_score": 25,
                    "band": score_res["pillar_1"].band_id,
                    "rating": score_res["pillar_1"].rating_label,
                    "evidence": score_res["pillar_1"].evidence_text,
                },
                "pillar_2_solvency": {
                    "score": score_res["pillar_2"].final_score,
                    "max_score": 25,
                    "band": score_res["pillar_2"].band_id,
                    "rating": score_res["pillar_2"].rating_label,
                    "evidence": score_res["pillar_2"].evidence_text,
                },
                "pillar_3_collateral": {
                    "score": score_res["pillar_3"].final_score,
                    "max_score": 25,
                    "band": score_res["pillar_3"].band_id,
                    "rating": score_res["pillar_3"].rating_label,
                    "evidence": score_res["pillar_3"].evidence_text,
                },
                "pillar_4_liquidity": {
                    "score": score_res["pillar_4"].final_score,
                    "max_score": 25,
                    "band": score_res["pillar_4"].band_id,
                    "rating": score_res["pillar_4"].rating_label,
                    "evidence": score_res["pillar_4"].evidence_text,
                },
            },
            "malus_deductions": [
                {
                    "type": m.type,
                    "name": m.name,
                    "penalty": m.penalty,
                    "trigger": m.trigger_detail,
                    "evidence": m.evidence_quote,
                }
                for m in score_res["malus_deductions"]
            ],
            "sources": sources
            or [
                {
                    "source_type": "curated_profile",
                    "path": f"data/platforms/{platform_id}/profile.yaml",
                },
                {
                    "source_type": "erfahrungen",
                    "path": f"data/erfahrungen/p2p-empire/{platform_id}.md",
                },
            ],
        }

        # YAML String generieren
        yaml_str = yaml.dump(frontmatter_data, sort_keys=False, allow_unicode=True)

        # Markdown Body aufbauen
        lines = [
            "---",
            yaml_str.strip(),
            "---",
            "",
            f"# Platform Audit Factsheet: {platform_name}",
            "",
            f"**Audit-Datum:** {audit_date} | **Klasse:** `{score_res['risk_class']}` | **Depot-Limit:** `{score_res['portfolio_limit']}`",
            "",
            "## 1. Executive Summary & Audit-Verdict",
            "",
            "> [!IMPORTANT]",
            f"> **Finaler Netto-Score:** **{score_res['net_score']} / 100 Punkte** (Rohscore: {score_res['raw_score']} Pkt | Malus-Abschläge: {score_res['malus_total']} Pkt)",
            f"> **Allokationsempfehlung:** {score_res['recommendation']}",
            "",
        ]

        if score_res["flags"].has_conflict:
            lines.extend(
                [
                    "> [!WARNING]",
                    "> **Achtung - Widersprüchliche Angaben identifiziert:**",
                ]
            )
            for note in score_res["flags"].conflict_notes:
                lines.append(f"> • {note}")
            lines.append("")

        if score_res["flags"].data_gaps:
            lines.extend(
                [
                    "> [!NOTE]",
                    "> **Vorsichtsprinzip bei Datenlücken aktiv:**",
                ]
            )
            for gap in score_res["flags"].data_gaps:
                lines.append(f"> • {gap}")
            lines.append("")

        # Tabelle der 4 Säulen
        p1 = score_res["pillar_1"]
        p2 = score_res["pillar_2"]
        p3 = score_res["pillar_3"]
        p4 = score_res["pillar_4"]

        lines.extend(
            [
                "## 2. Aufschlüsselung der 4 Säulen",
                "",
                "| Säule | Kategorie | Punkte | Einstufung | Kern-Evidenz |",
                "| :--- | :--- | :---: | :--- | :--- |",
                f"| **Säule 1** | Regulierung & Verwahrung | **{p1.final_score} / 25** | {p1.rating_label} | {p1.evidence_text} |",
                f"| **Säule 2** | Solvenz & Governance | **{p2.final_score} / 25** | {p2.rating_label} | {p2.evidence_text} |",
                f"| **Säule 3** | Besicherung & Workout | **{p3.final_score} / 25** | {p3.rating_label} | {p3.evidence_text} |",
                f"| **Säule 4** | Liquidität & Zweitmarkt | **{p4.final_score} / 25** | {p4.rating_label} | {p4.evidence_text} |",
                f"| **SUMME** | **Rohscore (vor Mali)** | **{score_res['raw_score']} / 100** | - | Theoretisches Maximum: 100 Pkt |",
                "",
                "## 3. Malus-System (Strikte Risiko-Abschläge)",
                "",
            ]
        )

        if score_res["malus_deductions"]:
            lines.extend(
                [
                    "| Malus-Typ | Abzug | Auslöser / Kriterium | Beleg / Nachweis |",
                    "| :--- | :---: | :--- | :--- |",
                ]
            )
            for m in score_res["malus_deductions"]:
                lines.append(
                    f"| **{m.name}** | `{m.penalty} Pkt` | {m.trigger_detail} | {m.evidence_quote} |"
                )
            lines.append("")
        else:
            lines.extend(
                [
                    "Keine Malus-Abschläge wirksam. Das Portfolio weist weder unzulässige Monokulturen (>50 %), noch Fristen-Mismatches oder Governance-Opazität auf.",
                    "",
                ]
            )

        # Benchmark-Spiegel
        b = score_res["benchmarks"]
        lines.extend(
            [
                "## 4. Benchmark-Spiegel (Marktkonsens & Triangulierung)",
                "",
                "| Externe Referenzquelle | Metrik / Wert | Interpretation |",
                "| :--- | :---: | :--- |",
                f"| **re:think P2P Risk Score** | **{b.rethink_p2p_score if b.rethink_p2p_score is not None else 'N/A'} / 10** ({b.rethink_p2p_rank or 'Nicht gelistet'}) | Denny Neidhardt Sicherheitsranking {f'(Red Flags: {b.rethink_p2p_red_flags})' if b.rethink_p2p_red_flags else ''} |",
                f"| **P2P Game Rating** | **{b.p2p_game_score if b.p2p_game_score is not None else 'N/A'} / 100** ({b.p2p_game_rank or 'Nicht gelistet'}) | Thomas P2P Rating (von 40 Plattformen) |",
                f"| **P2P Empire Safety Score** | **{b.p2p_empire_safety_score if b.p2p_empire_safety_score is not None else 'N/A'} / 10** ({b.p2p_empire_safety_band or 'Kein Test'}) | Unabhängiger Testbericht Jakub Krejci |",
                f"| **P2P Empire Portfolio Performance** | **{b.p2p_empire_portfolio_perf if b.p2p_empire_portfolio_perf is not None else 'N/A'} %** | Reale Rückzahlungsquote im Portfolio |",
                f"| **Lars Wrobbel / Passives Einkommen** | **{b.lars_wrobbel_rank or 'Kein Rating'}** ({b.lars_wrobbel_score if b.lars_wrobbel_score is not None else 'N/A'}/40 Pkt) | Langzeit-Rating aus Community- & Blog-Erfahrung |",
                "",
                "---",
                f"*Automatisch generiert durch das P2P Audit Scoring System am {audit_date}.*",
            ]
        )

        target_file = self.output_dir / f"{platform_id}.md"
        with open(target_file, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        return target_file
