# Evidence and Risk Model

Use this reference to classify a dead-code candidate, record its evidence, apply
automatic-deletion vetoes, and choose a lifecycle. The model supports judgment;
it does not replace it with a score.

## Working definition

An asset is verified dead only inside a named support boundary when all are true:

1. it cannot affect supported observable behavior;
2. it is not part of a live internal or external contract;
3. it has no remaining migration, rollback, recovery, audit, or compatibility
   duty; and
4. its removal has a credible validation and recovery path.

Anything reported by a detector before those conditions hold is a candidate.

## Candidate record

Keep one compact record per independently decidable asset or tightly coupled set:

| Field | Record |
| --- | --- |
| `candidate` | Exact symbol, file, target, dependency, API, flag, key, job, topic, field, or schema |
| `type` | Unreachable, semantically ineffective, unused local/private/export/dependency, stale lifecycle asset, migration residue, test/example residue, or build-variant asset |
| `support_boundary` | Repositories, versions, targets, platforms, environments, regions, tenants, permissions, features, and client versions |
| `entrypoints` | Language, framework, configuration, network, message, scheduler, script, plugin, generated, and operator entry points |
| `static_build_evidence` | Tool and version, configuration, raw result, source/build scope, and known model gaps |
| `runtime_evidence` | Signal, environment, sampling, coverage, start/end, represented cycles and populations, and blind spots |
| `consumer_contract_evidence` | Search domains, service/package catalogs, owners, APIs, schemas, clients, history, and confirmations |
| `counterfactual_recovery` | Disable or isolation result, guardrails, unexpected-hit alert, rollback mechanism, and rehearsal |
| `criticality` | Customer, data, billing, security, permissions, compliance, control-plane, or recovery impact |
| `decision` | In use, direct removal, human-confirmed removal, migrate/deprecate, or insufficient evidence |
| `review_date` | Required for deferred candidates, suppressions, or observation windows |

Record links or exact commands where practical. A summary without the decisive
raw source is weaker evidence.

## Evidence families and interpretation

### Static and build reachability

Examples include compiler diagnostics, local control/data flow, call graphs,
dependency graphs, configured build graphs, symbol/package visibility, and
generated-action graphs.

- Compiler proof for a side-effect-free local in a closed compilation boundary
  can be strong.
- Repository search, an IDE warning, a single default target, or linker removal
  from one binary is normally a clue or supporting evidence.
- Conservative analysis can hide dead code; incomplete modeling can falsely
  report reflection, generated, registered, or dynamically loaded code.

### Runtime execution

Examples include coverage, entry counters, traces, flag evaluations, job history,
consumer identity, and production traffic.

- A credible positive hit is strong evidence that the asset is in use.
- Zero hits are meaningful only with known instrumentation coverage, sampling,
  population, environment, and a representative observation window.
- Test non-coverage is a test-gap signal, not deletion proof.

### Contracts, consumers, ownership, and history

Examples include APIs, schemas, package registries, service catalogs, cross-repo
search, deployment/configuration inventories, CODEOWNERS, owner confirmation,
design history, migration records, and external-client policy.

- These establish why an asset exists and who can rely on it; code age alone is
  weak evidence.
- No owner or no registered consumer means the boundary is incomplete, not that
  nobody uses the asset.
- A declared deprecation is a lifecycle state, not proof that the contract ended.

### Counterfactual and recovery

Examples include preventing new references, fixing a flag, pausing a scheduler,
removing a registration, routing away from an endpoint, shadowing, canarying,
unexpected-hit alerts, and rollback rehearsal.

- This family tests whether the system remains correct without the old entry.
- Observation must cover the relevant business period. Exercise disaster and
  rare paths deliberately.
- A counterfactual without a usable recovery route is unsafe experimentation.

## Decision matrix

| Decision | Appropriate when | Required handling |
| --- | --- | --- |
| **In use** | Any credible supported consumer, runtime hit, required test/example contract, migration duty, or recovery use exists | Reject or redefine the candidate; do not average positive evidence against negative evidence |
| **Direct or automated removal** | Local/private, side-effect-free, compiler- or graph-proven inside a closed boundary; no veto; affected validation is complete | Small reviewed change; do not auto-merge a high-impact deletion |
| **Low-risk human-confirmed removal** | Module-internal asset; owner and consumer boundary known; independent evidence converges; recovery is simple | Focused review, full affected target validation, and proportionate observation |
| **Migrate or deprecate** | Public, cross-repo, dynamic, multi-version, data, message, configuration, flag, job, plugin, or operational asset | Prevent new use, identify and migrate consumers, observe, then remove through the asset playbook |
| **Insufficient evidence** | Owner, consumer, build/configuration, runtime, lifecycle, or rollback boundary has a material gap | Preserve; state the exact gap, owner, next discriminating action, and review date |

Do not add together correlated signals as if they were independent. A numeric
score can prioritize investigation, but cannot override positive-use evidence or
the vetoes below.

## Automatic-deletion vetoes

Any applicable unresolved item blocks automatic deletion:

- public API, SDK, CLI, package, event, message, database, storage, or serialized
  data contract;
- cross-repository, external, third-party, offline, or old-client consumers;
- reflection, dynamic dispatch/import, dependency injection, plugin discovery,
  callbacks, macros, code generation, or framework registration not fully modeled;
- load, import, initialization, registration, or constructor side effects;
- incomplete target, platform, architecture, profile, feature, region, tenant,
  permission, environment, or version matrix;
- scheduled, operator-triggered, migration, repair, replay, fallback, disaster,
  or other intentionally low-frequency path;
- data writes, state transitions, schema changes, or irreversible effects;
- billing, security, authorization, compliance, audit, control-plane, or recovery
  responsibility;
- unknown owner or unresolved owner objection;
- no representative runtime evidence where runtime proof is needed, or a known
  telemetry blind spot;
- no executable recovery route; or
- only a single weak signal such as an IDE warning, zero grep result, low test
  coverage, code age, or absence from one build artifact.

## High-risk evidence supplements

| Risk | Minimum supplemental evidence before lifecycle progress |
| --- | --- |
| Reflection, DI, or framework registration | Registration/scan configuration, resolved runtime targets where authorized, and production-profile startup or equivalent evidence |
| Dynamic imports, plugins, callbacks | Name/manifest domain, loader configuration, installed plugin inventory, activation evidence, and plugin-owner or compatibility checks |
| Generated code, macros, AOP | Generator/template source, generation manifests and actions, complete generated build, and edits at the authoritative source |
| Configuration or environment keys | Deployment and configuration-control sources, IaC/CI/scripts, read telemetry or consumer warning, and environment matrix |
| HTTP, RPC, SDK, CLI, packages | Consumer identity and version traffic, service/package catalogs, cross-repo search, compatibility policy, and deprecation window |
| Messages and events | Topic/subscription and consumer-group inventory, retention and replay requirements, schema compatibility, and backlog checks |
| Jobs and operator scripts | Scheduler/audit/runbook inventory, expected execution periods, pause-first observation, and manual recovery path |
| Mobile or long-lived clients | Minimum supported versions, traffic by version, offline-return behavior, release adoption, and compatibility policy |
| Region, tenant, role, platform, feature | Explicit matrix, per-segment evidence or synthesized exercise, and all supported builds |
| Failure, fallback, or disaster recovery | Game day, fault injection, tabletop plus executable runbook evidence; passive zero traffic is insufficient |
| Database and persisted formats | Readers/writers, CDC/ETL/BI/backups, retention, historical replay, stop-write sequence, reconciliation, and rollback |
| Tests, fixtures, and examples | Test discovery, all relevant test targets, documentation/example builds, distribution contents, and public-example contract review |

## Observation windows

Choose a window from actual system cycles rather than a universal day count:

- cover at least the slowest relevant scheduled or business cycle;
- cover region, tenant, role, environment, platform, and client-version segments;
- cover peak and failure behavior when they affect reachability;
- for disaster paths, use an exercise rather than passive waiting;
- for external APIs and long-lived clients, follow the compatibility and sunset
  policy even if traffic appears to be zero.

Declare the start, end, telemetry gaps, and what the window did not cover.
