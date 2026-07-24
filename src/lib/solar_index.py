"""Helpers for SOLAR's output/data/index.json discovery file.

index.json is a git-tracked file published by the SOLAR repo describing every
file under its output/data/ tree. It is a nested dict of directory names down
to file leaves; each file leaf carries "themes" (list[str]) and
"publication_export" (bool). Top-level keys starting with "_" are metadata
("_themes", "_publication_exports") rather than tree nodes.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def load_index(path: str | Path) -> dict:
    with open(path) as f:
        return json.load(f)


def _is_file_leaf(node: object) -> bool:
    return isinstance(node, dict) and "themes" in node and "publication_export" in node


def list_themes(index: dict) -> dict:
    themes = index.get("_themes", {})
    if isinstance(themes, dict):
        return themes
    return {name: "" for name in themes}


def filter_index_tree(
    tree: dict,
    themes: list[str] | None = None,
    publication_only: bool = False,
) -> list[str]:
    """Recursively walk an index.json tree, returning matching relative paths.

    Paths are forward-slash-joined and relative to output/data/. With no
    filters, every file path in the tree is returned. With themes given, a
    file matches if it has any theme in common with `themes`. With
    publication_only=True, a file matches if publication_export is True.
    Both filters may be combined (AND).
    """
    theme_set = set(themes) if themes else None
    if theme_set:
        available = list_themes(tree)
        unknown = theme_set - set(available)
        if unknown:
            raise ValueError(
                f"Unknown theme(s): {', '.join(sorted(unknown))}. "
                f"Available themes: {', '.join(sorted(available))}"
            )

    paths: list[str] = []

    def walk(node: dict, prefix: str) -> None:
        for key, value in node.items():
            if key.startswith("_"):
                continue
            rel = f"{prefix}/{key}" if prefix else key
            if _is_file_leaf(value):
                if publication_only and not value.get("publication_export"):
                    continue
                if theme_set is not None and not (theme_set & set(value.get("themes", []))):
                    continue
                paths.append(rel)
            elif isinstance(value, dict):
                walk(value, rel)

    walk(tree, "")
    return sorted(paths)


def _main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Query a SOLAR output/data/index.json file")
    sub = parser.add_subparsers(dest="command", required=True)

    filter_p = sub.add_parser("filter", help="Print output/data/-relative paths matching filters")
    filter_p.add_argument("--index", required=True, help="Path to a local index.json")
    filter_p.add_argument("--theme", action="append", default=None, help="Restrict to this theme (repeatable)")
    filter_p.add_argument("--publication", action="store_true", help="Restrict to publication_export files")

    themes_p = sub.add_parser("list-themes", help="Print available themes and exit")
    themes_p.add_argument("--index", required=True, help="Path to a local index.json")

    args = parser.parse_args(argv)
    index = load_index(args.index)

    if args.command == "filter":
        try:
            for path in filter_index_tree(index, themes=args.theme, publication_only=args.publication):
                print(path)
        except ValueError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 1
    elif args.command == "list-themes":
        for name, description in sorted(list_themes(index).items()):
            print(f"{name}: {description}")

    return 0


if __name__ == "__main__":
    sys.exit(_main())
