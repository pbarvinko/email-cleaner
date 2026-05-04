## ADDED Requirements

### Requirement: User can run a read-only inbox scan
The system SHALL provide a local scan workflow that searches only the configured IMAP account's `INBOX` and returns matching emails without modifying the mailbox.

#### Scenario: Scan request with valid search fields
- **WHEN** the user submits at least one non-limit search field and an optional limit
- **THEN** the system searches `INBOX`, fetches up to the requested number of matching emails, and returns normalized results without moving, deleting, or flagging any message

#### Scenario: Scan request missing search criteria
- **WHEN** the user submits a scan request with no search fields other than limit
- **THEN** the system rejects the request with a validation error explaining that at least one search criterion is required

### Requirement: User-facing search fields are simple and validated
The system SHALL expose simple search inputs instead of raw IMAP query syntax.

#### Scenario: Supported search input fields
- **WHEN** the user opens the scan UI
- **THEN** the system presents fields for `from_email`, `from_name_contains`, `subject_contains`, `since_date`, and `limit`

#### Scenario: Limit defaults and bounds
- **WHEN** the user does not provide a limit
- **THEN** the system uses the configured default limit of 20

### Requirement: Scan results are per-run only
The system SHALL treat scan results and user review decisions as temporary state for the current run only.

#### Scenario: New run replaces previous review state
- **WHEN** the user starts a new scan or refreshes the application
- **THEN** the system does not restore labels or results from a previous run
