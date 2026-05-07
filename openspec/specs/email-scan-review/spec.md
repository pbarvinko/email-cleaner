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

### Requirement: User-facing search fields are simple and validated
The system SHALL expose simple search inputs instead of raw IMAP query syntax. Sender search SHALL use a single generic field, `from_query`, that is mapped directly to IMAP `FROM` search behavior rather than split into separate email-only or display-name-only filters. Optional search fields, including `since_date`, SHALL accept blank UI submission without failing validation, and blank values SHALL be treated as missing values.

#### Scenario: Supported search input fields
- **WHEN** the user opens the scan UI
- **THEN** the system presents fields for `from_query`, `subject_contains`, `since_date`, and `limit`

#### Scenario: Blank optional date field
- **WHEN** the user leaves `since_date` empty and provides another valid search criterion
- **THEN** the request validates successfully and the system treats `since_date` as absent

#### Scenario: Generic sender query behavior
- **WHEN** the user supplies `from_query`
- **THEN** the system uses that value as the IMAP `FROM` search term

#### Scenario: Limit defaults and bounds
- **WHEN** the user does not provide a limit
- **THEN** the system uses the configured default limit of 20

### Requirement: Scan results are per-run only
The system SHALL treat scan results and user review decisions as temporary state for the current run only.

#### Scenario: New run replaces previous review state
- **WHEN** the user starts a new scan or refreshes the application
- **THEN** the system does not restore labels or results from a previous run

### Requirement: Scan result snippets prefer readable body content
The system SHALL build each scan result snippet from readable message body content by preferring clean `text/plain` parts and falling back to readable text extracted from `text/html` only when no clean plain-text parts remain.

#### Scenario: Clean plain-text body is available
- **WHEN** a message contains at least one `text/plain` part that does not include any configured noisy plain-text marker
- **THEN** the snippet is built from the available clean plain-text content instead of HTML content

#### Scenario: Only noisy plain-text parts are available alongside HTML
- **WHEN** every available `text/plain` part includes at least one configured noisy plain-text marker and the message also contains `text/html`
- **THEN** the snippet is built from readable text extracted from the HTML content instead of the noisy plain-text content

#### Scenario: Mixed clean and noisy plain-text parts
- **WHEN** a message contains both clean and noisy `text/plain` parts
- **THEN** the snippet includes the clean plain-text content and excludes the noisy plain-text parts

#### Scenario: Noise markers are matched case-insensitively
- **WHEN** a `text/plain` part contains a configured noisy plain-text marker with different letter casing
- **THEN** the system still treats that part as noisy
