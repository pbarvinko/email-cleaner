### Requirement: Local web UI and API are served from one application
The system SHALL serve a browser UI from `/` and JSON API endpoints from `/api/...` on the same local Flask server. The browser UI SHALL be delivered as static files served by Flask, and the browser code SHALL communicate with the backend through `/api/...` endpoints rather than server-side HTML templating.

#### Scenario: Browser access to UI root
- **WHEN** the user navigates to the local server root
- **THEN** the system returns the static root HTML document for running scans and reviewing results

#### Scenario: Programmatic access to API
- **WHEN** a client requests `/api/health`
- **THEN** the system returns a health response indicating the service is running

### Requirement: UI displays scan results without local relabel override
The system SHALL show scan results in the browser, including search-only runs and classified runs, without allowing the user to change the suggested label locally.

#### Scenario: Result review in browser
- **WHEN** a scan completes successfully
- **THEN** the UI displays basic metadata, the snippet, the scan action status, and classification details when the selected scan mode includes classification

#### Scenario: Local relabeling is not available
- **WHEN** the user reviews scan results in the UI
- **THEN** the page does not render a local label-edit control

### Requirement: UI makes scan mode and date filters explicit
The system SHALL present scan mode and date filter controls clearly enough for a user to distinguish search-only behavior, read-only classification, and opt-in mailbox mutation behavior.

#### Scenario: Scan form shows both date bounds
- **WHEN** the user opens the scan UI
- **THEN** the form includes controls labeled `On or after the date` and `Before the date`

#### Scenario: Scan form defaults to classify mode
- **WHEN** the user opens the scan UI
- **THEN** the mode selector is present, includes `Search only`, `Classify`, and `Clean`, and defaults to `Classify`

#### Scenario: Notice text explains mode behavior
- **WHEN** the user opens the scan UI
- **THEN** the notice text explains that search skips classification, classify is read-only, and clean requires explicit opt-in mailbox changes

### Requirement: Configuration is environment-based and validated at startup
The system SHALL load runtime configuration from environment variables validated with `pydantic-settings`. The application SHALL not expose a configurable server host setting and SHALL bind the web server to `0.0.0.0`.

#### Scenario: Missing required IMAP configuration
- **WHEN** a required IMAP setting is absent or invalid
- **THEN** the application fails fast with a configuration validation error before serving requests

#### Scenario: Missing Anthropic configuration still allows startup
- **WHEN** Anthropic configuration is absent but required IMAP settings are valid
- **THEN** the application still starts and serves requests so `search` mode remains available

#### Scenario: Fixed server host binding
- **WHEN** the application starts normally
- **THEN** it binds the web server to `0.0.0.0` rather than reading a host value from environment configuration
