## Context

The app currently exposes separate sender inputs, but the backend ultimately relies on IMAP search plus extra local filtering to approximate that model. Since IMAP `FROM` is already a generic sender-text search, keeping two sender fields creates both UI confusion and implementation overhead. The simplest consistent model is one sender query field passed straight through to IMAP `FROM`.

## Goals / Non-Goals

**Goals:**
- Simplify sender search to a single field.
- Align backend behavior directly with IMAP `FROM` search semantics.
- Remove unnecessary local sender-name filtering code.
- Preserve the rest of the scan workflow and validation model.

**Non-Goals:**
- Maintain backward compatibility for the old sender field names.
- Add provider-specific enhanced search semantics.
- Change classification, result rendering, or non-sender filters.

## Decisions

### 1. Introduce a single sender query field
- **Decision:** Use one field, `from_query`, as the sender-related search term in API and UI.
- **Why:** This is explicit, small, and avoids pretending we can distinguish display-name-only versus email-only matching portably across IMAP servers.
- **Alternative considered:** Keep aliases for old fields. Rejected because the repo is early-stage and a clean break is simpler.

### 2. Map `from_query` directly to IMAP `FROM`
- **Decision:** Pass the value directly into the IMAP `FROM` search criterion.
- **Why:** This matches actual IMAP behavior and eliminates local post-filter logic.
- **Alternative considered:** Preserve local display-name filtering. Rejected because it adds complexity and diverges from the simplified model.

### 3. Remove sender-specific local filtering
- **Decision:** Delete local `From` header inspection used only for `from_name_contains`.
- **Why:** It is no longer needed once sender search is represented as generic IMAP `FROM` search.

## Risks / Trade-offs

- **[Behavior differs from prior field names]** → Intended; docs/UI/tests should make the new generic sender-search meaning clear.
- **[IMAP `FROM` matching varies somewhat by provider]** → Acceptable within the provider-agnostic IMAP scope; the new model is at least honest about that behavior.

## Migration Plan

Update the request model, IMAP client, UI, tests, and docs to use `from_query` only, then remove obsolete sender filtering code.

## Open Questions

- None.
