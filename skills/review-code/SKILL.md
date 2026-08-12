---
name: review-code
description: Review supplied code, pull-request patches, commits, or diffs for correctness, readability, architecture, security, and performance. Use when the user asks to review, audit, assess, inspect, critique, or identify risks in code changes across any language or repository. Report only evidence-based, concrete, actionable findings; remain read-only unless implementation is explicitly requested.
---

# Review Code

Review the requested code against its intended behavior and surrounding system. Prioritize defects and material engineering risks over commentary. Remain read-only unless the user explicitly requests implementation.

## Establish Scope and Context

- Identify the exact review target: supplied snippet, files, working-tree diff, staged diff, commit range, or pull request.
- Read applicable repository instructions and recover the intended behavior from the request, tests, interfaces, documentation, configuration, and existing conventions.
- Inspect complete enclosing functions, classes, and modules rather than judging isolated changed lines.
- Follow relevant callers, consumers, data flows, state transitions, authorization boundaries, dependencies, and failure paths far enough to determine actual behavior.
- Inspect related tests and analogous code when they provide decision-relevant evidence. Do not expand into an unfocused repository audit.
- If only a standalone snippet is available, state which conclusions are limited by missing surrounding context.

## Review Workflow

1. Recover the behavioral contract and identify what must remain unchanged.
2. Trace each suspicious path from a realistic input or state through the code to its observable outcome.
3. Challenge the suspected issue with counterexamples, guards, upstream validation, downstream handling, and tests.
4. Evaluate the surviving risks across all five axes.
5. Run the smallest relevant non-destructive checks when they materially resolve uncertainty and are allowed. Never claim a check passed if it was not run.
6. Report only findings that are specific, actionable, and supported by the inspected evidence.

## Review Axes

- **Correctness** — Find bugs, missing edge-case handling, invalid state transitions, incorrect error handling, concurrency hazards, broken contracts, and behavioral regressions.
- **Readability** — Flag unclear naming, control flow, duplication, or unnecessary complexity only when it materially increases misunderstanding, defect risk, or maintenance cost.
- **Architecture** — Check responsibility boundaries, coupling, cohesion, dependency direction, interface ownership, and consistency with the surrounding design.
- **Security** — Check input trust boundaries, validation and encoding, authentication and authorization, secret or personal-data exposure, injection paths, unsafe deserialization, insecure defaults, and privilege expansion.
- **Performance** — Check algorithmic cost, repeated or unnecessary work, blocking and contention, unbounded growth, excessive I/O or allocation, resource lifetime, and bottlenecks that are plausible for the actual workload.

Assign each finding one primary axis. Mention a secondary axis only when it changes the impact or recommended fix.

## Evidence and Uncertainty Gate

Report a finding only when all of the following are available:

- a precise code location;
- a realistic triggering input, state, or call path;
- a causal explanation of the resulting behavior;
- a material impact; and
- a feasible direction for correction.

Do not report hypothetical failure modes unsupported by the code or surrounding context. Put unresolved but relevant unknowns under validation gaps instead of presenting them as defects.

Label each finding's certainty:

- **Confirmed** — Direct inspection, a reproduction, or a test establishes the behavior.
- **High confidence** — The code and surrounding context establish the causal path, but it was not executed during review.
- **Conditional** — The issue depends on an explicitly named runtime, input, configuration, or caller condition. Include it only when that condition is supported by evidence, and state how to verify it.

Severity follows demonstrated impact and reachability, not diff size:

- **Critical** — Reachable exploitation, catastrophic data loss, safety failure, or broad service compromise.
- **High** — Likely major incorrect behavior, security exposure, outage, or regression affecting important users or systems.
- **Medium** — A realistic bounded failure or material architecture/maintenance risk that should be fixed.
- **Low** — A concrete, limited-impact problem worth fixing; never use Low for cosmetic preference alone.

Avoid purely stylistic comments, personal preferences, praise, and issues outside the requested scope. Do not inflate severity to compensate for uncertainty.

## Output Contract

List findings first, ordered by severity and then by code location. Use this exact field structure for every finding:

```markdown
### Short actionable title

- Severity: Critical | High | Medium | Low
- Axis: Correctness | Readability | Architecture | Security | Performance
- Location: `path/to/file.ext:line` or the narrowest available symbol/diff hunk
- Problem: Describe the faulty behavior and its realistic trigger.
- Impact: Explain the observable consequence and affected scope.
- Recommended fix: Describe the smallest complete correction and any test needed to prevent regression.
- Certainty: Confirmed | High confidence | Conditional — cite the supporting evidence or exact condition.
```

Keep separate root causes as separate findings. Combine repeated manifestations only when they share the same cause and fix.

After the findings, add `Validation gaps and residual risks` containing only material missing context, checks not run, environment limitations, or risks that could not be resolved. Distinguish `not run` from `failed`.

If no finding passes the evidence gate, say exactly: `No actionable issues found in the reviewed scope.` Then identify any validation gaps or residual risks; do not invent a finding to fill an axis.

## Authorization Boundary

Treat invocation of this skill as authorization to inspect and report, not to modify. Do not edit files, apply patches, reformat code, stage or commit changes, push branches, deploy, or alter external systems unless the user explicitly requests implementation or that specific action. If implementation is requested, preserve unrelated changes and limit edits to the authorized findings.
