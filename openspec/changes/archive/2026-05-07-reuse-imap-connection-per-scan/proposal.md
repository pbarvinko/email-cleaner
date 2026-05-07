## Why

The current scan flow opens one IMAP connection to search and then opens a fresh IMAP connection for each message fetch. Reusing one authenticated read-only connection for the whole scan removes unnecessary round trips and keeps the implementation aligned with the app's simple sequential scan workflow.

## What Changes

- Reuse a single IMAP connection across search and message fetches within one scan run.
- Keep mailbox access read-only while the shared connection is open.
- Preserve the current search criteria, fetch behavior, and scan result shape.
- Add tests covering multi-message scans without per-message reconnection.

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `email-scan-review`: Perform each read-only inbox scan over a single authenticated IMAP session instead of reconnecting for every fetched message.

## Impact

- `email_cleaner/imap_client.py` connection lifecycle.
- `email_cleaner/service.py` scan orchestration.
- IMAP-related tests and mocks.
