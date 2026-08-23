---
name: understand-repo
description: Create or update traceable repository knowledge by recovering executable topology, critical paths, boundaries, state, and change impact for large or unfamiliar repositories. Use only when the user explicitly asks for repository takeover, system or architecture understanding, critical-path tracing, technical due diligence, pre-change impact analysis, or a refresh of existing .edru assets after repository changes or major refactoring. Do not auto-invoke for ordinary implementation, debugging, code review, or single-file questions.
---

# EDRU Repository Understanding

## Goal

Within a fixed revision, build target, and runtime configuration, use locatable repository evidence to answer:

1. How does the system work?
2. Where is the critical code?
3. What could a specified change affect?
4. What risks remain unverified?

The deliverable is a set of conclusions with evidence, applicability, and unknowns—not a directory summary or reading log.

## Authority boundaries

- Analyze source code, configuration, data, and remote resources read-only by default. Invoking this Skill does not authorize modifying them.
- When the user requests persistent EDRU assets, write only derived EDRU files under `output_root`. If the user asks only for an answer, answer directly and do not create an asset directory.
- Before running builds, tests, or repository scripts, confirm that execution is authorized and inspect repository instructions and command risk. For an unknown repository, prefer isolation, do not load host secrets or production credentials, and do not enable network access without authorization.
- When permissions or environment access are insufficient, complete the statically supportable work and record dynamic conclusions as unknown. Never present unexecuted work as validated.

## Operations, modes, and required inputs

`operation` controls the lifecycle of persistent EDRU knowledge. `mode` controls analysis depth. They are orthogonal: every operation supports every mode.

| Operation | Use when | Required behavior |
|---|---|---|
| `create` | No valid baseline exists, or the user requests a new baseline | Build assets for the target snapshot without inventing prior lineage |
| `update` | The user explicitly asks to refresh existing EDRU assets after repository or execution-envelope changes | Validate the prior manifest, compare snapshots, retain only still-valid knowledge, invalidate affected records, preserve history, and refresh impacted assets |

| Mode | Use when | Deliverable scope |
|---|---|---|
| `survey` | Quickly establish system boundaries and executable topology | Baseline, topology, modules, boundaries, evidence, and unknowns |
| `takeover` | Build reusable repository knowledge; default | Everything in `survey`, plus critical paths, data and state, historical risks, and a validation map |
| `change-ready` | Establish the impact closure for one explicit change | `takeover` evidence within the affected scope, plus an impact matrix, pre-change predictions, validation, and rollback plans |

Derive the repository path or URL, objective, included and excluded scope, operation, mode, revision, build/platform/feature flags, runtime and network permissions, budget, and output location from the request and repository state. `change-ready` also requires an explicit `change_target`. Ask only when a missing value would materially change scope, authority, or the deliverable.

Select `update` only when the user explicitly requests an update or refresh of persistent EDRU assets. Repository changes alone do not authorize writes. An update requires a readable previous `manifest.yaml` with enough repository and snapshot identity to establish lineage. If it is missing or invalid, do not silently overwrite the assets or invent a parent run; ask whether to repair the baseline or run `create`. A valid prior run with unbounded change may use the `full_rebaseline` update strategy while preserving lineage and the previous asset versions.

Defaults:

- `operation`: `create`;
- `revision`: current `HEAD`, while also recording branch, dirty state, and a working-tree fingerprint when dirty;
- `scope`: current repository;
- `mode`: `takeover`;
- `runtime_access`, `network_access`: `false`;
- `max_critical_paths`: `3`;
- `output_root`: `.edru`.

If the user selects `change-ready` without a change target, ask one focused question before proceeding. Do not fabricate target-level impact analysis. If `update` targets the same repository snapshot and execution envelope as the parent, record a validated no-op update rather than rewriting unchanged knowledge.

## Load resources only when needed

Read only resources required for the current request:

- For `takeover`, `change-ready`, or a complex `survey` spanning multiple executables, read the [takeover protocol](references/takeover-protocol.md).
- For every `update`, read the [update protocol](references/update-protocol.md) before changing persistent assets.
- When producing an asset, read only its corresponding file in `templates/`; use `manifest.yaml` for `create` and `update-manifest.yaml` for `update`. Do not load every template at once.
- When producing or validating manifest, claim, evidence, or machine-readable readiness data, read the corresponding file in `schemas/`.
- Read the matching item in `examples/` only when the structure remains unclear.
- Read [method sources](references/method-sources.md) only when the user asks about methodological grounding, research sources, or method boundaries.

After producing an asset directory, run:

```bash
python3 scripts/validate_edru_assets.py <output_root> --operation <operation> --mode <mode>
```

The script proves only that required files exist, lifecycle metadata is coherent, and basic structure is parseable. It does not prove that repository conclusions are true or that an update found every affected dependency.

## Evidence contract

### Relationship types

- `EXPECTED`: intent stated by documentation, an ADR, or a proposal;
- `DECLARED`: a relationship directly declared by build metadata, configuration, IDL, registration, or source code;
- `MAY`: a possible relationship found through static analysis;
- `OBSERVED`: a relationship observed through tests, traces, coverage, profiles, logs, or data changes;
- `REFUTED`: a conclusion contradicted by stronger evidence.

### Confidence

- `C0`: no evidence;
- `C1`: only names, directories, comments, one document, or model inference;
- `C2`: at least one direct implementation, build, configuration, or interface source;
- `C3`: corroboration through two relatively independent evidence channels;
- `C4`: execution under a recorded version, configuration, and input.

`C4` covers only the executed scenario. Static reachability does not prove runtime execution, and failure to observe a path does not prove it is unreachable.

### Recording rules

- For each substantive claim, record its type, confidence, revision, scope, evidence IDs, counter-hypotheses, and remaining unknowns.
- Give each evidence item a reviewable locator such as `path#symbol:line`, build target, command, trace ID, or commit, and record the tool, revision, scope, and limitations.
- Use directory, file, and class names only for navigation; they cannot independently prove an architectural boundary.
- For generated code, establish `source → generator → output → consumer`; do not treat a generated artifact as the source to edit.
- Phrase negative findings as "not found within the inspected scope" unless the evidence actually covers static, dynamic, and external channels.
- Prefer build systems, compilers, LSPs, indexers, and language-specific tools for symbol references, reverse dependencies, and call relationships. Keep model inference at `C0/C1`.

## Execution method

Follow dependency order, but do not perform phases that do not serve the objective:

1. **Select the operation and freeze the envelope.** Record operation, revision, dirty state and fingerprint, repository instructions, scope, build targets, platform, configuration, feature flags, permissions, and budget. For `update`, validate the parent manifest and follow the update protocol before reusing any prior claim or evidence.
2. **Recover executable topology.** Use build and deployment facts to identify entry points, artifacts, services, libraries, generated relationships, and external boundaries; then map module responsibilities and data ownership.
3. **Choose representative scenarios.** Select primary reads/writes, asynchronous flows, failure/retry paths, permissions, or extension paths according to the objective and budget. Define the included set before measuring coverage.
4. **Trace critical paths vertically.** Follow each path from external stimulus to final state, recording callers, symbols, inputs and outputs, state changes, side effects, transactions, errors, timeouts, retries, compensation, and degradation.
5. **Corroborate and challenge.** Compare implementation, build, configuration, tests, runtime observations, and history for critical claims. Check registration, DI, reflection, plugins, RPC, messaging, FFI, and generated code for hidden edges.
6. **Expand the impact closure.** Required only for `change-ready`: inspect build reverse dependencies, callers and implementers, contract consumers, shared-state readers and writers, runtime consumers, tests, operations, security, compatibility history, and cross-repository unknowns.
7. **Converge.** Run structural validation with both operation and mode, evaluate gates, preserve unresolved items and next validation actions, and link the final report to underlying assets.

Within the budget, prioritize evidence that most reduces high-severity unknowns. Stop expanding when the budget is reached, progress requires additional permission, credentials, or a user decision, or further search cannot materially improve the conclusion. Degrade status truthfully.

## Persistent assets

Generate the following files only when the user requests persistent assets. Use fields from `templates/`; the validator determines required files.

Every `update` also requires:

- `16-update-summary.md`

Before replacing any existing asset, preserve the parent manifest and every changed or removed asset under the manifest's history root. Do not delete invalidated claims or evidence merely because they are stale; retain their provenance and mark their lifecycle state.

### `survey`

- `manifest.yaml`
- `00-repository-passport.yaml`
- `01-system-overview.md`
- `02-technology-stack.yaml`
- `03-executable-topology.md`
- `04-module-map.yaml`
- `05-boundary-catalog.yaml`
- `08-evidence-ledger.jsonl`
- `09-claim-register.yaml`
- `10-hypotheses-and-unknowns.yaml`
- `15-readiness-report.md`

### `takeover`

In addition to `survey` assets:

- `06-data-and-state-map.md`
- `07-critical-paths/KP-xxx.md`
- `11-history-and-decisions.md`
- `12-risk-register.yaml`
- `14-validation-and-observability.md`

### `change-ready`

In addition to `takeover` assets:

- `13-change-impact-matrix.md`

## Completion gates

- **Baseline:** Every conclusion is bound to an explicit revision, analysis scope, and execution envelope.
- **Map:** Enumerate in-scope critical executables, modules, and boundaries before calculating coverage. Critical boundaries have at least `C2` evidence, and intended/as-built differences are recorded.
- **Paths:** Every edge in each included critical path has evidence of at least `C2`; `MAY` and `OBSERVED` are not conflated. `C4` is optional when runtime access is unavailable, but the dynamic gap must be recorded.
- **Impact:** `change-ready` has checked relevant direct and indirect consumers. Any unmitigated high-severity unknown blocks a "safe to modify" conclusion without erasing completed analysis.
- **Unknowns:** Every material unknown has severity, impact, blocking source, and a next validation action.
- **Reviewability:** The final four answers trace to claims, evidence, or explicit unknowns, and structural validation passes.
- **Lifecycle:** For `update`, lineage is valid, unchanged assets are explicitly retained, affected records are invalidated or superseded, prior versions are recoverable, and the incremental or full-rebaseline strategy is justified.

Status meanings:

- `completed`: the target scope meets all gates and has no unresolved unknown that affects the conclusion;
- `completed_with_unknowns`: the objective can be answered, but bounded unknowns or dynamic gaps remain;
- `blocked`: a missing decision, permission, credential, or critical input prevents a supportable answer to the objective itself.

Do not claim completion from asset counts, files read, or a coverage ratio with an undefined denominator.

## Final response

Briefly report repository and revision, operation, mode and scope, how the system works, critical code and paths, boundaries and state, change impact, highest-risk unknowns, gate status, and asset paths. For `update`, include the parent and target snapshots, retained/invalidated/regenerated assets, and whether the strategy was incremental, no-op, or full rebaseline. Clearly distinguish supported facts, inference, unobserved behavior, and unknowns. Do not let the summary replace the underlying evidence.
