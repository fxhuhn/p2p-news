"""
Git & GitHub Publisher für P2P-News.

Veröffentlicht automatisiert generierte Artefakte (Newsletter, Factsheets, Rankings)
zurück in das GitHub-Repository.

Unterstützt zwei Betriebsmodi:
1. Git CLI Engine:
   Nutzt das lokale git-Binary (git add, git commit, git push), wenn ein .git-Verzeichnis
   vorhanden ist (lokaler Entwickler-Modus oder Container mit gemountetem Repo).
2. GitHub REST API Engine (Zero-CLI):
   Führt atomare Commits direkt über die GitHub Git Database API aus.
   Ideal für schlanke Docker-Container, in denen nur /app/data gemountet ist und kein
   .git-Verzeichnis vorliegt.

Konfiguration via Umgebungsvariablen (.env):
- GIT_PUSH_ENABLED: 'true' (Standard) oder 'false' zum Deaktivieren.
- GITHUB_TOKEN / GH_TOKEN: Personal Access Token oder GitHub Actions Token.
- GITHUB_REPOSITORY: Repository im Format 'owner/repo' (Standard: 'fxhuhn/p2p-news').
- GIT_BRANCH: Ziel-Branch (Standard: 'main').
- GIT_AUTHOR_NAME: Commit-Autor (Standard: 'P2P News Automation').
- GIT_AUTHOR_EMAIL: Commit-E-Mail (Standard: 'bot@p2p-news.local').
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import shutil
import subprocess
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

logger = logging.getLogger("git_publisher")


class GitPublisher:
    """Verwaltet und führt automatisierte Git-Commits und Pushes durch."""

    def __init__(
        self,
        repo_dir: Path | str | None = None,
        enabled: bool | None = None,
        token: str | None = None,
        repository: str | None = None,
        branch: str | None = None,
        author_name: str | None = None,
        author_email: str | None = None,
    ) -> None:
        self.repo_dir = Path(repo_dir or Path.cwd()).resolve()

        if enabled is None:
            env_val = os.getenv("GIT_PUSH_ENABLED", "true").strip().lower()
            self.enabled = env_val not in ("false", "0", "no", "off")
        else:
            self.enabled = enabled

        self.token = (
            token or os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN") or ""
        ).strip()
        self.repository = (
            repository or os.getenv("GITHUB_REPOSITORY") or "fxhuhn/p2p-news"
        ).strip()
        self.branch = (branch or os.getenv("GIT_BRANCH") or "main").strip()
        self.author_name = (
            author_name or os.getenv("GIT_AUTHOR_NAME") or "P2P News Automation"
        ).strip()
        self.author_email = (
            author_email or os.getenv("GIT_AUTHOR_EMAIL") or "bot@p2p-news.local"
        ).strip()

    def has_local_git_repo(self) -> bool:
        """Prüft, ob ein gültiges .git-Verzeichnis existiert und git im PATH ist."""
        git_dir = self.repo_dir / ".git"
        has_git_dir = git_dir.is_dir() or git_dir.is_file()  # submodule/worktree
        has_binary = shutil.which("git") is not None
        return has_git_dir and has_binary

    def publish_files(
        self,
        files: list[Path | str],
        commit_message: str,
        data_dir: Path | str = "data",
    ) -> bool:
        """
        Committet und pusht die angegebenen Dateien zurück nach GitHub.

        Args:
            files: Liste von Dateipfaden oder Verzeichnissen (z. B. 'data/newsletters/newsletter-2026-W41.md').
            commit_message: Git-Commit-Botschaft.
            data_dir: Basisverzeichnis für relative Pfade (Standard: 'data').

        Returns:
            True bei Erfolg oder wenn keine Änderungen vorlagen, False bei Fehler.
        """
        if not self.enabled:
            logger.info(
                "[GIT-PUBLISHER] Push deaktiviert (GIT_PUSH_ENABLED=false). Vorgang übersprungen."
            )
            return True

        resolved_files = self._resolve_file_list(files)
        if not resolved_files:
            logger.warning(
                "[GIT-PUBLISHER] Keine existierenden Dateien zum Veröffentlichen gefunden."
            )
            return True

        logger.info(
            "[GIT-PUBLISHER] Starte Veröffentlichung von %d Dateien...",
            len(resolved_files),
        )

        # 1. Bevorzuge Git CLI, wenn lokales .git vorhanden ist
        if self.has_local_git_repo():
            logger.info("[GIT-PUBLISHER] Verwende lokale Git CLI Engine.")
            return self._publish_via_git_cli(resolved_files, commit_message)

        # 2. Fallback: GitHub REST API Engine (Container ohne .git-Mount)
        if self.token:
            logger.info(
                "[GIT-PUBLISHER] Kein .git-Verzeichnis gefunden. Verwende GitHub REST API Engine für %s...",
                self.repository,
            )
            return self._publish_via_github_api(resolved_files, commit_message)

        logger.warning(
            "[GIT-PUBLISHER] Weder lokales .git-Verzeichnis noch GITHUB_TOKEN vorhanden. "
            "Änderungen können nicht nach GitHub gepusht werden. "
            "Tipp: Konfiguriere GITHUB_TOKEN in .env für automatische Pushes aus Containern."
        )
        return False

    def _resolve_file_list(self, files: list[Path | str]) -> list[Path]:
        """Löst Pfade, Verzeichnisse und Globs in existierende Dateipfade auf."""
        result: list[Path] = []
        for item in files:
            p = Path(item)
            if not p.is_absolute():
                p = self.repo_dir / p

            if p.is_dir():
                for sub in p.rglob("*"):
                    if sub.is_file() and not sub.name.startswith("."):
                        result.append(sub.resolve())
            elif p.is_file():
                result.append(p.resolve())
            elif "*" in str(item) or "?" in str(item):
                # Versuch als relatives Glob-Muster
                try:
                    rel_pat = (
                        str(p.relative_to(self.repo_dir))
                        if p.is_relative_to(self.repo_dir)
                        else str(item)
                    )
                    matched = list(self.repo_dir.glob(rel_pat))
                    for m in matched:
                        if m.is_file():
                            result.append(m.resolve())
                except Exception:
                    pass

        # Duplikate entfernen unter Beibehaltung der Reihenfolge
        seen: set[Path] = set()
        deduped: list[Path] = []
        for r in result:
            if r not in seen:
                seen.add(r)
                deduped.append(r)
        return deduped

    # =========================================================================
    # Engine 1: Git CLI
    # =========================================================================

    def _publish_via_git_cli(self, files: list[Path], commit_message: str) -> bool:
        try:
            # 1. Git-Konfiguration für Commit-Autor sicherstellen (falls nicht global gesetzt)
            subprocess.run(
                ["git", "config", "user.name", self.author_name],
                cwd=self.repo_dir,
                check=True,
                capture_output=True,
            )
            subprocess.run(
                ["git", "config", "user.email", self.author_email],
                cwd=self.repo_dir,
                check=True,
                capture_output=True,
            )

            # 2. Dateien stagen
            rel_paths = [str(f.relative_to(self.repo_dir)) for f in files]
            subprocess.run(
                ["git", "add", "--"] + rel_paths,
                cwd=self.repo_dir,
                check=True,
                capture_output=True,
            )

            # 3. Prüfen, ob tatsächliche Änderungen vorliegen
            status_res = subprocess.run(
                ["git", "diff", "--cached", "--name-only"],
                cwd=self.repo_dir,
                capture_output=True,
                text=True,
                check=True,
            )
            staged = status_res.stdout.strip().splitlines()
            if not staged:
                logger.info(
                    "[GIT-PUBLISHER] Keine Änderungen gegenüber HEAD. Commit übersprungen."
                )
                return True

            logger.info(
                "[GIT-PUBLISHER] %d geänderte Datei(en) vorgemerkt zum Commit.",
                len(staged),
            )

            # 4. Commit erstellen
            commit_res = subprocess.run(
                ["git", "commit", "-m", commit_message],
                cwd=self.repo_dir,
                capture_output=True,
                text=True,
            )
            if commit_res.returncode != 0:
                logger.error(
                    "[GIT-PUBLISHER] 'git commit' fehlgeschlagen: %s",
                    commit_res.stderr.strip(),
                )
                return False

            # 5. Push mit Authentifizierung
            push_target = "origin"
            if self.token and self.repository:
                # Nutze token-basierte Remote-URL für headless pushes ohne interaktive Passwortabfrage
                push_target = f"https://x-access-token:{self.token}@github.com/{self.repository}.git"

            push_res = subprocess.run(
                ["git", "push", push_target, self.branch],
                cwd=self.repo_dir,
                capture_output=True,
                text=True,
            )
            if push_res.returncode != 0:
                # Sensible Token-URL in Fehlermeldungen maskieren
                safe_err = (
                    push_res.stderr.replace(self.token, "***")
                    if self.token
                    else push_res.stderr
                )
                logger.error(
                    "[GIT-PUBLISHER] 'git push' fehlgeschlagen: %s", safe_err.strip()
                )
                return False

            logger.info(
                "✓ [GIT-PUBLISHER] Erfolgreich committet und gepusht nach origin/%s: '%s'",
                self.branch,
                commit_message,
            )
            return True

        except subprocess.CalledProcessError as exc:
            err_msg = (
                exc.stderr.decode("utf-8", errors="replace")
                if isinstance(exc.stderr, bytes)
                else str(exc.stderr)
            )
            if self.token:
                err_msg = err_msg.replace(self.token, "***")
            logger.error("[GIT-PUBLISHER] Git CLI Fehler: %s", err_msg)
            return False
        except Exception as exc:
            logger.exception(
                "[GIT-PUBLISHER] Unerwarteter Fehler bei Git CLI Ausführung: %s", exc
            )
            return False

    # =========================================================================
    # Engine 2: GitHub REST API (Zero-CLI)
    # =========================================================================

    def _publish_via_github_api(self, files: list[Path], commit_message: str) -> bool:
        """Erstellt einen atomaren Git-Commit direkt über die GitHub Git Database REST API."""
        try:
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "P2P-News-GitPublisher/1.0",
            }
            api_base = f"https://api.github.com/repos/{self.repository}"

            # 1. Neuesten Commit-SHA des Ziel-Branches abrufen
            ref_url = f"{api_base}/git/ref/heads/{self.branch}"
            ref_data = self._http_request(ref_url, headers=headers)
            latest_commit_sha = ref_data["object"]["sha"]

            # 2. Base Tree SHA des neuesten Commits ermitteln
            commit_url = f"{api_base}/git/commits/{latest_commit_sha}"
            commit_data = self._http_request(commit_url, headers=headers)
            base_tree_sha = commit_data["tree"]["sha"]

            # 3. Tree-Elemente für alle geänderten Dateien vorbereiten
            tree_items: list[dict[str, Any]] = []
            for f in files:
                rel_path = str(f.relative_to(self.repo_dir)).replace("\\", "/")
                content = f.read_text(encoding="utf-8")
                tree_items.append(
                    {
                        "path": rel_path,
                        "mode": "100644",
                        "type": "blob",
                        "content": content,
                    }
                )

            # 4. Neuen Tree erstellen
            trees_url = f"{api_base}/git/trees"
            tree_payload = {
                "base_tree": base_tree_sha,
                "tree": tree_items,
            }
            new_tree_data = self._http_request(
                trees_url,
                method="POST",
                headers=headers,
                payload=tree_payload,
            )
            new_tree_sha = new_tree_data["sha"]

            if new_tree_sha == base_tree_sha:
                logger.info(
                    "[GIT-PUBLISHER] GitHub API: Keine inhaltlichen Änderungen gegenüber Remote-Tree. Commit übersprungen."
                )
                return True

            # 5. Neuen Commit erstellen
            commits_url = f"{api_base}/git/commits"
            commit_payload = {
                "message": commit_message,
                "tree": new_tree_sha,
                "parents": [latest_commit_sha],
                "author": {
                    "name": self.author_name,
                    "email": self.author_email,
                },
            }
            new_commit_data = self._http_request(
                commits_url,
                method="POST",
                headers=headers,
                payload=commit_payload,
            )
            new_commit_sha = new_commit_data["sha"]

            # 6. Branch Ref aktualisieren
            self._http_request(
                ref_url,
                method="PATCH",
                headers=headers,
                payload={"sha": new_commit_sha},
            )

            logger.info(
                "✓ [GIT-PUBLISHER] GitHub REST API: Neuer Commit %s auf Branch '%s' erstellt: '%s'",
                new_commit_sha[:8],
                self.branch,
                commit_message,
            )
            return True

        except urllib.error.HTTPError as http_err:
            body = http_err.read().decode("utf-8", errors="replace")
            logger.error(
                "[GIT-PUBLISHER] GitHub API HTTP-Fehler %d: %s (%s)",
                http_err.code,
                http_err.reason,
                body,
            )
            return False
        except Exception as exc:
            logger.exception("[GIT-PUBLISHER] GitHub REST API Fehler: %s", exc)
            return False

    def _http_request(
        self,
        url: str,
        method: str = "GET",
        headers: dict[str, str] | None = None,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        data_bytes = (
            json.dumps(payload).encode("utf-8") if payload is not None else None
        )
        req = urllib.request.Request(
            url,
            data=data_bytes,
            headers=headers or {},
            method=method,
        )
        if payload is not None:
            req.add_header("Content-Type", "application/json")

        with urllib.request.urlopen(req, timeout=20.0) as resp:
            raw_response = resp.read().decode("utf-8")
            return json.loads(raw_response) if raw_response else {}


def publish_changes(
    files: list[Path | str],
    commit_message: str,
    data_dir: Path | str = "data",
) -> bool:
    """Komfort-Funktion zur einfachen Einbindung in Scheduler und Pipeline."""
    publisher = GitPublisher()
    return publisher.publish_files(
        files=files, commit_message=commit_message, data_dir=data_dir
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="P2P News Git Publisher CLI (Commit & Push zu GitHub)"
    )
    parser.add_argument(
        "--files",
        nargs="+",
        required=True,
        help="Dateien oder Ordner, die committet werden sollen",
    )
    parser.add_argument(
        "--message",
        "-m",
        required=True,
        help="Commit-Botschaft",
    )
    parser.add_argument(
        "--data-dir",
        default="data",
        help="Basis-Datenverzeichnis",
    )
    args = parser.parse_args()

    success = publish_changes(
        files=args.files, commit_message=args.message, data_dir=args.data_dir
    )
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
