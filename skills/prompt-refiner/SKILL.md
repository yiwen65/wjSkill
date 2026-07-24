---
name: prompt-refiner
description: Transform raw, vague, repetitive, contradictory, or over-engineered prompts into lean, outcome-first, executable prompts using GPT-5.6 prompting guidance. Use whenever the user asks to optimize, rewrite, refine, simplify, compress, structure, upgrade, or make reusable a prompt, system prompt, developer instruction, agent specification, AGENTS.md, tool description, workflow prompt, output contract, or prompt stack. Also use when the user provides instructions that are clearly intended for another model and wants a better version. Do not use when the user wants the underlying task completed rather than the prompt itself rewritten.
compatibility: No external tools or dependencies are required. Read a referenced prompt file only when the user supplies it or explicitly asks to optimize that file.
---

# Prompt Refiner

## Purpose

Turn the user's raw prompt into a concise, directly reusable task contract. Make
the destination, constraints, evidence, output, and completion bar clear while
leaving the model room to choose an efficient path.

Optimize the prompt itself. Do not perform the task described by the prompt.

## Default Output

Return only the complete optimized prompt in one copyable fenced block. Do not
add diagnosis, commentary, a change log, or alternative versions unless the user
requests them.

There is one exception: when mandatory requirements are logically incompatible
and no valid prompt can satisfy them, ask one concise clarification instead of
pretending the conflict is solved. A final-prompt-only request does not justify
silently inventing a default or weakening an explicit constraint.

Preserve the input language by default. Preserve mixed-language code, product
names, commands, variables, paths, schemas, and domain terminology when they are
meaningful.

If the user asks for a different mode, follow it:

- `diagnosis`: explain instability, ambiguity, repetition, and missing controls;
- `before/after`: show the source and optimized versions;
- `template`: replace reusable inputs with clear placeholders;
- `multiple versions`: provide distinctly named alternatives;
- `final prompt only`: emit no text outside the optimized prompt.

## Optimization Contract

Preserve before improving:

- the user's actual objective and intended audience;
- explicit facts, values, dates, names, paths, commands, and thresholds;
- required artifact type, language, structure, genre, and output schema;
- genuine safety, permission, evidence, business, and compliance boundaries;
- behavior that is clearly intentional even when it is unusual.

Do not invent facts, requirements, metrics, citations, tools, capabilities,
dependencies, audiences, or policies. Do not silently broaden or narrow the
task.

## Workflow

### 1. Recover the real task

Identify:

- the user-visible outcome;
- the context or input that can change the result;
- what must be true for the task to count as complete;
- which side effects or decisions require a boundary;
- the expected output and how it will be used.

Infer harmless details when the intent is clear. Ask at most two short questions
only when the missing answer would materially change the task, risk, output
format, or authority. Otherwise optimize immediately.

### 2. Separate invariants from judgment

Use absolute rules only for true invariants such as safety limits, required
fields, exact schemas, or forbidden side effects.

Turn judgment calls into decision rules. This is especially important for when
to search, ask a question, call a tool, continue iterating, use a fallback, or
stop.

Preserve explicit user values. When a value is implicit, provide criteria for
choosing it instead of inventing a universal default or keyword map.

### 3. Simplify before adding

Remove or merge:

- repeated versions of the same rule;
- style or process instructions that do not change behavior;
- examples that add no decision boundary or output clarity;
- instructions for behavior a capable model already performs reliably;
- irrelevant tools and tool descriptions;
- verbose reassurance, slogans, and meta-commentary.

Do not remove information merely to make the prompt shorter. Optimize for
behavioral signal per token.

### 4. Resolve contradictions

Find rules that compete over language, autonomy, approvals, tool use, response
length, output format, evidence, or stopping behavior. Resolve them using this
priority:

1. explicit user intent;
2. safety, permission, legal, and compliance constraints;
3. required facts, schemas, and deliverable format;
4. task-specific rules;
5. general style preferences.

Treat source wording as evidence of intent, not automatically as an invariant.
Words such as `always`, `never`, and `must` may be accidental over-constraints.
When the user asks to optimize a prompt, rewrite literal process rules when they
conflict with the requested outcome or with prerequisites needed to achieve it.

Use these general tie-breakers:

- required discovery, inspection, and validation outrank a blanket prohibition
  on commands or tools;
- correctness and required evidence outrank minimizing calls, turns, or tokens;
- concise collaboration outranks narrating every routine action, so use updates
  at meaningful phase changes;
- one scoped approval can cover routine in-scope work, while destructive,
  external, costly, or scope-expanding actions remain separately gated.

When the conflict cannot be resolved safely from context, ask the smallest
necessary question instead of guessing.

Treat a prompt as unsatisfiable when two required conditions cannot both hold.
Common examples include requiring a field, forbidding `null`, forbidding
inference, and allowing the source field to be absent; or requiring an external
action while also prohibiting every available action path.

For an unsatisfiable prompt:

1. Do not generate a supposedly final prompt.
2. State the exact conflict in one sentence.
3. Ask one decision-focused question with two or three concrete resolution
   options when that makes the choice easier.
4. Do not silently add `null`, a default value, an error schema, an approval, or
   another policy the user did not authorize.

If the user explicitly refuses clarification, preserve the higher-priority
constraint and make the necessary assumption visible inside the optimized
prompt. Never present an assumption as if it came from the source request.

### 5. Build an outcome-first contract

Use only the sections that change behavior. A complex prompt may use:

```text
Role: [function and necessary context]

Goal: [user-visible outcome]

Inputs: [provided material and input boundaries]

Success criteria: [conditions that must be true before completion]

Constraints: [safety, permission, business, evidence, and side-effect limits]

Tools: [relevant tools, routing rules, prerequisites, and failure behavior]

Output: [artifact, structure, length, language, and required content]

Validation: [checks that prove the result]

Stop rules: [when to answer, retry, fall back, ask, abstain, or stop]
```

Do not force this structure onto a simple prompt. A short request may need only
the goal, essential context, output requirement, and one meaningful boundary.

### 6. Define autonomy when the prompt controls an agent

Clarify authorization by request type when actions are possible:

- answer, explain, review, diagnose, or plan: inspect and report without
  implementing unless implementation is requested;
- change, build, or fix: make in-scope changes and run non-destructive validation;
- external writes, destructive actions, purchases, credential changes, or
  material scope expansion: require confirmation.

Keep the policy in one place. Do not scatter repeated approval instructions
through the prompt.

### 7. Make tool routing conditional and economical

Include only tools relevant to the task. When tools matter, describe:

- what each tool provides;
- when to use it;
- prerequisites that must not be skipped;
- important return fields;
- how to handle empty, partial, stale, or suspicious results.

Parallelize independent reads; keep dependent work sequential. Require one or
two meaningful fallbacks for suspiciously empty retrieval, but do not create
unbounded tool loops.

Use programmatic tool calling only for bounded deterministic reduction such as
filtering, joining, sorting, deduplication, aggregation, batching, or repeated
validation. Keep approvals, semantic judgment, citations, and final validation
in direct model control.

### 8. Control evidence and retrieval

For grounded work, define:

- which claims require support;
- acceptable source types and freshness;
- where citations should appear;
- how to label inference and source conflicts;
- what to do when evidence is insufficient.

Absence of evidence is not automatically evidence of absence. Narrow the answer
or state the missing evidence instead of guessing.

For creative work, keep supplied facts distinct from newly written language.
Do not invent names, dates, metrics, capabilities, or outcomes to strengthen the
draft.

### 9. Control length by priority

When brevity matters, specify what must survive compression. Preserve facts,
decisions, evidence, caveats, and next actions before trimming introductions,
repetition, generic reassurance, and optional background.

Describe concrete tone choices rather than vague labels. For example, specify
whether to lead with the answer, acknowledge a reported problem, explain
tradeoffs, or omit a sign-off.

Do not add a model-specific verbosity or reasoning setting unless the user is
also designing the API request or explicitly asks for one.

### 10. Add validation and stopping behavior

Define the smallest validation that can catch a meaningful failure. Examples
include targeted tests, schema checks, lint, builds, calculations, citation
checks, rendering, or a minimal smoke test.

For long-running tasks, request a short preamble before the first tool call and
sparse updates only at major phase changes. Do not require narration of routine
steps.

State when the model should:

- answer because the core request is supported;
- retry a transient failure;
- use the smallest useful fallback;
- ask for one missing material fact;
- report a blocker or uncertainty;
- stop rather than continue searching or polishing.

## Special Cases

### Editing and rewriting prompts

Preserve the requested artifact, factual claims, structure, genre, and length
before improving clarity and flow. Do not add claims, sections, or promotional
language unless requested.

### Structured outputs

Preserve exact field names, types, required fields, enums, and error behavior.
Use a strict output contract when the result feeds automation, evaluation, or a
parser. Check that required fields, allowed values, and missing-data behavior can
all be satisfied at the same time; if not, use the unsatisfiable-prompt rule
instead of inventing a schema change or default.

### Coding and agent prompts

Include environment, scope, relevant files, constraints, verification, failure
behavior, and side-effect limits only when they affect execution. Prefer a
verifiable completion bar over a long prescribed implementation sequence.

### High-impact domains

For legal, medical, financial, employment, safety, security, or compliance work,
preserve jurisdiction, source, date, uncertainty, professional-boundary, and
escalation requirements. Ask when a missing high-impact detail would materially
change the result.

## Quality Gate

Before returning the optimized prompt, verify that it:

- preserves the user's intent and explicit values;
- can be copied and used without surrounding explanation;
- defines the outcome and completion bar clearly;
- contains no unresolved contradictions;
- does not preserve a literal process rule that blocks a prerequisite for the
  requested outcome;
- asks for clarification instead of fabricating a resolution when mandatory
  requirements cannot all be satisfied;
- distinguishes invariants from decision rules;
- contains only behaviorally useful sections, examples, and tools;
- defines permissions, evidence, output, validation, and stopping behavior when
  those controls matter;
- avoids invented facts and unnecessary model-specific scaffolding;
- is no longer than needed for reliable execution.
