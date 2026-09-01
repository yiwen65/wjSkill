# Review Workflow, Self-Check Gate, and Release Bar

A repeatable process for reviewing an existing page and for post-generation
verification. It is a working method synthesized by the source methodology —
not a mandatory standard, and never a substitute for a full WCAG audit or
real user research.

## Before generating

- Fix the page's task type (marketing vs application); write real content
  and object relationships; inherit the existing brand/system and state what
  may change; choose functional density and a justified expressive
  direction; record Hard, Conv, and Taste constraints separately.
- Never lock "purple SaaS hero" first and fill content afterwards.

## During generation

- Semantic structure, key tasks, and real states first; then typography and
  layout; stable decisions written as tokens and component contracts;
  continuous checking at one narrow and one wide width.
- Do not wait until decoration is finished to discover the content structure
  fails.

## After generating — check in this order

1. Content truth and task reachability.
2. Keyboard / focus / forms.
3. Contrast and target sizes.
4. Zoom / reflow / text-spacing override.
5. Themes and all states.
6. Motion and performance.
7. Only then: brand and art-direction comparison.

While any P0 item fails, shadows and glows wait.

## Self-check gate — answer yes/no per item

Unknown counts as **no**; not-applicable requires a recorded reason. Fix
task/accessibility items first, then hierarchy, then polish. Never write
"tested" for what was not actually operated.

- [ ] Page object, core value or task, and next step are clear; content and
      evidence are real?
- [ ] Primary emphasis matches the task; same-role type / spacing / color /
      components are consistent?
- [ ] Long text, numbers, CJK–Latin mixing, icons, and font fallbacks
      checked with real samples?
- [ ] Every card, whitespace, centering, material, and animation has a job —
      none are filler?
- [ ] All applicable text, controls, and states measured for contrast in
      every theme on actual backgrounds?
- [ ] Key flows completable with keyboard alone; focus visible, sensibly
      ordered, never fully obscured?
- [ ] Labels, names, states, errors, and modals checked via screen reader /
      accessibility tree?
- [ ] Target sizes, hover content, touch, and dragging alternatives meet
      applicable requirements?
- [ ] 200% text, 320px-equivalent reflow, and the text-spacing override all
      pass?
- [ ] Long content, loading, empty, error, success, disabled, and permission
      states lose no task information?
- [ ] With reduced motion the function is complete; auto-motion has
      applicable controls?
- [ ] Real load / input / paint measured — no lab score treated as complete
      conformance proof?
- [ ] Test conditions, fixes, exceptions, and not-yet-verified scope
      recorded?

## Evidence record

Use this format instead of writing "optimized":

```text
Item:      on save failure, the error is visible and announced
Conditions: narrow viewport / dark theme / keyboard / simulated save failure
Expected:  field and reason identified; input preserved; sensible focus;
           retry available
Result:    yes / no / untested
Evidence:  screenshot, interaction log, accessibility tree or screen-reader
           recording
Fix:       concrete location and implementation change
Remainder: uncovered browsers, devices, or exceptions
```

## Release bar

- Every applicable blocking item passes **with evidence**.
- Exceptions carry stated reasons.
- Untested items are explicitly exposed in the deliverable.
- Every aesthetic judgment answers three questions: why this design, under
  what conditions it would be wrong, and how to check whether it holds.

## Two worked before/after patterns

Teaching scenarios constructed by the source methodology — not measured
case studies or conversion experiments.

**A. B2B landing page.** *Before*: centered giant "Redefine the future";
perpetually moving glow background; three abstract cards; four competing
solid CTAs; a tiny product screenshot of dubious authenticity. The problem
is not purple — the user cannot see the object, the value, the evidence, or
the primary action. *After*: the headline states for-whom and what; the
sub-head explains mechanism and limits; a verified product UI with captions;
one decision region with one primary CTA and demoted secondaries; explicit
brand graphics keep identity; narrow screens, focus, and reduced motion all
usable. *Acceptance*: a stranger can point to the object, core value,
evidence, and next step; every fact has a source; CTAs perform their
actions.

**B. Task-management admin.** *Before*: stats, filters, and every record
each in its own big card; left-aligned numbers; more actions on hover only;
save failure just flashes red. *After*: stable page title and primary create
action; filters adjacent to the list; comparison data in a table with
unified number formats; high-frequency actions discoverable; failure gives
a text reason, preserves input, and offers retry; loading / no-results /
empty-ledger / no-permission each explained. *Acceptance*: create, find, and
fix completable without a mouse; cross-row comparison is fast; every state
is clear; the mobile layout keeps necessary information.
