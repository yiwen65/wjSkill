# Core Principles

Working rules for typography, color, layout, hierarchy, motion, and
consistency. Basis classes: **Hard** = normative requirement in scope ·
**Conv** = system/project convention · **Taste** = justified preference.
Every rule gives a check and a counterexample — the counterexample is part
of the rule, because these are decision aids, not laws. Numbers not marked
Hard are starting points to verify against real content, never universal
standards.

## Typography

- **Conv** — Define named type roles (display / section / body / label /
  caption) with sizes and weights; reuse few font families. A sample scale
  like 12/14/16/20/24/32/48px is an illustration, not an industry standard.
  Check: same role renders identically everywhere; CJK, Latin, punctuation,
  required weights, and font-load failure all verified with real text.
  Counterexample: everything 16px, everything bold, or mixing families for
  novelty. Neither "custom fonts required" nor "system fonts are tasteless"
  holds.
- **Conv/Taste** — Choose base size by reading task; 16px is a reasonable
  body starting point, dense tools may justify smaller (Carbon ships 14px
  productive / 16px expressive — context conventions, not floors). Try line
  height 1.5–1.7 (Latin) / 1.6–1.8 (CJK) for long paragraphs; tighten
  headings per font. Check: actually read consecutive lines, narrow screens,
  and zoomed states. Counterexample: treating 16px as a WCAG floor; single
  line controls and display headings need not inherit paragraph leading.
- **Conv/Taste** — Cap line length per language. USWDS suggests ~45–90
  characters (~66 for long-form) for English; for CJK try ~28–40em desktop
  columns and adjust by reading. Check: count real characters, read
  continuous paragraphs, watch the return sweep. Counterexample: `65ch` is
  an approximate width, not 65 glyphs in any font; never copy a Latin
  character count onto Han characters; never shrink type to hit a count.
- **Conv** — Align compared numbers: unify units, precision, and
  localization; right-align or decimal-align comparison columns; use
  `font-variant-numeric: tabular-nums` when the font supports it. Check:
  negatives, empty values, large numbers, mixed-script wrapping, thousand
  separators, currencies. Counterexample: aligning with spaces; rendering
  unknown as 0 (distinguish 0 / unknown / N/A); tabular-nums alone does not
  align decimal points.
- **Conv** — Handle language, punctuation, and breaking for CJK and mixed
  text: correct `lang` on page and fragments; respect line-head/line-end
  rules, quotes/brackets, unit wrapping; long URLs break locally.
  Counterexample: site-wide `word-break: break-all`; treating CLREQ (a
  Group Note Draft) as WCAG-mandatory.
- Text handling: never align data with hand-typed spaces; never bake key
  information into images; never keep headings "tidy" with fixed heights and
  clipping; visual size may differ from HTML semantics, but semantic
  headings still express document structure; browser-faked bold is not a
  hierarchy tool; all-caps/letter-spacing/italics are brand devices, not
  defaults for long paragraphs.

## Color

- **Hard** — Text contrast ≥ 4.5:1; large text ≥ 3:1 (large ≈ ≥24 CSS px or
  ≥18.67 CSS px bold; when unsure use 4.5:1). Visual information needed to
  identify controls/states ≥ 3:1 against adjacent colors. Measure per theme,
  per state, on the composited background — never an average. Details and
  exceptions: references/accessibility.md. Counterexample: light-gray small
  text as "premium"; assuming every decorative border needs 3:1.
- **Conv** — Define semantic color roles first — canvas / surface /
  text-primary / text-secondary / border / action / on-action / focus /
  success / warning / danger — then assign values per theme. Check: same
  meaning → same role; different meanings not forced into one color; dark
  theme verified independently. Counterexample: global invert as dark mode;
  red for everything important; brand color doubling as all primary text.
  "Neutral base + limited accents" is a common starting point, not a
  60/30/10 law — editorial, entertainment, and cultural brands may need
  richer palettes.
- **Taste** — Accent color and materials serve brand, hierarchy, or state.
  Check: explain the job of every gradient, glass panel, and shadow.
  Counterexample: banning purple on principle; adding glow to every region
  without a reason. Materials are not original sin — jobless materials are.
  Any perceptual color space (CIELAB, OKLCH…) never exempts the final
  contrast measurement.
- Dark mode and materials (Conv/Taste): reassign surface levels, text
  strength, chart colors, borders, and focus — never a global invert or a
  white-to-black swap. Check the same component in all states across both
  themes. Pure black/white are not forbidden; the problems are glare, lost
  boundaries, image adaptation, unclear hierarchy. Transparency, blur, and
  gradients make the effective background content-dependent: provide a
  stable text surface and a no-blur fallback, and do not stack glass on
  glass for content layers.

## Layout

- **Conv** — Use a finite spacing scale (4/8-based is a common start) with
  named uses for within-group, between-group, and page margins; related
  items close, groups farther apart; share primary alignment lines. Check:
  extract actual spacing from code — repeated uses reuse tokens; exceptions
  documented. Counterexample: arbitrary 16/19/23/27px stacks; forcing 1px
  borders and 2px optical corrections onto 8-multiples; mixing CSS px,
  device pixels, and native pt as one "8pt".
- **Conv** — Grid constrains alignment, container widths, and column
  relationships; choose column count from content. Counterexample: 12
  columns is not truth — Carbon uses 16; grid thinking predates every CSS
  framework.
- **Conv/Taste** — Containers follow data relationships: independent objects
  → cards; cross-record comparison → tables; sequential/continuous content →
  lists/prose. Check: every card boundary names its object or interaction
  scope; if converting a card to a row makes comparison easier, it was the
  wrong container. Counterexample: cards within cards; indiscriminate
  cardification (the problem is not cards — products, works, and independent
  tasks suit them); an admin stretched into a poster of whitespace.
- **Conv/Taste** — Whitespace separates paragraphs and action groups; "empty"
  is never the goal. Check: does deleting surplus space improve comparison;
  does adding space actually reduce confusion? Counterexample: professional
  tables can be dense and excellent; marketing hero rhythm must not be
  copied into every admin list.
- **Conv** — Breakpoints from content failure points: adjust columns,
  navigation, and density independently; keep core tasks. A working
  regression set: 320/360/768/1024/1440 CSS px plus continuous dragging
  between them (a test sample, not a market-share claim). Check: long
  labels, long numbers, translations, sidebars, popups. Counterexample:
  verifying only two device presets; mobile "adaptation" by hiding key
  columns or cutting features — reorganize priority, offer detail views,
  column choices, or local scrolling instead.
- **Conv** — Decide height, wrapping, and overflow rules against real data
  and all states: longest title, empty set, huge values, validation errors,
  slow loading. Truncation is acceptable only for summaries with a complete
  access path — never permanently clip errors or values the user must see.
  Keep DOM reading order sane; never create keyboard-order chaos with CSS
  visual reordering.

## Hierarchy

- **Taste** — The largest visual weight maps to the most important
  information; every decision region has one clear primary action. Check: a
  fresh viewer can point to the title, the evidence, the next step; list all
  high-emphasis elements — each has a reason; no region has competing
  primary actions. Counterexample: all buttons equally loud; demanding a
  whole complex app have exactly one primary button; building hierarchy by
  pushing secondary text below contrast thresholds (danger actions need not
  be the loudest either).
- **Taste** — Express reading order before designing scan paths: headings
  summarize, evidence supports, actions sit predictably. Short heroes may
  center; long copy and forms align to the reading-direction start. Check: a
  person uninvolved in the design identifies title/evidence/next step — note
  misreads and adjust. Counterexample: centering the whole page; F-pattern
  or Z-pattern as mandatory templates (image browsing, explicit tasks, and
  language change scanning); filler modules added for symmetry.
- A quick occlusion/recall test — show the page briefly, ask "what is this,
  what is the main information, what is next" — is a cheap formative check,
  not a universal five-second pass bar, and never a substitute for task
  testing.

## Motion

- **Conv/Taste** — Separate functional from expressive motion. Write one
  sentence of purpose for each animation: confirm an action, explain a
  spatial relationship, preserve object continuity, present state, or carry
  explicit brand narrative. Delete what has no purpose yet steals attention
  or blocks input. Brand films and interactive exhibitions may need
  expressive motion; high-frequency approval forms usually need instant
  feedback.
- Duration/easing starting points (Conv, tuning origins — not a spec
  transcription): micro-feedback 120–180ms, panel expand 180–280ms, larger
  scene transitions 240–400ms; then adjust by distance, size, input
  frequency, and device. Enter/confirm usually eases out; exit eases in;
  continuous progress can be linear; do not spring everything by default.
  Check: action-to-feedback latency; rapid repeated actions do not queue;
  tasks can continue before animation ends.
- **Conv** — Respect `prefers-reduced-motion`: remove non-essential
  parallax, zoom, and continuous movement; keep state information, end
  states, and function. Test by enabling the system/browser preference and
  completing the original task. Counterexample: blanket
  `* { animation: none }` hiding content that should appear; business state
  depending on `animationend`; assuming `transform` is always zero-cost.
  (The WCAG clause for disabling non-essential interaction animation, 2.3.3,
  is AAA — do not mislabel it AA.)
- Performance (Conv): prefer `transform` and `opacity`, but do not claim
  they are free — large blurs, shadows, composited layers, and main-thread
  scripts still jank. Use `will-change` sparingly and watch real paint
  paths. Do not load heavy animation dependencies per scroll section or let
  preloaders block usable content. Core Web Vitals good thresholds: LCP ≤
  2.5s, INP ≤ 200ms, CLS ≤ 0.1, judged at the field 75th percentile split by
  mobile/desktop — a single local Lighthouse run is not a user percentile,
  and CWV is not a task-efficiency or aesthetics score. Without field data,
  report "lab result / field data pending".

## Consistency

- **Conv** — Reuse semantic tokens and component contracts covering default,
  focus, selected, disabled, loading, empty, error, and success. Check:
  same-class components behave identically across pages — behavior, not just
  looks; if marketing and app densities differ while semantics and brand
  hold, do not mechanically "unify" them. Counterexample: unifying only
  colors; treating a component library, a Figma file, an npm package, or a
  color page as a complete design system.
- **Conv** — Component contract minimum: purpose and forbidden uses,
  structure, sizes/density, text rules, interaction behavior, accessible
  name, keyboard/focus, loading/empty/error/disabled/success states,
  overflow, theming, localization. Accept against a state matrix, never a
  single default screenshot. Governance (maintenance owner, versions,
  migration/deprecation rules, interaction and visual-regression tests)
  exists to keep changes traceable — no single process fits every team.
- **Taste** — Copy, imagery, icons, and materials share one brand direction.
  Check: each item explains its purpose and holds beyond the screenshot;
  without the logo, a viewer can still name the project's specific traits
  and their business reason. Counterexample: emoji as anonymous functional
  icons (unify one icon family with accessible names; emoji may suit content
  tone); mixing icon stroke weights; declaring system fonts automatically
  tasteless; enlarging small icons into hero graphics instead of drawing
  large-format artwork.

## Token architecture (Conv)

Three layers — raw values → semantic roles → component usage:

```text
palette.blue.600 → color.action.primary → button.primary.background
space.3          → space.control.inline  → button.padding.inline
```

Check: theme switching mostly changes the mapping; components do not bypass
tokens with hard-coded values; the same token name never carries
contradictory meanings across pages. Allow a few documented exceptions
rather than minting meaningless tokens to reach "zero hard-coding". DTCG
2025.10 (released 2025-10-28, first stable format) is a community-group
format — explicitly not a W3C standard; adopting it is neither a design
system nor an accessibility proof. APCA may supplement perceptual
evaluation, but WCAG 2.2 conformance claims still use the normative
contrast math.
