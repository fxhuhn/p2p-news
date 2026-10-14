"""
Watermark-Manager für Exactly-Once Selektion von NewsItems (Stufe 1).

Ablagestruktur:
data/watermark.json
"""

from __future__ import annotations

import json
import logging
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from item_models import NewsItem
from item_store import ItemStore

logger = logging.getLogger("watermark_manager")


def get_previous_iso_week(iso_week: str) -> str:
    """Berechnet die ISO-Kalenderwoche der direkten Vorwoche (W-1)."""
    match = re.match(r"^(\d{4})-W(\d{2})$", iso_week)
    if not match:
        raise ValueError(f"Ungültiges ISO-Wochenformat: {iso_week}")
    year, week = int(match.group(1)), int(match.group(2))
    current_monday = datetime.fromisocalendar(year, week, 1)
    prev_monday = current_monday - timedelta(days=7)
    prev_year, prev_week, _ = prev_monday.isocalendar()
    return f"{prev_year}-W{prev_week:02d}"


def load_previous_newsletter_mentions(
    base_dir: Path, prev_iso_week: str
) -> tuple[set[str], set[str]]:
    """
    Lädt alle Item-IDs und URLs, die bereits im vorherigen Digest oder Newsletter (W-1) erwähnt wurden.
    Gibt (mentioned_item_ids, mentioned_urls) zurück.
    """
    mentioned_ids: set[str] = set()
    mentioned_urls: set[str] = set()

    # 1. Manifest aus Stufe 1: data/digests/digest-{prev_iso_week}.manifest.json
    manifest_path = base_dir / "digests" / f"digest-{prev_iso_week}.manifest.json"
    if manifest_path.exists():
        try:
            data = json.loads(manifest_path.read_text(encoding="utf-8"))
            item_hashes = data.get("inputs", {}).get("item_hashes", {})
            if isinstance(item_hashes, dict):
                mentioned_ids.update(item_hashes.keys())
        except Exception as exc:
            logger.warning(
                "Konnte Vorwochen-Manifest %s nicht lesen: %s", manifest_path, exc
            )

    # 2. Digest-Cluster aus Stufe 1: data/digests/digest-{prev_iso_week}.json
    digest_path = base_dir / "digests" / f"digest-{prev_iso_week}.json"
    if digest_path.exists():
        try:
            data = json.loads(digest_path.read_text(encoding="utf-8"))
            for cluster in data.get("clusters", []):
                for src in cluster.get("source_items", []):
                    item_id = src.get("item_id")
                    if item_id:
                        mentioned_ids.add(str(item_id))
                    url = src.get("url")
                    if url:
                        mentioned_urls.add(str(url).strip())
                        clean_url = (
                            urlparse(str(url))
                            ._replace(fragment="", query="")
                            .geturl()
                            .rstrip("/")
                        )
                        mentioned_urls.add(clean_url)
        except Exception as exc:
            logger.warning(
                "Konnte Vorwochen-Digest %s nicht lesen: %s", digest_path, exc
            )

    # 3. Newsletter-Markdown: data/newsletters/newsletter-{prev_iso_week}*.md
    newsletters_dir = base_dir / "newsletters"
    if newsletters_dir.exists():
        for nl_file in newsletters_dir.glob(f"newsletter-{prev_iso_week}*.md"):
            try:
                content = nl_file.read_text(encoding="utf-8")
                found_urls = re.findall(r"\[.*?\]\((https?://[^)]+)\)", content)
                for u in found_urls:
                    clean = u.strip()
                    mentioned_urls.add(clean)
                    clean_norm = (
                        urlparse(clean)
                        ._replace(fragment="", query="")
                        .geturl()
                        .rstrip("/")
                    )
                    mentioned_urls.add(clean_norm)
            except Exception as exc:
                logger.warning(
                    "Konnte Newsletter-Datei %s nicht analysieren: %s", nl_file, exc
                )

    return mentioned_ids, mentioned_urls


class WatermarkManager:
    """Verwaltet den persistenten Verarbeitungs-Wasserstand zur Exactly-Once Garantie."""

    def __init__(self, watermark_path: Path | str = "data/watermark.json") -> None:
        self.watermark_path = Path(watermark_path)

    def load_state(self) -> dict[str, Any]:
        if not self.watermark_path.exists():
            return {
                "last_watermark": None,
                "last_run_id": None,
                "history": [],
            }
        try:
            return json.loads(self.watermark_path.read_text(encoding="utf-8"))
        except Exception as exc:
            logger.warning(
                "Konnte Watermark-Datei %s nicht lesen: %s", self.watermark_path, exc
            )
            return {"last_watermark": None, "last_run_id": None, "history": []}

    def get_last_watermark(self) -> str | None:
        state = self.load_state()
        return state.get("last_watermark")

    def update_watermark(
        self,
        watermark_iso: str,
        run_id: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Aktualisiert die Watermark und fügt einen Eintrag zur Historie hinzu."""
        state = self.load_state()
        history_entry = {
            "watermark": watermark_iso,
            "run_id": run_id,
            "recorded_at": datetime.now(timezone.utc).isoformat(),
            "metadata": metadata or {},
        }
        state["last_watermark"] = watermark_iso
        state["last_run_id"] = run_id
        state.setdefault("history", []).append(history_entry)

        self.watermark_path.parent.mkdir(parents=True, exist_ok=True)
        self.watermark_path.write_text(
            json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        logger.info("Watermark auf %s gesetzt (Run: %s)", watermark_iso, run_id)

    def select_items_for_run(
        self,
        store: ItemStore,
        current_run_time_iso: str | None = None,
        iso_week: str | None = None,
        include_baseline: bool = False,
    ) -> list[NewsItem]:
        """
        Selektiert Items für den aktuellen Lauf.

        Modus 1 (ISO-Woche explizit):
        Filtert nach Kalenderwoche (z. B. '2026-W41') anhand von published_date.
        Lässt Nachzügler aus der direkten Vorwoche (W-1) zu, sofern sie im vorherigen
        Newsletter / Digest noch nicht erwähnt wurden.
        Schließt ältere Meldungen (W-2 oder älter) strikt aus.

        Modus 2 (Exactly-Once via Watermark):
        first_seen_at > last_watermark AND first_seen_at <= current_run_time
        """
        all_items = store.get_all_items()
        selected: list[NewsItem] = []

        if iso_week:
            # Modus 1: Spezifische Kalenderwoche (Format: YYYY-Wxx)
            prev_iso_week = get_previous_iso_week(iso_week)
            base_dir = (
                store.items_dir.parent
                if hasattr(store, "items_dir")
                else self.watermark_path.parent
            )
            prev_mentioned_ids, prev_mentioned_urls = load_previous_newsletter_mentions(
                base_dir, prev_iso_week
            )

            for item in all_items:
                if not include_baseline and item.is_baseline:
                    continue

                item_iso_week: str | None = None
                has_explicit_date = False

                # 1. Priorisiere strikt das redaktionelle Veröffentlichungsdatum
                if item.published_date:
                    try:
                        dt = datetime.fromisoformat(item.published_date)
                        item_iso_week = (
                            f"{dt.isocalendar().year}-W{dt.isocalendar().week:02d}"
                        )
                        has_explicit_date = True
                    except Exception:
                        pass

                # 2. Datum aus URL-Slug prüfen (z. B. 2026-10-12 oder p2p-kredite-35-26)
                if not item_iso_week:
                    date_match = re.search(r"(\d{4}-\d{2}-\d{2})", item.url)
                    if date_match:
                        try:
                            dt = datetime.fromisoformat(date_match.group(1))
                            item_iso_week = (
                                f"{dt.isocalendar().year}-W{dt.isocalendar().week:02d}"
                            )
                            has_explicit_date = True
                        except Exception:
                            pass
                    else:
                        kw_match = re.search(r"p2p-kredite-(\d{1,2})-(\d{2})", item.url)
                        if kw_match:
                            try:
                                kw = int(kw_match.group(1))
                                year = 2000 + int(kw_match.group(2))
                                dt = datetime.fromisocalendar(year, kw, 1)
                                item_iso_week = f"{dt.isocalendar().year}-W{dt.isocalendar().week:02d}"
                                has_explicit_date = True
                            except Exception:
                                pass

                # 3. Fallback auf first_seen_at (NUR für die aktuelle Woche W zulässig!)
                if not item_iso_week and item.first_seen_at:
                    try:
                        dt = datetime.fromisoformat(item.first_seen_at[:10])
                        cand_week = (
                            f"{dt.isocalendar().year}-W{dt.isocalendar().week:02d}"
                        )
                        if cand_week == iso_week:
                            item_iso_week = cand_week
                    except Exception:
                        pass

                if not item_iso_week:
                    continue

                # Filterung nach Kalenderwoche
                if item_iso_week == iso_week:
                    # Direkte Meldung der Zielwoche
                    selected.append(item)
                elif item_iso_week == prev_iso_week and has_explicit_date:
                    # Nachzügler aus der Vorwoche W-1: Nur zulassen, wenn noch nicht im vorherigen Newsletter erwähnt
                    clean_url = (
                        urlparse(item.url)
                        ._replace(fragment="", query="")
                        .geturl()
                        .rstrip("/")
                    )
                    if (
                        item.item_id not in prev_mentioned_ids
                        and item.url.strip() not in prev_mentioned_urls
                        and clean_url not in prev_mentioned_urls
                    ):
                        logger.info(
                            "Nachzügler aus Vorwoche %s zugelassen (nicht in letztem Newsletter): %s [%s]",
                            prev_iso_week,
                            item.title,
                            item.url,
                        )
                        selected.append(item)
                    else:
                        logger.debug(
                            "Vorwochen-Item %s übersprungen, da bereits im letzten Newsletter erwähnt.",
                            item.title,
                        )
                else:
                    # W-2 oder älter: Strikt ausschließen!
                    continue

            # Sortierung: Schweregrad (critical > high > medium > low), Tier (primary vor secondary), Neueste zuerst
            severity_weights = {"critical": 3, "high": 2, "medium": 1, "low": 0}
            tier_weights = {"primary": 1, "secondary": 0}
            selected.sort(
                key=lambda x: (
                    severity_weights.get(x.severity, 0),
                    tier_weights.get(x.source_tier, 0),
                    x.published_date or "",
                    x.first_seen_at,
                ),
                reverse=True,
            )
            return selected

        # Modus 2: Exactly-Once über Watermark
        run_time = current_run_time_iso or datetime.now(timezone.utc).isoformat()
        last_wm = self.get_last_watermark()

        return store.get_items_for_period(
            watermark_from_iso=last_wm,
            watermark_to_iso=run_time,
            include_baseline=include_baseline,
        )
