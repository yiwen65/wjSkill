#!/usr/bin/env python3
"""Validate the structural completeness of an EDRU asset directory.

This script checks file presence, JSONL syntax, selected Markdown headings,
and YAML syntax when PyYAML is available. It does not validate the truth of
repository claims or the quality of evidence.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Iterable

try:
    import yaml  # type: ignore
except Exception:
    yaml = None


COMMON_REQUIRED = [
    "manifest.yaml",
    "00-repository-passport.yaml",
    "01-system-overview.md",
    "02-technology-stack.yaml",
    "03-executable-topology.md",
    "04-module-map.yaml",
    "05-boundary-catalog.yaml",
    "08-evidence-ledger.jsonl",
    "09-claim-register.yaml",
    "10-hypotheses-and-unknowns.yaml",
    "15-readiness-report.md",
]

TAKEOVER_REQUIRED = [
    "06-data-and-state-map.md",
    "11-history-and-decisions.md",
    "12-risk-register.yaml",
    "14-validation-and-observability.md",
]

CHANGE_READY_REQUIRED = [
    "13-change-impact-matrix.md",
]

MARKDOWN_HEADINGS = {
    "01-system-overview.md": ["# 系统概览", "## 系统目标", "## 最高风险未知"],
    "15-readiness-report.md": ["# EDRU 仓库接管完成度报告", "## 最终四问", "## 门禁结果"],
}


def required_for_mode(mode: str) -> list[str]:
    result = list(COMMON_REQUIRED)
    if mode in {"takeover", "change-ready"}:
        result.extend(TAKEOVER_REQUIRED)
    if mode == "change-ready":
        result.extend(CHANGE_READY_REQUIRED)
    return result


def check_jsonl(path: Path) -> list[str]:
    errors: list[str] = []
    if not path.exists():
        return errors
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"{path}: line {number}: invalid JSON: {exc}")
            continue
        if not isinstance(record, dict):
            errors.append(f"{path}: line {number}: record must be an object")
            continue
        for field in ("id", "source_type", "locator", "summary", "revision"):
            if field not in record:
                errors.append(f"{path}: line {number}: missing field {field!r}")
    return errors


def check_yaml(path: Path) -> list[str]:
    if yaml is None or not path.exists():
        return []
    try:
        yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return [f"{path}: invalid YAML: {exc}"]
    return []


def check_markdown(path: Path, headings: Iterable[str]) -> list[str]:
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    return [f"{path}: missing heading {heading!r}" for heading in headings if heading not in text]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("asset_root", type=Path)
    parser.add_argument("--mode", choices=["survey", "takeover", "change-ready"], default="takeover")
    args = parser.parse_args()

    root: Path = args.asset_root
    errors: list[str] = []
    warnings: list[str] = []

    if not root.is_dir():
        print(f"ERROR: asset root does not exist or is not a directory: {root}", file=sys.stderr)
        return 2

    for relative in required_for_mode(args.mode):
        path = root / relative
        if not path.exists():
            errors.append(f"missing required asset: {relative}")

    critical_dir = root / "07-critical-paths"
    if args.mode in {"takeover", "change-ready"}:
        if not critical_dir.is_dir():
            errors.append("missing required directory: 07-critical-paths")
        elif not list(critical_dir.glob("*.md")):
            errors.append("07-critical-paths contains no Markdown path asset")

    errors.extend(check_jsonl(root / "08-evidence-ledger.jsonl"))

    for relative in required_for_mode(args.mode):
        if relative.endswith((".yaml", ".yml")):
            errors.extend(check_yaml(root / relative))

    for relative, headings in MARKDOWN_HEADINGS.items():
        errors.extend(check_markdown(root / relative, headings))

    if yaml is None:
        warnings.append("PyYAML not installed; YAML syntax was not checked")

    if errors:
        print("EDRU asset validation FAILED")
        for error in errors:
            print(f"- {error}")
    else:
        print("EDRU asset validation PASSED")

    for warning in warnings:
        print(f"WARNING: {warning}")

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
