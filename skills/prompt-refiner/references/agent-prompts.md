# Agent prompts

Read this file only for prompts that control an agent, system, developer
instruction, AGENTS.md, tool, or workflow.

## Authority

Preserve explicit authorization and approval boundaries. Do not infer that a
request to improve autonomy authorizes external writes, destructive actions,
purchases, credential changes, or scope expansion.

When the source is ambiguous, distinguish:

- read-only work such as answering, explaining, reviewing, diagnosing, or
  planning;
- in-scope implementation and non-destructive validation;
- external, destructive, costly, privileged, or scope-expanding actions.

A scoped approval may cover routine work only when the source clearly permits
that interpretation. If changing the approval cadence would alter a deliberate
security, audit, production, or compliance control, preserve it or ask.

## Capabilities and tools

Include only capabilities confirmed by the source or known target environment.
Do not add parallel execution, subagents, programmatic tool calling, MCP,
browsing, shell access, or a named product feature merely because it might help.

When tools are confirmed and their routing matters, define:

- what each tool provides and when it applies;
- prerequisites and authoritative return fields;
- how to handle empty, partial, stale, or suspicious results;
- a bounded fallback when the primary path fails.

Prefer clear tool names, parameters, types, enums, and return states over long
usage examples. Let the interface communicate behavior where possible.

## Workflow and communication

Prefer an outcome and completion bar over a prescribed implementation sequence.
Add sequencing only when order is load-bearing.

For long-running work, define meaningful update points only if the product or
user needs them. Do not require narration before every routine action.

Unless the source explicitly ties a rule to safety, audit, production, or
compliance:

- replace “explain every tool call” with updates at meaningful phase changes;
- do not let “minimize tool calls” outrank correctness, evidence, or validation;
- rewrite a blanket command ban when inspection, diagnosis, or validation
  requires commands, limiting commands to relevant and non-destructive uses.

If the target environment truly lacks shell or tool access, preserve that
capability limit instead of inventing access.

Use bounded stopping behavior when the source otherwise asks the agent to search,
retry, or polish indefinitely. Stop when the objective is supported, further
work cannot materially improve the result, or progress requires a user decision,
permission, credential, or external state change.

## Validation

Ask for the smallest validation capable of catching a meaningful failure:
targeted tests, schema checks, lint, build, calculation, rendering, citation
check, or a minimal smoke test. Require broader validation only when risk or the
requested completion bar justifies it.
