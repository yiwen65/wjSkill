# EDRU Update Protocol

Read this protocol for every `operation: update`. It governs the lifecycle of persistent EDRU assets without changing the analysis depth selected by `mode` or expanding the authority boundaries in `SKILL.md`.

## 1. Validate the parent baseline

- Locate the existing `manifest.yaml` under the requested `output_root` and parse it before changing any asset.
- Confirm repository identity, parent run ID, parent revision, asset root, analysis mode, scope, and execution envelope. A legacy schema-v1 manifest may be inspected as a migration input, but the new run must emit schema v2 and must not invent missing lineage facts.
- If the manifest is missing, malformed, points to a different repository, or lacks enough snapshot identity to compare safely, stop the update. Ask whether to repair the baseline or run `create`; never silently replace the only copy.
- Treat a dirty working tree as a distinct snapshot. Record a stable fingerprint of the relevant diff or content set; equal `HEAD` values do not imply equal snapshots.

## 2. Open the update run safely

- Create a new run ID and bind it to `parent_run_id`.
- Record `from_revision`, `to_revision`, parent and target dirty-state fingerprints, trigger, ancestry, and changed execution-envelope dimensions.
- Before overwriting, moving, or removing an existing asset, copy the parent manifest and each affected asset to `<output_root>/history/<parent_run_id>/` or another user-specified history subdirectory within `output_root`. Preserve paths relative to `output_root` in `preserved_parent_assets` so the parent view is recoverable and validator-checkable.
- Write only derived EDRU assets. Updating EDRU knowledge does not authorize edits to repository source, configuration, data, generated outputs, or remote systems.

## 3. Compare snapshots and classify change

Compare repository content and every evidence-validity dimension recorded by the parent:

- source symbols, entry points, registrations, and module layout;
- build targets, dependencies, generators, and generated outputs;
- deployment units, runtime wiring, feature flags, and configuration;
- APIs, IDLs, messages, schemas, migrations, and shared-state contracts;
- tests, fixtures, observability, runbooks, and operational dependencies;
- platform, build variant, tool versions, runtime inputs, permissions, and external resources.

Use repository-aware diff and dependency tools where available. Record changed paths and envelope dimensions as evidence; a filename diff alone does not bound semantic impact.

## 4. Expand the invalidation closure

Start from each changed fact and expand conservatively:

```text
changed source, contract, configuration, or envelope dimension
-> generated output or registration
-> reverse build and symbol dependencies
-> contract and shared-state consumers
-> executable topology and critical paths
-> claims, evidence, reports, and readiness gates
```

Also check deletions, renames, moves, dynamic registration, dependency injection, reflection, plugins, RPC, messaging, FFI, cross-repository consumers, and runtime-only wiring. If an edge cannot be bounded, record an unknown; do not treat lack of a static reference as proof that reuse is safe.

## 5. Retain, invalidate, or supersede

Classify every parent claim, evidence record, and generated asset:

- `retained`: its locator, scope, revision applicability, execution envelope, and upstream dependencies remain valid;
- `invalidated`: a changed fact or unresolved impact breaks its applicability; record `invalidated_by` and keep the old record in history;
- `superseded`: newer evidence or a regenerated asset replaces it; link old and new records rather than reusing the old ID as if nothing changed;
- `new`: the target snapshot introduces knowledge with no parent equivalent.

Retained records keep their original evidence IDs and record `inherited_from_run_id`. New observations receive new IDs. Never raise confidence merely because a record survived an update; preserve the original evidence strength unless the current run adds independent corroboration.

## 6. Choose the update strategy

Use `no_op` when repository snapshot and execution envelope are unchanged and validation confirms that all assets remain applicable.

Use `incremental` when the changed set and invalidation closure are bounded. Regenerate every impacted asset and any summary that depends on it; preserve unaffected assets with explicit retention provenance.

Use `full_rebaseline` when a valid parent exists but incremental safety cannot be bounded, including:

- rewritten or divergent history without a trustworthy comparison base;
- broad module moves or major architectural refactoring;
- replacement of root build, deployment, registration, or generation mechanisms;
- widespread public contract, schema, state-ownership, or executable-topology changes;
- critical execution-envelope changes that invalidate most runtime evidence;
- stale locators or dependency edges across a material portion of the parent assets.

A full rebaseline remains an `update` because parent lineage and history are preserved. Record the trigger and reason; do not relabel it as a fresh `create` or pretend it was incremental.

## 7. Refresh according to mode

- `update + survey`: refresh the baseline, topology, modules, boundaries, evidence, unknowns, and readiness view.
- `update + takeover`: also refresh critical paths, state/data ownership, historical risks, and validation/observability assets.
- `update + change-ready`: first refresh the affected baseline, then expand impact closure around the explicit `change_target`; stale parent coverage cannot satisfy the safe-to-modify gate.

If the selected mode is shallower than the parent mode, do not delete deeper parent assets. Preserve them in history and mark current applicability as not reassessed unless the user explicitly requests their refresh.

## 8. Converge and report

- Complete `16-update-summary.md` with lineage, comparison evidence, change inventory, retained/invalidated/superseded records, regenerated assets, strategy, unknowns, and validation results.
- Update the manifest and readiness report only after dependent assets converge.
- Run `validate_edru_assets.py` with both `--operation update` and the selected `--mode`.
- Report structural validation separately from claim truth. A passing structure check cannot prove that invalidation closure is complete.
- Use `completed_with_unknowns` when the update objective is supportable but bounded gaps remain. Use `blocked` when missing lineage, permission, credentials, or an unbounded critical unknown prevents a supportable current view.
