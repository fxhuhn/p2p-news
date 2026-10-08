"""
Text-Normalisierung und Markdown-AST-Bereinigung für revisionssichere P2P-News.

Funktionen:
- normalize_plain_text: Befreit Markdown von Formatierungen und Syntax für exakte Zitatverifikation.
- normalize_whitespace: Bereinigt mehrfache Whitespaces und Zeilenumbrüche.
- parse_german_date: Parst deutsche Datumsformate ("02. Oktober 2026") in ISO-Format ("2026-10-02").
"""

from __future__ import annotations

import re
import unicodedata
from urllib.parse import urlparse

GERMAN_MONTHS: dict[str, str] = {
    "januar": "01",
    "februar": "02",
    "märz": "03",
    "maerz": "03",
    "april": "04",
    "mai": "05",
    "juni": "06",
    "juli": "07",
    "august": "08",
    "september": "09",
    "oktober": "10",
    "november": "11",
    "dezember": "12",
}


def normalize_plain_text(text: str) -> str:
    """
    Normalisiert Markdown-Text in sauberen, kontinuierlichen Fließtext.
    Entfernt Markdown-Links, Bilder, Formatierungszeichen, typografische Sonderzeichen
    und normalisiert Whitespace sowie Unicode (NFC).

    Wichtig für Verifier 1: Zitate aus LLM-Antworten können hiermit fehlertolerant,
    aber semantisch exakt (inkl. Negationen) gegen den Snapshot geprüft werden.
    """
    if not text:
        return ""

    # 1. Unicode NFC Normalisierung
    result = unicodedata.normalize("NFC", text)

    # 2. Markdown-Bilder entfernen: ![alt](url) -> ""
    result = re.sub(r"!\[.*?\]\(.*?\)", "", result)

    # 3. Markdown-Links bereinigen: [Anchor Text](url) -> "Anchor Text"
    result = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", result)

    # 4. Markdown-Header-Marker entfernen: #, ##, ### etc. am Zeilenanfang
    result = re.sub(r"^#{1,6}\s+", "", result, flags=re.MULTILINE)

    # 5. Markdown-Formatierungszeichen entfernen (*kursiv*, **fett**, __fett__, ~~durchgestrichen~~)
    result = re.sub(r"\*\*([^*]+)\*\*", r"\1", result)
    result = re.sub(r"__([^_]+)__", r"\1", result)
    result = re.sub(r"\*([^*]+)\*", r"\1", result)
    result = re.sub(r"_([^_]+)_", r"\1", result)
    result = re.sub(r"`([^`]+)`", r"\1", result)

    # 5b. Markdown Escapes entfernen (\ vor Zeichen wie \, *, _, etc.)
    result = re.sub(r"\\([\\`*_{}\[\]()#+\-.!|~])", r"\1", result)
    result = result.replace("\\", "")

    # 6. Blockquotes und horizontale Trennlinien entfernen
    result = re.sub(r"^>\s*", "", result, flags=re.MULTILINE)
    result = re.sub(r"^[-*_]{3,}\s*$", "", result, flags=re.MULTILINE)

    # 7. Typografische Anführungszeichen & Apostrophe vereinheitlichen
    quote_map = {
        "„": '"',
        "“": '"',
        "”": '"',
        "«": '"',
        "»": '"',
        "’": "'",
        "‘": "'",
        "–": "-",  # En-dash zu Bindestrich
        "—": "-",  # Em-dash zu Bindestrich
        "\u00a0": " ",  # Non-breaking space
    }
    for old_char, new_char in quote_map.items():
        result = result.replace(old_char, new_char)

    # 8. Whitespace normalisieren (mehrfache Leerzeichen, Zeilenumbrüche glätten)
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in result.splitlines()]
    # Leere Zeilen zusammenfassen
    cleaned_lines: list[str] = []
    prev_empty = False
    for line in lines:
        if not line:
            if not prev_empty:
                cleaned_lines.append("")
                prev_empty = True
        else:
            cleaned_lines.append(line)
            prev_empty = False

    return "\n".join(cleaned_lines).strip()


def parse_german_date(date_str: str | None) -> str | None:
    """
    Parst deutsche Datumsangaben wie '02. Oktober 2026' oder '28. September 2026'
    oder '2026-09-28' in standardisiertes ISO 8601 Datumsformat 'YYYY-MM-DD'.
    """
    if not date_str:
        return None

    cleaned = date_str.strip().strip("*").strip()

    # Fall 1: Bereits ISO Format (YYYY-MM-DD)
    if re.match(r"^\d{4}-\d{2}-\d{2}$", cleaned):
        return cleaned

    # Fall 2: '02. Oktober 2026' oder '2. Okt 2026'
    match = re.search(r"(\d{1,2})\.\s*([A-Za-zäöüÄÖÜ]+)\s*(\d{4})", cleaned)
    if match:
        day_str, month_name, year_str = match.groups()
        month_lower = month_name.lower()
        month_num = None
        for name, num in GERMAN_MONTHS.items():
            if month_lower.startswith(name[:3]):
                month_num = num
                break

        if month_num:
            day_int = int(day_str)
            return f"{year_str}-{month_num}-{day_int:02d}"

    # Fall 3: '02.10.2026' oder '02.10.26'
    match_dots = re.search(r"(\d{1,2})\.(\d{1,2})\.(\d{2,4})", cleaned)
    if match_dots:
        d, m, y = match_dots.groups()
        if len(y) == 2:
            y = f"20{y}"
        return f"{y}-{int(m):02d}-{int(d):02d}"

    return None


def mask_ephemeral_timestamps(text: str) -> str:
    """
    Maskiert flüchtige Zeitstempel, relative Datumsangaben und Kommentarzähler
    in deutschen und englischen Texten zur Vermeidung von Hash-Jitter.
    """
    if not text:
        return ""

    # 1. Englische Zeitstempel wie z. B. 'Last update at 03-10-2026 12:12 UTC'
    result = re.sub(
        r"Last update(?:d)?(?:\s+at|\s+on|\s*:)?\s+\d{1,4}[-./]\d{1,2}[-./]\d{1,4}(?:\s+\d{1,2}:\d{2}(?::\d{2})?(?:\s*[A-Z]{2,4})?)?",
        "Last update at [TIMESTAMP]",
        text,
        flags=re.IGNORECASE,
    )

    # 2. Deutsche Datumsangaben wie 'Zuletzt aktualisiert am 08. Oktober 2026', 'Aktualisiert am: 08.10.2026 um 11:30 Uhr'
    result = re.sub(
        r"(?:Zuletzt\s+)?[Aa]ktualisiert(?:\s+am(?:\s*:)?|:)?\s+\d{1,2}\.\s*(?:Januar|Februar|März|Maerz|April|Mai|Juni|Juli|August|September|Oktober|November|Dezember|[A-Za-zäöüÄÖÜ]{3,9})\s+\d{4}(?:\s*,?\s*(?:um\s+)?\d{1,2}:\d{2}(?::\d{2})?(?:\s*Uhr)?)?",
        "[TIMESTAMP]",
        result,
        flags=re.IGNORECASE,
    )
    result = re.sub(
        r"(?:Zuletzt\s+)?[Aa]ktualisiert(?:\s+am(?:\s*:)?|:)?\s+\d{1,2}\.\d{1,2}\.\d{2,4}(?:\s*,?\s*(?:um\s+)?\d{1,2}:\d{2}(?::\d{2})?(?:\s*Uhr)?)?",
        "[TIMESTAMP]",
        result,
        flags=re.IGNORECASE,
    )

    # 3. Stand-Angaben: 'Stand: 01.10.2026', 'Stand: Oktober 2026'
    result = re.sub(
        r"\bStand:\s*(?:\d{1,2}\.\d{1,2}\.\d{2,4}|(?:Januar|Februar|März|Maerz|April|Mai|Juni|Juli|August|September|Oktober|November|Dezember)\s+\d{4})",
        "Stand: [TIMESTAMP]",
        result,
        flags=re.IGNORECASE,
    )

    # 4. Relative Zeitstempel ('vor 2 Stunden', 'vor 3 Tagen', '5 hours ago')
    result = re.sub(
        r"\bvor\s+\d+\s+(?:Sekunden?|Minuten?|Stunden?|Tagen?|Wochen?|Monaten?)\b",
        "[TIMESTAMP]",
        result,
        flags=re.IGNORECASE,
    )
    result = re.sub(
        r"\b\d+\s+(?:seconds?|minutes?|hours?|days?|weeks?|months?)\s+ago\b",
        "[TIMESTAMP]",
        result,
        flags=re.IGNORECASE,
    )

    # 5. Dynamische Kommentarzähler in Meta-Zeilen ('14 Kommentare', '1 Comment')
    result = re.sub(
        r"\b\d+\s+(?:Kommentare?|Comments?)\b",
        "[COMMENTS]",
        result,
        flags=re.IGNORECASE,
    )

    return result


def strip_blog_boilerplate(text: str) -> str:
    """
    Entfernt repetitive, globale Blog-Footer-Listen (z. B. 25-Plattform-Cashback-Listen
    auf passives-einkommen-mit-p2p.de), die bei Template-Änderungen ansonsten alle
    Erfahrungsberichte künstlich als 'geändert' markieren würden.
    """
    if not text:
        return ""
    return re.sub(
        r"##\s+Weitere\s+Infos\s+zu\s+den\s+aktiven\s+P2P\s+Plattformen.*?(?=\n#{1,5}\s+|\Z)",
        "",
        text,
        flags=re.DOTALL | re.IGNORECASE,
    )


def normalize_metric_content(text: str) -> str:
    """
    Normalisiert Live-Statistikseiten und Kreditanbahner-Dashboards:
    1. Maskiert flüchtige Währungs- und Zählwerte (z. B. '67.918.411,25 €' -> '[METRIC_NUM]')
    2. Sortiert Zeilen in Abschnitten deterministisch alphabetisch, um Zeilentausch-Jitter
       (dynamische Sortierung nach Live-Kreditvolumen) zu verhindern.
    """
    if not text:
        return ""

    # 1. Währungs- und Zahlenwerte maskieren
    text_masked = re.sub(
        r"(?:€\s*|\$\s*|£\s*)?\b\d{1,3}(?:[.,\s]\d{3})*(?:[.,]\d+)?(?:\s*(?:€|\$|£|EUR|USD|GBP|%))?",
        "[METRIC_NUM]",
        text,
        flags=re.IGNORECASE,
    )

    # 2. Abschnitte mit Zeilenlisten deterministisch sortieren
    sections = re.split(r"(\n#{1,4}\s+[^\n]+)", text_masked)
    processed_parts: list[str] = []
    for part in sections:
        if part.startswith("\n#"):
            processed_parts.append(part)
        else:
            lines = [line.strip() for line in part.splitlines() if line.strip()]
            if len(lines) > 2:
                processed_parts.append("\n" + "\n".join(sorted(lines)))
            else:
                processed_parts.append(part)

    return "".join(processed_parts)


def is_metric_url(url: str | None) -> bool:
    """Prüft, ob eine URL eine Live-Metrik- oder Statistikseite darstellt."""
    if not url:
        return False
    path = urlparse(url).path.lower().rstrip("/")
    return any(
        kw in path
        for kw in (
            "statistics",
            "peerberry-statistics",
            "loan-originators",
            "kreditanbahner",
        )
    )


def normalize_text(raw_text: str, is_metric: bool = False) -> str:
    """
    Führt eine deterministische Text-Normalisierung durch:
    1. Unicode-Normalisierung (NFC)
    2. Maskierung flüchtiger Zeitstempel, relativer Daten und Kommentarzähler
    3. Bereinigung repetitiver Template-Footer
    4. Optionale Normalisierung flüchtiger Live-Metriken (bei Statistikseiten)
    5. Whitespace-Bereinigung (Entfernung redundanter Leerzeichen, Tabs und Zeilenumbrüche)
    """
    if not raw_text:
        return ""
    normalized_unicode = unicodedata.normalize("NFC", raw_text)
    masked = mask_ephemeral_timestamps(normalized_unicode)
    masked = strip_blog_boilerplate(masked)
    if is_metric:
        masked = normalize_metric_content(masked)
    return " ".join(masked.split())
