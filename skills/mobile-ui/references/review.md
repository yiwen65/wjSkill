# Review: Critique Contract, Severity, Scoring

How to produce findings that survive scrutiny. The scoring weights and
blocker policy are C-class project acceptance machinery — calibrate them per
project; they are not a WCAG conformance method and not platform compliance
certification.

## Severity scale

- **P0**: can cause serious misoperation, irreversible loss, or critical
  results expressed wrongly.
- **P1**: blocks a critical task, an important recovery path, or a committed
  key accessibility requirement.
- **P2**: clearly raises comprehension, operation, or maintenance cost.
- **P3**: local visual issue that does not block tasks.

## Critique output contract

Every finding includes, in order:

> location/node → current state and device conditions → observable symptom →
> evidence class → user impact → severity → minimal fix → retest method →
> uncertainty

Example (illustrative, not a real measurement):

> **Problem:** On the search page at maximum text size, the "Clear filters"
> button label is truncated.
> **Evidence:** Screenshot of that state plus layout bounds; the full label
> is not obtainable in the current view.
> **Impact:** The user cannot reliably understand the recovery action for the
> no-results state.
> **Fix:** Allow the button/action area to wrap or stack vertically; do not
> shrink the text further.
> **Retest:** Default and maximum text settings, long translations, keyboard
> visible.
> **Unknown:** Whether a screen reader announces the full name — not yet
> tested.

"Doesn't look premium enough" cannot alone constitute a defect report.

## Blockers before scores

None of the following can be offset by high aesthetic scores:

- Unresolved P0 or critical P1 issues.
- A critical task cannot be completed, its result is expressed wrongly, or an
  important recovery path is missing.
- A key accessibility requirement the project explicitly committed to is not
  met.
- A key verification was never run but is about to be marked as passed.

## Weighted rubric

Four checks per dimension. Weights are a suggested starting point — adjust
for product risk.

| Dimension | Weight | Four checks | Typical deductions |
|---|---:|---|---|
| Tasks, IA, usability | 18 | Required content complete; destination/action semantics clear; critical tasks completable; back/cancel keeps reasonable context | Missing key info, broken flow, no exit or recovery |
| Visual hierarchy | 12 | Emphasis order matches tasks; primary/secondary distinguishable; grouping expresses real relationships; important states not buried | Multiple unrelated focal points; secondary content overpowers core; warnings invisible |
| Layout & typography | 14 | Stable alignment; semantic spacing; sensible text roles; density and content-growth strategy hold | Baseline chaos, random spacing, clipping, force-fitting by shrinking type |
| Component & visual consistency | 10 | Consistent token use; same semantics same expression; icon/image language coherent; component states consistent | Same button in many unjustified styles; drifting state expression; repeated local implementations |
| Platform & device adaptation | 10 | Platform navigation behavior sound; window changes usable; insets/keyboard correct; localized layouts hold | Hijacking system gestures; broken landscape; keyboard occlusion; long-translation overflow |
| Accessibility | 16 | Contrast meets target; touch and alternative operations usable; text scaling loses no function; assistive-tech tasks pass | Necessary text unreadable; cannot zoom; key controls unnamed or focus broken |
| States, feedback, recovery | 12 | Load/refresh distinguished; empty vs no-results distinguished; errors recoverable with retry; offline/disabled/pending states honest | Needless full-screen blocking; lost input; fake success; unsynced content unmarked |
| Aesthetics & brand | 8 | Brand expression grounded; complexity suits tasks; cross-page language coherent; comparison-driven improvement didn't sacrifice content or usability | Template collage; decoration competition; only one page holds up; aesthetic rationale unexplainable |
| **Total** | **100** | | |

## Scoring each check

| Result | Value | Definition |
|---|--:|---|
| Pass | 1 | Supported by evidence |
| Partial | 0.5 | Clear, bounded defect; critical task not blocked |
| Fail | 0 | Substantive defect |
| Unverified | U | Not enough evidence to judge — **not** a pass |
| N/A | — | Must justify why inapplicable; cannot hide defects |

With four applicable checks: `dimension score = weight × (sum of four) / 4`.
One check moving pass → fail costs a quarter of the dimension's weight;
pass → partial costs an eighth.

When U items exist, report:

> **verified lower bound – possible upper bound + verified coverage +
> blocker list**

Compute the lower bound with U = 0 and the upper bound with U = 1, so
"unknown" never masquerades as a good result. N/A leaves the dimension's
denominator only with a recorded reason.

**Avoid false precision.** "86 points" is not a law of nature. A project may
adopt 85 as an internal candidate line, but that threshold is class C and
needs calibration by human review. Real release depends on blockers, evidence
coverage, and project risk.

## Making scores repeatable

Reviewers share one task brief, data samples, state matrix, and reference
anchors. Every deduction binds to an issue number and its evidence. Aesthetic
opinions must name their context and comparison target. One root cause gets
one issue regardless of how many ways it is described.

Check inter-reviewer disagreement periodically. Disagreement can come from
unclear rules, missing context, or legitimate style preference — do not
paper over all of it with majority vote.
