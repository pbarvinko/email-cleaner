## Context

This repository is effectively greenfield, so the v1 design can optimize for simplicity without migration constraints. The product goal is a local read-only review workflow for transactional versus promotional email triage from IMAP `INBOX`, with Flask serving both the HTML UI and JSON API.

## Goals / Non-Goals

**Goals:**
- Provide a local web UI at `/` and JSON API endpoints under `/api/...`.
- Connect to any IMAP-enabled mailbox using environment-based configuration.
- Let users run a manual search against `INBOX` using simple fields instead of raw IMAP syntax.
- Normalize matched emails into compact payloads and classify each email independently as `keep`, `move`, or `uncertain`.
- Keep all mailbox interaction read-only in v1.
- Leave a small seam so Anthropic can be replaced later without rewriting the scan flow.

**Non-Goals:**
- Moving or deleting emails.
- Persisting scan results or user label overrides.
- OAuth, background jobs, multi-user support, or cross-sender auto-discovery.
- A rules engine for final classification decisions.

## Decisions

### 1. Use Flask as a single local server for UI and API
- **Decision:** Serve HTML, CSS, and JavaScript from Flask at `/` and expose JSON endpoints under `/api/...`.
- **Why:** It is the smallest solution that cleanly separates browser UI from programmatic API without adding a frontend build system.
- **Alternative considered:** Separate frontend app. Rejected because it adds tooling and deployment complexity without helping v1.

### 2. Keep workflow deterministic and use the LLM only for per-email classification
- **Decision:** Application code handles search, fetch, parse, normalize, and response shaping. Anthropic Haiku handles only the judgment step.
- **Why:** This minimizes token usage, keeps behavior debuggable, and preserves a clear failure boundary.
- **Alternative considered:** LLM-directed orchestration or batched reasoning. Rejected because it adds complexity and makes failures harder to localize.

### 3. Use simple search fields in the UI and translate them to IMAP plus local filtering
- **Decision:** Support fields such as `from_email`, `from_name_contains`, `subject_contains`, `since_date`, and `limit`.
- **Why:** This is safer and easier to validate than exposing raw IMAP search syntax.
- **Alternative considered:** Free-form IMAP query input. Rejected because it would complicate validation and make UX provider-specific.

### 4. Read only from `INBOX` and cap results per run
- **Decision:** Search only `INBOX` and fetch up to a configurable limit, defaulting to 20.
- **Why:** This keeps latency, token cost, and UI volume manageable while matching the requested workflow.
- **Alternative considered:** Whole-mailbox or multi-folder search. Rejected as unnecessary for v1.

### 5. Normalize a bounded subset of each message before classification
- **Decision:** Send only compact metadata, selected headers, and a truncated text snippet to the classifier.
- **Why:** This reduces privacy exposure and token cost while retaining the signals most useful for triage.
- **Alternative considered:** Full raw message submission. Rejected as wasteful and harder to reason about.

### 6. Add a minimal classifier seam instead of a general plugin system
- **Decision:** Define a tiny interface around classification, with Anthropic as the only v1 implementation.
- **Why:** This preserves future model flexibility without overengineering.
- **Alternative considered:** Multi-provider abstraction from day one. Rejected because the extra indirection is not yet justified.

### 7. Keep review state in browser memory only
- **Decision:** The backend returns scan results; any user label edits remain client-side for the current run only.
- **Why:** This satisfies the UX requirement while avoiding session storage or a database.
- **Alternative considered:** Persisting review state server-side. Rejected because it is out of scope and adds risk.

## Risks / Trade-offs

- **[IMAP search differences across providers]** → Use a conservative subset of IMAP search features and apply application-side filtering where server-side matching is inconsistent.
- **[LLM misclassification of mixed transactional/promo emails]** → Include an explicit `uncertain` label and expose model reasoning plus manual override in the UI.
- **[Latency from one-request-per-email classification]** → Keep the default limit low and allow small bounded concurrency only if implementation stays simple.
- **[HTML-heavy messages produce poor snippets]** → Add normalization that extracts readable text before truncation.
- **[Hosted model privacy concerns]** → Send only bounded snippets and selected headers; do not persist content in v1.

## Migration Plan

No data migration is required because the repository is greenfield and v1 is read-only. Future mailbox-write features can be added behind new API endpoints and new specs without changing the scan result contract.

## Open Questions

- None blocking for v1. The only optional implementation choice is sequential versus small bounded-concurrency classification; either is acceptable if the external API contract remains unchanged.
