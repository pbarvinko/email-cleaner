## Why

The current workflow exposes a binary analysis/apply toggle and renders sparse card-based results. Reviewers now need three explicit scan modes that reflect the actual pipeline stages (`search`, `classify`, `clean`) and a denser review surface that makes high-volume inbox triage easier.

## What Changes

- Replace `apply_changes` with `mode: "search" | "classify" | "clean"`, defaulting to `classify`.
- Keep `before_date` validation and IMAP `BEFORE` translation.
- Add explicit stage metadata and search-mode result semantics to the scan response.
- Make Anthropic configuration optional at startup while rejecting `classify`/`clean` requests when classifier configuration is missing.
- Keep mailbox access read-only for `search` and `classify`, and allow mutation only for explicit `clean` mode.
- Replace the UI result cards and local relabeling control with a compact expandable results table.

## Capabilities

### Modified Capabilities
- `email-scan-review`: Support explicit `search`, `classify`, and `clean` runs with stage-aware responses and classifier gating.
- `local-web-ui`: Allow users to select scan mode and review dense table-based results without local label overrides.

## Impact

- `email_cleaner/models.py`, `service.py`, `api.py`, `app.py`, `config.py`, and `classifier.py`
- `email_cleaner/web/index.html`, `app.js`, and `style.css`
- API, IMAP, service, and UI tests
- OpenSpec capability docs for email scan review and local web UI
