## 1. Request and UI contract update

- [x] 1.1 Replace `from_email` and `from_name_contains` with a single `from_query` field in the scan request model and related validation
- [x] 1.2 Update the static web UI labels, inputs, and request payload shape to use the new sender query field

## 2. IMAP search simplification

- [x] 2.1 Update the IMAP client to use `from_query` directly in IMAP `FROM` search criteria
- [x] 2.2 Remove obsolete local sender-name filtering code and any helper logic used only for that behavior

## 3. Verification

- [x] 3.1 Update tests and documentation to reflect the new sender-query contract
- [x] 3.2 Run the relevant test and lint checks and update the change task list to reflect completed work
