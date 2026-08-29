---
name: dead-code-cleanup
description: Safely identify, validate, deprecate, and, when authorized, remove dead-code candidates using bounded consumer discovery, independent evidence, reversible changes, and regression gates. Use for unused or unreachable code, stale exports or dependencies, obsolete flags or configuration, retired APIs, migration remnants, and unreferenced build targets. Do not use for generic refactoring, ordinary code review, or performance optimization.
---

# Dead Code Cleanup

## Outcome

Turn each suspected dead asset into one evidence-backed result:

- **in use** — credible positive-use evidence rejects the candidate;
- **verified within a stated boundary** — deletion is supported for the named
  versions, targets, configurations, consumers, and observation window;
- **migration or deprecation required** — the asset is still a contract or has
  open-world consumers;
- **insufficient evidence** — preserve it and name the missing proof and next
  discriminating action; or
- **removed and verified** — an authorized, recoverable deletion passed the
  applicable regression gates.

Treat dead-code cleanup as a controlled behavior change, not as a static-tool
autofix. A tool report creates a candidate; it does not grant deletion authority.

## Preserve authority and the worktree

- Requests to inspect, audit, identify, assess, explain, or plan are read-only.
  Do not edit code, configuration, dependencies, tests, or generated assets.
- Requests to clean, remove, or delete authorize repository changes only within
  the stated scope. They do not authorize production instrumentation, flag or
  scheduler changes, customer or owner contact, deployment, canarying, or other
  external mutations unless the user separately requests them.
- If the user restricts the task to static inspection or forbids execution,
  builds, instrumentation, or runtime access, do not cross that boundary. Return
  candidates, static facts, and unknowns instead of inventing runtime evidence.
- Read repository instructions and preserve unrelated user changes. Do not mix
  formatting, upgrades, renames, or opportunistic refactoring into a deletion.
- Ask only when a missing support boundary, consumer scope, data impact,
  acceptance criterion, or mutation authority would materially change safety.

## Recover the cleanup contract

Before deciding that an asset is dead, identify the smallest relevant boundary:

- the artifact type and exact symbol, file, package, target, dependency, API,
  flag, configuration key, job, topic, field, or schema;
- supported versions, entry points, build targets, platforms, features,
  environments, regions, tenants, permissions, and client versions;
- known and plausible consumers, including other repositories, generated code,
  plugins, scripts, operators, external clients, and retained historical data;
- business criticality, side effects, compatibility or recovery duties, and any
  irreversible data change;
- the success oracle, required validation, observation window, stop conditions,
  and recovery mechanism.

Use current repository manifests, build definitions, deployment files, tests,
configuration, ownership records, and history to fill harmless gaps. Do not call
the boundary closed merely because the current repository has no reference.

## Select the operating mode

### Static-only audit

Use this mode when the request permits only source and existing static artifacts,
or when execution and representative runtime evidence are unavailable. Inspect
control flow, symbol visibility, side effects, source and string references,
build graphs, configuration, tests, history, and documented entry points within
the allowed scope.

Label results as `STATIC FACT`, `CONDITIONAL CANDIDATE`, or `UNKNOWN`. A local,
private, side-effect-free declaration may be verified within a demonstrably
closed source/build boundary; exported, dynamic, cross-process, data, recovery,
or externally consumable assets remain candidates. Do not continue into builds,
instrumentation, counterfactual runtime tests, edits, or deployment.

### Evidence-backed audit

Use this mode when non-mutating repository checks and existing build, runtime,
contract, or ownership evidence are authorized. Build a decision record for each
candidate, but do not remove it. Distinguish current observations from inherited
reports and record telemetry coverage, sampling, time window, and blind spots.

### Authorized cleanup

Use this mode only when repository deletion is requested. Run the evidence gate
before editing. When the gate fails, preserve the candidate and report the
blocker; deletion intent does not convert missing evidence into proof.

## Run the evidence workflow

### 1. Establish the baseline and generate candidates

Record the revision and worktree state, relevant build and test commands,
supported target matrix, current behavior oracle, and any available operational
guardrails. Generate candidates in report-only mode using the project-native
compiler, linter, static graph, dependency graph, coverage, and search tools.
Record tool version, configuration, scope, and raw decisive result.

Read [references/ecosystem-routing.md](references/ecosystem-routing.md) only when
choosing language- or build-system-specific detectors and validation.

### 2. Classify risk before gathering more negative evidence

Determine whether the candidate is local and closed or public, dynamic,
cross-repository, multi-version, data-bearing, operational, generated,
side-effectful, security-sensitive, billing-sensitive, or recovery-related.
Apply the vetoes in
[references/evidence-and-risk.md](references/evidence-and-risk.md). A veto blocks
automatic deletion even when a numeric score or several tools look favorable.

### 3. Discover consumers and converge independent evidence

Trace entry points and consumers through code, strings, manifests, build and
package registries, service catalogs, API or schema definitions, configuration,
CI, infrastructure, scripts, jobs, message subscriptions, history, and ownership.
Account explicitly for reflection, dependency injection, framework registration,
dynamic import, plugins, callbacks, generated code, initialization side effects,
old clients, low-frequency paths, and platform or feature variants.

Use evidence from the applicable independent families:

1. static and build reachability;
2. runtime execution and representative observation;
3. contracts, consumers, ownership, and history; and
4. counterfactual disablement and recovery.

Two tools based on the same AST, call graph, or telemetry source remain one
evidence family. Absence of calls is bounded negative evidence; one credible
production call, required recovery exercise, or confirmed consumer is stronger
and marks the asset in use.

### 4. Decide the lifecycle

Use the decision matrix and candidate record in
[references/evidence-and-risk.md](references/evidence-and-risk.md). Reserve direct
or automated removal for local/private, side-effect-free assets inside a closed
boundary. Route public, cross-repository, dynamic, data, message, job, flag, and
multi-version assets through migration, deprecation, isolation, or observation.

Read [references/asset-playbooks.md](references/asset-playbooks.md) only for the
asset types present in the current task. Do not impose a long lifecycle on a
compiler-proven unused local, and do not shorten an open-world contract lifecycle
because the code change is mechanically simple.

### 5. Prove absence before physical deletion when risk requires it

Where the asset has a callable or configurable entry, first prevent new use,
disable or isolate the old path, retain a quick recovery route, alert on any
unexpected hit, and observe the relevant business cycle. Exercise disaster,
scheduled, or low-frequency paths deliberately rather than waiting passively.

Keep deprecation, traffic migration, data migration, physical deletion, and
unrelated redesign separately reviewable. Do not combine deletion with an
irreversible data change.

### 6. Make the smallest complete deletion

Remove one coherent candidate or tightly coupled candidate set. Delete its
entry points and registrations, implementation, now-unused private dependents,
and only the tests, dependencies, configuration, documentation, monitoring, and
build rules whose purpose ended with it. Preserve tests that still protect a
supported contract. Inspect generated diffs and edit generators rather than
regenerable output when the repository requires it.

### 7. Verify in risk order

Run and record the smallest applicable layers, broadening with exposure:

1. candidate and reference checks show no unintended surviving or missing edge;
2. all affected supported targets, profiles, features, platforms, and generated
   artifacts compile or build;
3. focused, integration, end-to-end, startup, packaging, and test-discovery
   checks preserve supported behavior;
4. API, schema, consumer, upgrade, rollback, and mixed-version checks pass when
   the boundary includes them;
5. authorized canary or production observation stays within predeclared service,
   business, data, and resource guardrails for the required window; and
6. the final diff contains only the intended cleanup and complete related assets.

Treat `not run`, `not available`, `passed`, and `failed` as different results.
Never claim production safety from source inspection or a default build alone.

## Stop conditions

Do not delete, or stop rollout and recover, when any of these applies:

- an unknown or credible consumer, production call, old client, or third-party
  use appears;
- the dynamic-entry, build/configuration, telemetry, ownership, or observation
  boundary is incomplete;
- contract, schema, mixed-version, test, build, package, data, or rollback checks
  fail or were required but not run;
- a service, business, data, security, billing, compliance, or recovery owner has
  an unresolved objection;
- canary guardrails, data reconciliation, message backlog, or regional/tenant
  behavior diverges; or
- recovery assets are unavailable or the change would be irreversible.

## Report the result

Lead with the decision or completed removal, then include only supported sections:

```markdown
## Scope and boundary
Candidate assets, supported targets and versions, consumers, mode, and authority.

## Decision ledger
For each candidate: classification, decisive positive and negative evidence,
blind spots or vetoes, and decision: in use | removable | migrate/deprecate |
insufficient evidence.

## Changes
Authorized deletions and related assets removed; omit for audits.

## Verification
Commands or evidence sources, results, observation window, guardrails, and
checks not run.

## Recovery and residual risk
Rollback route, remaining assumptions, blockers, and next discriminating action.
```

State the boundary of every safety claim. Do not report a candidate count or
deleted line count as the primary success measure.
