---
name: visual-explain
description: Create a self-contained HTML visual explainer that teaches one topic to a beginner with accurate pictures, a clear visual sequence, and minimal text. Use when the user asks for a picture-first, or dead-simple visual explanation of how something works. Do not use for ordinary prose explanations, slide decks, production interfaces, or architecture documentation.
---

# Visual Explain

## Outcome

Teach the requested topic to someone with no prior knowledge through one polished
HTML artifact with large, meaningful visuals and few words. Simplify the
explanation, not the truth: after a quick scan, the reader should understand the
topic's essence and its main sequence, relationship, or mechanism.

Use the user's language. Ask a question only when the topic is missing or an
ambiguity would materially change the explanation; otherwise choose the most
common beginner-friendly interpretation and state that framing briefly.

## Build the explanation

Before designing the page, reduce the topic to:

- one plain-language sentence that answers "What is it?";
- three to six essential parts or steps;
- the causal, spatial, or before-and-after relationship between them;
- one concrete analogy when it improves understanding.

Keep only details needed to make that model accurate. Use consistent objects,
colors, and labels; label arrows with actions. Distinguish an analogy visually
from the real mechanism and note its important limit. Surface a material unknown
or disputed interpretation instead of inventing certainty.

Choose the smallest visual story that fits the concept: a whole-picture hero
followed by a short sequence is a useful default, while comparison, timeline,
layered zoom, or cause-and-effect flow may be clearer. Prefer diagrammatic HTML,
CSS, and inline SVG over decorative imagery. Use short labels and at most one
brief sentence per step. Add interaction or animation only when it clarifies
order, cause, scale, or state; the page must remain understandable without it.

## Artifact contract

Produce one standalone `.html` file that:

- keeps CSS, SVG, and any JavaScript inline and works without network access;
- is responsive at desktop and narrow mobile widths;
- uses semantic HTML, readable contrast, keyboard-visible controls, and
  reduced-motion support when animation exists;
- avoids external frameworks, build steps, and unrelated assets;
- contains no broken, clipped, overlapping, or horizontally overflowing content.

Write to the user's requested path. Otherwise use a clear, collision-safe
filename in the current workspace. If file creation is unavailable, return the
complete HTML in one fenced block. When a file is created, return a link to it
with a one-sentence description.

## Completion check

If rendering tools are available, inspect the page at one wide and one narrow
viewport. Otherwise perform source-level checks and clearly say rendering was
not verified. Finish only when:

- the first screen communicates the essence without prior explanation;
- the visual reading order and mappings are unambiguous;
- the file opens locally with no missing dependencies; and
- the explanation preserves important boundaries between fact, analogy, and
  uncertainty.
