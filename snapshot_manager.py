"""
Snapshot-Manager für inhaltsadressierte, unveränderliche Quell-Snapshots (Write-Once).

Architektur (Option 1: Hybrider Platin-Store):
- Nutzt dateibasiertes SQLite-Backend (data/p2p_archive.db) mit zlib-Kompression
- Wahrung des deterministischen SHA-256 Hashs als Primärschlüssel
- Optionale Rückwärtskompatibilität zu diskreten Flat-Files (snapshots/pages/<sha256>.md)
"""

from __future__ import annotations

import hashlib
import logging
from pathlib import Path

from storage_sqlite import SQLiteStore

logger = logging.getLogger("snapshot_manager")


class SnapshotManager:
    """Verwaltet inhaltsadressierte Rohseiten-Snapshots zur revisionssicheren Beweissicherung."""

    def __init__(
        self,
        base_dir: Path | str = "data/snapshots",
        db_path: Path | str | None = None,
        sync_flat_files: bool | None = None,
    ) -> None:
        self.base_dir = Path(base_dir)
        self.pages_dir = self.base_dir / "pages"
        self.pages_dir.mkdir(parents=True, exist_ok=True)

        if db_path is not None:
            self.sqlite_store: SQLiteStore | None = SQLiteStore(db_path)
        else:
            candidate = self.base_dir.parent / "p2p_archive.db"
            if candidate.exists():
                self.sqlite_store = SQLiteStore(candidate)
            elif Path("data/p2p_archive.db").exists() and (
                self.base_dir == Path("data/snapshots")
                or str(self.base_dir).endswith("data/snapshots")
            ):
                self.sqlite_store = SQLiteStore("data/p2p_archive.db")
            else:
                self.sqlite_store = None

        if sync_flat_files is not None:
            self.sync_flat_files = sync_flat_files
        else:
            self.sync_flat_files = self.sqlite_store is None

    @staticmethod
    def compute_hash(content: str) -> str:
        """Berechnet den deterministischen SHA-256 Hash des Inhalts."""
        return hashlib.sha256(content.strip().encode("utf-8")).hexdigest()

    def save_page_snapshot(
        self, content: str, original_url: str = ""
    ) -> tuple[str, Path, bool]:
        """
        Speichert den Rohinhalt als Write-Once-Eintrag.

        Gibt zurück:
        (content_hash, file_path, was_created)
        """
        content_hash = self.compute_hash(content)
        file_path = self.pages_dir / f"{content_hash}.md"
        was_created = False

        if self.sqlite_store:
            was_created = self.sqlite_store.save_snapshot(
                snapshot_hash=content_hash,
                content=content,
                original_url=original_url,
            )

        if self.sync_flat_files:
            if not file_path.exists():
                header = f"<!-- snapshot_url: {original_url} -->\n<!-- snapshot_hash: {content_hash} -->\n"
                file_path.write_text(header + content, encoding="utf-8")
                if not self.sqlite_store:
                    was_created = True
            elif not self.sqlite_store:
                was_created = False

        return content_hash, file_path, was_created

    def get_page_snapshot(self, content_hash: str) -> str | None:
        """Lädt den Snapshot-Inhalt für einen gegebenen Hash."""
        if self.sqlite_store:
            content = self.sqlite_store.get_snapshot(content_hash)
            if content is not None:
                return content.strip()

        file_path = self.pages_dir / f"{content_hash}.md"
        if not file_path.exists():
            return None
        text = file_path.read_text(encoding="utf-8")
        lines = text.splitlines(keepends=True)
        content_lines = [
            line for line in lines if not line.startswith("<!-- snapshot_")
        ]
        return "".join(content_lines).strip()
