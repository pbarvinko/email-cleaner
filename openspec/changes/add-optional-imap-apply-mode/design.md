## Context

The existing scan flow already centralizes classification policy in `ScanService` and IMAP mechanics in `ImapClient`. This change preserves that split while making the pipeline explicit as three request-scoped modes: `search`, `classify`, and `clean`.

## Goals / Non-Goals

**Goals:**
- Keep `POST /api/scan` as the only scan endpoint.
- Preserve read-only mailbox behavior except in explicit `clean` mode.
- Add validated `before_date` filtering alongside the existing criteria.
- Return enough result metadata for the UI to distinguish skipped, suggested, and applied stages.
- Replace the card UI with a compact table plus expandable details.

**Non-Goals:**
- Support arbitrary folder mappings configured by users.
- Persist browser-side label changes back to the mailbox.
- Introduce partial-failure recovery for move operations.

## Decisions

### 1. Keep mode selection request-scoped
- **Decision:** Add `mode: Literal["search", "classify", "clean"] = "classify"` to `ScanRequest`.
- **Why:** Makes the workflow explicit while preserving safe read-only default behavior for existing callers.

### 2. Keep folder policy in the service layer
- **Decision:** `ScanService` resolves `move -> promo`, `uncertain -> promo-check`, and `keep -> None`.
- **Why:** Classifier output remains decoupled from mailbox mechanics.

### 3. Reuse the per-scan IMAP session for mutations
- **Decision:** `ImapClient.scan_messages()` selects `INBOX` read-only for `search`/`classify` and read-write for `clean`, returning a session object that can also move a fetched message.
- **Why:** Search, fetch, and optional move operations stay on one authenticated connection per scan.

### 4. Surface stage and action metadata in every result
- **Decision:** Include `classification_status`, `target_folder`, `action`, and `action_reason` in `ScanResultItem`, plus `mode`, `applied_count`, and `stages` in `ScanResponse`.
- **Why:** Callers need to know whether classification was skipped, suggested, or applied.

### 5. Fail fast when classification is unavailable
- **Decision:** Anthropic configuration becomes optional at startup, but `ScanService` rejects `classify` and `clean` requests before IMAP work when no classifier is configured.
- **Why:** `search` mode should still work without Anthropic configuration, while classified flows must not degrade silently.

### 6. Tighten classifier fallback behavior for clean mode
- **Decision:** Preserve fallback-to-`uncertain` only for classifier output validation cases that still represent a successful call; surface infrastructure failures as scan errors.
- **Why:** Clean mode must not move mail due to transport or auth failures collapsed into `uncertain`.

## Risks / Trade-offs

- **Move failures abort the scan** → Acceptable for this version because the API already reports scan-level failure for IMAP errors.
- **Longer-lived read-write IMAP sessions during clean runs** → Acceptable because scans are sequential and explicitly user-triggered.

## Migration Plan

Implement request/response contract changes first, then update classifier/configuration seams and IMAP session behavior, then refresh UI rendering and OpenSpec docs, and finally verify with tests.

## Open Questions

- None.
