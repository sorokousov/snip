from __future__ import annotations

import argparse
import sys
from typing import Sequence

from snip.service import SnipError, SnippetService
from snip.storage import JsonSnippetStorage, StorageError


class SnipArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        self.print_usage(sys.stderr)
        raise SystemExit(f"Error: {message}")


def build_parser() -> argparse.ArgumentParser:
    parser = SnipArgumentParser(prog="snip", description="Store and run named shell snippets.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser("add", help="Add a new snippet")
    add_parser.add_argument("name")
    add_parser.add_argument("command_parts", nargs=argparse.REMAINDER)

    subparsers.add_parser("list", help="List snippets")

    run_parser = subparsers.add_parser("run", help="Run a snippet")
    run_parser.add_argument("reference")

    show_parser = subparsers.add_parser("show", help="Show a snippet command")
    show_parser.add_argument("reference")

    remove_parser = subparsers.add_parser("remove", help="Remove a snippet")
    remove_parser.add_argument("reference")

    rename_parser = subparsers.add_parser("rename", help="Rename a snippet")
    rename_parser.add_argument("reference")
    rename_parser.add_argument("new_name")

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    service = SnippetService(JsonSnippetStorage())

    try:
        if args.command == "add":
            service.add(args.name, args.command_parts)
            print(f"Added snippet '{args.name}'.")
            return 0

        if args.command == "list":
            snippets = service.list_snippets()
            if not snippets:
                print("No snippets saved yet.")
                return 0
            for index, snippet in enumerate(snippets, start=1):
                print(f"{index}. {snippet.name}: {snippet.command}")
            return 0

        if args.command == "show":
            snippet = service.show(args.reference)
            print(snippet.command)
            return 0

        if args.command == "remove":
            snippet = service.remove(args.reference)
            print(f"Removed snippet '{snippet.name}'.")
            return 0

        if args.command == "rename":
            snippet = service.rename(args.reference, args.new_name)
            print(f"Renamed snippet to '{snippet.name}'.")
            return 0

        if args.command == "run":
            return service.run(args.reference)

        parser.error(f"Unknown command: {args.command}")
    except (SnipError, StorageError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
