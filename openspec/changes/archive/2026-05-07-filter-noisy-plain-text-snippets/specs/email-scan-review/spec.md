## ADDED Requirements

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
