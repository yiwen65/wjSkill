# X Source Ingestion

Use this reference for public `x.com` or `twitter.com` URLs. The original X URL remains the canonical provenance; an API or CLI is only the retrieval method.

## Choose a retrieval path

1. For a public, read-only URL, try the no-credential public endpoint first when it is available:

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

## Completeness and provenance checks

Before compiling an X source, verify the response has the expected post ID and author. For Articles, record the number of non-empty blocks and extracted characters privately during validation; do not dump the full response into logs. If the public mirror and Bird differ, distinguish formatting/normalization differences from missing content and preserve the retrieval method in the source record.

For public copyrighted Articles, preserve the URL, attribution, metadata, paraphrased summary, and short verification excerpts by default. Store the full body only when the user explicitly requests it and retention is appropriate under the applicable policy; never create duplicate full-text copies merely because two retrieval methods were used.
