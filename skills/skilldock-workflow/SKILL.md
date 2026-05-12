---
name: skilldock-workflow
description: Enforce SkillDock project contribution workflow — branching, commits, local gates, PRs, releases, and CI failure recovery. Use when making code changes in SkillDock, preparing a PR, cutting a release, or troubleshooting CI failures.
---

# SkillDock Workflow

## Quick start — fix or feature

```bash
git checkout main && git pull --ff-only
git checkout -b fix/scope-description   # or feat/, chore/, refactor/
# ... make changes ...
```

**Before every commit, run the local gates:**

```bash
npm run lint && npm run format:check && npm run typecheck && npm run build && npm run ui:smoke
cargo test --manifest-path src-tauri/Cargo.toml --locked
npm run e2e   # only if you touched UI or an e2e spec
```

```bash
git commit -m "fix(scope): imperative summary under 70 chars"
git push -u origin fix/scope-description
gh pr create --base main --head fix/scope-description --title "fix(scope): ..."
```

## Commit conventions

| Branch prefix | Commit type | Use for |
|---|---|---|
| `fix/` | `fix:` | bug fixes |
| `feat/` | `feat:` | user-facing features |
| `chore/` | `chore:` | deps, version bumps, hygiene |
| `ci/` | `ci:` | GitHub Actions, branch protection |
| `test/` | `test:` | test-only changes |
| `docs/` | `docs:` | documentation |
| `refactor/` | `refactor:` | no-behaviour-change refactors |
| `perf/` | `perf:` | performance-only |

**Template:**

```
type(scope): short summary

Body: problem, approach, trade-offs. Wrap at ~72 columns.

Testing:
- npm run lint / format:check / typecheck / build / ui:smoke — pass
- cargo test --locked — pass
- npm run e2e (if UI touched) — pass

Closes #<issue>
```

## Release (annotated tag)

```bash
# 1. Bump version in THREE files via a PR:
#    package.json, src-tauri/tauri.conf.json, src-tauri/Cargo.toml
#    Commit: chore(release): bump to v0.2.0

# 2. After merge, tag and push
git checkout main && git pull --ff-only
git tag -a v0.2.0 -m "v0.2.0 — one-liner + highlights"
git push origin v0.2.0

# 3. Watch workflow
gh run list --workflow=release.yml --limit 1
```

## CI gates on main (all must pass)

| Check | Runner | Time |
|---|---|---|
| Quality (lint, types, build, audit) | ubuntu-latest | ~20s |
| Rust tests (ubuntu) | ubuntu-latest | ~25s |
| Rust tests (macos) | macos-latest | ~45s |
| Playwright (chromium) | ubuntu-latest | ~1m |

Merge with `gh pr merge <PR#> --rebase --delete-branch`. Never force-push to `main`.

## Fix common CI failures

| Failure | Fix |
|---|---|
| Lint / format | `npm run lint:fix && npm run format`, commit, push |
| Types / build | Read error; fix root cause. No `// @ts-ignore`. |
| Rust tests | Run `cargo test --manifest-path src-tauri/Cargo.toml --locked` locally |
| Playwright | UI drift. Reproduce with `npm run e2e`, update spec to match current UI |
| npm audit | Pinned to `--audit-level=high`. Upgrade offending dep |

Re-running a failed workflow without a code change is rarely the right answer.

## Full details

See [REFERENCE.md](REFERENCE.md) for re-cutting releases, Dependabot strategy, and extended troubleshooting.
