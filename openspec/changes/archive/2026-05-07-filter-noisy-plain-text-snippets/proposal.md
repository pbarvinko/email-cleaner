## Why

Some messages include malformed or generated `text/plain` parts that contain HTML/CSS styling markers instead of readable body text. Snippet generation currently prefers plain text whenever it exists, which can produce noisy snippets even when a cleaner HTML alternative is available. Separately, the classifier currently receives the same flattened snippet representation, which loses structure that would help it interpret HTML-heavy messages.

## What Changes

- Filter individual `text/plain` parts before snippet generation.
- Treat a plain-text part as noisy when it contains known styling markers such as `font-family`, `font-size`, `line-height`, `background-color`, `color:`, `mso-`, or `@media`.
- Prefer user-visible snippets built from remaining clean plain-text parts.
- Fall back to readable HTML-derived text for the user-visible snippet only when no clean plain-text parts remain.
- Convert selected HTML fallback content to Markdown only when preparing classifier input.

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `email-scan-review`: Refine snippet extraction so scan results prefer readable plain text and, when needed, fall back to readable text extracted from HTML when only noisy plain-text parts are available.
- `email-classification`: Prepare HTML fallback content as Markdown for classifier input while leaving the user-visible snippet as readable text.

## Impact

- `email_cleaner/normalize.py` snippet selection logic.
- Classifier input preparation and its tests.
- HTML-to-Markdown conversion dependency used for classifier input.
- Normalization tests covering multipart email body selection.
- User-visible scan result snippets.
