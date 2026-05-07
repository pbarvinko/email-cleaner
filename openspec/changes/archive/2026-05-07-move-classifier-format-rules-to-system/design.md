## Context

The current classifier request sends one user message whose content is a JSON blob containing `task`, `labels`, `rules`, and `email`. Although the `rules` list clearly says to return one raw JSON object with no fences or prose, the model can still treat those rules as application data rather than as the strongest formatting instruction. A dedicated system prompt is a smaller and more direct way to emphasize output constraints without changing classification semantics.

## Goals / Non-Goals

**Goals:**
- Put output-format constraints in the strongest prompt position available in the current API usage.
- Keep label semantics and email payload content unchanged.
- Limit the change to prompt structure and tests.

**Non-Goals:**
- Add tolerant parsing for fenced or malformed output.
- Change allowed labels, classification policy, or model settings.
- Introduce tool-calling or a different response API mode.

## Decisions

### 1. Move formatting rules to the system message
- **Decision:** Send the raw-JSON contract and example in a dedicated `system` instruction.
- **Why:** System instructions typically carry stronger behavioral weight than metadata embedded inside a JSON user payload.
- **Alternative considered:** Keep only the user-message `rules` block. Rejected because that structure has already proven unreliable.

### 2. Keep the user message focused on task plus email payload
- **Decision:** Leave the user message responsible for the classification request and email data.
- **Why:** This keeps the output contract separated from the content to be classified.
- **Alternative considered:** Move all instructions into one plain-text user prompt. Rejected because it weakens separation between stable contract and per-email content.

### 3. Preserve the existing JSON contract text
- **Decision:** Reuse the current raw-JSON requirements and example, but place them in the system prompt.
- **Why:** The wording is already explicit; placement is the main issue.
- **Alternative considered:** Rewrite the contract substantially. Rejected as unnecessary scope for this change.

## Risks / Trade-offs

- **[The model may still occasionally ignore even system instructions]** → Accept for now; parser hardening remains the next fallback if needed.
- **[Prompt construction becomes slightly more split across fields]** → Acceptable because the separation maps cleanly to format rules versus email content.

## Migration Plan

Update classifier prompt construction and tests together so the system/user split is verified in one change.

## Open Questions

- None.
