---
name: code-debug
description: Diagnose and, when authorized, fix software defects through objective reproduction, first-divergence localization, falsifiable experiments, causal root-cause proof, minimal patches, and regression verification. Use when a user reports or asks to debug/root-cause/fix a crash, failing test, wrong result, regression, flaky or concurrent failure, leak, performance regression, or environment-specific bug. Do not use for speculative code review, feature implementation, or repairing a test when no product behavior is known to be wrong.
---

# Code Debug

## Outcome

Turn a reported failure into either:

- a verified minimal fix with regression protection; or
- a bounded diagnosis that states the strongest proven facts, unresolved
  hypotheses, missing evidence, and exact next discriminating action.

Treat debugging as a stateful search for the first meaningful difference between
a good execution and a bad execution. Make every material action exclude a
cause, establish a fact, narrow the failure boundary, test a hypothesis, or
verify the causal link between the root cause and the fix.

## Preserve authority and evidence

- Interpret requests to explain, investigate, diagnose, or find the root cause
  as read-only authority. Add or change code only when the user also authorizes
  a fix or diagnostic modification.
- Read applicable repository instructions and preserve unrelated user changes.
  Keep temporary logs, assertions, switches, tests, and debug configuration
  isolated from the production fix and remove them unless they provide durable
  protection or observability.
- Separate `FACT` (observed), `HYPOTHESIS` (testable explanation), `ASSUMPTION`
  (temporarily accepted), and `QUESTION` (unresolved). Never promote a
  hypothesis because it was repeated or because a patch made the symptom vanish.
- Ask only when missing expected behavior, scope, environment, destructive
  authority, or acceptance criteria would materially change the investigation.

## Run the evidence loop

### 1. Define the failure

Recover the smallest objective contract:

- expected behavior and observed behavior;
- their precise delta and triggering conditions;
- affected inputs, versions, modules, and frequency;
- environment, revision, and relevant recent changes;
- a PASS/FAIL oracle and the cheapest command or action that evaluates it.

Do not proceed on descriptions such as "it is broken" when an observable oracle
can be established from tests, logs, traces, exit codes, responses, state, or
measurements.

### 2. Establish a bad baseline

Reproduce with fixed input, environment, revision, command, and oracle. Record
the return code, decisive output, duration, and result. Obtain a known-good run,
version, input, or environment when practical.

For intermittent failures, repeat enough times to record `runs`, `failures`, and
the observed failure rate. Reduce nondeterminism by fixing seeds and time,
isolating external state, saving inputs and schedules, or using record/replay,
dumps, or traces.

Do not change production behavior or enter a formal fix until one of these is
available:

- a repeatable failure;
- a measured statistical failure with a useful comparison oracle; or
- a captured failure that can be replayed or inspected causally.

If none is attainable within the authorized environment, stop at a bounded
diagnosis. Report what was attempted and what evidence or access would unblock
the next step; do not claim a root cause or verified fix.

### 3. Minimize when it improves the search

Remove one input field, step, dependency, configuration, dataset portion, time
window, or call-path segment at a time. Keep a reduction only when the failure
oracle still triggers. Stop when another reduction removes the failure or costs
more than the localization benefit.

Preserve the shortest reliable reproducer, the minimal relevant dependencies,
and the exact trigger discovered. Do not make minimization a ritual when the
failure boundary is already cheap and precise.

### 4. Locate the first divergence

Compare good and bad executions at meaningful module or state boundaries. Use
binary search over a call chain, commit range, pipeline, or time interval instead
of reading the repository linearly.

When a value is wrong, trace backward through readers and writers:

`final symptom <- propagated bad state <- first bad write <- triggering condition`

Prefer existing traces, structured logs, assertions, watchpoints, data
breakpoints, sanitizers, profilers, dumps, and boundary input/output comparisons.
Add instrumentation only when it distinguishes competing hypotheses. Record the
last known-good point, first known-bad point, and the evidence at each.

### 5. Test falsifiable hypotheses

Maintain a small ranked hypothesis set. For each candidate, state:

- the observation it explains and supporting or contradicting evidence;
- what must be observed if it is true and if it is false;
- one experiment that can distinguish those outcomes;
- its cost, invasiveness, and likely information gain.

Run the lowest-cost, highest-information experiment first. Change one primary
variable per experiment. Classify the result as `supported`, `rejected`, or
`inconclusive`; supported means the candidate survives, not that it is proven.
Record new facts and the next action before continuing.

Reject experiments whose outcomes cannot distinguish the hypothesis, which
change several causes at once, or which merely suppress timing or symptoms, such
as an unexplained sleep or terminal null check.

### 6. Prove the root cause

Call a cause proven only when the available evidence jointly shows:

1. it explains the trigger, good/bad difference, and final symptom;
2. controlling the causal variable makes the failure appear or disappear, or an
   equivalent discriminating experiment demonstrates causality;
3. the local chain from cause to first bad state to observed failure is complete;
4. the leading alternative explanations have contrary evidence; and
5. the proposed repair point acts on the cause rather than masking its last
   symptom.

If experiments stop shrinking the search space, improve observability, redefine
the failure, or report the blocker instead of continuing low-information work.

### 7. Encode the regression and fix only when authorized

Capture the reproducer at the lowest stable behavioral seam. Before changing
production behavior, run it against the faulty code and observe failure for the
expected reason. A syntax, fixture, import, dependency, or unrelated environment
failure is not regression evidence.

Implement the smallest change that corrects the proven cause. Do not mix in
refactoring, broad renaming, formatting, unrelated API changes, or speculative
hardening. Expand the repair only when evidence shows that a local patch cannot
preserve the real contract, such as an invalid ownership model, concurrency
protocol, or public API that permits illegal states; keep direct repair and
structural work separately reviewable.

If durable automated regression coverage is impossible, preserve the smallest
available replay or deterministic check and disclose the gap. Do not describe
the task as fully complete without a credible way to detect recurrence.

### 8. Verify in risk order

Run and record the smallest checks that establish each applicable layer:

1. **Failure** — the original input, environment, and path now satisfy the oracle.
2. **Regression** — the guard failed before the fix and passes after it.
3. **Neighbors** — relevant boundaries, similar inputs/configurations, repeated
   runs, error paths, or concurrency paths still behave correctly.
4. **System** — the justified unit/integration suites, type checks, linters,
   build, sanitizers, static analysis, benchmarks, or CI subset pass.
5. **Diff** — changes are limited to the causal fix and intentional protection.

Treat `not run` as different from `passed` or `failed`. If a check fails, use the
new evidence to continue debugging; never hide it behind the original success.

## Completion gates

Do not claim a verified root cause without causal evidence. Do not claim a
verified fix without rerunning the original failure oracle. Do not claim full
completion without a regression guard or an explicitly disclosed, justified
substitute and residual risk.

Before finishing, ensure the report can answer:

- What exactly failed, and how was failure judged?
- Where did good and bad executions first diverge?
- Which experiment proved the cause and rejected the main alternatives?
- Why does the patch correct that cause with the smallest justified scope?
- What failed before, passed after, and was not run?

## Report the result

Lead with the outcome, then report only sections supported by the work:

```markdown
## Failure
Expected, observed, trigger, oracle, and reproduction command.

## Root cause
Cause, triggering condition, and causal chain to the symptom.

## Evidence
Good/bad comparison, first divergence, decisive experiments, and rejected
alternatives.

## Fix
Changed behavior and why the scope is sufficient and minimal.

## Verification
Before/after regression evidence, commands and results, neighbor/system checks,
and checks not run.

## Residual risks
Uncovered cases, remaining assumptions, blockers, and the next discriminating
action when the task is not complete.
```

Keep process narration brief. Include exact commands, locations, and decisive
outputs when they are needed to make the evidence reproducible.
