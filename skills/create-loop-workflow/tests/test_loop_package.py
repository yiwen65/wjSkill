import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "loop_package.py"
SPEC = importlib.util.spec_from_file_location("loop_package", SCRIPT)
assert SPEC and SPEC.loader
loop_package = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(loop_package)


def v3_spec(template_version=1):
    return {
        "schema_version": "3.0",
        "title": "Test workflow",
        "template": {"id": "test-workflow", "version": template_version},
        "language": "en",
        "domain": "coding",
        "execution_mode": "sequential",
        "goal": "Produce and verify a bounded artifact.",
        "audience": "Maintainers",
        "inputs": ["Repository files"],
        "input_schema": [
            {
                "name": "repository",
                "type": "path",
                "description": "Target repository",
                "required": True,
            }
        ],
        "input_bindings": {"repository": "/tmp/project"},
        "invariants": ["Do not weaken tests."],
        "conditions": [
            {
                "id": "artifact-valid",
                "description": "The artifact passes deterministic validation.",
                "evidence_requirement_ids": ["artifact-check"],
            }
        ],
        "evidence_requirements": [
            {
                "id": "artifact-check",
                "type": "deterministic",
                "description": "Run the declared artifact validator.",
            }
        ],
        "initial_graph": {
            "nodes": [
                {
                    "id": "prepare",
                    "title": "Prepare",
                    "description": "Prepare the artifact.",
                    "input_ports": [],
                    "output_ports": [
                        {
                            "id": "artifact",
                            "type": "artifact",
                            "description": "Prepared artifact",
                        }
                    ],
                    "acceptance_criteria": ["Artifact exists."],
                    "resource_keys": ["workspace"],
                    "max_attempts": 3,
                    "no_progress_limit": 2,
                },
                {
                    "id": "verify",
                    "title": "Verify",
                    "description": "Verify the artifact.",
                    "input_ports": [
                        {
                            "id": "candidate",
                            "type": "artifact",
                            "description": "Candidate artifact",
                            "required": True,
                        }
                    ],
                    "output_ports": [
                        {
                            "id": "evidence",
                            "type": "evidence",
                            "description": "Validation evidence",
                        }
                    ],
                    "acceptance_criteria": ["Validator passes."],
                    "resource_keys": ["workspace"],
                    "max_attempts": 2,
                    "no_progress_limit": 1,
                },
            ],
            "edges": [
                {
                    "id": "prepare-to-verify",
                    "from": {"node_id": "prepare", "port_id": "artifact"},
                    "to": {"node_id": "verify", "port_id": "candidate"},
                }
            ],
        },
        "authority": {
            "risk_level": "medium",
            "rules": [
                {
                    "authority_id": "read-workspace",
                    "effect": "allow",
                    "description": "Read files in the confirmed workspace.",
                },
                {
                    "authority_id": "external-write",
                    "effect": "approve",
                    "description": "Require approval for external writes.",
                },
                {
                    "authority_id": "publish-denied",
                    "effect": "deny",
                    "description": "Do not publish or deploy.",
                },
            ],
            "credential_policy": "Retrieve only named credentials at runtime; never store values.",
            "credential_env": ["TEST_RUNTIME_TOKEN"],
        },
        "limits": {
            "max_iterations": 8,
            "max_minutes": 120,
            "max_cost": None,
            "cost_currency": None,
            "max_total_tokens": 40000,
        },
        "checkpoint": {
            "required_triggers": ["task_evaluated", "before_context_reset"],
            "required_evidence": ["State and evidence references"],
        },
        "circuit_breakers": [
            {"id": "no-evidence", "signal": "no_new_evidence", "threshold": 2, "action": "block"},
            {"id": "attempt-limit", "signal": "task_attempts", "threshold": 3, "action": "fail"},
            {"id": "verifier-limit", "signal": "consecutive_verifier_failures", "threshold": 2, "action": "block"},
        ],
        "memory_policy": {
            "max_entries": 200,
            "retrieval_top_k": 8,
            "max_context_tokens": 2000,
        },
        "context_policy": {
            "estimator": "utf8_bytes",
            "fail_on_required_overflow": True,
            "role_token_budgets": {
                "planner": 3000,
                "worker": 5000,
                "evaluator": 3000,
                "final_evaluator": 2500,
            },
        },
    }


def v2_spec():
    spec = v3_spec()
    return {
        "schema_version": "2.0",
        "title": spec["title"],
        "template": spec["template"],
        "language": spec["language"],
        "domain": spec["domain"],
        "execution_mode": spec["execution_mode"],
        "goal": spec["goal"],
        "audience": spec["audience"],
        "inputs": spec["inputs"],
        "input_schema": spec["input_schema"],
        "input_bindings": spec["input_bindings"],
        "invariants": spec["invariants"],
        "done_conditions": ["Artifact validator passes."],
        "tasks": [
            {
                "id": "prepare",
                "title": "Prepare",
                "description": "Prepare the artifact.",
                "dependencies": [],
                "acceptance_criteria": ["Artifact exists."],
            }
        ],
        "verification": ["Run artifact validator."],
        "authority": {
            "risk_level": "medium",
            "auto_allowed": ["Read workspace files."],
            "approval_required": ["External write."],
            "forbidden": ["Publish."],
            "credential_policy": "Never store secret values.",
        },
        "limits": {"max_iterations": 8, "max_minutes": 120, "max_cost": None, "cost_currency": None},
        "checkpoint": {"frequency": "after each task", "required_evidence": ["State"]},
        "stop_conditions": ["Stop at a hard limit."],
    }


def recommendation():
    return {
        "policy": {
            "allow": [
                {"authority_id": "read-workspace", "tool": "read", "targets": ["workspace://."]}
            ],
            "approve": [
                {
                    "authority_id": "external-write",
                    "tool": "shell_argv",
                    "targets": ["workspace://."],
                    "argv_prefix": ["npm", "test"],
                }
            ],
            "deny": [{"authority_id": "publish-denied", "tool": "*"}],
        },
        "verifiers": [
            {
                "id": "artifact-check",
                "type": "command",
                "requirement_id": "artifact-check",
                "argv": ["npm", "test"],
            }
        ],
        "inference_manifest": [
            {
                "path": "/verifiers/artifact-check",
                "status": "inferred",
                "confidence": "high",
                "source_refs": [
                    {
                        "uri": "repo://package.json#scripts.test",
                        "digest": "a" * 64,
                    }
                ],
                "rationale": "Repository test script is deterministic.",
            },
            {
                "path": "/policy/allow/read-workspace",
                "status": "inferred",
                "confidence": "high",
                "source_refs": [
                    {"uri": "repo://", "digest": "b" * 64}
                ],
                "rationale": "The confirmed repository is the read scope.",
            },
            {
                "path": "/policy/approve/external-write",
                "status": "inferred",
                "confidence": "medium",
                "source_refs": [
                    {"uri": "repo://package.json#scripts.test", "digest": "a" * 64}
                ],
                "rationale": "The repository test command is approval scoped.",
            },
        ],
    }


class LoopPackageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.workspace = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def test_create_v3_has_canonical_initial_state(self):
        path = loop_package.create_package(self.workspace, "test-loop", v3_spec())
        loop_package.validate_package(path)
        state = json.loads((path / "state.json").read_text())
        self.assertEqual(state["schema_version"], "3.0")
        self.assertEqual(
            set(state),
            {
                "schema_version",
                "loop_id",
                "status",
                "contract",
                "iteration",
                "usage",
                "active_task_ids",
                "tasks",
                "completion_evidence",
                "pending_approval",
                "last_checkpoint",
                "started_at",
                "updated_at",
                "node_outputs",
                "condition_coverage",
                "breaker_counters",
                "memory_index_head",
                "progress_hash_chain",
                "handoff_sha256",
            },
        )
        self.assertEqual([task["id"] for task in state["tasks"]], ["prepare", "verify"])
        self.assertEqual(state["tasks"][1]["dependencies"], ["prepare"])
        self.assertEqual(state["node_outputs"], [])
        self.assertEqual(state["memory_index_head"], None)
        self.assertEqual(state["progress_hash_chain"]["entries"], 1)
        self.assertEqual(
            state["progress_hash_chain"]["head_sha256"],
            loop_package.progress_chain_next(None, (path / "progress.md").read_text()),
        )
        self.assertEqual(state["condition_coverage"][0]["requirement_results"][0]["result"], "pending")
        self.assertRegex(state["handoff_sha256"], r"^[0-9a-f]{64}$")

    def test_runtime_recommendation_is_generated_validated_and_rebound(self):
        spec = v3_spec()
        spec["runtime_recommendation"] = recommendation()
        path = loop_package.create_package(self.workspace, "recommended-loop", spec)
        loop_package.validate_package(path)
        value = json.loads((path / "runtime-recommendation.json").read_text())
        state = json.loads((path / "state.json").read_text())
        self.assertEqual(value["status"], "complete")
        self.assertEqual(value["contract_sha256"], state["contract"]["sha256"])
        self.assertEqual(value["models"]["planner"]["min_context_tokens"], 14096)
        self.assertEqual(loop_package.auto_budget(spec)["max_iterations"], 5)

        value["contract_sha256"] = "0" * 64
        (path / "runtime-recommendation.json").write_text(json.dumps(value) + "\n")
        with self.assertRaisesRegex(loop_package.ValidationError, "contract_sha256 is stale"):
            loop_package.validate_package(path)

        value["contract_sha256"] = state["contract"]["sha256"]
        (path / "runtime-recommendation.json").write_text(json.dumps(value, indent=2) + "\n")
        instance = loop_package.instantiate_package(
            path,
            self.workspace,
            "recommended-instance",
            {
                "input_bindings": {"repository": "/tmp/instance"},
                "runtime_recommendation": recommendation(),
            },
        )
        instance_value = json.loads((instance / "runtime-recommendation.json").read_text())
        self.assertEqual(instance_value["loop_id"], "recommended-instance")
        self.assertNotEqual(instance_value["contract_sha256"], state["contract"]["sha256"])
        conservative_instance = loop_package.instantiate_package(
            path,
            self.workspace,
            "recommended-needs-refresh",
            {"input_bindings": {"repository": "/tmp/other-instance"}},
        )
        conservative_value = json.loads(
            (conservative_instance / "runtime-recommendation.json").read_text()
        )
        self.assertEqual(conservative_value["status"], "needs_input")
        self.assertEqual(conservative_value["inference_manifest"][0]["source_refs"], [])

    def test_default_recommendation_reports_only_blocking_gaps(self):
        path = loop_package.create_package(self.workspace, "needs-input", v3_spec())
        value = json.loads((path / "runtime-recommendation.json").read_text())
        self.assertEqual(value["status"], "needs_input")
        paths = {entry["path"] for entry in value["inference_manifest"]}
        self.assertIn("/verifiers/artifact-check", paths)
        self.assertIn("/policy/allow/read-workspace", paths)
        self.assertIn("/policy/approve/external-write", paths)

    def test_contract_hash_is_stable_across_instances_with_same_binding(self):
        first = loop_package.create_package(self.workspace, "stable-one", v3_spec())
        other_workspace = self.workspace / "other"
        other_workspace.mkdir()
        second = loop_package.create_package(other_workspace, "stable-two", v3_spec())
        first_state = json.loads((first / "state.json").read_text())
        second_state = json.loads((second / "state.json").read_text())
        self.assertEqual(first_state["contract"]["sha256"], second_state["contract"]["sha256"])
        self.assertNotEqual(first_state["contract"]["workflow_sha256"], second_state["contract"]["workflow_sha256"])

    def test_condition_cannot_rely_only_on_independent_evaluator(self):
        spec = v3_spec()
        spec["evidence_requirements"][0]["type"] = "independent_evaluator"
        with self.assertRaisesRegex(loop_package.ValidationError, "deterministic or human"):
            loop_package.normalize_v3_spec(spec, "test-loop")

    def test_nullable_token_limit_arbitrary_checkpoint_and_repeated_signal_are_valid(self):
        spec = v3_spec()
        spec["limits"]["max_total_tokens"] = None
        spec["checkpoint"]["required_triggers"] = ["after_evaluation"]
        spec["circuit_breakers"].append(
            {"id": "no-evidence-fail", "signal": "no_new_evidence", "threshold": 5, "action": "fail"}
        )
        normalized = loop_package.normalize_v3_spec(spec, "test-loop")
        self.assertIsNone(normalized["limits"]["max_total_tokens"])
        self.assertEqual(normalized["checkpoint"]["required_triggers"], ["after_evaluation"])
        self.assertEqual(normalized["authority"]["credential_env"], ["TEST_RUNTIME_TOKEN"])
        spec["checkpoint"]["required_triggers"] = ["after_evaluation", "after_evaluation"]
        with self.assertRaisesRegex(loop_package.ValidationError, "contains duplicates"):
            loop_package.normalize_v3_spec(spec, "test-loop")

    def test_technical_defaults_use_the_published_budget_and_breaker_formula(self):
        spec = v3_spec()
        for field in (
            "limits",
            "checkpoint",
            "circuit_breakers",
            "memory_policy",
            "context_policy",
        ):
            spec.pop(field)
        for node in spec["initial_graph"]["nodes"]:
            node.pop("max_attempts")
            node.pop("no_progress_limit")
            node.pop("resource_keys")
        normalized = loop_package.normalize_v3_spec(spec, "test-loop")
        self.assertEqual([node["max_attempts"] for node in normalized["initial_graph"]["nodes"]], [2, 2])
        self.assertEqual(normalized["limits"]["max_iterations"], 4)
        self.assertEqual(normalized["limits"]["max_minutes"], 75)
        self.assertEqual(normalized["limits"]["max_total_tokens"], 165000)
        self.assertEqual(
            normalized["context_policy"]["role_token_budgets"],
            {"planner": 10000, "worker": 20000, "evaluator": 9000, "final_evaluator": 9000},
        )
        self.assertEqual(
            normalized["checkpoint"]["required_triggers"],
            ["task_evaluated", "before_context_reset", "approval_resolved"],
        )
        self.assertEqual(
            [(item["signal"], item["threshold"], item["action"]) for item in normalized["circuit_breakers"]],
            [
                ("no_new_evidence", 2, "block"),
                ("consecutive_verifier_failures", 3, "block"),
                ("tool_failures", 3, "fail"),
                ("approval_denials", 1, "block"),
            ],
        )

    def test_graph_rejects_cycle_and_type_mismatch(self):
        mismatch = v3_spec()
        mismatch["initial_graph"]["nodes"][1]["input_ports"][0]["type"] = "json"
        with self.assertRaisesRegex(loop_package.ValidationError, "incompatible"):
            loop_package.normalize_v3_spec(mismatch, "test-loop")
        cycle = v3_spec()
        cycle["initial_graph"]["nodes"][0]["input_ports"] = [
            {"id": "feedback", "type": "evidence", "description": "Feedback", "required": True}
        ]
        cycle["initial_graph"]["edges"].append(
            {
                "id": "verify-to-prepare",
                "from": {"node_id": "verify", "port_id": "evidence"},
                "to": {"node_id": "prepare", "port_id": "feedback"},
            }
        )
        with self.assertRaisesRegex(loop_package.ValidationError, "cycle"):
            loop_package.normalize_v3_spec(cycle, "test-loop")

    def test_running_node_requires_digested_inputs_and_completed_node_outputs(self):
        spec = v3_spec()
        spec["execution_mode"] = "parallel"
        path = loop_package.create_package(self.workspace, "runtime-graph", spec)
        state_path = path / "state.json"
        state = json.loads(state_path.read_text())
        state["status"] = "running"
        state["tasks"][1]["status"] = "in_progress"
        state["active_task_ids"] = ["verify"]
        state_path.write_text(json.dumps(state, indent=2) + "\n")
        with self.assertRaisesRegex(loop_package.ValidationError, "digested upstream output"):
            loop_package.validate_package(path)

        state["tasks"][0]["status"] = "completed"
        state["tasks"][0]["evidence"] = ["evidence://prepare/check"]
        state["tasks"][1]["status"] = "completed"
        state["tasks"][1]["evidence"] = ["evidence://verify/check"]
        state["active_task_ids"] = []
        state["node_outputs"] = [
            {
                "node_id": "prepare",
                "port_id": "artifact",
                "uri": "evidence://prepare/artifact",
                "digest": "a" * 64,
                "evidence_refs": ["evidence://prepare/check"],
                "summary": "Prepared artifact with verified checksum.",
                "produced_at": "2026-08-16T00:00:00Z",
            }
        ]
        state_path.write_text(json.dumps(state, indent=2) + "\n")
        with self.assertRaisesRegex(loop_package.ValidationError, "missing output evidence"):
            loop_package.validate_package(path)

        state["tasks"][0]["status"] = "in_progress"
        state["tasks"][1]["status"] = "in_progress"
        state["active_task_ids"] = ["prepare", "verify"]
        state_path.write_text(json.dumps(state, indent=2) + "\n")
        with self.assertRaisesRegex(loop_package.ValidationError, "share resource key"):
            loop_package.validate_package(path)

    def test_create_refuses_overwrite_and_instantiate_is_fresh(self):
        source = loop_package.create_package(self.workspace, "source-loop", v3_spec())
        with self.assertRaisesRegex(loop_package.ValidationError, "already exists"):
            loop_package.create_package(self.workspace, "source-loop", v3_spec())
        instance = loop_package.instantiate_package(
            source, self.workspace, "instance-loop", {"input_bindings": {"repository": "/tmp/next"}}
        )
        state = json.loads((instance / "state.json").read_text())
        self.assertEqual(state["status"], "ready")
        self.assertEqual(state["contract"]["definition"]["input_bindings"]["repository"], "/tmp/next")
        self.assertNotEqual(
            state["contract"]["definition"]["input_bindings_sha256"],
            json.loads((source / "state.json").read_text())["contract"]["definition"]["input_bindings_sha256"],
        )

    def test_v2_and_v1_validation_remain_supported(self):
        path = loop_package.create_package(self.workspace, "legacy-loop", v2_spec())
        loop_package.validate_package(path)
        state_path = path / "state.json"
        state = json.loads(state_path.read_text())
        definition = state["contract"]["definition"]
        for key in ("title", "template", "input_schema", "input_bindings", "input_bindings_sha256", "initial_tasks"):
            definition.pop(key)
        state["schema_version"] = "1.0"
        state["contract"]["sha256"] = loop_package.sha256_bytes(loop_package.canonical_json(definition))
        state_path.write_text(json.dumps(state, indent=2) + "\n")
        loop_package.validate_package(path)

    def test_migrate_plan_is_read_only_and_migrate_creates_fresh_v3(self):
        source = loop_package.create_package(self.workspace, "legacy-loop", v2_spec())
        before = (source / "state.json").read_bytes()
        plan = loop_package.migration_plan(source)
        self.assertEqual(plan["source_schema_version"], "2.0")
        self.assertTrue(plan["unresolved"])
        self.assertEqual((source / "state.json").read_bytes(), before)
        target = loop_package.migrate_package(
            source,
            self.workspace,
            "migrated-loop",
            {"specification": v3_spec()},
        )
        loop_package.validate_package(target)
        self.assertEqual((source / "state.json").read_bytes(), before)

    def test_update_uses_cas_and_preserves_handoff(self):
        path = loop_package.create_package(self.workspace, "update-loop", v3_spec())
        before_state = json.loads((path / "state.json").read_text())
        handoff = (path / "handoff.md").read_bytes()
        (path / "runtime-evidence.json").write_text('{"kept":true}\n')
        changed = v3_spec()
        changed["goal"] = "Produce, verify, and document a bounded artifact."
        update = {
            "expected_contract_sha256": before_state["contract"]["sha256"],
            "specification": changed,
            "approval": {
                "approved_by": "test-owner",
                "approved_at": "2026-08-16T00:00:00Z",
                "rationale": "Add the confirmed documentation outcome.",
            },
        }
        loop_package.update_package(path, update)
        loop_package.validate_package(path)
        after_state = json.loads((path / "state.json").read_text())
        self.assertEqual(after_state["contract"]["version"], 2)
        before_progress = loop_package.render_progress(
            "update-loop", before_state["updated_at"], "en"
        )
        appended = (path / "progress.md").read_text()[len(before_progress):]
        self.assertEqual(
            after_state["progress_hash_chain"]["head_sha256"],
            loop_package.progress_chain_next(
                before_state["progress_hash_chain"]["head_sha256"], appended
            ),
        )
        self.assertTrue((path / "handoff.md").read_bytes().startswith(handoff))
        self.assertIn("Current goal", (path / "handoff.md").read_text())
        self.assertEqual((path / "runtime-evidence.json").read_text(), '{"kept":true}\n')
        self.assertIn("Contract update", (path / "progress.md").read_text())
        with self.assertRaisesRegex(loop_package.ValidationError, "does not match"):
            loop_package.update_package(path, update)

    def test_update_requires_template_bump_for_graph_change(self):
        path = loop_package.create_package(self.workspace, "update-loop", v3_spec())
        state = json.loads((path / "state.json").read_text())
        changed = v3_spec()
        changed["initial_graph"]["nodes"][0]["description"] = "Changed blueprint."
        update = {
            "expected_contract_sha256": state["contract"]["sha256"],
            "specification": changed,
            "approval": {
                "approved_by": "test-owner",
                "approved_at": "2026-08-16T00:00:00Z",
                "rationale": "Change blueprint.",
            },
        }
        with self.assertRaisesRegex(loop_package.ValidationError, "template.version"):
            loop_package.update_package(path, update)

    def test_failed_update_rolls_back_original_package(self):
        path = loop_package.create_package(self.workspace, "rollback-loop", v3_spec())
        before = {name: (path / name).read_bytes() for name in loop_package.REQUIRED_FILES}
        state = json.loads((path / "state.json").read_text())
        changed = v3_spec()
        changed["goal"] = "A changed goal that will not be installed."
        update = {
            "expected_contract_sha256": state["contract"]["sha256"],
            "specification": changed,
            "approval": {
                "approved_by": "test-owner",
                "approved_at": "2026-08-16T00:00:00Z",
                "rationale": "Exercise rollback.",
            },
        }
        original_validate = loop_package.validate_package
        calls = {"count": 0}

        def fail_staging(candidate):
            calls["count"] += 1
            if calls["count"] == 2:
                raise loop_package.ValidationError("injected staging failure")
            return original_validate(candidate)

        loop_package.validate_package = fail_staging
        try:
            with self.assertRaisesRegex(loop_package.ValidationError, "injected"):
                loop_package.update_package(path, update)
        finally:
            loop_package.validate_package = original_validate
        for name, content in before.items():
            self.assertEqual((path / name).read_bytes(), content)
        original_validate(path)

    def test_cli_create_and_validate(self):
        created = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "create",
                "--workspace",
                str(self.workspace),
                "--slug",
                "cli-loop",
            ],
            input=json.dumps(v3_spec()),
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(created.returncode, 0, created.stderr)
        result = json.loads(created.stdout)
        self.assertFalse(result["started"])
        validated = subprocess.run(
            [sys.executable, str(SCRIPT), "validate", "--path", result["path"]],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(validated.returncode, 0, validated.stderr)


if __name__ == "__main__":
    unittest.main()
