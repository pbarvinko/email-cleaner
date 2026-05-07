## 1. Prompt contract update

- [x] 1.1 Update the classifier prompt rules to require exactly one raw JSON object and nothing else
- [x] 1.2 Explicitly forbid tool calls, explanations, prose, and Markdown code fences in classifier output
- [x] 1.3 Add a concrete example JSON object showing the exact required output shape

## 2. Verification

- [x] 2.1 Update classifier tests to assert the stricter prompt contract and example JSON
- [x] 2.2 Run the relevant test and lint checks and update this task list to reflect completed work
