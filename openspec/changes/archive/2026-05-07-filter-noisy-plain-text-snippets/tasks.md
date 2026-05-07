## 1. Snippet source selection

- [x] 1.1 Update `_build_snippet` to filter individual `text/plain` parts using the agreed noisy marker list before choosing the snippet source
- [x] 1.2 Preserve readable HTML-to-text fallback for the user-visible snippet when no clean plain-text parts remain

## 2. Classifier input preparation

- [x] 2.1 Update the classifier input path to convert selected HTML fallback content to Markdown using an existing Python library
- [x] 2.2 Keep plain-text classifier input unchanged when a clean plain-text part is selected

## 3. Verification

- [x] 3.1 Add or update tests for clean plain text, mixed clean/noisy plain text, readable HTML snippet fallback, Markdown classifier fallback, and case-insensitive marker matching
- [x] 3.2 Run the relevant test and lint checks and update this task list to reflect completed work
