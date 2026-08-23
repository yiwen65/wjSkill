# EDRU Takeover Protocol

Read this protocol only for `takeover`, `change-ready`, or a complex `survey` spanning multiple executables. It adds execution checkpoints without changing the authority, scope, or completion gates in `SKILL.md`.

## 1. Establish the analysis baseline

- Freeze revision, branch, dirty state, submodules, LFS state, platform, and tool versions.
- Read in-scope `AGENTS.md` files, contribution rules, OWNERS, generation rules, and repository constraints.
- Record included and excluded scope, build targets, deployment form, feature flags, runtime configuration, permissions, and budget.
- Add missing dependencies, environment limitations, and unverified defaults to the unknowns register.
- If the user wants only an answer, remain answer-only. Initialize `output_root` and the manifest only when persistent assets are requested.

## 2. Recover the system map

Locate candidate boundaries from these fact sources:

1. build targets and dependency graphs;
2. deployment manifests, startup commands, and runtime units;
3. routing, registration, dependency injection, plugins, and message subscriptions;
4. APIs, IDLs, schemas, configuration, and database migrations;
5. generators, generated artifacts, and consumers.

For each in-scope critical unit, record responsibility, entry points, build targets, deployment form, provided interfaces, dependencies, state or data ownership, configuration, tests, owners, evidence, and unknowns. Define the critical-unit inventory before reporting coverage.

Maintain all three views:

- intended architecture: intent expressed by documentation, ADRs, or proposals;
- as-built architecture: current behavior directly supported by build, configuration, and implementation evidence;
- deviation: differences, risks, and supporting evidence.

## 3. Select scenarios and critical paths

Choose a small representative set according to objective, risk, and budget. It will usually cover:

- the primary write path;
- the primary read path;
- an asynchronous event path;
- a primary failure, timeout, or retry path;
- a permission, security, administration, or extension path.

For each scenario, first define actors, trigger, input, initial state, critical configuration, expected output, final state, and an observable oracle. Then trace:

```text
external stimulus
→ boundary adapter
→ routing or dispatch
→ authentication, validation, and transformation
→ orchestration and core rules
→ data read/write or message publication
→ downstream consumer
→ response or final state
```

For every edge, record caller, symbol, inputs and outputs, state changes, side effects, transaction boundaries, errors, timeouts, retries, compensation, degradation, claim, evidence, and confidence. Trace result objects backward to their producer or write point as well.

## 4. Corroboration, refutation, and history

- Static calls, references, and data flow establish only `MAY`.
- Tests, coverage, traces, profiles, logs, metrics, and data changes establish `OBSERVED`.
- Explain "static but not dynamic" and "dynamic but not static" separately; retain unknown status when evidence is insufficient.
- Give every high-risk claim at least one falsifiable counter-hypothesis.
- Check reflection, dynamic registration, dependency injection, plugins, RPC, messaging, FFI, and generated code for implicit relationships.
- For unusual designs, critical modules, and proposed change points, inspect introduction, fixes, rollbacks, co-changes, PRs, issues, and ADRs.
- Distinguish deliberate compatibility, temporary debt, accidental complexity, and architectural constraints. Keep unrecoverable intent unknown.

## 5. `change-ready` impact closure

Around the explicit `change_target`, inspect:

- build reverse dependencies and affected targets;
- symbol callers, implementers, overrides, registrations, and generated relationships;
- API, message, configuration, schema, and data consumers;
- shared-state readers and writers, caches, transactions, migrations, and consistency;
- runtime consumers, tests, alerts, permissions, deployment, and runbooks;
- compatibility history, co-changes, and cross-repository or external consumers.

Produce pre-change predictions: expected changes, expected non-changes, observable oracles, and validation methods. Prepare targeted validation and executable rollback conditions for every high-risk impact. Put uncovered consumers in the unknowns register; never treat them as evidence of no impact.

## 6. Cost control

- Inspect build and deployment facts, precise symbols, registrations, contracts, and error strings before broad searches.
- For many homogeneous leaf modules, sample a typical, boundary, and high-risk implementation. Never sample away entry points, public contracts, migrations, permissions, failure handling, generation sources, state machines, or the direct upstream and downstream of a change target.
- Bind cached evidence to `(repo, revision, dirty_fingerprint, build_variant, platform, feature_flags, tool_versions)` and reassess validity when any critical dimension changes.
- For persistent asset refreshes, follow `update-protocol.md`; invalidate along `changed source/contract/config/envelope → generated output or registration → reverse dependency → contract/state consumer → critical path → claim/report`.
- Stop expanding at the budget or when marginal value is low, and use `completed_with_unknowns` for the remaining gaps.

## 7. Delivery check

- Required assets exist and pass structural validation.
- Every material conclusion traces to claims and evidence.
- Critical-path scope is defined, and every included edge has `C2+` evidence.
- `MAY`, `OBSERVED`, and `REFUTED` are not conflated.
- Every material unknown has severity, impact, blocking source, and a next action.
- High-severity unknowns correctly block a "safe to modify" conclusion in `change-ready`.
- The readiness report answers the final four questions from underlying assets and states every downgrade explicitly.
