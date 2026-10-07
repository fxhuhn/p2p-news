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
