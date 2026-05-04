### Requirement: Each email is classified independently
The system SHALL classify each fetched email independently using the configured classifier implementation.

#### Scenario: Independent message classification
- **WHEN** a scan returns multiple emails
- **THEN** the system classifies each email as a separate unit rather than relying on a shared batch decision

### Requirement: Classification outputs use constrained labels
The system SHALL produce only the labels `keep`, `move`, or `uncertain`, along with a short explanation for each classified email.

#### Scenario: Classification result shape
- **WHEN** the classifier returns a successful result
- **THEN** the result includes exactly one allowed label and a short human-readable reason

#### Scenario: Ambiguous content
- **WHEN** an email does not provide enough evidence to confidently distinguish important transactional content from promotional content
- **THEN** the system returns or preserves the label `uncertain`

### Requirement: Classification input is normalized and bounded
The system SHALL send only compact normalized email data to the classifier.

#### Scenario: Normalized email payload
- **WHEN** the system prepares an email for classification
- **THEN** it includes message identifier, sender display name, sender email address, subject, date, a bounded text snippet, and selected headers when available

#### Scenario: HTML-heavy emails
- **WHEN** a message body is primarily HTML
- **THEN** the system converts it to readable text or extracts a readable text snippet before classification

### Requirement: Classifier provider seam is minimal and replaceable
The system SHALL isolate model-provider-specific classification code behind a small interface without changing the scan API contract.

#### Scenario: Future provider replacement
- **WHEN** a different classifier provider is introduced later
- **THEN** the system can replace the classifier implementation without changing the required request or response shape of the scan workflow
