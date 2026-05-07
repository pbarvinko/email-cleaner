## ADDED Requirements

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
