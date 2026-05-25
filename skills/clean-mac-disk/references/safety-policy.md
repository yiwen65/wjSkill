# Safety Policy

## Protected Paths And Data

Never delete or modify these without an explicit, specific user override:

- `/System`, `/Library`, `/usr`, `/bin`, `/sbin`, `/private`, `/var`, `/etc`, `/opt` except tool-owned cache cleanup commands.
- `~/Documents`, `~/Desktop`, `~/Pictures`, `~/Movies`, `~/Music`, `~/Downloads` personal files.
- Photos Library, Mail, Messages, Notes, Contacts, Calendar, Safari profiles, browser passwords, Keychains, iCloud Drive, CloudStorage.
- `~/.ssh`, `~/.gnupg`, `~/.aws`, credentials, certificates, environment files, database files, app configuration, source files, Git history.
- Unknown files or directories whose purpose is not clear.

## Usually Low Risk

Still require user confirmation before deletion:

- `~/Library/Developer/Xcode/DerivedData`
- Clearly identified project build outputs: `.build`, `target`, `.next`, `dist`, `build`, `.turbo`
- Package-manager caches: npm, pnpm, yarn, pip, Cargo registry cache, Gradle cache, Maven cache, Go module cache
- Homebrew cleanup via `brew cleanup`
- Browser cache directories under `~/Library/Caches/...` when the path is specifically cache-only
- Logs and temporary files that are not app databases or profiles

## Medium Risk

Explain side effects and ask separately:

- Xcode `iOS DeviceSupport`
- Simulator devices or runtime data
- Docker unused images, containers, build cache, and especially volumes
- `node_modules` and Python virtual environments because they require reinstalling dependencies
- AI model caches or deployment volumes because downloads may be expensive or data may be nontrivial

## Do Not Treat As Safe By Name Alone

Be careful with:

- `.cache` inside unknown projects
- `Application Support`, `Group Containers`, `Containers`
- Browser profile directories outside `~/Library/Caches`
- Anything named `data`, `db`, `storage`, `volume`, `uploads`, `media`, `backup`, or `archive`

## Command Rules

- Prefer dry-runs first: `brew cleanup -n`, `docker system df -v`, and `du -sh`.
- Use exact quoted paths in destructive commands.
- Do not use broad globs such as `rm -rf ~/Library/Caches/*`.
- Do not use `sudo` unless the user approves the exact reason and command.
- After deletion, verify with read-only size checks.
