# Project Learnings

## `skills/*` packaging — validate supported metadata before finalizing a Skill

- Wrong approach: Preserved unsupported `version` and `language` frontmatter fields and initially used a 22-character UI `short_description`.
- Why it failed: The official Skill validator accepts only its documented frontmatter keys, while `agents/openai.yaml` requires a 25–64 character short description.
- Recognition signal: `quick_validate.py` reports `Unexpected key(s) in SKILL.md frontmatter`, or a metadata length assertion falls outside 25–64 characters.
- Correct approach: Keep only supported frontmatter fields, preserve supported `agents/openai.yaml` policy fields, and size UI metadata to its documented bounds.
- Prevention: Run `python3 /Users/w/.codex/skills/.system/skill-creator/scripts/quick_validate.py <skill-dir>` and check UI string lengths immediately after metadata edits.
- Verified by: `skills/understand-repo` passed official validation after removing the unsupported fields and expanding `short_description` to 29 characters.

## `docs/tasks/*-task.md` — use the task-ledger completion enums exactly

- Wrong approach: Marked completed tasks as `Status: completed` and the final result as `pass`.
- Why it failed: `task_document.py` accepts `Status: done` for checked tasks and `Result: passed` when `Overall status: done`.
- Recognition signal: Validation reports `invalid Status 'completed'`, a checkbox/status mismatch, or `invalid final Result 'pass'`.
- Correct approach: Pair `### [x]` with `Status: done`, then close the document with `Overall status: done` and `Result: passed`.
- Prevention: Run `python3 /Users/w/.codex/skills/wjskill-plan-and-execute-tasks/scripts/task_document.py validate --path <task-document>` immediately after every task-status transition.
- Verified by: The understand-repo operations ledger passed after applying these exact enum values.

## `skills/code-performance` — give static-only diagnosis a real mode branch

- Wrong approach: Added generic cautions for missing runtime evidence while leaving reproduction, profiling, baseline, and A/B sections as the only executable workflow.
- Why it failed: Without an early mode gate and exit, a code-only request could still be pushed through the measured workflow or produce empty runtime sections.
- Recognition signal: The request forbids target execution, builds, benchmarks, profiling, or instrumentation, but the Skill still asks for measured baselines or before/after results.
- Correct approach: Select Static-only before the measured contract, route it to a dedicated reference, prohibit entry into the measured loop, and classify output as static facts, conditional risks, or unknowns.
- Prevention: Check that the static router precedes the measured workflow, defines a hard stop, forbids unmeasured runtime labels, and provides its own finding gate and report contract.
- Verified by: `skills/code-performance` passed official `quick_validate.py` plus targeted checks for routing order, hard-stop language, evidence classes, zero-finding behavior, and resolved references.
