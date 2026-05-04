## Why

The API contract treats `since_date` as optional, but an empty UI field currently still triggers validation failure because blank date input is not normalized correctly. The documented default port also still refers to the old value in a few places, which makes local setup inconsistent with the current config.

## What Changes

- Normalize an empty `since_date` request value so leaving the field blank behaves as an optional filter.
- Keep the existing requirement that at least one real search criterion must be supplied.
- Update remaining references to the new default server port `38452`.

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `email-scan-review`: Clarify optional `since_date` input behavior so blank UI submission does not fail validation, while preserving the existing search-criteria requirement.
- `local-web-ui`: Update user-facing documentation/examples to reflect the current default port.

## Impact

- Request validation for scan input.
- Tests and documentation that mention the default server port.
