# X Source Ingestion

Use this reference for public `x.com` or `twitter.com` URLs. The original X URL remains the canonical provenance; an API or CLI is only the retrieval method.

## Choose a retrieval path

1. **FxTwitter API is the default first choice** for a public, read-only X post or Article. Use the no-credential endpoint before generic URL proxies, search, or authenticated tooling:

   ```text
   https://api.fxtwitter.com/<handle>/status/<id>
   ```

   This is a third-party mirror, not the official X API. Treat it as a convenience source with no guaranteed availability or schema. Do not use it for private posts or account actions.

2. Parse the response according to its shape:

   - Ordinary posts normally expose text at `tweet.text`.
   - X Articles may have an empty `tweet.text` while the full body is under `tweet.article.content`.
   - Article content may be DraftJS-like JSON. Extract `content.blocks[].text` in order, preserve meaningful block boundaries, and retain entity/style data when links or formatting matter.
   - Capture the Article title, post/article ID, author, publication timestamp, media, and source URL when present.

3. If the public endpoint fails, returns incomplete content, or the task needs search, threads, timelines, bookmarks, or other authenticated views, use the local `bird` CLI through its configured credential source:

   ```bash
   bird read "$X_URL" --json
   bird thread "$X_URL" --json
   bird search "QUERY" --json
   ```

   Prefer the user-managed `bird` shim and the installed CLI's current help. Do not patch an NVM- or npm-managed package file; upgrades may replace it. If an upgrade breaks the command, resolve the active global package through `npm root -g` behind a user-managed shim instead.

4. If both paths fail, report the failure and its cause. Do not infer, reconstruct, or silently substitute a different post.

## Credentials and privacy

- Never place `auth_token`, `ct0`, Bearer tokens, cookies, or browser-profile data in the vault, `_wiki/raw/`, logs, shell command arguments, or Git-tracked files.
- Do not echo credentials while diagnosing `bird`; check only exit status or redact output.
- Prefer a local permission-restricted credential file or browser-cookie extraction configured outside the vault. Treat pasted credentials as compromised and recommend rotation.
- Use Bird for personal, local retrieval only unless the user has separately established an authorized, policy-compliant integration.

## Duplicate detection and canonical identity

Treat X identity as an exact-key problem before treating it as a semantic-search problem:

1. Normalize the user URL for comparison by lowercasing the host, removing query parameters and fragments, and extracting the numeric `/status/<post_id>` or `/article/<post_id>` ID. Keep the original user URL, including its query string, as the canonical provenance value in the raw record.
2. Search existing raw records for the normalized `post_id` before searching titles, authors, filenames, or concepts.
3. For an Article, also extract and compare the exact `article_id` from the API payload. Same `post_id` or same `article_id` means the existing raw record is the canonical source; update its retrieval metadata or integrate new evidence instead of creating a second record.
4. Treat `/status/<id>` and `/article/<id>` with the same numeric ID as URL aliases, not different sources. Do not infer identity from a shared author, similar title, topic, date, or semantic similarity: different IDs are different X sources unless the source itself explicitly establishes a repost or quotation.
5. If the existing record lacks IDs and exact identity cannot be established, classify it as `possible related source`, not `duplicate`; ask or preserve a separate record rather than silently merging.
6. When an ID mismatch is discovered after editing, restore the prior record and create/update the correct source record. Re-run hash and audit checks before reporting success.

## Completeness and provenance checks

Before compiling an X source, verify the response has the expected post ID and author. For Articles, record the number of non-empty blocks and extracted characters privately during validation; do not dump the full response into logs. If the public mirror and Bird differ, distinguish formatting/normalization differences from missing content and preserve the retrieval method in the source record.

For public copyrighted Articles, preserve the URL, attribution, metadata, a source-faithful deep analysis and structured summary, and short verification excerpts by default. Store the full body only when the user explicitly requests it and retention is appropriate under the applicable policy; never create duplicate full-text copies merely because two retrieval methods were used.
