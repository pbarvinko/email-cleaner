## Context

The current classifier prompt asks for concise JSON but does not explicitly forbid common wrapper formats like Markdown fences or explanatory text. Since the runtime currently expects direct `json.loads` on the returned text, even otherwise valid JSON can fail when wrapped. The requested scope is to tighten the prompt contract first rather than adding tolerant parsing.

## Goals / Non-Goals

**Goals:**
- Make the expected classifier output format explicit and narrow.
- Reduce parse failures caused by fenced JSON or surrounding prose.
- Keep the change local to prompt wording and tests.

**Non-Goals:**
- Add parser tolerance for malformed or wrapped model output.
- Change the label schema or classification logic.
- Introduce tool-calling or structured-output SDK features.

## Decisions

### 1. Require exactly one raw JSON object
- **Decision:** The prompt will explicitly require exactly one raw JSON object and nothing else.
- **Why:** This matches the current parser contract exactly.
- **Alternative considered:** Ask for JSON more generally. Rejected because the current wording already allows too much ambiguity.

### 2. Explicitly forbid common failure wrappers
- **Decision:** The prompt will explicitly forbid tool calls, prose, explanations, and Markdown code fences.
- **Why:** These are the observed and likely wrapper forms that break parsing.
- **Alternative considered:** Only add a positive instruction. Rejected because negative constraints are useful when the model tends to wrap answers.

### 3. Include a concrete JSON example
- **Decision:** Add a minimal example such as `{"label":"move","reason":"Short explanation here"}` directly in the prompt rules.
- **Why:** An exact example reduces formatting drift while staying aligned with the existing response schema.
- **Alternative considered:** Rely on schema description alone. Rejected because the user explicitly asked for an example and it likely improves compliance.

## Risks / Trade-offs

- **[The model may still occasionally ignore instructions]** → Accept for this change; if failures persist, add a follow-up hardening change in parsing.
- **[An example with `move` could bias label choice]** → Keep the allowed labels listed separately and use a neutral short reason in the example.

## Migration Plan

Update the prompt strings and the classifier prompt tests together. No data migration or API migration is required.

## Open Questions

- None.
