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
   - Capture the Article title, post/article ID, author, publication timestamp, media, and source URL when present. Substantive image media must be downloaded into the raw asset folder and embedded at its source position; do not treat a media URL or empty placeholder as the final raw representation.

3. If the public endpoint fails, returns incomplete content, or the task needs search, threads, timelines, bookmarks, or other authenticated views, use the local `bird` CLI through its configured credential source:

   ```bash
   bird read "$X_URL" --json
   bird thread "$X_URL" --json
   bird search "QUERY" --json
   ```

   Prefer the user-managed `bird` shim and the installed CLI's current help. Do not patch an NVM- or npm-managed package file; upgrades may replace it. If an upgrade breaks the command, resolve the active global package through `npm root -g` behind a user-managed shim instead.

4. If both paths fail, report the failure and its cause. Do not infer, reconstruct, or silently substitute a different post.

## Article image handling

For X posts and Articles, treat diagrams, screenshots, charts, infographics, and other content images as part of the source rather than optional decoration:

1. Inspect the retrieved media fields and Article entity/block references, choose the highest-quality public image variant available, and preserve the order in which the images occur in the Article. Do not download avatars, tracking pixels, or unrelated thumbnails unless they carry source meaning.
2. Save each image under `_wiki/raw/assets/<raw-stem>/` with a stable ordinal filename, insert `![[_wiki/raw/assets/<raw-stem>/NNN-figure.ext|original alt/caption]]` at the corresponding block or nearest recoverable paragraph, and store the original URL, placement, local path, extraction status, media type, and byte SHA-256 in `_wiki/raw/assets/<raw-stem>/_provenance.json`. Keep the Markdown body limited to the image embed, source-provided alt/caption, and nearby explanation; never add inline HTML provenance comments or print the URL beside the image.
3. If the API exposes media but not an exact block anchor, record that placement is approximate in the sidecar, not beside the embed. If download or decoding fails, retain `[图片未成功归档：原因]` without the URL in the raw body, record the safe URL/failure details in the sidecar, mark the raw capture partial, and report the failed media privately in the ingest result. Never invent a caption or visual conclusion.
4. Validate that every local image decodes, every embed resolves, and every sidecar record matches the archived bytes before recomputing the raw body hash. Same URL/byte hash may be reused within one source, but different X sources must retain independent provenance unless reuse is explicit.

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

Before compiling an X source, verify the response has the expected post ID and author. For Articles, record the number of non-empty blocks, extracted characters, discovered content images, successfully archived images, and failed images privately during validation; do not dump the full response into logs. If the public mirror and Bird differ, distinguish formatting/normalization differences from missing content and preserve the retrieval method in the source record.

For public copyrighted Articles, preserve the URL, attribution, metadata, a source-faithful deep analysis and structured summary, and short verification excerpts by default. Store the full body only when the user explicitly requests it and retention is appropriate under the applicable policy; never create duplicate full-text copies merely because two retrieval methods were used.
