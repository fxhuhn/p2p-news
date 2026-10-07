"""
Migrations- und Verifikations-Script für Option 1: Hybrider Platin-Store.

Migriert und verifiziert:
1. data/items/*.json -> SQLite `items` Tabelle
2. data/snapshots/pages/*.md -> SQLite `snapshots` Tabelle (zlib-komprimiert)
3. data/runs/*/llm/*_raw.json.gz -> SQLite `runs` Tabelle

Bietet atomare Hash-Integritätsprüfung und sicheres Cleanup alter Einzeldateien.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

from item_models import NewsItem
from manifest_manager import ManifestManager
from snapshot_manager import SnapshotManager
from storage_sqlite import SQLiteStore

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("storage_migration")


class StorageMigrator:
    """Führt Migration, Integritätsprüfung und Bereinigung durch."""

    def __init__(
        self, data_dir: Path | str = "data", db_path: Path | str = "data/p2p_archive.db"
    ) -> None:
        self.data_dir = Path(data_dir)
        self.db_path = Path(db_path)
        self.items_dir = self.data_dir / "items"
        self.snapshots_dir = self.data_dir / "snapshots" / "pages"
        self.runs_dir = self.data_dir / "runs"
        self.store = SQLiteStore(self.db_path)

    def migrate_items(self) -> int:
        """Migriert alle diskreten NewsItems aus data/items/*.json."""
        if not self.items_dir.exists():
            logger.info("Kein items-Verzeichnis gefunden unter %s", self.items_dir)
            return 0

        item_files = [
            p for p in sorted(self.items_dir.glob("*.json")) if p.name != "items.jsonl"
        ]
        logger.info("Gefunden: %d Item-Dateien zur Migration.", len(item_files))

        items: list[NewsItem] = []
        for p in item_files:
            try:
                items.append(NewsItem.load(p))
            except Exception as exc:
                logger.error("Fehler beim Laden von %s: %s", p, exc)

        count = self.store.batch_upsert_items(items)
        logger.info("Erfolgreich %d Items in SQLite migriert.", count)
        return count

    def migrate_snapshots(self) -> int:
        """Migriert alle Rohseiten-Snapshots aus data/snapshots/pages/*.md komprimiert in SQLite."""
        if not self.snapshots_dir.exists():
            logger.info(
                "Kein snapshots-Verzeichnis gefunden unter %s", self.snapshots_dir
            )
            return 0

        snap_files = sorted(self.snapshots_dir.glob("*.md"))
        logger.info("Gefunden: %d Snapshot-Dateien zur Migration.", len(snap_files))

        count = 0
        for p in snap_files:
            expected_hash = p.stem
            text = p.read_text(encoding="utf-8")

            # Header parsen
            url = ""
            lines = text.splitlines(keepends=True)
            content_lines = []
            for line in lines:
                if line.startswith("<!-- snapshot_url:"):
                    url = (
                        line.replace("<!-- snapshot_url:", "")
                        .replace("-->", "")
                        .strip()
                    )
                elif line.startswith("<!-- snapshot_hash:"):
                    pass
                else:
                    content_lines.append(line)

            content = "".join(content_lines).strip()
            # SHA-256 Validierung vor dem Speichern
            computed_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
            if computed_hash != expected_hash:
                logger.warning(
                    "Hash-Abweichung bei Snapshot %s: berechnet %s != stem %s",
                    p.name,
                    computed_hash,
                    expected_hash,
                )

            mtime = datetime.fromtimestamp(
                p.stat().st_mtime, tz=timezone.utc
            ).isoformat()
            self.store.save_snapshot(
                snapshot_hash=expected_hash,
                content=content,
                original_url=url,
                created_at=mtime,
            )
            count += 1

        logger.info("Erfolgreich %d Snapshots komprimiert in SQLite archiviert.", count)
        return count

    def migrate_runs(self) -> int:
        """Migriert alle LLM-Runs aus data/runs/*/llm/*_raw.json.gz in SQLite."""
        if not self.runs_dir.exists():
            logger.info("Kein runs-Verzeichnis gefunden unter %s", self.runs_dir)
            return 0

        run_files = sorted(self.runs_dir.glob("run_*/llm/*_raw.json.gz"))
        logger.info("Gefunden: %d Run-Dateien zur Migration.", len(run_files))

        count = 0
        for gz in run_files:
            try:
                raw_bytes = gz.read_bytes()
                payload = json.loads(gzip.decompress(raw_bytes).decode("utf-8"))
                run_id = payload.get("run_id") or gz.parent.parent.name
                stage = payload.get("stage") or (1 if "stage1" in gz.name else 2)
                iso_week = run_id.split("_")[1] if "_" in run_id else ""

                self.store.save_run(
                    run_id=run_id,
                    stage=stage,
                    iso_week=iso_week,
                    model_version=payload.get("model_version", ""),
                    duration_s=payload.get("duration_seconds", 0.0),
                    usage=payload.get("usage", {}),
                    prompt=payload.get("prompt", ""),
                    raw_response=payload.get("raw_response", ""),
                    created_at=payload.get("timestamp"),
                )
                count += 1
            except Exception as exc:
                logger.error("Fehler beim Migrieren von Run %s: %s", gz, exc)

        logger.info("Erfolgreich %d LLM-Runs in SQLite archiviert.", count)
        return count

    def verify_all(self) -> tuple[bool, list[str]]:
        """
        Führt vollständige kryptographische Verifikation aller Daten in SQLite durch.
        """
        errors: list[str] = []
        logger.info("=== Starte kryptographische Verifikation ===")

        # 1. Items prüfen
        item_files = (
            [
                p
                for p in sorted(self.items_dir.glob("*.json"))
                if p.name != "items.jsonl"
            ]
            if self.items_dir.exists()
            else []
        )
        db_items = self.store.get_all_items()
        logger.info(
            "Items-Prüfung: %d Dateien vs. %d Einträge in SQLite.",
            len(item_files),
            len(db_items),
        )

        if len(item_files) > 0 and len(db_items) < len(item_files):
            errors.append(
                f"Item-Anzahl fehlerhaft: {len(db_items)} in DB < {len(item_files)} auf Platte"
            )

        db_items_map = {item.item_id: item for item in db_items}
        for p in item_files:
            file_item = NewsItem.load(p)
            db_item = db_items_map.get(file_item.item_id)
            if not db_item:
                errors.append(f"Item {file_item.item_id} fehlt in SQLite")
                continue

            # SHA-256 des Inhalts prüfen
            computed_hash = hashlib.sha256(
                db_item.content_plain.encode("utf-8")
            ).hexdigest()
            if computed_hash != file_item.item_content_hash:
                errors.append(
                    f"Item {file_item.item_id}: Content-Hash Mismatch {computed_hash} != {file_item.item_content_hash}"
                )

            if db_item.page_snapshot_hash != file_item.page_snapshot_hash:
                errors.append(f"Item {file_item.item_id}: Snapshot-Hash Mismatch")

            if db_item.first_seen_at != file_item.first_seen_at:
                errors.append(f"Item {file_item.item_id}: first_seen_at Mismatch")

        # 2. Snapshots prüfen
        snap_files = (
            sorted(self.snapshots_dir.glob("*.md"))
            if self.snapshots_dir.exists()
            else []
        )
        db_snap_hashes = self.store.get_all_snapshot_hashes()
        logger.info(
            "Snapshot-Prüfung: %d Dateien vs. %d Einträge in SQLite.",
            len(snap_files),
            len(db_snap_hashes),
        )

        snap_mgr = SnapshotManager(base_dir=self.data_dir / "snapshots")
        for p in snap_files:
            expected_hash = p.stem
            db_content = self.store.get_snapshot(expected_hash)
            if db_content is None:
                errors.append(f"Snapshot {expected_hash} fehlt in SQLite")
                continue

            file_content = snap_mgr.get_page_snapshot(expected_hash)
            if file_content != db_content:
                errors.append(
                    f"Snapshot {expected_hash}: Inhalt in SQLite weicht von Datei ab"
                )

            computed_hash = hashlib.sha256(db_content.encode("utf-8")).hexdigest()
            if computed_hash != expected_hash:
                errors.append(
                    f"Snapshot {expected_hash}: SHA-256 Prüfsumme ungültig ({computed_hash})"
                )

        # 3. Runs prüfen
        run_files = (
            sorted(self.runs_dir.glob("run_*/llm/*_raw.json.gz"))
            if self.runs_dir.exists()
            else []
        )
        db_runs = self.store.get_all_runs()
        logger.info(
            "Runs-Prüfung: %d Dateien vs. %d Einträge in SQLite.",
            len(run_files),
            len(db_runs),
        )
        if len(run_files) > 0 and len(db_runs) < len(run_files):
            errors.append(
                f"Runs-Anzahl fehlerhaft: {len(db_runs)} in DB < {len(run_files)} auf Platte"
            )

        # 4. Manifest-Integrität prüfen
        manifest_mgr = ManifestManager(digests_dir=self.data_dir / "digests")
        for mf_path in sorted(self.data_dir.glob("digests/*.manifest.json")):
            is_valid, mf_errors = manifest_mgr.verify_integrity(mf_path)
            if not is_valid:
                errors.extend([f"Manifest {mf_path.name}: {e}" for e in mf_errors])
            else:
                logger.info("Manifest %s ist intakt.", mf_path.name)

        is_success = len(errors) == 0
        if is_success:
            logger.info(
                "=== VERIFIKATION ERFOLGREICH: 100%% Datenintegrität bestätigt! ==="
            )
        else:
            logger.error(
                "=== VERIFIKATION FEHLGESCHLAGEN: %d Fehler gefunden! ===", len(errors)
            )
            for err in errors[:10]:
                logger.error("  - %s", err)

        return is_success, errors

    def cleanup_legacy_files(self) -> dict[str, int]:
        """
        Löscht verifizierte redundante Einzeldateien zur Entlastung des Dateisystems.
        Bewahrt:
        - data/p2p_archive.db
        - data/items/items.jsonl (als kompakter Index)
        - data/digests/*
        - data/newsletters/*
        - data/watermark.json
        """
        logger.info("=== Starte Bereinigung redundanter Einzeldateien ===")
        deleted_counts = {"items": 0, "snapshots": 0, "runs": 0}

        # 1. Items löschen
        if self.items_dir.exists():
            for p in self.items_dir.glob("*.json"):
                if p.name != "items.jsonl":
                    p.unlink()
                    deleted_counts["items"] += 1

        # 2. Snapshots löschen
        if self.snapshots_dir.exists():
            for p in self.snapshots_dir.glob("*.md"):
                p.unlink()
                deleted_counts["snapshots"] += 1

        # 3. Runs bereinigen
        if self.runs_dir.exists():
            for gz in self.runs_dir.glob("run_*/llm/*_raw.json.gz"):
                gz.unlink()
                deleted_counts["runs"] += 1
            # Leere llm und run-Ordner entfernen
            for llm_dir in self.runs_dir.glob("run_*/llm"):
                try:
                    llm_dir.rmdir()
                except OSError:
                    pass
            for r_dir in self.runs_dir.glob("run_*"):
                try:
                    r_dir.rmdir()
                except OSError:
                    pass

        logger.info(
            "Bereinigung abgeschlossen: %d Items, %d Snapshots, %d Runs entfernt.",
            deleted_counts["items"],
            deleted_counts["snapshots"],
            deleted_counts["runs"],
        )
        return deleted_counts


def main() -> int:
    parser = argparse.ArgumentParser(description="P2P News Storage Migrator & Verifier")
    parser.add_argument("--data-dir", default="data", help="Pfad zum data Verzeichnis")
    parser.add_argument(
        "--db-path", default="data/p2p_archive.db", help="Pfad zur SQLite-Datenbank"
    )
    parser.add_argument(
        "--migrate", action="store_true", help="Führt die Migration in SQLite durch"
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Führt die kryptographische Verifikation durch",
    )
    parser.add_argument(
        "--cleanup", action="store_true", help="Löscht verifizierte Einzeldateien"
    )
    parser.add_argument(
        "--stats", action="store_true", help="Gibt Speicherstatistiken aus"
    )
    args = parser.parse_args()

    migrator = StorageMigrator(data_dir=args.data_dir, db_path=args.db_path)

    if args.migrate:
        migrator.migrate_items()
        migrator.migrate_snapshots()
        migrator.migrate_runs()

    if args.verify:
        success, errors = migrator.verify_all()
        if not success:
            logger.error("Verifikation fehlgeschlagen!")
            return 1

    if args.cleanup:
        # Sicherheitsprüfung: erst verifizieren, bevor gelöscht wird!
        success, errors = migrator.verify_all()
        if not success:
            logger.error(
                "Cleanup abgebrochen: Verifikation ist nicht zu 100%% bestanden!"
            )
            return 1
        migrator.cleanup_legacy_files()

    if args.stats or (not args.migrate and not args.verify and not args.cleanup):
        stats = migrator.store.stats()
        print("\n--- P2P News Archiv-Statistiken ---")
        print(f"Datenbank:       {stats['db_path']} ({stats['db_size_mb']} MB)")
        print(f"Items:           {stats['items_count']}")
        print(f"Snapshots:       {stats['snapshots_count']} (zlib-komprimiert)")
        print(f"LLM-Runs:        {stats['runs_count']}")
        print("-----------------------------------\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
