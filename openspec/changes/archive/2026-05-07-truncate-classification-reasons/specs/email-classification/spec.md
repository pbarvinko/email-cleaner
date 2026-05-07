## MODIFIED Requirements

### Requirement: Classification outputs use constrained labels
The system SHALL produce only the labels `keep`, `move`, or `uncertain`, along with a short explanation for each classified email. If a produced `reason` exceeds the maximum allowed length, the system SHALL preserve the label and truncate the `reason` to fit within the limit by ending the shortened string with `…`.

#### Scenario: Classification result shape
- **WHEN** the classifier returns a successful result
- **THEN** the result includes exactly one allowed label and a short human-readable reason

#### Scenario: Ambiguous content
- **WHEN** an email does not provide enough evidence to confidently distinguish important transactional content from promotional content
- **THEN** the system returns or preserves the label `uncertain`

#### Scenario: Overlong model reason is truncated
- **WHEN** the classifier returns an allowed label with a `reason` longer than the allowed maximum
- **THEN** the system preserves that label and truncates the `reason` to the maximum length with a trailing `…`

#### Scenario: Overlong fallback reason is truncated
- **WHEN** classification falls back to `uncertain` because of an exception whose message would make the fallback `reason` exceed the allowed maximum
- **THEN** the system returns `uncertain` and truncates the fallback `reason` to the maximum length with a trailing `…`
