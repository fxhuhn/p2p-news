"""
Unit Tests für GitPublisher (tests/test_git_publisher.py)

Prüft:
- Auflösung von Dateipfaden und Ordnern
- Deaktivierter Modus (GIT_PUSH_ENABLED=false)
- Lokale Git CLI Engine (Erfolg, Keine Änderungen, Fehlertoleranz)
- GitHub REST API Engine (Zero-CLI Mocking für Docker-Container)
- Fehlende Authentifizierung & Fallback
- 100 % Offline-Ausführung ohne externe Netzwerkaufrufe
"""

from __future__ import annotations

import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from git_publisher import GitPublisher, publish_changes


class TestGitPublisher(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.repo_dir = Path(self.temp_dir.name)
        (self.repo_dir / "data" / "newsletters").mkdir(parents=True, exist_ok=True)
        (self.repo_dir / "data" / "rankings").mkdir(parents=True, exist_ok=True)

        self.newsletter_file = (
            self.repo_dir / "data" / "newsletters" / "newsletter-2026-W41.md"
        )
        self.newsletter_file.write_text("# Test Newsletter", encoding="utf-8")

        self.ranking_file = (
            self.repo_dir / "data" / "rankings" / "audit-ranking-2026-10.md"
        )
        self.ranking_file.write_text("# Test Ranking", encoding="utf-8")

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_disabled_publisher(self) -> None:
        """Prüft, dass bei enabled=False keine Aktionen ausgeführt werden."""
        pub = GitPublisher(repo_dir=self.repo_dir, enabled=False)
        self.assertFalse(pub.enabled)
        res = pub.publish_files([self.newsletter_file], "chore: test")
        self.assertTrue(res)

    def test_resolve_files_and_directories(self) -> None:
        """Prüft die Auflösung von einzelnen Dateien und Verzeichnissen."""
        pub = GitPublisher(repo_dir=self.repo_dir)
        # Verzeichnis übergeben
        resolved = pub._resolve_file_list([self.repo_dir / "data"])
        self.assertIn(self.newsletter_file.resolve(), resolved)
        self.assertIn(self.ranking_file.resolve(), resolved)

        # Einzelne Datei übergeben
        resolved_single = pub._resolve_file_list([self.newsletter_file])
        self.assertEqual(len(resolved_single), 1)
        self.assertEqual(resolved_single[0], self.newsletter_file.resolve())

        # Nicht-existente Datei
        resolved_empty = pub._resolve_file_list(
            [self.repo_dir / "data" / "does_not_exist.md"]
        )
        self.assertEqual(resolved_empty, [])

    def test_strict_data_whitelist_newsletters_rankings_factsheets_only(
        self,
    ) -> None:
        """Prüft, dass ausschließlich newsletters, rankings und factsheets als Daten übertragen werden."""
        # Erlaubte Factsheet-Datei
        fs_dir = self.repo_dir / "data" / "factsheets"
        fs_dir.mkdir(parents=True, exist_ok=True)
        factsheet_file = fs_dir / "mintos.md"
        factsheet_file.write_text("# Mintos Factsheet", encoding="utf-8")

        # Nicht erlaubte lokale Dateien
        digest_dir = self.repo_dir / "data" / "digests"
        digest_dir.mkdir(parents=True, exist_ok=True)
        digest_file = digest_dir / "digest-2026-W41.manifest.json"
        digest_file.write_text("{}", encoding="utf-8")

        plat_dir = self.repo_dir / "data" / "platforms" / "mintos"
        plat_dir.mkdir(parents=True, exist_ok=True)
        plat_file = plat_dir / "profile.yaml"
        plat_file.write_text("platform: mintos", encoding="utf-8")

        draft_dir = self.repo_dir / "data" / "newsletters" / "drafts"
        draft_dir.mkdir(parents=True, exist_ok=True)
        draft_file = draft_dir / "newsletter-2026-W41.draft.md"
        draft_file.write_text("# Draft", encoding="utf-8")

        item_dir = self.repo_dir / "data" / "items"
        item_dir.mkdir(parents=True, exist_ok=True)
        item_file = item_dir / "item_01.md"
        item_file.write_text("# Item", encoding="utf-8")

        db_file = self.repo_dir / "data" / "p2p_archive.db"
        db_file.write_text("mock db", encoding="utf-8")

        pub = GitPublisher(repo_dir=self.repo_dir)

        # 1. Direkte Übergabe
        resolved = pub._resolve_file_list(
            [
                self.newsletter_file,
                self.ranking_file,
                factsheet_file,
                digest_file,
                plat_file,
                draft_file,
                item_file,
                db_file,
            ]
        )
        # Erlaubt
        self.assertIn(self.newsletter_file.resolve(), resolved)
        self.assertIn(self.ranking_file.resolve(), resolved)
        self.assertIn(factsheet_file.resolve(), resolved)
        # Verboten
        self.assertNotIn(digest_file.resolve(), resolved)
        self.assertNotIn(plat_file.resolve(), resolved)
        self.assertNotIn(draft_file.resolve(), resolved)
        self.assertNotIn(item_file.resolve(), resolved)
        self.assertNotIn(db_file.resolve(), resolved)

        # 2. Rekursive Auflösung von data/
        resolved_dir = pub._resolve_file_list([self.repo_dir / "data"])
        self.assertIn(self.newsletter_file.resolve(), resolved_dir)
        self.assertIn(self.ranking_file.resolve(), resolved_dir)
        self.assertIn(factsheet_file.resolve(), resolved_dir)
        self.assertEqual(len(resolved_dir), 3)

    @patch("git_publisher.shutil.which", return_value="/usr/bin/git")
    def test_has_local_git_repo(self, mock_which: MagicMock) -> None:
        """Prüft die Erkennung von lokalen Git-Repositories."""
        pub = GitPublisher(repo_dir=self.repo_dir)
        self.assertFalse(pub.has_local_git_repo())

        # .git Verzeichnis simulieren
        (self.repo_dir / ".git").mkdir()
        self.assertTrue(pub.has_local_git_repo())

    @patch("git_publisher.subprocess.run")
    @patch("git_publisher.shutil.which", return_value="/usr/bin/git")
    def test_publish_via_git_cli_success(
        self, mock_which: MagicMock, mock_run: MagicMock
    ) -> None:
        """Prüft den erfolgreichen Git CLI Durchlauf."""
        (self.repo_dir / ".git").mkdir()

        def side_effect(cmd: list[str], **kwargs: object) -> MagicMock:
            res = MagicMock()
            res.returncode = 0
            if "diff" in cmd:
                res.stdout = "data/newsletters/newsletter-2026-W41.md\n"
            else:
                res.stdout = ""
            res.stderr = ""
            return res

        mock_run.side_effect = side_effect

        pub = GitPublisher(repo_dir=self.repo_dir, enabled=True, branch="main")
        success = pub.publish_files([self.newsletter_file], "chore: publish newsletter")
        self.assertTrue(success)

        # Prüfen, dass git add, git commit und git push ausgeführt wurden
        commands_called = [call_args[0][0] for call_args in mock_run.call_args_list]
        self.assertTrue(any("add" in c for c in commands_called))
        self.assertTrue(any("commit" in c for c in commands_called))
        self.assertTrue(any("push" in c for c in commands_called))

    @patch("git_publisher.subprocess.run")
    @patch("git_publisher.shutil.which", return_value="/usr/bin/git")
    def test_publish_via_git_cli_no_changes(
        self, mock_which: MagicMock, mock_run: MagicMock
    ) -> None:
        """Prüft Verhalten, wenn keine Änderungen vorliegen."""
        (self.repo_dir / ".git").mkdir()

        def side_effect(cmd: list[str], **kwargs: object) -> MagicMock:
            res = MagicMock()
            res.returncode = 0
            if "diff" in cmd:
                res.stdout = ""  # Keine Änderungen
            return res

        mock_run.side_effect = side_effect

        pub = GitPublisher(repo_dir=self.repo_dir, enabled=True)
        success = pub.publish_files([self.newsletter_file], "chore: no change")
        self.assertTrue(success)

        commands_called = [call_args[0][0] for call_args in mock_run.call_args_list]
        self.assertFalse(any("commit" in c for c in commands_called))

    @patch("git_publisher.subprocess.run")
    @patch("git_publisher.shutil.which", return_value="/usr/bin/git")
    def test_publish_via_git_cli_push_error(
        self, mock_which: MagicMock, mock_run: MagicMock
    ) -> None:
        """Prüft Fehlerbehandlung bei fehlgeschlagenem Push."""
        (self.repo_dir / ".git").mkdir()

        def side_effect(cmd: list[str], **kwargs: object) -> MagicMock:
            res = MagicMock()
            if "push" in cmd:
                res.returncode = 1
                res.stderr = "fatal: Authentication failed"
            elif "diff" in cmd:
                res.returncode = 0
                res.stdout = "data/newsletters/newsletter-2026-W41.md\n"
            else:
                res.returncode = 0
                res.stdout = ""
                res.stderr = ""
            return res

        mock_run.side_effect = side_effect

        pub = GitPublisher(repo_dir=self.repo_dir, enabled=True)
        success = pub.publish_files([self.newsletter_file], "chore: fail push")
        self.assertFalse(success)

    @patch("git_publisher.urllib.request.urlopen")
    def test_publish_via_github_api_success(self, mock_urlopen: MagicMock) -> None:
        """Prüft den Zero-CLI GitHub REST API Modus für Container ohne .git."""
        # Sicherstellen, dass kein lokales .git existiert
        self.assertFalse((self.repo_dir / ".git").exists())

        responses = [
            # 1. GET ref
            json.dumps({"object": {"sha": "commit_sha_123"}}).encode("utf-8"),
            # 2. GET commit
            json.dumps({"tree": {"sha": "tree_sha_123"}}).encode("utf-8"),
            # 3. POST tree
            json.dumps({"sha": "new_tree_sha_456"}).encode("utf-8"),
            # 4. POST commit
            json.dumps({"sha": "new_commit_sha_789"}).encode("utf-8"),
            # 5. PATCH ref
            json.dumps({"object": {"sha": "new_commit_sha_789"}}).encode("utf-8"),
        ]

        mock_context = MagicMock()
        mock_context.__enter__.side_effect = [io.BytesIO(resp) for resp in responses]
        mock_urlopen.return_value = mock_context

        pub = GitPublisher(
            repo_dir=self.repo_dir,
            enabled=True,
            token="ghp_mock_token",
            repository="fxhuhn/p2p-news",
            branch="main",
        )
        success = pub.publish_files(
            [self.newsletter_file], "chore(newsletter): publish W41"
        )
        self.assertTrue(success)

        # 5 API-Aufrufe müssen stattgefunden haben
        self.assertEqual(mock_urlopen.call_count, 5)

        # Prüfen, dass der 5. Aufruf PATCH auf das Plural-Endpoint /git/refs/heads/main war
        patch_req = mock_urlopen.call_args_list[4][0][0]
        self.assertEqual(patch_req.get_method(), "PATCH")
        self.assertTrue(
            patch_req.full_url.endswith("/git/refs/heads/main"),
            f"Erwartete plural git/refs/heads/main URL, erhalten: {patch_req.full_url}",
        )

    def test_missing_git_and_token(self) -> None:
        """Prüft den sauberen Warn-Fallback, wenn weder .git noch Token existieren."""
        pub = GitPublisher(repo_dir=self.repo_dir, enabled=True, token="")
        success = pub.publish_files([self.newsletter_file], "chore: no auth")
        self.assertFalse(success)

    def test_convenience_function(self) -> None:
        """Prüft die Top-Level publish_changes Funktion."""
        with patch.object(GitPublisher, "publish_files", return_value=True) as mock_pub:
            res = publish_changes([self.newsletter_file], "chore: test")
            self.assertTrue(res)
            mock_pub.assert_called_once()


if __name__ == "__main__":
    unittest.main()
