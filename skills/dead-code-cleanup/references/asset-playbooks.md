# Asset Cleanup Playbooks

Read only the sections matching the current candidates. These sequences are
lifecycle defaults; repository contracts and explicit user constraints override
them.

## Local or private code

1. Confirm the compilation, module, feature, and test boundary is closed.
2. Check for side effects, reflection, registration, address-taking, callbacks,
   FFI, serialization, and generated references.
3. Remove the smallest leaf or coherent private chain.
4. Run every affected supported target and focused behavior check.

Compiler-proven unused locals or unreachable statements normally do not require
a production deprecation cycle. Public visibility or dynamic use changes the
playbook.

## Exported packages, libraries, and dependencies

1. Identify package publication, binary consumers, re-exports, optional features,
   examples, scripts, generators, tests, and transitive use.
2. Search organization repositories and package/build registries; confirm owners
   and supported versions.
3. Deprecate or release a compatibility version when external consumers exist.
4. Remove the dependency only after imports, runtime loads, plugins, generated
   actions, license tooling, and all target matrices are clear.
5. Rebuild distribution artifacts and smoke-test installation and startup.

An unused manifest entry can still support a generator, plugin, side-effect
import, optional target, or operator script.

## Feature flags and duplicated implementations

1. Confirm the intended winning behavior and prohibit new evaluations or callers
   of the losing branch.
2. Verify the flag value in every environment and client context; observe both
   evaluation values and state/data differences.
3. Keep migration, dual-read/write, shadow, comparison, or rollback duties until
   their explicit completion criteria pass.
4. Fix the final state and alert on unexpected losing-branch use.
5. Delete the losing branch in a focused change.
6. After the code is fully deployed, remove flag definitions, platform records,
   tests that only protect the old behavior, dashboards, and documentation.

Do not delete a branch merely because a control-plane UI labels the flag stale.

## Public APIs, SDKs, CLIs, and published schemas

1. Freeze new consumers and document the supported replacement.
2. Mark the surface deprecated without changing its current behavior.
3. Inventory consumers by identity and version; notify and migrate them through
   the governing compatibility policy.
4. Publish a sunset only when policy and consumer visibility permit it.
5. Alert on old-surface use throughout the required window.
6. Remove or retain a monitored tombstone as the compatibility model requires.
7. Verify schema, contract, package, mixed-version, upgrade, and rollback paths.

Zero repository references or recent traffic never replaces a public lifecycle.

## Configuration and environment keys

1. Inventory defaults, schemas, configuration services, secrets, environment
   variables, deployment manifests, IaC, CI, startup scripts, and operator docs.
2. Deprecate the key and emit an attributable read warning where authorized.
3. Stop deployment systems from setting it, then fix the intended behavior.
4. Observe all environments and variants.
5. Remove parsing and schema support, then remove IaC and documentation.

Do not remove the parser first; doing so converts an unknown consumer into a
silent behavior change or startup failure.

## Scheduled jobs and operator or repair scripts

1. Check scheduler history, audit logs, runbooks, tickets, bastion/automation
   inventories, and manual invocation paths.
2. Establish expected execution and retention cycles.
3. Pause scheduling while preserving an executable manual recovery path.
4. Observe at least the relevant cycles and exercise the replacement when the
   path is for repair or recovery.
5. Archive required evidence or runnable artifacts before deletion when policy
   calls for it.

Rare use is expected for repair and disaster assets; it is not evidence of death.

## Messages, events, and queues

1. Stop new producers only after identifying event versions, topics, subscribers,
   consumer groups, dead-letter paths, retention, and replay duties.
2. Wait for queues and replay windows to drain or expire.
3. Verify every consumer and the schema compatibility result.
4. Remove consumer compatibility logic only when old messages cannot reappear.
5. Remove the schema or topic last, then clean monitoring and runbooks.

Paused or offline consumers and retained messages are part of the boundary even
when current throughput is zero.

## Database fields and persisted formats

Use the safe direction:

`stop writes -> tolerate/read old data -> wait retention and rollback period -> remove readers -> remove schema`

Before progressing, inventory application queries, migrations, CDC, ETL, BI,
backups, exports, reprocessing, historical data, and rollback versions. Reconcile
data at each behavior-changing boundary. Never combine physical schema removal
with the first application deletion when mixed versions or rollback may exist.

## Framework, reflection, plugins, and generated code

1. Identify the authoritative registration, scan, manifest, template, macro, or
   generator source.
2. Enumerate configured names and runtime variants; inspect the actual production
   profile or existing evidence when authorized.
3. Remove or disable registration before implementation when recoverable.
4. Run startup, discovery, plugin compatibility, generated-artifact, package, and
   supported-profile checks.
5. Edit the source of generated output and regenerate through the project tool;
   do not hand-edit disposable output unless the repository requires it.

An apparently uncalled constructor, class, route, or module may be the framework
entry point itself.

## Low-observability legacy systems

Change the order of work:

1. inventory entry points and supported builds;
2. make builds reproducible;
3. add or recover characterization and startup tests when authorized;
4. establish attributable entry telemetry where authorized;
5. establish recoverable release mechanics; and
6. expand deletion beyond compiler-proven locals only after those foundations
   are credible.

Without these foundations, classify most non-local candidates as insufficient
evidence. Isolation or archival may be safer than deletion.

## Completeness sweep after verified deletion

Check only assets causally tied to the removed behavior:

- callers, registrations, routes, exports, parameters, constructors, interfaces,
  serialization, and initialization;
- direct and transitive dependencies, package metadata, build targets, generated
  actions, licenses, and vulnerability exceptions;
- flags, configuration, IaC, jobs, topics, permissions, secrets, and schemas;
- tests, fixtures, examples, snapshots, docs, architecture records, runbooks,
  alerts, dashboards, and service catalogs.

Preserve any item that still protects, documents, or operates a supported path.
Do not turn this sweep into unrelated repository cleanup.
