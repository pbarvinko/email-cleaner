## Why

The current UI is server-rendered from a Flask template and the server host is configurable, which adds unnecessary coupling between backend rendering and frontend assets for this small API-driven app. Converting the UI into static files served by Flask and fixing the bind host to `0.0.0.0` simplifies the app structure and runtime behavior.

## What Changes

- Replace the templated root UI with a static web bundle under `email_cleaner/web/`.
- Serve the UI as static files from Flask, with the browser communicating with the backend only through `/api/...` endpoints.
- Remove the `SERVER_HOST` setting and bind the app to `0.0.0.0` consistently.
- Update documentation and config expectations to match the simplified serving model.

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `local-web-ui`: Change the UI delivery model from Flask templating to static-file serving, and remove configurable server-host behavior in favor of a fixed `0.0.0.0` bind host.

## Impact

- Flask app setup and root route behavior.
- Frontend file layout and asset serving.
- Runtime configuration and README instructions.
