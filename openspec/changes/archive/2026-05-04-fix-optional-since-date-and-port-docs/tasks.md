## 1. Scan request validation

- [x] 1.1 Update scan request validation so an empty `since_date` value is normalized to `None` instead of causing a date-parsing error
- [x] 1.2 Add or update tests covering blank `since_date` alongside the existing “at least one search criterion” rule

## 2. Port reference cleanup

- [x] 2.1 Update remaining project documentation and tests that still refer to the old default port `5000` so they match `38452`

## 3. Verification

- [x] 3.1 Run the relevant test and lint checks and update the change task list to reflect completed work
