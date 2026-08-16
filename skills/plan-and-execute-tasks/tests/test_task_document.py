from __future__ import annotations

from datetime import date
import importlib.util
from pathlib import Path
import tempfile
import unittest


SCRIPT = Path(__file__).parents[1] / "scripts" / "task_document.py"
SPEC = importlib.util.spec_from_file_location("task_document", SCRIPT)
assert SPEC and SPEC.loader
task_document = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(task_document)


def task_block(
    task_id: str = "T-001",
    status: str = "pending",
    checked: str = " ",
    dependencies: str = "None.",
) -> str:
    evidence = "python -m unittest: passed." if status in {"done", "blocked"} else "Not run."
    blocker = "Missing approved API access." if status == "blocked" else "None."
    unblock = "User grants API access." if status == "blocked" else "None."
    return f"""### [{checked}] {task_id} — Implement bounded change

- Status: {status}
- Owner: coordinator
- Objective: Implement the requested bounded behavior.
- Inputs and prerequisites: Confirmed repository state.
- Scope or files: src/example.py
- Expected output: Working implementation.
- Dependencies: {dependencies}
- Execution steps:
  1. Make the bounded change.
- Acceptance criteria:
  - Requested behavior is observable.
- Verification method:
  - Run the targeted test.
- Validation evidence: {evidence}
- Blocker: {blocker}
- Unblock condition: {unblock}
"""


def valid_document(status: str = "pending", checked: str = " ") -> str:
    sections: list[str] = []
    for marker in task_document.SECTION_MARKERS:
        section = f"<!-- task-doc-section:{marker} -->\n## {marker}\n\nRecorded."
        if marker == "task-list":
            section += "\n\n" + task_block(status=status, checked=checked)
        if marker == "final-validation":
            result = "passed" if status == "done" else "partial"
            section += f"\n\n- Result: {result}"
        sections.append(section)
    overall = "done" if status == "done" else "pending"
    return (
        f"# Task Plan: Example\n\n- Overall status: {overall}\n\n"
        + "\n\n".join(sections)
        + "\n"
    )


class TaskDocumentTest(unittest.TestCase):
    def test_create_is_collision_safe(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            first = task_document.create_document(root, "API Health", "api-health", "plan")
            first_body = first.read_text(encoding="utf-8")
            second = task_document.create_document(root, "API Health", "api-health", "plan")

            prefix = f"{date.today().isoformat()}-api-health"
            self.assertEqual(first.name, f"{prefix}-task.md")
            self.assertEqual(second.name, f"{prefix}-2-task.md")
            self.assertEqual(first.read_text(encoding="utf-8"), first_body)

    def test_valid_pending_and_done_documents(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "task.md"
            path.write_text(valid_document(), encoding="utf-8")
            self.assertEqual(task_document.validate_document(path), [])
            path.write_text(valid_document(status="done", checked="x"), encoding="utf-8")
            self.assertEqual(task_document.validate_document(path), [])

    def test_rejects_unverified_done_and_bad_dependency(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "task.md"
            body = valid_document(status="done", checked="x").replace(
                "python -m unittest: passed.", "Not run."
            ).replace("Dependencies: None.", "Dependencies: T-999")
            path.write_text(body, encoding="utf-8")
            errors = task_document.validate_document(path)
            self.assertTrue(any("requires actual validation evidence" in error for error in errors))
            self.assertTrue(any("dependency T-999 does not exist" in error for error in errors))

    def test_blocked_requires_reason_evidence_and_unblock_condition(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "task.md"
            body = valid_document(status="blocked").replace(
                "Missing approved API access.", "None."
            ).replace("User grants API access.", "None.")
            path.write_text(body, encoding="utf-8")
            errors = task_document.validate_document(path)
            self.assertTrue(any("requires a concrete Blocker" in error for error in errors))
            self.assertTrue(any("requires a concrete Unblock condition" in error for error in errors))

    def test_rejects_dependency_cycle(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "task.md"
            body = valid_document().replace(
                "- Dependencies: None.", "- Dependencies: T-002", 1
            )
            second = task_block(task_id="T-002", dependencies="T-001")
            body = body.replace(
                "<!-- task-doc-section:validation-plan -->", second + "\n\n<!-- task-doc-section:validation-plan -->"
            )
            path.write_text(body, encoding="utf-8")
            errors = task_document.validate_document(path)
            self.assertTrue(any("dependency cycle" in error for error in errors))

    def test_rejects_false_overall_completion(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "task.md"
            body = valid_document().replace("Overall status: pending", "Overall status: done")
            body = body.replace("Result: partial", "Result: passed")
            path.write_text(body, encoding="utf-8")
            errors = task_document.validate_document(path)
            self.assertTrue(any("requires every task to be done" in error for error in errors))
            self.assertTrue(any("Result passed requires" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
