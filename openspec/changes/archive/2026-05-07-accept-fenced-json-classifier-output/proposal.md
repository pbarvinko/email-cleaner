## Why

The classifier still sometimes returns valid JSON wrapped in Markdown code fences even after prompt-contract tightening and moving format rules into the system prompt. Because the runtime currently passes the raw text directly to `json.loads`, these otherwise usable responses fail parsing and unnecessarily downgrade classifications to `uncertain`.

## What Changes

- Accept raw JSON responses and common Markdown-fenced JSON wrappers from the classifier.
- Strip one outer fenced-code wrapper before JSON parsing when present.
- Keep rejection behavior unchanged for responses that are still not valid JSON after normalization.
- Add tests covering raw JSON, ```json fenced JSON, and bare ``` fenced JSON responses.

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `email-classification`: Tolerate common Markdown-fenced classifier responses by normalizing them to raw JSON before parsing.

## Impact

- `email_cleaner/classifier.py` response parsing.
- Classifier tests for output normalization.
- Fewer false `uncertain` results caused by fenced JSON wrappers.
