# Repository scout report

## Detected stack
- **Language/runtime:** Python 3.11+ (`pyproject.toml`)
- **Backend framework:** Flask (`pyproject.toml`, `email_cleaner/app.py`, `email_cleaner/api.py`)
- **Validation/settings:** Pydantic + pydantic-settings (`email_cleaner/models.py`, `email_cleaner/config.py`)
- **Email/normalization:** stdlib `email` parser + BeautifulSoup + **markdownify** (`email_cleaner/normalize.py`, `pyproject.toml`)
- **Classifier:** Anthropic SDK (`email_cleaner/classifier.py`, `pyproject.toml`)
- **Packaging/build:** setuptools (`pyproject.toml`)

## Entrypoints and runtime
- Run app: `python -m email_cleaner` (`email_cleaner/__main__.py`)
- App factory: `create_app()` (`email_cleaner/app.py`)
- HTTP surface:
  - `GET /` serves static UI (`email_cleaner/app.py`, `email_cleaner/web/`)
  - `GET /api/health`, `POST /api/scan` (`email_cleaner/api.py`)
- Settings are env-driven (`email_cleaner/config.py`); app binds `0.0.0.0` + `SERVER_PORT` (`email_cleaner/app.py`)

## Actual scan pipeline (current code)
`POST /api/scan` -> `ScanRequest` validation -> `ScanService.scan()` -> IMAP scan -> normalize -> classifier -> typed response (`ScanResponse` / `ScanResultItem`).

Concrete layering in code:
- API layer validates input and returns JSON/error envelopes (`email_cleaner/api.py`)
- Service layer orchestrates per-message flow (`email_cleaner/service.py`)
- IMAP layer performs search/fetch (`email_cleaner/imap_client.py`)
- Normalization layer creates normalized fields (`email_cleaner/normalize.py`)
- Classification layer returns `ClassificationResult` (`email_cleaner/classifier.py`, `email_cleaner/models.py`)

## IMAP behavior
- IMAP uses `IMAP4_SSL`, logs in, and selects `INBOX` with `readonly=True` (`email_cleaner/imap_client.py`)
- Full scan reuses **one read-only IMAP session**: `scan_messages()` opens one connection, runs search once, then fetches each message on the same connection before closing (`email_cleaner/imap_client.py`)
- Search criteria mapping includes `from_query` -> IMAP `FROM` (`email_cleaner/imap_client.py`)

## Normalization behavior
- `normalize_email()` returns both:
  - UI-facing `snippet`
  - classifier-only `classifier_input` (excluded from API serialization via model field config) (`email_cleaner/normalize.py`, `email_cleaner/models.py`)
- Plain-text handling prefers readable text and filters noisy plain-text using marker heuristics (e.g., CSS-like fragments such as `font-family`, `mso-`, `@media`) (`email_cleaner/normalize.py`)
- HTML fallback behavior:
  - UI `snippet` is extracted from HTML via BeautifulSoup text collapse
  - `classifier_input` is generated from HTML via markdownify and normalized newlines (`email_cleaner/normalize.py`)
- If neither clean plain text nor HTML yields content, fallback uses collapsed raw text parts with empty-content guard string (`email_cleaner/normalize.py`)

## Anthropic classifier behavior
- Uses a fixed `system` prompt describing keep/move/uncertain policy (`email_cleaner/classifier.py`)
- Sends JSON payload where classifier sees `snippet` populated from `classifier_input` (`email_cleaner/classifier.py`)
- Requests structured output with `output_config` + JSON schema (`label`, `reason`) (`email_cleaner/classifier.py`)
- Classification reason truncation:
  - reasons are truncated to 280 chars with trailing ellipsis when needed
  - truncation is applied on normal parse path and fallback error paths (`email_cleaner/classifier.py`, `email_cleaner/models.py`)

## Quality gates and conventions
- Lint: `ruff check .` (`README.md`, `pyproject.toml`)
- Test: `pytest` (`README.md`, `pyproject.toml`)
- No dedicated formatter/type-checker command configured in repo configs.
