## Context

The current scan request model already declares `since_date` as optional, but only text fields are normalized from empty string to `None`. Browser form submission therefore sends an empty string for an unfilled date input, which Pydantic rejects before the optional semantics can apply. Separately, the default port was changed in configuration, but some docs/tests still mention the old value.

## Goals / Non-Goals

**Goals:**
- Make a blank `since_date` field behave like other optional search inputs.
- Preserve the current validation rule that at least one non-limit search criterion is required.
- Align documentation and tests with the current default port `38452`.

**Non-Goals:**
- Change the search model to allow limit-only scans.
- Remove `since_date` from the UI or API.
- Change any networking/runtime behavior beyond correcting references.

## Decisions

### 1. Normalize empty `since_date` before validation
- **Decision:** Reuse the existing empty-string-to-`None` pattern for `since_date`.
- **Why:** This is the smallest correction that makes the optional contract true in practice.
- **Alternative considered:** Special-case date parsing in the UI. Rejected because server-side validation should correctly handle empty optional fields regardless of client behavior.

### 2. Keep the search-criteria requirement unchanged
- **Decision:** A blank `since_date` no longer fails on its own, but requests with no actual criteria still remain invalid.
- **Why:** This matches the approved product scope and avoids silently broad scans.
- **Alternative considered:** Allow limit-only scans. Rejected because that would broaden behavior beyond the requested bug fix.

### 3. Update all remaining default-port references
- **Decision:** Replace stale `5000` references with `38452` where they represent the app's default port.
- **Why:** Keeps docs, tests, and architecture notes consistent with actual config.

## Risks / Trade-offs

- **[Blank date accepted but empty search still rejected]** → Intended behavior; tests should cover both cases so the distinction stays clear.
- **[Stale port references outside main docs]** → Search targeted project files and update only true default-port references, not unrelated numeric bounds.

## Migration Plan

Adjust request-model normalization, update targeted tests/docs/architecture references, and verify validation plus existing test/lint workflows.

## Open Questions

- None.
