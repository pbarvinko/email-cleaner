### ADDED Requirements

#### Requirement: UI exposes explicit scan modes
The system SHALL present a required scan-mode selector with `search`, `classify`, and `clean` options and submit the chosen value through the existing `/api/scan` workflow.

##### Scenario: Mode selector is visible on initial load
- **WHEN** the user first opens the page
- **THEN** the scan-mode selector is visible and includes `Search only`, `Classify`, and `Clean`

##### Scenario: UI status text reflects scan mode
- **WHEN** a scan completes
- **THEN** the page status message distinguishes search-only results, classification-only suggestions, and confirmed clean-mode mailbox moves

#### Requirement: UI renders compact tabular scan results
The system SHALL render scan results in a compact table with overview columns for sender, subject, date/time, classification, action, snippet, and expandable details.

##### Scenario: Search mode renders explicit not-classified state
- **WHEN** a search-mode scan completes successfully
- **THEN** each result row shows `not classified` rather than a guessed label badge

##### Scenario: Local relabel override is removed
- **WHEN** the user reviews scan results
- **THEN** the page does not render a local label-edit select control
