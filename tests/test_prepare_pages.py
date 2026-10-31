"""Unit tests for scripts/prepare_pages.py."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from scripts.prepare_pages import (
    extract_platform_name,
    format_week_label,
    prepare_docs,
    scan_factsheets,
    scan_newsletters,
    scan_rankings,
)


def test_format_week_label() -> None:
    assert format_week_label("2026-W43") == "KW 43/2026"
    assert format_week_label("2026-W05") == "KW 5/2026"
    assert format_week_label("invalid-week") == "invalid-week"


def test_extract_platform_name(tmp_path: Path) -> None:
    # With frontmatter platform_name
    p1 = tmp_path / "inrento.md"
    p1.write_text(
        "---\nplatform: inrento\nplatform_name: InRento\n---\n# Content",
        encoding="utf-8",
    )
    assert extract_platform_name(p1) == "InRento"

    # Without frontmatter or missing key
    p2 = tmp_path / "custom_platform.md"
    p2.write_text("# Simple heading", encoding="utf-8")
    assert extract_platform_name(p2) == "Custom Platform"


def test_scan_newsletters_version_resolution(tmp_path: Path) -> None:
    nl_dir = tmp_path / "newsletters"
    nl_dir.mkdir()

    (nl_dir / "newsletter-2026-W40.md").write_text("# W40", encoding="utf-8")
    (nl_dir / "newsletter-2026-W41.md").write_text("# W41 v1", encoding="utf-8")
    (nl_dir / "newsletter-2026-W41.v2.md").write_text("# W41 v2", encoding="utf-8")
    (nl_dir / "newsletter-2026-W41.v3.md").write_text("# W41 v3", encoding="utf-8")
    (nl_dir / "newsletter-draft.md").write_text("# Draft", encoding="utf-8")

    scanned = scan_newsletters(nl_dir)
    assert set(scanned.keys()) == {"2026-W40", "2026-W41"}
    assert scanned["2026-W41"] == (3, nl_dir / "newsletter-2026-W41.v3.md")


def test_scan_rankings_and_factsheets(tmp_path: Path) -> None:
    rank_dir = tmp_path / "rankings"
    fs_dir = tmp_path / "factsheets"
    rank_dir.mkdir()
    fs_dir.mkdir()

    (rank_dir / "audit-ranking-2026-09.md").write_text("# Sept", encoding="utf-8")
    (rank_dir / "audit-ranking-2026-10.md").write_text("# Oct", encoding="utf-8")
    (rank_dir / "audit-ranking-2026-10.v2.md").write_text("# Oct v2", encoding="utf-8")
    (rank_dir / "other.md").write_text("ignore", encoding="utf-8")

    (fs_dir / "mintos.md").write_text(
        "---\nplatform_name: Mintos\n---\n", encoding="utf-8"
    )
    (fs_dir / "afranga.md").write_text(
        "---\nplatform_name: Afranga\n---\n", encoding="utf-8"
    )

    rankings = scan_rankings(rank_dir)
    assert set(rankings.keys()) == {"2026-09", "2026-10"}
    assert rankings["2026-10"] == (2, rank_dir / "audit-ranking-2026-10.v2.md")

    factsheets = scan_factsheets(fs_dir)
    assert [name for name, _ in factsheets] == ["Afranga", "Mintos"]


def test_prepare_docs_full_pipeline(tmp_path: Path) -> None:
    nl_dir = tmp_path / "newsletters"
    rank_dir = tmp_path / "rankings"
    fs_dir = tmp_path / "factsheets"
    docs_dir = tmp_path / "docs"
    mkdocs_file = tmp_path / "mkdocs.yml"

    nl_dir.mkdir()
    rank_dir.mkdir()
    fs_dir.mkdir()

    (nl_dir / "newsletter-2026-W42.md").write_text("W42 NL", encoding="utf-8")
    (rank_dir / "audit-ranking-2026-10.md").write_text("Oct Rank", encoding="utf-8")
    (fs_dir / "inrento.md").write_text(
        "---\nplatform_name: InRento\n---\n", encoding="utf-8"
    )

    initial_config: dict[str, Any] = {"site_name": "Test Site"}
    with open(mkdocs_file, "w", encoding="utf-8") as f:
        yaml.safe_dump(initial_config, f)

    weeks, periods, fs_count = prepare_docs(
        newsletters_dir=nl_dir,
        rankings_dir=rank_dir,
        factsheets_dir=fs_dir,
        docs_dir=docs_dir,
        mkdocs_file=mkdocs_file,
    )

    assert weeks == ["2026-W42"]
    assert periods == ["2026-10"]
    assert fs_count == 1

    # Verify copied files
    assert (docs_dir / "index.md").read_text(encoding="utf-8") == "W42 NL"
    assert (docs_dir / "archiv" / "newsletter-2026-W42.md").exists()
    assert (docs_dir / "rankings" / "index.md").read_text(
        encoding="utf-8"
    ) == "Oct Rank"
    assert (docs_dir / "rankings" / "audit-ranking-2026-10.md").read_text(
        encoding="utf-8"
    ) == "Oct Rank"
    assert (docs_dir / "factsheets" / "inrento.md").exists()

    # Verify nav structure in mkdocs.yml
    with open(mkdocs_file, "r", encoding="utf-8") as f:
        updated: dict[str, Any] = yaml.safe_load(f)

    nav = updated["nav"]
    assert len(nav) == 3
    assert "Newsletter" in nav[0]
    assert "Audit-Ranking" in nav[1]
    assert "Factsheets" in nav[2]
