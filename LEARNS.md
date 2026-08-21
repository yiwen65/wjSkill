# Project Learnings

## `skills/*` packaging — validate supported metadata before finalizing a Skill

- Wrong approach: Preserved unsupported `version` and `language` frontmatter fields and initially used a 22-character UI `short_description`.
- Why it failed: The official Skill validator accepts only its documented frontmatter keys, while `agents/openai.yaml` requires a 25–64 character short description.
- Recognition signal: `quick_validate.py` reports `Unexpected key(s) in SKILL.md frontmatter`, or a metadata length assertion falls outside 25–64 characters.
- Correct approach: Keep only supported frontmatter fields, preserve supported `agents/openai.yaml` policy fields, and size UI metadata to its documented bounds.
- Prevention: Run `python3 /Users/w/.codex/skills/.system/skill-creator/scripts/quick_validate.py <skill-dir>` and check UI string lengths immediately after metadata edits.
- Verified by: `skills/understand-repo` passed official validation after removing the unsupported fields and expanding `short_description` to 29 characters.
