#!/usr/bin/env python3
"""Copy a generated dataset into a clean DAB-facing package directory."""

from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path


QUERY_RE = re.compile(r"^query\d+$")
LOCAL_ONLY_DIRS = {"clean", "logs", "__pycache__"}
LOCAL_ONLY_SUFFIXES = {".pyc", ".pyo"}


def ignore_local_only(_dir: str, names: list[str]) -> set[str]:
    ignored: set[str] = set()
    for name in names:
        path = Path(name)
        if name in LOCAL_ONLY_DIRS:
            ignored.add(name)
        elif path.suffix in LOCAL_ONLY_SUFFIXES:
            ignored.add(name)
    return ignored


def copy_path(src: Path, dst: Path) -> None:
    if src.is_dir():
        shutil.copytree(src, dst, ignore=ignore_local_only)
    else:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Generated query_<dataset> directory")
    parser.add_argument("destination", type=Path, help="Destination package directory")
    parser.add_argument("--include-manual", action="store_true", help="Also copy provenance/manual files")
    parser.add_argument("--force", action="store_true", help="Replace destination if it already exists")
    args = parser.parse_args()

    source = args.source.resolve()
    destination = args.destination.resolve()

    if not source.exists():
        print(f"ERROR: source does not exist: {source}")
        return 1
    if destination.exists():
        if not args.force:
            print(f"ERROR: destination exists; pass --force to replace: {destination}")
            return 1
        shutil.rmtree(destination)
    destination.mkdir(parents=True)

    copied: list[str] = []
    top_level = [
        "db_config.yaml",
        "db_description.txt",
        "db_description_withhint.txt",
        "query_dataset",
    ]
    for rel in top_level:
        src = source / rel
        if src.exists():
            copy_path(src, destination / rel)
            copied.append(rel)

    for child in sorted(source.iterdir()):
        if child.is_dir() and QUERY_RE.match(child.name):
            copy_path(child, destination / child.name)
            copied.append(child.name)

    if args.include_manual:
        for rel in ["manual_querycode", "GOLD_ANSWERS.md", "PROVENANCE.md"]:
            src = source / rel
            if src.exists():
                copy_path(src, destination / rel)
                copied.append(rel)

    print(f"source: {source}")
    print(f"destination: {destination}")
    print("copied:")
    for rel in copied:
        print(f"- {rel}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
