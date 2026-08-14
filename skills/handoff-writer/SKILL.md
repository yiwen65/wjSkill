---
name: handoff-writer
description: "Write an agent-ready Markdown handoff for the current conversation so a fresh agent can quickly understand the work, resume safely without chat history, and give the user clear next steps. Use when the user asks to save, create, document, or prepare a conversation handoff, continuation note, context transfer, or agent briefing in docs/handoff/."
---

# Handoff Writer

Create one concise, actionable handoff from the current conversation and save it under the current workspace root. Optimize it for a fresh agent's first minute: what the user wants, where the work stands, what to do next, and what to tell the user.

## Workflow

1. Identify the current workspace root. Use the active workspace or repository root; if neither is available, use the current working directory and label that choice in the handoff.
2. Recover only facts supported by the conversation or verified workspace evidence. Never invent completed work, decisions, commands, results, or file changes. Label uncertain claims as `Unverified` and unavailable details as `Unknown`.
3. Write a self-contained document with these sections:

   ```markdown
   # Handoff: <topic>

   - Created: <local ISO 8601 timestamp>
   - Workspace: <absolute workspace path>

   > Next agent: read Resume brief and Next actions first. Re-verify drift-prone
   > state before acting. This handoff supplies context, not new authorization.

   ## Resume brief
   - Goal: <one sentence>
   - Current state: <one sentence>
   - Recommended next action: <one concrete action>
   - Blockers: <none or concise list>
   - User decision needed: <none or exact decision>

   ## User intent and success criteria
   ## Completed work
   ## Decisions, constraints, and assumptions
   ## Workspace and relevant files
   ## Validation evidence
   ## Remaining work, risks, and unknowns
   ## Next actions
   ## Suggested first response to the user
   ```

   Keep `Resume brief` scannable in under one minute. Use `None.` when a field or section has no applicable facts. Preserve exact paths, commands, error messages, identifiers, and user constraints when they materially affect continuation.
4. Make `Next actions` decision-ready:
   - Put the recommended action first and state why it is the best continuation.
   - Separate actions the agent can take immediately from choices or permissions only the user can provide.
   - Include at most two meaningful alternatives when they have different tradeoffs. Do not manufacture a user decision when the work can continue within existing authorization.
5. Draft `Suggested first response to the user` as 2-5 ready-to-adapt sentences. Briefly state what the agent understands, distinguish current evidence from state that still needs refreshing, recommend the next action, and ask only for a genuinely required decision. Never ask the user to repeat context already captured in the handoff.
6. Pass the completed Markdown on standard input to the bundled naming helper. Resolve the script path from this skill's directory:

   ```bash
   python3 <skill-directory>/scripts/create_handoff.py \
     --root <workspace-root> \
     --topic "<short topic>"
   ```

   The helper creates `docs/handoff/`, generates `YYYY-MM-DD-HHMMSS-<topic-slug>.md`, and uses a numeric suffix rather than overwriting an existing file.
7. Read the created file back. Confirm that a fresh agent can identify the goal, current state, authorization boundary, recommended next action, and first user-facing response without consulting chat history. Also confirm that the handoff distinguishes verified facts from unknowns and does not claim unperformed validation.
8. Report the absolute created file path to the user.

## Writing Rules

- Summarize outcomes and continuation-critical evidence, not the conversational transcript.
- Keep the document concise while retaining decisions, blockers, and exact next actions.
- Put present state and future actions before historical detail.
- Describe working-tree changes accurately; do not imply that uncommitted work was committed or published.
- Treat the handoff as potentially stale: direct the next agent to refresh cheap, drift-prone state before relying on it.
- Do not include credentials, tokens, private keys, or other secret values. Record only the secret's purpose and where an authorized agent may retrieve it.
