---
name: create-loop-workflow
description: Create or instantiate durable, bounded, resumable loop workflow packages for long-running coding, research, content, and operations tasks. Use when the user asks to design, create, scaffold, formalize, reuse, or run again with new inputs an agent loop, Ralph loop, autonomous multi-session workflow, or checkpointed planner-worker-evaluator process. Infer technical evidence, graph, budgets, breakers, verifiers, permissions, and model needs from repository evidence; ask only for truly blocking user decisions, confirm one business summary, then generate and validate the package without executing it.
---

# Create Loop Workflow

Create a practical workflow package that another Codex session can run and
resume. Design the workflow; do not execute its target task.

## Preserve the creation boundary

- Inspect conversation context and the target workspace read-only before asking.
- Do not create or modify a loop package until the user confirms the recovered
  contract.
- After creation, validate the package and report its path. Do not start the loop.
- Treat confirmation of the workflow design as permission to create the package,
  not permission to perform the work it describes.
- Keep credentials and secret values out of questions, generated files, logs, and
  command output. Record only how an authorized runtime retrieves them.

## Recover the contract adaptively

Maintain a compact internal decision tree. Recover answers from the conversation,
supplied artifacts, and target workspace before questioning. Resolve or close
these material nodes:

- goal, intended outcome, audience, and target workspace;
- stable input parameter definitions, this instance's bindings, source-of-truth
  systems, environment, and available tools;
- explicit, externally testable completion conditions;
- initial work units and dependencies;
- planner, worker, and evaluator responsibilities;
- automatically allowed, approval-gated, and forbidden actions;
- user-stated hard time, cost, or operational constraints;
- language, loop slug, and output location.

Separate reusable rules from per-instance values. Give every changing input a
lowercase parameter name, type (`string`, `integer`, `number`, `boolean`, `path`,
or `uri`), description, and required flag. Bind the confirmed values for the new
instance; do not hide changing targets inside the goal, task text, or permission
prose. Never put secret values in bindings—store only the authorized runtime
reference mechanism.

## Infer technical details before asking

Inspect the confirmed target repository read-only before asking about technical
workflow fields. Prefer direct evidence in package scripts, Make/CMake/Bazel,
CI, test configuration, deployment configuration, and project documentation.
Read [references/loop-design.md](references/loop-design.md) for the inference
policy and Runtime Recommendation contract.

- Treat explicit user statements and direct repository evidence as high
  confidence.
- Treat a domain rule supported by repository evidence as medium confidence.
- Treat an unsupported heuristic as low confidence.
- Automatically use high- and medium-confidence evidence, graph ports, budgets,
  breakers, checkpoints, verifier mappings, permission scopes, and model needs.
- Ask only about low-confidence gaps that prevent a safe, runnable draft. Merge
  all independent blocking gaps into one structured interaction.
- Never ask the user to supply stable IDs, port types, token calculations,
  breaker thresholds, TOML, or verifier bindings directly.

For an information-complete coding workflow, permit at most two user decisions:
one consolidated blocking-gap response when necessary and one final business
summary confirmation. Never generate an unbounded loop.

## Confirm before writing

When every material node is resolved, present one concise business summary containing:

- goal and expected outcome;
- workspace, reusable input schema, this instance's bindings, and initial work
  units;
- completion standards in user language;
- major steps and role split;
- permission scope, credential boundary, and forbidden actions;
- aggregate time, token, and known cost limits;
- assumptions and explicit exclusions.

Keep evidence IDs, typed ports, breaker counters, verifier wire fields, and
Runtime TOML in an optional advanced section. Do not require the user to review
or edit them.

Request confirmation or revision. Treat only explicit confirmation as authority
to create the package. If the target directory already exists, inspect it and ask
the user to choose update, a new slug, or cancellation. Never silently overwrite.

For an update:

1. Read and validate the existing package.
2. Preserve `progress.md`, `handoff.md`, and all runtime evidence.
3. Show the proposed contract and state migration before editing.
4. Require explicit confirmation for the update.
5. Increase the contract version, recompute both hashes, append the approval and
   rationale to `progress.md`, and validate the updated package.

When changing reusable input definitions or the typed initial graph, also
increase `template.version`. An instance binding change creates a fresh instance;
never reset a completed or cancelled package.

## Design the workflow

Apply the already-read reference's core invariants and only the domain section
matching the request after confirmation and before materializing the package.

Always separate these responsibilities, even if one model performs them in fresh
roles:

- **Planner:** select or revise the next bounded work unit without performing it.
- **Worker:** execute one selected work unit and collect evidence without grading
  its own completion.
- **Evaluator:** compare evidence against the immutable completion conditions and
  decide pass, retry, replan, block, or complete.

Use independent agents only when subtasks are genuinely independent, merge and
permission boundaries are explicit, and parallelism provides material value.
Otherwise encode role separation within a sequential loop.

Keep the immutable template identity, input schema, instance bindings, typed
initial graph, evidence contract, goal, and safety contract in `WORKFLOW.md` and
its canonical machine snapshot in `state.json`. Allow runtime nodes, progress, evidence, and
handoffs to evolve. Require user approval before changing the goal, completion
conditions, invariants, authority, approval gates, or limits.

## Materialize a new package

Build a Schema v3 JSON specification following
[references/loop-design.md](references/loop-design.md). Resolve this Skill's
directory. Include stable conditions, evidence requirements, authority rules, a
typed bounded DAG, structured circuit breakers and checkpoints, memory/context
policies, `input_schema`, `input_bindings`, and a `runtime_recommendation` based
on repository evidence; `template` is optional and
defaults to the new slug at version 1. Pipe the JSON to:

```bash
python3 <skill-directory>/scripts/loop_package.py create \
  --workspace <absolute-workspace> \
  --slug <lowercase-hyphen-slug>
```

The command creates `<workspace>/.agent/loops/<slug>/` and returns its absolute
path. It refuses existing targets. Do not add overwrite flags or delete an
existing package to bypass that protection. Schema v3 is the default. Generate
legacy v2 only when the user explicitly requests it by setting
`"schema_version": "2.0"` and using the legacy v2 fields from the reference.

## Instantiate a reusable package

When the user wants the same workflow with new inputs, inspect and validate the
source package, recover only the new binding values and new slug, and confirm the
instance summary. Do not repeat questions about unchanged template rules. Pipe a
JSON object containing `input_bindings` and an optional `title` to:

```bash
python3 <skill-directory>/scripts/loop_package.py instantiate \
  --template <absolute-source-loop-directory> \
  --workspace <absolute-workspace> \
  --slug <new-lowercase-hyphen-slug>
```

Instantiation supports schema v2 and v3, preserves the source package, reuses its
immutable initial blueprint, creates fresh state/progress/handoff files, and
does not copy runtime configuration or evidence. Require the user to review
one regenerated business summary before saving or starting.

## Migrate or update an existing package

Never migrate a legacy package in place. First inspect the read-only plan:

```bash
python3 <skill-directory>/scripts/loop_package.py migrate-plan \
  --path <absolute-v1-or-v2-loop-directory>
```

Infer reported evidence, graph, breaker, budget, policy, and verifier decisions
from the source package and target repository. Ask once only for remaining
blocking gaps, confirm the business summary, then pipe
`{"specification": <v3-spec>}` to:

```bash
python3 <skill-directory>/scripts/loop_package.py migrate \
  --source <absolute-v1-or-v2-loop-directory> \
  --workspace <absolute-workspace> \
  --slug <new-lowercase-hyphen-slug>
```

Migration creates fresh `ready` state and never copies runtime configuration,
approvals, progress, handoff, or evidence. For an approved v3 contract update,
pipe the full new specification, `expected_contract_sha256`, and approval record
to `loop_package.py update --path <absolute-loop-directory>`. Update is allowed
only for `ready`, `blocked`, or `failed` packages with no active task or pending
approval. It uses compare-and-swap, appends the approval
to progress, preserves runtime artifacts, and rejects binding changes. Completed
or cancelled packages must be instantiated instead.

The generated package contains these core artifacts:

- `WORKFLOW.md`: immutable execution, verification, authority, and recovery
  contract;
- `state.json`: versioned machine state, graph progress, evidence coverage,
  breaker counters, memory/integrity heads, budgets, approvals, and
  contract hashes;
- `progress.md`: append-only iteration and evidence ledger;
- `handoff.md`: latest clean-context resume briefing.
- `runtime-recommendation.json`: optional, non-secret, contract-bound Runtime
  Config and model recommendation with provenance and confidence.

## Validate and hand off

Run the validator after every creation or approved update:

```bash
python3 <skill-directory>/scripts/loop_package.py validate \
  --path <absolute-loop-directory>
```

Fix package-generation defects within the confirmed contract and revalidate.
Stop for user input when a valid fix would change scope, completion, authority,
approval, or budget. Report:

- the created or updated absolute path;
- validation success or the exact blocker;
- the configured hard limits and approval gates;
- one explicit reminder that the loop has not been started.

If `pi-loop` is available, run `pi-loop review --workspace <workspace> --slug
<slug>` to open the generated business-summary confirmation page. Opening the
page is not permission to save the draft or start the loop. If Pi is unavailable,
report the recommendation file and continue without installing it.

Do not add a generic runner, connect a hosted agent platform, install the Skill,
commit, publish, or deploy unless the user separately requests it.
