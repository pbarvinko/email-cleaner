## Context

`_build_snippet` currently aggregates all `text/plain` parts and uses HTML only when no plain text is present. In real multipart messages, some plain-text parts are not actually readable message bodies; they are generated artifacts that include CSS or Outlook-specific markers. The desired behavior is to keep the simple "prefer plain text" rule, but only for plain-text parts that look readable. The user-visible snippet should remain a readable text string, while classifier input can preserve more HTML structure by converting fallback HTML to Markdown at classification time.

## Goals / Non-Goals

**Goals:**
- Preserve the existing preference for plain-text snippets when the plain text is readable.
- Exclude noisy plain-text parts using a deterministic marker list.
- Fall back to readable HTML-derived text for the snippet only when no clean plain-text parts remain.
- Provide Markdown-converted HTML only to the classifier when HTML fallback is selected.
- Keep the change local to normalization logic and tests.

**Non-Goals:**
- Introduce scoring, ranking, or ML-based part selection.
- Reorder multipart traversal beyond the current walk order.
- Render Markdown in the browser UI.
- Introduce multipart scoring or ranking beyond the agreed noise filtering.

## Decisions

### 1. Filter plain-text parts individually
- **Decision:** Evaluate each `text/plain` part independently and drop only the parts that match the noise markers.
- **Why:** This preserves readable plain-text bodies when a message also contains noisy auxiliary plain-text parts.
- **Alternative considered:** If any plain-text part is noisy, discard all plain text and switch to HTML. Rejected because it throws away good plain-text content too aggressively.

### 2. Use a fixed case-insensitive marker list
- **Decision:** Detect noisy plain-text parts with simple case-insensitive substring checks for the agreed marker list.
- **Why:** The rule is explicit, cheap, and easy to test.
- **Alternative considered:** Regex-heavy heuristics or content scoring. Rejected as unnecessary complexity for the current problem.

### 3. Keep HTML as fallback only
- **Decision:** Build the snippet from HTML parts only when no clean plain-text parts remain after filtering.
- **Why:** This matches the user intent and keeps plain text as the preferred source when it is usable.
- **Alternative considered:** Blend clean plain text and HTML text together. Rejected because it can duplicate content and complicate snippet construction.

### 4. Split UI snippet text from classifier body preparation
- **Decision:** Keep the normalized `snippet` field as readable text for UI display, but prepare Markdown from HTML only in the classifier input path when HTML fallback was selected.
- **Why:** This improves classifier context without changing the user-facing snippet contract or introducing Markdown artifacts in the browser.
- **Alternative considered:** Store Markdown directly in `snippet`. Rejected because it leaks classifier-oriented formatting into UI behavior.

### 5. Use an existing HTML-to-Markdown library
- **Decision:** Use an existing Python library for deterministic HTML-to-Markdown conversion rather than implementing a custom converter.
- **Why:** A library is smaller, safer, and easier to maintain than bespoke conversion logic.
- **Alternative considered:** Custom conversion helper. Rejected because it adds unnecessary complexity and edge-case handling.

### 6. Keep the UI display contract unchanged
- **Decision:** Continue returning the snippet as a plain string field and let the current UI display raw Markdown text without rendering it.
- **Why:** This keeps the result review experience stable and limits the change to body selection plus classifier preparation.
- **Alternative considered:** Render Markdown in the browser. Rejected as out of scope for this behavior-focused normalization change.

## Risks / Trade-offs

- **[Marker list may miss some noisy formats]** → Keep the first version limited to the agreed markers and extend only when real examples justify it.
- **[A legitimate plain-text message could contain one marker substring]** → Acceptable for now because the markers are strongly associated with styling artifacts, and HTML fallback still preserves a readable snippet when available.
- **[Markdown conversion may differ slightly from browser-visible text]** → Acceptable because the classifier and UI have different needs, and the UI contract remains stable.

## Migration Plan

No migration is required. Update normalization logic and tests together so future scans immediately use the refined snippet selection.

## Open Questions

- None.
