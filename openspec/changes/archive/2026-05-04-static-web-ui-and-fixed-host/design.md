## Context

The current application already follows an API-driven interaction model in the browser, but the root page is still rendered from a Flask template and server host binding remains configurable. For this app, a static frontend served by Flask is simpler than mixing server-side templating with client-side API calls, and a fixed bind host removes one non-essential runtime setting.

## Goals / Non-Goals

**Goals:**
- Serve the web UI as static files from the Python package rather than through Jinja templates.
- Keep the browser/backend boundary clean: the UI loads static assets and talks to the backend only via `/api/...`.
- Remove the `SERVER_HOST` setting and standardize host binding to `0.0.0.0`.
- Minimize behavioral change beyond asset serving and runtime configuration simplification.

**Non-Goals:**
- Redesign the UI workflow or classification behavior.
- Introduce a separate frontend build toolchain.
- Change API endpoints or mailbox/classification logic.
- Add client-side routing or a multi-page frontend.

## Decisions

### 1. Move the frontend into `email_cleaner/web/`
- **Decision:** Store `index.html`, JavaScript, and CSS together under `email_cleaner/web/` and serve them as package static assets.
- **Why:** This makes the frontend a clearly static, self-contained client instead of a template plus separate static files.
- **Alternative considered:** Keep using `templates/` with Jinja. Rejected because the UI does not need server-side rendering.

### 2. Serve `/` by returning the static `index.html`
- **Decision:** Flask should serve the web bundle root document directly from the static web directory.
- **Why:** This preserves the current root URL while removing template rendering.
- **Alternative considered:** Introduce a new `/web/` prefix. Rejected because it adds user-visible churn without value.

### 3. Remove `SERVER_HOST` and bind to `0.0.0.0`
- **Decision:** Host binding is no longer configurable; startup and docs should assume `0.0.0.0`.
- **Why:** The user explicitly requested a fixed bind address, and host configuration is not core application behavior.
- **Alternative considered:** Keep configurability with a different default. Rejected because it preserves unnecessary configuration surface.

### 4. Keep all server data injection out of the HTML
- **Decision:** Any values the UI needs at runtime should come from API responses or browser defaults, not Jinja interpolation.
- **Why:** This enforces a clean static-frontend/API separation.
- **Alternative considered:** Generate a small inline config blob at render time. Rejected because it would reintroduce template coupling.

## Risks / Trade-offs

- **[Static UI loses easy server-side value injection]** → Keep the UI independent of server-rendered config and derive defaults from HTML or API-compatible client behavior.
- **[Binding to `0.0.0.0` increases network exposure]** → Document the resulting local URL usage clearly; this change follows explicit user direction.
- **[Frontend asset paths can break after relocation]** → Keep the structure flat and add tests for the root document and asset serving if practical.

## Migration Plan

Move the existing HTML, CSS, and JavaScript into `email_cleaner/web/`, update Flask app setup to serve that directory statically, remove the host setting from config/docs/tests, and verify that `/` still loads and `/api/...` behavior remains unchanged.

## Open Questions

- None.
