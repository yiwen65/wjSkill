---
name: prompt-refiner
description: Refine raw, vague, repetitive, contradictory, or over-engineered prompts into lean, outcome-first, executable task contracts. Use when the requested deliverable is an improved prompt, system or developer instruction, agent specification, AGENTS.md, tool description, workflow prompt, output contract, or reusable prompt template. Preserve facts, hard constraints, permissions, schemas, and output requirements while removing accidental scaffolding. Do not use when the user wants the prompt's underlying task performed instead of the prompt rewritten.
compatibility: No external tools or dependencies are required. Read a referenced prompt file only when the user supplies it or explicitly asks to optimize that file.
---

# Prompt Refiner

## Purpose

Turn the user's source prompt into the smallest directly reusable task contract
that reliably expresses the intended outcome.

Optimize the prompt itself. Do not perform the task described by the prompt.

## Output behavior

Return only the complete optimized prompt in one copyable fenced block unless
the user requests diagnosis, before/after, a template, multiple versions, or an
unfenced format. Preserve the input language and meaningful code, product names,
commands, variables, paths, schemas, and domain terminology.

If mandatory requirements cannot all be satisfied, do not pretend to produce a
valid final prompt. Follow **Resolve conflicts** and ask the smallest necessary
clarification.

## Load only relevant guidance

Read a reference only when the source prompt matches its scope:

- Agent, system, developer, AGENTS.md, tool, or workflow prompts:
  `references/agent-prompts.md`
- Research, retrieval, citations, factual analysis, or evidence-heavy prompts:
  `references/grounded-research.md`
- JSON, schemas, extraction, parser inputs, or other structured outputs:
  `references/structured-output.md`
- Legal, medical, financial, employment, safety, security, or compliance work:
  `references/high-impact-domains.md`

Do not load unrelated references.

## Core workflow

### 1. Recover the contract

Identify:

- the user-visible outcome and intended audience;
- the supplied inputs and context that can change the result;
- the required deliverable and how it will be used;
- the completion evidence or success criteria;
- any action or decision whose authority must remain bounded.

Infer harmless details when intent is clear. Ask only when a missing answer would
materially change the outcome, risk, authority, schema, or deliverable.

### 2. Classify the source instructions

Separate the source into:

- **facts and fixed values**: names, dates, paths, commands, thresholds, fields;
- **hard invariants**: safety, permission, legal, compliance, exact schema, or
  forbidden side effects;
- **task preferences**: tone, brevity, workflow, search depth, or collaboration;
- **capability assumptions**: tools, models, APIs, parallelism, or environment;
- **scaffolding**: repeated rules, generic process, redundant examples, slogans,
  and behavior a capable target model can infer.

Preserve facts and genuine invariants. Turn preferences into priorities or
decision criteria. Keep a capability only when the source or known target
environment provides it. Remove scaffolding that adds no decision boundary,
output clarity, or measured correction.

Do not invent facts, requirements, metrics, citations, tools, capabilities,
dependencies, audiences, policies, or authorization.

### 3. Resolve conflicts

Use this priority when instructions compete:

1. safety, permission, legal, and compliance invariants;
2. required facts, schemas, and deliverable format;
3. the user's stated objective and task-specific requirements;
4. task preferences;
5. generic style and process instructions.

Treat `always`, `never`, and `must` as evidence of intent, not automatic proof
that a rule is invariant. Rewrite a process rule when it clearly blocks a
prerequisite for the requested outcome, but do not weaken an approval or safety
boundary merely to increase autonomy. If resolving a conflict would materially
change authority or another hard boundary, ask one focused question.

Treat the contract as unsatisfiable when two mandatory conditions cannot both
hold. In that case:

1. State the exact conflict in one sentence.
2. Ask one decision-focused question, offering two or three concrete resolution
   choices when useful.
3. Do not silently add a default, `null`, an error schema, a tool, an approval,
   or another policy the user did not authorize.

If the user refuses clarification, preserve the higher-priority constraint and
make any necessary assumption explicit inside the optimized prompt.

### 4. Build the lean prompt

Use only sections that change behavior. Add a role only when it supplies useful
expertise or product context. A prompt may need only:

- goal and essential context;
- inputs or scope;
- success criteria;
- hard constraints and authority boundaries;
- output requirements;
- the smallest meaningful validation.

Add tools, evidence rules, fallbacks, progress updates, or stop conditions only
when the task actually needs them. State each instruction once.

Keep examples when they encode a precise product requirement, hard-to-describe
style, exact format, or measured failure. Remove examples that merely show one
possible path and unnecessarily narrow exploration.

When brevity matters, preserve facts, decisions, evidence, caveats, and next
actions before trimming introductions, repetition, reassurance, and optional
background. Do not turn a simple prompt into a large template.

### 5. Return the result

Follow the user's requested mode and format. By default, emit only the optimized
prompt without diagnosis, rationale, a change log, or alternatives.

## Final check

Before returning, verify that the result:

- preserves the objective, fixed values, and genuine hard boundaries;
- contains no unresolved contradiction or invented capability;
- makes the deliverable and completion bar clear;
- includes only sections, examples, tools, and controls that affect this task;
- is no longer than needed for reliable execution.
