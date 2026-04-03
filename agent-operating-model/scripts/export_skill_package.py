#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

SKIP_NAMES = {".git", "__pycache__", "README.md"}
SKIP_SUFFIXES = {".pyc"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Export a clean skill package for distribution, excluding repo-only "
            "artifacts such as README.md and .git."
        )
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Directory where the exported skill folder should be created.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace an existing exported folder.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    skill_root = Path(__file__).resolve().parents[1]
    output_root = Path(args.output).expanduser().resolve()
    target = output_root / skill_root.name

    if target.exists():
        if not args.force:
            raise SystemExit(f"Export target already exists: {target}. Use --force to replace it.")
        shutil.rmtree(target)

    output_root.mkdir(parents=True, exist_ok=True)
    copy_tree(skill_root, target)

    print(f"Exported clean skill package to {target}")
    return 0


def copy_tree(source: Path, target: Path) -> None:
    for path in source.rglob("*"):
        relative = path.relative_to(source)
        if should_skip(relative):
            continue

        destination = target / relative
        if path.is_dir():
            destination.mkdir(parents=True, exist_ok=True)
            continue

        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, destination)


def should_skip(relative: Path) -> bool:
    parts = set(relative.parts)
    if parts & SKIP_NAMES:
        return True
    return relative.suffix in SKIP_SUFFIXES


if __name__ == "__main__":
    sys.exit(main())
