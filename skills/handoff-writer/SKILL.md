---
name: handoff-writer
description: "Summarize the key aspects of the current session in a self-contained Markdown handoff so a fresh agent can understand the user's goal, outcomes, decisions, evidence, files, unresolved work, and recommended continuation without chat history. Use when the user asks to save, create, document, or prepare a session summary, conversation handoff, continuation note, context transfer, or agent briefing in docs/handoff/."
---

# Handoff Writer

Create one concise handoff that preserves the session's decision-relevant state and save it under the current workspace root. The primary deliverable is an accurate summary of the session; continuation guidance is secondary.

## Workflow

1. Identify the current workspace root. Use the active workspace or repository root; if neither is available, use the current working directory and label that choice in the handoff.
2. Recover only facts supported by the conversation or verified workspace evidence. Select what a new agent must know about the user's intent, work performed, outcomes, decisions, evidence, artifacts, and unfinished work. Never invent completed work, decisions, commands, results, or file changes. Label uncertain claims as `Unverified` and unavailable details as `Unknown`.
3. Write a self-contained document with these sections:

   ```markdown
   # Session Handoff: <topic>

   - Created: <local ISO 8601 timestamp>
   - Workspace: <absolute workspace path>

   > Next agent: start with Session summary. Re-verify drift-prone state before
   > acting. This handoff supplies context, not new authorization.

   ## Session summary
   ## User intent and success criteria
   ## Work completed and outcomes
   ## Key decisions, constraints, and rationale
   ## Files and artifacts
   ## Commands, validation, and evidence
   ## Unresolved items, risks, and unknowns
   ## Recommended continuation
   ```

   Make `Session summary` the most valuable section. In 5-10 concise bullets or short paragraphs, capture the session's goal, current outcome, most important work, key decisions or constraints, material evidence, and unresolved state. It must stand alone without the later detail sections.
4. Use the remaining sections to preserve supporting detail without repeating the transcript:
   - Record outcomes, not merely actions taken.
   - Include the rationale for decisions when it changes how later work should proceed.
   - Preserve exact paths, commands, error messages, identifiers, and user constraints only when they materially affect continuation.
   - Use `None.` when a section has no applicable facts.
5. Keep `Recommended continuation` short and ordered. Put the best next action first, separate work the agent may continue from decisions only the user can authorize, and state when no user input is needed. Do not turn the handoff into a drafted user reply unless the user requests one.
6. Pass the completed Markdown on standard input to the bundled naming helper. Resolve the script path from this skill's directory:

   ```bash
   python3 <skill-directory>/scripts/create_handoff.py \
     --root <workspace-root> \
     --topic "<short topic>"
   ```

   The helper creates `docs/handoff/`, generates `YYYY-MM-DD-HHMMSS-<topic-slug>.md`, and uses a numeric suffix rather than overwriting an existing file.
7. Read the created file back. Confirm that `Session summary` accurately covers the key aspects of the session, the detailed sections support it without unnecessary repetition, evidence is separated from unknowns, and no unperformed validation is claimed. Confirm that a fresh agent can understand the session before reading `Recommended continuation`.
8. Report the absolute created file path to the user.

## Writing Rules

- Synthesize the session; do not reproduce the conversational transcript or routine tool narration.
- Prioritize user intent, outcomes, decisions, evidence, artifacts, and unresolved work.
- Keep historical detail only when it explains the current state or a decision.
- Avoid repeating the same fact across sections unless the summary needs it for clarity.
- Describe working-tree changes accurately; do not imply that uncommitted work was committed or published.
- Treat the handoff as potentially stale: direct the next agent to refresh cheap, drift-prone state before relying on it.
- Do not include credentials, tokens, private keys, or other secret values. Record only the secret's purpose and where an authorized agent may retrieve it.
