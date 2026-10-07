"""
Item-Store zur persistenten Verwaltung von NewsItems (Stufe 0).

Architektur (Option 1: Hybrider Platin-Store):
- Nutzt dateibasiertes SQLite-Backend (data/p2p_archive.db) für skalierbare Massendaten
- Wahrung von first_seen_at über Wiederholungs-Scans hinweg (Revisionsstabilität)
- Exakte Zustandserkennung (neu / geändert / unverändert) basierend auf item_content_hash
- Baseline-Schutz für historische Altbestände
- Optionale Rückwärtskompatibilität zu diskreten Flat-Files (items/*.json)
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from item_models import NewsItem
from storage_sqlite import SQLiteStore

logger = logging.getLogger("item_store")


class ItemStore:
    """Verwaltet diskrete NewsItems mit Revisionshistorie und Zustandserkennung."""

    def __init__(
        self,
        items_dir: Path | str = "data/items",
        db_path: Path | str | None = None,
        sync_flat_files: bool | None = None,
    ) -> None:
        self.items_dir = Path(items_dir)
        self.items_dir.mkdir(parents=True, exist_ok=True)
        self.index_file = self.items_dir / "items.jsonl"

        # SQLite-Integration (Option 1: Hybrider Platin-Store)
        if db_path is not None:
            self.sqlite_store: SQLiteStore | None = SQLiteStore(db_path)
        else:
            candidate = self.items_dir.parent / "p2p_archive.db"
            if candidate.exists():
                self.sqlite_store = SQLiteStore(candidate)
            elif Path("data/p2p_archive.db").exists() and (
                self.items_dir == Path("data/items")
                or str(self.items_dir).endswith("data/items")
            ):
                self.sqlite_store = SQLiteStore("data/p2p_archive.db")
            else:
                self.sqlite_store = None

        if sync_flat_files is not None:
            self.sync_flat_files = sync_flat_files
        else:
            self.sync_flat_files = self.sqlite_store is None

    def get_item_path(self, item_id: str) -> Path:
        return self.items_dir / f"{item_id}.json"

    def exists(self, item_id: str) -> bool:
        if self.sqlite_store:
            return self.sqlite_store.exists_item(item_id)
        return self.get_item_path(item_id).exists()

    def get_item(self, item_id: str) -> NewsItem | None:
        if self.sqlite_store:
            item = self.sqlite_store.get_item(item_id)
            if item:
                return item
        path = self.get_item_path(item_id)
        if not path.exists():
            return None
        return NewsItem.load(path)

    def upsert_item(
        self,
        item: NewsItem,
        is_baseline: bool = False,
    ) -> tuple[NewsItem, str]:
        """
        Fügt ein Item ein oder aktualisiert es.

        Rückgabe:
        (aktualisiertes_item, status) mit status in ["neu", "unverändert", "geändert"]
        """
        if self.sqlite_store:
            updated_item, status = self.sqlite_store.upsert_item(
                item, is_baseline=is_baseline
            )
            if self.sync_flat_files:
                updated_item.save(self.items_dir)
                if status == "neu":
                    self._append_to_index(updated_item)
                elif status == "geändert":
                    self._rebuild_index()
            return updated_item, status

        # Flat-File Fallback (z. B. für isolierte Temp-Tests)
        existing = self.get_item(item.item_id)
        now_iso = datetime.now(timezone.utc).isoformat()

        if existing is None:
            status = "neu"
            if not item.first_seen_at:
                item.first_seen_at = now_iso
            if not item.last_seen_at:
                item.last_seen_at = now_iso
            if is_baseline:
                item.is_baseline = True
            item.save(self.items_dir)
            self._append_to_index(item)
            return item, status

        # Existierendes Item
        item.first_seen_at = existing.first_seen_at  # Unveränderlich bewahren!
        item.last_seen_at = now_iso
        item.is_baseline = existing.is_baseline

        if existing.item_content_hash != item.item_content_hash:
            status = "geändert"
            item.save(self.items_dir)
            self._rebuild_index()
        else:
            status = "unverändert"
            # Aktualisiere nur last_seen_at
            item.save(self.items_dir)

        return item, status

    def get_all_items(self) -> list[NewsItem]:
        """Gibt alle gespeicherten Items zurück."""
        if self.sqlite_store:
            sqlite_items = self.sqlite_store.get_all_items()
            if sqlite_items:
                return sqlite_items
        items: list[NewsItem] = []
        for path in sorted(self.items_dir.glob("*.json")):
            if path.name == "items.jsonl":
                continue
            try:
                items.append(NewsItem.load(path))
            except Exception as exc:
                logger.warning("Konnte Item %s nicht laden: %s", path, exc)
        return items

    def get_items_for_period(
        self,
        watermark_from_iso: str | None,
        watermark_to_iso: str,
        include_baseline: bool = False,
    ) -> list[NewsItem]:
        """
        Selektiert Items für einen Newsletter-Lauf nach Exactly-Once Semantik.
        Bedingung:
        first_seen_at > watermark_from_iso AND first_seen_at <= watermark_to_iso
        """
        if self.sqlite_store:
            return self.sqlite_store.get_items_for_period(
                watermark_from_iso=watermark_from_iso,
                watermark_to_iso=watermark_to_iso,
                include_baseline=include_baseline,
            )
        all_items = self.get_all_items()
        selected: list[NewsItem] = []

        to_dt = datetime.fromisoformat(watermark_to_iso)
        from_dt = (
            datetime.fromisoformat(watermark_from_iso) if watermark_from_iso else None
        )

        for item in all_items:
            if not include_baseline and item.is_baseline:
                continue

            item_dt = datetime.fromisoformat(item.first_seen_at)

            # Prüfe Zeitfenster
            if from_dt and item_dt <= from_dt:
                continue
            if item_dt > to_dt:
                continue

            selected.append(item)

        return selected

    def _append_to_index(self, item: NewsItem) -> None:
        summary = {
            "item_id": item.item_id,
            "provider": item.provider,
            "title": item.title,
            "url": item.url,
            "published_date": item.published_date,
            "first_seen_at": item.first_seen_at,
            "item_content_hash": item.item_content_hash,
            "platforms": item.platforms,
            "topics": item.topics,
            "is_baseline": item.is_baseline,
        }
        with open(self.index_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(summary, ensure_ascii=False) + "\n")

    def _rebuild_index(self) -> None:
        all_items = self.get_all_items()
        with open(self.index_file, "w", encoding="utf-8") as f:
            for item in all_items:
                summary = {
                    "item_id": item.item_id,
                    "provider": item.provider,
                    "title": item.title,
                    "url": item.url,
                    "published_date": item.published_date,
                    "first_seen_at": item.first_seen_at,
                    "item_content_hash": item.item_content_hash,
                    "platforms": item.platforms,
                    "topics": item.topics,
                    "is_baseline": item.is_baseline,
                }
                f.write(json.dumps(summary, ensure_ascii=False) + "\n")
