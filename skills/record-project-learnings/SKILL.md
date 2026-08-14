---
name: record-project-learnings
description: Record verified, reusable lessons from mistakes, misdiagnoses, failed approaches, and wasteful detours that actually occurred during a project task, then safely merge them into the project root LEARNS.md. Use after an agent fixes or conclusively resolves such a problem, at task wrap-up, or when the user asks to capture lessons learned; also use when deciding whether a task failure is durable enough to document. Do not use for routine exploration, unresolved guesses, or generic retrospectives without task evidence.
---

# Record Project Learnings

Capture only lessons that can prevent a future agent from repeating a verified
project-task failure. Keep the main task primary; recording a lesson does not
prove that the task itself is complete.

## Apply the evidence gate

Record a lesson only when every condition holds:

- The mistake, misdiagnosis, failed approach, or avoidable detour actually
  occurred in the current task.
- Task evidence confirms what failed, why it failed, and what corrected or
  decisively resolved it. Do not convert temporal sequence or a plausible theory
  into causation.
- The lesson could change how a future task is executed in this project or a
  clearly named sub-scope.
- A future agent can recognize the same situation and take a concrete preventive
  action.

Do not record routine exploration, expected iteration, harmless command typos,
one-off transient environment failures, unresolved hypotheses, observations
without a correction, generic advice, or details unlikely to affect future work.
When no candidate passes the gate, leave `LEARNS.md` unchanged and do not invent
a lesson to create activity.

## Respect project and task boundaries

1. Resolve the project root from the user's explicit scope, then the active
   workspace or repository root. Do not write into a parent repository merely
   because the task touches a nested project.
2. Read every applicable `AGENTS.md` and contribution rule before editing.
3. Treat review-only, diagnosis-only, read-only, or file-scope restrictions as
   prohibiting this write unless the user explicitly authorizes it. If a
   governing rule blocks or limits `LEARNS.md`, do not write and briefly report
   why.
4. Never include passwords, tokens, keys, personal information, internal
   credentials, secret locations that expose them, or complete sensitive logs.
   Retain only the minimum sanitized signal needed to recognize the problem.

## Merge before adding

1. If `<project-root>/LEARNS.md` exists, read it before drafting. Search for the
   same scope, failure mode, cause, signal, correction, and prevention even when
   the wording differs.
2. Handle the closest existing entry as follows:
   - If it already conveys the same actionable lesson, make no change.
   - If it is incomplete, add only the newly verified fields or sharper scope.
   - If current evidence disproves part of it, surgically correct that part and
     retain useful history when it remains relevant.
   - If candidates overlap, merge them into one concise entry instead of adding
     another.
3. Preserve the user's headings, ordering, prose style, and unrelated entries.
   Do not reformat or rewrite the file globally.

## Write an actionable entry

Follow the existing file's format when one is established. Otherwise, create
`LEARNS.md` with this minimal structure and use it for new entries:

```markdown
# Project Learnings

## `<applicable scope>` — <concise lesson>

- Wrong approach: <what was tried>
- Why it failed: <verified cause>
- Recognition signal: <observable symptom or evidence>
- Correct approach: <what worked or was conclusively established>
- Prevention: <command, check, or decision a future agent can apply directly>
- Verified by: <smallest sanitized evidence that confirms the lesson>
```

Keep each entry brief and project-specific. Narrow the applicable scope whenever
the evidence does not support a project-wide rule. Refer to concise commands,
paths, test names, or error fragments only when they are necessary and safe.

## Finish safely

Write only after the related problem is resolved or while wrapping up the task,
so the note does not interrupt diagnosis or repair. Read the resulting entry
back, confirm that it passes the evidence gate, check for duplication and secret
leakage, and inspect the focused diff to ensure unrelated content is unchanged.
Then finish and validate the main task independently. Report whether a lesson
was added, merged, corrected, skipped as non-reusable, or blocked by project
rules.
