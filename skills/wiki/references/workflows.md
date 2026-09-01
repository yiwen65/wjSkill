# Operational Workflows

## Contents

- Capture a human note
- Organize Inbox or another human-note scope
- Ingest a source and compile knowledge
- Compile human notes into the wiki
- Query and optionally persist an answer
- Audit and repair
- Resolve contradictions
- Handoff checklist

## Capture a human note

1. Determine whether the note is a capture, daily entry, project, resource, or source.
2. Start from the matching `_meta/templates/` template.
3. Preserve the user's wording and add only structure that improves retrieval or actionability.
4. Add relevant existing wikilinks without inventing relationships.
5. Put unknown or mixed material in `00-Inbox/`; do not force a classification.

## Organize Inbox or another human-note scope

### Read-only inventory

1. List every Markdown file in scope, including empty files.
2. Read each candidate and identify its dominant purpose, current links, embeds, and references.
3. Search candidate destinations and duplicate basenames across the vault.
4. Search exact incoming wikilinks separately from attachment-path text.
5. Classify each candidate as `clear move`, `merge candidate`, `keep`, or `needs decision`.

### Execute

1. Move only `clear move` items within the user-authorized scope.
2. Merge only when the user requested consolidation and a canonical target is evident. Preserve all unique content and source attribution.
3. Update exact backlinks and only the paths affected by the move.
4. Keep mixed-purpose, empty, or ambiguous notes in place.
5. Verify new paths, attachments, and absence of exact stale wikilinks.

Never infer that an untracked note is disposable. Never treat a broad filename match inside an asset path as a broken note link.

## Ingest a source and compile knowledge

1. Choose one canonical source copy using `vault-profile.md`:
   - If the complete source already exists inside `04-Sources/` or elsewhere in the vault, keep it there and create only a non-duplicative `_wiki/raw/` ingestion record when needed.
   - If the user supplies pasted text or an external local file for direct wiki ingestion, preserve one copy under `_wiki/raw/`.
   - Do not store the same full body in both `04-Sources/` and `_wiki/raw/`.
2. Retain title, URL, author, publication date, capture date, original vault path, content hash, and attachment references when available. Never substitute ingestion date for an unknown publication date.
3. For a URL, retrieve the page from the named source and distinguish publication date from access date. Store a source-faithful deep analysis and structured summary that follows the source's native organization, plus short verification excerpts by default—not a simple abstract or metadata card, and not a full copyrighted page. Follow `references/raw-structure.md`: preserve the source's own headings, order, hierarchy, timestamps, or other native organization instead of applying a universal raw-body template. Do not replace a user-supplied source with third-party web summaries.
4. During retrieval, enumerate substantive source images and extract them into `_wiki/raw/assets/<raw-stem>/` in source order. Replace each original image marker at the same location with a vault-local `![[...]]` embed, preserve caption/alt text and nearby explanation, and store URL/location/local-path/media-type/SHA-256 provenance in `_wiki/raw/assets/<raw-stem>/_provenance.json` rather than in the Markdown body. Do not emit inline HTML provenance comments or print image URLs beside embeds. A failed image must remain visible as a failure marker without its URL in the body, make the capture partial, and record the safe URL/failure details in the sidecar; never silently leave only a remote URL or omit the figure.
5. Read the source completely enough to identify thesis, claims, evidence, limitations, entities, concepts, comparisons, and durable questions.
6. Read `_wiki/index.md` and, for X sources, perform exact canonical identity matching by normalized `post_id`/`article_id` before searching synonyms and aliases. A same-author or semantically similar page with a different X ID is only a related source, never an automatic duplicate.
7. Present or internally form an update map: canonical source, ingestion record if needed, existing pages to revise, justified new pages, contradictions, index entry, and log entry.
8. Read `references/concept-quality.md` before creating or reshaping concept pages. Update existing canonical concepts before creating new pages; use the matching `_wiki/_templates/` template for justified new pages, but treat its frontmatter/governance as the contract rather than a fixed prose outline. Keep book/report entities, chapter/source bridge pages, canonical concepts, comparisons, and syntheses distinct. A chapter page may map source structure to concepts, but should not become a duplicate canonical concept merely because the source has a chapter heading.
9. Assign or preserve `page_role` and `evidence_scope` for every formal page touched. If a high-confidence page has one source, mark its scope `source-local` unless comparable cross-source evidence is actually present.
10. Cite the source from every page whose important claims depend on it. Do not imply that a page was fully verified when only one source supports it.
11. Update related pages bidirectionally where the relationship is useful; express important relationships in prose instead of a bare `Related` list.
12. Update the index review queue and append one structured log entry after the content batch.
13. Validate local image decodability, embed resolution, provenance/hash consistency, raw body hash, and report any failed or approximate image placement.

Prefer a narrow, deep integration over generating many thin placeholder pages.

## Compile human notes into the wiki

1. Scan only the directories or time range the user named.
2. Separate transient content from reusable knowledge:
   - Keep reminders, raw emotion, one-off status, and private details in the human note unless explicitly requested.
   - Compile stable methods, recurring decisions, definitions, lessons, and evidence-backed conclusions.
3. Treat the original human note as immutable provenance during compilation; do not replace it with the generated wiki page.
4. If claims lack external evidence, mark the formal page `status: needs-source` and `confidence: low`, or defer compilation when the result would have little durable value.
5. Link the compiled page back to related concepts and, where the schema permits, to the originating note.
6. Summarize what was compiled and what remained only in the human layer.

## Query and optionally persist an answer

1. Read `_wiki/index.md` first.
2. Search formal pages, source records, and relevant human notes; do not assume the index is complete.
3. Read the cited pages and follow source references for disputed or high-stakes claims.
4. Answer with Obsidian wikilinks or explicit note paths and label uncertainty.
5. If the user asks to save the result, create or update one durable `queries/` page, connect it to related pages, update the index, and log the operation.
6. Do not persist routine chat answers automatically.

## Audit and repair

Run the deterministic auditor first:

```bash
WIKI_VAULT="$(python3 "$WIKI_SKILL_DIR/scripts/find_vault.py")"
python3 "$WIKI_SKILL_DIR/scripts/audit_vault.py" --vault "$WIKI_VAULT" --format markdown
```

Interpret findings carefully:

- `error`: definite schema or reference failure needing attention.
- `warning`: quality concern requiring judgment, such as an orphan or low linkage.
- `info`: inventory, not a defect.

Then inspect suspected duplicates semantically; filename similarity alone does not prove duplication. For repair requests, fix definite in-scope issues, rerun the audit, and log only material wiki repairs. For audit-only requests, do not edit or append to the log.

For a governance audit, additionally enumerate formal pages with missing `page_role`/`evidence_scope`, `confidence: high` plus one source, `status: needs-source|stale|draft`, missing `review_status`, generic empty-link sections, and index omissions. These are review candidates, not automatic grounds for rewriting supported content.

## Resolve contradictions

1. Identify the exact claims, scope, dates, and sources.
2. Determine whether the difference is a real contradiction, a change over time, or differing definitions/conditions.
3. Preserve both supported claims with their contexts.
4. Update the synthesis to state the current best interpretation and why.
5. Lower confidence or mark `stale`/`needs-source` when the evidence cannot resolve the conflict.
6. Add an open question or follow-up source need instead of guessing.

## Handoff checklist

- Existing dirty work remained untouched.
- Human-authored wording and provenance were preserved.
- No ambiguous or empty notes were moved or deleted.
- Sources, dates, and attribution were not invented.
- Substantive source images were archived and embedded at their source positions, or explicit failure markers and provenance were retained.
- Formal pages satisfy the live schema and have meaningful links.
- Exact backlinks, embeds, and renamed paths were checked.
- `_wiki/index.md` and `_wiki/log.md` match material wiki changes.
- File-scoped whitespace checks and the vault audit were run.
- The report separates completed changes, deferred decisions, and pre-existing issues.
