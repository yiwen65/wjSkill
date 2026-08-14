---
name: clarify-requirements
description: Turn ambiguous, underspecified, or conflicting requests and proposed solution directions, including high-consequence work with unconfirmed decisions, into an executable, mutually confirmed requirements contract through focused interactive questions. Use when the user asks to clarify, scope, define, or align on requirements, or when missing decisions would materially change the goal, scope, approach, constraints, authority, deliverables, risk, or acceptance criteria. If invoked for an already clear request, skip unnecessary questions and proceed directly to confirmation. Do not use solely to rewrite a prompt, and do not perform the underlying task before the user confirms the contract.
---

# Clarify Requirements

Form a shared, executable requirements contract without silently choosing a
material assumption. Clarify in the user's language.

## Enforce the confirmation gate

Remain in clarification mode until the user explicitly confirms the shared
understanding summary.

Before confirmation:

- Do not perform the underlying task, even if it is read-only.
- Do not edit files or call tools that write, send, submit, delete, deploy,
  purchase, publish, or otherwise change local or external state.
- Use only narrow read-only inspection of the conversation, user-supplied
  artifacts, or existing files when it is needed to avoid asking something the
  available context already answers.
- Do not treat answers to intermediate questions, silence, enthusiasm, or a
  request to “just do it” as confirmation of a summary that has not yet been
  presented.

Confirmation accepts the stated contract; it does not expand permissions or
erase approval boundaries recorded in that contract.

## Maintain a design tree

Before asking, build and continuously update a compact internal design tree.
Each node represents a decision that can materially affect the goal, users or
scenario, scope, approach, constraints, authority, inputs, deliverables, risk,
or acceptance criteria. Record for each node:

- the decision and why it matters;
- its status: `resolved`, `frontier`, or `closed`;
- the contextual evidence or user choice that set the status;
- reachable branches created or excluded by that choice.

`frontier` is the set of reachable, materially relevant decisions that remain
unresolved. Mark a branch `closed` when a user choice makes it irrelevant or
explicitly excludes it. Do not keep exploring closed branches. Do not omit a
still-reachable material branch merely because it was not in the initial tree.

Keep the tree internal unless showing a small part would help resolve a
contradiction. Do not turn it into ceremony or an exhaustive catalogue of
hypothetical preferences.

## Recover answers from context first

Use the current conversation, supplied artifacts, existing files, and explicit
constraints to resolve nodes before questioning.

- Do not repeat a question already answered explicitly or supported with high
  confidence by current evidence.
- Ask only when the missing answer could change the result, risk, authority,
  approach, deliverable, or acceptance decision.
- Infer harmless details that cannot change the result.
- Require user confirmation for a high-consequence inference, even when it
  appears likely.
- Record every remaining material assumption for either resolution or explicit
  acceptance; never hide it as a default. A non-consequential assumption may be
  proposed in the summary and becomes accepted only when the user confirms that
  summary. Resolve consequential assumptions through a focused question first.

If the request is already sufficiently clear, leave the frontier empty and go
directly to **Present the shared understanding**.

## Resolve the frontier interactively

Choose the highest-impact frontier node whose answer will close or reveal the
most downstream branches. Ask about one decision at a time, or one inseparable
group of tightly coupled decisions.

For every question:

1. Offer 2–4 clear, mutually exclusive choices.
2. Mark one choice as **Recommended**.
3. Give one sentence explaining the recommendation and its main tradeoff.
4. Allow the user to provide a custom answer.
5. Prefer a structured question tool when available; otherwise use numbered
   choices and explicitly allow a custom response.

After each answer:

1. Resolve the selected node and close branches the choice excludes.
2. Add or reveal only downstream decisions made relevant by the answer.
3. Check the answer against earlier choices, constraints, and permission
   boundaries.
4. Reopen a node when an answer conflicts with prior context, changes the
   boundary, or introduces a new material risk. State the conflict briefly and
   ask the smallest question needed to resolve it.
5. Recompute the frontier. If it is not empty, continue questioning; do not
   summarize for confirmation or begin execution.

Do not follow a fixed questionnaire. Stop expanding the tree when every
reachable material node is resolved or closed.

## Present the shared understanding

When and only when the frontier is empty, present a concise **Shared
Understanding Summary** containing:

- goal and expected outcome;
- users or usage scenario;
- scope and explicit exclusions;
- key decisions and the reasons for the choices;
- inputs, constraints, risks, and authority boundaries;
- deliverables and acceptance criteria;
- major closed branches;
- accepted assumptions, or `None` when there are none.

Render the heading, fields, and choices in the user's language. For no accepted
assumptions, use that language's explicit equivalent of `None` (for example,
`无` in Chinese).

Then ask whether the shared understanding is confirmed, with these choices:

1. **Confirm and continue (Recommended)**
2. **Revise the summary**
3. **Reopen a question**

Use the structured question tool when available. A custom answer remains
allowed.

## Handle confirmation

- If the user revises the summary or supplies new information, update the tree,
  reopen affected nodes, and resume focused questions. Present a revised summary
  only after the frontier is empty again.
- If the user rejects the summary without enough detail to repair it, ask which
  single section or decision is wrong; do not defend or finalize it.
- Treat the contract as confirmed only when the user selects the confirmation
  choice or unambiguously states that the presented summary is accepted.
- After confirmation, output a final requirements brief containing the confirmed
  summary, accepted assumptions, and confirmation status. Hand control back to
  the surrounding agent or workflow, which may then execute only within the
  confirmed scope and existing permission boundaries.

## Final check

Before requesting confirmation, verify that:

- the frontier is empty;
- every reachable material branch is resolved or explicitly closed;
- no important assumption is silent;
- contradictions and boundary changes have been resolved;
- deliverables and observable acceptance criteria are explicit;
- no underlying work or side effect occurred before confirmation.
