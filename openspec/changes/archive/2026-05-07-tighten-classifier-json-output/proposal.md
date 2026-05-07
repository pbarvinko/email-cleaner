## Why

The classifier sometimes returns JSON wrapped in Markdown code fences or extra prose, which causes JSON parsing failures and downgrades classification to `uncertain`. Tightening the prompt contract is the smallest first fix because it addresses the model instruction directly without broadening parsing logic.

## What Changes

- Strengthen the classifier prompt so it demands exactly one raw JSON object and nothing else.
- Explicitly forbid tool calls, prose, explanations, and Markdown code fences in classifier output.
- Add a concrete one-line JSON example to anchor the required response shape.
- Update tests to verify the prompt contains the stricter output instructions.

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `email-classification`: Tighten the classifier response contract so model output must be a single unfenced raw JSON object matching the expected label/reason schema.

## Impact

- `email_cleaner/classifier.py` prompt construction.
- Classifier tests asserting prompt contents.
- Model-output reliability for downstream JSON parsing.
