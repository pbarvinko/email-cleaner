### Requirement: Each email is classified independently
The system SHALL classify each fetched email independently using the configured classifier implementation.

#### Scenario: Independent message classification
- **WHEN** a scan returns multiple emails
- **THEN** the system classifies each email as a separate unit rather than relying on a shared batch decision

### Requirement: Classification outputs use constrained labels
The system SHALL produce only the labels `keep`, `move`, or `uncertain`, along with a short explanation for each classified email.

The classifier request SHALL deliver the output-format contract through a dedicated system instruction that requires exactly one raw JSON object and nothing else, with keys `label` and `reason`, and that explicitly forbids tool calls, prose, explanations, and Markdown code fences around the JSON. The instruction SHALL include an example JSON object matching the required shape.

Before parsing classifier output, the system SHALL accept either one raw JSON object or that same JSON wrapped as a single outer Markdown code fence, with or without a `json` language hint.

If a produced `reason` exceeds the maximum allowed length, the system SHALL preserve the label and truncate the `reason` to fit within the limit by ending the shortened string with `…`.

#### Scenario: Classification result shape
- **WHEN** the classifier returns a successful result
- **THEN** the result includes exactly one allowed label and a short human-readable reason

#### Scenario: Ambiguous content
- **WHEN** an email does not provide enough evidence to confidently distinguish important transactional content from promotional content
- **THEN** the system returns or preserves the label `uncertain`

#### Scenario: System prompt requires raw JSON only
- **WHEN** the system builds the classifier request
- **THEN** it sends a dedicated system instruction that requires exactly one raw JSON object and nothing else

#### Scenario: System prompt forbids wrappers around JSON
- **WHEN** the system builds the classifier request
- **THEN** the dedicated system instruction explicitly forbids tool calls, explanatory prose, and Markdown code fences around the JSON output

#### Scenario: System prompt includes exact JSON example
- **WHEN** the system builds the classifier request
- **THEN** the dedicated system instruction includes an example JSON object matching the required `label` and `reason` shape

#### Scenario: Raw JSON output parses directly
- **WHEN** the classifier returns one raw JSON object with no wrapper
- **THEN** the system parses it without extra normalization

#### Scenario: JSON-fenced output is normalized before parsing
- **WHEN** the classifier returns one JSON object wrapped in a single outer ```json Markdown code fence
- **THEN** the system strips that outer fence and parses the remaining JSON object

#### Scenario: Bare fenced output is normalized before parsing
- **WHEN** the classifier returns one JSON object wrapped in a single outer ``` Markdown code fence without a language hint
- **THEN** the system strips that outer fence and parses the remaining JSON object

#### Scenario: Overlong model reason is truncated
- **WHEN** the classifier returns an allowed label with a `reason` longer than the allowed maximum
- **THEN** the system preserves that label and truncates the `reason` to the maximum length with a trailing `…`

#### Scenario: Overlong fallback reason is truncated
- **WHEN** classification falls back to `uncertain` because of an exception whose message would make the fallback `reason` exceed the allowed maximum
- **THEN** the system returns `uncertain` and truncates the fallback `reason` to the maximum length with a trailing `…`

### Requirement: Classification input is normalized and bounded
The system SHALL send only compact normalized email data to the classifier.

#### Scenario: Normalized email payload
- **WHEN** the system prepares an email for classification
- **THEN** it includes message identifier, sender display name, sender email address, subject, date, a bounded text snippet, and selected headers when available

#### Scenario: HTML-heavy emails
- **WHEN** a message body is primarily HTML
- **THEN** the system converts it to readable text or extracts a readable text snippet before classification

### Requirement: Classifier input preserves structure for HTML fallback content
The system SHALL prepare classifier input from readable normalized email content, and when the selected body source is HTML fallback content it SHALL convert that HTML to Markdown using an existing Python library before applying classifier-facing length limits.

#### Scenario: Plain-text body remains plain for classification
- **WHEN** a message has at least one clean `text/plain` part selected as the body source
- **THEN** the classifier input uses that readable plain-text content without HTML-to-Markdown conversion

#### Scenario: HTML fallback is converted for classification
- **WHEN** every available `text/plain` part is noisy and `text/html` is selected as the body source
- **THEN** the classifier input uses Markdown converted from the HTML content rather than raw HTML or flattened plain text

#### Scenario: User-visible snippet remains readable text
- **WHEN** HTML fallback is selected for a message
- **THEN** the scan result snippet remains readable text for UI display even though the classifier input is prepared from Markdown

### Requirement: Classifier provider seam is minimal and replaceable
The system SHALL isolate model-provider-specific classification code behind a small interface without changing the scan API contract.

#### Scenario: Future provider replacement
- **WHEN** a different classifier provider is introduced later
- **THEN** the system can replace the classifier implementation without changing the required request or response shape of the scan workflow
