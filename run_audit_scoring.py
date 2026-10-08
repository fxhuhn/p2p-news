"""
P2P Platform Audit Scoring - Haupt-Orchestrierung

Führt den kompletten Audit-Lebenszyklus aus:
1. Lädt alle Plattform-Profile (data/platforms/*/profile.yaml)
2. Führt das deterministische Scoring durch (PlatformScorer)
3. Speichert Snapshots in SQLite (data/p2p_archive.db -> platform_audit_scores)
4. Schreibt einzelne Factsheets (data/factsheets/<platform>.md)
5. Generiert das monatliche Gesamtranking mit Delta-Vergleich (data/rankings/audit-ranking-YYYY-MM.md)
"""

import datetime
import glob
import json
import logging
import os
import shutil
from pathlib import Path

import yaml

from factsheet_generator import FactsheetGenerator
from platform_scorer import PlatformScorer
from ranking_generator import RankingGenerator
from storage_sqlite import SQLiteStore

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("audit_pipeline")


def ensure_platform_profiles(
    data_dir: Path | str = "data",
    auto_sync: bool | None = None,
) -> list[str]:
    """
    Stellt sicher, dass Plattform-Profile existieren und autark synchronisiert werden.

    Verhalten:
    - Fehlende Plattform-Profile werden automatisch aus seed_platforms/ initialisiert.
    - Existierende Profile auf gemounteten Volumes werden bei Container-Restart oder
      Scoring-Läufen automatisch mit aktualisierten Seed-Profilen synchronisiert
      (kann via PLATFORM_PROFILES_AUTO_SYNC=false deaktiviert werden).
    """
    base = Path(data_dir)
    platforms_dir = base / "platforms"
    platforms_dir.mkdir(parents=True, exist_ok=True)

    if auto_sync is None:
        env_val = os.getenv("PLATFORM_PROFILES_AUTO_SYNC", "true").strip().lower()
        should_sync = env_val not in ("false", "0", "no", "off")
    else:
        should_sync = auto_sync

    seed_candidates = [
        Path("seed_platforms"),
        Path("/app/seed_platforms"),
        Path(__file__).resolve().parent / "seed_platforms",
    ]

    for seed_dir in seed_candidates:
        if seed_dir.exists() and list(seed_dir.glob("*/profile.yaml")):
            created_cnt = 0
            updated_cnt = 0

            for seed_path in seed_dir.glob("*/profile.yaml"):
                platform_name = seed_path.parent.name
                dest = platforms_dir / platform_name / "profile.yaml"

                if not dest.exists():
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(seed_path, dest)
                    created_cnt += 1
                elif should_sync:
                    try:
                        seed_content = seed_path.read_text(encoding="utf-8")
                        dest_content = dest.read_text(encoding="utf-8")
                        if seed_content != dest_content:
                            shutil.copy2(seed_path, dest)
                            updated_cnt += 1
                            logger.debug(
                                "[PLATFORMS] Profil für '%s' auf neueste Seed-Version aktualisiert.",
                                platform_name,
                            )
                    except Exception as err:
                        logger.warning(
                            "[PLATFORMS] Fehler beim Abgleich von Profil %s: %s",
                            platform_name,
                            err,
                        )

            if created_cnt > 0 or updated_cnt > 0:
                logger.info(
                    "✓ [PLATFORMS] Autarker Profil-Sync abgeschlossen (%d initialisiert, %d aktualisiert).",
                    created_cnt,
                    updated_cnt,
                )
            break

    return sorted(glob.glob(str(platforms_dir / "*/profile.yaml")))


def run_full_audit(
    audit_date: str | None = None,
    data_dir: Path | str = "data",
    do_publish: bool = True,
) -> tuple[int, Path]:
    base = Path(data_dir)
    audit_date = audit_date or datetime.date.today().isoformat()
    store = SQLiteStore(str(base / "p2p_archive.db"))
    scorer = PlatformScorer()
    factsheet_gen = FactsheetGenerator(output_dir=str(base / "factsheets"))
    ranking_gen = RankingGenerator(
        db_path=str(base / "p2p_archive.db"), output_dir=str(base / "rankings")
    )

    profiles = ensure_platform_profiles(data_dir=base)
    if not profiles:
        logger.error("Keine profile.yaml Dateien unter %s/platforms/ gefunden!", base)
        return 0, Path()

    logger.info(
        f"Starte Audit-Lauf für {len(profiles)} Plattformen am Stichtag {audit_date}..."
    )

    scored_count = 0
    for p_path in profiles:
        with open(p_path, "r", encoding="utf-8") as f:
            profile_data = yaml.safe_load(f)

        score_res = scorer.score_platform(profile_data)
        plat = score_res["platform"]

        # Factsheet schreiben
        fs_path = factsheet_gen.generate_factsheet(score_res)

        # In SQLite persistieren
        snapshot_dict = {
            "platform": plat,
            "audit_date": audit_date,
            "raw_score": score_res["raw_score"],
            "net_score": score_res["net_score"],
            "risk_class": score_res["risk_class"],
            "pillar_1": score_res["pillar_1"].final_score,
            "pillar_2": score_res["pillar_2"].final_score,
            "pillar_3": score_res["pillar_3"].final_score,
            "pillar_4": score_res["pillar_4"].final_score,
            "malus_total": score_res["malus_total"],
            "malus_json": json.dumps(
                [
                    m.model_dump() if hasattr(m, "model_dump") else m.dict()
                    for m in score_res["malus_deductions"]
                ]
            ),
            "has_conflict": score_res["flags"].has_conflict,
            "conflict_notes": "; ".join(score_res["flags"].conflict_notes)
            if score_res["flags"].conflict_notes
            else None,
            "data_gaps_json": json.dumps(score_res["flags"].data_gaps),
            "sourcing_strategy": score_res["flags"].sourcing_strategy,
            "factsheet_path": str(fs_path),
            "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }
        store.save_platform_score(snapshot_dict)
        logger.info(
            f"✓ {plat.capitalize():<15} -> Net Score: {score_res['net_score']:<3} | Klasse: {score_res['risk_class']}"
        )
        scored_count += 1

    # Master-Ranking generieren
    ranking_path = ranking_gen.generate_monthly_ranking(audit_date=audit_date)
    logger.info(f"✓ Master-Ranking generiert: {ranking_path}")

    # Git Push ausführen
    if do_publish:
        from git_publisher import publish_changes

        publish_changes(
            files=[ranking_path, base / "factsheets"],
            commit_message=f"chore(audit): publish monthly platform rankings and factsheets {audit_date[:7]}",
            data_dir=base,
        )

    return scored_count, ranking_path


if __name__ == "__main__":
    count, rank_file = run_full_audit()
    print(
        f"\nAudit erfolgreich abgeschlossen: {count} Factsheets erstellt, Ranking unter {rank_file}"
    )
