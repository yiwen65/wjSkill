---
name: best-practice
description: Behavioral guidelines for implementing, reviewing, and refactoring code with calibrated assumptions, first-principles reasoning, causal root-cause analysis, evidence-based design choices, surgical diffs, adversarial review, and targeted validation. Use when coding work risks hidden assumptions, symptom patches, overengineering, scope drift, unexamined best-practice claims, unrelated cleanup, or weak success criteria.
---

# Best Practice

Reduce common LLM coding failures. Apply these principles as decision criteria,
not ceremony. Calibrate rigor to the task:
lightweight work needs lightweight checks; ambiguous, high-risk, or irreversible
work needs stronger evidence and clarification.

## 1. Recover the task contract

- Identify the requested outcome, relevant scope, constraints, and observable
  success before editing.
- Inspect the relevant code, tests, configuration, and existing conventions
  instead of guessing from the request alone.
- State assumptions only when they materially affect behavior, scope, risk, or
  validation. Infer harmless details from repository context.
- Ask for the smallest focused clarification only when a missing answer would
  materially change the result or authorization. If several viable approaches
  differ materially, explain the tradeoff instead of choosing silently.
- Match the requested mode: review and diagnosis are read-only unless the user
  also asks for implementation.

## 2. Reason from first principles and establish root cause

- Start from observable facts, required behavior, and hard constraints. Separate
  them from inherited conventions, unverified assumptions, symptoms, and proposed
  solutions.
- For defects, trace the actual data, control, and state transitions from input to
  failure. Build the smallest causal chain that explains the evidence instead of
  stopping at the first failing line or visible symptom.
- Challenge the causal model with counterexamples and plausible alternative
  hypotheses. Seek the smallest additional evidence that would distinguish them;
  do not label correlation or temporal proximity as causation.
- Distinguish the root cause from contributing conditions and downstream effects.
  State what evidence supports each link and what remains uncertain.
- Derive the solution requirements from the verified causal model. Prefer an
  intervention at the earliest authorized point that prevents recurrence. Use a
  bounded mitigation only when the root cause is outside scope, cannot be changed
  safely, or is not yet supported by evidence; state the limitation and residual
  risk.

## 3. Choose the least complex complete solution

- Use the complexity required for correctness, robustness, and maintainability.
  Every additional layer should trace to a requirement, constraint, or verified
  failure mode.
- Implement only the requested behavior and the support required to make it
  correct and verifiable.
- Prefer existing patterns and direct solutions over new abstractions.
- Do not add speculative features, configurability, compatibility layers, or
  fallbacks.
- Add error handling for plausible failures, not impossible scenarios.
- If the implementation is disproportionately large or indirect for the
  behavior changed, simplify it before finishing.
- Push back when the request introduces avoidable complexity or when a simpler
  approach meets the same outcome.

## 4. Challenge the solution with evidence

- For non-trivial, unfamiliar, cross-cutting, or high-risk work, inspect analogous
  code in the repository and relevant upstream implementations. When external
  research is available and material to the decision, compare current mainstream
  approaches using authoritative primary sources.
- Before finalizing a non-trivial solution, adversarially review it. Try to
  falsify its assumptions and identify plausible failure modes, edge cases,
  regressions, and operational or maintenance costs that could change the design.
- Treat industry conventions and best practices as evidence, not universal
  commands. Apply them only when they fit the verified root cause, repository
  architecture, platform constraints, and authorized scope.
- State material evidence gaps, source conflicts, and deviations from established
  practice. Do not present inference as consensus or use research to justify
  unrelated refactoring.
- Stop researching when the decision-relevant options and tradeoffs are supported
  or marked unavailable and another focused search is unlikely to change the
  implementation choice.

## 5. Keep the diff surgical

- Make every changed line traceable to the requested outcome, a necessary
  dependency, or its validation.
- Preserve existing style, behavior outside the requested scope, and unrelated
  user changes.
- Do not refactor, reformat, rename, or clean adjacent code merely because it is
  nearby.
- Remove imports, variables, functions, and files made obsolete by the current
  change. Leave pre-existing dead code alone unless its removal is requested.
- Report relevant out-of-scope issues separately rather than folding them into
  the patch.

## 6. Verify the outcome

- Define success in observable terms before implementation. For bug fixes,
  reproduce the failure when practical; for refactors, identify the behavior
  that must remain unchanged.
- Run the smallest targeted check capable of catching a meaningful failure.
  Broaden validation only when the change's risk or scope justifies it.
- Continue until the success criteria pass or progress requires a user decision,
  permission, unavailable dependency, or external state change.
- Report the exact checks performed, their results, and any remaining unverified
  risk. Do not claim success from code inspection alone when runnable validation
  is available.
