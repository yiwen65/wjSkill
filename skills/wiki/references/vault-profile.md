# Vault Profile

## Cross-device locations

Use these fixed platform paths:

- macOS: `/Users/w/Library/Mobile Documents/iCloud~md~obsidian/Documents/wiki`
- Linux: `/home/w/Documents/Obsidian`

`scripts/find_vault.py` first honors an explicit path, `OBSIDIAN_VAULT_PATH`, or the current workspace, then selects the matching platform path. It validates these repository markers before allowing changes:

- `.obsidian/`
- `README.md`
- `_wiki/SCHEMA.md`
- `_meta/Agent Workflow.md`

Do not parse Syncthing configuration or scan unrelated directories. Resolve symlinks before comparing paths.

## Dual-track structure

| Path | Owner and purpose | Default treatment |
| --- | --- | --- |
| `00-Inbox/` | Human quick captures and uncertain material | Process conservatively; ambiguity stays here |
| `01-Daily/YYYY/MM/` | Human chronology, journal, and reflection | Preserve voice and dates; extract only durable knowledge |
| `02-Projects/` | Active outcomes with a finish condition | Keep project context and next actions together |
| `03-Knowledge/` | Durable cross-project knowledge organized by domain | Keep one canonical reusable note |
| `04-Sources/` | Human-curated external sources and attachments | Preserve URL, author, date, attribution, and binaries |
| `90-Private/` | Credentials and sensitive infrastructure notes | Keep Git-ignored; never expose from public notes |
| `_meta/templates/` | Human note templates | Use for new ordinary notes |
| `_wiki/raw/` | Wiki ingestion records and preserved evidence | Read as source; do not silently rewrite during synthesis |
| `_wiki/entities/` | People, organizations, products, projects, tools | LLM-maintained formal pages |
| `_wiki/concepts/` | Ideas, methods, architectures, workflows | LLM-maintained formal pages |
| `_wiki/comparisons/` | Alternatives, tradeoffs, and decisions | LLM-maintained formal pages |
| `_wiki/queries/` | Durable questions and evidence-backed answers | Persist only reusable answers |
| `_wiki/index.md` | Content-oriented map of the compiled wiki | Update for every formal page batch |
| `_wiki/log.md` | Append-only operational history | Append once for material operations |
| `_wiki/SCHEMA.md` | Authoritative wiki schema and taxonomy | Read before formal wiki edits |

Do not force the traditional notes into entity/concept/comparison types. The `_wiki` is a compiled projection, not a replacement for the human workspace.

## Current routing map

Route by lifecycle before topic:

1. Keep unresolved captures in `00-Inbox/`.
2. Keep chronology in `01-Daily/`.
3. Put work with a goal, deliverable, or finish condition in `02-Projects/`.
4. Put durable cross-project knowledge in `03-Knowledge/`.
5. Put raw external evidence and attachments in `04-Sources/`.
6. Put credentials and sensitive infrastructure records in `90-Private/` without public backlinks.

### `02-Projects/`

- `自动驾驶/天驰 OS/`: platform-specific deployment, time synchronization, server operations, and perception debugging.
- `自动驾驶/云乐/`: mapping, calibration, LiDAR configuration, and project debugging.
- `软件/`: active software products such as HR tooling.

### `03-Knowledge/`

- `AI/`: `提示词/`, `Vibe Coding/`, and `智能体与工具/`.
- `自动驾驶/`: `基础知识/`, `标准法规/`, `算法/`, `开源框架/`, `工程实践/`, `方案设计/`, `调研报告/`, `供应链/`, and `学习资源/`.
- `软件工程/`: `Linux/`, `Git/`, `编程语言/`, `网络/`, `后端与平台/`, `DevOps/`, and `工具/`.
- `产品与管理/`: product development, project management, engineering management, recruiting, and work methods.
- `个人成长/`: action systems, thinking, psychology, and communication.
- `财务/`: investment and entrepreneurship.
- `阅读/`: book notes and reading synthesis.

Keep project-specific debugging in `02-Projects/`; extract only reusable conclusions into `03-Knowledge/` and link between them. Do not recreate `03-Areas/`, `04-Resources/`, or `05-Sources/`.

### One canonical source copy

- Keep a source already stored in `04-Sources/` or another human-note path in place. Do not copy its full body into `_wiki/raw/`.
- Create a non-duplicative `_wiki/raw/` ingestion record only when formal pages need the schema's `raw/...` source reference. Record the original vault path, metadata, hash, and a source-faithful deep analysis and structured summary; follow `references/raw-structure.md` rather than forcing a fixed body template.
- For user-provided pasted text or an external local attachment not yet in the vault, preserve one canonical copy under the appropriate `_wiki/raw/` folder when ingesting directly into the wiki.
- For a public web page, store URL, author/date when known, access date, a source-faithful deep analysis and structured summary that follows the page's own heading/narrative order, and only short verification excerpts. Do not archive a full copyrighted article by default.
- For substantive images in a public web page or X Article, archive the retrieved image bytes under `_wiki/raw/assets/<raw-stem>/` and embed each image at its original position in the raw record with `![[...]]`; keep the raw Markdown body limited to the image and source-provided caption/alt text, store source URL/location/media type/byte-hash provenance in `_wiki/raw/assets/<raw-stem>/_provenance.json`, and mark failed extraction without printing the image URL in the body.
- Never keep two independently editable full-text copies. If the original moves, update the ingestion record rather than duplicating it.
- Treat Git ignore as version-control isolation, not encryption. Do not quote or surface `90-Private/` contents unless the user explicitly requests the exact private note.

## Naming and linking

- Use `YYYY-MM-DD.md` under daily year/month folders.
- Use clear Chinese or English titles for human notes.
- Use lowercase kebab-case slugs for formal `_wiki` pages.
- Prefer explicit Obsidian links such as `[[03-Knowledge/AI/提示词/提示词优化|提示词优化]]` when basename collisions or cross-layer ambiguity are possible.
- Preserve embeds such as `![[04-Sources/assets/example.png]]`; distinguish asset-path matches from stale note wikilinks.
- Raw ingest image embeds should use vault-local paths such as `![[_wiki/raw/assets/<raw-stem>/001-figure.png|caption]]`; verify the referenced asset exists and is decodable before accepting the record.
- Do not assume a directory is a valid note link.

## Formal page contract

Read `_wiki/SCHEMA.md` live because it is authoritative. At the current schema revision, formal pages require:

```yaml
---
title: Page title
created: YYYY-MM-DD
updated: YYYY-MM-DD
type: entity | concept | comparison | query | schema | index | log | raw/article
tags:
  - approved-tag
sources:
  - raw/articles/example.md
status: seed | active | draft | needs-source | verified | stale | archived
confidence: low | medium | high
page_role: canonical | source-bridge | seed | synthesis
evidence_scope: source-local | cross-source | time-sensitive | user-note
---
```

Current quality rules include at least two meaningful outgoing wikilinks, traceable important claims, no `confidence: high` with empty `sources`, page-role/evidence-scope alignment, index/review-queue maintenance, and structured log maintenance. Concept pages must follow `references/concept-quality.md`: preserve semantic invariants while choosing prose structure by concept role; chapter/source bridge pages are not automatically canonical concepts. Pages over about 200 lines are candidates for splitting, not automatic splits.

## Repository checks

This is a Markdown vault with no checked-in build or test runner. Use:

```bash
WIKI_VAULT="$(python3 "$WIKI_SKILL_DIR/scripts/find_vault.py")"
git -C "$WIKI_VAULT" status --short
git -C "$WIKI_VAULT" diff --check
# macOS: open -a Obsidian "$WIKI_VAULT"
# Linux: obsidian "$WIKI_VAULT"  # when the CLI is available
```

Use file-scoped `git diff --check` when repository-wide output comes from unrelated pre-existing edits. Never reset or stage unrelated work.
