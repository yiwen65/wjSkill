# Loop Workflow Design Reference

Read the automatic-inference section before asking technical questions. Apply
the domain-specific design sections only after the user confirms the business
contract. This reference distills the durable-state methodology from Addy
Osmani's “Long-Running Agents” and turns it into a vendor-neutral package
contract. The wording and schemas here are original to this Skill.

## Contents

1. Core design invariants
2. Loop lifecycle
3. Specification schema
4. Automatic inference and Runtime Recommendation
5. Domain adaptations
6. Evidence and completion
7. Permission and failure design
8. Context reset and contract changes

## 1. Core design invariants

Design a sequence of bounded sessions, not one indefinitely growing
conversation.

- Keep durable truth outside the model context.
- Make the next session reconstructable from files, not conversational memory.
- Store the template identity, input schema, instance bindings, typed initial
  graph, goal, completion conditions, authority, and limits in a versioned
  contract.
- Keep the task queue, evidence, checkpoints, and latest handoff separately
  mutable.
- Let the planner choose work, the worker produce evidence, and the evaluator
  decide whether that evidence passes.
- Reset context when it becomes noisy; do not repeatedly summarize a degraded
  context forever.
- Require a hard bound and stop safely when it is reached.
- Treat permissions and credentials as runtime policy, never as prompt text that
  the worker may reinterpret.

The basic transition is:

```text
load contract and state
  -> planner selects one ready graph node
  -> worker performs only that node
  -> deterministic checks produce evidence
  -> evaluator returns pass, retry, replan, block, or complete
  -> append progress, checkpoint state, refresh handoff
  -> stop or begin a fresh iteration
```

## 2. Loop lifecycle

Use these loop states exactly:

- `ready`: generated and validated, not started;
- `running`: one task is active or awaiting evaluation;
- `waiting_approval`: the next action requires explicit human approval;
- `blocked`: progress needs unavailable information, authority, or external state;
- `completed`: every completion condition has independent passing evidence;
- `failed`: a terminal technical failure occurred within the authorized scope;
- `cancelled`: the user stopped the workflow.

Use these node states exactly:

- `pending`
- `in_progress`
- `awaiting_evaluation`
- `completed`
- `failed`
- `blocked`

Permit at most one `in_progress` node in a sequential workflow. For a parallel
workflow, use isolated worker branches or workspaces and make merge ownership,
dependency edges, and evaluator order explicit in `WORKFLOW.md` before starting.

## 3. Specification schema

Schema v3 separates a reusable parameter definition from one run's bound values,
uses stable IDs for every completion and authority reference, and replaces a
flat task list with a typed bounded DAG. Pass one JSON object on standard input
to `loop_package.py create`. Use UTF-8 strings. Use `zh` or `zh-*` for Chinese
content; stable machine fields remain English.

Required top-level fields:

```json
{
  "title": "Repository-wide API migration",
  "language": "en",
  "domain": "coding",
  "execution_mode": "sequential",
  "goal": "Migrate every supported caller without changing public behavior.",
  "audience": "Repository maintainers",
  "inputs": ["Repository source", "Current API contract"],
  "input_schema": [
    {
      "name": "repository",
      "type": "path",
      "description": "Repository root for this migration instance",
      "required": true
    },
    {
      "name": "target_api_version",
      "type": "string",
      "description": "API version to migrate callers to",
      "required": true
    }
  ],
  "input_bindings": {
    "repository": "/workspace/project",
    "target_api_version": "v2"
  },
  "invariants": ["Do not weaken existing tests"],
  "conditions": [
    {
      "id": "target-tests-pass",
      "description": "The target build and tests pass.",
      "evidence_requirement_ids": ["target-test-command"]
    }
  ],
  "evidence_requirements": [
    {
      "id": "target-test-command",
      "type": "deterministic",
      "description": "Run the exact target build and test commands."
    }
  ],
  "initial_graph": {
    "nodes": [
      {
        "id": "inventory-callers",
        "title": "Inventory callers",
        "description": "Find and classify every supported caller.",
        "input_ports": [],
        "output_ports": [
          {
            "id": "inventory",
            "type": "artifact",
            "description": "Verified caller inventory"
          }
        ],
        "acceptance_criteria": ["Every caller has a file and symbol location"],
        "resource_keys": ["repository"],
        "max_attempts": 3,
        "no_progress_limit": 2
      }
    ],
    "edges": []
  },
  "authority": {
    "risk_level": "medium",
    "rules": [
      {
        "authority_id": "workspace-edit",
        "effect": "allow",
        "description": "Read and edit files in the confirmed scope."
      },
      {
        "authority_id": "publish-gate",
        "effect": "approve",
        "description": "Push, merge, release, or deploy."
      },
      {
        "authority_id": "secret-and-test-deny",
        "effect": "deny",
        "description": "Expose credentials or weaken tests."
      }
    ],
    "credential_policy": "Retrieve secrets only through the authorized runtime secret store.",
    "credential_env": ["MIGRATION_API_TOKEN"]
  },
  "limits": {
    "max_iterations": 24,
    "max_minutes": 480,
    "max_cost": null,
    "cost_currency": null,
    "max_total_tokens": 240000
  },
  "checkpoint": {
    "required_triggers": ["task_evaluated", "before_context_reset"],
    "required_evidence": ["State transition", "Verification result", "Next action"]
  },
  "circuit_breakers": [
    {"id": "no-evidence", "signal": "no_new_evidence", "threshold": 2, "action": "block"},
    {"id": "attempt-limit", "signal": "task_attempts", "threshold": 3, "action": "fail"},
    {"id": "verifier-limit", "signal": "consecutive_verifier_failures", "threshold": 2, "action": "block"}
  ],
  "memory_policy": {
    "max_entries": 500,
    "retrieval_top_k": 8,
    "max_context_tokens": 3000
  },
  "context_policy": {
    "estimator": "utf8_bytes",
    "fail_on_required_overflow": true,
    "role_token_budgets": {
      "planner": 5000,
      "worker": 8000,
      "evaluator": 5000,
      "final_evaluator": 4000
    }
  }
}
```

Validation rules:

- Use `coding`, `research`, `content`, `operations`, or `general` for `domain`.
- Give every changing input a unique lowercase name, one of `string`, `integer`,
  `number`, `boolean`, `path`, or `uri`, a description, and a required flag.
- Bind every required input, reject unknown bindings, and keep secrets out of all
  bindings. Integral numbers are canonicalized consistently for hashing.
- Give conditions and evidence requirements unique lowercase hyphenated stable
  IDs. Every condition must bind at least one `deterministic` or
  `human_attestation` requirement; `independent_evaluator` cannot prove global
  completion alone.
- Use `artifact`, `evidence`, `data`, `text`, or `json` for port types. Every
  required input port must have exactly one same-typed incoming edge. Ordinary
  graph edges must be acyclic; retry and replan belong to the harness.
- Give every node positive `max_attempts` and `no_progress_limit`, with the latter
  no greater than the former. Use `resource_keys` to prevent unsafe parallel
  ownership overlap.
- Use `low`, `medium`, or `high` for `authority.risk_level`.
- Give every authority rule a stable `authority_id` and one of `allow`,
  `approve`, or `deny`. Medium/high risk needs an approval rule; every v3
  contract needs a deny rule. Optional `credential_env` contains only unique,
  explicitly authorized environment-variable names, never values.
- Supply at least one positive hard limit among `max_iterations`, `max_minutes`,
  `max_cost`, and `max_total_tokens`; the others may be null. Supply
  `cost_currency` when `max_cost` is set.
- Circuit breakers use only observable `no_new_evidence`, `task_attempts`,
  `consecutive_verifier_failures`, `tool_failures`, or `approval_denials`
  signals and only `block` or `fail` actions. Multiple breakers may observe the
  same signal at different thresholds.
- Checkpoint triggers are unique, confirmed, nonblank runtime event names rather
  than a hard-coded enum.
- Memory is workflow-local. Only planner decisions, verifier results, user
  resolutions, checkpoints, and errors may produce memory records; a model may
  not freely assert facts. External MemoryProvider candidates remain read-only.
- Context assembly uses role-specific budgets and must fail closed when the
  immutable contract, authority, or required evidence cannot fit.
- Never put a secret value in any field.

The generator records a template identity and version, hashes the normalized
bindings, and stores the typed initial graph as an immutable blueprint. Runtime
state records typed output references and evidence without modifying that graph.

To repeat a workflow, instantiate a fresh package with a new slug and bindings.
Never clear a terminal package or reuse its state, progress, handoff, approvals,
runtime configuration, or evidence. Increase `template.version` when parameter
definitions or the initial graph changes; an ordinary new binding does not
change the template version.

Schema v1/v2 packages remain valid and runnable with their original semantics.
Generate v2 only when explicitly requested. `migrate-plan` is read-only and
surfaces decisions that prose verification and stop rules cannot resolve.
`migrate` always creates a fresh v3 package and never copies runtime history.

## 4. Automatic inference and Runtime Recommendation

Inspect repository facts read-only before inventing technical fields. Use package scripts,
Make/CMake/Bazel targets, CI jobs, test configuration, checked-in schemas,
deployment manifests, and explicit project documentation. Record every source
reference as an object containing its URI and SHA-256 digest; a stable fragment
may be part of the URI. Never copy raw prompts or secret values.

Classify each inferred field as high confidence for explicit/direct evidence,
medium for a domain rule with repository corroboration, or low for an unsupported
heuristic. Use high and medium values automatically. A low-confidence field only
becomes a user question when it prevents a safe Runtime Config; combine all such
gaps into one interaction.

For `N` nodes, `E` edges, `C` conditions, and total node attempts `A`, use:

- planner context: `min(24000, 8000 + 1000N)`;
- worker context: `min(48000, 16000 + 2000N)`;
- evaluator context: `min(24000, 8000 + 1000C)`;
- final evaluator context: `min(16000, 8000 + 1000C)`;
- `max_iterations=A`, `max_minutes=clamp(30N+15E, 60, 480)`;
- `max_total_tokens=A*(planner+worker+evaluator)+final_evaluator`.

Use node `max_attempts=2`, increasing to `3` only for evidenced unstable external
systems, and `no_progress_limit=2`. Default breakers are no-new-evidence
`2/block`, verifier-failures `3/block`, tool-failures `3/fail`, and
approval-denials `1/block`. Default checkpoint triggers are `task_evaluated`,
`before_context_reset`, and `approval_resolved`.

An optional input field `runtime_recommendation` controls the generated
`runtime-recommendation.json`. It may contain:

- `models.{planner,worker,evaluator,final_evaluator}` with reasoning requirement,
  minimum context tokens, and `lowest_known` cost preference;
- Runtime Config v2 `execution`, `policy`, `verifiers`, and credential environment
  names;
- `inference_manifest[]` entries with `path`, `status`, `confidence`,
  `source_refs`, and `rationale`;
- a business `review` containing goal, steps, completion, permissions, and
  aggregate budget.

The generator supplies loop/template/contract hashes, computes `complete` or
`needs_input`, rejects authority or credential expansion, and adds a precise
needs-input entry for every uncovered deterministic/human requirement or
unmapped allow/approve authority. The file is advisory: Pi validates it against
the immutable contract and the user confirms the materialized Runtime Config
before any grant is active or a loop can start.

## 5. Domain adaptations

### Coding

- Derive tasks from the repository's actual dependency and build graph.
- Use an isolated branch or worktree for multihour changes when available.
- Checkpoint after a coherent, verified change; use commits only when authorized.
- Include builds, tests, static checks, and manual runtime checks appropriate to
  the changed behavior.
- Forbid deleting, skipping, or weakening a failing test merely to pass a gate.
- Make rollback and compatibility requirements explicit for migrations.

### Research

- Define the research question, decision audience, freshness boundary, and source
  quality hierarchy before searching.
- Keep a source ledger close to claims and distinguish confirmed facts,
  inference, missing evidence, and recommendations.
- Checkpoint after a source cluster or evidence question, not after every page.
- Stop on coverage and evidence saturation, not only on word count.
- Let the evaluator audit claim support, contradictions, dates, and unproven
  generalizations.

### Content

- Fix the audience, format, voice, source boundary, and factual claims before
  drafting.
- Split outline, drafting, factual review, structural edit, and final format
  verification into separate tasks.
- Preserve a source ledger for factual or attributed content.
- Let the evaluator check the brief and evidence rather than rewarding prose
  volume.

### Operations

- Separate observation, proposal, approval, execution, and post-change
  verification.
- Put every production write, deletion, external message, spend, permission
  change, and irreversible action behind a discrete approval when relevant.
- Store policy outside worker-editable files when a runtime policy layer exists.
- Define retries, exponential backoff where appropriate, idempotency, rollback,
  alerts, and a circuit breaker.
- Never place credentials in the package; reference the authorized retrieval
  mechanism only.

## 6. Evidence and completion

Write completion conditions so an evaluator can return pass or fail without
reading the worker's intentions. Prefer observable results such as:

- exact tests, builds, or runtime probes;
- required artifact paths and schema checks;
- claim-level citations and source coverage;
- before/after metrics with the measurement method;
- successful rollback or recovery rehearsal;
- explicit owner acceptance for a human judgment gate.

Do not use “looks good,” “high quality,” “mostly complete,” or “all reasonable
work is done” without an operational definition. A worker report is evidence
input, never final proof by itself.

Only transition the loop to `completed` when every immutable completion
condition has recorded passing evidence and no approval or blocked state remains.

## 7. Permission and failure design

Classify actions through stable rules in three nonoverlapping sets:

- `allow`: reversible actions inside the confirmed scope;
- `approve`: discrete high-impact actions that pause the loop;
- `deny`: actions outside scope or unacceptable under any iteration.

Do not infer broader authorization from approval of one action. Record a pending
approval with the exact action, target, reason, expected effect, rollback, and
evidence to collect afterward.

On failure:

1. Preserve the failing evidence.
2. Retry only when the failure is transient and the retry limit allows it.
3. Replan when the task decomposition was wrong but the immutable contract still
   holds.
4. Block when progress requires new information or authority.
5. Fail when a terminal condition is reached inside the existing contract.
6. Never expand scope or weaken completion to manufacture success.

## 8. Context reset and contract changes

Before resetting context, update `state.json`, append one complete entry to
`progress.md`, and rewrite `handoff.md` with:

- current goal and immutable constraints;
- current state and completed work;
- verified evidence and failed approaches;
- pending task, approval, or blocker;
- exact next action and files to read.

Maintain `progress_hash_chain` over exact appended entries. Initialize
`head_sha256 = sha256(utf8("\\0" + initial_progress_text))`; for each append use
`sha256(utf8(previous_head + "\\0" + exact_appended_entry_text))` and increment
`entries`. Store the current `handoff.md` SHA-256 separately.

Start the new session by reading `WORKFLOW.md`, validating the package, then
reading `state.json`, the latest progress entry, and `handoff.md`.

Allow evidence updates, progress entries, and handoff refreshes without changing
the contract or typed initial graph. Retry and replan are harness-controlled and
remain within graph and circuit-breaker bounds. Require explicit user approval
to change the reusable input schema, graph blueprint,
goal, completion conditions, invariants, authority, approval gates, or limits.
For an approved change:

1. append the old and new values, rationale, and approval evidence to progress;
2. increase `contract.version`;
3. update the canonical contract snapshot and its SHA-256;
4. update `WORKFLOW.md` and its SHA-256;
5. validate before resuming.

If the input schema or initial graph changed, increase `template.version` as
part of the same approved migration. If only instance bindings changed, create a
new instance instead of updating or resuming the old one.

`update` is a compare-and-swap operation keyed by the expected contract SHA-256.
It is permitted only for `ready`, `blocked`, or `failed` v3 packages with no
active task or pending tool approval. Preserve
progress, handoff, runtime evidence, and auxiliary runtime files transactionally;
reject graph replacement after runtime evidence exists. Completed and cancelled
packages are terminal and must be instantiated instead.
