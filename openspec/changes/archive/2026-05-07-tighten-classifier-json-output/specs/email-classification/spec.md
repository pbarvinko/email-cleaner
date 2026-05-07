## MODIFIED Requirements

### Requirement: Classification outputs use constrained labels
The system SHALL produce only the labels `keep`, `move`, or `uncertain`, along with a short explanation for each classified email. The classifier prompt SHALL instruct the model to return exactly one raw JSON object and nothing else, with keys `label` and `reason`, and SHALL explicitly forbid tool calls, prose, explanations, and Markdown code fences around the JSON.

#### Scenario: Classification result shape
- **WHEN** the classifier returns a successful result
- **THEN** the result includes exactly one allowed label and a short human-readable reason

#### Scenario: Ambiguous content
- **WHEN** an email does not provide enough evidence to confidently distinguish important transactional content from promotional content
- **THEN** the system returns or preserves the label `uncertain`

#### Scenario: Prompt requires raw JSON only
- **WHEN** the system builds the classifier prompt
- **THEN** it instructs the model to return exactly one raw JSON object and nothing else

#### Scenario: Prompt forbids wrappers around JSON
- **WHEN** the system builds the classifier prompt
- **THEN** it explicitly forbids tool calls, explanatory prose, and Markdown code fences around the JSON output

#### Scenario: Prompt includes exact JSON example
- **WHEN** the system builds the classifier prompt
- **THEN** it includes an example JSON object matching the required `label` and `reason` shape
