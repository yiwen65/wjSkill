# Accessibility — Hard Rules and Interaction Bottom Lines

The WCAG 2.2 criteria most relevant to design decisions. **This is not a
complete audit**: claiming AA requires every applicable A and AA criterion.
Each entry gives the clause, level, what to do, and where it is commonly
misread. W3C Understanding documents and the ARIA APG are informative
companions; the normative text is WCAG itself.

## Contrast and color

| Clause | Requirement | Measurement and misreadings |
|---|---|---|
| 1.4.3 AA — text contrast | Normal text ≥ **4.5:1**; large text ≥ **3:1**. Large ≈ ≥24 CSS px, or ≥18.67 CSS px bold (CJK equivalent sizes interpreted per clause) | Measure the **composited background** per theme and per state — hover, selected, focus, error, over images and gradients. For text crossing a varying background, check the worst glyph region, never an image average. Do not round 4.49 into a 4.5 pass. Thin weights may need practical margin beyond the number. Not all 18px text is "large"; when unsure, use 4.5:1. |
| 1.4.11 AA — non-text contrast | Visual information needed to identify controls, perceive state, or understand graphics ≥ **3:1** against adjacent colors | Not every decorative border or shadow needs 3:1. Disabled controls and unmodified browser-default appearances carry exceptions. |
| 1.4.1 A — use of color | Color is never the only visual means of conveying information, action, or state | Errors get text/symbol as well; charts get labels, line styles, or patterns; never "click the green button" alone. |

## Target size and focus appearance

- **2.5.8 AA — target size (minimum)**: targets ≥ **24×24 CSS px**, measured
  on the actual hit region — not the visible icon glyph. Exceptions, checked
  per target: the *spacing* exception (a 24 CSS px-diameter circle centered
  on the target intersects no other target or other targets' circles — not a
  vague "leave a 24px gap"), inline targets, an equivalent same-page
  control, unmodified user-agent controls, and essential presentation.
  Accept small targets only after checking these exceptions and the real
  hit area.
- **2.5.5 AAA — target size (enhanced)**: 44×44 CSS px as the comfortable
  touch enhancement. A sound project default for touch-first interfaces —
  but it is **not** the AA bar, and Apple/Android native pt/dp is not
  CSS px.
- **2.4.7 AA — focus visible** and **2.4.11 AA — focus not obscured
  (minimum)**: focus is visible, and a focused component is never *entirely*
  covered by sticky headers or overlays (AA requires "not fully obscured";
  projects may adopt stronger). Test occlusion, not only the ring.
- **2.4.13 AAA — focus appearance**: when adopting the enhanced target, the
  indicator area is at least a 2 CSS px-thick perimeter of the unfocused
  component (or sub-component), with ≥ 3:1 contrast between focused and
  unfocused pixels, exceptions per clause. A "2px outline" is a starting
  point — not automatic AAA proof, and not an AA-wide requirement.

## Text: three different tests — run every applicable one

- **1.4.4 AA — resize text**: text scales to **200%** with no loss of
  content or function.
- **1.4.10 AA — reflow**: applicable content reflows at **320 CSS px**
  equivalent width (check a 1280 CSS px viewport at 400% zoom) without
  two-dimensional scrolling for reading. This is not "320px wide then zoom
  400%". Genuine two-dimensional content (data tables, maps) may scroll
  **locally** — never let the whole page slide sideways.
- **1.4.12 AA — text spacing**: when the user overrides line height to
  1.5× font size, paragraph spacing to 2×, letter spacing to 0.12×, and word
  spacing to 0.16×, nothing is lost. This tests **tolerance of user
  overrides — it is not a required default stylesheet**. Languages without a
  given spacing concept support only the applicable items. Inject the test
  styles and check navigation, buttons, labels, and popups — not just body
  text.

"Did a mobile adaptation" substitutes for none of these three.

## Keyboard, structure, names

- **2.1.1 A — keyboard** and **2.1.2 A — no keyboard trap**: complete key
  flows without a mouse (Tab, Shift+Tab, Enter, Space, applicable arrow
  keys); every region exitable. Do not sprinkle `tabindex="0"` on plain
  elements; a modal's managed focus loop is not an illegal trap.
- **1.3.1 A — info and relationships** and **4.1.2 A — name, role, value**:
  inspect landmarks, headings, labels, table headers, names, roles, and
  states in the accessibility tree / with a screen reader. Prefer native
  elements: `role="button"` ships without button keyboard behavior, and
  ARIA never repairs broken HTML by itself (No ARIA > bad ARIA). Decorative
  images produce no meaningless narration.
- **2.4.3 A — focus order**: focus order matches the task. Fix DOM order
  first, then express with layout; never patch a broken order with positive
  tabindex.

## Forms and status

- **3.3.2 A — labels or instructions**: visible labels and necessary
  instructions persist after input. A placeholder alone is not a persistent
  label — put format examples in associated helper text.
- **3.3.1 A — error identification**: failed submits identify the field and
  give a text reason — never red alone; offer correction suggestions where
  feasible.
- **4.1.3 AA — status messages**: save confirmations, result counts, and
  failures reach assistive technology without a focus hunt. Use
  urgency-appropriate status mechanisms; do not let every number refresh
  preempt narration; do not move focus without reason.

## Modal dialogs — behavior, not attributes

On open: move focus to a task-appropriate place — not always the first
input; long structured content and destructive confirmations need different
initial-focus choices. While open: Tab loops inside; the background is
inert. Provide a proper close path. On close: return focus to the trigger —
or to a sensible next position when the trigger is gone or the workflow
advanced. `aria-modal="true"` implements none of this on its own.

## Hover, drag, authentication

- **1.4.13 AA — content on hover or focus**: applicable additional content
  is dismissible, hoverable, and persistent; core operations keep keyboard
  and touch paths. Never place essential explanation behind mouse hover
  only. Native browser tooltips etc. follow the clause's conditions.
- **2.5.7 AA — dragging movements**: sorting, moving, and range selection
  get a single-pointer alternative (e.g., move up/down buttons). A keyboard
  shortcut alone does not satisfy this single-pointer requirement; essential
  dragging and unmodified UA behavior are exceptions.
- **3.3.8 AA — accessible authentication (minimum)**: logins allow password
  managers, autofill, paste, or a suitable alternative; never force unaided
  memorization or transcription. The clause carries its own
  alternative/assistance/object-recognition exceptions — do not flatten it
  into "all cognitive tests forbidden".

## Motion and auto-updating content

- Respect `prefers-reduced-motion`: remove non-essential parallax, zoom, and
  continuous motion; keep state information and end states. Test by enabling
  the OS/browser preference and completing the original task. Never blanket
  `* { animation: none }` content into invisibility; never gate business
  state on `animationend`.
- **2.2.2 A — pause, stop, hide**: auto-starting moving/blinking/scrolling
  content that lasts over 5 seconds in parallel with other content needs a
  pause/stop/hide mechanism (essential-motion exceptions exist).
  Auto-updating content has its own conditions — "under five seconds" is not
  a blanket exemption.
- **2.3.3 AAA — animation from interactions**: disabling non-essential
  interaction animation is AAA; do not report it as an AA gap.
- **2.3.1 A — flashes**: check flash thresholds; the safest project policy
  is avoiding non-essential flashing.

## Testing honesty

Run at least one representative browser/screen-reader combination through
real task flows. Automated tools complement — never replace — keyboard,
screen-reader, cognitive-order, and content judgment: "the tool reported
nothing" only means this tool's checks found nothing. A Lighthouse score or
a component library's "accessible" label is not a site-wide conformance
claim. Record tools used, scope, and untested items.
