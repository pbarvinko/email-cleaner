### Requirement: User can run scans in explicit search, classify, or clean mode
The system SHALL provide one `POST /api/scan` workflow that searches only the configured IMAP account's `INBOX`. The request SHALL accept `mode` with allowed values `search`, `classify`, and `clean`, defaulting to `classify`. Each scan SHALL use a single authenticated IMAP session for the search and all message fetches in that run, opening `INBOX` read-only in `search` and `classify` mode and read-write in `clean` mode.

#### Scenario: Search mode request with valid search fields
- **WHEN** the user submits at least one non-limit search field, an optional limit, and `mode="search"`
- **THEN** the system searches `INBOX`, fetches up to the requested number of matching emails, skips classification, and returns normalized results without moving, deleting, or flagging any message

#### Scenario: Classify mode is the default request behavior
- **WHEN** the user submits at least one non-limit search field, an optional limit, and does not provide `mode`
- **THEN** the system runs in `classify` mode, searches `INBOX`, fetches up to the requested number of matching emails, and returns suggested mailbox actions without modifying the mailbox

#### Scenario: Clean mode request with valid search fields
- **WHEN** the user submits at least one non-limit search field, an optional limit, and `mode="clean"`
- **THEN** the system searches `INBOX`, fetches up to the requested number of matching emails, and applies folder moves for classifications that map to a destination folder

#### Scenario: Classify or clean mode without classifier configuration
- **WHEN** the user submits a valid scan request in `classify` or `clean` mode without classifier configuration
- **THEN** the system rejects the request before IMAP work with a classifier-not-configured error

#### Scenario: Scan request missing search criteria
- **WHEN** the user submits a scan request with no search fields other than limit
- **THEN** the system rejects the request with a validation error explaining that at least one search criterion is required

#### Scenario: One read-only session per search or classify scan
- **WHEN** the system executes a `search` or `classify` scan that returns one or more message identifiers
- **THEN** it reuses the same authenticated read-only IMAP session for the search and the subsequent message fetches in that scan

#### Scenario: One read-write session per clean scan
- **WHEN** the system executes a `clean` scan that returns one or more message identifiers
- **THEN** it reuses the same authenticated read-write IMAP session for the search, fetches, and optional moves in that scan

### Requirement: User-facing search fields are simple and validated
The system SHALL expose simple search inputs instead of raw IMAP query syntax. Sender search SHALL use a single generic field, `from_query`, that is mapped directly to IMAP `FROM` search behavior rather than split into separate email-only or display-name-only filters. Optional search fields, including `since_date` and `before_date`, SHALL accept blank UI submission without failing validation, and blank values SHALL be treated as missing values.

#### Scenario: Supported search input fields
- **WHEN** the user opens the scan UI
- **THEN** the system presents fields for `from_query`, `subject_contains`, `since_date`, `before_date`, and `limit`

#### Scenario: Blank optional date field
- **WHEN** the user leaves `since_date` empty and provides another valid search criterion
- **THEN** the request validates successfully and the system treats `since_date` as absent

#### Scenario: Blank optional before-date field
- **WHEN** the user leaves `before_date` empty and provides another valid search criterion
- **THEN** the request validates successfully and the system treats `before_date` as absent

#### Scenario: Generic sender query behavior
- **WHEN** the user supplies `from_query`
- **THEN** the system uses that value as the IMAP `FROM` search term

#### Scenario: Date window must be valid
- **WHEN** the user supplies both `since_date` and `before_date`
- **THEN** the system requires `before_date` to be later than `since_date`

#### Scenario: Limit defaults and bounds
- **WHEN** the user does not provide a limit
- **THEN** the system uses the configured default limit of 20

### Requirement: Scan results are per-run only
The system SHALL treat scan results and user review decisions as temporary state for the current run only.

#### Scenario: New run replaces previous review state
- **WHEN** the user starts a new scan or refreshes the application
- **THEN** the system does not restore labels or results from a previous run

### Requirement: Scan results explain skipped, suggested, and applied mailbox actions
The system SHALL return scan results with action metadata that explains whether classification was skipped, whether a destination folder was only suggested, and whether a mailbox mutation was actually applied.

#### Scenario: Search result includes not-classified action metadata
- **WHEN** a result is returned from a `search` scan
- **THEN** the result marks classification as not classified and the action as none

#### Scenario: Classify result includes suggested action metadata
- **WHEN** a classification maps to a folder during a `classify` scan
- **THEN** the result includes the target folder and marks the action as a suggested move rather than an applied one

#### Scenario: Clean result includes applied action metadata
- **WHEN** a classification maps to a folder during a `clean` scan and the IMAP move succeeds
- **THEN** the result includes the target folder and marks the action as moved

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
