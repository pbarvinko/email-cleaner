## ADDED Requirements

### Requirement: Local web UI and API are served from one application
The system SHALL serve a browser UI from `/` and JSON API endpoints from `/api/...` on the same local Flask server.

#### Scenario: Browser access to UI root
- **WHEN** the user navigates to the configured local server root
- **THEN** the system returns the HTML UI for running scans and reviewing results

#### Scenario: Programmatic access to API
- **WHEN** a client requests `/api/health`
- **THEN** the system returns a health response indicating the service is running

### Requirement: UI displays classification results and supports local override
The system SHALL show scan results in the browser and allow the user to change the suggested label for the current run.

#### Scenario: Result review in browser
- **WHEN** a scan completes successfully
- **THEN** the UI displays basic metadata, the snippet used for classification, the model label, and the model reason for each email

#### Scenario: Manual relabeling
- **WHEN** the user changes an email label in the UI
- **THEN** the updated label is reflected in the browser for the current run without writing changes back to the mailbox

### Requirement: Configuration is environment-based and validated at startup
The system SHALL load runtime configuration from environment variables validated with `pydantic-settings`.

#### Scenario: Missing required configuration
- **WHEN** a required IMAP or Anthropic setting is absent or invalid
- **THEN** the application fails fast with a configuration validation error before serving requests
