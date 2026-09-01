# Aesthetics and Taste — Turning "Premium" into Named Decisions

Everything here is **Taste** class (justified preference, evidence from
mature practice and first-party cases) unless marked otherwise. Taste
decisions are checkable, but they never convert into universal thresholds:
contrast is measurable; whether a brand suits a serif or a giant gradient
must be weighed against task, context, recognizability, and cost.

## Marketing page vs web application

A working distinction synthesized from design systems and cases — not a
template every product must follow:

| Decision | Marketing / landing page | Web application |
|---|---|---|
| First question | Can the user understand the value, trust the evidence, and name the next step? | Can the user locate objects, compare information, complete and recover operations? |
| Typography & density | Characterful big headlines, rhythmic variation, narrative whitespace | Stable headings, labels, tables; compact but readable density |
| Primary action | One conversion direction per decision region; long pages may repeat the same CTA | Each work area may have its own primary action — no app-wide single-primary-button rule |
| Visual materials | Brand photography, illustration, and expressive motion may carry argument or memory | State, data, navigation, and operations first; decoration never squeezes task content |
| Success evidence | Comprehension tests, first-click position, lead quality, proper conversion experiments | Task completion, error recovery, find/compare efficiency, repeat-use cost |
| Shared floor | Real content, semantic structure, clear states, responsiveness, accessibility, performance | Same — brand differences never excuse breaking the floor |

Do not build an admin like a poster, nor a landing page like an admin.

## Eight operable dimensions of "premium"

"Premium" is not an objective property independent of culture, industry, and
audience — but it decomposes into discussable decisions:

| Dimension | Practice | Check | Counterexample |
|---|---|---|---|
| Intentional attention | Highest emphasis serves the most important information | Mark the loudest text/blocks/images — do they match task priority? | Festive/entertainment content may legitimately have multiple foci; don't force enterprise-admin calm on them |
| Relational proportion & spacing | Whitespace separates levels; margins, columns, and group distances cohere | Same relationship → same spacing; anomalies exist for content, optics, or brand? | Blanket padding increases fix nothing; trading tables may need compactness |
| Typographic finish | Headings, body, numbers, punctuation, mixed-script each handled | With real long text and long numbers, do scale, breaking, and baselines still hold? | A big serif display suits some editorial brands — not every tool |
| Materials with hierarchy, not heap | Shadow, border, blur, transparency each carry a layering or interaction role | Remove effects one by one: any loss of hierarchy, affordance, or explicit brand expression? If not, delete | Narrative-rich materials should not be deleted merely for "simplicity" |
| Brand ≠ template recolor | Content, language, graphics, and typography share one explainable direction | Without the logo, can you name the project's specific traits and their business reason? | Government forms need not reinvent every control; familiarity has value |
| Images with jobs | Selection and crop explain a concrete product, context, or concept | Which question does each image answer; does the crop lose key information; does it hold on narrow screens? | Abstract graphics can express brand — but must still be explainable |
| Detail holds across states | Hover, focus, loading, empty, error, selected follow the same logic | Don't stop at the default screenshot: after state switches, are position, text, contrast, and behavior coherent? | A smooth fade-in cannot rescue a form with no error-recovery path |
| Reasonable expression cost | Expressive effects match their loading, input, and scroll cost | On target devices, watch input latency and paint; with effects off, is the task smoother while brand is nearly unharmed? | Art experiences may budget more rendering — with notice, degradation, and an access path |

A fair comparison method: give two schemes the **same content, same data,
same states**, then compare information priority, brand coherence, and task
completion. Never credit a layout difference when one side had professional
photography and the other placeholder text.

## Style languages — features, fit, risks

Styles mix and revive; this is not a linear evolution, and newer is not
better. Grid thinking predates every frontend framework.

| Style | Recognizable decisions | Better fit | Must-check risks |
|---|---|---|---|
| Grid / internationalist | Stable alignment, clear proportions, type-led, decoration serves organization | Content-dense, editorial, professional brands, long-lived systems | Mobile and long content; 12 columns, sans-serif, or symmetry are not identity checks — grids support asymmetry |
| Minimal / plain | Few accents, limited materials, duplicate cues removed, key content kept | Task tools, reading, service flows — also brand | Labels, boundaries, focus, empty states deleted away; "low contrast + big whitespace" is not a minimalism requirement |
| Editorial / type-driven | Characterful headlines, long-short rhythm, image-text relations, visible page hierarchy | Media, culture, brand story, content marketing | Body must stay readable; long headlines, CJK, and narrow screens must not break; display scale should not rule every admin panel |
| Brutalism (raw HTML feel) | Exposed HTML and links, plain structure, anti-polish or raw feel — not necessarily saturated | Art, experiment, archives, author sites | Must be "intentionally precise", not "unfinished"; restrained cases exist with default fonts and almost no CSS |
| Neobrutalism | Thick borders, hard shadows, vivid blocks, strong contrast, direct visual weight | Distinctive products, creative/cultural marketing, some light tools | Visual noise over long tasks; not a synonym for raw HTML; not inherently inaccessible |
| Glassmorphism | Translucency, blur, floating layers, background participating in material | Navigation/control overlays with clear hierarchy; specific brand scenes | Test worst-case backgrounds, no-blur fallback, performance; all-glass content and glass-on-glass destroy reading |
| Skeuomorphism | Real-object shapes, materials, and operation metaphors explaining digital functions | Audio, instruments, creative tools, specific learning/brand experiences | Is the metaphor actually familiar; does it hide the function; knobs also need non-drag input; "more photographic" is not the goal |
| Neumorphism | Near-background tones, soft light/dark shadows, raised/pressed relief | Small-scope material expression, low-density display | If controls/states differ only via low-contrast shadows, risk is high; explicit labels, boundaries, and states help — don't blanket-declare all implementations violations |
| Immersive / 3D / motion narrative | Staged perspectives, large media, coherent transitions, spatial exploration | Product demos, campaigns, brand stories, art experiences | Resources, input latency, reduced motion, alternative paths; never turn login, forms, or high-frequency tables into a forced animation show |

## Trend lifecycle — what to retire

| Layer | Examples | Update strategy |
|---|---|---|
| Long-term task principles | Readability, clear relationships, predictable interaction, accessibility | Keep; revise per new standards and user feedback; never sacrifice for a new style |
| Evolvable system conventions | Spacing scales, type scales, token formats, motion parameters, component APIs | Track system versions and test migrations; old parameters are not eternal truth |
| Expressive languages | Gradients, bento layouts, glass, thick borders, giant headlines, 3D | Judge per brand fit, task benefit, usage frequency, competitive context, and cost — no universal "expiry year" |

**Retire the mismatch, not the material**: abstract heroes unrelated to the
business, the same three cards on every page, contrast lowered to look
modern, complex states hidden for prettier screenshots. The same materials
remain good choices where they are justified, accessible, and
performance-controlled.

## Borrowing from case studies — decisions, not skins

Purposeful case selection (not a "world's best sites" ranking, not random
sampling, no real conversion/retention comparison):

- **Linear (2024, 2026 refreshes)**: an application's identity can come from
  precise relationships and consistent detail, not only loud decoration;
  frequently used tools need predictability — navigation receding must not
  become navigation unreadable. First-party intent is not proven task-speed
  gain; copying dark thin lines does not copy the taste.
- **Pentagram / Cohere (brand launched 2023-03-29)**: brand character comes
  from a set of choices in one direction across type, color, and graphics —
  a random purple gradient cannot substitute for a brand concept. Also not a
  new template for all AI products.
- **Stripe (2019 color system)**: saturated, expressive brand color coexists
  with verifiable color roles — write allowed text/background pairings and
  verify each, don't just show pretty swatches. Their exploration used
  CIELAB (not the OKLCH later tool-marketing claims); any perceptual space
  never exempts final contrast checks.
- **Carbon / GOV.UK (continuously maintained)**: reliable, plain, and
  explicit is a mature aesthetic — button copy that predicts the action,
  labeled fields, reused semantics, task-fit density. Taste is not "the more
  it looks like a creative studio, the better".
- **Work & Co / IKEA**: style consistency serves cross-channel task
  continuity (terms, objects, states connecting across web, internal tools,
  mobile) — not pixel-identical screens. Marketing numbers from case pages
  prove no visual style's causal effect without controls.

**Awwwards caveat**: published jury weights are design 40% / usability 30% /
creativity 20% / content 10%. Good for discovering art direction and
interaction ideas; an award proves nothing about WCAG, performance,
conversion, or complex-app efficiency. Ask separately: "what expression is
worth borrowing" and "can our users afford this interaction cost".

## On the "AI look"

Anthropic's 2026-03-24 engineering article lists generic purple gradients
and white cards among the phenomena it watches when evaluating originality —
a vendor-, task-, and evaluation-specific observation, **not** a cross-model
frequency study and not proof that purple is ugly. For tool interfaces,
forced originality can damage familiarity. The correct response is the
decision order in SKILL.md: task and brand first, materials with jobs,
verified states — not swapping one template for another.
