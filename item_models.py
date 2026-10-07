"""
Datenmodelle für diskrete News-Items (Stufe 0).
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path


@dataclass
class NewsItem:
    """Repräsentiert eine diskrete Einzelmeldung aus einer Übersicht oder einem Artikel."""

    item_id: str
    provider: str
    source_tier: str  # "primary" | "secondary"
    url: str
    title: str
    published_date: str | None
    first_seen_at: str  # ISO 8601 Zeitstempel der ersten Erfassung
    last_seen_at: str  # ISO 8601 Zeitstempel der letzten Erfassung
    item_content_hash: str  # SHA-256 über normalisierten Fließtext
    page_snapshot_hash: str | None
    platforms: list[str] = field(default_factory=list)
    topics: list[str] = field(default_factory=list)
    sentiment: str = "neutral"
    severity: str = "low"
    content_raw: str = ""
    content_plain: str = ""
    is_baseline: bool = False

    def to_dict(self) -> dict[str, object]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> NewsItem:
        raw_platforms = data.get("platforms")
        platforms = (
            [str(x) for x in raw_platforms]
            if isinstance(raw_platforms, (list, tuple))
            else []
        )
        raw_topics = data.get("topics")
        topics = (
            [str(x) for x in raw_topics]
            if isinstance(raw_topics, (list, tuple))
            else []
        )
        return cls(
            item_id=str(data["item_id"]),
            provider=str(data["provider"]),
            source_tier=str(data.get("source_tier", "secondary")),
            url=str(data["url"]),
            title=str(data["title"]),
            published_date=str(data["published_date"])
            if data.get("published_date")
            else None,
            first_seen_at=str(data["first_seen_at"]),
            last_seen_at=str(data.get("last_seen_at", data["first_seen_at"])),
            item_content_hash=str(data["item_content_hash"]),
            page_snapshot_hash=str(data["page_snapshot_hash"])
            if data.get("page_snapshot_hash")
            else None,
            platforms=platforms,
            topics=topics,
            sentiment=str(data.get("sentiment", "neutral")),
            severity=str(data.get("severity", "low")),
            content_raw=str(data.get("content_raw", "")),
            content_plain=str(data.get("content_plain", "")),
            is_baseline=bool(data.get("is_baseline", False)),
        )

    def save(self, target_dir: Path | str = "data/items") -> Path:
        """Speichert das Item als <item_id>.json ab."""
        out_path = Path(target_dir) / f"{self.item_id}.json"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(
            json.dumps(self.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8"
        )
        return out_path

    @classmethod
    def load(cls, file_path: Path | str) -> NewsItem:
        """Lädt ein Item aus einer JSON-Datei."""
        content = Path(file_path).read_text(encoding="utf-8")
        return cls.from_dict(json.loads(content))
