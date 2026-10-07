"""
Zentraler SQLite-Speicher für Items, komprimierte Roh-Snapshots und LLM-Runs (Stufe 0 & 2).

Architektur (Option 1: Hybrider Platin-Store):
- Bündelt tausende Kleinstdateien in einer einzigen dateibasierten SQLite-Datenbank: data/p2p_archive.db
- WAL-Modus (Write-Ahead-Logging) für maximale Lese-/Schreib-Performance und Crash-Resistenz
- Komprimiert Roh-Snapshots transparent als BLOBs via zlib (70-80 % Platzersparnis)
- Wahrung aller kryptographischen Hashes (item_id, item_content_hash, page_snapshot_hash)
"""

from __future__ import annotations

import json
import logging
import sqlite3
import zlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from item_models import NewsItem

logger = logging.getLogger("storage_sqlite")


class SQLiteStore:
    """Verwaltet Items, komprimierte Snapshots und LLM-Runs in einer SQLite-Datenbank."""

    def __init__(self, db_path: Path | str = "data/p2p_archive.db") -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute("PRAGMA synchronous = NORMAL;")
        return conn

    def _init_db(self) -> None:
        with self._get_connection() as conn:
            conn.executescript(
                """
                -- Items Tabelle
                CREATE TABLE IF NOT EXISTS items (
                    item_id TEXT PRIMARY KEY,
                    provider TEXT NOT NULL,
                    source_tier TEXT NOT NULL,
                    url TEXT,
                    title TEXT NOT NULL,
                    published_date TEXT,
                    first_seen_at TEXT NOT NULL,
                    last_seen_at TEXT NOT NULL,
                    item_content_hash TEXT NOT NULL,
                    page_snapshot_hash TEXT NOT NULL,
                    platforms_json TEXT NOT NULL,
                    topics_json TEXT NOT NULL,
                    sentiment TEXT,
                    severity TEXT,
                    content_raw TEXT,
                    content_plain TEXT NOT NULL,
                    is_baseline INTEGER NOT NULL DEFAULT 0
                );

                CREATE INDEX IF NOT EXISTS idx_items_first_seen ON items(first_seen_at);
                CREATE INDEX IF NOT EXISTS idx_items_published ON items(published_date);
                CREATE INDEX IF NOT EXISTS idx_items_provider ON items(provider);
                CREATE INDEX IF NOT EXISTS idx_items_source_tier ON items(source_tier);

                -- Snapshots Tabelle (inhaltsadressiert & komprimiert)
                CREATE TABLE IF NOT EXISTS snapshots (
                    snapshot_hash TEXT PRIMARY KEY,
                    original_url TEXT,
                    content_compressed BLOB NOT NULL,
                    created_at TEXT NOT NULL
                );

                -- LLM Runs Tabelle
                CREATE TABLE IF NOT EXISTS runs (
                    run_id TEXT NOT NULL,
                    stage INTEGER NOT NULL,
                    iso_week TEXT,
                    model_version TEXT,
                    duration_seconds REAL,
                    usage_json TEXT,
                    prompt TEXT,
                    raw_response TEXT,
                    created_at TEXT NOT NULL,
                    PRIMARY KEY (run_id, stage)
                );

                -- Platform Audit Scores Tabelle (Historisierung & Delta-Tracking)
                CREATE TABLE IF NOT EXISTS platform_audit_scores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    platform TEXT NOT NULL,
                    audit_date TEXT NOT NULL,
                    raw_score INTEGER NOT NULL,
                    net_score INTEGER NOT NULL,
                    risk_class TEXT NOT NULL,
                    pillar_1 INTEGER NOT NULL,
                    pillar_2 INTEGER NOT NULL,
                    pillar_3 INTEGER NOT NULL,
                    pillar_4 INTEGER NOT NULL,
                    malus_total INTEGER NOT NULL,
                    malus_json TEXT NOT NULL,
                    has_conflict INTEGER NOT NULL DEFAULT 0,
                    conflict_notes TEXT,
                    data_gaps_json TEXT,
                    sourcing_strategy TEXT NOT NULL,
                    factsheet_path TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    UNIQUE(platform, audit_date)
                );

                CREATE INDEX IF NOT EXISTS idx_audit_platform_date ON platform_audit_scores(platform, audit_date);
                CREATE INDEX IF NOT EXISTS idx_audit_date ON platform_audit_scores(audit_date);
                """
            )

    # =========================================================================
    # Items API
    # =========================================================================

    def get_item(self, item_id: str) -> NewsItem | None:
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM items WHERE item_id = ?", (item_id,)
            ).fetchone()
            if not row:
                return None
            return self._row_to_item(row)

    def exists_item(self, item_id: str) -> bool:
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT 1 FROM items WHERE item_id = ?", (item_id,)
            ).fetchone()
            return row is not None

    def upsert_item(
        self, item: NewsItem, is_baseline: bool = False
    ) -> tuple[NewsItem, str]:
        """
        Fügt ein Item ein oder aktualisiert es idempotenz- und revisionssicher.
        Bewahrt first_seen_at unverändert.
        """
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
            self._insert_item(item)
            return item, status

        # Existierendes Item
        item.first_seen_at = existing.first_seen_at
        item.last_seen_at = now_iso
        item.is_baseline = existing.is_baseline

        if existing.item_content_hash != item.item_content_hash:
            status = "geändert"
        else:
            status = "unverändert"

        self._update_item(item)
        return item, status

    def _insert_item(self, item: NewsItem) -> None:
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO items (
                    item_id, provider, source_tier, url, title, published_date,
                    first_seen_at, last_seen_at, item_content_hash, page_snapshot_hash,
                    platforms_json, topics_json, sentiment, severity, content_raw,
                    content_plain, is_baseline
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    item.item_id,
                    item.provider,
                    item.source_tier,
                    item.url,
                    item.title,
                    item.published_date,
                    item.first_seen_at,
                    item.last_seen_at,
                    item.item_content_hash,
                    item.page_snapshot_hash,
                    json.dumps(item.platforms, ensure_ascii=False),
                    json.dumps(item.topics, ensure_ascii=False),
                    item.sentiment,
                    item.severity,
                    item.content_raw,
                    item.content_plain,
                    1 if item.is_baseline else 0,
                ),
            )

    def _update_item(self, item: NewsItem) -> None:
        with self._get_connection() as conn:
            conn.execute(
                """
                UPDATE items SET
                    provider = ?, source_tier = ?, url = ?, title = ?, published_date = ?,
                    last_seen_at = ?, item_content_hash = ?, page_snapshot_hash = ?,
                    platforms_json = ?, topics_json = ?, sentiment = ?, severity = ?,
                    content_raw = ?, content_plain = ?, is_baseline = ?
                WHERE item_id = ?
                """,
                (
                    item.provider,
                    item.source_tier,
                    item.url,
                    item.title,
                    item.published_date,
                    item.last_seen_at,
                    item.item_content_hash,
                    item.page_snapshot_hash,
                    json.dumps(item.platforms, ensure_ascii=False),
                    json.dumps(item.topics, ensure_ascii=False),
                    item.sentiment,
                    item.severity,
                    item.content_raw,
                    item.content_plain,
                    1 if item.is_baseline else 0,
                    item.item_id,
                ),
            )

    def get_all_items(self) -> list[NewsItem]:
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM items ORDER BY published_date DESC, item_id ASC"
            ).fetchall()
            return [self._row_to_item(r) for r in rows]

    def filter_items(
        self,
        iso_week: str | None = None,
        min_date: str | None = None,
        include_baseline: bool = False,
    ) -> list[NewsItem]:
        """Filtert Items effizient direkt über SQL-Indizes."""
        query = "SELECT * FROM items WHERE 1=1"
        params: list[Any] = []

        if not include_baseline:
            query += " AND is_baseline = 0"

        if min_date:
            query += " AND (published_date >= ? OR (published_date IS NULL AND first_seen_at >= ?))"
            params.extend([min_date, min_date])

        query += " ORDER BY published_date DESC, item_id ASC"

        with self._get_connection() as conn:
            rows = conn.execute(query, params).fetchall()
            items = [self._row_to_item(r) for r in rows]

        if iso_week:
            # Zusätzlicher Wochen-Filter basierend auf Kalenderwoche
            from datetime import date

            filtered = []
            for itm in items:
                d_str = itm.published_date or itm.first_seen_at[:10]
                try:
                    dt = date.fromisoformat(d_str)
                    w = f"{dt.isocalendar().year}-W{dt.isocalendar().week:02d}"
                    if w == iso_week:
                        filtered.append(itm)
                except Exception:
                    pass
            return filtered

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

            if from_dt and item_dt <= from_dt:
                continue
            if item_dt > to_dt:
                continue

            selected.append(item)

        return selected

    def batch_upsert_items(
        self, items: list[NewsItem], is_baseline: bool = False
    ) -> int:
        """Fügt eine Liste von Items innerhalb einer einzigen Transaktion ein."""
        now_iso = datetime.now(timezone.utc).isoformat()
        count = 0
        with self._get_connection() as conn:
            for item in items:
                row = conn.execute(
                    "SELECT first_seen_at, is_baseline FROM items WHERE item_id = ?",
                    (item.item_id,),
                ).fetchone()
                if row:
                    item.first_seen_at = row["first_seen_at"]
                    item.last_seen_at = item.last_seen_at or now_iso
                    item.is_baseline = bool(row["is_baseline"])
                    conn.execute(
                        """
                        UPDATE items SET
                            provider = ?, source_tier = ?, url = ?, title = ?, published_date = ?,
                            last_seen_at = ?, item_content_hash = ?, page_snapshot_hash = ?,
                            platforms_json = ?, topics_json = ?, sentiment = ?, severity = ?,
                            content_raw = ?, content_plain = ?, is_baseline = ?
                        WHERE item_id = ?
                        """,
                        (
                            item.provider,
                            item.source_tier,
                            item.url,
                            item.title,
                            item.published_date,
                            item.last_seen_at,
                            item.item_content_hash,
                            item.page_snapshot_hash,
                            json.dumps(item.platforms, ensure_ascii=False),
                            json.dumps(item.topics, ensure_ascii=False),
                            item.sentiment,
                            item.severity,
                            item.content_raw,
                            item.content_plain,
                            1 if item.is_baseline else 0,
                            item.item_id,
                        ),
                    )
                else:
                    if not item.first_seen_at:
                        item.first_seen_at = now_iso
                    if not item.last_seen_at:
                        item.last_seen_at = now_iso
                    if is_baseline:
                        item.is_baseline = True
                    conn.execute(
                        """
                        INSERT OR REPLACE INTO items (
                            item_id, provider, source_tier, url, title, published_date,
                            first_seen_at, last_seen_at, item_content_hash, page_snapshot_hash,
                            platforms_json, topics_json, sentiment, severity, content_raw,
                            content_plain, is_baseline
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            item.item_id,
                            item.provider,
                            item.source_tier,
                            item.url,
                            item.title,
                            item.published_date,
                            item.first_seen_at,
                            item.last_seen_at,
                            item.item_content_hash,
                            item.page_snapshot_hash,
                            json.dumps(item.platforms, ensure_ascii=False),
                            json.dumps(item.topics, ensure_ascii=False),
                            item.sentiment,
                            item.severity,
                            item.content_raw,
                            item.content_plain,
                            1 if item.is_baseline else 0,
                        ),
                    )
                count += 1
        return count

    @staticmethod
    def _row_to_item(row: sqlite3.Row) -> NewsItem:
        return NewsItem(
            item_id=row["item_id"],
            provider=row["provider"],
            source_tier=row["source_tier"],
            url=row["url"],
            title=row["title"],
            published_date=row["published_date"],
            first_seen_at=row["first_seen_at"],
            last_seen_at=row["last_seen_at"],
            item_content_hash=row["item_content_hash"],
            page_snapshot_hash=row["page_snapshot_hash"],
            platforms=json.loads(row["platforms_json"]),
            topics=json.loads(row["topics_json"]),
            sentiment=row["sentiment"] or "neutral",
            severity=row["severity"] or "low",
            content_raw=row["content_raw"] or "",
            content_plain=row["content_plain"],
            is_baseline=bool(row["is_baseline"]),
        )

    # =========================================================================
    # Snapshots API (Content-Addressed & Compressed)
    # =========================================================================

    def save_snapshot(
        self,
        snapshot_hash: str,
        content: str,
        original_url: str = "",
        created_at: str | None = None,
    ) -> bool:
        """
        Speichert einen Rohseiten-Snapshot komprimiert in SQLite (Write-Once).
        Gibt True zurück, wenn neu angelegt, False, wenn bereits vorhanden.
        """
        now_iso = created_at or datetime.now(timezone.utc).isoformat()
        compressed = zlib.compress(content.encode("utf-8"), level=9)

        with self._get_connection() as conn:
            try:
                conn.execute(
                    """
                    INSERT INTO snapshots (snapshot_hash, original_url, content_compressed, created_at)
                    VALUES (?, ?, ?, ?)
                    """,
                    (snapshot_hash, original_url, compressed, now_iso),
                )
                return True
            except sqlite3.IntegrityError:
                # Bereits vorhanden (Write-Once)
                return False

    def get_snapshot(self, snapshot_hash: str) -> str | None:
        """Lädt und dekomprimiert den Rohseiten-Snapshot."""
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT content_compressed FROM snapshots WHERE snapshot_hash = ?",
                (snapshot_hash,),
            ).fetchone()
            if not row:
                return None
            try:
                decompressed = zlib.decompress(row["content_compressed"]).decode(
                    "utf-8"
                )
                return decompressed
            except Exception as exc:
                logger.error(
                    "Konnte Snapshot %s nicht dekomprimieren: %s", snapshot_hash, exc
                )
                return None

    def exists_snapshot(self, snapshot_hash: str) -> bool:
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT 1 FROM snapshots WHERE snapshot_hash = ?", (snapshot_hash,)
            ).fetchone()
            return row is not None

    def get_all_snapshot_hashes(self) -> list[str]:
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT snapshot_hash FROM snapshots ORDER BY snapshot_hash ASC"
            ).fetchall()
            return [r[0] for r in rows]

    # =========================================================================
    # Runs API
    # =========================================================================

    def save_run(
        self,
        run_id: str,
        stage: int,
        iso_week: str,
        model_version: str,
        duration_s: float,
        usage: dict[str, Any] | None,
        prompt: str,
        raw_response: str,
        created_at: str | None = None,
    ) -> None:
        now_iso = created_at or datetime.now(timezone.utc).isoformat()
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO runs (
                    run_id, stage, iso_week, model_version, duration_seconds,
                    usage_json, prompt, raw_response, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run_id,
                    stage,
                    iso_week,
                    model_version,
                    duration_s,
                    json.dumps(usage or {}, ensure_ascii=False),
                    prompt,
                    raw_response,
                    now_iso,
                ),
            )

    def get_run(self, run_id: str, stage: int = 2) -> dict[str, Any] | None:
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM runs WHERE run_id = ? AND stage = ?",
                (run_id, stage),
            ).fetchone()
            if not row:
                return None
            return {
                "run_id": row["run_id"],
                "stage": row["stage"],
                "iso_week": row["iso_week"],
                "model_version": row["model_version"],
                "duration_seconds": row["duration_seconds"],
                "usage": json.loads(row["usage_json"]),
                "prompt": row["prompt"],
                "raw_response": row["raw_response"],
                "created_at": row["created_at"],
            }

    def get_all_runs(self) -> list[dict[str, Any]]:
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM runs ORDER BY created_at DESC"
            ).fetchall()
            return [
                {
                    "run_id": r["run_id"],
                    "stage": r["stage"],
                    "iso_week": r["iso_week"],
                    "model_version": r["model_version"],
                    "duration_seconds": r["duration_seconds"],
                    "usage": json.loads(r["usage_json"]),
                    "prompt": r["prompt"],
                    "raw_response": r["raw_response"],
                    "created_at": r["created_at"],
                }
                for r in rows
            ]

    # =========================================================================
    # Platform Audit Scores API
    # =========================================================================

    def save_platform_score(self, score_data: dict[str, Any]) -> None:
        """Speichert oder aktualisiert einen Audit-Score-Snapshot idempotent."""
        now_iso = datetime.now(timezone.utc).isoformat()
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO platform_audit_scores (
                    platform, audit_date, raw_score, net_score, risk_class,
                    pillar_1, pillar_2, pillar_3, pillar_4,
                    malus_total, malus_json, has_conflict, conflict_notes,
                    data_gaps_json, sourcing_strategy, factsheet_path, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(platform, audit_date) DO UPDATE SET
                    raw_score = excluded.raw_score,
                    net_score = excluded.net_score,
                    risk_class = excluded.risk_class,
                    pillar_1 = excluded.pillar_1,
                    pillar_2 = excluded.pillar_2,
                    pillar_3 = excluded.pillar_3,
                    pillar_4 = excluded.pillar_4,
                    malus_total = excluded.malus_total,
                    malus_json = excluded.malus_json,
                    has_conflict = excluded.has_conflict,
                    conflict_notes = excluded.conflict_notes,
                    data_gaps_json = excluded.data_gaps_json,
                    sourcing_strategy = excluded.sourcing_strategy,
                    factsheet_path = excluded.factsheet_path,
                    created_at = excluded.created_at
                """,
                (
                    score_data["platform"],
                    score_data["audit_date"],
                    score_data["raw_score"],
                    score_data["net_score"],
                    score_data["risk_class"],
                    score_data["pillar_1"],
                    score_data["pillar_2"],
                    score_data["pillar_3"],
                    score_data["pillar_4"],
                    score_data["malus_total"],
                    score_data.get("malus_json", "[]"),
                    1 if score_data.get("has_conflict") else 0,
                    score_data.get("conflict_notes"),
                    score_data.get("data_gaps_json", "[]"),
                    score_data.get(
                        "sourcing_strategy", "curated_profile_and_secondary_audits"
                    ),
                    score_data.get("factsheet_path", ""),
                    score_data.get("created_at", now_iso),
                ),
            )

    def get_latest_platform_score(self, platform: str) -> dict[str, Any] | None:
        """Gibt den aktuellsten Audit-Score für eine Plattform zurück."""
        with self._get_connection() as conn:
            row = conn.execute(
                """
                SELECT * FROM platform_audit_scores
                WHERE platform = ?
                ORDER BY audit_date DESC, id DESC
                LIMIT 1
                """,
                (platform,),
            ).fetchone()
            return dict(row) if row else None

    def get_previous_platform_score(
        self, platform: str, before_date: str
    ) -> dict[str, Any] | None:
        """Gibt den vorherigen Score vor einem bestimmten Stichtag zurück (für Delta-Berechnung)."""
        with self._get_connection() as conn:
            row = conn.execute(
                """
                SELECT * FROM platform_audit_scores
                WHERE platform = ? AND audit_date < ?
                ORDER BY audit_date DESC, id DESC
                LIMIT 1
                """,
                (platform, before_date),
            ).fetchone()
            return dict(row) if row else None

    def get_all_latest_scores(self) -> list[dict[str, Any]]:
        """Gibt für alle Plattformen den jeweils neuesten Audit-Score zurück."""
        with self._get_connection() as conn:
            rows = conn.execute(
                """
                SELECT p.* FROM platform_audit_scores p
                INNER JOIN (
                    SELECT platform, MAX(audit_date) as max_date
                    FROM platform_audit_scores
                    GROUP BY platform
                ) m ON p.platform = m.platform AND p.audit_date = m.max_date
                ORDER BY p.net_score DESC, p.raw_score DESC, p.platform ASC
                """
            ).fetchall()
            return [dict(r) for r in rows]

    # =========================================================================
    # Statistiken
    # =========================================================================

    def stats(self) -> dict[str, Any]:
        with self._get_connection() as conn:
            items_count = conn.execute("SELECT COUNT(*) FROM items").fetchone()[0]
            snapshots_count = conn.execute("SELECT COUNT(*) FROM snapshots").fetchone()[
                0
            ]
            runs_count = conn.execute("SELECT COUNT(*) FROM runs").fetchone()[0]
            audit_scores_count = conn.execute(
                "SELECT COUNT(*) FROM platform_audit_scores"
            ).fetchone()[0]
            db_size_mb = (
                self.db_path.stat().st_size / (1024 * 1024)
                if self.db_path.exists()
                else 0.0
            )
            return {
                "db_path": str(self.db_path),
                "items_count": items_count,
                "snapshots_count": snapshots_count,
                "runs_count": runs_count,
                "audit_scores_count": audit_scores_count,
                "db_size_mb": round(db_size_mb, 2),
            }
