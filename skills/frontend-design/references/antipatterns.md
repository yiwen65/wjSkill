# Anti-Pattern Library — Symptom → Why It's Wrong → Fix

Forty risk patterns for review and post-generation repair, grouped by
category. **This is a risk checklist, not an AI-error frequency ranking.**
Default fix order: **P0 accessibility/task failure → P1 content/hierarchy
misleading → P2 brand/refinement** — and any visual error escalates to P0
when it breaks a task in the specific product. Treat each stated cause as a
diagnostic hypothesis to confirm against code and runtime.

## Templated, generic visuals

| # | Symptom | Why it's wrong | Fix |
|---|---|---|---|
| 01 | Purple-blue gradient, glow, and "intelligent" sparkles applied without asking the brand | Style with no task or brand basis; emphasis may outshout content. The color itself is not guilty | Write the brand direction and emphasis roles first; keep gradients that carry meaning, delete the rest; verify contrast for text on white and on gradient separately |
| 02 | Emoji standing in for all navigation, status, and tool icons | Glyph and tone unstable, meaning unclear; a function cannot rest on one nameless graphic | Unify one icon family (stroke/size) with accessible names; emoji may remain where content tone suits them |
| 03 | A card per sentence, cards nested in cards | Boundaries stop expressing object relationships; comparison and reading get shredded | Continuous content → prose/lists; multi-field comparison → tables; cards only for independent objects or clear interaction scopes |
| 04 | All headings, long paragraphs, and forms centered | No stable reading start line; forms and paragraphs resist scanning | Short heroes may center; long copy and forms align to the reading-direction start; data aligns to the comparison task |
| 05 | Giant vacuous slogan fills the first screen; the real product explanation lives far below | Visual weight mismatches information value | State "for whom, achieving what" plus mechanism/limits; follow immediately with product evidence and the next step; never invent numbers for effect |
| 06 | Headings, labels, and body all 16px/same weight — or everything bold | Roles indistinguishable; hierarchy collapses | Define display/section/body/label roles; differentiate with size, weight, and space — not color alone |
| 07 | Ultra-light gray thin type as "premium" | Secondary ≠ unreadable; may breach contrast requirements | Restore passing contrast first, then reduce competition via size, position, spacing; check thin strokes in the real font |
| 08 | Random mix of radii, shadows, gradients, outlines, and glass | Materials fight for the same level; boundary meaning unpredictable | Assign each effect a role; merge or delete role-less effects; compare same-level components across states |

## Typography, content, and layout basics

| # | Symptom | Why it's wrong | Fix |
|---|---|---|---|
| 09 | Defaults shipped with zero checks — fonts and colors never inspected | The fault is missing verification, not "default" itself: missing glyphs, fallbacks, weights, semantics may be broken | System fonts may stay; complete roles, fallbacks, real-character, theme, and contrast verification; record the rationale |
| 10 | Multiple icon sets mixed; small icons enlarged into hero art | Stroke, optical weight, and detail levels clash; enlargement is not redraw | Unify the icon family; use at designed sizes; commission large-format artwork for hero use |
| 11 | Arbitrary 16/19/23/27px spacing stacks | Same relationships render at different distances, breaking repetition and proximity | Extract spacing, converge onto the project scale; annotate optical corrections — don't force-change every non-8-multiple |
| 12 | Huge whitespace everywhere; an admin screen shows a handful of records | Marketing narrative density raises find/compare cost | Cut decorative margins, keep group separation; offer a sensible density option; verify hit areas |
| 13 | Article spans an ultra-wide screen; Latin line lengths copied onto Han characters | Line length never read-tested per language and font; return sweep fails | Give body text its own max-width (don't bind it to the app container); read-test CJK and Latin separately |
| 14 | `<br>`, fixed heights, `overflow: hidden` forcing a fixed layout | Assumes one text and one viewport; translations, zoom, and errors lose content | Let height grow with content; control wrapping locally only in explicit display-heading scenes; test other languages and widths |
| 15 | Left-aligned numbers, chaotic precision/units, empty values shown as 0 | Visual comparison and data semantics both broken | Unify format rules; right-align or decimal-align; distinguish 0 / unknown / N/A; tabular-nums where supported |
| 16 | Fabricated client logos, testimonials, growth numbers, or feature screenshots to fill the layout | Decoration over information truth; manufactures false trust | Use confirmed evidence; mark dev samples clearly as sample data; replace or remove before launch |

## Containers, responsiveness, information structure

| # | Symptom | Why it's wrong | Fix |
|---|---|---|---|
| 17 | Forced three equal modules per row, padded with empty filler | Geometric symmetry decides content, reversing task-first order | Choose one/two/asymmetric columns from the actual information; delete worthless modules |
| 18 | Comparable records turned into big cards, fields in different positions on each | No stable comparison axis; users re-find labels per card | High-frequency cross-record comparison → tables; cards for images/independent objects with unified field positions |
| 19 | Mobile "adaptation" by hiding key fields or deleting actions | Surface no longer overflows; the task is gone | Reorganize priority; detail views, column choices, or local scrolling; key tasks stay completable |
| 20 | Whole page scrolls horizontally to fit desktop components | Breaks reflow for applicable content; stretches the 2D exception to the entire page | Confine scrolling to genuinely two-dimensional regions; prose, headings, forms reflow to the narrow viewport |
| 21 | Only ever screenshotted at 1440px and one phone preset | Between-breakpoint, long-content, zoom, and landscape issues unverified | Resize continuously across representative widths; add longest-text, 200%-text, and 320px-equivalent reflow tests |
| 22 | CSS swaps visual order without checking Tab/screen-reader order | The seen flow and the operated flow diverge | Fix DOM order first, then express with layout; keyboard and screen-reader checks item by item; no positive-tabindex patching |
| 23 | Body text directly on complex transparent backgrounds for glass effect | Reading surface unpredictable; contrast and hierarchy can collapse | Provide stable text surfaces; confine glass to appropriate layers; check worst-case backgrounds and no-blur fallback |
| 24 | Product names, images, error text verified only with short placeholder content | Real layout constraints hidden; first state change breaks the page | Build real-length samples and boundary data; cover empty, loading, failure, success, no-permission, and disabled |

## Interaction and accessibility

| # | Symptom | Why it's wrong | Fix |
|---|---|---|---|
| 25 | `outline: none` with no replacement; sticky regions cover the focused control | Keyboard users cannot locate or see the focused component | Restore visible focus; adjust scroll margins/layout against occlusion; Tab through everything — not just screenshots |
| 26 | Clickable `div` as button, mouse-only | Missing native semantics, keyboard, and states; ARIA names don't add behavior | Actions use `button`; navigation uses links with `href`; if custom is unavoidable, implement the full interaction pattern |
| 27 | Placeholder as the only label; field meaning gone after typing | Persistent instruction lost; accessible name may also be missing | Keep a visible label; put format examples in associated helper text |
| 28 | Error only turns red; success only flashes green — no text or status message | Color becomes the sole encoding; screen readers may never learn the outcome | Explicit text tied to the field; status messages at appropriate urgency; don't yank focus for routine successes |
| 29 | Icon/text looks big enough but the hit area is a tiny glyph | Apparent size ≠ clickable area; adjacent targets invite mis-taps | Enlarge the real target region, not just the graphic; check neighboring targets, odd shapes, and applicable exceptions |
| 30 | Close/explain/menu available only on hover, or only via dragging | Keyboard, touch, and imprecise-pointer users have no path | Focusable/touch-accessible controls; sortable lists get move up/down single-pointer alternatives — not just keyboard shortcuts |
| 31 | Modal opens but focus stays in the background; focus lost on close | Visual and operational contexts detach; background still operable | Implement entry focus, internal loop, inert background, proper close, and focus return; choose sensible initial focus for long content |
| 32 | Disabled button unexplained; error clears all input; only restart offered | States don't help recovery; repeated labor | State the unmet condition; preserve safe valid input; offer retry/undo/next step; disabled is never the only feedback |

## Motion, engineering, delivery

| # | Symptom | Why it's wrong | Fix |
|---|---|---|---|
| 33 | Every element floats/zooms/bounces in; rapid input queues behind animations | Expressive effects occupy functional feedback and create waiting | Keep only change-explaining motion; shorten or make instant for high-frequency actions; allow interruption; no uniform duration on everything |
| 34 | Auto-carousels, parallax, marquees can't pause; scroll hijacked | User loses control; may breach auto-motion clauses | Prefer normal scrolling and static content; if auto-motion stays, provide the applicable controls; check keyboard, touch, reduced motion |
| 35 | With animations off, content stays transparent — or business logic waits forever for `animationend` | Animation misused as the business state machine; degradation breaks function | Commit state correctly first; motion is only the visual layer; under reduced motion jump straight to the usable end state and run the full flow |
| 36 | Dark mode via `filter: invert()` — images and state colors inverted too | No semantic remapping; brand and recognition distorted | Define theme tokens; verify images, hierarchy, error, selection, and focus per theme; light-theme passes never substitute for dark tests |
| 37 | Only color variables exist; buttons/forms/modals copied per page then locally edited | Looks may stay similar while behavior and states drift | Extend tokens to type, spacing, motion, and component contracts; share implementation and state tests; document reasonable exceptions |
| 38 | First screen loads big video, heavy blur, many font weights, animation libraries — no budget | Expressive cost can drag content and input; none of it is "modern frontend" necessity | Derive resources from a core-content-and-interaction budget; lazy-load non-critical media; measure paint and input; no blind `will-change` |
| 39 | Only ideal data and default state delivered, declared "done" | A static composition mistaken for a usable product; tasks and recovery unverified | Deliver the state matrix; test empty/loading/failure/success/long-content/permission plus keyboard focus; list untested items explicitly |
| 40 | Lighthouse high score or an "accessible" component library cited as site-wide conformance | Tool coverage is limited; correct parts don't guarantee correct composition, content, or flows | Combine manual tasks, keyboard, screen reader, and state checks; record tools, scope, and untested items; never claim an unaudited WCAG conformance |

## Using this library

Match observed symptoms to patterns, then confirm the cause in code and
runtime before prescribing the fix. The principles behind each row live in
references/principles.md; Hard thresholds live in references/accessibility.md;
the fix order and evidence format live in references/review.md.
