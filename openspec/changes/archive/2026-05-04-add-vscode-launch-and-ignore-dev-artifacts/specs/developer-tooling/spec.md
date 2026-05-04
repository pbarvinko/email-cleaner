## MODIFIED Requirements

### Requirement: Repository ignores common local Python artifacts
The repository SHALL provide a root `.gitignore` that excludes common local Python, testing, packaging, environment, and operating-system artifacts that are not intended for version control. The ignore rules SHALL also cover repository-local developer tool state such as `.opencode/`, local editor configuration under `.vscode/`, and virtual-environment directories such as `.venv/`.

#### Scenario: Local development artifacts are ignored
- **WHEN** a developer creates a virtual environment, runs tests, installs the project locally, or uses local developer tools
- **THEN** generated artifacts such as virtualenv directories, Python cache files, pytest caches, Ruff caches, packaging metadata, local editor configuration, and local tool state are ignored by Git

#### Scenario: Local secret files are ignored
- **WHEN** a developer creates local environment files for runtime credentials
- **THEN** those local environment files are ignored by Git by default

### Requirement: Repository provides a standard Python lint command
The repository SHALL define Ruff as the standard Python linter for local development and document how to run it.

#### Scenario: Developer installs dev dependencies
- **WHEN** a developer installs the project with dev dependencies
- **THEN** Ruff is available in the environment as part of the documented tooling setup

#### Scenario: Developer reads project instructions
- **WHEN** a developer consults the README for local development commands
- **THEN** the README includes a command for running the Python linter

### Requirement: Lint configuration stays minimal and repository-local
The repository SHALL define its Ruff configuration in the existing Python project configuration and keep the rule set small enough to avoid unrelated style churn.

#### Scenario: Lint configuration is discoverable
- **WHEN** a developer inspects project configuration
- **THEN** Ruff settings are defined in `pyproject.toml`

## ADDED Requirements

### Requirement: Repository supports local-only VS Code debugging
The repository SHALL allow a developer to create a local VS Code debug launch configuration that runs the supported `python -m email_cleaner` entrypoint using the current shell environment, without requiring the launch file to be tracked by Git.

#### Scenario: Local debug launch uses supported entrypoint
- **WHEN** a developer starts the local VS Code debug configuration
- **THEN** it runs `python -m email_cleaner` from the repository root using the developer's current shell environment

#### Scenario: Local debug launch remains untracked
- **WHEN** a developer creates `.vscode/launch.json` for the repository
- **THEN** Git ignores that file by default
