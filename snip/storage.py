from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from snip.models import Snippet


class StorageError(Exception):
    """Raised when the storage layer cannot read or write snippets."""


def get_config_dir() -> Path:
    xdg_config_home = os.environ.get("XDG_CONFIG_HOME")
    if xdg_config_home:
        return Path(xdg_config_home).expanduser() / "snip"
    return Path.home() / ".config" / "snip"


def get_storage_path() -> Path:
    return get_config_dir() / "snippets.json"


class JsonSnippetStorage:
    def __init__(self, path: Path | None = None) -> None:
        self._path = path or get_storage_path()

    @property
    def path(self) -> Path:
        return self._path

    def load(self) -> list[Snippet]:
        if not self._path.exists():
            return []

        try:
            with self._path.open("r", encoding="utf-8") as file:
                raw_data: Any = json.load(file)
        except json.JSONDecodeError as exc:
            raise StorageError(f"Failed to parse storage file: {self._path}") from exc
        except OSError as exc:
            raise StorageError(f"Failed to read storage file: {self._path}") from exc

        if not isinstance(raw_data, list):
            raise StorageError("Storage file must contain a list of snippets")

        snippets: list[Snippet] = []
        for item in raw_data:
            if not isinstance(item, dict):
                raise StorageError("Storage file contains an invalid snippet entry")
            name = item.get("name")
            command = item.get("command")
            if not isinstance(name, str) or not isinstance(command, str):
                raise StorageError("Storage file contains an invalid snippet entry")
            snippets.append(Snippet(name=name, command=command))
        return snippets

    def save(self, snippets: list[Snippet]) -> None:
        payload = [{"name": snippet.name, "command": snippet.command} for snippet in snippets]
        try:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            with self._path.open("w", encoding="utf-8") as file:
                json.dump(payload, file, ensure_ascii=False, indent=2)
                file.write("\n")
        except OSError as exc:
            raise StorageError(f"Failed to write storage file: {self._path}") from exc
