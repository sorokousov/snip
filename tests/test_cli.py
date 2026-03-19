from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run_cli(config_root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["XDG_CONFIG_HOME"] = str(config_root)
    env["PYTHONPATH"] = str(ROOT)
    return subprocess.run(
        [sys.executable, "-m", "snip.cli", *args],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


class SnipCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.config_root = Path(self._tmpdir.name) / "config"

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def test_add_and_list(self) -> None:
        add_result = run_cli(self.config_root, "add", "build", "docker", "compose", "up", "--build")
        self.assertEqual(add_result.returncode, 0)
        self.assertIn("Added snippet 'build'.", add_result.stdout)

        list_result = run_cli(self.config_root, "list")
        self.assertEqual(list_result.returncode, 0)
        self.assertEqual(list_result.stdout.strip(), "1. build: docker compose up --build")

    def test_show_by_name_and_index(self) -> None:
        run_cli(self.config_root, "add", "server", "python", "manage.py", "runserver")

        by_name = run_cli(self.config_root, "show", "server")
        by_index = run_cli(self.config_root, "show", "!1")

        self.assertEqual(by_name.returncode, 0)
        self.assertEqual(by_name.stdout.strip(), "python manage.py runserver")
        self.assertEqual(by_index.returncode, 0)
        self.assertEqual(by_index.stdout.strip(), "python manage.py runserver")

    def test_remove_by_index(self) -> None:
        run_cli(self.config_root, "add", "first", "echo", "one")
        run_cli(self.config_root, "add", "second", "echo", "two")

        remove_result = run_cli(self.config_root, "remove", "!1")
        list_result = run_cli(self.config_root, "list")

        self.assertEqual(remove_result.returncode, 0)
        self.assertIn("Removed snippet 'first'.", remove_result.stdout)
        self.assertEqual(list_result.stdout.strip(), "1. second: echo two")

    def test_rename_by_name_and_run_by_index(self) -> None:
        run_cli(self.config_root, "add", "hello", "printf", "hello")

        rename_result = run_cli(self.config_root, "rename", "hello", "greeting")
        run_result = run_cli(self.config_root, "run", "!1")

        self.assertEqual(rename_result.returncode, 0)
        self.assertIn("Renamed snippet to 'greeting'.", rename_result.stdout)
        self.assertEqual(run_result.returncode, 0)
        self.assertEqual(run_result.stdout, "hello")

    def test_duplicate_name_returns_error(self) -> None:
        run_cli(self.config_root, "add", "dup", "echo", "first")

        duplicate_result = run_cli(self.config_root, "add", "dup", "echo", "second")

        self.assertEqual(duplicate_result.returncode, 1)
        self.assertIn("already exists", duplicate_result.stderr)

    def test_invalid_index_returns_error(self) -> None:
        result = run_cli(self.config_root, "show", "!1")

        self.assertEqual(result.returncode, 1)
        self.assertIn("out of range", result.stderr)


if __name__ == "__main__":
    unittest.main()
