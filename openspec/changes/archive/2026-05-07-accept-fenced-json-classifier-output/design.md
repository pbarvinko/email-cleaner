## Context

Prompt-side tightening was the right first step, but real responses still sometimes come back as text blocks wrapped in Markdown code fences such as ```json ... ```. The API does not treat these as structured JSON; they are plain text. The smallest reliable fix is to normalize the most common wrapper forms before `json.loads` while still rejecting genuinely invalid outputs.

## Goals / Non-Goals

**Goals:**
- Accept raw JSON and the two common fenced wrapper forms.
- Keep the parsing rule explicit and narrow.
- Preserve existing failure handling for malformed responses outside those wrappers.

**Non-Goals:**
- Parse arbitrary prose surrounding JSON.
- Implement broad heuristic extraction of embedded JSON.
- Change prompt structure, label semantics, or classifier fallback behavior.

## Decisions

### 1. Strip only one outer code-fence wrapper
- **Decision:** Normalize response text by removing one matching outer fenced-code wrapper if the entire response is wrapped.
- **Why:** This directly addresses the observed failure mode without broadening parsing too far.
- **Alternative considered:** Search for any JSON-looking substring inside arbitrary text. Rejected because it is more error-prone and harder to reason about.

### 2. Accept both fenced forms with and without `json` language hint
- **Decision:** Support both ```json ... ``` and ``` ... ``` wrappers.
- **Why:** Both are common Markdown formats and equally harmless to normalize.
- **Alternative considered:** Support only ```json. Rejected because bare fences are also common and easy to handle.

### 3. Keep invalid-response handling unchanged after normalization
- **Decision:** If parsing still fails after normalization, let the existing error path produce `uncertain` via `safe_classify`.
- **Why:** This keeps the hardening local and preserves current failure semantics.
- **Alternative considered:** Add a second parsing fallback. Rejected as unnecessary scope for this targeted fix.

## Risks / Trade-offs

- **[A response with prose outside the fence still fails]** → Intentional; this change is limited to the observed wrapper forms.
- **[Very unusual fenced formatting may not match]** → Acceptable for now because the target forms are the common model outputs already observed.

## Migration Plan

Add response normalization in classifier parsing and cover the accepted forms with tests.

## Open Questions

- None.
