## Why

The classifier still sometimes wraps JSON in Markdown fences even after the output contract was tightened. The current prompt packs formatting rules inside a JSON payload in a user message, which weakens those rules compared with a dedicated system instruction.

## What Changes

- Move the classifier output-format contract into a dedicated system prompt.
- Keep the email payload and classification task in the user message.
- Preserve the existing allowed labels and required `label`/`reason` JSON shape.
- Update tests to verify the system prompt contains the strict raw-JSON instructions and example.

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `email-classification`: Deliver the classifier's raw-JSON output contract through a dedicated system instruction instead of embedding those rules only inside the user payload.

## Impact

- `email_cleaner/classifier.py` prompt construction.
- Classifier tests asserting system/user message separation.
- Model compliance with JSON-only output requirements.
