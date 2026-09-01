# Anti-Pattern Library

Match observed symptoms to these patterns during review. **Root causes are
diagnostic hypotheses** — confirm them with implementation and runtime
evidence; they are not statistics about how often agents err. Severity:
P0 serious misoperation/irreversible loss/wrong critical result · P1 blocks
critical task, recovery, or committed accessibility · P2 raises cost ·
P3 local visual issue.

| Anti-pattern | Observable symptom | Root-cause hypothesis | Detection | Fix | Severity |
|---|---|---|---|---|---|
| Content deleted for "simplicity" | Fees, limits, states, or action consequences missing | Optimizing the screenshot, not task completeness | Diff against required-content list and task contract | Restore content, then fix organization and hierarchy | P0–P1 |
| Destination/action confusion in nav | "New" mixed into same-level content tabs | Copying a popular bottom bar | Check nav graph; check each item's semantics | Separate navigation from action entries | P2 |
| Unstable nav and back | Tabs vanish on empty data; position lost on back | Designing isolated pages only | Replay multi-step navigation | Stable destinations; preserve reasonable context | P1–P2 |
| Everything emphasized | Multiple saturated buttons, huge titles, badges competing | Unknown task priorities | Compare task ranking against visual emphasis | Remove jobless emphasis; build hierarchy | P2 |
| Over-containment | Cards in cards, repeated shadows and borders | Containers replacing organization thinking | Each container must name its grouping/interaction job | Delete jobless containers; keep meaningful grouping | P2–P3 |
| Whitespace mismatched to task | Key comparisons scattered across screens | Equating low density with premium | Run find/compare tasks with real data | Adjust density; never fix by shrinking touch targets | P2 |
| Style-value drift | Same-type lists differ in spacing, radius, font size | Local generation without token constraints | Diff tokens and component instances | Converge to components and tokens by semantics | P2–P3 |
| Fixed height clips text | Truncation/overlap at large text or long titles | Only default copy verified | Font-scaling and long-content tests | Adaptive height, wrapping, reflow | P1–P2 |
| Helper text too faint | Times, notes, units nearly unreadable | Mistaking de-emphasis for reduced readability | Measure actual foreground/background contrast | De-emphasize via weight, position, grouping together | P1–P2 |
| Small or conflicting touch areas | Icon visible but hard to hit; mis-taps | Confusing graphic bounds with hit region | Runtime hit test; edge-tap tests | Enlarge and separate hit regions | P1–P2 |
| Icons only decoratively similar | Unfamiliar icons unlabeled; synonyms drawn differently | Choosing icons by looks | Check names, semantics, labels | Comprehensible symbols; add text when needed | P2 |
| State by color alone | Red/green dots the only state difference | Ignoring non-visual and color-vision differences | Grayscale check + semantics check | Add text, shape, or icon information | P1–P2 |
| Disappearing input labels | After typing, field meaning is gone | Placeholder used as persistent label | Inspect filled and error states | Keep field names and necessary hints | P2 |
| Unfamiliar gesture as sole path | Key task requires long-press, drag, or complex swipe | Chasing "advanced interaction" | Check for alternative operations; assistive-tech test | Provide button, menu, or equivalent path | P1 |
| Success state only | No-data, failure, permission states undefined | Prototype mistaken for product | State coverage matrix | Add meaningful states and transitions | P1 |
| Over-broad loading feedback | Local refresh blocks the whole screen | One global Loading variable | Simulate a slow partial request | Keep usable content; local feedback | P2 |
| Fake progress, early success | Percentage unrelated to real task | Faking determinism for "smoothness" | Diff request and state-transition logs | Indeterminate for unknown; success only after confirmation | P0–P2 |
| Empty, error, no-permission merged | Everything shows "no content" | State model too coarse | Inject different failure and permission conditions | Present cause-specific explanation and path | P1–P2 |
| Dishonest offline state | Cache described as live; unsynced changes unmarked | UI disconnected from data state | Airplane mode, reconnect, sync-conflict tests | Mark freshness and sync status | P0–P2 |
| Lost input, duplicate submit | Retry means retyping; taps create repeated requests | Missing recovery and submission contract | Fail, time out, double-tap tests | Preserve input; distinguish failed vs pending | P0–P1 |
| Unknowable disabled reason | Primary button grey, no perceivable explanation | Only the Disabled look implemented | Check preconditions and explanation accessibility | Show requirements; separate read-only from disabled | P1–P2 |
| Keyboard/system occlusion | Focus, errors, or actions covered | Fixed layout; hardcoded insets | Keyboard, landscape, system-bar change tests | Runtime insets and scrollable layout | P1 |
| Big screen = stretched phone | Content spans too wide; nav far from actions | Scaling by device ratio | Same task at different windows | Sensible columns, max content width, adaptive nav | P2 |
| Localization breaks | Long translations clipped; RTL order/icons wrong | Only short English samples tested | Target languages, pseudolocalization, RTL tests | Semantic layout, correct mirroring, content strategy | P1–P2 |
| Screen-reader experience broken | No names, wrong order, modal focus escapes | Accessibility treated as a text patch | Full VoiceOver/TalkBack task runs | Fix roles, names, states, grouping, focus | P1 |
| Motion blocks operation | Must wait; large repeated movement; no reduced mode | Showmanship replacing feedback | Reduced-motion and repeated-action tests | Trim inessential animation; keep state understandable | P1–P2 |
| Templated brand, material abuse | Every page the same gradient glass cards | Trendy surface features replacing brand strategy | Diff against brand brief and material purposes | Keep expressive elements with jobs; cut the rest | P2–P3 |
| Untested claimed as passed | "Accessibility compliant" from screenshots alone | Over-trusting one evaluation method | Check the evidence type behind each conclusion | Mark unverified; add runtime and assistive-tech tests | P1 for key items |

Normative basis: navigation stability, dragging alternatives, text
readability, error identification, platform adaptation, and assistive-tech
testing (class A). Diagnostic methods and severity grading are the source
methodology's engineering organization (class C).
