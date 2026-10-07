"""
Phase 0 Data Ingestion & Scanner Ingestion
1. Lädt fehlende P2P Empire Erfahrungsberichte herunter und speichert sie in data/erfahrungen/p2p-empire/<platform>.md
2. Lädt fehlende Primärplattform-Daten (z. B. bondora, hive5, lande, swaper, crowdpear, twino etc.) nach data/platforms/<platform>/main.md
3. Führt item_extractor aus, um alle neuen Inhalte direkt in data/p2p_archive.db zu indizieren.
"""

import datetime
import logging
import sys
from pathlib import Path

import httpx
import yaml

# Projektverzeichnis zum sys.path hinzufügen
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Importiere bestehende Module des Projekts
from item_extractor import process_all_scraped_news  # noqa: E402
from p2p_news_scraper import (  # noqa: E402
    ContentExtractor,
    compute_sha256_hash,
    serialize_markdown_with_frontmatter,
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("phase0_ingestion")


def get_headers():
    return {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7",
    }


def fetch_url(client: httpx.Client, url: str) -> str | None:
    try:
        r = client.get(url, headers=get_headers(), timeout=15.0, follow_redirects=True)
        if r.status_code == 200:
            return r.text
        logger.warning(f"Status {r.status_code} für {url}")
    except Exception as exc:
        logger.error(f"Fehler beim Abruf von {url}: {exc}")
    return None


def ingest_p2p_empire_reviews(client: httpx.Client, extractor: ContentExtractor):
    logger.info("=== 1. Ingestion von P2P Empire Erfahrungsberichten ===")

    # Mapping von platform_id auf P2P Empire Review-Slug
    slug_map = {
        "indemo": "indemo",
        "inrento": "inrento",
        "robocash": "robocash",
        "lande": "lande",
        "bondora": "bondora",
        "fintown": "fintown",
        "capitalia": "capitalia",
        "monefit": "monefit",
        "revest": "revest",
        "mintos": "mintos",
        "viainvest": "viainvest",
        "esketit": "esketit",
        "lendermarket": "lendermarket",
        "bondster": "bondster",
        "estateguru": "estateguru",
        "debitum": "debitum-network",
        "swaper": "swaper",
        "ventus": "ventus-energy",
        "loanch": "loanch",
        "crowdpear": "crowdpear",
        "twino": "twino",
        "modena": "modena",
        "insoil": "insoil-finance",
        "income": "income",
    }

    out_dir = Path("data/erfahrungen/p2p-empire")
    out_dir.mkdir(parents=True, exist_ok=True)

    success_count = 0
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

    for platform_id, slug in slug_map.items():
        target_file = out_dir / f"{platform_id}.md"
        if target_file.exists() and target_file.stat().st_size > 5000:
            logger.info(
                f"Überspringe {platform_id}: Datei existiert bereits und ist vollständig ({target_file.stat().st_size} Bytes)"
            )
            continue

        url = f"https://p2pempire.com/de/erfahrungen/{slug}"
        logger.info(f"Lade Review für {platform_id} ({url})...")
        html = fetch_url(client, url)
        if not html:
            continue

        content, title, pub_date, author = extractor.extract(html, url)
        if not content or len(content.strip()) < 200:
            logger.warning(f"Zu wenig Text für {platform_id} von {url}")
            continue

        c_hash = compute_sha256_hash(content)
        frontmatter = {
            "source": "p2p-empire",
            "content_type": "erfahrungen",
            "platform": platform_id,
            "url": url,
            "title": title or f"{platform_id.capitalize()} Erfahrungen 2026",
            "published_date": pub_date or "2026-10-01",
            "author": author or "Jakub Krejci Gründer",
            "content_hash": c_hash,
            "first_seen_at": now_iso,
            "last_scanned_at": now_iso,
            "scan_count": 1,
            "status": "neu",
            "history": [
                {"content_hash": c_hash, "recorded_at": now_iso, "status": "neu"}
            ],
        }

        md_text = serialize_markdown_with_frontmatter(frontmatter, content)
        with open(target_file, "w", encoding="utf-8") as f:
            f.write(md_text)

        logger.info(f"Gespeichert: {target_file} ({len(md_text)} Zeichen)")
        success_count += 1

    logger.info(
        f"P2P Empire Ingestion abgeschlossen: {success_count} neue/aktualisierte Berichte."
    )


def ingest_missing_platforms(client: httpx.Client, extractor: ContentExtractor):
    logger.info("=== 2. Ingestion fehlender Primär-Plattformen ===")

    with open("providers.yaml") as f:
        cfg = yaml.safe_load(f)
    platforms_cfg = cfg.get("platforms", {})

    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
    success_count = 0

    for platform_id, p_info in platforms_cfg.items():
        p_dir = Path("data/platforms") / platform_id
        main_file = p_dir / "main.md"

        # Prüfe, ob Hauptdatei fehlt oder leer / trivial ist
        needs_fetch = False
        if not main_file.exists():
            needs_fetch = True
        else:
            with open(main_file, "r", errors="ignore") as f:
                c = f.read()
            if "loading..." in c.lower() or len(c.strip()) < 400:
                needs_fetch = True

        if not needs_fetch:
            continue

        p_dir.mkdir(parents=True, exist_ok=True)
        base_url = p_info.get("base_url")
        if not base_url:
            continue

        logger.info(f"Lade Primärseite für {platform_id} ({base_url})...")
        html = fetch_url(client, base_url)
        if not html:
            continue

        content, title, pub_date, author = extractor.extract(html, base_url)
        if not content:
            continue

        c_hash = compute_sha256_hash(content)
        frontmatter = {
            "source": platform_id,
            "content_type": "platform",
            "category": "overview",
            "platform": platform_id,
            "url": base_url,
            "title": title or platform_id.capitalize(),
            "published_date": pub_date or "2026-01-01",
            "author": None,
            "content_hash": c_hash,
            "first_seen_at": now_iso,
            "last_scanned_at": now_iso,
            "scan_count": 1,
            "status": "neu",
            "history": [
                {"content_hash": c_hash, "recorded_at": now_iso, "status": "neu"}
            ],
        }

        md_text = serialize_markdown_with_frontmatter(frontmatter, content)
        with open(main_file, "w", encoding="utf-8") as f:
            f.write(md_text)

        logger.info(f"Gespeichert: {main_file} ({len(md_text)} Zeichen)")
        success_count += 1

    logger.info(
        f"Primärplattformen Ingestion abgeschlossen: {success_count} neue/aktualisierte Seiten."
    )


def main():
    extractor = ContentExtractor(output_format="markdown")
    with httpx.Client(timeout=15.0, follow_redirects=True) as client:
        ingest_p2p_empire_reviews(client, extractor)
        ingest_missing_platforms(client, extractor)

    logger.info("=== 3. Indizierung in SQLite (item_extractor) ===")
    files_proc, items_saved = process_all_scraped_news(data_dir="data")
    logger.info(
        f"Indizierung beendet: {files_proc} Dateien geprüft, {items_saved} Items aktuell in DB."
    )


if __name__ == "__main__":
    main()
