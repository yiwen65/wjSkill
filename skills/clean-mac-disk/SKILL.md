---
name: clean-mac-disk
description: Safely analyze and clean macOS disk space with a dry-run-first workflow, explicit confirmation gates, and optional interactive HTML cleanup checklists. Use when the user asks to free Mac disk space, inspect large folders, clean caches, remove build artifacts, generate deletion commands, or clean Xcode, Simulator, Homebrew, npm, pnpm, yarn, pip, Gradle, Maven, Cargo, Go, Docker, browser, or project-derived data without touching personal/system data.
---

# Clean Mac Disk

Act as a cautious macOS disk cleanup assistant. Prioritize safety over reclaiming space. Never delete anything during analysis, never use `sudo` unless the user explicitly approves it, and never modify personal data, account data, keys, system directories, or project source.

## Core Workflow

1. **Analyze first**
   - Start with read-only commands: `df`, `du`, `find`, `tmutil`, package-manager dry-runs, and Docker size queries.
   - Do not bypass macOS privacy-denied directories unless the user explicitly asks and approves why.
   - Prefer `du -xhd 1` for same-volume summaries and narrowly scoped `du -xsh` for known candidates.

2. **Classify candidates**
   - Read [references/safety-policy.md](references/safety-policy.md) before proposing deletion.
   - Separate candidates into low-risk, confirmation-required, and do-not-touch groups.
   - Treat unknown directories, personal folders, iCloud, browser profile data, Mail, Messages, Keychains, Photos, credentials, databases, and source trees as protected.

3. **Report before deleting**
   - Use the user's language.
   - Include: current disk summary, major space sources, candidate table, commands requiring confirmation, estimated reclaimable space, and items not recommended.
   - Explain each candidate's path, type/source, size, risk, expected side effect, and whether it is recommended.

4. **Generate an interactive checklist when useful**
   - When the user asks for a selectable cleanup UI, use `scripts/generate_cleanup_checklist.py`.
   - Build a JSON candidate file from the analysis results, then generate a self-contained HTML file.
   - The HTML must only preview/copy commands. It must not execute deletion.

5. **Delete only after explicit confirmation**
   - Require the user to explicitly approve the exact set or category to delete.
   - Use concrete, quoted paths only. Avoid broad globs and broad `rm -rf`.
   - Prefer tool-native cleanup commands where safer, such as `brew cleanup --prune=all --scrub`, `npm cache clean --force`, and `python3 -m pip cache purge`.
   - After cleanup, rerun a small read-only verification (`df -h`, selected `du -sh`) and summarize actual results.

## Read-Only Inventory Commands

Use a subset appropriate to the machine and the user's request:

```zsh
df -h / /System/Volumes/Data
tmutil listlocalsnapshots /
du -xhd 1 "$HOME"
du -xhd 1 "$HOME/Library"
du -xhd 1 "$HOME/Library/Caches"
du -xhd 1 "$HOME/Library/Developer"
du -xhd 2 "$HOME/Library/Developer/Xcode"
du -xhd 2 "$HOME/Library/Developer/CoreSimulator"
brew cleanup -n
brew cleanup -n --prune=all --scrub
docker system df -v
```

For project build products, search only likely project roots and prune `.git`:

```zsh
find "$HOME/Projects" "$HOME/AI" "$HOME/AD" -path '*/.git' -prune -o -type d \
  \( -name node_modules -o -name .next -o -name dist -o -name build -o -name target -o -name .turbo -o -name .cache -o -name .build \) \
  -prune -print
```

## Interactive HTML Checklist

Create a JSON file with this shape:

```json
{
  "title": "macOS 安全清理勾选列表",
  "disk": {
    "available": "686Gi 可用",
    "summary": "数据卷已用约 218Gi，总量 926Gi。推荐先清可再生成内容。"
  },
  "items": [
    {
      "path": "/Users/w/Projects/App/.build",
      "type": "Swift/Xcode 构建产物。可再生成。",
      "sizeText": "12G",
      "sizeGiB": 12,
      "risk": "low",
      "riskText": "低",
      "recommended": true,
      "command": "rm -rf \"/Users/w/Projects/App/.build\""
    }
  ]
}
```

Then run:

```zsh
python3 /path/to/clean-mac-disk/scripts/generate_cleanup_checklist.py \
  --input /path/to/candidates.json \
  --output "$HOME/disk-cleanup-checklist.html"
```

Use `--sample` to create a demo page for smoke testing.

## HTML UI Requirements

Follow [references/html-checklist.md](references/html-checklist.md). Preserve these safety properties:

- Generate commands with real newline separators, not literal `\n`.
- Append a final read-only report block that writes `~/disk-cleanup-report-YYYYmmdd-HHMMSS.txt` after cleanup commands finish.
- Require an "execution confirmed" checkbox before copying commands.
- Show obvious copy feedback in a fixed top-right toast and temporarily change the copy button state.
- Include summary cards for total items, selected items, and estimated reclaimable space.
- Include risk filters, recommendation selection, clear selection, command preview, and protected-items notes.

## Handling Blockers

- If `du`, `find`, `ps`, Docker, Simulator, or package-manager commands fail due to permissions or unavailable services, report the limitation and continue with narrower read-only checks.
- If a candidate's purpose is unclear, list it as "not recommended" or "needs confirmation"; do not infer safety from size alone.
- If the user asks to delete a prohibited area, explain the risk and offer safer alternatives.
