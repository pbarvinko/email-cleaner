## Context

The repository now has a Python/Flask application and pytest-based tests, but it still lacks a root `.gitignore` and any standardized linting configuration. This change is intentionally small and developer-facing: add baseline repository hygiene and a light Python linter without introducing formatting churn or broader tooling complexity.

## Goals / Non-Goals

**Goals:**
- Prevent common local, virtualenv, cache, packaging, and secret files from being committed accidentally.
- Add Ruff as the default Python linter for local development.
- Keep the Ruff setup minimal and focused on high-value checks.
- Document the lint command alongside existing install/run/test instructions.

**Non-Goals:**
- Introduce an autoformatter.
- Reformat the codebase extensively.
- Add CI workflows, pre-commit hooks, or multiple lint tools.
- Change runtime behavior of the application.

## Decisions

### 1. Add a root `.gitignore` tailored to this Python repo
- **Decision:** Ignore virtualenvs, Python caches, pytest/Ruff caches, packaging outputs, local environment files, and common OS/editor noise.
- **Why:** These are the most likely accidental commits in this project and can be excluded with a single simple file.
- **Alternative considered:** Ignore only currently observed artifacts. Rejected because it would miss obvious near-term files like `.ruff_cache/` and build outputs.

### 2. Use Ruff as the only linter in v1
- **Decision:** Add Ruff to dev dependencies and configure it in `pyproject.toml`.
- **Why:** Ruff is fast, covers core linting needs with minimal config, and avoids layering multiple tools.
- **Alternative considered:** Add Flake8 plus isort plus pyupgrade. Rejected because Ruff subsumes the needed baseline checks with less maintenance.

### 3. Keep the initial Ruff rule set narrow
- **Decision:** Enable default linting plus import sorting and a small upgrade-oriented rule set, but avoid formatter adoption and large style-only churn.
- **Why:** This keeps the change low-risk and likely to pass quickly while still improving quality.
- **Alternative considered:** Enable a broad strict profile. Rejected because it could force unrelated refactors.

### 4. Document only the essential developer commands
- **Decision:** Update `README.md` with a single lint command alongside existing install and test instructions.
- **Why:** The repo is simple; extra tooling documentation would be noise.
- **Alternative considered:** Separate contributor guide. Rejected as unnecessary at current repo size.

## Risks / Trade-offs

- **[Ruff flags existing code issues]** → Keep the rule set modest and fix only the violations introduced by the selected rules.
- **[Ignoring `.env` could hide a desired sample file]** → Ignore `.env`-style runtime files but continue to allow explicit checked-in examples such as `.env.example` if added later.
- **[No CI enforcement yet]** → Document the lint command now; CI can be added later as a separate change if needed.

## Migration Plan

No runtime migration is required. After the change, developers reinstall dev dependencies if needed and can run Ruff locally.

## Open Questions

- None.
