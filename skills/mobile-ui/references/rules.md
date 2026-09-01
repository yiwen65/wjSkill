# Decision Rules R01–R24

Behavioral contract for mobile UI design and review. Letters are evidence
classes (see SKILL.md): A = official standard/guide, B = research or mature
practice, C = project heuristic. Exceptions are part of each rule — a rule
without its exception list produces false positives.

| # | Rule (class) | Exception / boundary | Violation looks like |
|---|---|---|---|
| R01 | Keep task-required information first, then do visual subtraction (B/C) | Product-confirmed non-task info may be progressively disclosed | Deleting key fees or action consequences for "cleanliness" |
| R02 | Navigation items are destinations; action controls are actions (A) | Pro tools may organize differently but must explain the semantics | A bottom-tab "New" that acts like content switching |
| R03 | Visual emphasis matches a declared priority (A/C) | Dashboards may have several parallel focuses | A giant CTA regardless of task |
| R04 | Every container states its grouping, interaction, or expression job (C) | Brand expression can itself be a legitimate job | Three nested cards with no function in one area |
| R05 | Spacing uses semantic tokens; reasoned optical corrections allowed (A/C) | Icons, baselines, hairlines may need special handling | Every padding a different hand-typed number |
| R06 | Set type by text role; verify font scaling (A) | Logos and special graphic text handled separately | Fixed size, fixed height for all text |
| R07 | Predefine overflow strategy for content that can grow (A/C) | Summaries may truncate if full text has a reasonable path | Key status or button text ellipsized away |
| R08 | Visual de-emphasis must not make necessary info unreadable (A) | Genuinely inactive controls per the specific standard | Setting all helper text to very low opacity |
| R09 | Icons and images carry a semantic strategy (A/C) | Pure decoration should be skipped by assistive tech | Reader announces "image_123"; decorative art interrupts repeatedly |
| R10 | Measure actual hit regions; follow platform default targets (A/C) | Small-size exceptions need platform basis + verification record | Enlarging the icon glyph and declaring touch compliance |
| R11 | Critical gestures get an accessible equivalent path (A) | Functions truly inherent to the gesture assessed individually | Key task completable only by precise drag |
| R12 | State is driven by data and operation facts (A/B) | Pure local static content may simplify | Presenting a network failure as empty data |
| R13 | Recovery preserves the user's completed work (B/C) | Security or permission changes may require clearing some data | One field error resets the whole form |
| R14 | Distinguish disabled, read-only, hidden (B/C) | Hiding suits capabilities that should not be exposed or don't apply | Rendering every non-editable content as grey Disabled |
| R15 | Progress and results state only known facts (A/C) | Estimable progress must be labeled as estimate | Showing "done" before the backend confirms |
| R16 | Layout follows runtime safe areas and keyboard (A) | Immersive content may extend backgrounds if key controls are handled | A fixed bottom button covering input errors |
| R17 | Reorganize for the actual window, don't just scale (A) | Simple pages may need no structural change | Stretching narrow-screen content proportionally wide |
| R18 | Assistive-tech information matches visible state (A) | Decorative elements need not be separate a11y nodes | Visually selected, semantically reported unselected |
| R19 | Brand expression is defined in the brief, not skinned on at the end (C) | System utilities may take minimal brand intervention | One gradient + big-radius recipe applied to every product at the end |
| R20 | Motion needs a functional or expressive reason, with reduction supported (A/C) | Entertainment content may be highly dynamic, still assessed for accessibility | All actions wait for a decorative animation |
| R21 | Localization changes layout conditions, not just strings (A/C) | Symbols with fixed directional semantics are not mechanically mirrored | Flipping the whole screen horizontally for RTL |
| R22 | Visuals, copy, and real consequences of critical actions agree (B/C) | Low-risk reversible actions may skip confirmation | A "Preview" button that performs an irreversible action |
| R23 | Auth flows support appropriate autofill and paste (A) | Compliance-equivalent auth judged per the specific criterion | Blocking paste of a verification code for visual tidiness |
| R24 | Every completion claim carries its evidence (B/C) | If runtime is impossible, deliver a draft marked with its verification boundary | "UI fully verified" because the code compiles |

## Store rules as maintainable data, not just prompt text

Example — the iOS touch rule as a record (44 pt is the project default
policy; the exception path must not be deleted):

```yaml
id: TOUCH-IOS-001
title: Hit region of primary actionable controls
evidence_class: A-guide
policy_strength: project-default

scope:
  platform: iOS
  units: pt
  target: actual_hit_region
  applicable_to: actionable_controls

default_target:
  width_at_least: 44
  height_at_least: 44

checks:
  - inspect_runtime_hit_region
  - test_activation_near_edges
  - check_adjacent_target_ambiguity

exceptions:
  automatic_approval: false
  required:
    - specific_platform_or_component_rationale
    - documented_context
    - usability_and_accessibility_verification

source:
  title: Apple HIG — Buttons / Accessibility
  accessed_at: 2026-09-01

report:
  measured_bounds: required_or_unknown
  coordinate_unit: required
  affected_task: required
  evidence: required
  severity: based_on_user_impact
  fix: required
  retest: required
```

The same structure works for contrast, navigation, keyboard occlusion,
component consistency, and state coverage. Rules must carry applicability
conditions and exceptions, or reasonable designs get reported as violations.
