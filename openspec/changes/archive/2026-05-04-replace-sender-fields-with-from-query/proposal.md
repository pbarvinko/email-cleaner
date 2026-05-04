## Why

The current scan API splits sender search into `from_email` and `from_name_contains`, but this does not match how IMAP `FROM` search actually works and adds unnecessary local filtering complexity. Replacing both fields with a single generic sender query makes the UI and backend simpler and aligns behavior directly with provider-agnostic IMAP search semantics.

## What Changes

- Replace `from_email` and `from_name_contains` with a single sender search field.
- Use that field directly as the IMAP `FROM` query term.
- Remove local sender-name post-filtering from the IMAP client.
- Update the UI, validation model, tests, and docs to reflect the new sender-query contract.

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `email-scan-review`: Replace the two sender-specific search fields with one generic sender query field mapped directly to IMAP `FROM` search.

## Impact

- Scan request schema and validation.
- UI labels and payload shape.
- IMAP search implementation and related tests/documentation.
