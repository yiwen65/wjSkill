import importlib.util
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from test_loop_package import v3_spec


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "loop_package.py"
SPEC = importlib.util.spec_from_file_location("loop_package_interop", SCRIPT)
assert SPEC and SPEC.loader
loop_package = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(loop_package)


class PiLoopInteropTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        configured = os.environ.get("PI_LOOP_HARNESS_DIR")
        if not configured:
            raise unittest.SkipTest("set PI_LOOP_HARNESS_DIR to run Pi Loop interop")
        cls.pi_root = Path(configured).resolve()
        cls.pi_module = cls.pi_root / "dist" / "schema" / "workflow.js"
        cls.recommendation_module = cls.pi_root / "dist" / "recommendation.js"
        if not cls.pi_module.is_file():
            raise unittest.SkipTest("Pi Loop dist/schema/workflow.js is not built")
        if not cls.recommendation_module.is_file():
            raise unittest.SkipTest("Pi Loop dist/recommendation.js is not built")

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.workspace = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def run_pi_validator(self, package):
        script = """
import { pathToFileURL } from 'node:url';
const modulePath = pathToFileURL(process.argv[1]).href;
const recommendationPath = pathToFileURL(process.argv[2]).href;
const { validateWorkflowPackage } = await import(modulePath);
const { loadRuntimeRecommendation } = await import(recommendationPath);
const result = await validateWorkflowPackage(process.argv[3]);
const recommendation = await loadRuntimeRecommendation({
  loopDir: process.argv[3],
  loopId: result.state.loop_id,
  contractSha256: result.state.contract.sha256,
  definition: result.state.contract.definition,
});
process.stdout.write(JSON.stringify({ schema: result.state.schema_version, status: result.state.status, recommendation: recommendation?.status }));
"""
        result = subprocess.run(
            [
                "node",
                "--input-type=module",
                "-e",
                script,
                str(self.pi_module),
                str(self.recommendation_module),
                str(package),
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def test_python_package_validates_in_pi_and_pi_checkpoint_validates_in_python(self):
        package = loop_package.create_package(self.workspace, "interop-loop", v3_spec())
        self.assertEqual(
            self.run_pi_validator(package),
            {"schema": "3.0", "status": "ready", "recommendation": "needs_input"},
        )

        progress_entry = "\n## Interop checkpoint\n\n- Evidence: faux provider only.\n"
        state_path = package / "state.json"
        state = json.loads(state_path.read_text())
        hash_script = """
import { createHash } from 'node:crypto';
const value = `${process.argv[1]}\\0${process.argv[2]}`;
process.stdout.write(createHash('sha256').update(value, 'utf8').digest('hex'));
"""
        chained = subprocess.run(
            [
                "node",
                "--input-type=module",
                "-e",
                hash_script,
                state["progress_hash_chain"]["head_sha256"],
                progress_entry,
            ],
            text=True,
            capture_output=True,
            check=True,
        ).stdout
        with (package / "progress.md").open("a", encoding="utf-8") as handle:
            handle.write(progress_entry)
        state["progress_hash_chain"] = {
            "head_sha256": chained,
            "entries": state["progress_hash_chain"]["entries"] + 1,
        }
        state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n")
        loop_package.validate_package(package)
        self.assertEqual(self.run_pi_validator(package)["schema"], "3.0")


if __name__ == "__main__":
    unittest.main()
