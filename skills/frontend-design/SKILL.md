---
name: frontend-design
description: Design, review, or repair web interfaces — marketing/landing pages and web apps — with evidence-graded rules and honest verification instead of screenshot intuition. Use whenever asked to design or build a web page, landing page, dashboard, admin, or web app UI; review or improve a web design, mockup, screenshot, or front-end code; fix typography, color, contrast, spacing, layout, hierarchy, dark mode, motion, or responsive problems; design loading/empty/error/success/disabled/permission states; check WCAG contrast, target sizes, reflow, text scaling, or keyboard/focus/screen-reader behavior; evaluate visual styles (minimal, editorial, brutalist, glass, etc.) or design tokens; or remove a generic "AI look" (unjustified purple gradients, everything-in-cards, all-centered layouts, emoji as icons). Applies to hand-written HTML/CSS, any framework, and code-free deliverables. Do not use for native iOS/Android screen design (use mobile-ui) or pure code bugs with no design judgment.
---

# Frontend Design

Design and judge web interfaces in this order: **real task and content first,
then information hierarchy expressed through typography, spacing, and semantic
color, then brand-justified materials and motion — with accessibility,
responsive behavior, and real states verified throughout.**

Two failure modes this skill prevents:

- A page that looks right in one happy-path screenshot while failing keyboard
  users, contrast, reflow, long content, or error recovery.
- The generic "AI look": unjustified purple gradients, everything in cards,
  everything centered, light-gray tiny text, emoji as functional icons —
  decoration with no task or brand reason.

The cure for both is the same: every visual decision must name its job. Taste
is a set of checkable decisions — not a fixed look, and never a license to
override usability. An accessibility pass does not prove aesthetic quality,
and an aesthetic preference never excuses an accessibility failure.

## Calibrations that prevent common overcorrection

These simplifications are wrong in both directions — verify scope before
applying or rejecting a rule:

- **16px is not a WCAG minimum font size.** No universal floor exists; Carbon
  ships 14px for dense productive UI and 16px for expressive reading. Judge by
  reading task, not a magic number.
- **8pt is not a mandatory grid.** A finite spacing scale aids consistency;
  1px borders and 2px optical corrections are legitimate exceptions.
- **44×44px is not a WCAG AA target-size requirement.** AA requires 24×24
  CSS px with exceptions; 44×44 is the AAA enhancement and a fine touch
  default — neither cite it as an AA failure nor stop at AA when touch
  comfort matters.
- **WCAG text spacing (1.5× line height etc.) tests tolerance of user
  overrides, not your default CSS.** Inject the override values and check
  nothing breaks; you are not required to ship them as defaults.
- **Purple, gradients, cards, glass, and system fonts are not inherently
  cheap.** Judge each material by its job, measured contrast, and cost — not
  by category. What deserves retirement is the mismatch, not the material.

## Evidence discipline

Every rule and finding carries its basis — keep the grading attached:

| Class | Meaning | How to use |
|---|---|---|
| **Hard** | Normative requirement in scope, e.g. WCAG 2.2 A/AA | Test against the actual clause, its conditions, and its exceptions; cite the level. Never inflate an AAA enhancement into an AA failure. |
| **Conv** | Engineering/system convention: type scales, spacing scales, token structures chosen for consistency | Project default, adjustable with a stated reason. Testable against project config; not a law of nature. |
| **Taste** | Justified preference: hierarchy, brand, material, and style choices | Name the intent, compare alternatives, check the counterexamples, validate against task and brand. |

Three consequences:

- **Units and context are evidence.** CSS px ≠ device pixels ≠ native pt;
  contrast is measured on the composited background in the actual theme and
  state, not an average over a gradient; a CJK line length is not a
  transliterated Latin one; an 8pt native spacing unit is not a CSS 8px law.
- **Unverified is a reportable result.** A screenshot, a Lighthouse score, or
  a component library's "accessible" claim each covers only part of the
  truth. Mark unchecked claims *Unverified*; never write "tested" for what
  was only looked at.
- The check methods in this skill are working acceptance methods distilled
  from the source methodology — not published experiments and not a
  substitute for a full WCAG audit or real user research.

## Conflict decision order

When brand, aesthetics, and usability compete, fix in this order:

1. **P0 — task failure and accessibility blocks**: content or function lost,
   keyboard/screen-reader paths broken, contrast below Hard thresholds,
   dishonest states, fabricated content presented as real.
2. **P1 — hierarchy and content misleading**: visual weight contradicts task
   priority, comparisons broken, real information hidden for looks.
3. **P2 — brand and refinement**: materials, motion, style coherence.

While any P0 fails, do not spend effort on shadows and glows. A blocker is
never offset by aesthetic polish — and any visual error escalates to P0 when
it breaks a task in the specific product.

## Workflow

### Frame (before generating or judging)

- **Page type**: marketing/landing page versus web application. They have
  different first questions, densities, and success evidence
  (references/aesthetics.md). Do not build an admin like a poster or a
  landing page like an admin.
- **Task contract**: page object, audience, the decision or task the user
  came for, the evidence they must see, the next step.
- **Real content**: actual copy lengths, real numbers, boundary data — long
  titles, empty sets, huge values, errors, missing media. One-line
  placeholder text hides every layout constraint.
- **Brand brief**: which traits are fixed (inherited brand/system) versus
  open. "Modern, premium, clean" adjectives are not a brief — ask, or record
  the gap as an assumption. Do not break familiar interactions for
  originality.
- **Applicable Hard rules**: list the WCAG criteria in scope and which
  failures block delivery (references/accessibility.md).

Record missing answers as explicit assumptions. Never silently drop a
requirement to make the design easier to render or prettier to show.

### Generate

Order matters — each step constrains the next:

1. **Structure and tasks first**: semantic HTML, reading order, one primary
   action per decision region, all states (loading / empty / error / success
   / disabled / permission) designed together with the default view.
2. **Hierarchy through the basics**: named type roles, a finite spacing
   scale, semantic color roles, shared alignment lines, proximity grouping.
   Get contrast, density, and comparison right before any decoration
   (references/principles.md).
3. **Materials and motion last, each with a stated reason**: a gradient,
   glass panel, shadow, or animation must answer "what job does this do?" —
   feedback, orientation, continuity, or explicit brand narrative. No job,
   no material (references/aesthetics.md).

Working rules:

- Prefer native elements and components with complete behavior contracts;
  ARIA describes semantics, it does not implement keyboard behavior.
- Build themes and semantics together. Dark mode is a semantic remapping,
  never a global invert.
- Choose containers by data relationship: independent objects → cards,
  cross-record comparison → tables, continuous content → lists/prose.
- Use real copy and boundary data from the start, at one narrow and one wide
  width continuously — not only after decoration.
- Subtract conditionally: remove elements without a job, then confirm
  content, affordances, and brand roles survived.
- Fix by risk (P0 → P2), then regress the other states, themes, widths, and
  text sizes. A fix that improves one screenshot while breaking 200% text is
  a net loss.

### Verify

Run the self-check gate in references/review.md (13 yes/no items; unknown
counts as no) and keep an evidence record per item. Coverage to attempt,
then report honestly what did and did not run:

- Keyboard end-to-end: complete key tasks, visible focus, sensible order,
  nothing fully obscured; modals trap and return focus.
- Contrast measured on composited backgrounds, per theme, per state.
- The text trio as three separate tests: 200% text resize, 320 CSS
  px-equivalent reflow, and the text-spacing override.
- Real states: longest content, empty, loading, error, success, disabled,
  permission-denied, slow network.
- Reduced motion: the task still completes and end states stay intact.
- Real load/input/paint on target devices where possible. A lab score is
  not a field percentile; neither proves task efficiency or taste.

Release bar: every applicable blocking item passes with evidence, exceptions
carry reasons, untested items are explicitly listed.

## Reviewing an existing UI

Read references/antipatterns.md (plus references/accessibility.md for Hard
thresholds). Core contract:

- Every finding follows: location → conditions → observable symptom →
  evidence class → user impact → severity (P0/P1/P2) → minimal fix → retest
  method → uncertainty. "Doesn't feel premium" is not a finding.
- Match symptoms to the anti-pattern library; treat its causes as diagnostic
  hypotheses to confirm against code and runtime — not as statistics about
  how often AI errs.
- Order fixes P0 → P1 → P2. Blockers cannot be offset by aesthetic scores.

## Deliverables

A design or review deliverable includes: task contract and assumptions, page
type rationale, structure and state definitions, verification evidence with
conditions, exceptions taken, unresolved issues, and the untested scope.
Claims about WCAG conformance name the tested criteria and environment —
never a blanket "compliant".

## Reference map

| Task | Read |
|---|---|
| Working rules for typography, color, layout, hierarchy, motion, consistency, tokens | references/principles.md |
| WCAG hard rules, exact thresholds and exceptions, interaction bottom lines | references/accessibility.md |
| Reviewing or repairing a UI; matching symptoms to 40 risk patterns | references/antipatterns.md |
| Marketing-vs-app differences, "premium" dimensions, style languages, trends, brand judgment | references/aesthetics.md |
| Review workflow, 13-item self-check gate, evidence record, release bar | references/review.md |

Load only what the current task needs.

Distilled from `docs/Methodology/frontend_design_research_report.md` and
`docs/Methodology/frontend_design_taste_guide.md` (rules graded
Hard/Conv/Taste; web sources verified 2026-09-01). Keep the grading attached
when quoting numbers.
