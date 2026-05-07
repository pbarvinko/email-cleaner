## Context

`ImapClient.search()` and `ImapClient.fetch_message()` each open and close their own IMAP connection. `ScanService.scan()` first calls `search()` and then loops over message IDs, so a scan of N messages currently performs N+1 authenticated IMAP sessions. The scan flow is already sequential and read-only, so the smallest improvement is to hold one connection open for the duration of a single scan and use it for both search and fetches.

## Goals / Non-Goals

**Goals:**
- Reuse one authenticated read-only IMAP connection for a full scan.
- Preserve the current scan contract and sequential processing model.
- Keep connection management explicit and easy to test.

**Non-Goals:**
- Introduce long-lived pooled connections across requests.
- Parallelize message fetching or classification.
- Change search criteria, mailbox selection, or write behavior.

## Decisions

### 1. Scope connection reuse to one scan only
- **Decision:** Open one IMAP connection per `ScanService.scan()` call and close it when the scan completes or fails.
- **Why:** This removes repeated login/select overhead without adding shared mutable state across requests.
- **Alternative considered:** Cache a connection on `ImapClient`. Rejected because it complicates lifecycle management and failure recovery.

### 2. Keep search and fetch operations on the same selected mailbox
- **Decision:** Perform search and subsequent fetches using the same connection after selecting `INBOX` in read-only mode once.
- **Why:** It matches current behavior while eliminating redundant `select` calls.
- **Alternative considered:** Split search and fetch into separate reused sessions. Rejected because it retains unnecessary session churn.

### 3. Preserve small client API surface
- **Decision:** Add a scan-oriented path that can search and fetch over an existing connection rather than exposing a broad connection abstraction throughout the codebase.
- **Why:** The repo favors simple deterministic flows and does not need a generic IMAP session layer.
- **Alternative considered:** Refactor all public IMAP methods to require an external connection argument. Rejected as more invasive than needed.

## Risks / Trade-offs

- **[A single connection failure aborts the whole scan]** → Acceptable; the current implementation already fails the scan on IMAP errors, and retry logic is out of scope.
- **[Longer-lived connection stays open during classification work]** → Acceptable for now because scans are sequential and bounded; the reduced reconnect cost is the main goal.

## Migration Plan

Update the IMAP client and scan service together, then verify with tests that one scan uses one connection while remaining read-only.

## Open Questions

- None.
