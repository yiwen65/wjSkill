---
name: release-trigger
description: >
  Bump version numbers, create a git tag, and push it to trigger a GitHub
  release workflow. Use this skill whenever the user wants to:
  - "release", "cut a release", "publish a version", "bump version", "tag a release"
  - push a semver tag to trigger CI/CD
  - update version files (package.json, Cargo.toml, pyproject.toml, etc.)
  - create a draft or full release on GitHub
  Also trigger when the user mentions version bumping, tagging, or release
  automation even if they don't explicitly say "release".
---

# Release Trigger

Automate the full release pipeline: detect version files, bump versions, commit,
create a semver tag, and push it to trigger the GitHub release workflow.

## Workflow

### 1. Detect project type and version files

Scan the project root for version-bearing files. Check these in order:

| File | What to update | Pattern |
|------|----------------|---------|
| `package.json` | `"version"` field | `"version": "X.Y.Z"` |
| `src-tauri/Cargo.toml` | `version` under `[package]` | `version = "X.Y.Z"` |
| `Cargo.toml` (root) | `version` under `[package]` | `version = "X.Y.Z"` |
| `Cargo.lock` | `version` for the root package | multiple entries |
| `pyproject.toml` | `version` under `[project]` or `project.version` | `version = "X.Y.Z"` |
| `setup.py` | `version=` argument | `version="X.Y.Z"` |

Read ALL detected files to extract current versions. If versions differ across
files, warn the user and ask which to use as the source of truth.

### 2. Inspect the release workflow

Read `.github/workflows/release.yml` (or any `*.yml` with "release" in the name).
Note:
- What triggers the workflow (`push.tags`, `workflow_dispatch`, etc.)
- What tag format it expects (e.g. `v*`, `v*.*.*`)
- Whether it requires the tag to already exist for manual dispatch

If no release workflow is found, warn the user and ask if they want to proceed
with just a tag push.

### 3. Determine the new version

If the user provided a version (e.g. "1.2.3" or "v1.2.3"), use it (strip the `v`
prefix for file updates, keep it for the git tag).

If not provided, suggest the next version based on the current version:
- Patch: 0.5.0 -> 0.5.1 (for bugfixes)
- Minor: 0.5.0 -> 0.6.0 (for features)
- Major: 0.5.0 -> 1.0.0 (for breaking changes)

Ask the user which to use, or let them type a custom version.

### 4. Update version files

For each detected version file, update the version string to the new version.
Use precise edits. Update `Cargo.lock` only if `Cargo.toml` was updated and the
project is a Rust workspace (the lockfile is needed for reproducible builds).

### 5. Commit and tag

Create a conventional commit for the version bump:

```
chore(release): bump version to X.Y.Z

Co-Authored-By: Claude <noreply@anthropic.com>
```

Then create an annotated tag (or lightweight tag if the repo convention is
lightweight) with the format the workflow expects, typically `vX.Y.Z`.

If a tag with that name already exists locally or remotely, ask the user whether
to overwrite (delete and recreate) or abort.

### 6. Push to trigger release

Push both the commit and the tag:

```bash
git push origin <branch> <tag>
```

This should trigger the GitHub Actions release workflow. Confirm with the user
that the workflow is running (they can check the Actions tab).

## Edge cases

- **Dirty working tree**: If there are uncommitted changes, either stash them or
  include them in the version-bump commit if they are part of the release.
- **Tag already exists**: Ask before force-overwriting.
- **No remote**: Warn and stop; the user needs to set up a remote.
- **Branch protection**: If push fails due to status checks, report the error and
  suggest opening a PR instead.
- **Multiple version files with different versions**: Ask user which is canonical.
- **Monorepo**: If the user is in a subdirectory of a monorepo, detect the root
  by looking for `.git` and the version files, then operate from the root.

## Example interaction

**User**: "cut a release"
**Claude**: "Current version is 0.5.0 (from package.json and src-tauri/Cargo.toml).
The release workflow is triggered by pushing tags matching `v*`. Suggest:
- patch: 0.5.1
- minor: 0.6.0
- major: 1.0.0
What version?"

**User**: "0.6.0"
**Claude**: [updates files, commits, tags v0.6.0, pushes] "Done. Tag v0.6.0
pushed. The release workflow should be running now."

**User**: "release 1.2.3"
**Claude**: [directly uses 1.2.3, no questions asked]
