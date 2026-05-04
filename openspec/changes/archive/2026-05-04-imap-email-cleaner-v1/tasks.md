## 1. Project setup

- [x] 1.1 Create the Python application structure for Flask app, API routes, static assets, templates, IMAP integration, email normalization, and classifier modules
- [x] 1.2 Add runtime dependencies and basic project configuration for Flask, Anthropic client usage, `pydantic-settings`, and any email parsing helpers needed for v1
- [x] 1.3 Implement environment-based settings loading and startup validation for IMAP, Anthropic, and server configuration

## 2. Read-only scan backend

- [x] 2.1 Implement the Flask application factory or equivalent startup entrypoint that serves the UI at `/` and API routes under `/api/...`
- [x] 2.2 Implement `GET /api/health` and `POST /api/scan` with request validation and structured JSON responses
- [x] 2.3 Implement provider-agnostic IMAP connection and `INBOX` search using the supported search fields and configurable result limit
- [x] 2.4 Implement email fetch and normalization logic to extract metadata, selected headers, and bounded readable snippets from plain-text or HTML-heavy messages

## 3. Classification flow

- [x] 3.1 Define a minimal classifier interface and result model that returns only `keep`, `move`, or `uncertain` plus a short reason
- [x] 3.2 Implement the Anthropic Claude Haiku classifier adapter using one independent classification request per email
- [x] 3.3 Integrate classification into the scan flow, including graceful handling of ambiguous or failed classifications

## 4. Local review UI

- [x] 4.1 Build the root HTML page with search inputs for `from_email`, `from_name_contains`, `subject_contains`, `since_date`, and `limit`
- [x] 4.2 Implement browser-side JavaScript to submit scan requests to `/api/scan`, render results, and display metadata, snippets, labels, and reasons
- [x] 4.3 Implement client-side label override behavior that updates labels locally for the current run without persisting state or calling mailbox-write APIs
- [x] 4.4 Add basic CSS and UI copy that makes the read-only nature of `move` suggestions clear

## 5. Validation and developer experience

- [x] 5.1 Add targeted tests for config validation, scan request validation, and core normalization/classification response shaping
- [x] 5.2 Add a README or equivalent run instructions covering environment variables, local startup, and the v1 read-only limitations
- [ ] 5.3 Manually verify the end-to-end flow against a real IMAP inbox: start server, run a scan, inspect results, and confirm that no mailbox mutations occur
