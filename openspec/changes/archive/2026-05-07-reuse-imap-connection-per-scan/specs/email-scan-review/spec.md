## MODIFIED Requirements

### Requirement: User can run a read-only inbox scan
The system SHALL provide a local scan workflow that searches only the configured IMAP account's `INBOX` and returns matching emails without modifying the mailbox. Each scan SHALL use a single authenticated IMAP session in read-only mode for the search and all message fetches in that run.

#### Scenario: Scan request with valid search fields
- **WHEN** the user submits at least one non-limit search field and an optional limit
- **THEN** the system searches `INBOX`, fetches up to the requested number of matching emails, and returns normalized results without moving, deleting, or flagging any message

#### Scenario: Scan request missing search criteria
- **WHEN** the user submits a scan request with no search fields other than limit
- **THEN** the system rejects the request with a validation error explaining that at least one search criterion is required

#### Scenario: One read-only session per scan
- **WHEN** the system executes a scan that returns one or more message identifiers
- **THEN** it reuses the same authenticated read-only IMAP session for the search and the subsequent message fetches in that scan
