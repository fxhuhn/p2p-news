"""
Item-Extraktor für P2P-News (Stufe 0).

Zerlegt Übersichtsseiten (z. B. re:think P2P, P2P Empire, P2P Game) sowie
Detailartikel in diskrete, unveränderliche Einzelmeldungen (NewsItem).

Garantiert:
- Stabile, kollisionsfreie item_id (nicht von relativen Daten abhängig)
- Item-Level Content-Hashing (Änderungserkennung pro Meldung)
- Granulare Keyword-Klassifikation pro Einzelmeldung
"""

from __future__ import annotations

import argparse
import hashlib
import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from item_models import NewsItem
from item_store import ItemStore
from normalization import normalize_plain_text, parse_german_date
from p2p_news_scraper import (
    DEFAULT_CLASSIFIER,
    KeywordClassifier,
    parse_markdown_with_frontmatter,
)
from snapshot_manager import SnapshotManager

logger = logging.getLogger("item_extractor")

PRIMARY_PROVIDERS: set[str] = {
    "nectaro",
    "mintos",
    "peerberry",
    "esketit",
    "debitum",
    "indemo",
    "swaper",
    "estateguru",
    "loanch",
    "revest",
    "lande",
    "afranga",
    "stock.estate",
    "inrento",
    "fintown",
    "bondster",
    "fagura",
    "capitalia",
    "ventus energy",
    "robocash",
    "bondora",
    "twino",
    "viainvest",
}

PRIMARY_PLATFORM_DOMAINS: set[str] = {
    "nectaro.eu",
    "mintos.com",
    "peerberry.com",
    "esketit.com",
    "debitum.investments",
    "indemo.eu",
    "estateguru.co",
    "swaper.com",
    "loanch.com",
    "revest.group",
    "robo.cash",
    "asterra.estate",
    "capitalia.com",
    "ventus.energy",
    "lande.finance",
    "afranga.com",
    "inrento.com",
    "fintown.eu",
    "bondster.com",
    "fagura.com",
    "stock.estate",
    "bondora.com",
    "viainvest.com",
    "getincome.com",
    "hive5.eu",
    "hive5.com",
    "lendermarket.com",
    "monefit.com",
    "twino.eu",
}


def slugify(text: str) -> str:
    """Erzeugt einen sauberen URL-kompatiblen Slug aus einem String."""
    cleaned = re.sub(r"[^\w\s-]", "", text.lower()).strip()
    return re.sub(r"[-\s]+", "-", cleaned)


def compute_item_id(
    provider: str,
    title: str,
    url: str | None,
    content_hash: str,
) -> str:
    """
    Berechnet die unzerstörbare item_id nach Konzept 2.2:
    - Basiert auf provider + eindeutiger URL/Slug falls vorhanden
    - Fallback: provider + normalisierter Titel + content_hash[:8]
    - NIEMALS abhängig von variablen oder relativen Datumsangaben!
    """
    norm_title = re.sub(r"\W+", " ", title).strip().lower()

    # Prüfe, ob die URL ein spezifischer Artikel oder Anker ist (nicht nur die Übersichtsseite)
    is_overview_url = False
    if url:
        parsed = urlparse(url)
        path = parsed.path.rstrip("/")
        if path in {
            "/nachrichten",
            "/news",
            "/p2p-kredite-plattform-news",
            "/p2p-kredite-news",
            "",
        }:
            is_overview_url = True

    if url and not is_overview_url:
        identity_base = f"{provider.lower()}|{url.strip().lower()}"
    else:
        identity_base = f"{provider.lower()}|{norm_title}|{content_hash[:8]}"

    return hashlib.sha256(identity_base.encode("utf-8")).hexdigest()[:16]


class ItemExtractor:
    """Extrahiert diskrete NewsItems aus Markdown-Dateien oder Rohtexten."""

    def __init__(
        self,
        classifier: KeywordClassifier | None = None,
        snapshot_manager: SnapshotManager | None = None,
    ) -> None:
        self.classifier = classifier or DEFAULT_CLASSIFIER
        self.snapshot_manager = snapshot_manager or SnapshotManager()

    def determine_source_tier(self, provider: str, url: str | None = None) -> str:
        """
        Ermittelt das Source-Tier (primary oder secondary).
        Erkennt offizielle Plattform-Domains auch dann als primary, wenn sie über
        einen Aggregator oder Blog erfasst wurden.
        """
        if provider.lower() in PRIMARY_PROVIDERS:
            return "primary"
        if url:
            try:
                netloc = urlparse(url).netloc.lower()
                domain = netloc[4:] if netloc.startswith("www.") else netloc
                if domain in PRIMARY_PLATFORM_DOMAINS:
                    return "primary"
            except Exception:
                pass
        return "secondary"

    def extract_from_markdown_file(
        self,
        file_path: Path | str,
        is_baseline: bool = False,
    ) -> list[NewsItem]:
        """Liest eine Markdown-Datei und zerlegt sie in NewsItems."""
        path = Path(file_path)
        if not path.exists():
            return []

        content = path.read_text(encoding="utf-8")
        frontmatter, body = parse_markdown_with_frontmatter(content)
        return self.extract_items(
            body, frontmatter=frontmatter, is_baseline=is_baseline
        )

    def extract_items(
        self,
        markdown_body: str,
        frontmatter: dict[str, Any] | None = None,
        is_baseline: bool = False,
    ) -> list[NewsItem]:
        """Hauptmethode zur Extraktion diskreter Items aus Markdown-Text."""
        fm = frontmatter or {}
        provider = str(fm.get("source", "unknown"))
        page_url = str(fm.get("url", ""))
        page_first_seen = str(
            fm.get("first_seen_at", datetime.now(timezone.utc).isoformat())
        )
        source_tier = self.determine_source_tier(provider)

        # Ausschluss von binären PDF-Dateien oder PDF-URLs
        lower_url = page_url.lower()
        if (
            lower_url.endswith(".pdf")
            or ".pdf/" in lower_url
            or markdown_body.lstrip().startswith("%PDF")
            or "%PDF-" in markdown_body[:500]
        ):
            logger.warning("Überspringe binäre PDF-Daten für %s", page_url)
            return []

        # Sichere den Rohinhalt als Seiten-Snapshot
        snapshot_hash, _, _ = self.snapshot_manager.save_page_snapshot(
            markdown_body, original_url=page_url
        )

        # Prüfe, ob es sich um eine Übersichtsseite handelt
        if self._is_overview_page(markdown_body, fm):
            items = self._split_overview_page(
                markdown_body=markdown_body,
                provider=provider,
                page_url=page_url,
                page_first_seen=page_first_seen,
                snapshot_hash=snapshot_hash,
                source_tier=source_tier,
                is_baseline=is_baseline,
            )
            if items:
                return items

        # Fallback / Single Article: Die gesamte Seite ist ein eigenständiges Item
        return [
            self._create_single_article_item(
                markdown_body=markdown_body,
                frontmatter=fm,
                provider=provider,
                page_url=page_url,
                page_first_seen=page_first_seen,
                snapshot_hash=snapshot_hash,
                source_tier=source_tier,
                is_baseline=is_baseline,
            )
        ]

    def _is_overview_page(self, body: str, frontmatter: dict[str, Any]) -> bool:
        """Erkennt, ob eine Datei eine Übersichtsseite mit mehreren Meldungen ist."""
        url = frontmatter.get("url", "")
        if any(
            marker in url
            for marker in ["/nachrichten", "/news/", "/p2p-kredite-plattform-news"]
        ):
            return True

        # Zähle ## Headings
        h2_headings = re.findall(r"^##\s+(.+)$", body, flags=re.MULTILINE)
        if len(h2_headings) >= 2:
            return True

        # P2P-Game News-Muster: **[Plattform](...)** News *Datum*
        game_matches = re.findall(
            r"\*\*\[[A-Za-z0-9_-]+\]\(.*?\)\*\*\s+News\s+\*\d{2}\.\d{2}\.\d{2}\*", body
        )
        if len(game_matches) >= 2:
            return True

        return False

    def _split_overview_page(
        self,
        markdown_body: str,
        provider: str,
        page_url: str,
        page_first_seen: str,
        snapshot_hash: str,
        source_tier: str,
        is_baseline: bool,
    ) -> list[NewsItem]:
        """Zerlegt eine Übersichtsseite in einzelne NewsItems."""
        items: list[NewsItem] = []

        # Strategie 1: P2P Game Format
        if "p2p-game" in provider or re.search(
            r"\*\*\[[A-Za-z0-9_-]+\]\(.*?\)\*\*\s+News", markdown_body
        ):
            items = self._split_p2p_game(
                markdown_body,
                provider,
                page_url,
                page_first_seen,
                snapshot_hash,
                source_tier,
                is_baseline,
            )
            if items:
                return items

        # Strategie 2: Standard H2-Abschnitte (re:think P2P, P2P Empire)
        h2_pattern = re.compile(r"^##\s+(.+)$", flags=re.MULTILINE)
        splits = list(h2_pattern.finditer(markdown_body))
        if not splits:
            return []

        for idx, match in enumerate(splits):
            title = match.group(1).strip()
            # Start des Inhalts
            start_pos = match.end()
            # Ende des Inhalts ist entweder der nächste H2 oder das Dateiende
            end_pos = (
                splits[idx + 1].start() if idx + 1 < len(splits) else len(markdown_body)
            )
            section_raw = markdown_body[start_pos:end_pos].strip()

            # Entferne abschließende Trennlinie
            section_raw = re.sub(r"[-*_]{3,}\s*$", "", section_raw).strip()

            if not section_raw:
                continue

            # Extrahiere relatives Datum am Anfang des Abschnitts: *02. Oktober 2026*
            date_match = re.match(r"^\*([^*]+)\*", section_raw)
            published_date = None
            if date_match:
                published_date = parse_german_date(date_match.group(1))
                # Entferne die Datumszeile aus dem Rohinhalt
                section_raw = section_raw[date_match.end() :].strip()

            # Extrahiere mögliche direkte Detail-Links im Abschnitt
            item_url = self._extract_best_url(
                section_raw, base_url=page_url, title=title
            )

            # Normalisiere Fließtext
            content_plain = normalize_plain_text(section_raw)
            if not content_plain:
                continue

            item_content_hash = hashlib.sha256(
                content_plain.encode("utf-8")
            ).hexdigest()
            item_id = compute_item_id(provider, title, item_url, item_content_hash)

            # Granulare Klassifikation nur für dieses Item
            classification = self.classifier.classify(
                title=title, content=content_plain, url=item_url
            )

            item = NewsItem(
                item_id=item_id,
                provider=provider,
                source_tier=self.determine_source_tier(provider, url=item_url),
                url=item_url,
                title=title,
                published_date=published_date,
                first_seen_at=page_first_seen,
                last_seen_at=page_first_seen,
                item_content_hash=item_content_hash,
                page_snapshot_hash=snapshot_hash,
                platforms=list(classification.platforms),
                topics=list(classification.topics),
                sentiment=classification.sentiment,
                severity=classification.severity,
                content_raw=section_raw,
                content_plain=content_plain,
                is_baseline=is_baseline,
            )
            items.append(item)

        return items

    def _split_p2p_game(
        self,
        markdown_body: str,
        provider: str,
        page_url: str,
        page_first_seen: str,
        snapshot_hash: str,
        source_tier: str,
        is_baseline: bool,
    ) -> list[NewsItem]:
        """Zerlegt P2P-Game News-Blöcke."""
        items: list[NewsItem] = []
        pattern = re.compile(
            r"\*\*\[([A-Za-z0-9_-]+)\]\(.*?\)\*\*\s+News\s+\*(\d{2}\.\d{2}\.\d{2})\*(.*?)(?=(\*\*\[[A-Za-z0-9_-]+\]\(.*?\)\*\*\s+News|\Z))",
            flags=re.DOTALL,
        )

        for match in pattern.finditer(markdown_body):
            platform_name = match.group(1).strip()
            date_raw = match.group(2).strip()
            published_date = parse_german_date(date_raw)
            block_body = match.group(3).strip()

            # Extrahiere Headline: **Headline**Text
            headline_match = re.search(
                r"\*\*([^*]+)\*\*(.*)", block_body, flags=re.DOTALL
            )
            if headline_match:
                title = f"{platform_name}: {headline_match.group(1).strip()}"
                text_part = headline_match.group(2).strip()
            else:
                title = f"{platform_name} News"
                text_part = block_body

            # Extrahiere Quellenlink: [📰 *Quelle*](https://...)
            source_match = re.search(
                r"\[📰\s*\*Quelle\*\s*\]\((https?://[^)]+)\)", block_body
            )
            item_url = (
                source_match.group(1).strip()
                if source_match
                else f"{page_url}#{slugify(title)}"
            )

            # Bereinige Links am Ende
            clean_raw = re.sub(r"\[.*?\]\(.*?\)", "", text_part).strip()
            content_plain = normalize_plain_text(clean_raw)
            if not content_plain:
                continue

            item_content_hash = hashlib.sha256(
                content_plain.encode("utf-8")
            ).hexdigest()
            item_id = compute_item_id(provider, title, item_url, item_content_hash)

            classification = self.classifier.classify(
                title=title, content=content_plain, url=item_url
            )
            # Garantiere, dass die erkannte Plattform im Set ist
            platforms = list(
                dict.fromkeys(list(classification.platforms) + [platform_name.lower()])
            )

            item = NewsItem(
                item_id=item_id,
                provider=provider,
                source_tier=self.determine_source_tier(provider, url=item_url),
                url=item_url,
                title=title,
                published_date=published_date,
                first_seen_at=page_first_seen,
                last_seen_at=page_first_seen,
                item_content_hash=item_content_hash,
                page_snapshot_hash=snapshot_hash,
                platforms=platforms,
                topics=list(classification.topics),
                sentiment=classification.sentiment,
                severity=classification.severity,
                content_raw=text_part,
                content_plain=content_plain,
                is_baseline=is_baseline,
            )
            items.append(item)

        return items

    def _create_single_article_item(
        self,
        markdown_body: str,
        frontmatter: dict[str, Any],
        provider: str,
        page_url: str,
        page_first_seen: str,
        snapshot_hash: str,
        source_tier: str,
        is_baseline: bool,
    ) -> NewsItem:
        """Erstellt ein NewsItem für einen einzelnen Artikel."""
        title = str(frontmatter.get("title") or "Ohne Titel")
        published_raw = frontmatter.get("published_date")
        published_date = (
            parse_german_date(str(published_raw)) if published_raw else None
        )

        content_plain = normalize_plain_text(markdown_body)
        item_content_hash = hashlib.sha256(content_plain.encode("utf-8")).hexdigest()
        item_id = compute_item_id(provider, title, page_url, item_content_hash)

        classification = self.classifier.classify(
            title=title, content=content_plain, url=page_url
        )

        return NewsItem(
            item_id=item_id,
            provider=provider,
            source_tier=self.determine_source_tier(provider, url=page_url),
            url=page_url,
            title=title,
            published_date=published_date,
            first_seen_at=page_first_seen,
            last_seen_at=page_first_seen,
            item_content_hash=item_content_hash,
            page_snapshot_hash=snapshot_hash,
            platforms=list(classification.platforms),
            topics=list(classification.topics),
            sentiment=classification.sentiment,
            severity=classification.severity,
            content_raw=markdown_body,
            content_plain=content_plain,
            is_baseline=is_baseline,
        )

    def _extract_best_url(self, section_text: str, base_url: str, title: str) -> str:
        """Sucht nach einem spezifischen Permalink im Text, sonst Fallback auf Anker."""
        # 1. Prüfe auf direkte Artikel-Links (z.B. https://rethink-p2p.de/news/... oder YouTube)
        url_matches = re.findall(r"\[(?:[^\]]+)\]\((https?://[^)]+)\)", section_text)
        for u in url_matches:
            clean_u = u.replace(r"\_", "_").replace(r"\-", "-")
            # Bevorzuge Links, die nicht nur auf Plattform-Erfahrungsberichte verweisen
            if "/news/" in clean_u or "youtube.com" in clean_u or "youtu.be" in clean_u:
                return clean_u

        # 2. Reiner URL-Link im Fließtext
        raw_urls = re.findall(r"(https?://\S+)", section_text)
        for u in raw_urls:
            u_clean = u.rstrip(".,;*)]").replace(r"\_", "_").replace(r"\-", "-")
            if "youtube.com" in u_clean or "youtu.be" in u_clean or "/news/" in u_clean:
                return u_clean

        # 3. Fallback: Basis-URL + Anker-Slug
        anchor = slugify(title)
        return f"{base_url}#{anchor}" if anchor else base_url


def process_all_scraped_news(
    data_dir: Path | str = "data",
    is_baseline: bool = False,
) -> tuple[int, int]:
    """
    Verarbeitet alle gescrapten Markdown-Dateien in data/news/ und data/platforms/
    und speichert sie als strukturierte Items in data/items/.

    Gibt zurück: (total_files_processed, total_items_extracted)
    """
    base = Path(data_dir)
    store = ItemStore(items_dir=base / "items")
    snapshot_mgr = SnapshotManager(base_dir=base / "snapshots")
    extractor = ItemExtractor(snapshot_manager=snapshot_mgr)

    total_files = 0
    total_items = 0

    scan_dirs = [base / "news", base / "platforms"]
    for sdir in scan_dirs:
        if not sdir.exists():
            continue
        for md_file in sorted(sdir.glob("**/*.md")):
            total_files += 1
            try:
                items = extractor.extract_from_markdown_file(
                    md_file, is_baseline=is_baseline
                )
                for item in items:
                    store.upsert_item(item, is_baseline=is_baseline)
                    total_items += 1
            except Exception as exc:
                logger.error("Fehler bei Verarbeitung von %s: %s", md_file, exc)

    return total_files, total_items


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="P2P News Item Extraktor (Stufe 0)")
    parser.add_argument("--data-dir", default="data", help="Pfad zum data Verzeichnis")
    parser.add_argument(
        "--baseline",
        action="store_true",
        help="Markiert Items als Baseline (Altbestand)",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
    )
    files_count, items_count = process_all_scraped_news(
        data_dir=args.data_dir, is_baseline=args.baseline
    )
    print(
        f"Abgeschlossen: {files_count} Dateien verarbeitet, {items_count} Items in {args.data_dir}/items/ extrahiert."
    )
