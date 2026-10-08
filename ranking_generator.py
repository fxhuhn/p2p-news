"""
P2P Platform Ranking Generator

Erstellt monatliche Gesamtrankings unter data/rankings/audit-ranking-YYYY-MM.md
Enthält:
- Master-Rangliste aller Plattformen (sortiert nach Netto-Score inkl. Deltas +/-)
- Akute Watchlist- & Risiko-Warnungen
- Portfolio-Allokationsmatrix für ein 100.000 € Musterdepot
- Benchmark-Spiegel (Abgleich mit externen Experten-Rankings)
"""

import datetime
from pathlib import Path
from typing import Any, Dict, List

import yaml

from scoring_models import RISK_CLASS_LIMITS
from storage_sqlite import SQLiteStore


class RankingGenerator:
    """Generiert Master-Rankings und Delta-Reports."""

    def __init__(
        self, db_path: str = "data/p2p_archive.db", output_dir: str = "data/rankings"
    ) -> None:
        self.store = SQLiteStore(db_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_monthly_ranking(self, audit_date: str | None = None) -> Path:
        today = datetime.date.today()
        audit_date = audit_date or today.isoformat()
        year_month = today.strftime("%Y-%m")

        scores = self.store.get_all_latest_scores()
        if not scores:
            raise ValueError("Keine Audit-Scores in der Datenbank gefunden!")

        # Deltas zum Vormonat berechnen
        enriched_scores: List[Dict[str, Any]] = []

        for s in scores:
            plat = s["platform"]
            prev = self.store.get_previous_platform_score(plat, audit_date)
            if prev:
                delta = s["net_score"] - prev["net_score"]
                delta_str = (
                    f"+{delta}" if delta > 0 else f"{delta}" if delta < 0 else "±0"
                )
            else:
                delta_str = "NEU"

            item = dict(s)
            item["delta_str"] = delta_str
            enriched_scores.append(item)

        # Sortieren: Net Score desc, Raw Score desc, Pillar 1 desc
        enriched_scores.sort(
            key=lambda x: (x["net_score"], x["raw_score"], x["pillar_1"]), reverse=True
        )

        # YAML Frontmatter
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        frontmatter = [
            "---",
            f"title: 'P2P Platform Audit Ranking – {year_month}'",
            f"audit_date: '{audit_date}'",
            f"year_month: '{year_month}'",
            f"platforms_count: {len(enriched_scores)}",
            "model: 'Mathematisches Nettomodell (Max. 100 Pkt - Mali)'",
            f"generated_at: '{now_iso}'",
            "---",
            "",
        ]

        # Markdown Aufbau
        lines = [
            f"# P2P Platform Audit Ranking – {year_month}",
            "",
            "## 1. Master-Rangliste aller Plattformen",
            "",
            "| Rang | Plattform | Netto-Score | Δ Vormonat | Risikoklasse | Depot-Limit | P1 (Reg) | P2 (Solv) | P3 (Asset) | P4 (Liq) | Malus | Flags |",
            "| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |",
        ]

        for rank, s in enumerate(enriched_scores, 1):
            plat_name = s["platform"].capitalize()
            net = s["net_score"]
            delta = s["delta_str"]
            k = s["risk_class"]

            # Limit aus Metamodell
            limit = (
                "0 %"
                if k in ("SPECULATIVE", "DISTRESSED")
                else RISK_CLASS_LIMITS.get(k, "0 %").replace(" - ", "-")
            )

            p1, p2, p3, p4 = s["pillar_1"], s["pillar_2"], s["pillar_3"], s["pillar_4"]
            malus = f"`{s['malus_total']} Pkt`" if s["malus_total"] < 0 else "0"

            # Flags
            flag_icons = []
            if s.get("has_conflict"):
                flag_icons.append("⚠️ Konflikt")
            if s.get("data_gaps_json") and s["data_gaps_json"] != "[]":
                flag_icons.append("⚠️ Lücke")
            flag_str = ", ".join(flag_icons) if flag_icons else "✅ Valide"

            # Factsheet-Link
            fs_link = f"[{plat_name}](../factsheets/{s['platform']}.md)"

            lines.append(
                f"| **{rank}** | {fs_link} | **{net}** | `{delta}` | `{k}` | {limit} | {p1} | {p2} | {p3} | {p4} | {malus} | {flag_str} |"
            )

        # Watchlist & Risiko-Warnungen
        distressed = [
            s
            for s in enriched_scores
            if s["risk_class"] in ["SPECULATIVE", "DISTRESSED"]
        ]
        lines.extend(
            [
                "",
                "## 2. Akute Watchlist- & Risiko-Warnungen",
                "",
            ]
        )

        if distressed:
            lines.extend(
                [
                    "> [!CAUTION]",
                    "> **Kapitalabzug & Neuanlage-Stopp für folgende Plattformen aktiv:**",
                ]
            )
            for d in distressed:
                lines.append(
                    f"> • **{d['platform'].capitalize()}** ({d['risk_class']}, Score: {d['net_score']}): Malus-Abzug {d['malus_total']} Pkt."
                )
            lines.append("")
        else:
            lines.extend(
                [
                    "Aktuell befinden sich keine Plattformen in den Kategorien SPECULATIVE oder DISTRESSED.",
                    "",
                ]
            )

        # Allokationsmatrix
        lines.extend(
            [
                "## 3. Portfoliogewichtung für ein 100.000 € Musterdepot",
                "",
                "| Risikoklasse | Zulässiges Depot-Limit | Plattformen im Universum | Maximale Allokation |",
                "| :--- | :---: | :--- | :---: |",
                f"| **TOP TIER (70 - 100)** | 8 – 15 % je Plattform | {', '.join([s['platform'].capitalize() for s in enriched_scores if s['risk_class'] == 'TOP TIER']) or 'Keine'} | **50 – 70 %** |",
                f"| **MID RISK (60 - 69)** | 5 – 8 % je Plattform | {', '.join([s['platform'].capitalize() for s in enriched_scores if s['risk_class'] == 'MID RISK']) or 'Keine'} | **25 – 40 %** |",
                f"| **WATCHLIST (51 - 59)** | 0 – 3 % je Plattform | {', '.join([s['platform'].capitalize() for s in enriched_scores if s['risk_class'] == 'WATCHLIST']) or 'Keine'} | **0 – 10 %** |",
                "| **SPECULATIVE / DISTRESSED (0 - 50)** | **0 %** (Neuanlage-Stopp) | "
                + (
                    ", ".join(
                        [
                            s["platform"].capitalize()
                            for s in enriched_scores
                            if s["risk_class"] in ["SPECULATIVE", "DISTRESSED"]
                        ]
                    )
                    or "Keine"
                )
                + " | **0 %** |",
                "",
                "## 4. Markt-Triangulierung & Benchmark-Vergleichsspiegel",
                "",
                "Abgleich unseres mathematischen Netto-Scores mit den externen Experten-Rankings:",
                "- **re:think P2P:** Risk Score (0.0 - 10.0) inkl. Red Flags / Malus-Abzüge (Denny Neidhardt)",
                "- **P2P Game:** Rating-Score (0 - 100) aus 40 getesteten Plattformen (Thomas P2P)",
                "- **P2P Empire:** Safety Score (0.0 - 10.0) von Jakub Krejci",
                "- **Passives Einkommen:** P2P-Rating (0 - 40 Punkte) von Lars Wrobbel",
                "",
                "| Plattform | Unser Netto-Score | Risikoklasse | re:think P2P (0-10) | P2P Game (0-100) | P2P Empire (0-10) | Lars Wrobbel (0-40) |",
                "| :--- | :---: | :---: | :---: | :---: | :---: | :---: |",
            ]
        )

        for s in enriched_scores:
            plat = s["platform"]
            prof_path = Path("data/platforms") / plat / "profile.yaml"
            bench = {}
            if prof_path.exists():
                try:
                    with open(prof_path, "r", encoding="utf-8") as pf:
                        bench = yaml.safe_load(pf).get("benchmarks", {})
                except Exception:
                    pass

            # rethink
            r_val = bench.get("rethink_p2p_score")
            r_str = f"**{r_val}**" if r_val is not None else "-"
            if (
                bench.get("rethink_p2p_rank")
                and bench.get("rethink_p2p_rank") != "Nicht gelistet"
            ):
                r_str += f" ({bench.get('rethink_p2p_rank')})"
            if (
                bench.get("rethink_p2p_red_flags")
                and bench.get("rethink_p2p_red_flags") != "0"
            ):
                r_str += f" `RF: {bench.get('rethink_p2p_red_flags')}`"

            # p2p game
            g_val = bench.get("p2p_game_score")
            g_str = f"**{g_val}**" if g_val is not None else "-"
            if (
                bench.get("p2p_game_rank")
                and bench.get("p2p_game_rank") != "Nicht gelistet"
            ):
                g_str += f" ({bench.get('p2p_game_rank')})"

            # p2p empire
            e_val = bench.get("p2p_empire_safety_score")
            e_str = f"**{e_val}**" if e_val is not None else "-"

            # wrobbel
            w_val = bench.get("lars_wrobbel_score")
            w_str = f"**{w_val}**" if w_val is not None else "-"

            fs_link = f"[{plat.capitalize()}](../factsheets/{plat}.md)"
            lines.append(
                f"| {fs_link} | **{s['net_score']}** | `{s['risk_class']}` | {r_str} | {g_str} | {e_str} | {w_str} |"
            )

        lines.extend(
            [
                "",
                "---",
                f"*Erstellt am {audit_date} durch das P2P Audit Scoring System.*",
            ]
        )

        target_file = self.output_dir / f"audit-ranking-{year_month}.md"
        with open(target_file, "w", encoding="utf-8") as f:
            f.write("\n".join(frontmatter + lines))

        return target_file
