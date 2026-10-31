#!/usr/bin/env python3
"""Prepare newsletter, ranking, and factsheet Markdown files for MkDocs publication.

Scans:
- data/newsletters/ -> mirrors latest edition to docs/index.md and archives to docs/archiv/
- data/rankings/    -> mirrors latest ranking to docs/rankings/index.md and archives to docs/rankings/
- data/factsheets/  -> mirrors platform factsheets to docs/factsheets/
"""

from __future__ import annotations

import argparse
import logging
import re
import shutil
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger("prepare_pages")

NEWSLETTER_PATTERN = re.compile(
    r"^newsletter-(?P<week>\d{4}-W\d{2})(?:\.v(?P<ver>\d+))?\.md$"
)
RANKING_PATTERN = re.compile(
    r"^audit-ranking-(?P<period>\d{4}-\d{2})(?:\.v(?P<ver>\d+))?\.md$"
)


def format_week_label(iso_week: str) -> str:
    """Format ISO week like '2026-W43' into human-friendly 'KW 43/2026'."""
    parts = iso_week.split("-W")
    if len(parts) == 2:
        year, week = parts
        return f"KW {int(week)}/{year}"
    return iso_week


def extract_platform_name(file_path: Path) -> str:
    """Extract platform_name from YAML frontmatter or fall back to title-cased stem."""
    try:
        content = file_path.read_text(encoding="utf-8")
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                data = yaml.safe_load(parts[1])
                if isinstance(data, dict) and data.get("platform_name"):
                    return str(data["platform_name"])
    except Exception:
        pass
    return file_path.stem.replace("-", " ").replace("_", " ").title()


def scan_newsletters(newsletters_dir: Path) -> dict[str, tuple[int, Path]]:
    """Scan newsletter directory and return highest version file for each ISO week."""
    if not newsletters_dir.exists():
        return {}

    grouped: dict[str, tuple[int, Path]] = {}
    for entry in newsletters_dir.iterdir():
        if not entry.is_file():
            continue
        match = NEWSLETTER_PATTERN.match(entry.name)
        if not match:
            continue
        week = match.group("week")
        raw_ver = match.group("ver")
        ver = int(raw_ver) if raw_ver is not None else 1

        if week not in grouped or ver > grouped[week][0]:
            grouped[week] = (ver, entry)

    return grouped


def scan_rankings(rankings_dir: Path) -> dict[str, tuple[int, Path]]:
    """Scan rankings directory and return highest version file for each period."""
    if not rankings_dir.exists():
        return {}

    grouped: dict[str, tuple[int, Path]] = {}
    for entry in rankings_dir.iterdir():
        if not entry.is_file():
            continue
        match = RANKING_PATTERN.match(entry.name)
        if not match:
            continue
        period = match.group("period")
        raw_ver = match.group("ver")
        ver = int(raw_ver) if raw_ver is not None else 1

        if period not in grouped or ver > grouped[period][0]:
            grouped[period] = (ver, entry)

    return grouped


def scan_factsheets(factsheets_dir: Path) -> list[tuple[str, Path]]:
    """Scan platform factsheets and return sorted list of (display_name, file_path)."""
    if not factsheets_dir.exists():
        return []

    items: list[tuple[str, Path]] = []
    for entry in factsheets_dir.glob("*.md"):
        if entry.is_file():
            name = extract_platform_name(entry)
            items.append((name, entry))

    items.sort(key=lambda x: x[0].lower())
    return items


def update_mkdocs_nav(
    mkdocs_file: Path,
    sorted_weeks: list[str],
    sorted_periods: list[str],
    factsheets: list[tuple[str, Path]],
) -> None:
    """Update nav section in mkdocs.yml with newsletters, rankings, and factsheets."""
    if not mkdocs_file.exists():
        return

    with open(mkdocs_file, "r", encoding="utf-8") as f:
        config: dict[str, Any] = yaml.safe_load(f) or {}

    nav: list[dict[str, Any]] = []

    # 1. Newsletter Section
    if sorted_weeks:
        newest_week = sorted_weeks[0]
        newest_label = f"Aktuelle Ausgabe ({format_week_label(newest_week)})"
        newsletter_archive: list[dict[str, str]] = [
            {format_week_label(w): f"archiv/newsletter-{w}.md"} for w in sorted_weeks
        ]
        nav.append(
            {
                "Newsletter": [
                    {newest_label: "index.md"},
                    {"Archiv": newsletter_archive},
                ]
            }
        )

    # 2. Ranking Section (kept at docs/rankings/ level for relative factsheet links)
    if sorted_periods:
        newest_period = sorted_periods[0]
        newest_rank_label = f"Aktuelles Ranking ({newest_period})"
        rankings_archive: list[dict[str, str]] = [
            {f"Ranking {p}": f"rankings/audit-ranking-{p}.md"} for p in sorted_periods
        ]
        nav.append(
            {
                "Audit-Ranking": [
                    {newest_rank_label: "rankings/index.md"},
                    {"Archiv": rankings_archive},
                ]
            }
        )

    # 3. Factsheets Section
    if factsheets:
        factsheet_entries: list[dict[str, str]] = [
            {name: f"factsheets/{path.name}"} for name, path in factsheets
        ]
        nav.append({"Factsheets": factsheet_entries})

    config["nav"] = nav

    with open(mkdocs_file, "w", encoding="utf-8") as f:
        yaml.safe_dump(
            config,
            f,
            sort_keys=False,
            allow_unicode=True,
            default_flow_style=False,
        )
    logger.info("Updated nav in %s", mkdocs_file)


def prepare_docs(
    newsletters_dir: Path,
    rankings_dir: Path,
    factsheets_dir: Path,
    docs_dir: Path,
    mkdocs_file: Path | None = None,
) -> tuple[list[str], list[str], int]:
    """Mirror newsletters, rankings, and factsheets to docs and update MkDocs config.

    Returns tuple: (sorted_weeks, sorted_ranking_periods, factsheet_count).
    """
    docs_dir.mkdir(parents=True, exist_ok=True)

    # 1. Process Newsletters
    grouped_nl = scan_newsletters(newsletters_dir)
    sorted_weeks = sorted(grouped_nl.keys(), reverse=True)
    if sorted_weeks:
        archive_dir = docs_dir / "archiv"
        archive_dir.mkdir(parents=True, exist_ok=True)

        newest_week = sorted_weeks[0]
        _, newest_nl_path = grouped_nl[newest_week]
        shutil.copy2(newest_nl_path, docs_dir / "index.md")

        for week in sorted_weeks:
            _, src_path = grouped_nl[week]
            shutil.copy2(src_path, archive_dir / f"newsletter-{week}.md")

    # 2. Process Rankings
    grouped_rank = scan_rankings(rankings_dir)
    sorted_periods = sorted(grouped_rank.keys(), reverse=True)
    if sorted_periods:
        rankings_docs = docs_dir / "rankings"
        rankings_docs.mkdir(parents=True, exist_ok=True)

        newest_period = sorted_periods[0]
        _, newest_rank_path = grouped_rank[newest_period]
        shutil.copy2(newest_rank_path, rankings_docs / "index.md")

        for period in sorted_periods:
            _, rank_src = grouped_rank[period]
            shutil.copy2(rank_src, rankings_docs / f"audit-ranking-{period}.md")

    # 3. Process Factsheets
    factsheets = scan_factsheets(factsheets_dir)
    if factsheets:
        factsheets_docs = docs_dir / "factsheets"
        factsheets_docs.mkdir(parents=True, exist_ok=True)
        for _, path in factsheets:
            shutil.copy2(path, factsheets_docs / path.name)

    # 4. Update MkDocs Config
    if mkdocs_file is not None and mkdocs_file.exists():
        update_mkdocs_nav(mkdocs_file, sorted_weeks, sorted_periods, factsheets)

    return sorted_weeks, sorted_periods, len(factsheets)


def main() -> None:
    """CLI entrypoint for docs preparation."""
    parser = argparse.ArgumentParser(
        description="Prepare newsletter, ranking, and factsheet files for GitHub Pages."
    )
    parser.add_argument(
        "--newsletters-dir",
        type=Path,
        default=Path("data/newsletters"),
        help="Path to newsletters directory",
    )
    parser.add_argument(
        "--rankings-dir",
        type=Path,
        default=Path("data/rankings"),
        help="Path to rankings directory",
    )
    parser.add_argument(
        "--factsheets-dir",
        type=Path,
        default=Path("data/factsheets"),
        help="Path to factsheets directory",
    )
    parser.add_argument(
        "--docs-dir",
        type=Path,
        default=Path("docs"),
        help="Path to output docs directory",
    )
    parser.add_argument(
        "--mkdocs-file",
        type=Path,
        default=Path("mkdocs.yml"),
        help="Path to mkdocs.yml",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    weeks, periods, fs_count = prepare_docs(
        newsletters_dir=args.newsletters_dir,
        rankings_dir=args.rankings_dir,
        factsheets_dir=args.factsheets_dir,
        docs_dir=args.docs_dir,
        mkdocs_file=args.mkdocs_file,
    )
    print(
        f"Prepared: {len(weeks)} newsletters, {len(periods)} rankings, {fs_count} factsheets."
    )


if __name__ == "__main__":
    main()
