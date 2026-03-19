from __future__ import annotations

import subprocess
from typing import Sequence

from snip.models import Snippet
from snip.storage import JsonSnippetStorage


class SnipError(Exception):
    """Raised for expected user-facing errors."""


class SnippetService:
    def __init__(self, storage: JsonSnippetStorage) -> None:
        self._storage = storage

    def add(self, name: str, command_parts: Sequence[str]) -> Snippet:
        command = " ".join(command_parts).strip()
        if not name.strip():
            raise SnipError("Snippet name cannot be empty.")
        if not command:
            raise SnipError("Snippet command cannot be empty.")

        snippets = self._storage.load()
        if self._find_by_name(snippets, name) is not None:
            raise SnipError(f"Snippet '{name}' already exists.")

        snippet = Snippet(name=name, command=command)
        snippets.append(snippet)
        self._storage.save(snippets)
        return snippet

    def list_snippets(self) -> list[Snippet]:
        return self._storage.load()

    def show(self, reference: str) -> Snippet:
        snippets = self._storage.load()
        return self._resolve_reference(snippets, reference)

    def remove(self, reference: str) -> Snippet:
        snippets = self._storage.load()
        snippet = self._resolve_reference(snippets, reference)
        updated = [item for item in snippets if item.name != snippet.name]
        self._storage.save(updated)
        return snippet

    def rename(self, reference: str, new_name: str) -> Snippet:
        if not new_name.strip():
            raise SnipError("New snippet name cannot be empty.")

        snippets = self._storage.load()
        snippet = self._resolve_reference(snippets, reference)
        if snippet.name != new_name and self._find_by_name(snippets, new_name) is not None:
            raise SnipError(f"Snippet '{new_name}' already exists.")

        renamed = Snippet(name=new_name, command=snippet.command)
        updated: list[Snippet] = []
        for item in snippets:
            updated.append(renamed if item.name == snippet.name else item)
        self._storage.save(updated)
        return renamed

    def run(self, reference: str) -> int:
        snippet = self.show(reference)
        completed = subprocess.run(["bash", "-lc", snippet.command], check=False)
        return completed.returncode

    def _resolve_reference(self, snippets: Sequence[Snippet], reference: str) -> Snippet:
        if reference.startswith("!"):
            return self._find_by_index(snippets, reference)

        snippet = self._find_by_name(snippets, reference)
        if snippet is None:
            raise SnipError(f"Snippet '{reference}' not found.")
        return snippet

    def _find_by_name(self, snippets: Sequence[Snippet], name: str) -> Snippet | None:
        for snippet in snippets:
            if snippet.name == name:
                return snippet
        return None

    def _find_by_index(self, snippets: Sequence[Snippet], reference: str) -> Snippet:
        raw_index = reference[1:]
        try:
            index = int(raw_index)
        except ValueError as exc:
            raise SnipError(f"Invalid snippet index: {reference}.") from exc

        if index < 1 or index > len(snippets):
            raise SnipError(f"Snippet index out of range: {reference}.")
        return snippets[index - 1]
