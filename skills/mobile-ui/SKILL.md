---
name: mobile-ui
description: Design, critique, or improve mobile app interfaces (iOS/Android) using evidence-graded rules, task × state × condition thinking, and verified findings instead of pretty-picture intuition. Use whenever the user asks to design a mobile screen, page, flow, or component; review, audit, or critique a mobile UI, screenshot, mockup, or design spec; fix mobile navigation, layout, density, typography, color, or touch problems; design loading, empty, error, offline, disabled, or permission states; check HIG, Material, or WCAG conformance, touch targets, contrast, text scaling, or accessibility; or asks for mobile design taste, design-system, or cross-platform consistency decisions. Applies to SwiftUI, UIKit, Compose, React Native, Flutter, and code-free design deliverables. Do not use for desktop-only web UI or for pure code bugs with no design judgment involved.
---

# Mobile UI

Design and judge mobile interfaces as **task flow × state × usage condition**,
not as static pictures. The failure this skill prevents: a screen that looks
right in one happy-path screenshot while failing on touch targets, text
scaling, error recovery, reading order, or dishonest state representation.
Aim for justified design choices verified against real renders, semantics,
and task runs — not for images that merely resemble a good app.

Two calibrations that prevent common overcorrection:

- "Restrained" means no element competes for attention without a job. It does
  not mean deleting content, color, imagery, or containers.
- "Consistent" means identical semantics get identical expression. It does
  not mean titles, warnings, primary actions, and content cards share one look.

## Evidence discipline

Grade every rule, claim, and finding by its basis, and keep the grading with
it:

| Class | Meaning | How to use |
|---|---|---|
| **A** | Official standard or platform guide: WCAG success criteria, Apple HIG, Material, Android/Apple developer docs | Record source, platform, unit, scope, and exceptions. Do not rewrite guides into unconditional laws. |
| **B** | Peer-reviewed research or mature first-hand practice: design-system case studies, NN/g heuristics | State the study's subjects and limits. Do not generalize one experiment into a law for all apps. |
| **C** | Contextual heuristic: aesthetic judgment, project policy, this skill's checklists and weights | Mark explicitly as adjustable strategy, calibrated per project. Never present as an industry standard. |

Two consequences:

- **Units are evidence.** iOS pt, Android dp/sp, CSS px, and screenshot
  pixels are different quantities, and WCAG's 24 CSS px is not a native-app
  24 dp rule (details in references/platforms.md). Record the unit and device
  scale for every measurement. Without runtime coordinates, say "target
  appears too small" — never invent a precise dp value.
- **Unverified is a reportable result.** Evidence comes in three types —
  actual rendering, component/semantic data, and task-run results — and a
  screenshot covers only the first. Mark unchecked claims *Unverified*.
  "It compiles", "looks similar to the mock", and a model's self-score are
  not verification.

## Conflict decision order

When brand, aesthetics, usability, and platform norms compete, resolve in
this order (a C-class acceptance priority — not an instruction to postpone
brand work):

1. Safety, data integrity, critical-task completion, declared accessibility
   commitments.
2. Usability and platform expectations: navigation, back behavior, text
   scaling, insets, system gestures.
3. Brand and aesthetic refinement among the options that survive 1–2.

## Workflow

### Frame (before generating or judging)

- **Task contract**: audience, usage context, key tasks, required
  information, consequences of actions, success/failure criteria.
- **Platform scope**: iOS/Android, minimum OS, target SDK, component library,
  window and input modes.
- **Brand brief**: which traits are fixed versus flexible. "Modern, premium,
  clean" adjectives are not a brief — ask, or record the gap as an assumption.
- **Navigation + state map**: destinations versus actions, back/cancel,
  error recovery, offline, and permission states.
- **References with reasons**: what principle transfers and what must not be
  copied (references/taste.md).
- **Boundary data**: zero/many/long items, long translations, missing images,
  slow network.
- **Validation goals**: which accessibility criteria apply and which failures
  block delivery.

Record missing answers as explicit assumptions. Never silently drop a
requirement to make the design easier to render or prettier to show.

### Generate

- Compare structural alternatives (browse-first versus action-first versus
  status-first) before comparing colors, whenever the organization is
  genuinely uncertain.
- Prefer components with a complete behavior and accessibility contract;
  justify each custom component by why the standard one fails.
- Build states and semantics together with the default view — loading, error,
  and accessibility are not final-polish tasks.
- Use real copy and boundary data, not one-line placeholder text.
- Render early; check proportion, baseline, clipping, density, and themes.
- Check visible bounds, hit regions, and accessibility nodes as three
  separate things.
- Subtract conditionally: remove elements without a job, but confirm content,
  discoverability, and brand roles survived.
- Fix by risk, then regress other states, windows, and text sizes. A fix that
  improves one screenshot while breaking large-text mode is a net loss.

Reference material, loaded only as the task needs it:

- Decision rules R01–R24 with exceptions: references/rules.md
- State design (loading/empty/error/offline/permission/disabled):
  references/states.md
- Units, sizes, contrast, platform adaptation: references/platforms.md

### Verify

Attempt this coverage, then report honestly what was and was not run:

- Key tasks end-to-end: enter, act, go back, cancel, fail, retry, confirm
  result.
- Windows: smallest supported, wide, landscape, split-screen or foldable as
  applicable.
- Content: empty, many, long, missing media, target languages, RTL, input
  methods.
- Display: dark/light, largest supported accessibility text size.
- Keyboard and system bars: focus, errors, and required actions stay
  reachable.
- Assistive technology: names, roles, states, values, reading order, modal
  focus.
- Network: slow, offline, timeout, partial failure, double submit, reconnect.
- Motion: reduced-motion settings still explain state; repeated actions stay
  stable.

Automated audits raise coverage; they do not replace real assistive-tech and
task testing — Apple and Android both state this (class A).

## Reviewing an existing UI

Read references/review.md and references/antipatterns.md. Core contract:

- Every finding follows: location/node → state and device conditions →
  observable symptom → evidence class → user impact → severity (P0–P3) →
  minimal fix → retest method → uncertainty. "Doesn't feel premium" is not
  a finding.
- Blockers — unresolved P0 or critical P1, broken critical tasks, dishonest
  result reporting, unmet declared accessibility commitments — cannot be
  offset by aesthetic scores.
- Apply the weighted rubric only after blockers; report verified lower
  bound – possible upper bound + coverage + blocker list, and keep U
  (unverified) out of the passed column.
- Match symptoms to the anti-pattern library, but treat its root causes as
  diagnostic hypotheses to confirm with runtime evidence, not as statistics
  about how often agents err.

## Deliverables

A design or review deliverable includes: design rationale, platform
differences, component and state definitions, verification evidence,
unresolved issues, exceptions taken, and the score range with its
verification boundary. Save only verified lessons to design memory, each with
the contexts where it does and does not apply.

## Reference map

| Task | Read |
|---|---|
| Checking a choice against decision rules R01–R24 | references/rules.md |
| Reviewing, auditing, or scoring a UI; writing findings | references/review.md, references/antipatterns.md |
| Designing or fixing loading/empty/error/offline/permission/disabled states | references/states.md |
| Sizes, units, contrast, text scaling, iOS/Android differences, windows, insets | references/platforms.md |
| Building a reference library, taste judgment, design comparisons, training loops | references/taste.md |

Load only what the current task needs.

Distilled from the wiki note "Mobile UI Design" (evidence graded A/B/C;
sources accessed 2026-09-01). Keep that grading intact when quoting numbers.
