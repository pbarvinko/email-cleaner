# AGENTS.md

## Purpose
- Local-first IMAP inbox review tool.
- Flask backend + static web UI.
- Read-only mailbox behavior in v1.

## Stack
- Python 3.11+
- Flask
- pydantic-settings
- Anthropic SDK
- markdownify
- setuptools
- pytest
- Ruff

## Entrypoints
- Run app: `python -m email_cleaner`
- App factory: `email_cleaner.app:create_app`

## Local commands
- Install: `pip install -e ".[dev]"`
- Lint: `ruff check .`
- Test: `pytest`

## Runtime conventions
- Config comes from environment variables.
- Required env vars: `IMAP_HOST`, `IMAP_USERNAME`, `IMAP_PASSWORD`, `ANTHROPIC_API_KEY`.
- Server binds to `0.0.0.0` and uses `SERVER_PORT`.

## Architecture notes
- Static web assets live in `email_cleaner/web/`.
- UI is served from `/` and talks to the backend only via `/api/...`.
- Main flow: API -> `ScanService` -> IMAP scan -> normalize -> classifier -> typed response.
- Each scan reuses one authenticated read-only IMAP session for search and message fetches.
- Normalization produces a readable UI `snippet` and a classifier-only `classifier_input`.
- Plain-text parts are preferred unless they contain noisy styling markers; HTML fallback becomes readable text for the UI snippet and Markdown for classifier input.
- Classifier requests use Anthropic structured JSON output via `output_config` and truncate overlong reasons to fit the response contract.
- Sender search uses `from_query`, mapped directly to IMAP `FROM`.

## Guardrails
- Keep mailbox access read-only unless a spec explicitly changes that.
- Prefer simple deterministic flow outside the LLM.
- Keep the classifier seam minimal.
- Preserve the distinction between UI `snippet` text and classifier-only `classifier_input` when updating docs or behavior.
- Update OpenSpec for behavior changes before implementation.
