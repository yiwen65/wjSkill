# Concept Page Quality and Structure

Use this reference when creating, reviewing, or substantially rewriting `_wiki/concepts/` pages.

This is a **semantic contract, not a Markdown template**. Raw records follow the source's structure; concept pages follow the reusable concept's structure.

## What a concept page is for

A concept page is a durable knowledge-graph node that explains one reusable idea, method, architecture, workflow, evaluation protocol, or technical boundary. It is not:

- a copy of the raw source record;
- a chapter-by-chapter transcript;
- a generic source summary;
- a list of names or benchmark numbers;
- a cross-source synthesis disguised as a single-source fact.

A source can justify a concept page when the concept is central to that source or likely to recur. One source is sufficient for a seed page if the page clearly marks its evidence scope and confidence; later sources should strengthen the canonical page instead of creating parallel chapter-shaped pages.

## Required semantic invariants

The prose layout may vary, but a usable concept page should make the following recoverable from its body:

1. **Scope and definition** — what the concept means here and what it does not mean.
2. **Role or interface** — where it sits in the system, workflow, or research problem; identify important inputs, outputs, dependencies, or neighboring concepts when applicable.
3. **Mechanism or reasoning** — how it works, why it matters, and which stages, states, losses, constraints, or decisions carry the explanation.
4. **Evidence boundary** — distinguish direct source claims, engineering interpretation, and unresolved uncertainty. Keep numbers tied to dataset, split, metric, hardware, scenario, date, or protocol where relevant.
5. **Applicability and failure modes** — assumptions, trade-offs, conditions of validity, and ways the concept can fail or be misused.
6. **Relationships** — explain meaningful links to existing pages; do not append a bare `Related` list solely to satisfy a link count.
7. **Traceability** — important claims must be supported by `sources`, with the source role and scope clear enough for a future reader to follow.

Do not invent a section merely to satisfy this list. If an invariant is not applicable or not supported by the source, state that boundary briefly or omit it rather than filling it with generic prose.

## Frontmatter role and evidence contract

For formal concept pages, preserve these fields when creating or materially updating a page:

```yaml
page_role: canonical | source-bridge | seed | synthesis
evidence_scope: source-local | cross-source | time-sensitive | user-note
```

Use `source-bridge` for a chapter/paper mapping page and `canonical` for a reusable node accumulated across sources. Use `seed` when the page is useful but evidence is still narrow. Use `synthesis` for comparisons, routes, trends, and decision rules. `confidence` describes evidence strength inside `evidence_scope`; it does not by itself authorize cross-source, current-market, or production claims.


Keep these roles distinct:

- **Book/report entity page:** identifies the work, gives its map/navigation, states source completeness, and summarizes the work's system-level contribution and limits.
- **Chapter/source bridge page:** explains what the source unit covers and maps it to canonical concepts. It may retain chapter order, but it is not the final definition of every concept mentioned in that chapter.
- **Canonical concept page:** owns the reusable concept across sources. Its title should be the concept, not merely `Chapter N`, unless the chapter itself is the durable object being queried.
- **Comparison/synthesis page:** owns cross-source judgments, alternatives, trends, or trade-offs that should not be hidden inside a single concept page.

A book ingest may keep chapter bridge pages, but do not create a new canonical concept for every chapter by default. Prefer a narrow set of durable concepts and update them as later papers, standards, datasets, or implementation sources arrive.

## Type-specific guidance

Choose the content shape from the page's actual job:

### Algorithm or method

Explain the problem/representation, input-output data flow, objective or constraints, why the method works, implementation assumptions, evaluation protocol, failure modes, and boundaries against nearby methods. Include equations only when they reveal the mechanism and preserve the source's notation/uncertainty.

### System or architecture

Explain components, interfaces, timing/data/control flow, resource and fault boundaries, deployment assumptions, and validation implications. Do not reduce architecture to a component inventory.

### Dataset, benchmark, or testing method

Explain task, scenario/data composition, split, metric direction, evaluation loop, sampling/statistical assumptions, reproducibility boundary, and what the result can and cannot establish. Never present an unscoped number as a general capability claim.

### Security or safety concept

State assets and trust boundaries, threat or failure model, attack/failure surface, mitigations, residual risk, and evidence status. Keep defensive summaries non-operational when the source concerns attacks.

### Industry, product, or deployment concept

Separate time-sensitive source claims from durable mechanism. Preserve date, geography, ODD, product stage, regulation, and evidence limitations. Use `entity`, `comparison`, or `synthesis` when the page is primarily about a company, product, route, or market landscape rather than a technical concept.

## Source integration and update policy

- Prefer updating an existing canonical concept when a new source adds evidence, a mechanism, a boundary, or a counterexample.
- Add the source to `sources` and update `source_count` when the schema supports it; do not inflate source count from citations merely mentioned by a book.
- Keep “the source states” separate from “the wiki infers” when the distinction affects confidence or generalization.
- Do not move raw-only extraction caveats into a confident concept claim; carry them forward where they qualify the interpretation.
- If the concept is only a passing mention or the evidence is too thin, keep it in the chapter/source bridge or plain prose rather than creating a new page.
- Avoid broad edits across many unrelated concepts. Update only pages directly justified by the source.

## Prose quality and conceptual voice

The semantic invariants above are a quality contract, not a mandatory chapter list. A concept page should have the shape of the concept it owns.

- Do not copy the raw record's source headings into a canonical concept one by one. Reorganize around the reusable mechanism, interface, decision rule, or boundary.
- Avoid a default sequence such as `Scope → Mechanism → Applicability → Evidence boundary` when the concept does not need each part as a separate heading. Put a boundary in the paragraph where it matters, or use a source-specific heading that helps the reader.
- Prefer direct conceptual statements over repeated attribution leads such as “文章指出……”, “作者认为……”, or “本页是……的编译”. State the mechanism first, then mark source-local evidence where the distinction matters.
- Keep one clear evidence/provenance passage when the page is seed or source-local. Do not repeat the same uncertainty disclaimer after every claim unless the claim has a different protocol or source boundary.
- A useful page may be asymmetric: one mechanism can deserve several paragraphs while a passing example needs only one sentence. Do not pad sections to satisfy an outline or a link-count checklist.
- Read the page once without its frontmatter. If it sounds like a report summarizing a report rather than an explanation a future reader can reuse, revise the prose before accepting the page.

## Review checklist

Before accepting a concept rewrite, verify:

- the page title identifies a reusable concept or an explicitly justified source bridge;
- the page is not merely a compressed copy of the raw record;
- the body explains mechanism/role rather than only listing terms;
- adjacent concepts and boundaries are explicit where confusion is likely;
- every benchmark, date-sensitive claim, and external citation retains its scope;
- links are meaningful and point to existing pages;
- `page_role` and `evidence_scope` match the page's job and do not overstate generalization;
- frontmatter, `sources`, `status`, `confidence`, and index/review-queue coverage remain valid;
- the page is deep enough to reuse without reopening the source, but not padded with unsupported generalities.
