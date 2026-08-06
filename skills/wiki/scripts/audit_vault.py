#!/usr/bin/env python3
"""Read-only health audit for the user's dual-track Obsidian vault."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path

from find_vault import VaultDiscoveryError, find_vault


FORMAL_DIRS = {"entities", "concepts", "comparisons", "queries"}
FORMAL_SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
REQUIRED_FIELDS = {
    "title",
    "created",
    "updated",
    "type",
    "tags",
    "sources",
    "status",
    "confidence",
}
SKIP_DIRS = {".git", ".obsidian", ".stfolder", ".migration-backups"}
WIKILINK_RE = re.compile(r"(?<!!)\[\[([^\]]+)\]\]")
FENCED_CODE_RE = re.compile(r"^\s*(```|~~~).*?^\s*\1\s*$", re.MULTILINE | re.DOTALL)
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    path: str
    message: str


def parse_frontmatter(text: str) -> tuple[dict[str, object], str]:
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end < 0:
        return {}, text
    block = text[4:end]
    body = text[end + 5 :]
    data: dict[str, object] = {}
    current_list: str | None = None
    for raw_line in block.splitlines():
        list_match = re.match(r"^\s{2,}-\s+(.*)$", raw_line)
        if list_match and current_list:
            value = list_match.group(1).strip().strip('"\'')
            cast = data.setdefault(current_list, [])
            if isinstance(cast, list):
                cast.append(value)
            continue
        field_match = re.match(r"^([A-Za-z_][\w-]*):(?:\s*(.*))?$", raw_line)
        if not field_match:
            current_list = None
            continue
        key, raw_value = field_match.groups()
        raw_value = (raw_value or "").strip()
        if raw_value == "":
            data[key] = []
            current_list = key
        elif raw_value == "[]":
            data[key] = []
            current_list = None
        elif raw_value.startswith("[") and raw_value.endswith("]"):
            data[key] = [
                item.strip().strip('"\'')
                for item in raw_value[1:-1].split(",")
                if item.strip()
            ]
            current_list = None
        else:
            data[key] = raw_value.strip('"\'')
            current_list = None
    return data, body


def markdown_files(vault: Path) -> list[Path]:
    files: list[Path] = []
    for root, dirs, names in os.walk(vault):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        root_path = Path(root)
        files.extend(root_path / name for name in names if name.endswith(".md"))
    return sorted(files)


def extract_links(text: str) -> list[str]:
    text = FENCED_CODE_RE.sub("", text)
    text = INLINE_CODE_RE.sub("", text)
    links: list[str] = []
    for match in WIKILINK_RE.finditer(text):
        target = match.group(1).split("|", 1)[0].split("#", 1)[0].strip()
        if target:
            links.append(target.replace("\\", "/"))
    return links


def normalized_target(target: str) -> str:
    target = target.lstrip("/")
    return target[:-3] if target.lower().endswith(".md") else target


def build_lookup(vault: Path, files: list[Path]) -> tuple[set[str], dict[str, set[str]]]:
    rel_stems: set[str] = set()
    basenames: dict[str, set[str]] = defaultdict(set)
    for path in files:
        rel = path.relative_to(vault).with_suffix("").as_posix()
        rel_stems.add(rel)
        basenames[path.stem].add(rel)
    return rel_stems, basenames


def resolve_link(
    target: str,
    source: Path,
    vault: Path,
    rel_stems: set[str],
    basenames: dict[str, set[str]],
) -> tuple[bool, bool]:
    target = normalized_target(target)
    if target in rel_stems:
        return True, False
    source_dir = source.relative_to(vault).parent
    relative = (source_dir / target).as_posix()
    if relative in rel_stems:
        return True, False
    matches = basenames.get(Path(target).name, set())
    if len(matches) == 1:
        return True, False
    return False, len(matches) > 1


def audit(vault: Path) -> dict[str, object]:
    files = markdown_files(vault)
    rel_stems, basenames = build_lookup(vault, files)
    findings: list[Finding] = []
    contents: dict[Path, str] = {}
    inbound: Counter[str] = Counter()
    formal_pages: list[Path] = []

    index_path = vault / "_wiki" / "index.md"
    index_text = index_path.read_text(encoding="utf-8") if index_path.exists() else ""
    index_links = {normalized_target(link) for link in extract_links(index_text)}

    for path in files:
        rel = path.relative_to(vault).as_posix()
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            findings.append(Finding("error", "non-utf8", rel, "Markdown is not valid UTF-8"))
            continue
        contents[path] = text
        if not text.strip():
            findings.append(Finding("warning", "empty-note", rel, "Markdown note is empty"))
        parts = path.relative_to(vault).parts
        is_formal = len(parts) >= 3 and parts[0] == "_wiki" and parts[1] in FORMAL_DIRS
        if is_formal:
            formal_pages.append(path)
            meta, body = parse_frontmatter(text)
            if not FORMAL_SLUG_RE.fullmatch(path.stem):
                findings.append(
                    Finding("error", "invalid-formal-slug", rel, "Formal page filename is not lowercase kebab-case")
                )
            missing = sorted(REQUIRED_FIELDS - set(meta))
            if missing:
                findings.append(
                    Finding("error", "missing-frontmatter", rel, "Missing fields: " + ", ".join(missing))
                )
            sources = meta.get("sources", [])
            if not isinstance(sources, list):
                sources = [str(sources)] if sources else []
            if not sources:
                severity = "error" if meta.get("confidence") == "high" else "warning"
                findings.append(Finding(severity, "empty-sources", rel, "Formal page has no sources"))
            if not sources and (
                meta.get("status") != "needs-source" or meta.get("confidence") != "low"
            ):
                findings.append(
                    Finding(
                        "warning",
                        "unsourced-status",
                        rel,
                        "Unsourced page should normally use status needs-source and confidence low",
                    )
                )
            for source_ref in sources:
                source_ref = str(source_ref).strip()
                if not source_ref or re.match(r"^[a-z]+://", source_ref):
                    continue
                candidates = [
                    vault / "_wiki" / source_ref,
                    vault / source_ref,
                    path.parent / source_ref,
                ]
                if not any(candidate.exists() for candidate in candidates):
                    findings.append(
                        Finding("error", "missing-source-ref", rel, f"Missing source path: {source_ref}")
                    )
            outgoing = set(extract_links(body))
            if len(outgoing) < 2:
                findings.append(
                    Finding("warning", "few-outgoing-links", rel, f"Only {len(outgoing)} outgoing wikilink(s)")
                )
            stem = path.with_suffix("").relative_to(vault).as_posix()
            if not any(
                candidate in index_links
                for candidate in (stem, path.stem, f"_wiki/{path.parent.name}/{path.stem}")
            ):
                findings.append(Finding("warning", "missing-from-index", rel, "Formal page is not linked from _wiki/index.md"))

        is_raw = len(parts) >= 3 and parts[0] == "_wiki" and parts[1] == "raw"
        if is_raw:
            meta, body = parse_frontmatter(text)
            expected_hash = str(meta.get("sha256", "")).strip()
            if expected_hash:
                actual_hash = hashlib.sha256(body.encode("utf-8")).hexdigest()
                if actual_hash != expected_hash:
                    findings.append(
                        Finding(
                            "error",
                            "raw-hash-drift",
                            rel,
                            f"Body SHA-256 is {actual_hash}, expected {expected_hash}",
                        )
                    )

    seen_broken: set[tuple[str, str]] = set()
    for source, text in contents.items():
        source_rel = source.relative_to(vault).as_posix()
        for target in extract_links(text):
            resolved, ambiguous = resolve_link(target, source, vault, rel_stems, basenames)
            if resolved:
                matches = basenames.get(Path(normalized_target(target)).name, set())
                if len(matches) == 1:
                    inbound[next(iter(matches))] += 1
                elif normalized_target(target) in rel_stems:
                    inbound[normalized_target(target)] += 1
                continue
            key = (source_rel, target)
            if key in seen_broken:
                continue
            seen_broken.add(key)
            code = "ambiguous-wikilink" if ambiguous else "broken-wikilink"
            message = f"Ambiguous target [[{target}]]" if ambiguous else f"Missing target [[{target}]]"
            findings.append(Finding("error", code, source_rel, message))

    for path in formal_pages:
        rel_stem = path.relative_to(vault).with_suffix("").as_posix()
        if inbound[rel_stem] == 0:
            findings.append(
                Finding("warning", "orphan-formal-page", path.relative_to(vault).as_posix(), "No inbound wikilinks")
            )

    for basename, matches in sorted(basenames.items()):
        if len(matches) > 1:
            findings.append(
                Finding(
                    "info",
                    "duplicate-basename",
                    basename,
                    "Multiple notes share this basename: " + ", ".join(sorted(matches)),
                )
            )

    area_counts: Counter[str] = Counter()
    for path in files:
        rel = path.relative_to(vault)
        area_counts[rel.parts[0] if rel.parts else "."] += 1

    findings.sort(key=lambda item: ({"error": 0, "warning": 1, "info": 2}[item.severity], item.path, item.code))
    return {
        "vault": str(vault),
        "summary": {
            "markdown_files": len(files),
            "formal_pages": len(formal_pages),
            "errors": sum(item.severity == "error" for item in findings),
            "warnings": sum(item.severity == "warning" for item in findings),
            "info": sum(item.severity == "info" for item in findings),
            "areas": dict(sorted(area_counts.items())),
        },
        "findings": [asdict(item) for item in findings],
    }


def render_markdown(report: dict[str, object]) -> str:
    summary = report["summary"]
    assert isinstance(summary, dict)
    lines = [
        "# Obsidian Vault Audit",
        "",
        f"- Vault: `{report['vault']}`",
        f"- Markdown files: {summary['markdown_files']}",
        f"- Formal wiki pages: {summary['formal_pages']}",
        f"- Errors: {summary['errors']}",
        f"- Warnings: {summary['warnings']}",
        f"- Info: {summary['info']}",
        "",
        "## Area Counts",
        "",
        "| Area | Markdown files |",
        "| --- | ---: |",
    ]
    areas = summary["areas"]
    assert isinstance(areas, dict)
    lines.extend(f"| `{area}` | {count} |" for area, count in areas.items())
    lines.extend(["", "## Findings", ""])
    findings = report["findings"]
    assert isinstance(findings, list)
    if not findings:
        lines.append("No findings.")
    else:
        lines.extend(["| Severity | Code | Path | Detail |", "| --- | --- | --- | --- |"])
        for item in findings:
            path = str(item["path"]).replace("|", "\\|")
            detail = str(item["message"]).replace("|", "\\|")
            lines.append(f"| {item['severity']} | `{item['code']}` | `{path}` | {detail} |")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--vault",
        type=Path,
        help="Obsidian vault path; auto-discovered when omitted",
    )
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument("--strict", action="store_true", help="Exit 1 when errors are found")
    args = parser.parse_args()
    try:
        vault = find_vault(explicit=args.vault)
    except VaultDiscoveryError as exc:
        parser.error(str(exc))
    report = audit(vault)
    if args.format == "json":
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(render_markdown(report), end="")
    summary = report["summary"]
    assert isinstance(summary, dict)
    return 1 if args.strict and int(summary["errors"]) > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
