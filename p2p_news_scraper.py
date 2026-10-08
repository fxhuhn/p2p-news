"""
Modularer, produktionsreifer Scraper für P2P-News, Erfahrungsberichte und P2P-Plattformen (Python 3.11+).

Unterstützt mehrere Anbieter (Multi-Provider-Architektur):
1. Aggregatoren & Blogs:
   - P2P Empire:          https://p2pempire.com/de/nachrichten
   - P2P Game:            https://p2p-game.com/p2p-kredite-plattform-news
   - Rethink P2P:         https://rethink-p2p.de/news/
   - Passives Einkommen:  https://passives-einkommen-mit-p2p.de/p2p-kredite-news/
   - P2P Anlage:          https://p2p-anlage.de
2. Offizielle P2P-Plattformen:
   - Nectaro:             https://nectaro.eu (Hauptseite, Statistik, Dokumente, Anbahner, Blog)

Scannt die jeweiligen Übersichten sowie verlinkte Detailartikel / Erfahrungsberichte / Plattformseiten,
extrahiert Kerninhalte via Trafilatura, normalisiert Texte deterministisch
und erkennt Änderungen anhand von SHA-256 Hashes.

Ablagestruktur (Flat-File Storage mit YAML Frontmatter & Markdown):
data/
  ├── news/
  │     ├── p2p-empire/nachrichten-uebersicht.md
  │     ├── p2p-game/plattform-news.md
  │     └── ...
  ├── erfahrungen/
  │     ├── p2p-empire/<platform>.md
  │     ├── p2p-game/<platform>.md
  │     └── ...
  └── platforms/
        └── nectaro/
              ├── main.md
              ├── statistics.md
              ├── documents.md
              ├── lending-companies.md
              └── blog/
                    ├── index.md
                    └── <slug>.md
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
import re
import sys
import time
from abc import ABC, abstractmethod
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse

import httpx
import trafilatura
import yaml
from bs4 import BeautifulSoup, Tag
from trafilatura.settings import use_config

from normalization import is_metric_url, normalize_text

IGNORED_BINARY_EXTENSIONS: tuple[str, ...] = (
    ".pdf",
    ".zip",
    ".tar",
    ".gz",
    ".tgz",
    ".rar",
    ".7z",
    ".exe",
    ".bin",
    ".dmg",
    ".pkg",
    ".deb",
    ".rpm",
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
    ".ppt",
    ".pptx",
    ".odt",
    ".ods",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".svg",
    ".webp",
    ".ico",
    ".tiff",
    ".mp3",
    ".mp4",
    ".wav",
    ".avi",
    ".mov",
    ".mkv",
    ".flv",
)

# ==============================================================================
# Logging Configuration
# ==============================================================================


def setup_logging(level: int = logging.INFO) -> logging.Logger:
    """Konfiguriert strukturiertes Logging mit sauberem Format."""
    logger = logging.getLogger("p2p_news_scraper")
    logger.setLevel(level)
    logger.propagate = False

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)-7s] %(name)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    logging.getLogger("trafilatura").setLevel(logging.ERROR)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)

    return logger


logger = setup_logging()


# ==============================================================================
# Datenstrukturen & Konfiguration
# ==============================================================================


class ArticleStatus(StrEnum):
    """Status eines Artikels im Vergleich zum vorherigen Scan."""

    NEW = "neu"
    UNCHANGED = "unverändert"
    CHANGED = "geändert"


class ContentType(StrEnum):
    """Kategorie des Inhalts zur Differenzierung von Speicherort und Schema."""

    NEWS = "news"
    ERFAHRUNGEN = "erfahrungen"
    PLATFORM = "platform"


@dataclass(slots=True, frozen=True)
class ArticleItem:
    """Repräsentiert einen gescannten Artikel mit Metadaten und Hash."""

    url: str
    title: str | None
    published_date: str | None
    author: str | None
    content: str
    content_hash: str
    scanned_at: str


@dataclass(slots=True, frozen=True)
class ClassificationResult:
    """Ergebnis der automatischen Keyword-Klassifikation eines Beitrags."""

    platforms: tuple[str, ...]
    topics: tuple[str, ...]
    sentiment: str
    severity: str

    def to_dict(self) -> dict[str, object]:
        return {
            "platforms": list(self.platforms),
            "topics": list(self.topics),
            "sentiment": self.sentiment,
            "severity": self.severity,
        }


@dataclass(slots=True, frozen=True)
class ScanResult:
    """Ergebnis des Hash-Vergleichs für einen Artikel."""

    item: ArticleItem
    status: ArticleStatus
    file_path: Path
    provider_name: str
    previous_hash: str | None = None
    classification: ClassificationResult | None = None


# ==============================================================================
# Keyword-basierte Klassifikation (Plattformen, Themen, Sentiment, Severity)
# ==============================================================================

DEFAULT_PLATFORMS: tuple[str, ...] = (
    "nectaro",
    "mintos",
    "peerberry",
    "bondora",
    "esketit",
    "twino",
    "viainvest",
    "swaper",
    "estateguru",
    "inrento",
    "fintown",
    "loanch",
    "debitum",
    "indemo",
    "fagura",
    "revest",
    "hive5",
    "finbee",
    "devon",
    "lande",
    "monefit",
    "robocash",
    "heavyfinance",
    "iuvo",
    "income",
    "crowdestor",
    "lendermarket",
    "moncera",
    "neo-finance",
    "macclear",
    "afranga",
    "mypeak",
    "evenfi",
    "reinvest24",
)

DEFAULT_TOPIC_KEYWORDS: dict[str, tuple[str, ...]] = {
    "zinsen_aktionen": (
        "cashback",
        "bonus",
        "zinssatz",
        "zinserhöhung",
        "zinsanstieg",
        "zinsensenkung",
        "zinsaktion",
        "loyalty",
        "treueprogramm",
        "summer splash",
        "summer storm",
        "kampagne",
        "promo",
        "zinsen",
        "aktion",
        "rabatt",
        "rendite",
        "interest rate",
    ),
    "risiko_ausfaelle": (
        "ausfall",
        "ausfälle",
        "verzug",
        "insolvenz",
        "pleite",
        "zahlungsverzug",
        "verlust",
        "restrukturierung",
        "krieg",
        "moratorium",
        "rückforderung",
        "eintreibung",
        "suspendiert",
        "recovery",
        "in default",
        "delayed",
        "late payment",
        "scam",
        "betrug",
        "risiko",
        "verspätung",
        "schaden",
    ),
    "kreditanbahner": (
        "kreditanbahner",
        "anbahner",
        "originator",
        "loan originator",
        "lending company",
        "lending companies",
        "creditstar",
        "abele finance",
        "wowwo",
        "placet group",
        "ecofinance",
        "sun finance",
        "idf eurasia",
        "daphinvest",
        "partner",
    ),
    "regulierung_legal": (
        "lizenz",
        "lizenziert",
        "reguliert",
        "regulierung",
        "bafin",
        "fcmc",
        "ibf",
        "aufsicht",
        "agb",
        "terms and conditions",
        "investor protection",
        "anlegerschutz",
        "steuer",
        "steuern",
        "freistellungsauftrag",
        "quellensteuer",
        "withholding tax",
        "legal",
        "dokument",
        "rechtlich",
    ),
    "zahlen_statistik": (
        "statistik",
        "zahlen",
        "geschäftsbericht",
        "jahresabschluss",
        "quartal",
        "q1",
        "q2",
        "q3",
        "q4",
        "portfolio",
        "volumen",
        "monatsbericht",
        "monatszahlen",
        "profit",
        "gewinn",
        "earnings",
        "performance statistics",
        "investor earnings",
    ),
    "plattform_features": (
        "auto-invest",
        "autopilot",
        "app",
        "dashboard",
        "sekundärmarkt",
        "secondary market",
        "strategie",
        "update",
        "redesign",
        "neue funktion",
        "feature",
        "interface",
    ),
    "review_erfahrungen": (
        "erfahrungen",
        "test",
        "review",
        "testbericht",
        "bewertung",
        "erfahrungsbericht",
        "fazit",
        "erfahrung",
    ),
}

DEFAULT_SENTIMENT_KEYWORDS: dict[str, tuple[str, ...]] = {
    "positive": (
        "erhöhung",
        "anstieg",
        "wachstum",
        "cashback",
        "bonus",
        "gewinn",
        "profit",
        "erfolgreich",
        "lizenziert",
        "lizenz erhalten",
        "pünktlich",
        "rekord",
        "zugewinn",
        "verbesserung",
        "positive",
        "growth",
        "increased",
    ),
    "negative": (
        "senkung",
        "verlust",
        "ausfall",
        "insolvenz",
        "pleite",
        "verzug",
        "betrug",
        "suspendiert",
        "krieg",
        "problem",
        "kritik",
        "warnung",
        "schadensersatz",
        "verspätung",
        "default",
        "delayed",
        "loss",
        "risk",
        "warning",
    ),
}

DEFAULT_SEVERITY_KEYWORDS: dict[str, tuple[str, ...]] = {
    "high": (
        "insolvenz",
        "betrug",
        "pleite",
        "suspendiert",
        "moratorium",
        "aufsichtsverfahren",
        "warnung",
        "scam",
        "bankruptcy",
        "default",
        "strafanzeige",
    ),
    "medium": (
        "verzug",
        "verzögerung",
        "zinsensenkung",
        "steuer",
        "agb-änderung",
        "lizenz",
        "restrukturierung",
        "delayed",
        "late payment",
    ),
}


class KeywordClassifier:
    """
    Klassifiziert Artikelinhalte anhand konfigurierter oder voreingestellter Keywords.
    Erkennt Plattformen, Themengruppen, Sentiment und Dringlichkeit (Severity).
    """

    def __init__(
        self,
        platforms: Sequence[str] | None = None,
        topics: Mapping[str, Sequence[str]] | None = None,
        sentiment_keywords: Mapping[str, Sequence[str]] | None = None,
        severity_keywords: Mapping[str, Sequence[str]] | None = None,
    ) -> None:
        raw_platforms = list(platforms or DEFAULT_PLATFORMS)
        self.platforms = sorted(
            list(dict.fromkeys(p.strip().lower() for p in raw_platforms if p.strip()))
        )
        self.topics = {
            t: [kw.strip().lower() for kw in kws]
            for t, kws in (topics or DEFAULT_TOPIC_KEYWORDS).items()
        }
        self.sentiment_keywords = {
            s: [kw.strip().lower() for kw in kws]
            for s, kws in (sentiment_keywords or DEFAULT_SENTIMENT_KEYWORDS).items()
        }
        self.severity_keywords = {
            s: [kw.strip().lower() for kw in kws]
            for s, kws in (severity_keywords or DEFAULT_SEVERITY_KEYWORDS).items()
        }

    def classify(
        self,
        title: str | None,
        content: str,
        url: str = "",
        default_platform: str | None = None,
    ) -> ClassificationResult:
        full_text = f"{title or ''} {content} {url}".lower()

        # 1. Plattformen erkennen
        detected_platforms: list[str] = []
        if default_platform and default_platform.strip():
            norm_default = default_platform.strip().lower()
            if norm_default not in detected_platforms:
                detected_platforms.append(norm_default)

        for platform in self.platforms:
            pattern = rf"\b{re.escape(platform)}\b"
            if re.search(pattern, full_text):
                if platform not in detected_platforms:
                    detected_platforms.append(platform)

        # 2. Themen erkennen
        detected_topics: list[str] = []
        for topic, kws in self.topics.items():
            for kw in kws:
                pattern = rf"\b{re.escape(kw)}\b"
                if re.search(pattern, full_text):
                    detected_topics.append(topic)
                    break

        if not detected_topics:
            detected_topics.append("allgemein")

        # 3. Sentiment ermitteln
        pos_count = sum(
            1
            for kw in self.sentiment_keywords.get("positive", [])
            if re.search(rf"\b{re.escape(kw)}\b", full_text)
        )
        neg_count = sum(
            1
            for kw in self.sentiment_keywords.get("negative", [])
            if re.search(rf"\b{re.escape(kw)}\b", full_text)
        )

        if neg_count > pos_count:
            sentiment = "negativ"
        elif pos_count > neg_count:
            sentiment = "positiv"
        else:
            sentiment = "neutral"

        # 4. Severity ermitteln
        is_high = any(
            re.search(rf"\b{re.escape(kw)}\b", full_text)
            for kw in self.severity_keywords.get("high", [])
        )
        is_medium = any(
            re.search(rf"\b{re.escape(kw)}\b", full_text)
            for kw in self.severity_keywords.get("medium", [])
        )

        if is_high:
            severity = "high"
        elif is_medium or sentiment == "negativ":
            severity = "medium"
        else:
            severity = "low"

        return ClassificationResult(
            platforms=tuple(detected_platforms),
            topics=tuple(detected_topics),
            sentiment=sentiment,
            severity=severity,
        )


# ==============================================================================
# Text-Normalisierung & Hashing
# ==============================================================================


def compute_sha256_hash(text: str, url: str | None = None) -> str:
    """Berechnet den hexadezimalen SHA-256-Hash über den normalisierten UTF-8-Text."""
    is_metric = is_metric_url(url)
    normalized = normalize_text(text, is_metric=is_metric)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


# ==============================================================================
# Provider-Abstraktion (Multi-Provider Support)
# ==============================================================================


class BaseProvider(ABC):
    """Abstrakte Basisklasse für einen News-, Erfahrungs- oder Plattform-Anbieter."""

    name: str
    base_url: str
    is_platform: bool = False

    @abstractmethod
    def extract_links(
        self, html_content: str, client: httpx.Client | None = None
    ) -> list[str]:
        """Extrahiert alle relevanten Detailartikel-Links aus der Übersichtsseite."""
        pass

    @abstractmethod
    def classify_content_type(self, url: str) -> ContentType:
        """Klassifiziert eine URL als News, Erfahrungsbericht oder Plattformseite."""
        pass

    def classify_category(self, url: str) -> str | None:
        """Optionale feinere Unterkategorie für Frontmatter (z. B. statistics, documents, blog)."""
        return None

    @abstractmethod
    def extract_platform_name(self, url: str) -> str | None:
        """Extrahiert den Plattformnamen (z. B. 'nectaro'), falls anwendbar."""
        pass

    @abstractmethod
    def generate_filename(self, item: ArticleItem) -> str:
        """Erzeugt einen sauberen Dateinamen für das Dateisystem."""
        pass

    def extract_content(
        self,
        html_content: str,
        url: str,
        content_extractor: ContentExtractor,
    ) -> tuple[str, str | None, str | None, str | None] | None:
        """
        Optionaler Hook für Provider-spezifische Inhalts-Extraktion.
        Gibt None zurück, um die Standard-Trafilatura-Extraktion zu verwenden.
        """
        return None

    def get_target_path(self, base_dir: Path, item: ArticleItem) -> Path:
        """Ermittelt den Ziel-Dateipfad für einen Artikel."""
        content_type = self.classify_content_type(item.url)
        sub_dir = base_dir / content_type.value / self.name
        return sub_dir / self.generate_filename(item)


class P2PEmpireProvider(BaseProvider):
    """Provider-Implementierung für https://p2pempire.com/de/nachrichten."""

    name: str = "p2p-empire"
    base_url: str = "https://p2pempire.com/de/nachrichten"

    NON_ARTICLE_PATHS: frozenset[str] = frozenset(
        {
            "/de",
            "/de/",
            "/de/ueber-uns",
            "/de/haftungsausschluss",
            "/de/cookies",
            "/de/impressum",
            "/de/erfahrungen",
            "/de/bonus",
            "/de/nachrichten",
            "/de/ratgeber",
            "/de/p2p-kredite-risiko",
        }
    )

    def extract_links(
        self, html_content: str, client: httpx.Client | None = None
    ) -> list[str]:
        soup = BeautifulSoup(html_content, "html.parser")
        collected_urls: list[str] = []

        news_containers = soup.find_all(
            "div", class_=["news-box-wrapper", "news-wrapper"]
        )
        search_targets = news_containers if news_containers else [soup]

        for container in search_targets:
            for anchor in container.find_all("a", href=True):
                raw_href = anchor["href"].strip()
                if not raw_href or raw_href.startswith(
                    ("#", "javascript:", "mailto:", "tel:")
                ):
                    continue

                full_url = urljoin(self.base_url, raw_href)
                parsed = urlparse(full_url)
                cleaned_url = parsed._replace(fragment="").geturl()

                if parsed.netloc.lower() == "p2pempire.com":
                    path = parsed.path.rstrip("/")
                    if path not in self.NON_ARTICLE_PATHS and path != "":
                        if not any(
                            path.endswith(ext)
                            for ext in [".svg", ".png", ".jpg", ".pdf", ".css", ".js"]
                        ):
                            collected_urls.append(cleaned_url)

        return list(dict.fromkeys(collected_urls))

    def extract_content(
        self,
        html_content: str,
        url: str,
        content_extractor: ContentExtractor,
    ) -> tuple[str, str | None, str | None, str | None] | None:
        """
        Extrahiert die News-Beiträge der P2P Empire Übersichtsseite unter Beibehaltung
        der 'h2' (##) Überschriften, Veröffentlichungsdaten und Bewertungs-Links.
        """
        if url.rstrip("/") != self.base_url.rstrip("/"):
            return None

        soup = BeautifulSoup(html_content, "html.parser")
        boxes = soup.find_all("div", class_="news-box-wrapper")
        if not boxes:
            return None

        lines: list[str] = [
            "# P2P News | Aktuelle Neuigkeiten",
            "",
            "Überblick über die neuesten Nachrichten aus der P2P-Lending Industrie",
            "",
        ]

        latest_date = None

        for box in boxes:
            date_el = box.find(class_="news-date")
            date_str = date_el.get_text(strip=True) if date_el else ""
            if not latest_date and date_str:
                latest_date = date_str

            title_el = box.find("h2")
            title_str = title_el.get_text(strip=True) if title_el else ""

            p_el = box.find("p")
            body_str = p_el.get_text(strip=True) if p_el else ""

            link_el = box.find(class_="review-link")
            link_a = link_el.find("a") if link_el else None

            if title_str:
                lines.append(f"## {title_str}")
            if date_str:
                lines.append(f"*{date_str}*")
            lines.append("")
            if body_str:
                lines.append(body_str)
                lines.append("")
            if link_a and link_a.get("href"):
                full_href = urljoin(self.base_url, link_a["href"].strip())
                anchor_text = link_a.get_text(strip=True) or "Zum Erfahrungsbericht"
                lines.append(f"[{anchor_text}]({full_href})")
                lines.append("")
            lines.append("---")
            lines.append("")

        full_content = "\n".join(lines).strip()
        page_title = "P2P News | Aktuelle Neuigkeiten"
        if soup.title and soup.title.string:
            page_title = soup.title.string.strip()

        return full_content, page_title, latest_date, None

    def classify_content_type(self, url: str) -> ContentType:
        path = urlparse(url).path.lower()
        if "/erfahrungen" in path:
            return ContentType.ERFAHRUNGEN
        return ContentType.NEWS

    def extract_platform_name(self, url: str) -> str | None:
        path = urlparse(url).path.rstrip("/")
        parts = [p for p in path.split("/") if p]
        if "erfahrungen" in parts:
            idx = parts.index("erfahrungen")
            if idx + 1 < len(parts):
                return parts[idx + 1].strip().lower()
        return None

    def generate_filename(self, item: ArticleItem) -> str:
        if item.url.rstrip("/") == self.base_url.rstrip("/"):
            return "nachrichten-uebersicht.md"
        platform = self.extract_platform_name(item.url)
        if platform:
            return f"{platform}.md"
        slug = re.sub(r"[^a-zA-Z0-9_\-]+", "-", urlparse(item.url).path).strip("-")
        return f"{slug or 'artikel'}.md"


class P2PGameProvider(BaseProvider):
    """Provider-Implementierung für https://p2p-game.com/p2p-kredite-plattform-news."""

    name: str = "p2p-game"
    base_url: str = "https://p2p-game.com/p2p-kredite-plattform-news"

    def extract_links(
        self, html_content: str, client: httpx.Client | None = None
    ) -> list[str]:
        soup = BeautifulSoup(html_content, "html.parser")
        collected_urls: list[str] = []

        for anchor in soup.find_all("a", href=True):
            raw_href = anchor["href"].strip()
            if not raw_href or raw_href.startswith(
                ("#", "javascript:", "mailto:", "tel:")
            ):
                continue

            full_url = urljoin(self.base_url, raw_href)
            parsed = urlparse(full_url)
            cleaned_url = parsed._replace(fragment="").geturl()

            if parsed.netloc.lower() == "p2p-game.com":
                path = parsed.path.lower().rstrip("/")
                # Relevant sind Erfahrungsberichte (z. B. /nectaro-erfahrungen)
                if "erfahrungen" in path:
                    collected_urls.append(cleaned_url)

        return list(dict.fromkeys(collected_urls))

    def classify_content_type(self, url: str) -> ContentType:
        path = urlparse(url).path.lower()
        if "erfahrungen" in path:
            return ContentType.ERFAHRUNGEN
        return ContentType.NEWS

    def extract_platform_name(self, url: str) -> str | None:
        path = urlparse(url).path.strip("/").lower()
        if not path or "news" in path:
            return None
        match = re.search(r"([a-z0-9\-]+)-erfahrungen", path, re.IGNORECASE)
        if match:
            slug = match.group(1)
            # Bereinige Präfixe wie '4-jahre-'
            slug = re.sub(r"^\d+-jahre-", "", slug)
            return slug
        return None

    def generate_filename(self, item: ArticleItem) -> str:
        if item.url.rstrip("/") == self.base_url.rstrip("/"):
            return "plattform-news.md"
        platform = self.extract_platform_name(item.url)
        if platform:
            return f"{platform}.md"
        slug = re.sub(r"[^a-zA-Z0-9_\-]+", "-", urlparse(item.url).path).strip("-")
        return f"{slug or 'artikel'}.md"


class RethinkP2PProvider(BaseProvider):
    """Provider-Implementierung für https://rethink-p2p.de/news/."""

    name: str = "rethink-p2p"
    base_url: str = "https://rethink-p2p.de/news/"

    def extract_links(
        self, html_content: str, client: httpx.Client | None = None
    ) -> list[str]:
        soup = BeautifulSoup(html_content, "html.parser")
        news_urls: list[str] = []
        erfahrungen_urls: list[str] = []

        for anchor in soup.find_all("a", href=True):
            raw_href = anchor["href"].strip()
            if not raw_href or raw_href.startswith(
                ("#", "javascript:", "mailto:", "tel:")
            ):
                continue

            full_url = urljoin(self.base_url, raw_href)
            parsed = urlparse(full_url)
            cleaned_url = parsed._replace(fragment="", query="").geturl()

            if parsed.netloc.lower() == "rethink-p2p.de":
                path = parsed.path.strip("/")
                if path.startswith("news/") and path != "news":
                    news_urls.append(cleaned_url)
                elif "erfahrungen" in path:
                    erfahrungen_urls.append(cleaned_url)

        # Aktuelle News-Artikel zuerst, danach Plattform-Erfahrungsberichte
        combined = list(dict.fromkeys(news_urls)) + list(
            dict.fromkeys(erfahrungen_urls)
        )
        return list(dict.fromkeys(combined))

    def extract_content(
        self,
        html_content: str,
        url: str,
        content_extractor: ContentExtractor,
    ) -> tuple[str, str | None, str | None, str | None] | None:
        """
        Extrahiert die vollständigen News-Beiträge der rethink-p2p Übersichtsseite aus dem
        embedded 'data-nf' JSON-Datensatz, um Textabschneidungen (...) in den HTML-Karten zu verhindern.
        """
        if url.rstrip("/") != self.base_url.rstrip("/"):
            return None

        soup = BeautifulSoup(html_content, "html.parser")
        div_nf = soup.find("div", attrs={"data-nf": True})
        if not div_nf or not isinstance(div_nf, Tag):
            return None
        raw_nf = div_nf.get("data-nf")
        if not raw_nf or not isinstance(raw_nf, str):
            return None

        try:
            raw_json = raw_nf
            data = json.loads(raw_json)
            posts = data.get("posts", [])
        except Exception as exc:
            logger.warning("Konnte data-nf JSON auf %s nicht parsen: %s", url, exc)
            return None

        if not posts:
            return None

        cards = soup.find_all(class_="nf-card")
        lines: list[str] = [
            "# P2P Kredite News",
            "",
            "Die aktuellsten Nachrichten aus dem P2P Kredite Marktumfeld auf einen Blick.",
            "",
        ]

        latest_date = None

        for idx, post in enumerate(posts):
            card = cards[idx] if idx < len(cards) else None
            permalink = ""
            if card:
                link_el = card.find(class_="nf-card-permalink")
                if link_el and link_el.get("href"):
                    permalink = link_el["href"].strip()

            date_str = str(post.get("date") or "").strip()
            if not latest_date and date_str:
                latest_date = date_str

            title_str = str(post.get("title") or "").strip()
            content_html = str(post.get("content") or "").strip()
            platform_url = str(post.get("platform") or "").strip()
            platform_name = str(post.get("platform_name") or "").strip()

            # HTML-Inhalt in Markdown umwandeln
            entry_md, _, _, _ = content_extractor.extract(
                f"<html><body>{content_html}</body></html>",
                permalink or url,
            )

            lines.append(f"## {title_str}")
            if date_str:
                lines.append(f"*{date_str}*")
            lines.append("")
            if entry_md:
                lines.append(entry_md)
                lines.append("")
            if platform_url and platform_name:
                lines.append(f"[{platform_name} Erfahrungsbericht]({platform_url})")
                lines.append("")
            lines.append("---")
            lines.append("")

        full_content = "\n".join(lines).strip()
        page_title = "P2P Kredite News – Analysen & Marktupdates | re:think P2P"
        if soup.title and soup.title.string:
            page_title = soup.title.string.strip()

        return full_content, page_title, latest_date, "Denny Neidhardt"

    def classify_content_type(self, url: str) -> ContentType:
        path = urlparse(url).path.lower()
        if "erfahrungen" in path:
            return ContentType.ERFAHRUNGEN
        return ContentType.NEWS

    def extract_platform_name(self, url: str) -> str | None:
        path = urlparse(url).path.strip("/").lower()
        match = re.search(r"([a-z0-9\-]+)-erfahrungen", path, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return None

    def generate_filename(self, item: ArticleItem) -> str:
        if item.url.rstrip("/") == self.base_url.rstrip("/"):
            return "news-uebersicht.md"
        platform = self.extract_platform_name(item.url)
        if platform and self.classify_content_type(item.url) == ContentType.ERFAHRUNGEN:
            return f"{platform}.md"
        slug = re.sub(
            r"[^a-zA-Z0-9_\-]+", "-", urlparse(item.url).path.strip("/")
        ).strip("-")
        slug = re.sub(r"^news-", "", slug)
        return f"{slug or 'artikel'}.md"


class PassivesEinkommenProvider(BaseProvider):
    """Provider-Implementierung für https://passives-einkommen-mit-p2p.de/p2p-kredite-news/ (Lars Wrobbel)."""

    name: str = "passives-einkommen"
    base_url: str = "https://passives-einkommen-mit-p2p.de/p2p-kredite-news/"

    def extract_links(
        self, html_content: str, client: httpx.Client | None = None
    ) -> list[str]:
        soup = BeautifulSoup(html_content, "html.parser")
        news_urls: list[str] = []
        erfahrungen_urls: list[str] = []

        for anchor in soup.find_all("a", href=True):
            raw_href = anchor["href"].strip()
            if not raw_href or raw_href.startswith(
                ("#", "javascript:", "mailto:", "tel:")
            ):
                continue

            full_url = urljoin(self.base_url, raw_href)
            parsed = urlparse(full_url)
            cleaned_url = parsed._replace(fragment="", query="").geturl()

            if parsed.netloc.lower() == "passives-einkommen-mit-p2p.de":
                path = parsed.path.strip("/")
                if any(
                    ignore in path
                    for ignore in ["wp-content", "author", "category", "tag"]
                ):
                    continue
                if re.search(r"p2p-kredite-\d+-\d+", path):
                    news_urls.append(cleaned_url)
                elif "erfahrungen" in path:
                    erfahrungen_urls.append(cleaned_url)

        # Aktuelle News-Detailbeiträge zuerst, danach statische Erfahrungsberichte
        combined = list(dict.fromkeys(news_urls)) + list(
            dict.fromkeys(erfahrungen_urls)
        )
        return list(dict.fromkeys(combined))

    def classify_content_type(self, url: str) -> ContentType:
        path = urlparse(url).path.lower()
        if "erfahrungen" in path:
            return ContentType.ERFAHRUNGEN
        return ContentType.NEWS

    def extract_platform_name(self, url: str) -> str | None:
        path = urlparse(url).path.strip("/").lower()
        match = re.search(r"([a-z0-9\-]+)-erfahrungen", path, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return None

    def generate_filename(self, item: ArticleItem) -> str:
        if item.url.rstrip("/") == self.base_url.rstrip("/"):
            return "p2p-kredite-news.md"
        platform = self.extract_platform_name(item.url)
        if platform and self.classify_content_type(item.url) == ContentType.ERFAHRUNGEN:
            return f"{platform}.md"
        slug = re.sub(
            r"[^a-zA-Z0-9_\-]+", "-", urlparse(item.url).path.strip("/")
        ).strip("-")
        return f"{slug or 'artikel'}.md"


class P2PAnlageProvider(BaseProvider):
    """Provider-Implementierung für https://p2p-anlage.de."""

    name: str = "p2p-anlage"
    base_url: str = "https://p2p-anlage.de"

    def extract_links(
        self, html_content: str, client: httpx.Client | None = None
    ) -> list[str]:
        soup = BeautifulSoup(html_content, "html.parser")
        collected_urls: list[str] = []

        for anchor in soup.find_all("a", href=True):
            raw_href = anchor["href"].strip()
            if not raw_href or raw_href.startswith(
                ("#", "javascript:", "mailto:", "tel:")
            ):
                continue

            full_url = urljoin(self.base_url, raw_href)
            parsed = urlparse(full_url)
            cleaned_url = parsed._replace(fragment="", query="").geturl()

            if parsed.netloc.lower() == "p2p-anlage.de":
                path = parsed.path.strip("/")
                # Artikel mit Datums-Pfad YYYY/MM/...
                if re.match(r"^\d{4}/\d{2}/[a-z0-9\-]+", path):
                    collected_urls.append(cleaned_url)

        return list(dict.fromkeys(collected_urls))

    def classify_content_type(self, url: str) -> ContentType:
        path = urlparse(url).path.lower()
        if "erfahrungen" in path:
            return ContentType.ERFAHRUNGEN
        return ContentType.NEWS

    def extract_platform_name(self, url: str) -> str | None:
        path = urlparse(url).path.strip("/").lower()
        known_platforms = [
            "mypeak",
            "loanch",
            "debitum",
            "indemo",
            "fagura",
            "mintos",
            "nectaro",
            "peerberry",
            "afranga",
            "esketit",
            "inrento",
            "fintown",
            "revest",
            "hive5",
            "finbee",
            "devon",
            "twino",
            "viainvest",
            "swaper",
            "bondora",
            "estateguru",
            "lande",
        ]
        for p in known_platforms:
            if p in path:
                return p
        return None

    def generate_filename(self, item: ArticleItem) -> str:
        if item.url.rstrip("/") == self.base_url.rstrip("/"):
            return "p2p-anlage-uebersicht.md"
        platform = self.extract_platform_name(item.url)
        slug = re.sub(
            r"[^a-zA-Z0-9_\-]+", "-", urlparse(item.url).path.strip("/")
        ).strip("-")
        slug = re.sub(r"^\d{4}-\d{2}-", "", slug)
        if platform and self.classify_content_type(item.url) == ContentType.ERFAHRUNGEN:
            return f"{platform}.md"
        return f"{slug or 'artikel'}.md"


# ==============================================================================
# P2P-Plattform Provider (Offizielle Plattformseiten)
# ==============================================================================


class BasePlatformProvider(BaseProvider):
    """
    Abstrakte Basisklasse für offizielle P2P-Plattformen (z. B. Nectaro).
    Speichert Inhalte strukturiert unter:
    data/platforms/<platform_name>/
      ├── main.md
      ├── statistics.md
      ├── documents.md
      ├── lending-companies.md
      └── blog/
            ├── index.md
            └── <slug>.md
    """

    is_platform: bool = True

    def classify_content_type(self, url: str) -> ContentType:
        return ContentType.PLATFORM

    def extract_platform_name(self, url: str) -> str | None:
        return self.name

    def classify_category(self, url: str) -> str:
        path = urlparse(url).path.strip("/").lower()
        if not path:
            return "overview"
        if path == "blog" or path.startswith("blog/"):
            return "blog"
        if path == "statistics":
            return "statistics"
        if path == "documents" or path.startswith("documents/"):
            return "documents"
        if path == "lending-companies":
            return "lending-companies"
        return path.split("/")[0]

    def generate_filename(self, item: ArticleItem) -> str:
        path = urlparse(item.url).path.strip("/").lower()
        if not path:
            return "main.md"
        if path == "blog":
            return "index.md"
        parts = path.split("/")
        return f"{parts[-1]}.md"

    def generate_platform_relative_path(self, item: ArticleItem) -> Path:
        path = urlparse(item.url).path.strip("/").lower()
        if not path:
            return Path("main.md")
        if path == "blog":
            return Path("blog") / "index.md"
        if path.startswith("blog/"):
            slug = path.split("/", 1)[1].strip("/")
            clean_slug = re.sub(r"[^a-zA-Z0-9_\-]+", "-", slug).strip("-")
            return Path("blog") / f"{clean_slug or 'post'}.md"

        parts = [
            re.sub(r"[^a-zA-Z0-9_\-]+", "-", p).strip("-") for p in path.split("/") if p
        ]
        if len(parts) > 1:
            return Path(*parts[:-1]) / f"{parts[-1]}.md"
        return Path(f"{parts[0]}.md")

    def get_target_path(self, base_dir: Path, item: ArticleItem) -> Path:
        platform_dir = base_dir / "platforms" / self.name
        rel_path = self.generate_platform_relative_path(item)
        return platform_dir / rel_path


@dataclass(slots=True)
class PlatformConfig:
    """Deklarative Konfiguration für eine P2P-Plattform."""

    name: str
    base_url: str
    subpages: list[str] = field(default_factory=list)
    blog_path: str | None = None
    blog_pattern: str | None = None
    auto_discover: bool = True


class PlatformProvider(BasePlatformProvider):
    """
    Generischer, rein deklarativ konfigurierbarer Provider für P2P-Plattformen.
    Beliebig viele Plattformen können ohne Python-Code über `providers.yaml` ergänzt werden.
    """

    def __init__(self, config: PlatformConfig) -> None:
        self.config = config
        self.name = config.name.strip().lower()
        self.base_url = config.base_url.rstrip("/")

    def extract_links(
        self, html_content: str, client: httpx.Client | None = None
    ) -> list[str]:
        urls: list[str] = []
        domain = urlparse(self.base_url).netloc.lower()

        # 1. Konfigurierte Subpages hinzufügen
        for sub in self.config.subpages:
            urls.append(urljoin(self.base_url, sub))

        # 2. Blog-Übersicht hinzufügen & Blog-Artikel extrahieren
        blog_html: str | None = None
        if self.config.blog_path:
            blog_url = urljoin(self.base_url, self.config.blog_path)
            urls.append(blog_url)
            if client is not None:
                try:
                    resp = client.get(blog_url)
                    if resp.status_code == 200:
                        blog_html = resp.text
                except Exception as exc:
                    logger.warning(
                        "[%s] Konnte Blog-Übersicht (%s) nicht abrufen: %s",
                        self.name,
                        blog_url,
                        exc,
                    )

        # 3. Quellen für Link-Extraktion zusammenstellen
        sources_to_check = [html_content]
        if blog_html:
            sources_to_check.append(blog_html)

        blog_prefix = (
            self.config.blog_path.strip("/") if self.config.blog_path else "blog"
        )

        # 4. Links aus HTML-Quellen extrahieren (Blog-Artikel & Auto-Discovery)
        for src in sources_to_check:
            soup = BeautifulSoup(src, "html.parser")
            for anchor in soup.find_all("a", href=True):
                raw_href = anchor["href"].strip()
                if not raw_href or raw_href.startswith(
                    ("#", "javascript:", "mailto:", "tel:")
                ):
                    continue

                full_url = urljoin(self.base_url, raw_href)
                parsed = urlparse(full_url)
                cand_domain = parsed.netloc.lower()
                if cand_domain != domain and not cand_domain.endswith("." + domain):
                    continue

                path = parsed.path.strip("/")
                lower_path = path.lower()
                # Binäre Dateien (insbesondere PDFs) strikt ausschließen
                if any(
                    lower_path.endswith(ext) or f"{ext}/" in lower_path
                    for ext in IGNORED_BINARY_EXTENSIONS
                ):
                    continue

                cleaned_url = parsed._replace(fragment="", query="").geturl()
                if parsed.path in ("", "/"):
                    cleaned_url = cleaned_url.rstrip("/") + "/"

                # A) Blog-Artikel erkennen
                if self.config.blog_pattern:
                    if re.search(self.config.blog_pattern, path):
                        urls.append(cleaned_url)
                elif (
                    blog_prefix
                    and path.startswith(f"{blog_prefix}/")
                    and path != blog_prefix
                ):
                    urls.append(cleaned_url)

                # B) Auto-Discovery relevanter Plattformseiten von der Startseite
                if self.config.auto_discover:
                    lower_path = path.lower()
                    if any(
                        kw in lower_path
                        for kw in ["statistic", "statistik", "numbers", "zahlen"]
                    ):
                        urls.append(cleaned_url)
                    elif any(
                        kw in lower_path
                        for kw in ["document", "legal", "terms", "bedingungen"]
                    ):
                        urls.append(cleaned_url)
                    elif any(
                        kw in lower_path
                        for kw in [
                            "lending-comp",
                            "loan-originat",
                            "partner",
                            "anbahner",
                        ]
                    ):
                        urls.append(cleaned_url)

        return list(dict.fromkeys(urls))


# Rückwärtskompatibler Alias
class NectaroPlatformProvider(PlatformProvider):
    """Alias für Abwärtskompatibilität."""

    def __init__(self) -> None:
        super().__init__(
            PlatformConfig(
                name="nectaro",
                base_url="https://nectaro.eu",
                subpages=["/statistics/", "/documents/", "/lending-companies/"],
                blog_path="/blog/",
                auto_discover=True,
            )
        )


# ==============================================================================
# Deklaratives Provider-Laden aus providers.yaml
# ==============================================================================

DEFAULT_CONFIG_PATH = Path("providers.yaml")


def load_providers_from_yaml(
    config_path: Path | str | None = None,
) -> dict[str, BaseProvider]:
    """
    Lädt alle Provider deklarativ aus einer YAML-Datei.
    Neue Plattformen können ohne Python-Code in providers.yaml registriert werden.
    """
    providers: dict[str, BaseProvider] = {
        "p2p-empire": P2PEmpireProvider(),
        "p2p-game": P2PGameProvider(),
        "rethink-p2p": RethinkP2PProvider(),
        "passives-einkommen": PassivesEinkommenProvider(),
        "p2p-anlage": P2PAnlageProvider(),
    }

    path = Path(config_path) if config_path else DEFAULT_CONFIG_PATH
    if not path.exists():
        providers["nectaro"] = NectaroPlatformProvider()
        return providers

    try:
        content = path.read_text(encoding="utf-8")
        data = yaml.safe_load(content) or {}
    except Exception as exc:
        logger.warning("Konnte Konfigurationsdatei %s nicht laden: %s", path, exc)
        providers["nectaro"] = NectaroPlatformProvider()
        return providers

    # Plattformen deklarativ instanziieren
    platforms_data = data.get("platforms", {})
    if isinstance(platforms_data, dict):
        for p_name, p_conf in platforms_data.items():
            if not isinstance(p_conf, dict):
                continue
            base_url = p_conf.get("base_url")
            if not base_url:
                continue
            cfg = PlatformConfig(
                name=str(p_name),
                base_url=str(base_url),
                subpages=list(p_conf.get("subpages", [])),
                blog_path=p_conf.get("blog_path"),
                blog_pattern=p_conf.get("blog_pattern"),
                auto_discover=bool(p_conf.get("auto_discover", True)),
            )
            providers[str(p_name)] = PlatformProvider(cfg)

    if "nectaro" not in providers:
        providers["nectaro"] = NectaroPlatformProvider()

    return providers


def load_classifier_from_yaml(
    config_path: Path | str | None = None,
    merge_defaults: bool = True,
) -> KeywordClassifier:
    """
    Lädt das konfigurierbare Keyword-Wörterbuch aus der YAML-Datei.
    Unterstützt sowohl Erweiterung (merge_defaults=True) als auch komplettes Überschreiben:
      - Plattformen: Führt Standard-Plattformen, konfigurierte Plattformen und 'platforms'-Provider zusammen
      - topics: Ergänzt Standardthemen um neue Themen oder zusätzliche Keywords bestehender Themen
      - sentiment: Ergänzt/konfiguriert positive/negative Keywords
      - severity: Ergänzt/konfiguriert Dringlichkeits-Keywords (high, medium)
    """
    path = Path(config_path) if config_path else DEFAULT_CONFIG_PATH
    if not path.exists():
        return KeywordClassifier()

    try:
        content = path.read_text(encoding="utf-8")
        data = yaml.safe_load(content) or {}
    except Exception as exc:
        logger.warning("Konnte Klassifikations-Konfiguration nicht laden: %s", exc)
        return KeywordClassifier()

    class_data = data.get("classification", {})
    extra_platforms = list(data.get("platforms", {}).keys())

    configured_platforms = class_data.get("platforms")
    if configured_platforms:
        if merge_defaults:
            merged_platforms = list(
                dict.fromkeys(
                    list(DEFAULT_PLATFORMS)
                    + list(configured_platforms)
                    + extra_platforms
                )
            )
        else:
            merged_platforms = list(
                dict.fromkeys(list(configured_platforms) + extra_platforms)
            )
    else:
        merged_platforms = list(
            dict.fromkeys(list(DEFAULT_PLATFORMS) + extra_platforms)
        )

    # Topics zusammenführen
    configured_topics = class_data.get("topics") or {}
    if merge_defaults:
        merged_topics: dict[str, list[str]] = {
            t: list(kws) for t, kws in DEFAULT_TOPIC_KEYWORDS.items()
        }
        for topic_name, kws in configured_topics.items():
            if topic_name in merged_topics:
                merged_topics[topic_name] = list(
                    dict.fromkeys(merged_topics[topic_name] + list(kws))
                )
            else:
                merged_topics[topic_name] = list(dict.fromkeys(list(kws)))
    else:
        merged_topics = configured_topics or dict(DEFAULT_TOPIC_KEYWORDS)

    # Sentiment zusammenführen
    configured_sentiment = class_data.get("sentiment") or {}
    if merge_defaults and configured_sentiment:
        merged_sentiment: dict[str, list[str]] = {
            s: list(kws) for s, kws in DEFAULT_SENTIMENT_KEYWORDS.items()
        }
        for s_type, kws in configured_sentiment.items():
            if s_type in merged_sentiment:
                merged_sentiment[s_type] = list(
                    dict.fromkeys(merged_sentiment[s_type] + list(kws))
                )
            else:
                merged_sentiment[s_type] = list(dict.fromkeys(list(kws)))
    else:
        merged_sentiment = configured_sentiment or dict(DEFAULT_SENTIMENT_KEYWORDS)

    # Severity zusammenführen
    configured_severity = class_data.get("severity") or {}
    if merge_defaults and configured_severity:
        merged_severity: dict[str, list[str]] = {
            sev: list(kws) for sev, kws in DEFAULT_SEVERITY_KEYWORDS.items()
        }
        for sev_level, kws in configured_severity.items():
            if sev_level in merged_severity:
                merged_severity[sev_level] = list(
                    dict.fromkeys(merged_severity[sev_level] + list(kws))
                )
            else:
                merged_severity[sev_level] = list(dict.fromkeys(list(kws)))
    else:
        merged_severity = configured_severity or dict(DEFAULT_SEVERITY_KEYWORDS)

    return KeywordClassifier(
        platforms=merged_platforms,
        topics=merged_topics,
        sentiment_keywords=merged_sentiment,
        severity_keywords=merged_severity,
    )


REGISTERED_PROVIDERS: dict[str, BaseProvider] = load_providers_from_yaml()
DEFAULT_CLASSIFIER: KeywordClassifier = load_classifier_from_yaml()


def detect_provider_for_url(
    url: str, providers_map: dict[str, BaseProvider] | None = None
) -> BaseProvider:
    """Ermittelt den passenden Provider anhand der Domain der URL oder erzeugt einen dynamischen PlatformProvider."""
    providers = providers_map if providers_map is not None else REGISTERED_PROVIDERS
    domain = urlparse(url).netloc.lower()

    # 1. Bekannte Domains abgleichen
    for prov_name, prov in providers.items():
        prov_domain = urlparse(prov.base_url).netloc.lower()
        if prov_domain and (
            domain == prov_domain
            or domain.endswith("." + prov_domain)
            or prov_name in domain
        ):
            return prov

    # 2. Dynamischer PlatformProvider für unbekannte Plattform-URLs (Zero-Code Auto-Discovery)
    clean_name = domain.replace("www.", "").split(".")[0]
    clean_name = re.sub(r"[^a-zA-Z0-9\-]+", "-", clean_name).strip("-") or "plattform"
    base_url = f"{urlparse(url).scheme or 'https'}://{urlparse(url).netloc}"
    return PlatformProvider(
        PlatformConfig(
            name=clean_name,
            base_url=base_url,
            auto_discover=True,
        )
    )


# ==============================================================================
# Flat-File Storage: YAML Frontmatter & Markdown
# ==============================================================================


def parse_markdown_with_frontmatter(file_content: str) -> tuple[dict, str]:
    """Trennt YAML Frontmatter vom Markdown-Haupttext."""
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", file_content, re.DOTALL)
    if not match:
        return {}, file_content.strip()

    frontmatter_raw, body_raw = match.group(1), match.group(2)
    try:
        data = yaml.safe_load(frontmatter_raw)
        frontmatter = data if isinstance(data, dict) else {}
    except Exception as exc:
        logger.warning("Fehler beim Parsen von Frontmatter: %s", exc)
        frontmatter = {}

    return frontmatter, body_raw.strip()


def serialize_markdown_with_frontmatter(frontmatter: dict, body: str) -> str:
    """Formatiert Metadaten und Inhalt als standardkonformes Markdown mit YAML Frontmatter."""
    yaml_header = yaml.safe_dump(
        frontmatter,
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=False,
    )
    clean_body = body.strip()
    if clean_body:
        return f"---\n{yaml_header}---\n\n{clean_body}\n"
    return f"---\n{yaml_header}---\n"


class MarkdownStorageManager:
    """
    Verwaltet das Speichern und Lesen von Artikeln als Markdown-Dateien mit YAML Frontmatter.
    Trennt physisch nach Content-Typ (news / erfahrungen) und Provider (p2p-empire / p2p-game).
    """

    def __init__(
        self, output_dir: Path | str, classifier: KeywordClassifier | None = None
    ) -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.classifier = classifier or DEFAULT_CLASSIFIER
        self._url_to_path: dict[str, Path] = {}
        self._reindex()

    def _reindex(self) -> None:
        """Scannt rekursiv das Verzeichnis und indiziert vorhandene Dateien anhand des Frontmatter-Feldes 'url'."""
        self._url_to_path.clear()
        for md_file in self.output_dir.rglob("*.md"):
            try:
                content = md_file.read_text(encoding="utf-8")
                frontmatter, _ = parse_markdown_with_frontmatter(content)
                url = frontmatter.get("url")
                if url and isinstance(url, str):
                    self._url_to_path[url] = md_file
            except Exception as exc:
                logger.warning(
                    "Konnte Datei %s beim Indizieren nicht lesen: %s", md_file, exc
                )

        logger.debug(
            "Speicherverzeichnis indiziert: %d Dateien in %s",
            len(self._url_to_path),
            self.output_dir,
        )

    def get_target_path(self, item: ArticleItem, provider: BaseProvider) -> Path:
        """Bestimmt den Zielpfad strukturiert nach Typ und Provider."""
        return provider.get_target_path(self.output_dir, item)

    def _write_file_atomically(self, target_path: Path, content: str) -> None:
        """Schreibt eine Datei atomar über eine temporäre Datei zur Vermeidung von Datenkorruption."""
        target_path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = target_path.with_name(f".tmp_{target_path.name}")
        try:
            temp_path.write_text(content, encoding="utf-8")
            os.replace(temp_path, target_path)
        finally:
            if temp_path.exists():
                try:
                    temp_path.unlink()
                except OSError:
                    pass

    def record_scan(self, item: ArticleItem, provider: BaseProvider) -> ScanResult:
        """Liest bestehenden Stand ab, vergleicht Hashes und aktualisiert Frontmatter/Body."""
        existing_path = self._url_to_path.get(item.url)

        content_type = provider.classify_content_type(item.url)
        platform = provider.extract_platform_name(item.url)
        category = provider.classify_category(item.url)

        classification = self.classifier.classify(
            title=item.title,
            content=item.content,
            url=item.url,
            default_platform=platform,
        )

        if existing_path and existing_path.exists():
            old_raw = existing_path.read_text(encoding="utf-8")
            old_frontmatter, old_body = parse_markdown_with_frontmatter(old_raw)
            old_hash = str(old_frontmatter.get("content_hash", ""))
            old_history = old_frontmatter.get("history", [])
            if not isinstance(old_history, list):
                old_history = []

            scan_count = int(old_frontmatter.get("scan_count", 1)) + 1
            first_seen_at = old_frontmatter.get("first_seen_at", item.scanned_at)

            # 1. Unverändert
            if old_hash == item.content_hash:
                new_frontmatter: dict[str, Any] = {
                    "source": provider.name,
                    "content_type": content_type.value,
                }
                cat_val = category or old_frontmatter.get("category")
                if cat_val is not None:
                    new_frontmatter["category"] = str(cat_val)
                if platform:
                    new_frontmatter["platform"] = platform
                new_frontmatter.update(
                    {
                        "url": item.url,
                        "title": item.title or old_frontmatter.get("title"),
                        "published_date": item.published_date
                        or old_frontmatter.get("published_date"),
                        "author": item.author or old_frontmatter.get("author"),
                        "content_hash": item.content_hash,
                        "first_seen_at": first_seen_at,
                        "last_scanned_at": item.scanned_at,
                        "scan_count": scan_count,
                        "status": ArticleStatus.UNCHANGED.value,
                        "classification": classification.to_dict(),
                        "history": old_history,
                    }
                )

                file_text = serialize_markdown_with_frontmatter(
                    new_frontmatter, old_body
                )
                self._write_file_atomically(existing_path, file_text)

                return ScanResult(
                    item=item,
                    status=ArticleStatus.UNCHANGED,
                    file_path=existing_path,
                    provider_name=provider.name,
                    previous_hash=old_hash,
                    classification=classification,
                )

            # 2. Geändert
            updated_history = list(old_history)
            updated_history.append(
                {
                    "content_hash": item.content_hash,
                    "recorded_at": item.scanned_at,
                    "status": ArticleStatus.CHANGED.value,
                }
            )

            new_frontmatter = {
                "source": provider.name,
                "content_type": content_type.value,
            }
            cat_val = category or old_frontmatter.get("category")
            if cat_val is not None:
                new_frontmatter["category"] = str(cat_val)
            if platform:
                new_frontmatter["platform"] = platform
            new_frontmatter.update(
                {
                    "url": item.url,
                    "title": item.title or old_frontmatter.get("title"),
                    "published_date": item.published_date
                    or old_frontmatter.get("published_date"),
                    "author": item.author or old_frontmatter.get("author"),
                    "content_hash": item.content_hash,
                    "first_seen_at": first_seen_at,
                    "last_scanned_at": item.scanned_at,
                    "scan_count": scan_count,
                    "status": ArticleStatus.CHANGED.value,
                    "classification": classification.to_dict(),
                    "history": updated_history,
                }
            )

            file_text = serialize_markdown_with_frontmatter(
                new_frontmatter, item.content
            )
            self._write_file_atomically(existing_path, file_text)

            return ScanResult(
                item=item,
                status=ArticleStatus.CHANGED,
                file_path=existing_path,
                provider_name=provider.name,
                previous_hash=old_hash,
                classification=classification,
            )

        # 3. Neu
        target_path = self.get_target_path(item, provider)
        if target_path.exists():
            short_id = hashlib.sha256(item.url.encode()).hexdigest()[:6]
            target_path = target_path.parent / f"{target_path.stem}-{short_id}.md"

        new_frontmatter = {
            "source": provider.name,
            "content_type": content_type.value,
        }
        if category:
            new_frontmatter["category"] = category
        if platform:
            new_frontmatter["platform"] = platform
        new_frontmatter.update(
            {
                "url": item.url,
                "title": item.title,
                "published_date": item.published_date,
                "author": item.author,
                "content_hash": item.content_hash,
                "first_seen_at": item.scanned_at,
                "last_scanned_at": item.scanned_at,
                "scan_count": 1,
                "status": ArticleStatus.NEW.value,
                "classification": classification.to_dict(),
                "history": [
                    {
                        "content_hash": item.content_hash,
                        "recorded_at": item.scanned_at,
                        "status": ArticleStatus.NEW.value,
                    }
                ],
            }
        )

        file_text = serialize_markdown_with_frontmatter(new_frontmatter, item.content)
        self._write_file_atomically(target_path, file_text)
        self._url_to_path[item.url] = target_path

        return ScanResult(
            item=item,
            status=ArticleStatus.NEW,
            file_path=target_path,
            provider_name=provider.name,
            classification=classification,
        )

    def export_summary_json(self, export_path: Path | str) -> None:
        """Exportiert eine Zusammenfassung aller indizierten Dateien in eine JSON-Datei."""
        records = []
        for url, file_path in self._url_to_path.items():
            if file_path.exists():
                fm, _ = parse_markdown_with_frontmatter(
                    file_path.read_text(encoding="utf-8")
                )
                record = dict(fm)
                record["file_name"] = file_path.name
                record["relative_path"] = str(file_path.relative_to(self.output_dir))
                records.append(record)

        target = Path(export_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        with open(target, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "exported_at": datetime.now(timezone.utc).isoformat(),
                    "total_count": len(records),
                    "articles": records,
                },
                f,
                indent=2,
                ensure_ascii=False,
            )
        logger.info(
            "JSON-Zusammenfassung erfolgreich exportiert: %s (%d Artikel)",
            target,
            len(records),
        )


# ==============================================================================
# HTTP Client Fabrik
# ==============================================================================


@dataclass(slots=True)
class ScraperConfig:
    """Konfiguration für HTTP-Client, Parsing und Flat-File-Storage."""

    output_dir: Path = Path("data")
    timeout_seconds: float = 12.0
    user_agent: str = (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/128.0.0.0 Safari/537.36"
    )
    accept_language: str = "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7"
    output_format: str = "markdown"
    include_overview_page: bool = True
    rate_limit_delay: float = 0.5


def create_http_client(config: ScraperConfig) -> httpx.Client:
    headers = {
        "User-Agent": config.user_agent,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": config.accept_language,
        "Sec-Ch-Ua": '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"macOS"',
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
    }
    return httpx.Client(
        headers=headers,
        timeout=httpx.Timeout(config.timeout_seconds, connect=config.timeout_seconds),
        follow_redirects=True,
    )


# ==============================================================================
# Inhalts-Extraktion via Trafilatura & Cloudflare Anti-Jitter
# ==============================================================================


def decode_cloudflare_email(cf_hex: str) -> str:
    try:
        key = int(cf_hex[:2], 16)
        return "".join(
            chr(int(cf_hex[i : i + 2], 16) ^ key) for i in range(2, len(cf_hex), 2)
        )
    except Exception:
        return cf_hex


def sanitize_cloudflare_artifacts(html_content: str) -> str:
    def repl_email(match: re.Match[str]) -> str:
        return decode_cloudflare_email(match.group(1))

    html = re.sub(
        r'<a[^>]+data-cfemail="([0-9a-fA-F]+)"[^>]*>.*?</a>',
        repl_email,
        html_content,
        flags=re.IGNORECASE | re.DOTALL,
    )

    def repl_href(match: re.Match[str]) -> str:
        return f'href="mailto:{decode_cloudflare_email(match.group(1))}"'

    html = re.sub(
        r'href="/cdn-cgi/l/email-protection#([0-9a-fA-F]+)"',
        repl_href,
        html,
        flags=re.IGNORECASE,
    )
    return html


class ContentExtractor:
    """Extrahiert Kerninhalte und Metadaten unter Verwerfung von Boilerplate."""

    def __init__(self, output_format: str = "markdown") -> None:
        self.output_format = output_format
        self.trafilatura_config = use_config()
        self.trafilatura_config.set("DEFAULT", "EXTRACTION_TIMEOUT", "0")

    def extract(
        self, html_content: str, url: str
    ) -> tuple[str, str | None, str | None, str | None]:
        cleaned_html = sanitize_cloudflare_artifacts(html_content)

        metadata = trafilatura.extract_metadata(
            cleaned_html,
            default_url=url,
        )

        title = metadata.title if metadata else None
        published_date = metadata.date if metadata else None
        author = metadata.author if metadata else None

        extracted_content = trafilatura.extract(
            cleaned_html,
            url=url,
            record_id=url,
            output_format=self.output_format,
            include_tables=True,
            include_formatting=True,
            include_links=True,
            include_images=False,
            include_comments=False,
            favor_precision=True,
            config=self.trafilatura_config,
        )

        if not title:
            soup = BeautifulSoup(cleaned_html, "html.parser")
            h1 = soup.find("h1")
            if h1 and h1.get_text(strip=True):
                title = h1.get_text(strip=True)
            elif soup.title and soup.title.string:
                title = soup.title.string.strip()

        if not extracted_content:
            logger.info(
                "Trafilatura fand keinen Fließtext für %s, verwende Text-Fallback",
                url,
            )
            soup = BeautifulSoup(cleaned_html, "html.parser")
            for tag in soup(["script", "style", "nav", "footer", "header", "noscript"]):
                tag.decompose()
            extracted_content = soup.get_text(separator="\n", strip=True)

        return extracted_content, title, published_date, author


# ==============================================================================
# Scraper Orchestrierung (Multi-Provider)
# ==============================================================================


class P2PNewsScraper:
    """Orchestrierungs-Klasse für Multi-Provider Scraping."""

    def __init__(
        self,
        config: ScraperConfig | None = None,
        classifier: KeywordClassifier | None = None,
    ) -> None:
        self.config = config or ScraperConfig()
        self.classifier = classifier or DEFAULT_CLASSIFIER
        self.content_extractor = ContentExtractor(
            output_format=self.config.output_format
        )
        self.storage = MarkdownStorageManager(
            output_dir=self.config.output_dir,
            classifier=self.classifier,
        )

    def fetch_url(self, client: httpx.Client, url: str) -> str | None:
        parsed_path = urlparse(url).path.lower().rstrip("/")
        lower_url = url.lower()
        if any(
            parsed_path.endswith(ext)
            or lower_url.endswith(ext)
            or f"{ext}/" in lower_url
            for ext in IGNORED_BINARY_EXTENSIONS
        ):
            logger.info("Überspringe Binärdatei-URL: %s", url)
            return None

        try:
            response = client.get(url)
            # Falls 404 zurückkommt: versuche alternatives Slash-Format (ohne bzw. mit abschließendem Slash)
            if response.status_code == 404:
                alt_url = url.rstrip("/") if url.endswith("/") else f"{url}/"
                try:
                    alt_resp = client.get(alt_url)
                    if alt_resp.status_code == 200:
                        response = alt_resp
                        url = alt_url
                except Exception:
                    pass

            response.raise_for_status()

            # Content-Type Validierung: Keine Binärdateien wie application/pdf
            ctype = response.headers.get("content-type", "").lower()
            if ctype and not any(
                allowed in ctype
                for allowed in [
                    "text/html",
                    "application/xhtml",
                    "text/plain",
                    "application/xml",
                    "text/xml",
                ]
            ):
                logger.info(
                    "Überspringe Nicht-HTML Content-Type (%s) für %s", ctype, url
                )
                return None

            # Magic Bytes Prüfung (z. B. rohes PDF)
            if (
                response.content.startswith(b"%PDF")
                or b"%PDF-" in response.content[:1024]
            ):
                logger.info("Überspringe binäre PDF-Daten für %s", url)
                return None

            return response.text
        except httpx.HTTPStatusError as exc:
            domain = urlparse(url).netloc
            if exc.response.status_code == 403:
                logger.warning(
                    "[%s] Überspringe geschützte Seite (HTTP 403 / Bot-Schutz): %s",
                    domain,
                    url,
                )
            elif exc.response.status_code == 404:
                logger.warning(
                    "[%s] Überspringe nicht erreichbare Seite (HTTP 404): %s",
                    domain,
                    url,
                )
            else:
                logger.warning(
                    "[%s] HTTP-Fehler %s beim Aufruf von %s",
                    domain,
                    exc.response.status_code,
                    url,
                )
        except httpx.TimeoutException:
            logger.warning(
                "[%s] Timeout beim Aufruf von %s (> %.1fs)",
                urlparse(url).netloc,
                url,
                self.config.timeout_seconds,
            )
        except httpx.RequestError as exc:
            logger.warning(
                "[%s] Netzwerkfehler bei %s: %s", urlparse(url).netloc, url, exc
            )
        return None

    def process_page(
        self, url: str, html: str, provider: BaseProvider | None = None
    ) -> ArticleItem:
        custom_data = None
        if provider:
            try:
                custom_data = provider.extract_content(
                    html, url, self.content_extractor
                )
            except Exception as exc:
                logger.warning(
                    "[%s] Fehler bei benutzerdefinierter Extraktion von %s: %s",
                    provider.name,
                    url,
                    exc,
                )

        if custom_data:
            content, title, published_date, author = custom_data
        else:
            content, title, published_date, author = self.content_extractor.extract(
                html, url
            )

        content_hash = compute_sha256_hash(content, url=url)
        scanned_at = datetime.now(timezone.utc).isoformat()

        return ArticleItem(
            url=url,
            title=title,
            published_date=published_date,
            author=author,
            content=content,
            content_hash=content_hash,
            scanned_at=scanned_at,
        )

    def run_provider(
        self, client: httpx.Client, provider: BaseProvider, limit: int | None = None
    ) -> list[ScanResult]:
        """Führt den Scan für einen einzelnen Provider aus."""
        results: list[ScanResult] = []
        logger.info(
            "=== Starte Scan für Provider: %s (%s) ===",
            provider.name,
            provider.base_url,
        )

        # 1. Übersichtsseite laden
        overview_html = self.fetch_url(client, provider.base_url)
        if not overview_html:
            logger.error("Konnte Übersichtsseite für %s nicht laden.", provider.name)
            return results

        # 2. Übersichtsseite erfassen
        if self.config.include_overview_page:
            overview_item = self.process_page(
                provider.base_url, overview_html, provider=provider
            )
            res = self.storage.record_scan(overview_item, provider)
            results.append(res)
            self._log_item_result(res, is_overview=True)

        # 3. Links extrahieren
        try:
            article_urls = provider.extract_links(overview_html, client=client)
        except TypeError:
            article_urls = provider.extract_links(overview_html)
        logger.info(
            "[%s] %d relevante Links auf Übersichtsseite gefunden",
            provider.name,
            len(article_urls),
        )

        if limit is not None and limit > 0:
            article_urls = article_urls[:limit]
            logger.info(
                "[%s] Begrenze auf die ersten %d Artikel-URLs", provider.name, limit
            )

        # 4. Detailseiten abrufen
        for idx, article_url in enumerate(article_urls, start=1):
            if self.config.rate_limit_delay > 0 and idx > 1:
                time.sleep(self.config.rate_limit_delay)

            logger.debug(
                "[%s] [%d/%d] Lade: %s",
                provider.name,
                idx,
                len(article_urls),
                article_url,
            )
            article_html = self.fetch_url(client, article_url)
            if not article_html:
                continue

            item = self.process_page(article_url, article_html, provider=provider)
            scan_res = self.storage.record_scan(item, provider)
            results.append(scan_res)
            self._log_item_result(scan_res)

        return results

    def run(
        self, providers: list[BaseProvider], limit: int | None = None
    ) -> list[ScanResult]:
        """Führt den Scan für alle übergebenen Provider aus."""
        all_results: list[ScanResult] = []
        logger.info(
            "Starte Multi-Provider Scraper (Anzahl Provider: %d)", len(providers)
        )
        logger.info("Basis-Zielverzeichnis: %s", self.config.output_dir.resolve())

        with create_http_client(self.config) as client:
            for provider in providers:
                prov_results = self.run_provider(client, provider, limit=limit)
                all_results.extend(prov_results)

        self._print_summary(all_results)
        return all_results

    def _log_item_result(self, result: ScanResult, is_overview: bool = False) -> None:
        prefix = f"[{result.provider_name.upper()}]"
        if is_overview:
            type_str = "[ÜBERSICHT]"
        elif is_metric_url(result.item.url):
            type_str = "[STATISTIK]"
        else:
            type_str = "[ARTIKEL]"
        title_str = f"'{result.item.title}'" if result.item.title else "<Ohne Titel>"
        rel_path = result.file_path.relative_to(self.config.output_dir)

        match result.status:
            case ArticleStatus.NEW:
                logger.info(
                    "%s %s [NEU] %s -> %s | Hash: %s",
                    prefix,
                    type_str,
                    title_str,
                    rel_path,
                    result.item.content_hash[:12] + "...",
                )
            case ArticleStatus.UNCHANGED:
                logger.debug(
                    "%s %s [UNVERÄNDERT] %s -> %s | Hash: %s",
                    prefix,
                    type_str,
                    title_str,
                    rel_path,
                    result.item.content_hash[:12] + "...",
                )
            case ArticleStatus.CHANGED:
                logger.info(
                    "%s %s [GEÄNDERT] %s -> %s | Alter Hash: %s -> Neuer Hash: %s",
                    prefix,
                    type_str,
                    title_str,
                    rel_path,
                    result.previous_hash[:12] + "..."
                    if result.previous_hash
                    else "None",
                    result.item.content_hash[:12] + "...",
                )

    def _print_summary(self, results: list[ScanResult]) -> None:
        new_items = [r for r in results if r.status == ArticleStatus.NEW]
        unchanged_items = [r for r in results if r.status == ArticleStatus.UNCHANGED]
        changed_items = [r for r in results if r.status == ArticleStatus.CHANGED]

        logger.info("=" * 70)
        logger.info("GESAMT-SCAN-ABSCHLUSS-BERICHT")
        logger.info("  Gesamt gescannt:       %d", len(results))
        logger.info("  Neue Seiten:           %d", len(new_items))
        logger.info("  Unveränderte Seiten:   %d", len(unchanged_items))
        logger.info("  Geänderte Seiten:      %d", len(changed_items))
        logger.info("  Dateiverzeichnis:      %s", self.config.output_dir)
        logger.info("=" * 70)

        # Zusammenfassung nach Provider
        provider_counts: dict[str, int] = {}
        for r in results:
            provider_counts[r.provider_name] = (
                provider_counts.get(r.provider_name, 0) + 1
            )
        for prov, count in provider_counts.items():
            logger.info("  - Provider %s: %d Seiten", prov, count)


# ==============================================================================
# CLI Entrypoint
# ==============================================================================


def parse_cli_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="P2P News & Platform Scraper (Deklarativ via providers.yaml)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--config",
        "-c",
        default="providers.yaml",
        help="Pfad zur deklarativen Provider-Konfigurationsdatei (YAML)",
    )
    parser.add_argument(
        "--provider",
        default="all",
        help="Auszuführender Provider (z. B. nectaro, mintos, peerberry) oder 'all', 'aggregators', 'platforms'",
    )
    parser.add_argument(
        "--url",
        default=None,
        help="Spezifische Start-URL (erkennt Provider automatisch)",
    )
    parser.add_argument(
        "--output-dir",
        "-o",
        default="data",
        help="Basis-Zielverzeichnis für die generierten Markdown-Dateien",
    )
    parser.add_argument(
        "--json-export",
        default=None,
        help="Optionaler Pfad zum Export einer Gesamt-Zusammenfassung als JSON",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=12.0,
        help="HTTP-Timeout in Sekunden",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Optionale Begrenzung der Anzahl an Detailseiten je Provider",
    )
    parser.add_argument(
        "--extract-items",
        action="store_true",
        help="Extrahiert nach dem Scraping automatisch diskrete NewsItems in data/items/ (Stufe 0)",
    )
    parser.add_argument(
        "--audit",
        action="store_true",
        help="Führt das mathematische P2P Audit Scoring für alle konfigurierten Plattformen durch",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Ausführliche Debug-Logs aktivieren",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_cli_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    # Standalone-Audit ausführen, wenn --audit ohne explizite Provider-Überschreibung aufgerufen wird
    if args.audit and "--provider" not in sys.argv and "--url" not in sys.argv:
        from run_audit_scoring import run_full_audit

        logger.info("Starte P2P Platform Audit Scoring...")
        scored_count, rank_file = run_full_audit()
        logger.info(
            "Audit abgeschlossen: %d Plattformen bewertet -> %s",
            scored_count,
            rank_file,
        )
        return 0

    providers_map = load_providers_from_yaml(args.config)
    classifier = load_classifier_from_yaml(args.config)

    config = ScraperConfig(
        output_dir=Path(args.output_dir),
        timeout_seconds=args.timeout,
    )

    scraper = P2PNewsScraper(config=config, classifier=classifier)

    # Provider-Auswahl bestimmen
    if args.url:
        provider = detect_provider_for_url(args.url, providers_map=providers_map)
        provider.base_url = args.url
        active_providers = [provider]
    elif args.provider == "all":
        active_providers = list(providers_map.values())
    elif args.provider == "aggregators":
        active_providers = [p for p in providers_map.values() if not p.is_platform]
    elif args.provider == "platforms":
        active_providers = [p for p in providers_map.values() if p.is_platform]
    elif args.provider in providers_map:
        active_providers = [providers_map[args.provider]]
    else:
        logger.error(
            "Unbekannter Provider: '%s'. Verfügbare Provider in %s: %s",
            args.provider,
            args.config,
            ", ".join(providers_map.keys()),
        )
        return 1

    results = scraper.run(providers=active_providers, limit=args.limit)

    if args.json_export:
        scraper.storage.export_summary_json(args.json_export)

    if args.extract_items:
        from item_extractor import process_all_scraped_news

        logger.info("Starte nachgelagerte Item-Extraktion (Stufe 0)...")
        files_count, items_count = process_all_scraped_news(data_dir=args.output_dir)
        logger.info(
            "Item-Extraktion abgeschlossen: %d Dateien verarbeitet, %d Items im Store.",
            files_count,
            items_count,
        )

    if args.audit:
        from run_audit_scoring import run_full_audit

        logger.info("Starte nachgelagertes P2P Platform Audit Scoring...")
        scored_count, rank_file = run_full_audit()
        logger.info(
            "Audit abgeschlossen: %d Plattformen bewertet -> %s",
            scored_count,
            rank_file,
        )

    return 0 if results else 1


if __name__ == "__main__":
    sys.exit(main())
