## MODIFIED Requirements

### Requirement: Classification outputs use constrained labels
The system SHALL produce only the labels `keep`, `move`, or `uncertain`, along with a short explanation for each classified email. Before parsing classifier output, the system SHALL accept either one raw JSON object or that same JSON wrapped as a single outer Markdown code fence, with or without a `json` language hint.

#### Scenario: Classification result shape
- **WHEN** the classifier returns a successful result
- **THEN** the result includes exactly one allowed label and a short human-readable reason

#### Scenario: Ambiguous content
- **WHEN** an email does not provide enough evidence to confidently distinguish important transactional content from promotional content
- **THEN** the system returns or preserves the label `uncertain`

#### Scenario: Raw JSON output parses directly
- **WHEN** the classifier returns one raw JSON object with no wrapper
- **THEN** the system parses it without extra normalization

#### Scenario: JSON-fenced output is normalized before parsing
- **WHEN** the classifier returns one JSON object wrapped in a single outer ```json Markdown code fence
- **THEN** the system strips that outer fence and parses the remaining JSON object

#### Scenario: Bare fenced output is normalized before parsing
- **WHEN** the classifier returns one JSON object wrapped in a single outer ``` Markdown code fence without a language hint
- **THEN** the system strips that outer fence and parses the remaining JSON object
