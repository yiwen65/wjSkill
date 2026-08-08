---
name: wiki
description: 'Manage the user''s Obsidian Markdown vault as a dual-track personal knowledge base: preserve low-friction human notes while safely capturing, classifying, moving, deduplicating, and linking notes, and incrementally compiling sourced reusable knowledge into the structured `_wiki` layer. Use for Obsidian/vault/wiki/PKM work such as “整理笔记”, “整理 Inbox”, “把资料沉淀到 wiki”, “摄入这篇文章”, “摄入 X 推文或 Article”, “查询我的知识库”, “更新 index/log”, “检查断链/孤立页/重复内容”, or maintaining wikilinks, frontmatter, sources, confidence, contradictions, and note provenance.'
---

# Wiki

Manage the vault as two cooperating systems:

- Treat `00-Inbox/`, `01-Daily/`, `02-Projects/`, `03-Knowledge/`, and `04-Sources/` as the human-owned workspace. Keep sensitive records in Git-ignored `90-Private/`. Preserve the user's wording and low-friction capture style.
- Treat `_wiki/` as the LLM-maintained compiled knowledge layer. Keep it structured, sourced, linked, and cumulatively updated.

Read [references/vault-profile.md](references/vault-profile.md) for this vault's identity and conventions. Read [references/workflows.md](references/workflows.md) before ingesting, organizing, compiling, or repairing notes. Use `scripts/find_vault.py` on both macOS and Linux; run `scripts/audit_vault.py` for a deterministic health inventory.

## Orient Before Acting

1. Set `WIKI_SKILL_DIR` to the directory containing this `SKILL.md`, then run `python3 "$WIKI_SKILL_DIR/scripts/find_vault.py"`. Use its resolved path for every read and write in the turn.
2. Discovery must prefer an explicit user path, `OBSIDIAN_VAULT_PATH`, and the current workspace. Otherwise use `/Users/w/Library/Mobile Documents/iCloud~md~obsidian/Documents/wiki` on macOS and `/home/w/Documents/Obsidian` on Linux.
3. Read the nearest `AGENTS.md` and obey it.
4. Inspect `git status --short`; treat all existing changes as user-owned.
5. For formal wiki work, read `_wiki/SCHEMA.md`, `_wiki/index.md`, and recent `_wiki/log.md` entries.
6. Inventory the requested scope, links, attachments, duplicate names, and candidate destinations before editing.
7. Search both filenames and content before creating a page. Prefer improving an existing canonical page over creating a near-duplicate.

Do not turn a read-only request such as “分析”, “审查”, or “给建议” into edits. When the user asks to create, manage, organize, ingest, compile, or fix, perform the scoped edits and validate them.

## Choose the Operation

- **Capture:** Create a human note from the matching `_meta/templates/` template. Keep capture friction low; ordinary notes need no formal frontmatter.
- **Organize:** Classify and move only clearly scoped human notes. Preserve ambiguous, mixed-purpose, empty, or unclear notes in place and report them.
- **Ingest/compile:** Preserve the source, extract evidence, and update the relevant `_wiki` pages instead of merely creating a standalone summary.
- **Query:** Read the index, search broadly, synthesize from actual pages, and distinguish sourced facts from personal or unsourced notes. Persist only when requested or when the request explicitly asks to manage the wiki.
- **Lint/repair:** Audit first, separate definite defects from heuristics, then make only authorized fixes.

## Ingest X Sources Safely

When the source is an `x.com`/`twitter.com` post or Article, read [references/x-ingest.md](references/x-ingest.md) before retrieval. Keep the original X URL as the canonical source and record the actual retrieval method, access date, and any fallback or completeness limitation in the raw record. Do not treat an empty short-post field as proof that an Article has no body. Before semantic duplicate search, normalize and compare the exact X `post_id` and, for Articles, `article_id`; same author/title/topic with a different ID is not a duplicate.

## Protect Authorship and Provenance

- Never rewrite a human note into polished AI prose merely to make it uniform.
- Keep direct observations, personal reflections, plans, and tentative ideas recognizable as the user's material.
- Do not fabricate a source, author, date, URL, quote, or confidence level.
- Treat external source files and existing `_wiki/raw/` bodies as evidence. Do not silently alter them during synthesis.
- Never put X cookies, `auth_token`, `ct0`, Bearer tokens, browser session data, or other credentials in the vault, source metadata, logs, shell history, or committed files.
- When a human note has traceable context but no external source, cite the note path where the schema permits it and label the compiled claim conservatively. Otherwise use `status: needs-source` and `confidence: low`.
- Record contradictions side by side with source and date. Do not flatten disagreement into a false consensus.
- Paraphrase sources; retain only short excerpts needed for verification and preserve attribution.

## Maintain the Compiled Wiki

For every created or materially updated formal page:

1. Use a lowercase kebab-case filename and the matching `_wiki/_templates/` page type.
2. Maintain every frontmatter field required by `_wiki/SCHEMA.md`.
3. Add only schema-approved tags.
4. Make important claims traceable through `sources` and inline context where useful.
5. Add at least two useful outgoing wikilinks; do not create empty placeholder pages solely to satisfy this count.
6. Reconcile the new evidence with related pages, including contradictions and stale claims.
7. Update `_wiki/index.md` once per batch.
8. Append one concise, parseable entry to `_wiki/log.md` once per batch. Preserve the log's existing format.

Prefer one-source-at-a-time ingestion unless the user requests a batch. A source should change every relevant existing synthesis page, but touch only pages justified by its evidence.

## Organize Human Notes Conservatively

- Use semantic destination rules from `vault-profile.md`, not filename guessing alone.
- Before moving, check exact Obsidian wikilinks, embedded assets, name collisions, aliases, and backlinks.
- Move content without silently editing its meaning. Make only link/path adjustments required by the move unless content editing was requested.
- Update exact backlinks after a move and verify the destination and attachments exist.
- Do not delete source notes after compilation. Do not use permanent deletion as a cleanup shortcut.
- Keep uncertain candidates in place and return a short decision list.

## Validate and Report

Run checks proportional to the change:

```bash
WIKI_SKILL_DIR="/path/to/installed/wiki"
WIKI_VAULT="$(python3 "$WIKI_SKILL_DIR/scripts/find_vault.py")"
python3 "$WIKI_SKILL_DIR/scripts/audit_vault.py" --vault "$WIKI_VAULT"
git -C "$WIKI_VAULT" diff --check -- path/to/changed-note.md
git -C "$WIKI_VAULT" status --short
```

For `_wiki` edits, also verify required frontmatter, non-empty or conservatively handled `sources`, outgoing links, index coverage, log entry, and exact broken-link results. Open changed notes in Obsidian when UI access is available and layout, embeds, or graph behavior matters.

Report:

- files created, updated, or moved;
- what was intentionally left unchanged and why;
- sources and uncertainties;
- validation performed and any pre-existing unrelated failures.

Never stage, commit, push, reset, or absorb unrelated changes unless the user separately authorizes that Git action.
