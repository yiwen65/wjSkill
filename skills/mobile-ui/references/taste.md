# Taste: Definition, References, Comparison, Training

Design taste, operationally: **in a stated context, recognize the quality of
visual and interaction relationships, explain why they are good or bad, and
propose improvements with stated tradeoffs.** Measure a design agent not by
how many aesthetic terms it knows, but by whether it finds real problems in
concrete tasks, justifies its tradeoffs, and verifies improvements on actual
interfaces and behavior.

## Three layers — never confuse them

| Layer | Question | Judged by |
|---|---|---|
| Floor quality | Errors, unusable or inaccessible parts? | Standards checks, runtime tests, assistive-tech tests |
| Contextual quality | Do priority, density, rhythm, and interaction fit the task? | Same-task comparison, expert review, target-user task tests |
| Aesthetic preference | Among usable options, which expression fits brand and audience? | Contextual preference studies, brand review, multi-option comparison |

Do not dress a layer-3 preference up as a layer-1 defect. Research on website
visual preference (Reinecke & Gajos, CHI 2014, class B) shows preferences
differ across individuals and groups — its subjects were websites, so it
supports only "don't assume one universal aesthetic", not "mobile group X
must prefer style Y".

## Observable differences (review heuristic, class C — not a validated scale)

| Dimension | Good | Poor | Observable evidence |
|---|---|---|---|
| Task/emphasis match | Visual priority mirrors the current task | Decoration or marketing overpowers core content | Requirement priority vs actual emphasis order; task find-time records |
| Grouping | Belonging and click scope readable without reading every word | Distance, background, and borders give contradictory grouping | Grouping annotation; click-scope tests |
| Proportion & rhythm | Type, icons, whitespace, and content volume cohere | Giant titles over tiny body; inline elements unbalanced | Same-component comparison; baseline and spacing checks |
| Typography quality | Stable text roles; hierarchy survives long text and large sizes | Clipping, thin weights, chaotic weight, meaning-breaking wraps | Font-scaling, multilingual, long-content screenshots |
| Visual discipline | Every emphasis has a job; exceptions have reasons | Shadows, borders, gradients, badges applied uniformly and indiscriminately | Token diffs; stated purpose per container/emphasis |
| Brand expression | Consistent voice without logo dependence, not blocking tasks | Collage of references, or every product on one template | Item-by-item check against the brand brief |
| Information density | Supports the task; stable as content volume changes | Info deleted for airiness, or type endlessly shrunk to fit | Zero/few/many/long-title data sets |
| State resilience | Order survives default, failure, offline, large text | Only the showcase screenshot holds up | State × device matrix |
| Explanation ability | "What changes, why, at what cost, verified how" | Only "more premium", "not modern enough" | Critic output evidence and retest conditions |

The middle column ("average") is whatever sits between these poles; the
poles are what matter for calibration.

## Building a reference library with reasons — not an image folder

Each entry records:

```yaml
reference:
  task: what the user is accomplishing
  platform: iOS / Android
  captured_at: capture date
  app_version: known version or unknown
  screen_and_state: screen and interaction state
  audience_and_context: target users and usage conditions
  hierarchy: how information importance maps to visual emphasis
  reusable_principle: the transferable design principle
  tradeoff: what was sacrificed to gain what
  do_not_copy: brand-, content-, or platform-specific details
  evidence: screenshots, flow records, source, usage rights
```

Include varied densities, brand personalities, and content types — plus
failure states and large-text states, not just marketing pages, concept
shots, and perfectly-filled happy paths. This is a suggested knowledge
organization (class C); no fixed image count guarantees taste improvement.

**What to learn from mature cases:**

- **Apple Clock** (used in HIG Tab Bar guidance): learn destination/action
  separation — not its labels, icons, or colors.
- **Spotify Encore × Accessibility** (2023, class B): shared components can
  carry some accessibility capability, but components cannot replace correct
  implementation in every context. It's a web-component case — its sizes and
  behaviors are not native mobile specs.
- **Material 3 Expressive research** (Google, 2025, class B, vendor-run):
  learn *purposeful* expression — extract how attention, shape, color, and
  motion serve tasks, then validate in your own product. It neither proves
  "more vivid is always better" nor is mere trend-chasing to ignore.

## Comparison and training methods

1. **Same-task comparison, ties allowed.** Fix the task, required content,
   platform, and device conditions. Ask separately: which identifies key
   information more easily? Which layout relationships are clearer? Which
   fits the stated brand? Are the two merely different in style rather than
   quality? Label "standards defect", "task effect", and "brand preference"
   separately. Randomize left/right positions; hide brand names in suitable
   rounds to reduce prestige bias, then review again with brand context.
   (UIClip, UIST 2024, class B supports quality-assessment and comparison
   learning; the full pipeline here is the source methodology's extension.)

2. **Single-variable counterexamples for causal explanation.** Change one
   variable of the same design at a time: in-group spacing larger than
   between-group; helper text more prominent than primary info; container
   height fixed while type scales; icon glyph constant while hit region
   grows; remove one working label and watch "cleaner" become "harder".
   Require the agent to state what relationship changed — not just pick the
   nicer picture. Include counterexamples against minimalism: some content
   needs containers, some data pages need density, some brands need strong
   expression — so the agent doesn't learn "sparse, white, big = always good".

3. **Compare structures, not just recolors.** For the same task, propose
   different organizations — content-browse-first, action-first,
   status-overview-first — and compare content order, action entries, and
   density before comparing fonts, shapes, and colors. Otherwise the agent
   learns only to reskin one template.

4. **Generate–run–inspect–fix–regress loop.**

   ```text
   task & constraints → retrieve close references → generate candidate
   structures → implement and actually render → rule checks + visual
   comparison + task tests → fix high-impact issues → regress other states,
   windows, and text conditions → save evidence-backed design lessons
   ```

   "Compiles" and "high image similarity" are not sufficient quality
   conditions. (UICoder, 2024, class B: automated feedback helps generation,
   but simplified outputs, weak visual-detail judgment, and uncovered dynamic
   interaction still need separate verification.)

5. **Independent test sets — don't keep pleasing your own critic.** Track:
   defect identification (recall, false-positive rate, severity accuracy);
   comparison judgment (agreement with independent review, tie handling,
   cross-style stability); repair ability (defect elimination, new
   regressions, required content preserved); real usability (critical tasks
   completed, errors recovered, input preserved); robustness (large text,
   long content, windows, offline, assistive tech). Split train/test by app,
   brand, or whole flow — not by near-duplicate screenshots of one screen.
   An uncalibrated "90% aesthetic accuracy" proves nothing.

6. **Distinguish three kinds of "learning".** Reference retrieval improves
   context; critic and rule calibration improves checking; fine-tuning or
   other parameter training changes weights. Writing repair lessons into
   external memory does not mean the weights learned them. Before real
   training, check licensing, privacy, duplication, label quality, and style
   coverage of reference data.
