"""
Watermark-Manager für Exactly-Once Selektion von NewsItems (Stufe 1).

Ablagestruktur:
data/watermark.json
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from item_models import NewsItem
from item_store import ItemStore

logger = logging.getLogger("watermark_manager")


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
        Filtert nach Kalenderwoche (z. B. '2026-W40') anhand von published_date oder first_seen_at.

        Modus 2 (Exactly-Once via Watermark):
        first_seen_at > last_watermark AND first_seen_at <= current_run_time
        """
        all_items = store.get_all_items()
        selected: list[NewsItem] = []

        if iso_week:
            # Modus 1: Spezifische Kalenderwoche (Format: YYYY-Wxx)
            for item in all_items:
                if not include_baseline and item.is_baseline:
                    continue
                # Priorisiere strikt das redaktionelle Veröffentlichungsdatum
                if item.published_date:
                    try:
                        dt = datetime.fromisoformat(item.published_date)
                        if (
                            f"{dt.isocalendar().year}-W{dt.isocalendar().week:02d}"
                            == iso_week
                        ):
                            selected.append(item)
                    except Exception:
                        pass
                elif item.first_seen_at:
                    try:
                        dt = datetime.fromisoformat(item.first_seen_at[:10])
                        if (
                            f"{dt.isocalendar().year}-W{dt.isocalendar().week:02d}"
                            == iso_week
                        ):
                            selected.append(item)
                    except Exception:
                        pass

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
