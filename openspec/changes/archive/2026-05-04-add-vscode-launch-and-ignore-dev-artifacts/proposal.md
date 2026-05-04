## Why

Local debugging is easier with a ready-to-use VS Code launch configuration, but this project should keep editor-specific files and local development artifacts out of version control by default. Adding a local-only debug launch file and explicit ignore coverage improves developer ergonomics without changing application behavior.

## What Changes

- Add a VS Code debug launch configuration for running `python -m email_cleaner` using the current shell environment.
- Keep `.vscode/` ignored so the launch configuration remains local-only.
- Add explicit ignore coverage for `.opencode/` and retain ignore coverage for `.venv/`.

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `developer-tooling`: Extend repository-local developer tooling behavior to cover a local-only VS Code debug launch configuration and explicit ignore rules for local development artifacts.

## Impact

- Root `.gitignore` behavior.
- New local `.vscode/launch.json` debug configuration.
