# Email Cleaner

Local-first IMAP inbox review tool with a Flask backend and static web UI.

Each scan searches `INBOX`, fetches matching messages over one authenticated read-only IMAP session, extracts readable content, and asks the classifier for a `keep`, `move`, or `uncertain` recommendation.

## Requirements

- Python 3.11+
- IMAP-enabled mailbox credentials
- Anthropic API key

## Environment variables

Required:

- `IMAP_HOST`
- `IMAP_USERNAME`
- `IMAP_PASSWORD`
- `ANTHROPIC_API_KEY`

Optional:

- `IMAP_PORT` (default: `993`)
- `SERVER_PORT` (default: `38452`)
- `SCAN_DEFAULT_LIMIT` (default: `20`)
- `SCAN_MAX_LIMIT` (default: `100`)
- `CLASSIFIER_SNIPPET_LENGTH` (default: `1200`)
- `ANTHROPIC_MODEL` (default: `claude-haiku-4-5-20251001`)

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Run locally

```bash
export IMAP_HOST=imap.example.com
export IMAP_USERNAME=user@example.com
export IMAP_PASSWORD=app-password
export ANTHROPIC_API_KEY=your-key

python -m email_cleaner
```

This supported startup path always binds the server to `0.0.0.0` and uses `SERVER_PORT` if set.

Then open `http://127.0.0.1:38452/` from the same machine.

## How scans behave

- The static web UI uses a single sender field, `from_query`, which still maps directly to IMAP `FROM` search behavior.
- Snippet extraction prefers readable plain text, ignores noisy plain-text parts, and falls back to HTML when needed.
- The UI shows a readable text snippet, while the classifier may instead receive Markdown derived from HTML when that produces better input.
- Classifier responses are structured JSON with labels `keep`, `move`, and `uncertain`.
- Overlong classifier reasons are truncated before they are returned by the API.

## Validate

```bash
ruff check .
pytest
```

## v1 limitations

- Searches only `INBOX`
- Read-only IMAP access only
- Each scan reuses one authenticated read-only IMAP session for search and message fetches
- No moving, deleting, flagging, or persisting review results
- Label overrides exist only in the current browser session
- Anthropic is the only classifier implementation in v1
