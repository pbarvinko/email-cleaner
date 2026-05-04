## 1. Static web asset restructure

- [x] 1.1 Create an `email_cleaner/web/` directory for the frontend bundle and move the existing root UI HTML, JavaScript, and CSS into it as static assets
- [x] 1.2 Remove the Flask template-based root page and update the app to serve the static `index.html` and related assets from the new web directory

## 2. Fixed host binding and config cleanup

- [x] 2.1 Remove `SERVER_HOST` from runtime settings, docs, and any related tests
- [x] 2.2 Update the app startup path and documentation so the server binds to `0.0.0.0` instead of reading a configured host value

## 3. Verification

- [x] 3.1 Verify the browser UI still loads from `/` and communicates with the backend only through `/api/...`
- [x] 3.2 Run the relevant test suite and update tests as needed for the static-serving and config changes
