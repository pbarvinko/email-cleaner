## Why

Users often receive a mix of transactional and promotional emails from the same sender, which makes manual inbox cleanup slow and error-prone. A local read-only assistant can reduce that effort now by letting users review likely promotional messages without risking accidental mailbox changes.

## What Changes

- Add a local web application built with Python 3.11 and Flask.
- Add a read-only IMAP inbox scan flow that searches only `INBOX` using simple user-facing search fields.
- Add per-email LLM classification into `keep`, `move`, or `uncertain` with a short explanation.
- Add a browser-based review UI that lets the user adjust labels for the current run.
- Add a minimal classifier seam with Anthropic Claude Haiku as the only v1 implementation.
- Exclude persistence, background jobs, and any mailbox mutation from v1.

## Capabilities

### New Capabilities
- `email-scan-review`: Search `INBOX`, fetch matching emails, classify each one independently, and present read-only review results in the local UI.
- `email-classification`: Normalize email content and classify each message as `keep`, `move`, or `uncertain` using an Anthropic-backed classifier seam.
- `local-web-ui`: Serve a local browser UI at `/` and JSON API endpoints under `/api/...` for running scans and showing results.

### Modified Capabilities
- None.

## Impact

- New Flask server, IMAP integration, classification layer, and static web UI.
- New Anthropic dependency and environment-based configuration validated by `pydantic-settings`.
- New local API contract for scan requests and results.
