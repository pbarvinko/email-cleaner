# Email Cleaner

Local-first IMAP inbox review tool with a Flask backend and static web UI.

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

The static web UI uses a single sender field, `from_query`, which maps directly to IMAP `FROM` search behavior.

## Validate

```bash
ruff check .
pytest
```

## v1 limitations

- Searches only `INBOX`
- Read-only IMAP access only
- No moving, deleting, flagging, or persisting review results
- Label overrides exist only in the current browser session
- Anthropic is the only classifier implementation in v1
