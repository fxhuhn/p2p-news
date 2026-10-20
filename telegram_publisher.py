"""
Telegram Publisher für P2P-News und Audit-Rankings.

Veröffentlicht automatisierte Benachrichtigungen für:
1. Wöchentliche Newsletter (als übersichtliche Serie getrennt nach Kategorien)
2. Monatliche Plattform-Audit-Rankings (Top-5, Absteiger, Neuanlage-Stopps & Link)

Design-Prinzipien für mobile Endgeräte:
- Verzicht auf Piktogramme und horizontale Trennlinien (maximale Platzausnutzung).
- Hohe Informationsdichte mit klarer typografischer Hierarchie (Fettung für Plattformen).
- Ausfallsichere HTML-Formatierung (parse_mode="HTML").

Konfiguration via Umgebungsvariablen (.env):
- TELEGRAM_TOKEN / TELEGRAM_BOT_TOKEN: Bot-Token von BotFather
- TELEGRAM_CHAT_ID: Ziel-Chat-ID (Kanal oder Benutzer)
- TELEGRAM_NOTIFY_ENABLED: 'true' (Standard wenn Token gesetzt) oder 'false'
- GITHUB_REPOSITORY: Ziel-Repository (Standard: 'fxhuhn/p2p-news')
- GIT_BRANCH: Ziel-Branch (Standard: 'main')
"""

from __future__ import annotations

import argparse
import html
import json
import logging
import os
import re
import time
import urllib.error
import urllib.request
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("telegram_publisher")


def get_telegram_config() -> dict[str, str | bool]:
    """Liest die Telegram-Konfiguration aus den Umgebungsvariablen."""
    token = (
        os.getenv("TELEGRAM_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN") or ""
    ).strip()
    chat_id = (os.getenv("TELEGRAM_CHAT_ID") or "").strip()
    enabled_val = os.getenv("TELEGRAM_NOTIFY_ENABLED")

    if enabled_val is None:
        enabled = bool(token and chat_id)
    else:
        enabled = enabled_val.strip().lower() not in ("false", "0", "no", "off")

    repo = (os.getenv("GITHUB_REPOSITORY") or "fxhuhn/p2p-news").strip()
    branch = (os.getenv("GIT_BRANCH") or "main").strip()

    return {
        "token": token,
        "chat_id": chat_id,
        "enabled": enabled,
        "repo": repo,
        "branch": branch,
    }


def send_telegram_message(
    text: str,
    token: str | None = None,
    chat_id: str | None = None,
    parse_mode: str = "HTML",
    disable_web_page_preview: bool = True,
    timeout: float = 12.0,
) -> bool:
    """
    Sendet eine einzelne Textnachricht über die Telegram Bot API.

    Args:
        text: Der Nachrichtentext (HTML-formatiert).
        token: Optionaler Bot-Token (sonst aus Config).
        chat_id: Optionale Chat-ID (sonst aus Config).
        parse_mode: Parse-Modus ("HTML").
        disable_web_page_preview: Deaktiviert Link-Vorschau für kompaktere Darstellung.
        timeout: HTTP-Timeout in Sekunden.

    Returns:
        True bei erfolgreicher Übermittlung, sonst False.
    """
    config = get_telegram_config()
    bot_token = token or str(config["token"])
    target_chat = chat_id or str(config["chat_id"])
    is_enabled = bool(config["enabled"]) if token is None else True

    if not is_enabled:
        logger.info(
            "[TELEGRAM] Benachrichtigungen deaktiviert (TELEGRAM_NOTIFY_ENABLED=false)."
        )
        return True

    if not bot_token or not target_chat:
        logger.warning(
            "[TELEGRAM] Token oder Chat-ID nicht konfiguriert. Versand übersprungen."
        )
        return False

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": target_chat,
        "text": text,
        "parse_mode": parse_mode,
        "disable_web_page_preview": disable_web_page_preview,
    }

    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            resp_body = json.loads(resp.read().decode("utf-8"))
            if resp_body.get("ok"):
                msg_id = resp_body.get("result", {}).get("message_id")
                logger.info(
                    "[TELEGRAM] Nachricht erfolgreich gesendet (Message ID: %s).",
                    msg_id,
                )
                return True
            logger.error("[TELEGRAM] API-Antwort nicht ok: %s", resp_body)
            return False
    except urllib.error.HTTPError as err:
        err_body = err.read().decode("utf-8", errors="replace")
        logger.error("[TELEGRAM] HTTP-Fehler %d: %s", err.code, err_body)
        return False
    except Exception as exc:
        logger.error("[TELEGRAM] Unerwarteter Fehler beim Senden: %s", exc)
        return False


def format_ranking_message(
    ranking_path: Path | str,
    repo: str | None = None,
    branch: str | None = None,
) -> str:
    """
    Extrahiert die Kerndaten aus einer Monats-Ranking-Datei und formatiert sie
    für mobile Telegram-Benachrichtigungen (ohne Piktogramme/Linien).
    """
    path = Path(ranking_path)
    if not path.exists():
        raise FileNotFoundError(f"Ranking-Datei nicht gefunden: {path}")

    content = path.read_text(encoding="utf-8")
    lines = content.splitlines()

    config = get_telegram_config()
    repository = repo or str(config["repo"])
    git_branch = branch or str(config["branch"])

    # Metadaten aus Frontmatter
    year_month = ""
    for line in lines:
        if line.startswith("year_month:"):
            year_month = line.split(":", 1)[1].strip().strip("'\"")
            break

    title = f"P2P Platform Audit Ranking – {year_month or path.stem}"

    # 1. Top 5 Plattformen & Veränderungen parsen
    top_platforms: list[tuple[int, str, int, str, str]] = []
    changes: list[tuple[str, int, str, str]] = []

    # Regex für Zeilen der Rangliste
    row_pattern = re.compile(
        r"^\|\s*\*\*?(\d+)\*\*?\s*\|\s*\[?([A-Za-z0-9_ -]+)\]?(?:\([^)]+\))?\s*\|\s*\*\*?(\d+)\*\*?\s*\|\s*`?([±+\-0-9]+)`?\s*\|\s*`?([A-Z_ ]+)`?\s*\|"
    )

    in_table = False
    for line in lines:
        if line.startswith("## 1. Master-Rangliste"):
            in_table = True
            continue
        if in_table and line.startswith("## "):
            in_table = False
            break
        if in_table:
            match = row_pattern.match(line.strip())
            if match:
                rank = int(match.group(1))
                plat_name = match.group(2).strip()
                score = int(match.group(3))
                delta = match.group(4).strip()
                risk_class = match.group(5).strip().title()

                if rank <= 5:
                    top_platforms.append((rank, plat_name, score, delta, risk_class))

                # Delta prüfen (z. B. -16, -6, +4)
                if delta not in ("±0", "0", "-", "+0"):
                    try:
                        int(delta.replace("+", ""))
                        changes.append((plat_name, score, delta, risk_class))
                    except ValueError:
                        pass

    # Sortiere stärkste negative Veränderungen
    changes.sort(key=lambda x: int(x[2].replace("+", "")))

    # 2. Neuanlage-Stopps parsen
    stopp_platforms: list[str] = []
    in_warnings = False
    for line in lines:
        if "Akute Watchlist- & Risiko-Warnungen" in line:
            in_warnings = True
            continue
        if in_warnings and line.startswith("## "):
            in_warnings = False
            break
        if in_warnings and line.strip().startswith("> •"):
            plat_match = re.search(r">\s*•\s*\*\*([A-Za-z0-9_ -]+)\*\*", line)
            if plat_match:
                stopp_platforms.append(plat_match.group(1).strip())

    github_url = (
        f"https://github.com/{repository}/blob/{git_branch}/data/rankings/{path.name}"
    )

    # Aufbau der mobilen Nachricht
    blocks = [
        f"<b>{html.escape(title)}</b>",
        "Das neue Monats-Ranking für 31 Plattformen ist auf GitHub verfügbar.",
    ]

    if top_platforms:
        top_str = "<b>Top 5 Plattformen (Netto-Score / 100):</b>\n" + "\n".join(
            f"{r}. {html.escape(p)} – {s} Pkt ({d}) [{rc}]"
            for r, p, s, d, rc in top_platforms
        )
        blocks.append(top_str)

    if changes:
        notable = changes[:3]
        change_str = "<b>Größte Veränderungen:</b>\n" + "\n".join(
            f"{html.escape(p)}: {s} Pkt ({d}) [{rc}]" for p, s, d, rc in notable
        )
        blocks.append(change_str)

    if stopp_platforms:
        stopp_str = "<b>Neuanlage-Stopp (0 % Depot-Limit):</b>\n" + html.escape(
            ", ".join(stopp_platforms)
        )
        blocks.append(stopp_str)

    blocks.append(
        f'<b>Vollständiger Report:</b>\n<a href="{github_url}">Ranking auf GitHub öffnen</a>'
    )

    return "\n\n".join(blocks)


def format_newsletter_messages(
    newsletter_path: Path | str,
    repo: str | None = None,
    branch: str | None = None,
) -> list[str]:
    """
    Teilt einen wöchentlichen Newsletter in eine Serie von kompakten,
    kategoriebasierten Einzelnachrichten für Telegram auf.
    """
    path = Path(newsletter_path)
    if not path.exists():
        raise FileNotFoundError(f"Newsletter-Datei nicht gefunden: {path}")

    content = path.read_text(encoding="utf-8")
    lines = content.splitlines()

    config = get_telegram_config()
    repository = repo or str(config["repo"])
    git_branch = branch or str(config["branch"])

    # 1. Metadaten / Titel & Briefing
    kw_title = "P2P Kredite Wochenrückblick"
    briefing = ""

    for line in lines:
        if line.startswith("# P2P Kredite Wochenrückblick"):
            kw_title = line.replace("#", "").strip()
        elif line.startswith("> **Kompakt-Briefing:**"):
            briefing = line.replace("> **Kompakt-Briefing:**", "").strip()

    messages: list[str] = []

    # Nachricht 1: Intro / Kompakt-Briefing
    intro_msg = f"<b>{html.escape(kw_title)}</b>\n\n<b>Kompakt-Briefing:</b>\n{html.escape(briefing)}"
    messages.append(intro_msg)

    # 2. Abschnitte parsen
    current_headline = ""
    current_paragraphs: list[str] = []
    sections: list[tuple[str, list[str]]] = []

    in_sources = False
    in_frontmatter = False
    frontmatter_closed = False

    for line in lines:
        stripped = line.strip()

        if not frontmatter_closed:
            if stripped == "---":
                if in_frontmatter:
                    frontmatter_closed = True
                    in_frontmatter = False
                else:
                    in_frontmatter = True
                continue
            if in_frontmatter:
                continue

        if stripped == "---":
            continue

        if stripped.startswith("## "):
            if current_headline and current_paragraphs:
                sections.append((current_headline, current_paragraphs))
            current_headline = stripped.replace("## ", "").strip()
            current_paragraphs = []
            in_sources = False
            continue

        if stripped.startswith("### Revisions- & Prüfnachweis"):
            break

        if stripped.startswith("**Geprüfte Quellen:**"):
            in_sources = True
            continue

        if in_sources:
            continue

        if stripped.startswith("*Kategorie:") or stripped.startswith("> ⚠️"):
            continue

        if stripped.startswith("> -"):
            continue

        if stripped:
            current_paragraphs.append(stripped)

    if current_headline and current_paragraphs:
        sections.append((current_headline, current_paragraphs))

    # Map categories to clean concise headings
    headline_map = {
        "Volumen, Meilensteine & Portfoliorückflüsse": "Volumen & Statistiken",
        "Regulierung, Lizenzen & Personalentscheidungen": "Regulierung & Führung",
        "Kreditanbahner & Marktplatz-Partner": "Kreditanbahner & Marktplätze",
        "Risiken, Liquiditätsengpässe & Insolvenzen": "Risiken, Verzögerungen & Insolvenzen",
        "Plattform-Features & Produktneuheiten": "Features & Gesamtreport",
    }

    github_url = f"https://github.com/{repository}/blob/{git_branch}/data/newsletters/{path.name}"

    for idx, (headline, paragraphs) in enumerate(sections):
        clean_headline = headline_map.get(headline, headline)
        formatted_paras: list[str] = []

        for p in paragraphs:
            # Markdown Fettung **Plattform** in HTML <b>Plattform</b> wandeln
            # Falls am Zeilenanfang **Plattform** steht, mache **Plattform:** draus
            p_clean = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", p)
            formatted_paras.append(p_clean)

        msg_body = f"<b>{html.escape(clean_headline)}</b>\n\n" + "\n\n".join(
            formatted_paras
        )

        # Wenn es der letzte Abschnitt ist, Link anhängen
        if idx == len(sections) - 1:
            msg_body += f'\n\n<b>Vollständiger Report & Quellen:</b>\n<a href="{github_url}">Newsletter auf GitHub öffnen</a>'

        messages.append(msg_body)

    return messages


def send_ranking_notification(
    ranking_path: Path | str,
    token: str | None = None,
    chat_id: str | None = None,
) -> bool:
    """Formatiert und sendet die Ranking-Benachrichtigung an Telegram."""
    try:
        msg = format_ranking_message(ranking_path)
        return send_telegram_message(text=msg, token=token, chat_id=chat_id)
    except Exception as exc:
        logger.exception(
            "[TELEGRAM] Fehler beim Senden der Ranking-Benachrichtigung: %s", exc
        )
        return False


def send_newsletter_notification(
    newsletter_path: Path | str,
    token: str | None = None,
    chat_id: str | None = None,
    sleep_interval: float = 0.4,
) -> bool:
    """Formatiert und sendet die Newsletter-Nachrichtenserie an Telegram."""
    try:
        messages = format_newsletter_messages(newsletter_path)
        success = True
        for idx, msg in enumerate(messages, 1):
            sent = send_telegram_message(
                text=msg,
                token=token,
                chat_id=chat_id,
                disable_web_page_preview=True,
            )
            if not sent:
                success = False
            if idx < len(messages):
                time.sleep(sleep_interval)
        return success
    except Exception as exc:
        logger.exception("[TELEGRAM] Fehler beim Senden der Newsletter-Serie: %s", exc)
        return False


def main() -> int:
    """CLI-Einstiegspunkt für manuellen Versand."""
    parser = argparse.ArgumentParser(description="Telegram Publisher für P2P-News")
    parser.add_argument("--ranking", type=str, help="Pfad zur Ranking-Markdown-Datei")
    parser.add_argument(
        "--newsletter", type=str, help="Pfad zur Newsletter-Markdown-Datei"
    )
    parser.add_argument(
        "--test", action="store_true", help="Sendet eine einfache Testnachricht"
    )

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
    )

    if args.test:
        test_msg = "<b>P2P News</b>: Verbindungstest erfolgreich."
        ok = send_telegram_message(test_msg)
        return 0 if ok else 1

    if args.ranking:
        ok = send_ranking_notification(args.ranking)
        return 0 if ok else 1

    if args.newsletter:
        ok = send_newsletter_notification(args.newsletter)
        return 0 if ok else 1

    parser.print_help()
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
