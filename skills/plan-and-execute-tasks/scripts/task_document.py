#!/usr/bin/env python3
"""Create and structurally validate tracked Markdown task documents."""

from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import date
from pathlib import Path
import re
import sys


SECTION_MARKERS = (
    "background-goal",
    "scope-non-goals",
    "facts-evidence",
    "assumptions-questions",
    "acceptance-criteria",
    "dependencies-batches",
    "task-list",
    "validation-plan",
    "risks-blockers",
    "execution-log",
    "final-validation",
)

TASK_FIELDS = (
    "Status",
    "Owner",
    "Objective",
    "Inputs and prerequisites",
    "Scope or files",
    "Expected output",
    "Dependencies",
    "Execution steps",
    "Acceptance criteria",
    "Verification method",
    "Validation evidence",
    "Blocker",
    "Unblock condition",
)

TASK_HEADING_RE = re.compile(
    r"^### \[([ xX])\] (T-\d{3,})\b[^\n]*$", re.MULTILINE
)
FIELD_RE = re.compile(r"^- ([A-Za-z][A-Za-z ]+):(?:\s*(.*))?$", re.MULTILINE)
TASK_ID_RE = re.compile(r"\bT-\d{3,}\b")
VALID_STATUSES = {"pending", "in_progress", "blocked", "done"}
VALID_FINAL_RESULTS = {"not_run", "partial", "failed", "blocked", "passed"}
EMPTY_VALUES = {"", "todo", "tbd", "not run", "not run.", "未执行", "未执行。"}
NONE_VALUES = {"none", "none.", "无", "无。", "n/a"}


def kebab_slug(value: str) -> str:
    """Return a lowercase ASCII kebab slug or an empty string."""
    slug = re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")
    return re.sub(r"-+", "-", slug)


def validate_slug(slug: str) -> str:
    """Validate a stable lowercase ASCII kebab slug."""
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
        raise ValueError("slug must use lowercase ASCII letters, digits, and hyphens")
    if len(slug) > 60:
        raise ValueError("slug must be 60 characters or fewer")
    return slug


def skeleton(title: str, workspace: Path, mode: str) -> str:
    """Build a deliberately incomplete document for the agent to fill."""
    created = date.today().isoformat()
    return f"""# Task Plan: {title}

- Created: {created}
- Workspace: {workspace}
- Mode: {mode}
- Overall status: pending
- Source: TODO

<!-- task-doc-section:background-goal -->
## Background and goal

TODO

<!-- task-doc-section:scope-non-goals -->
## Scope and non-goals

TODO

<!-- task-doc-section:facts-evidence -->
## Confirmed facts and evidence

| ID | Confirmed fact | Evidence |
| --- | --- | --- |
| F-001 | TODO | TODO |

<!-- task-doc-section:assumptions-questions -->
## Assumptions and open questions

- Assumption: TODO
- Open question: TODO

<!-- task-doc-section:acceptance-criteria -->
## Acceptance criteria

- TODO

<!-- task-doc-section:dependencies-batches -->
## Dependencies and parallel batches

- Dependency graph: TODO
- Parallel batches: TODO
- Serialization constraints: TODO

<!-- task-doc-section:task-list -->
## Task list

### [ ] T-001 — TODO

- Status: pending
- Owner: unassigned
- Objective: TODO
- Inputs and prerequisites: TODO
- Scope or files: TODO
- Expected output: TODO
- Dependencies: None.
- Execution steps:
  1. TODO
- Acceptance criteria:
  - TODO
- Verification method:
  - TODO
- Validation evidence: Not run.
- Blocker: None.
- Unblock condition: None.

<!-- task-doc-section:validation-plan -->
## Test and validation plan

TODO

<!-- task-doc-section:risks-blockers -->
## Risks and blockers

TODO

<!-- task-doc-section:execution-log -->
## Execution log

- {created}: Task document created; content not yet completed.

<!-- task-doc-section:final-validation -->
## Final validation result

- Result: not_run
- Evidence: Not run.
- Limitations: TODO
"""


def create_document(root: Path, title: str, slug: str | None, mode: str) -> Path:
    """Create a collision-safe task document and return its resolved path."""
    root = root.expanduser().resolve()
    if not root.is_dir():
        raise ValueError(f"workspace root is not a directory: {root}")
    if not title.strip():
        raise ValueError("title must not be empty")

    resolved_slug = validate_slug(slug or kebab_slug(title))
    output_dir = root / "docs" / "tasks"
    output_dir.mkdir(parents=True, exist_ok=True)
    stem = f"{date.today().isoformat()}-{resolved_slug}"
    content = skeleton(title.strip(), root, mode)

    sequence = 1
    while True:
        suffix = "" if sequence == 1 else f"-{sequence}"
        destination = output_dir / f"{stem}{suffix}-task.md"
        try:
            with destination.open("x", encoding="utf-8", newline="\n") as output:
                output.write(content)
        except FileExistsError:
            sequence += 1
            continue
        return destination.resolve()


def field_values(block: str) -> dict[str, str]:
    """Extract top-level task fields, including their indented continuation."""
    matches = list(FIELD_RE.finditer(block))
    values: dict[str, str] = {}
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(block)
        inline = match.group(2) or ""
        continuation = block[match.end() : end].strip()
        values[match.group(1)] = "\n".join(
            part for part in (inline.strip(), continuation) if part
        ).strip()
    return values


def is_empty(value: str) -> bool:
    """Return whether a required field still has a placeholder value."""
    normalized = value.strip().casefold()
    return normalized in EMPTY_VALUES or "todo" in normalized


def validate_document(path: Path) -> list[str]:
    """Return structural and state-integrity errors for a task document."""
    path = path.expanduser().resolve()
    if not path.is_file():
        return [f"task document does not exist: {path}"]
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []

    if not text.startswith("# "):
        errors.append("document must start with a level-one heading")
    if re.search(r"\b(?:TODO|TBD)\b", text, re.IGNORECASE):
        errors.append("document still contains TODO or TBD placeholders")

    overall_match = re.search(r"^- Overall status:\s*(\S+)\s*$", text, re.MULTILINE)
    overall_status = overall_match.group(1) if overall_match else ""
    if not overall_match:
        errors.append("document must declare Overall status")
    elif overall_status not in VALID_STATUSES:
        errors.append(f"invalid Overall status {overall_status!r}")

    positions: list[int] = []
    for marker in SECTION_MARKERS:
        token = f"<!-- task-doc-section:{marker} -->"
        count = text.count(token)
        if count != 1:
            errors.append(f"required section marker {marker!r} must appear exactly once")
        else:
            positions.append(text.index(token))
    if len(positions) == len(SECTION_MARKERS) and positions != sorted(positions):
        errors.append("required section markers are out of order")

    task_start_token = "<!-- task-doc-section:task-list -->"
    task_end_token = "<!-- task-doc-section:validation-plan -->"
    task_start = text.find(task_start_token)
    task_end = text.find(task_end_token)
    all_headings = list(TASK_HEADING_RE.finditer(text))
    headings = [
        heading
        for heading in all_headings
        if task_start >= 0 and task_end >= 0 and task_start < heading.start() < task_end
    ]
    if len(headings) != len(all_headings):
        errors.append("all task headings must be inside the task-list section")
    if not headings:
        errors.append("document must contain at least one task heading")
        return errors

    tasks: dict[str, dict[str, object]] = {}
    dependencies: dict[str, set[str]] = defaultdict(set)
    for index, heading in enumerate(headings):
        checkbox, task_id = heading.groups()
        if task_id in tasks:
            errors.append(f"duplicate task ID: {task_id}")
            continue
        end = headings[index + 1].start() if index + 1 < len(headings) else task_end
        block = text[heading.end() : end]
        values = field_values(block)
        tasks[task_id] = {"checked": checkbox.casefold() == "x", "fields": values}

        for field in TASK_FIELDS:
            if field not in values:
                errors.append(f"{task_id}: missing field {field!r}")
            elif field not in {
                "Dependencies",
                "Validation evidence",
                "Blocker",
                "Unblock condition",
            } and is_empty(values[field]):
                errors.append(f"{task_id}: field {field!r} is empty or placeholder text")

        status = values.get("Status", "").strip()
        checked = checkbox.casefold() == "x"
        if status not in VALID_STATUSES:
            errors.append(f"{task_id}: invalid Status {status!r}")
        if checked != (status == "done"):
            errors.append(f"{task_id}: checkbox and Status must agree on done state")

        evidence = values.get("Validation evidence", "")
        if status in {"blocked", "done"} and is_empty(evidence):
            errors.append(f"{task_id}: {status} requires actual validation evidence")
        if status == "blocked":
            blocker = values.get("Blocker", "").strip().casefold()
            unblock = values.get("Unblock condition", "").strip().casefold()
            if blocker in EMPTY_VALUES | NONE_VALUES:
                errors.append(f"{task_id}: blocked requires a concrete Blocker")
            if unblock in EMPTY_VALUES | NONE_VALUES:
                errors.append(f"{task_id}: blocked requires a concrete Unblock condition")

        dependency_text = values.get("Dependencies", "")
        dependencies[task_id] = set(TASK_ID_RE.findall(dependency_text))

    task_ids = set(tasks)
    for task_id, refs in dependencies.items():
        if task_id in refs:
            errors.append(f"{task_id}: task cannot depend on itself")
        for ref in sorted(refs - task_ids):
            errors.append(f"{task_id}: dependency {ref} does not exist")
        fields = tasks[task_id]["fields"]
        assert isinstance(fields, dict)
        status = str(fields.get("Status", ""))
        if status == "done":
            for ref in refs & task_ids:
                ref_fields = tasks[ref]["fields"]
                assert isinstance(ref_fields, dict)
                ref_status = str(ref_fields.get("Status", ""))
                if ref_status != "done":
                    errors.append(f"{task_id}: done task depends on non-done {ref}")

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(task_id: str, trail: list[str]) -> None:
        if task_id in visiting:
            cycle = trail[trail.index(task_id) :] + [task_id]
            errors.append("dependency cycle: " + " -> ".join(cycle))
            return
        if task_id in visited:
            return
        visiting.add(task_id)
        for ref in sorted(dependencies[task_id] & task_ids):
            visit(ref, trail + [ref])
        visiting.remove(task_id)
        visited.add(task_id)

    for task_id in sorted(task_ids):
        visit(task_id, [task_id])

    task_statuses: list[str] = []
    for task_id in sorted(task_ids):
        fields = tasks[task_id]["fields"]
        assert isinstance(fields, dict)
        task_statuses.append(str(fields.get("Status", "")))
    all_done = bool(task_statuses) and all(status == "done" for status in task_statuses)

    final_start_token = "<!-- task-doc-section:final-validation -->"
    final_start = text.find(final_start_token)
    final_text = text[final_start:] if final_start >= 0 else ""
    result_match = re.search(r"^- Result:\s*(\S+)\s*$", final_text, re.MULTILINE)
    final_result = result_match.group(1) if result_match else ""
    if not result_match:
        errors.append("final-validation section must declare Result")
    elif final_result not in VALID_FINAL_RESULTS:
        errors.append(f"invalid final Result {final_result!r}")

    if overall_status == "done" and not all_done:
        errors.append("Overall status done requires every task to be done")
    if final_result == "passed" and (overall_status != "done" or not all_done):
        errors.append("final Result passed requires Overall status done and every task done")
    if overall_status == "done" and final_result != "passed":
        errors.append("Overall status done requires final Result passed")

    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create or validate evidence-driven Markdown task documents."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    create = subparsers.add_parser("create", help="Create a new collision-safe task document.")
    create.add_argument("--root", type=Path, default=Path.cwd())
    create.add_argument("--title", required=True)
    create.add_argument("--slug")
    create.add_argument("--mode", choices=("plan", "execute"), required=True)

    validate = subparsers.add_parser("validate", help="Validate document structure and states.")
    validate.add_argument("--path", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        if args.command == "create":
            destination = create_document(args.root, args.title, args.slug, args.mode)
            print(destination)
            return 0

        errors = validate_document(args.path)
        if errors:
            for error in errors:
                print(f"error: {error}", file=sys.stderr)
            return 1
        print(f"Task document is valid: {args.path.expanduser().resolve()}")
        return 0
    except (OSError, UnicodeError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
