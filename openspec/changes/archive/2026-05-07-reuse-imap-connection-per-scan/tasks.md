## 1. IMAP connection lifecycle

- [x] 1.1 Update IMAP access so one scan reuses a single authenticated read-only connection for search and message fetches
- [x] 1.2 Keep connection cleanup reliable on success and failure without changing mailbox write behavior

## 2. Verification

- [x] 2.1 Add or update tests to verify a multi-message scan does not reconnect per fetched message and remains read-only
- [x] 2.2 Run the relevant test and lint checks and update this task list to reflect completed work
