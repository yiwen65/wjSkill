---
name: tdd
description: Implement features and bug fixes test-first through observable Red-Green-Refactor cycles. Use when the user explicitly requests TDD, test-first development, red-green-refactor, or a failing regression test before a bug fix. Do not use merely because the user asks to add, run, or repair tests after implementation.
---

# Test-Driven Development

## Outcome

Deliver the requested behavior in small vertical slices. Every production
behavior change must be justified by a test observed failing before the change
and passing afterward. Keep the resulting tests as durable behavioral
specifications.

Follow the repository's instructions and existing test conventions. Read
relevant ADRs or `CONTEXT.md` files when present so test names and public
interfaces use the project's domain language.

## Establish the next behavior

Turn the request into the smallest observable example that moves the task
toward completion. For a bug, reproduce the reported failure with a regression
test. For a feature, express one externally meaningful capability.

Choose the lowest stable public seam that proves the behavior, such as a public
function, service method, HTTP endpoint, CLI, or user interaction. Infer the
seam from the current code, tests, and requirements. Ask the user only when the
expected behavior is ambiguous or competing seams would materially change the
public API, architecture, scope, or acceptance criteria.

Read [references/test-quality.md](references/test-quality.md) when choosing the
test level or correcting a weak, brittle, or tautological test. Read
[references/test-doubles.md](references/test-doubles.md) only when the behavior
crosses an external or nondeterministic boundary.

## Run one Red-Green-Refactor cycle

1. **Red** — Write one focused test for the next behavior and run the narrowest
   command that exercises it. Confirm it fails for the expected reason because
   the behavior is missing or wrong. A compile or type failure is valid only
   when the requested public API does not exist yet; unrelated syntax, import,
   fixture, or environment failures are not a valid red.
2. **Green** — Make the smallest production change that satisfies the test. Do
   not skip the test, weaken its assertion, encode test-only behavior, or expand
   into unrequested functionality. Re-run the same test and confirm it passes.
3. **Refactor** — Improve names, duplication, structure, or test clarity only
   while behavior stays unchanged. Re-run the focused test after refactoring.
4. Repeat with the next observable slice. Let each completed cycle inform the
   next test instead of writing a batch of tests for imagined behavior.

If testability requires a new seam, make the smallest behavior-preserving
preparatory change with the existing suite green, then begin the red step. Do
not hide feature behavior inside that preparation.

If the test cannot run, repair an in-scope test or environment problem when it
is safe to do so. Otherwise stop before implementation and report the exact
blocker; do not claim a red or green result that was not observed.

## Test quality invariants

- Assert observable behavior through stable interfaces, not private methods or
  incidental call sequences.
- Derive expected results independently from the implementation, using a
  requirement, worked example, invariant, or known-good fixture.
- Keep each test focused on one behavior. Use multiple assertions when they
  jointly describe that behavior; do not split tests to satisfy an assertion
  count rule.
- Prefer real internal collaborators. Replace only boundaries that are external,
  nondeterministic, slow, destructive, or otherwise unsuitable for the test.
- Keep tests deterministic, readable, and sensitive to a realistic wrong
  implementation.

## Completion evidence

Run every focused test used in the cycles, then the smallest relevant broader
suite justified by the change's risk and repository conventions. Report:

- the behavior delivered and production files changed;
- the red evidence for each cycle: command and expected failure reason;
- the corresponding green result and final validation commands;
- any untested path or validation that could not be completed.

Do not describe the work as TDD when production behavior was written before its
failing test or when the red state was not actually observed.
