## 1. Request and response contract

- [x] 1.1 Replace `apply_changes` with explicit `mode` values and add stage-aware response models
- [x] 1.2 Keep `before_date` validation while updating result semantics for search-only scans

## 2. IMAP and service behavior

- [x] 2.1 Keep IMAP `BEFORE` criteria support and make mailbox access mode-aware for `search`, `classify`, and `clean`
- [x] 2.2 Add classifier availability gating and clean-mode failure handling before mailbox mutation

## 3. UI and documentation

- [x] 3.1 Replace the apply checkbox with explicit mode selection and compact table rendering
- [x] 3.2 Update OpenSpec capability docs to reflect explicit scan modes and compact review UI

## 4. Verification

- [x] 4.1 Update automated tests for API, service, IMAP, configuration, classifier, and UI assertions
- [x] 4.2 Run lint and test checks successfully
