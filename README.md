# P2P News Scraper & Flat-File Tracker (Multi-Provider)

Ein modulares, produktionsreifes Python 3.11+ Tool zum Scannen von P2P-Lending-News und Plattform-Erfahrungsberichten. Kerninhalte werden via Trafilatura extrahiert, normalisiert und deterministisch über SHA-256 Hashes getrackt.

**Alle Daten werden als Markdown-Dateien mit YAML Frontmatter gespeichert.** Eine SQLite-Datenbank wird nicht benötigt.

---

## Unterstützte Anbieter (36 Provider)

### 1. News- und Erfahrungs-Aggregatoren (5 Blogs)
| Provider-Key | Name / Blog | Start-URL |
|---|---|---|
| `p2p-empire` | P2P Empire | `https://p2pempire.com/de/nachrichten` |
| `p2p-game` | P2P Game | `https://p2p-game.com/p2p-kredite-plattform-news` |
| `rethink-p2p` | re:think P2P | `https://rethink-p2p.de/news/` |
| `passives-einkommen` | Passives Einkommen mit P2P (Lars Wrobbel) | `https://passives-einkommen-mit-p2p.de/p2p-kredite-news/` |
| `p2p-anlage` | P2P-Anlage.de | `https://p2p-anlage.de` |

### 2. Offizielle P2P-Plattformen (31 Plattformen)
| Provider-Key | Plattform | Start-URL | Gescannte Bereiche |
|---|---|---|---|
| `nectaro` | Nectaro | `https://nectaro.eu` | Hauptseite, Statistik, Dokumente, Anbahner, Blog |
| `mintos` | Mintos | `https://www.mintos.com` | Hauptseite, Statistik, Blog |
| `peerberry` | PeerBerry | `https://peerberry.com` | Hauptseite, Statistik, News |
| `esketit` | Esketit | `https://esketit.com` | Hauptseite, Statistik, Blog |
| `debitum` | Debitum | `https://debitum.investments` | Hauptseite, Statistik, Blog |
| `indemo` | Indemo | `https://www.indemo.eu` | Hauptseite, Insights, Finanzberichte, Blog |
| `estateguru` | EstateGuru | `https://estateguru.co` | Hauptseite, Statistik, Blog |
| `swaper` | Swaper | `https://swaper.com` | Hauptseite, Blog |
| `loanch` | Loanch | `https://loanch.com` | Hauptseite, Blog |
| `revest` | Revest | `https://revest.group` | Hauptseite, Blog |
| `robocash` | Robocash | `https://robo.cash` | Hauptseite, News |
| `lande` | Lande | `https://lande.finance` | Hauptseite, Blog |
| `afranga` | Afranga | `https://afranga.com` | Hauptseite, Blog |
| `inrento` | InRento | `https://inrento.com` | Hauptseite, Blog |
| `fintown` | Fintown | `https://fintown.eu` | Hauptseite, Blog |
| `stockestate` | StockEstate | `https://stock.estate` | Hauptseite, Blog |
| `asterra` | Asterra | `https://asterra.estate` | Hauptseite, Blog |
| `capitalia` | Capitalia | `https://www.capitalia.com` | Hauptseite, Blog |
| `ventus` | Ventus | `https://ventus.energy` | Hauptseite, Blog |
| `bondster` | Bondster | `https://bondster.com` | Hauptseite, Blog |
| `fagura` | Fagura | `https://fagura.com` | Hauptseite, Blog |
| `bondora` | Bondora | `https://www.bondora.com` | Hauptseite, Blog |
| `viainvest` | VIAINVEST | `https://viainvest.com` | Hauptseite, Blog |
| `income` | Income Marketplace | `https://getincome.com` | Hauptseite, Blog |
| `hive5` | Hive5 | `https://hive5.eu` | Hauptseite, Blog |
| `lendermarket` | Lendermarket | `https://lendermarket.com` | Hauptseite, Kreditanbahner, Blog |
| `monefit` | Monefit SmartSaver | `https://monefit.com` | Hauptseite, Blog |
| `crowdpear` | Crowdpear | `https://crowdpear.com` | Hauptseite, Statistik, Blog |
| `twino` | Twino | `https://www.twino.eu` | Hauptseite, Kredite, Blog |
| `modena` | Modena | `https://modena.ee` | Hauptseite, Blog |
| `insoil` | Insoil | `https://insoil.finance` | Hauptseite, Auto-Discovery |

---

## Zero-Code: Neue Anbieter hinzufügen (ohne Python-Code)

Neue Plattformen können **vollständig ohne Python-Code** über die Datei [`providers.yaml`](file:///Users/produktmanagement/Python/github/p2p-news/providers.yaml) registriert werden:

```yaml
platforms:
  meine-neue-plattform:
    base_url: "https://plattform-beispiel.com"
    subpages:
      - "/statistics/"
      - "/documents/"
    blog_path: "/blog/"
    auto_discover: true
```

Beim Start liest der Scraper diese Datei ein, instanziiert automatisch den generischen `PlatformProvider` und ermöglicht sofort:
```bash
python p2p_news_scraper.py --provider meine-neue-plattform
```

Auch ganz **ohne Konfigurationseintrag** können beliebige Plattformen via URL gescannt werden:
```bash
python p2p_news_scraper.py --url https://beliebige-neue-plattform.com
```
Die Auto-Discovery erkennt Navigationslinks zu Statistiken, Dokumenten, Blogs und Anbahnern automatisch.

---

## Strukturierte Ablage: News, Erfahrungen & Plattformen

Die Ordnerstruktur trennt primär nach Inhaltstyp (`news/`, `erfahrungen/`, `platforms/`) und sekundär nach Anbieter/Plattform:

```text
data/
├── news/
│   ├── p2p-empire/nachrichten-uebersicht.md
│   ├── p2p-game/plattform-news.md
│   ├── rethink-p2p/news-uebersicht.md
│   ├── passives-einkommen/p2p-kredite-news.md
│   └── p2p-anlage/p2p-anlage-uebersicht.md
├── erfahrungen/
│   ├── p2p-empire/nectaro.md
│   ├── p2p-game/nectaro.md
│   ├── rethink-p2p/loanch.md
│   ├── passives-einkommen/nectaro.md
│   └── p2p-anlage/mypeak.md
└── platforms/
    └── nectaro/
        ├── main.md
        ├── statistics.md
        ├── documents.md
        ├── lending-companies.md
        └── blog/
            ├── index.md
            ├── summer-storm-campaign-cashback-for-every-investor.md
            └── introducing-autopilot-passive-and-profitable.md
```

### Frontmatter-Format (inkl. automatischer Klassifikation)

Jede Datei enthält Metadaten zu Quelle, Typ, Kategorie, Plattform, Änderungshistorie und automatischer Klassifikation:

```yaml
---
source: nectaro
content_type: platform
category: statistics
platform: nectaro
url: https://nectaro.eu/statistics/
title: Performance statistics
published_date: '2026-10-03'
author: null
content_hash: 02b447fdbab9f9e353116d95a7a999d005fd6d68723860901f9803328aba2112
first_seen_at: '2026-10-03T12:18:30.458148+00:00'
last_scanned_at: '2026-10-03T15:01:10.164676+00:00'
scan_count: 4
status: unverändert
classification:
  platforms:
  - nectaro
  topics:
  - zahlen_statistik
  - plattform_features
  sentiment: neutral
  severity: low
history:
- content_hash: 02b447fdbab9f9e353116d95a7a999d005fd6d68723860901f9803328aba2112
  recorded_at: '2026-10-03T12:18:30.458148+00:00'
  status: neu
---
```

---

## Automatische Keyword-Klassifikation

Jeder Artikel wird beim Scraping automatisch analysiert und im YAML Frontmatter unter `classification:` angereichert:
1. **`platforms`**: Erkannte Plattformen (z. B. `[nectaro, mintos, peerberry]`) mit Regex-Wortgrenzen (`\b`).
2. **`topics`**: Thematische Tags (z. B. `zinsen_aktionen`, `risiko_ausfaelle`, `kreditanbahner`, `regulierung_legal`, `zahlen_statistik`, `plattform_features`, `review_erfahrungen`).
3. **`sentiment`**: `positiv`, `negativ` oder `neutral`.
4. **`severity`**: Dringlichkeit/Relevanz (`low`, `medium`, `high` z. B. bei Insolvenzen oder Betrugsverdacht).

### Konfiguration des Keyword-Wörterbuchs via `providers.yaml` (ohne Code-Änderung)

Das gesamte Wörterbuch für Plattformen, Themengebiete, Sentiment und Severity lässt sich in [`providers.yaml`](file:///Users/produktmanagement/Python/github/p2p-news/providers.yaml) unter `classification:` flexibel erweitern und anpassen:

- **Bestehende Kategorien erweitern**: Eigene Signalwörter werden automatisch zu den Standard-Keywords hinzugefügt (z. B. `mega-bonus` zu `zinsen_aktionen`).
- **Neue Themenkategorien hinzufügen**: Beliebige neue Themengruppen (z. B. `ki_automatisierung`, `nachhaltigkeit`) können mit eigener Keyword-Liste definiert werden.
- **Plattform-Katalog**: Jede unter `platforms:` konfigurierte Plattform sowie alle Einträge unter `classification.platforms` werden automatisch erkannt.
- **Sentiment & Severity feintunen**: Signalwörter für Positiv/Negativ sowie Dringlichkeit (`high`, `medium`) sind frei konfigurierbar.

```yaml
classification:
  # Zusätzliche Plattformen
  platforms:
    - superpeer
    - indemo

  # Themen & Trigger-Begriffe (erweitert Defaults oder definiert neue Kategorien)
  topics:
    ki_automatisierung:    # Neue Kategorie
      - künstliche intelligenz
      - algo-trading
      - algorithmus
    zinsen_aktionen:       # Bestehende Kategorie erweitern
      - mega-bonus
      - sonderaktion

  # Sentiment-Signalwörter
  sentiment:
    positive:
      - überflieger
      - allzeithoch
    negative:
      - zahlungsunfähig
      - skandal

  # Dringlichkeits-Keywords
  severity:
    high:
      - insolvenzantrag
      - super-gau
    medium:
      - zinsensenkung
      - serverwartung
```

> [!NOTE]
> Flüchtige Zeitstempel (z. B. `Last update at 03-10-2026 12:18 UTC` auf Statistik-Seiten) werden vor der Hash-Berechnung deterministisch maskiert. Dadurch entstehen keine False-Positive-Änderungen, während echte Datenänderungen (z. B. Portfoliovolumen) weiterhin präzise erkannt werden.

---

## Verwendung

```bash
# Virtuelle Umgebung aktivieren
source .venv/bin/activate

# 1. Alle Anbieter scannen (Aggregatoren + Plattformen)
python p2p_news_scraper.py

# 2. Nur offizielle P2P-Plattformen scannen
python p2p_news_scraper.py --provider platforms

# 3. Nur Aggregatoren & Blogs scannen
python p2p_news_scraper.py --provider aggregators

# 4. Einzelnen Anbieter scannen
python p2p_news_scraper.py --provider nectaro
python p2p_news_scraper.py --provider rethink-p2p
python p2p_news_scraper.py --provider passives-einkommen

# 5. Begrenzter Testlauf (z. B. max. 2 Detailseiten je Anbieter)
python p2p_news_scraper.py --limit 2

# 6. Spezifische URL direkt übergeben (erkennt den Provider automatisch)
python p2p_news_scraper.py --url https://nectaro.eu --limit 3

# 7. JSON-Gesamtzusammenfassung exportieren
python p2p_news_scraper.py --json-export summary.json
```

### CLI-Optionen

| Option | Typ | Standard | Beschreibung |
|---|---|---|---|
| `--provider` | `str` | `all` | Anbietername (`nectaro`, `p2p-empire`, etc.) oder Gruppe (`all`, `aggregators`, `platforms`) |
| `--url` | `str` | `None` | Start-URL (erkennt Provider automatisch) |
| `--output-dir`, `-o` | `str` | `data` | Basis-Zielverzeichnis |
| `--limit` | `int` | `None` | Max. Anzahl Detailseiten je Provider |
| `--timeout` | `float` | `12.0` | HTTP-Timeout in Sekunden |
| `--json-export` | `str` | `None` | Pfad für aggregierten JSON-Export |
| `-v`, `--verbose` | Flag | `False` | Debug-Logging aktivieren |

---

## Tests & CI/CD Pipeline

```bash
./scripts/run_checks.sh
```
Führt die 5 Stufen des Development Pipeline Gates aus (`ruff format`, `ruff check`, `mypy`, `pre-commit`, `pytest`).

---

## Container (Docker & Docker Compose)

### Image bauen
```bash
docker build -t p2p-news:latest .
```

### Ausführen via Docker
```bash
# Einzelnen Scraper mit gemountetem Datenverzeichnis ausführen
docker run --rm -v $(pwd)/data:/app/data p2p-news:latest p2p_news_scraper.py --provider nectaro

# Gesamte Pipeline orchestrieren
docker run --rm -v $(pwd)/data:/app/data --env-file .env p2p-news:latest pipeline_orchestrator.py
```

### Ausführen via Docker Compose
```bash
# Ad-hoc CLI-Ausführungen
docker compose run scraper
docker compose run orchestrator
docker compose run scoring

# Autarker 24/7 Scheduler-Daemon im Hintergrund starten (Europe/Berlin Timezone)
# - Wöchentlich (Montag 06:00 Uhr): Scraping, Fakten-Clustering & Newsletter-Draft
# - Monatlich (1. des Monats 07:00 Uhr): Audit-Scoring & Plattform-Rankings
docker compose up -d scheduler

# Scheduler-Logs verfolgen
docker compose logs -f scheduler
```
