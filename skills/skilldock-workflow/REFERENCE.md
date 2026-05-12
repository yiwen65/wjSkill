# SkillDock Workflow — Reference

## Scenario A — fix a bug or add a feature (full)

```bash
# 0. main must be clean and up to date
git checkout main && git pull --ff-only

# 1. branch off
git checkout -b fix/login-race

# 2. make the change, then run every gate CI will run
npm run lint
npm run format:check
npm run typecheck
npm run build
npm run ui:smoke
cargo test --manifest-path src-tauri/Cargo.toml --locked
npm run e2e                       # only when you touched UI or an e2e spec

# 3. commit using Conventional Commits
git add <files>
git commit -m "fix(scope): one-line summary"

# 4. push and open the PR
git push -u origin fix/login-race
gh pr create --base main --head fix/login-race \
  --title "fix(scope): ..." \
  --body "Problem · change · local test results"

# 5. watch CI; all four checks must be green
gh pr checks <PR#>

# 6. merge with rebase, delete the remote branch
gh pr merge <PR#> --rebase --delete-branch

# 7. sync local main
git checkout main && git pull --ff-only
```

Tips:

- Running local gates **before** pushing avoids round-tripping through GitHub's ~3-minute CI cycle. The only gate that needs CI is Rust-on-macOS, which you generally can't reproduce locally on Linux.
- If `npm run format:check` fails, fix with `npm run format`. Same for `npm run lint` → `npm run lint:fix`.
- Playwright depends on Quality. If Quality fails, Playwright is skipped automatically.

## Scenario B — cut a release (full)

Preconditions: the code on `main` is the state you want to publish, and all planned PRs are merged.

```bash
# 1. Bump the version in three files — always via a dedicated PR
#
#    - package.json                 "version": "0.2.0"
#    - src-tauri/tauri.conf.json    "version": "0.2.0"
#    - src-tauri/Cargo.toml         version = "0.2.0"
#
#    Commit message: `chore(release): bump to v0.2.0`

# 2. After the bump PR merges, sync main
git checkout main && git pull --ff-only

# 3. Create an annotated tag — the tag message doubles as release notes
git tag -a v0.2.0 -m "v0.2.0 — one-liner + highlights"

# 4. Push the tag; this alone fires the release workflow
git push origin v0.2.0

# 5. Watch progress (about 6–7 minutes end-to-end)
gh run list --workflow=release.yml --limit 1
gh run watch <run-id>

# 6. Verify the published release
gh release view v0.2.0 --json assets --jq '.assets[].name'
```

What the release workflow does automatically:

1. Creates (or finds) a draft release for the tag
2. Builds in parallel on three runners:
   - `macos-latest` → universal `.dmg`, `.app.tar.gz`, `.zip`
   - `ubuntu-22.04` → x86_64 `.deb`, `.rpm`, `.AppImage`
   - `ubuntu-22.04-arm` → aarch64 `.deb`, `.rpm`, `.AppImage`
3. Flips the draft to published once every build succeeds

Nine assets total. Windows is intentionally excluded.

## Scenario C — re-cut a release under the same version

Use this only when the code has a fix but the version number doesn't need to move (for example, a CI or packaging bug that broke the previous attempt). Released versions that have actually shipped should **not** be re-cut this way — bump the patch instead.

```bash
# 1. Delete the broken release and its tag (remote + local)
gh release delete v0.2.0 --cleanup-tag --yes
git tag -d v0.2.0

# 2. Land the fix via Scenario A

# 3. Re-tag on the fixed main
git checkout main && git pull --ff-only
git tag -a v0.2.0 -m "..."
git push origin v0.2.0
```

## Dependabot

Weekly PRs land on Monday 09:00 Asia/Shanghai for npm, Cargo, and GitHub Actions (three ecosystems, five-PR cap each, minor + patch grouped, majors individual). They go through the same CI gates as any human PR.

Merge strategy:

- **Minor and patch updates**: merge once CI is green.
- **Major updates**: skim the changelog for breaking changes, run `npm run e2e` locally if the bump touches React/Vite/Playwright, then merge if clean.
- If a major bump needs related refactoring (for example, upgrading React to v19 pulls in new lint rules), close the PR with a comment pointing at a tracking issue and do the combined work as a dedicated PR.

## Branch protection on `main`

- Requires linear history
- Disallows force-push and delete
- Blocks merges until all four checks pass
- Admin bypass is available for emergencies but should not be the default
