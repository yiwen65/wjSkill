from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SKILL_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = SKILL_ROOT / "scripts" / "validate_edru_assets.py"

TEMPLATES = SKILL_ROOT / "templates"

COMMON = {
    "00-repository-passport.yaml": "repository-passport.yaml",
    "01-system-overview.md": "system-overview.md",
    "02-technology-stack.yaml": "technology-stack.yaml",
    "03-executable-topology.md": "executable-topology.md",
    "04-module-map.yaml": "module-map.yaml",
    "05-boundary-catalog.yaml": "boundary-catalog.yaml",
    "08-evidence-ledger.jsonl": "evidence-ledger.jsonl",
    "09-claim-register.yaml": "claim-register.yaml",
    "10-hypotheses-and-unknowns.yaml": "hypotheses-and-unknowns.yaml",
    "15-readiness-report.md": "readiness-report.md",
}

TAKEOVER = {
    "06-data-and-state-map.md": "data-and-state-map.md",
    "11-history-and-decisions.md": "history-and-decisions.md",
    "12-risk-register.yaml": "risk-register.yaml",
    "14-validation-and-observability.md": "validation-and-observability.md",
}


def create_manifest(
    mode: str = "survey", run_id: str = "EDRU-new", revision: str = "def456"
) -> str:
    return f"""edru_run:
  schema_version: "2.0"
  run_id: "{run_id}"
  operation: "create"
  parent_run_id: ""
  status: "completed"
  mode: "{mode}"
  repository:
    path_or_url: "/repo"
    revision: "{revision}"
  scope: {{}}
  asset_root: ".edru"
  history_root: "history"
"""


def update_manifest(mode: str = "takeover") -> str:
    return f"""edru_run:
  schema_version: "2.0"
  run_id: "EDRU-new"
  operation: "update"
  parent_run_id: "EDRU-old"
  status: "completed"
  mode: "{mode}"
  repository:
    path_or_url: "/repo"
    revision: "def456"
  scope: {{}}
  asset_root: ".edru"
  history_root: "history"
  update:
    previous_manifest: "history/EDRU-old/manifest.yaml"
    trigger: "revision_change"
    strategy: "incremental"
    from_revision: "abc123"
    to_revision: "def456"
    ancestry: "ancestor"
    changed_paths: ["parser.py"]
    changed_envelope_dimensions: []
    retained_assets: ["00-repository-passport.yaml"]
    preserved_parent_assets: ["history/EDRU-old/manifest.yaml"]
    invalidated_claim_ids: ["CLM-parser"]
    invalidated_evidence_ids: ["EV-parser-old"]
    superseded_evidence_ids: ["EV-parser-old"]
    regenerated_assets: ["03-executable-topology.md"]
    fallback_reason: ""
"""


def write_fixture(root: Path, manifest: str, mode: str, update: bool = False) -> None:
    for relative, template in COMMON.items():
        (root / relative).write_text((TEMPLATES / template).read_text(encoding="utf-8"), encoding="utf-8")
    if mode in {"takeover", "change-ready"}:
        for relative, template in TAKEOVER.items():
            (root / relative).write_text(
                (TEMPLATES / template).read_text(encoding="utf-8"), encoding="utf-8"
            )
        critical = root / "07-critical-paths"
        critical.mkdir()
        (critical / "KP-001.md").write_text(
            (TEMPLATES / "critical-path.md").read_text(encoding="utf-8"), encoding="utf-8"
        )
    if mode == "change-ready":
        (root / "13-change-impact-matrix.md").write_text(
            (TEMPLATES / "change-impact-matrix.md").read_text(encoding="utf-8"), encoding="utf-8"
        )
    if update:
        (root / "16-update-summary.md").write_text(
            (TEMPLATES / "update-summary.md").read_text(encoding="utf-8"), encoding="utf-8"
        )
        parent = root / "history" / "EDRU-old"
        parent.mkdir(parents=True)
        (parent / "manifest.yaml").write_text(
            create_manifest(mode, run_id="EDRU-old", revision="abc123"), encoding="utf-8"
        )
    (root / "manifest.yaml").write_text(manifest, encoding="utf-8")


def run_validator(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(VALIDATOR), str(root), *args],
        check=False,
        capture_output=True,
        text=True,
    )


class ValidateEdruAssetsTest(unittest.TestCase):
    def test_all_operation_mode_combinations_are_valid(self) -> None:
        for operation in ("create", "update"):
            for mode in ("survey", "takeover", "change-ready"):
                with self.subTest(operation=operation, mode=mode):
                    with tempfile.TemporaryDirectory() as directory:
                        root = Path(directory)
                        manifest = create_manifest(mode) if operation == "create" else update_manifest(mode)
                        write_fixture(root, manifest, mode, update=operation == "update")
                        result = run_validator(
                            root, "--operation", operation, "--mode", mode
                        )
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_valid_create_survey_is_inferred_from_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_fixture(root, create_manifest("survey"), "survey")
            result = run_validator(root)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("operation=create, mode=survey", result.stdout)

    def test_valid_update_takeover_requires_lineage_and_summary(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_fixture(root, update_manifest("takeover"), "takeover", update=True)
            result = run_validator(root, "--operation", "update", "--mode", "takeover")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("operation=update, mode=takeover", result.stdout)

    def test_update_fails_when_parent_manifest_was_not_preserved(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_fixture(root, update_manifest(), "takeover", update=True)
            (root / "history" / "EDRU-old" / "manifest.yaml").unlink()
            result = run_validator(root, "--operation", "update")
        self.assertEqual(result.returncode, 1)
        self.assertIn("preserved parent manifest does not exist", result.stdout)

    def test_update_fails_without_update_summary(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_fixture(root, update_manifest(), "takeover", update=True)
            (root / "16-update-summary.md").unlink()
            result = run_validator(root, "--operation", "update")
        self.assertEqual(result.returncode, 1)
        self.assertIn("missing required asset: 16-update-summary.md", result.stdout)

    def test_cli_operation_must_match_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_fixture(root, create_manifest("survey"), "survey")
            result = run_validator(root, "--operation", "update", "--mode", "survey")
        self.assertEqual(result.returncode, 1)
        self.assertIn("does not match manifest operation", result.stdout)

    def test_full_rebaseline_requires_reason(self) -> None:
        manifest = update_manifest().replace('strategy: "incremental"', 'strategy: "full_rebaseline"')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_fixture(root, manifest, "takeover", update=True)
            result = run_validator(root, "--operation", "update")
        self.assertEqual(result.returncode, 1)
        self.assertIn("requires a non-empty fallback_reason", result.stdout)

    def test_no_op_rejects_changed_or_regenerated_items(self) -> None:
        manifest = update_manifest().replace('strategy: "incremental"', 'strategy: "no_op"')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_fixture(root, manifest, "takeover", update=True)
            result = run_validator(root, "--operation", "update")
        self.assertEqual(result.returncode, 1)
        self.assertIn("no_op update requires edru_run.update.changed_paths to be empty", result.stdout)

    def test_from_revision_must_match_preserved_parent(self) -> None:
        manifest = update_manifest().replace('from_revision: "abc123"', 'from_revision: "wrong"')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_fixture(root, manifest, "takeover", update=True)
            result = run_validator(root, "--operation", "update")
        self.assertEqual(result.returncode, 1)
        self.assertIn("must match the parent repository.revision", result.stdout)

    def test_legacy_manifest_is_create_only_and_warns(self) -> None:
        legacy = create_manifest("survey").replace('schema_version: "2.0"', 'schema_version: "1.0"')
        legacy = legacy.replace('  operation: "create"\n', "")
        legacy = legacy.replace('  history_root: "history"\n', "")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_fixture(root, legacy, "survey")
            result = run_validator(root, "--operation", "create", "--mode", "survey")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("legacy create-era asset", result.stdout)


if __name__ == "__main__":
    unittest.main()
