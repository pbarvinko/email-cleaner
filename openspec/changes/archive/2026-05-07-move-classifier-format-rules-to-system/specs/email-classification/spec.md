## MODIFIED Requirements

### Requirement: Classification outputs use constrained labels
The system SHALL produce only the labels `keep`, `move`, or `uncertain`, along with a short explanation for each classified email. The classifier prompt SHALL deliver the output-format contract through a dedicated system instruction that requires exactly one raw JSON object and nothing else, with keys `label` and `reason`, and that explicitly forbids tool calls, prose, explanations, and Markdown code fences around the JSON.

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
