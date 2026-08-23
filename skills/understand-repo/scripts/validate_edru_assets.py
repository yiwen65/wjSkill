#!/usr/bin/env python3
"""Validate the structural completeness of an EDRU asset directory.

This script checks file presence, operation/mode consistency, update lineage,
JSONL syntax, selected Markdown headings, and YAML syntax when PyYAML is
available. It does not validate the truth of repository claims, the quality of
evidence, or the completeness of an update's invalidation closure.
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

UPDATE_REQUIRED = [
    "16-update-summary.md",
]

MARKDOWN_HEADINGS = {
    "01-system-overview.md": ["# System Overview", "## System Goals", "## Highest-Risk Unknowns"],
    "15-readiness-report.md": [
        "# EDRU Repository Takeover Readiness Report",
        "## Final Four Questions",
        "## Gate Results",
    ],
    "16-update-summary.md": [
        "# EDRU Update Summary",
        "## Lineage",
        "## Invalidation and Retention",
        "## Strategy Decision",
        "## Validation Result",
    ],
}


def required_for(operation: str, mode: str) -> list[str]:
    result = list(COMMON_REQUIRED)
    if mode in {"takeover", "change-ready"}:
        result.extend(TAKEOVER_REQUIRED)
    if mode == "change-ready":
        result.extend(CHANGE_READY_REQUIRED)
    if operation == "update":
        result.extend(UPDATE_REQUIRED)
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


def load_manifest(path: Path) -> tuple[dict | None, list[str]]:
    if not path.exists() or yaml is None:
        return None, []
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return None, [f"{path}: invalid YAML: {exc}"]
    if not isinstance(value, dict):
        return None, [f"{path}: manifest root must be an object"]
    run = value.get("edru_run")
    if not isinstance(run, dict):
        return None, [f"{path}: missing object 'edru_run'"]
    return run, []


def resolve_dimensions(
    run: dict | None,
    requested_operation: str | None,
    requested_mode: str | None,
) -> tuple[str, str, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    manifest_operation = run.get("operation") if run else None
    manifest_mode = run.get("mode") if run else None

    if manifest_operation is None and run:
        warnings.append("manifest has no operation; treating it as a legacy create-era asset")
    elif manifest_operation not in {None, "create", "update"}:
        errors.append(f"manifest operation is invalid: {manifest_operation!r}")

    if manifest_mode not in {None, "survey", "takeover", "change-ready"}:
        errors.append(f"manifest mode is invalid: {manifest_mode!r}")

    operation = requested_operation or manifest_operation or "create"
    mode = requested_mode or manifest_mode or "takeover"

    if requested_operation and manifest_operation and requested_operation != manifest_operation:
        errors.append(
            f"CLI operation {requested_operation!r} does not match manifest operation {manifest_operation!r}"
        )
    if requested_mode and manifest_mode and requested_mode != manifest_mode:
        errors.append(f"CLI mode {requested_mode!r} does not match manifest mode {manifest_mode!r}")
    if operation == "update" and manifest_operation != "update":
        errors.append("update validation requires a schema-v2 manifest with operation: update")

    return operation, mode, errors, warnings


def check_current_manifest(run: dict) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    schema_version = run.get("schema_version")
    if schema_version == "1.0":
        warnings.append("schema-v1 manifest accepted as a legacy create-era asset; new runs should use v2")
        return errors, warnings
    if schema_version != "2.0":
        return ["manifest schema_version must be '2.0' for current runs"], warnings

    string_fields = ("run_id", "operation", "status", "mode", "asset_root", "history_root")
    for field in string_fields:
        if not isinstance(run.get(field), str) or not run[field].strip():
            errors.append(f"manifest edru_run.{field} must be a non-empty string")
    if run.get("status") not in {
        "in_progress",
        "blocked",
        "completed",
        "completed_with_unknowns",
    }:
        errors.append("manifest status is invalid")
    if not isinstance(run.get("scope"), dict):
        errors.append("manifest edru_run.scope must be an object")
    repository = run.get("repository")
    if not isinstance(repository, dict):
        errors.append("manifest edru_run.repository must be an object")
    else:
        for field in ("path_or_url", "revision"):
            if not isinstance(repository.get(field), str) or not repository[field].strip():
                errors.append(f"manifest edru_run.repository.{field} must be a non-empty string")
    return errors, warnings


def check_update_manifest(root: Path, run: dict) -> list[str]:
    errors: list[str] = []
    required_run_fields = ("parent_run_id", "history_root")
    for field in required_run_fields:
        if not isinstance(run.get(field), str) or not run[field].strip():
            errors.append(f"manifest edru_run.{field} must be a non-empty string for update")

    if run.get("schema_version") != "2.0":
        errors.append("update manifest schema_version must be '2.0'")

    repository = run.get("repository")
    if not isinstance(repository, dict):
        errors.append("manifest edru_run.repository must be an object for update")
        repository = {}

    update = run.get("update")
    if not isinstance(update, dict):
        errors.append("manifest edru_run.update must be an object for update")
        return errors

    string_fields = ("previous_manifest", "trigger", "strategy", "from_revision", "to_revision", "ancestry")
    for field in string_fields:
        if not isinstance(update.get(field), str) or not update[field].strip():
            errors.append(f"manifest edru_run.update.{field} must be a non-empty string")

    array_fields = (
        "changed_paths",
        "changed_envelope_dimensions",
        "retained_assets",
        "preserved_parent_assets",
        "invalidated_claim_ids",
        "invalidated_evidence_ids",
        "superseded_evidence_ids",
        "regenerated_assets",
    )
    for field in array_fields:
        if not isinstance(update.get(field), list):
            errors.append(f"manifest edru_run.update.{field} must be an array")

    if update.get("trigger") not in {"manual", "revision_change", "envelope_change", "mixed"}:
        errors.append("manifest update trigger is invalid")
    if update.get("strategy") not in {"no_op", "incremental", "full_rebaseline"}:
        errors.append("manifest update strategy is invalid")
    if update.get("ancestry") not in {"ancestor", "diverged", "rewritten", "unknown"}:
        errors.append("manifest update ancestry is invalid")
    if update.get("strategy") == "full_rebaseline" and not str(update.get("fallback_reason", "")).strip():
        errors.append("full_rebaseline update requires a non-empty fallback_reason")
    if update.get("strategy") == "no_op":
        for field in (
            "changed_paths",
            "changed_envelope_dimensions",
            "invalidated_claim_ids",
            "invalidated_evidence_ids",
            "superseded_evidence_ids",
            "regenerated_assets",
        ):
            if update.get(field):
                errors.append(f"no_op update requires edru_run.update.{field} to be empty")
    if update.get("to_revision") and update.get("to_revision") != repository.get("revision"):
        errors.append("manifest update.to_revision must match repository.revision")

    previous_manifest = update.get("previous_manifest")
    previous_path: Path | None = None
    if isinstance(previous_manifest, str) and previous_manifest.strip():
        previous_path = Path(previous_manifest)
        if previous_path.is_absolute() or ".." in previous_path.parts:
            errors.append("manifest update.previous_manifest must be a safe path relative to asset_root")
        elif not (root / previous_path).is_file():
            errors.append(f"preserved parent manifest does not exist: {previous_manifest}")

    history_root = run.get("history_root")
    if isinstance(history_root, str) and history_root.strip():
        history_path = Path(history_root)
        if history_path.is_absolute() or ".." in history_path.parts:
            errors.append("manifest history_root must be a safe path relative to asset_root")
        elif not (root / history_path).is_dir():
            errors.append(f"history root does not exist: {history_root}")
        elif previous_path is not None and previous_path.parts[: len(history_path.parts)] != history_path.parts:
            errors.append("manifest update.previous_manifest must be located under history_root")

    preserved_assets = update.get("preserved_parent_assets")
    if isinstance(preserved_assets, list):
        if previous_manifest not in preserved_assets:
            errors.append("manifest update.preserved_parent_assets must include previous_manifest")
        for relative in preserved_assets:
            if not isinstance(relative, str) or not relative.strip():
                errors.append("manifest update.preserved_parent_assets entries must be non-empty strings")
                continue
            preserved_path = Path(relative)
            if preserved_path.is_absolute() or ".." in preserved_path.parts:
                errors.append(f"preserved parent asset path is unsafe: {relative}")
            elif not (root / preserved_path).is_file():
                errors.append(f"preserved parent asset does not exist: {relative}")
            elif isinstance(history_root, str):
                history_path = Path(history_root)
                if preserved_path.parts[: len(history_path.parts)] != history_path.parts:
                    errors.append(f"preserved parent asset must be under history_root: {relative}")

    if repository.get("dirty_worktree") is True and not str(
        repository.get("working_tree_fingerprint", "")
    ).strip():
        errors.append("dirty update snapshot requires repository.working_tree_fingerprint")

    if previous_path is not None and (root / previous_path).is_file() and yaml is not None:
        parent_run, parent_errors = load_manifest(root / previous_path)
        errors.extend(f"parent {error}" for error in parent_errors)
        if parent_run is not None:
            parent_repository = parent_run.get("repository")
            if run.get("parent_run_id") != parent_run.get("run_id"):
                errors.append("manifest parent_run_id must match the preserved parent manifest run_id")
            if not isinstance(parent_repository, dict):
                errors.append("preserved parent manifest repository must be an object")
            else:
                if parent_repository.get("path_or_url") != repository.get("path_or_url"):
                    errors.append("current and parent manifests must identify the same repository")
                if update.get("from_revision") != parent_repository.get("revision"):
                    errors.append("manifest update.from_revision must match the parent repository.revision")

    return errors


def check_markdown(path: Path, headings: Iterable[str]) -> list[str]:
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    return [f"{path}: missing heading {heading!r}" for heading in headings if heading not in text]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("asset_root", type=Path)
    parser.add_argument("--operation", choices=["create", "update"])
    parser.add_argument("--mode", choices=["survey", "takeover", "change-ready"])
    args = parser.parse_args()

    root: Path = args.asset_root
    errors: list[str] = []
    warnings: list[str] = []

    if not root.is_dir():
        print(f"ERROR: asset root does not exist or is not a directory: {root}", file=sys.stderr)
        return 2

    run, manifest_errors = load_manifest(root / "manifest.yaml")
    errors.extend(manifest_errors)
    operation, mode, dimension_errors, dimension_warnings = resolve_dimensions(
        run, args.operation, args.mode
    )
    errors.extend(dimension_errors)
    warnings.extend(dimension_warnings)

    if run is not None:
        current_errors, current_warnings = check_current_manifest(run)
        errors.extend(current_errors)
        warnings.extend(current_warnings)

    if operation == "update" and run is not None:
        errors.extend(check_update_manifest(root, run))

    required_assets = required_for(operation, mode)
    for relative in required_assets:
        path = root / relative
        if not path.exists():
            errors.append(f"missing required asset: {relative}")

    critical_dir = root / "07-critical-paths"
    if mode in {"takeover", "change-ready"}:
        if not critical_dir.is_dir():
            errors.append("missing required directory: 07-critical-paths")
        elif not list(critical_dir.glob("*.md")):
            errors.append("07-critical-paths contains no Markdown path asset")

    errors.extend(check_jsonl(root / "08-evidence-ledger.jsonl"))

    for relative in required_assets:
        if relative.endswith((".yaml", ".yml")):
            errors.extend(check_yaml(root / relative))

    for relative, headings in MARKDOWN_HEADINGS.items():
        errors.extend(check_markdown(root / relative, headings))

    if yaml is None:
        warnings.append("PyYAML not installed; YAML syntax and manifest lifecycle semantics were not checked")

    if errors:
        print("EDRU asset validation FAILED")
        for error in errors:
            print(f"- {error}")
    else:
        print(f"EDRU asset validation PASSED (operation={operation}, mode={mode})")

    for warning in warnings:
        print(f"WARNING: {warning}")

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
