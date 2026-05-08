### ADDED Requirements

#### Requirement: User can run scans in explicit search, classify, or clean mode
The system SHALL provide one `POST /api/scan` workflow that accepts `mode` with allowed values `search`, `classify`, and `clean`, defaulting to `classify`. Each scan SHALL use a single authenticated IMAP session for the search and all message fetches in that run, opening `INBOX` read-only in `search` and `classify` mode and read-write in `clean` mode.

##### Scenario: Search mode skips classification
- **WHEN** the user submits a valid scan request with `mode="search"`
- **THEN** the system does not call the classifier, does not modify the mailbox, and returns results marked as not classified

##### Scenario: Classify mode is the safe default
- **WHEN** the user submits a valid scan request without `mode`
- **THEN** the system runs in `classify` mode, does not modify the mailbox, and returns suggested move metadata for moveable classifications

##### Scenario: Clean mode moves moveable classifications
- **WHEN** the user submits a valid scan request with `mode="clean"`
- **THEN** the system opens `INBOX` in read-write mode and moves `move` results to `promo` and `uncertain` results to `promo-check`

##### Scenario: Classify and clean require classifier configuration
- **WHEN** the user submits a valid scan request in `classify` or `clean` mode without classifier configuration
- **THEN** the system rejects the request before IMAP work with a classifier-not-configured error

##### Scenario: Infrastructure classification failures abort clean mode
- **WHEN** the classifier call fails due to transport, authentication, or service availability during `clean`
- **THEN** the system fails the scan instead of converting the result into an `uncertain` mailbox move

#### Requirement: Scan requests support bounded date filtering
The system SHALL accept `before_date` as an optional scan filter in addition to `since_date`, and SHALL reject a request when both dates are present but `before_date` is not later than `since_date`.

##### Scenario: Before-date filter is translated to IMAP
- **WHEN** the user supplies `before_date`
- **THEN** the system translates it directly to IMAP `BEFORE`

##### Scenario: Invalid date window is rejected
- **WHEN** the user submits both dates and `before_date <= since_date`
- **THEN** the system rejects the request with a validation error
