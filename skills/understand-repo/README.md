# EDRU Repository Understanding

EDRU uses traceable evidence to create or update knowledge about the executable topology, critical paths, boundaries, state, and change impact of large or unfamiliar repositories. `operation: create | update` controls the asset lifecycle; `mode: survey | takeover | change-ready` controls analysis depth. See `SKILL.md` for the core contract and invocation boundaries.

## Resources

- `references/takeover-protocol.md`: execution checkpoints for complex takeovers and `change-ready` work;
- `references/update-protocol.md`: lineage, invalidation, retention, and full-rebaseline rules for every update;
- `templates/`: output templates loaded by asset type;
- `schemas/`: machine-validation contracts for manifests, claims, evidence, and readiness data;
- `examples/`: minimal examples used only when structure remains unclear;
- `scripts/validate_edru_assets.py`: asset structure validator;
- `evals/evals.json`: behavioral evaluation cases for routing, authority, and evidence boundaries;
- `references/method-sources.md`: methodological sources and boundaries, loaded only when requested.

## Validate assets

```bash
python3 scripts/validate_edru_assets.py /path/to/.edru --operation create --mode takeover
python3 scripts/validate_edru_assets.py /path/to/.edru --operation update --mode takeover
```

A passing result means only that required files exist, lifecycle metadata is coherent, and basic formats are parseable. It does not prove that repository conclusions are true or that an update found every affected dependency.

## Usage examples

- Create a reusable baseline: `Use $understand-repo with operation create and mode takeover. Persist the assets under .edru.`
- Refresh after repository changes: `Use $understand-repo with operation update and mode takeover. Update the existing .edru assets from the recorded revision to current HEAD.`
- Refresh before one planned change: `Use $understand-repo with operation update and mode change-ready for changing <target>. Refresh the existing .edru baseline first.`
