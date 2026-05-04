# Repository scout report

## Current stack
- **Python 3.11+** (`pyproject.toml`)
- **Flask** web app (`pyproject.toml`, `email_cleaner/app.py`)
- **Pydantic + pydantic-settings** for request/config validation (`email_cleaner/models.py`, `email_cleaner/config.py`)
- **Anthropic SDK** and IMAP integration for classification/scan pipeline (`pyproject.toml`, `email_cleaner/classifier.py`, `email_cleaner/imap_client.py`)
- **Packaging/build:** setuptools backend (`pyproject.toml`)

## Entrypoints
- Module entrypoint: `python -m email_cleaner` (`email_cleaner/__main__.py`)
- App factory: `create_app()` (`email_cleaner/app.py`)
- Runtime server launch: `run_app()` binds `0.0.0.0` and `SERVER_PORT` (`email_cleaner/app.py`, `email_cleaner/config.py`)

## Config and runtime model
- Environment-driven settings via `Settings(BaseSettings)` (`email_cleaner/config.py`)
- Required env vars: `IMAP_HOST`, `IMAP_USERNAME`, `IMAP_PASSWORD`, `ANTHROPIC_API_KEY` (`README.md`)
- Defaults include `IMAP_PORT=993`, `SERVER_PORT=38452`, scan limit/snippet bounds (`email_cleaner/config.py`)
- `ScanRequest` enforces at least one search filter (`from_query`, `subject_contains`, or `since_date`) (`email_cleaner/models.py`)

## UI and API structure
- Static UI served from `email_cleaner/web/` (`index.html`, `app.js`, `style.css`)
- `GET /` serves `index.html` directly (`email_cleaner/app.py`)
- API blueprint under `/api` with:
  - `GET /api/health`
  - `POST /api/scan` (`email_cleaner/api.py`)

## Tests and lint commands
- Test: `pytest` (`README.md`, `[tool.pytest.ini_options]` in `pyproject.toml`)
- Lint: `ruff check .` (`README.md`, `[tool.ruff]` in `pyproject.toml`)
- No formatter command configured; no mypy/pyright config detected.

## Notable architectural conventions
- App-factory + injectable `scan_service` to support test doubles (`email_cleaner/app.py`, `tests/conftest.py`)
- Layered flow: API -> `ScanService` -> IMAP fetch/normalize -> classifier -> typed response (`email_cleaner/api.py`, `email_cleaner/service.py`)
- Structured JSON error envelope for validation (`400`) and scan failures (`502`) (`email_cleaner/api.py`)
- OpenSpec project artifacts are present (`openspec/config.yaml`, `openspec/specs/*`, `openspec/changes/archive/*`)
