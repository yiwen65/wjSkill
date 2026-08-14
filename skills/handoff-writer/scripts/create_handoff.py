#!/usr/bin/env python3
"""Create a collision-safe, automatically named Markdown handoff."""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
import re
import sys
import unicodedata


def topic_slug(topic: str) -> str:
    """Convert a topic to a filesystem-safe, Unicode-aware slug."""
    normalized = unicodedata.normalize("NFKC", topic).casefold()
    slug = "".join(character if character.isalnum() else "-" for character in normalized)
    slug = re.sub(r"-+", "-", slug).strip("-")
    return slug[:60].rstrip("-") or "handoff"


def create_handoff(root: Path, topic: str, content: str) -> Path:
    """Write content without overwriting and return the resolved output path."""
    if not content.strip():
        raise ValueError("handoff content must not be empty")

    root = root.expanduser().resolve()
    if not root.is_dir():
        raise ValueError(f"workspace root is not a directory: {root}")

    output_dir = root / "docs" / "handoff"
    output_dir.mkdir(parents=True, exist_ok=True)
    stem = f"{datetime.now().strftime('%Y-%m-%d-%H%M%S')}-{topic_slug(topic)}"
    body = content.rstrip() + "\n"

    suffix = 1
    while True:
        filename = f"{stem}.md" if suffix == 1 else f"{stem}-{suffix}.md"
        destination = output_dir / filename
        try:
            with destination.open("x", encoding="utf-8", newline="\n") as output:
                output.write(body)
        except FileExistsError:
            suffix += 1
            continue
        return destination.resolve()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create an automatically named Markdown handoff from standard input."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Workspace root; defaults to the current working directory.",
    )
    parser.add_argument("--topic", required=True, help="Short topic used in the filename slug.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        destination = create_handoff(args.root, args.topic, sys.stdin.read())
    except (OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    print(destination)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
