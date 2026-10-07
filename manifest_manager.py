"""
Manifest-Manager für kryptographische Hash-Ketten und Revisionssicherheit (Stufe 2).

Verwaltet:
data/digests/digest-YYYY-Wxx.manifest.json

Eigenschaften:
- SHA-256 Hashes aller Ein- und Ausgabedateien
- previous_manifest_sha256 (Kryptographische Kette)
- verify_integrity: Erkennt nachträgliche Manipulationen (Tamper-Detection)
"""

from __future__ import annotations

import hashlib
import json
import logging
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger("manifest_manager")


def compute_file_sha256(path: Path | str) -> str:
    """Berechnet den SHA-256 Hash einer Datei."""
    p = Path(path)
    if not p.exists():
        return ""
    hasher = hashlib.sha256()
    with open(p, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def get_current_git_commit() -> str | None:
    """Versucht, den aktuellen Git-Commit-Hash zu ermitteln."""
    try:
        res = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
            timeout=2.0,
        )
        return res.stdout.strip()
    except Exception:
        return None


class ManifestManager:
    """Erstellt und verifiziert Revisions-Manifeste mit Hash-Ketten."""

    def __init__(self, digests_dir: Path | str = "data/digests") -> None:
        self.digests_dir = Path(digests_dir)
        self.digests_dir.mkdir(parents=True, exist_ok=True)

    def find_previous_manifest(
        self, current_week: str
    ) -> tuple[Path | None, str | None]:
        """Findet das chronologisch vorherige Manifest und berechnet dessen Hash."""
        all_manifests = sorted(self.digests_dir.glob("*.manifest.json"))
        prev_file = None
        for mf in all_manifests:
            if (
                current_week not in mf.name
                and mf.name < f"digest-{current_week}.manifest.json"
            ):
                prev_file = mf

        if prev_file and prev_file.exists():
            return prev_file, compute_file_sha256(prev_file)
        return None, None

    def create_manifest(
        self,
        iso_week: str,
        run_id: str,
        watermark_previous: str | None,
        watermark_current: str,
        digest_path: Path | str,
        newsletter_path: Path | str,
        item_hashes: dict[str, str],
        metrics: dict[str, Any],
    ) -> Path:
        """Erstellt das signierte Revisions-Manifest inklusive Hash-Kette."""
        digest_p = Path(digest_path)
        news_p = Path(newsletter_path)

        _, prev_hash = self.find_previous_manifest(current_week=iso_week)

        manifest_data = {
            "run_id": run_id,
            "iso_week": iso_week,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "watermark_previous": watermark_previous,
            "watermark_current": watermark_current,
            "previous_manifest_sha256": prev_hash,
            "git_commit": get_current_git_commit(),
            "git_tag": f"newsletter-{iso_week}",
            "inputs": {
                "total_items": len(item_hashes),
                "item_hashes": item_hashes,
            },
            "outputs": {
                "digest_file": str(digest_p),
                "digest_sha256": compute_file_sha256(digest_p),
                "newsletter_file": str(news_p),
                "newsletter_sha256": compute_file_sha256(news_p),
            },
            "verifier_metrics": metrics,
        }

        manifest_path = self.digests_dir / f"digest-{iso_week}.manifest.json"
        manifest_path.write_text(
            json.dumps(manifest_data, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        logger.info("Revisions-Manifest erstellt: %s", manifest_path)
        return manifest_path

    def verify_integrity(self, manifest_path: Path | str) -> tuple[bool, list[str]]:
        """
        Prüft die Integrität der Ausgabedateien gegen das Manifest (Tamper-Detection).

        Gibt zurück:
        (is_valid, errors_list)
        """
        p = Path(manifest_path)
        if not p.exists():
            return False, [f"Manifest-Datei {p} existiert nicht"]

        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except Exception as exc:
            return False, [f"Manifest konnte nicht geparst werden: {exc}"]

        errors: list[str] = []
        outputs = data.get("outputs", {})

        # 1. Digest prüfen
        digest_file = Path(outputs.get("digest_file", ""))
        expected_digest_hash = outputs.get("digest_sha256", "")
        if not digest_file.exists():
            errors.append(f"Digest-Datei {digest_file} fehlt")
        else:
            actual_digest_hash = compute_file_sha256(digest_file)
            if actual_digest_hash != expected_digest_hash:
                errors.append(
                    f"Digest manipuliert! Erwartet: {expected_digest_hash}, Berechnet: {actual_digest_hash}"
                )

        # 2. Newsletter prüfen
        news_file = Path(outputs.get("newsletter_file", ""))
        expected_news_hash = outputs.get("newsletter_sha256", "")
        if not news_file.exists():
            errors.append(f"Newsletter-Datei {news_file} fehlt")
        else:
            actual_news_hash = compute_file_sha256(news_file)
            if actual_news_hash != expected_news_hash:
                errors.append(
                    f"Newsletter manipuliert! Erwartet: {expected_news_hash}, Berechnet: {actual_news_hash}"
                )

        is_valid = len(errors) == 0
        return is_valid, errors
