## Why

Classification reasons are constrained to 280 characters, but both model-returned reasons and exception-derived fallback reasons can exceed that limit. When that happens, result validation fails even if the classification label itself is otherwise usable.

## What Changes

- Preserve classifier labels whenever they are valid, even if the accompanying reason is too long.
- Truncate overlong reasons to the model limit using an ellipsis so the result remains valid.
- Apply the same truncation rule to exception-derived fallback reasons.
- Add tests covering long model reasons and long exception messages.

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `email-classification`: Ensure classification results remain valid by truncating overlong `reason` values instead of failing validation when the label is otherwise usable.

## Impact

- `email_cleaner/classifier.py` result shaping and fallback behavior.
- Classifier tests for long reasons.
- Fewer dropped classifications caused only by oversized reason text.
- Preserve the current structured-output classifier request shape (`system` prompt plus JSON schema output config).
