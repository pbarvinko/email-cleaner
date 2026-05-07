## Context

`ClassificationResult.reason` is capped at 280 characters. The classifier now uses a dedicated `system` prompt plus provider JSON-schema output configuration, so fenced-JSON normalization is no longer part of the current path and should stay removed. Even with structured output, a long reason from the model or a long exception string in `safe_classify` can still cause validation to fail, which loses an otherwise usable label or even breaks the fallback path itself. The desired behavior is to preserve the current classifier request structure and simply shorten overlong reasons to fit the existing contract.

## Goals / Non-Goals

**Goals:**
- Preserve valid labels when only the reason length is problematic.
- Keep all emitted `reason` values within the 280-character contract.
- Use one consistent truncation rule for both normal and fallback paths.
- Preserve the current structured-output classifier request behavior.

**Non-Goals:**
- Change the 280-character limit.
- Reword or summarize reasons semantically.
- Alter handling of unsupported labels.
- Reintroduce Markdown-fence normalization or otherwise change the current request/response format handling.

## Decisions

### 1. Truncate instead of rejecting long reasons
- **Decision:** If a `reason` exceeds the allowed length, truncate it rather than failing the classification result.
- **Why:** The label is still useful, and a shortened explanation is better than dropping the result.
- **Alternative considered:** Reject the full result when `reason` is too long. Rejected because it discards useful classifier output over a formatting issue.

### 2. Use one-character ellipsis truncation
- **Decision:** Truncate to 279 characters and append `…` when shortening is needed.
- **Why:** This preserves the limit while making truncation visible.
- **Alternative considered:** Hard cut at 280 with no marker. Rejected because it hides that text was shortened.

### 3. Apply the same rule to fallback reasons
- **Decision:** Exception-derived fallback reasons use the same truncation helper.
- **Why:** This prevents the fallback path from failing on long exception messages.
- **Alternative considered:** Special-case only model output. Rejected because the observed failure also occurs in fallback construction.

### 4. Preserve the current structured-output path
- **Decision:** Keep the user's current `system` prompt handling and provider JSON-schema output configuration unchanged while adding reason truncation.
- **Why:** The requested fix is about overlong reasons, not output-format handling, and the user explicitly wants the recent classifier changes preserved.
- **Alternative considered:** Reintroduce response normalization helpers. Rejected because the current code no longer needs them and that would broaden scope unnecessarily.

## Risks / Trade-offs

- **[Truncated reasons may lose some detail]** → Acceptable because preserving a valid result is more important than retaining every character.
- **[Mid-word truncation can look abrupt]** → Acceptable for this small fix; semantic shortening is out of scope.

## Migration Plan

Add a shared reason-truncation step in classification result shaping and cover both direct and fallback paths with tests, without changing the current structured-output request path.

## Open Questions

- None.
