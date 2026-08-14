#!/usr/bin/env python3
"""Read bounded portions of LEARNS.md without modifying the file."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Iterable


MAX_HEADING_CHARS = 800
MAX_CONTENT_CHARS = 1600
MAX_SECTIONS = 3
MAX_SEARCH_WINDOWS = 3
SEARCH_CONTEXT_LINES = 3
HEADING_RE = re.compile(r"^##(?!#)\s+(.+?)\s*$")


def read_lines(path: Path) -> list[str]:
    if not path.is_file():
        return []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    if not text.strip():
        return []
    return text.splitlines()


def limit_output(text: str, max_chars: int) -> str:
    text = text.strip()
    if len(text) <= max_chars:
        return text
    marker = f"\n[truncated at {max_chars} characters]"
    return text[: max_chars - len(marker)].rstrip() + marker


def find_sections(lines: list[str]) -> list[tuple[int, str, int, int]]:
    headings: list[tuple[int, str, int]] = []
    for line_index, line in enumerate(lines):
        match = HEADING_RE.match(line)
        if match:
            headings.append((line_index, match.group(1), len(headings) + 1))

    sections: list[tuple[int, str, int, int]] = []
    for index, (start, title, identifier) in enumerate(headings):
        end = headings[index + 1][0] if index + 1 < len(headings) else len(lines)
        sections.append((identifier, title, start, end))
    return sections


def render_headings(lines: list[str]) -> str:
    items = [
        f"[{identifier}] line {start + 1}: {title}"
        for identifier, title, start, _ in find_sections(lines)
    ]
    return limit_output("\n".join(items), MAX_HEADING_CHARS)


def render_sections(lines: list[str], identifiers: Iterable[int]) -> str:
    requested = list(dict.fromkeys(identifiers))[:MAX_SECTIONS]
    by_identifier = {item[0]: item for item in find_sections(lines)}
    blocks: list[str] = []
    for identifier in requested:
        section = by_identifier.get(identifier)
        if section is None:
            continue
        _, _, start, end = section
        blocks.append("\n".join(lines[start:end]).strip())
    return limit_output(
        "\n\n".join(block for block in blocks if block), MAX_CONTENT_CHARS
    )


def merge_windows(windows: list[tuple[int, int]]) -> list[tuple[int, int]]:
    merged: list[tuple[int, int]] = []
    for start, end in sorted(windows):
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    return merged[:MAX_SEARCH_WINDOWS]


def render_search(lines: list[str], terms: Iterable[str]) -> str:
    needles = [term.casefold() for term in terms if term.strip()]
    if not needles:
        return ""

    windows: list[tuple[int, int]] = []
    for index, line in enumerate(lines):
        folded = line.casefold()
        if any(needle in folded for needle in needles):
            windows.append(
                (
                    max(0, index - SEARCH_CONTEXT_LINES),
                    min(len(lines), index + SEARCH_CONTEXT_LINES + 1),
                )
            )
    blocks = []
    for start, end in merge_windows(windows):
        numbered = [f"{line_no + 1}: {lines[line_no]}" for line_no in range(start, end)]
        blocks.append("\n".join(numbered))
    return limit_output("\n\n".join(blocks), MAX_CONTENT_CHARS)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Read bounded headings or entries from a LEARNS.md file."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    headings = subparsers.add_parser("headings", help="Print only level-two headings")
    headings.add_argument("path", type=Path)

    sections = subparsers.add_parser("sections", help="Print up to three sections")
    sections.add_argument("path", type=Path)
    sections.add_argument("--section", type=int, action="append", default=[])

    search = subparsers.add_parser("search", help="Run one bounded literal search")
    search.add_argument("path", type=Path)
    search.add_argument("--term", action="append", default=[])
    return parser


def main() -> int:
    args = build_parser().parse_args()
    lines = read_lines(args.path)
    if args.command == "headings":
        output = render_headings(lines)
    elif args.command == "sections":
        output = render_sections(lines, args.section)
    else:
        output = render_search(lines, args.term)
    if output:
        sys.stdout.write(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
