# Platforms: Units, Sizes, Contrast, Adaptation

Exact numbers and their scope. The unit and the exception list are part of
the rule — quoting a number without them is how wrong claims spread.

## Unit discipline

pt (iOS), dp/sp (Android), CSS px (web), and physical screenshot pixels are
different quantities. Record which one every measurement uses, plus device
scale. If runtime coordinates or scale are unavailable, report "appears too
small" — do not fabricate a precise converted value.

## Touch targets — three systems, do not merge

| Source | What it actually says | Agent rule |
|---|---|---|
| Apple HIG | Buttons guidance suggests at least **44 × 44 pt**; the current Accessibility table distinguishes **44 × 44 pt default** from **28 × 28 pt minimum** | Use **44 × 44 pt as project default hit target**. Do not treat 28 pt as the general recommendation, and do not claim Apple has one exceptionless 44 pt hard gate for every component |
| Android | Touch targets at least **48 × 48 dp**; the visible icon may be smaller | Inspect the actual hit region, not the icon's bounding box. After enlarging a hit region, check adjacent targets for ambiguity |
| WCAG 2.2 SC 2.5.8 (AA) | **24 × 24 CSS px**, with spacing, equivalent-control, and inline-target exceptions | A web success criterion — not a universal 24 dp native-app minimum |
| WCAG 2.2 SC 2.5.5 (AAA) | **44 × 44 CSS px**, scoped with exceptions | Not the same unit as Apple's 44 pt; not an AA requirement |

Checks: inspect the runtime hit region, test activation near edges, check
adjacent-target ambiguity.

## Contrast, text, and reflow

| Item | Executable principle | Common misreadings |
|---|---|---|
| Normal text contrast | WCAG AA: at least **4.5:1**; large text at least **3:1** | Not "all titles need only 3:1". WCAG large text is defined by actual size and weight, not by iOS role names |
| Large text definition | ~**18 typographic pt regular / 14 pt bold**, plus CJK equivalents | Typographic pt is not a native layout pt; "all bold" is not automatically large text |
| Essential non-text visuals | Visual information needed to identify components and states: **3:1** against adjacent colors | Not every decorative divider or shadow must meet 3:1 |
| Disabled vs secondary text | Genuinely inactive controls have a contrast exception; secondary or read-only information that must still be understood stays readable | "Secondary" or "less important" is not Disabled and gets no automatic exemption |
| Text resize | Web SC 1.4.4: up to **200%** without loss of content or function; native apps: platform text scaling and the real largest text mode | Do not scale glyphs and then clip them in fixed-height containers; one 200% screenshot does not prove every native accessibility size passes |
| User text spacing | WCAG 1.4.12: content and function survive user-adjusted spacing properties | It does not mandate 1.5× default line height, and CSS properties do not bind native components |
| Reflow | Web reflow has specific CSS viewport conditions; native products test real windows, text growth, and content growth | "320 CSS px" is not a universal "320 dp artboard" for native apps |

Typography starting points, not universal answers: iOS body default reference
is **17 pt**; Material 3 `bodyLarge` is **16 sp / 24 sp line height**, with
other body roles alongside. These are roles in a type system, not a command
that all body, label, and data text share one size.

## Platform adaptation: share semantics, not appearance

- **Navigation shares semantics, not chrome.** "Browse / saved / account" can
  share one information architecture while nav containers, back behavior,
  transitions, and system menus adapt per platform. Android Navigation Bar's
  "3–5 same-level destinations" is component guidance — it does not follow
  that every app must have 3–5 top-level modules.
- **Adapt to the window, not the device name.** Android window width classes:
  Compact, Medium, Expanded, Large, Extra-large with common breakpoints at
  **600, 840, 1200, 1600 dp**. Choose single-column, two-column, or
  list–detail from the actual window and task — not from an `isTablet` flag.
- **Full-bleed backgrounds and safe content areas are separate problems.**
  Backgrounds may extend behind system bars; important content and actions
  still need occlusion handling. On Android 15+ with target SDK 35+, edge-to-
  edge is enforced: handle system bars, cutouts, gesture areas, and IME
  insets properly rather than adding one fixed bottom padding. iOS uses
  runtime Safe Area layout information.
- **New platform materials are not global decoration commands.** Apple
  positions Liquid Glass mainly on navigation and control layers, not as a
  reason to glassify every content card. Prefer system components and the
  appropriate material level, and handle contrast, translucency, and the
  related accessibility settings.

## Which WCAG document is what

- **WCAG 2.2** — a W3C Recommendation for web content (A-standard).
- **WCAG2ICT** — a non-normative Group Note explaining how criteria apply to
  non-web software.
- **WCAG2Mobile** — currently a Group **Draft** Note, not a finished standard.

Native apps should neither copy CSS units and web test steps verbatim nor
ignore the same accessibility goals.

## Sources (all class A, accessed 2026-09-01, continuously updated)

Apple HIG (Buttons, Accessibility, Layout, Typography, Materials); Android
Accessibility, Window Size Classes, Window Insets, Predictive Back; Material
3 tokens and spacing; W3C WCAG 2.2 and the Understanding documents for the
success criteria above. Record the project's minimum OS, target SDK, and
component-library versions when applying any of them.
