## Context

The repository already documents `python -m email_cleaner` as the supported local startup path and already ignores `.vscode/` and `.venv/`. The requested change is intentionally narrow: provide a convenient local debug configuration while keeping editor and tool state out of git, and make `.opencode/` explicitly ignored at the repo root.

## Goals / Non-Goals

**Goals:**
- Add a local VS Code launch configuration that runs the supported app entrypoint.
- Keep the launch configuration untracked by Git.
- Ensure `.opencode/` and `.venv/` are ignored at the repository level.

**Non-Goals:**
- Share VS Code settings through version control.
- Introduce `.env`-file based debug configuration.
- Change runtime behavior, app startup code, or documentation beyond what is necessary for local debug convenience.

## Decisions

### 1. Use `python -m email_cleaner` as the debug target
- **Decision:** The launch config runs the supported module entrypoint rather than Flask CLI.
- **Why:** This preserves the app's fixed-host startup behavior and matches existing docs.
- **Alternative considered:** `flask run`. Rejected because it can bypass the supported host-binding path.

### 2. Keep `.vscode/` ignored
- **Decision:** The launch file is created for local use only and remains gitignored.
- **Why:** The user explicitly chose a local-only configuration.
- **Alternative considered:** Commit `.vscode/launch.json`. Rejected because it conflicts with the desired ignore behavior.

### 3. Add explicit `.opencode/` ignore coverage
- **Decision:** Add `.opencode/` to the root `.gitignore` even though some internal ignore files may already exist under it.
- **Why:** Root-level ignore intent should be obvious and complete.
- **Alternative considered:** Rely on nested ignore files. Rejected because it is less explicit.

## Risks / Trade-offs

- **[Local-only launch config is not shared]** → Acceptable by design; this change optimizes the current developer's environment only.
- **[Ignored `.vscode/` can hide future shareable editor config]** → A later change can unignore selected files if the team decides to share them.

## Migration Plan

Create `.vscode/launch.json` locally, update `.gitignore`, and verify that the debug config points at the supported module entrypoint.

## Open Questions

- None.
