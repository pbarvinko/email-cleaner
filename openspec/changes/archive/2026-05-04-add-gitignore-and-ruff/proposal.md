## Why

The repository currently lacks basic source-control hygiene and a standard linter, which makes local artifacts easy to commit accidentally and leaves code quality checks ad hoc. Adding a sensible `.gitignore` and Ruff now keeps the project clean with minimal tooling overhead.

## What Changes

- Add a root `.gitignore` covering Python, test, virtualenv, packaging, environment, and common local/editor artifacts for this repository.
- Add Ruff as the project's standard Python linter in dev dependencies.
- Add minimal Ruff configuration in `pyproject.toml`.
- Document how to run the linter in `README.md`.

## Capabilities

### New Capabilities
- `developer-tooling`: Define baseline repository hygiene and linting behavior for local development.

### Modified Capabilities
- None.

## Impact

- New root `.gitignore` file.
- Updated Python project config and developer documentation.
- New dev dependency and lint command for contributors.
