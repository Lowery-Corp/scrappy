# Scrappy Code Review Issues

Review date: 2026-10-26

This file records the static review findings for the Scrappy application and tracks the repair pass. The implementation changes are in the source tree; this document remains the complete issue dump for audit/history.

## Repair status (2026-10-26)

The sequential repair pass resolved the correctness, authorization, storage-safety, async-blocking, response-contract, timestamp, streaming-terminal-event, persistence, environment-documentation, reproducibility, and hook-lint findings. Backend contract tests and a frontend test command were added, and a production Compose definition now separates the built frontend/no-reload runtime from the development stack.

Remaining follow-ups are operational rather than safe local code edits:

- Rotate any credentials that may have been exposed in local or historical `.env` files, then load replacements through a secret manager.
- Complete a centralized frontend transport/error policy if the service surface grows; current calls are functionally correct but some retain local logging.
- Add full integration coverage against real auth, MinIO, queue, and OpenAI services; the new tests intentionally avoid requiring those external dependencies.

## Highest-priority correctness and security issues

### 1. Registration uses the wrong endpoint and field names — Critical

The frontend posts registration to `/api/v1/users/create`, but the Scrappy backend exposes `/api/v1/auth/register`. The frontend route currently returns `404`.

- Frontend: `frontend/src/services/AuthService.jsx:14`
- Backend route: `backend/api/v1/endpoints/auth.py:72`

There is a second mismatch: `UserCreate` defines `username`, while the registration route accesses `new_user.email`. A valid request reaching the backend will fail with an attribute error.

- Schema: `backend/schemas/user.py:4`
- Route access: `backend/api/v1/endpoints/auth.py:74`

Recommended fix: use one route contract consistently, update the frontend to call `/api/v1/auth/register`, and use `new_user.username` or rename the schema field consistently.

### 2. Conversation routes convert an existing UUID incorrectly — Critical

`AuthorizedUser.id` is already a `uuid.UUID`, but many conversation routes call `uuid.UUID(current_user.id)`. This raises `AttributeError: 'UUID' object has no attribute 'replace'`.

- Example: `backend/api/v1/endpoints/user_conversations.py:98`
- Type declaration: `backend/schemas/user.py:46`

This affects conversation creation, message operations, conversation-file attachment, and message retrieval.

Recommended fix: pass `current_user.id` directly.

### 3. Non-streaming chat passes a mapping instead of an OpenAI conversation ID — Critical

`get_or_create_openai_conversation_id()` returns a mapping containing `openai_conversation_id`, but the caller passes the entire mapping into `create_openai_response()`.

- Mapping return: `backend/repositories/user_conversation.py:309`
- Incorrect call: `backend/repositories/user_conversation.py:364`

The file contains a TODO explicitly documenting this unresolved defect at `backend/repositories/user_conversation.py:401`.

Recommended fix: extract `openai_conversation_id = result["openai_conversation_id"]` and pass only that string.

### 4. Admin authorization is inconsistent and one route is broken — High

`require_admin_user()` expects a FastAPI `Request` and checks a static `api-key` header, but the file-job creation route passes an `AuthorizedUser` object directly.

- Dependency: `backend/auth/dependencies.py:7`
- Incorrect call: `backend/api/v1/endpoints/file_jobs.py:20`

The function also does not check `AuthorizedUser.is_admin`; it is an API-key check rather than an admin-user check.

Recommended fix: separate `require_api_key()` from `require_admin_user()`, then use explicit dependencies consistently and validate the authenticated user's role where appropriate.

### 5. Login and registration forms do not await asynchronous auth calls — High

Both forms call async auth methods and immediately inspect the returned Promise.

- Login: `frontend/src/pages/Login.jsx:15`
- Registration: `frontend/src/pages/CreateUser.jsx:17`

`result.ok` is read before the request resolves, causing incorrect error handling and premature loading-state changes.

Recommended fix: make the submit handlers `async` and await `login()` / `createUser()`.

### 6. Logout uses a different cookie name from login — High

Login and authentication use `settings.cookie_key`, while logout reads and deletes the literal `access_token` cookie.

- Login cookie: `backend/api/v1/endpoints/auth.py:26`
- Logout cookie: `backend/api/v1/endpoints/auth.py:56`

Logout may therefore leave the actual session cookie in the browser.

Recommended fix: use `settings.cookie_key` for reading, blacklisting, and deleting the cookie.

### 7. Cookie security is not environment-aware — Medium/High

The login route always sets `secure=True`:

- `backend/api/v1/endpoints/auth.py:30`

That can make local HTTP development and non-HTTPS deployments fail to persist the cookie. The setting should be environment-controlled, with production enforcing HTTPS.

### 8. File ownership validation is incomplete and bypassed — High

The ownership function checks whether a file ID appears in an existing conversation rather than checking `UserFile.user_id`. The actual check is commented out, and conversation creation accepts arbitrary file UUIDs.

- Placeholder ownership logic: `backend/repositories/user_conversation.py:204`
- Commented-out enforcement: `backend/repositories/user_conversation.py:229`
- Unvalidated IDs accepted during creation: `backend/repositories/user_conversation.py:68`
- Input schema: `backend/schemas/user_conversation.py:9`

This permits invalid or foreign file IDs to be attached to conversations and weakens the authorization boundary.

Recommended fix: validate every referenced file against `UserFile.user_id` before storing or retrieving it.

## Data integrity and performance issues

### 9. File chunk endpoint response types do not match repository return types — High

The API declares a single `FileChunkRead`, while the repository returns a list. The update route has the same mismatch.

- GET route: `backend/api/v1/endpoints/file_chunks.py:61`
- Repository return type: `backend/repositories/file_chunk.py:64`
- PATCH route: `backend/api/v1/endpoints/file_chunks.py:84`

These routes are likely to produce FastAPI response-validation errors.

Recommended fix: decide whether the operation returns one chunk or a collection and align the endpoint annotation, response model, repository return type, and not-found behavior.

### 10. Uploads load the entire file into memory — High

The upload path calls `await file.read()` before sending the content to object storage.

- `backend/repositories/filestore.py:114`
- `backend/repositories/filestore.py:117`

There are also no file-size limits, content validation, or robust filename/path sanitization.

Recommended fix: enforce upload limits, normalize path components, validate content types, and stream or chunk large uploads.

### 11. Synchronous MinIO operations run inside async handlers — High

The MinIO client is synchronous, but it is called directly from `async def` repository functions.

- `backend/repositories/minio.py:20`
- `backend/repositories/minio.py:53`

Object-storage operations can block the event loop and reduce API concurrency.

Recommended fix: use an async-compatible client or run blocking MinIO calls in a worker thread.

### 12. File upload workflow is not atomic — High

The file workflow performs object-storage upload, multiple database commits, metadata synchronization, job creation, and queue submission as separate operations.

- Object upload: `backend/repositories/filestore.py:117`
- Metadata commit: `backend/repositories/filestore.py:148`
- Job creation: `backend/repositories/filestore.py:160`

A failure halfway through can leave orphaned objects, database records, or jobs.

Recommended fix: use an explicit upload state machine, minimize transaction boundaries, and add compensating cleanup for external side effects.

### 13. Streaming can finish without a terminal event — Medium/High

The backend returns early when there are no relevant files or no OpenAI conversation ID, without emitting a `done` event.

- `backend/repositories/user_conversation.py:423`

The frontend clears its streaming state only on `done`, so a conversation can remain stuck in a streaming state.

Recommended fix: always emit a terminal success or error event and handle disconnects on both sides.

### 14. Database queries have an N+1 pattern for conversation previews — Medium

The conversation list performs one query for conversations and then an additional latest-message query for every conversation.

- `backend/repositories/user_conversation.py:113`
- `backend/repositories/user_conversation.py:130`

Recommended fix: use a joined/subquery-based latest-message query or batch-load previews.

### 15. Timestamp handling is inconsistent — Medium

Most models use timezone-aware UTC timestamps, while `UserFileStore` uses `datetime.utcnow`, which creates naive timestamps.

- `backend/models/user_filestore.py:31`
- `backend/models/user_filestore.py:37`

Recommended fix: use timezone-aware UTC timestamps consistently, such as `datetime.now(timezone.utc)`.

### 16. File status filtering is incomplete — Medium

`get_user_files()` returns records without excluding files marked `deleted`.

- `backend/repositories/user_file.py:21`

Deleted records may therefore appear in normal user-facing file listings.

Recommended fix: apply an explicit default status filter and expose deleted records only through an administrative/recovery path.

## Frontend behavior and state issues

### 17. Folder creation and rename are local-only — High

Folder creation and file/folder rename update React state but never call the backend.

- Folder creation: `frontend/src/pages/FileStore.jsx:224`
- Rename: `frontend/src/pages/FileStore.jsx:282`

All changes disappear after refresh.

Recommended fix: implement persistence endpoints and refresh state from the server after successful mutations.

### 18. Authenticated user state has an inconsistent shape — High

`AuthProvider` stores only a username string, but the application checks `user.permissions` for admin access.

- State assignment: `frontend/src/auth/AuthProvider.jsx:42`
- Permission helper: `frontend/src/auth/AuthProvider.jsx:114`
- Admin navigation: `frontend/src/App.jsx:69`

Admin navigation and permission checks will not work reliably.

Recommended fix: store the complete authenticated-user object, or make all consumers consistently use a username-only state plus a separate permissions field.

### 19. Streaming client parsing is fragile — Medium

`JSON.parse()` is called without a local error boundary for every streamed event.

- `frontend/src/services/user_conversations.jsx:21`

A malformed or partial event can terminate the chat stream unexpectedly.

Recommended fix: handle malformed event payloads explicitly and preserve partial stream state.

### 20. Frontend API calls duplicate error logging and transport setup — Low/Medium

Many service functions catch errors only to log and rethrow them, producing duplicated logs and scattered error policy.

- Example: `frontend/src/services/AuthService.jsx:3`
- Stream transport separately uses `fetch` instead of the shared Axios client: `frontend/src/services/user_conversations.jsx:81`

Recommended fix: centralize transport/error handling and use one authenticated client abstraction.

## Error handling and code quality

### 21. Broad exception handling masks programming errors — High

The login route converts every exception into a 401, including internal bugs. Registration catches every exception and returns a normal response containing an error message.

- Login: `backend/api/v1/endpoints/auth.py:23`
- Registration: `backend/api/v1/endpoints/auth.py:85`

Recommended fix: catch expected exceptions specifically, log unexpected failures, and return correct HTTP status codes.

### 22. Assertions are used for runtime validation — Medium/High

Assertions are used for object-storage failures, database state, and request operations.

- `backend/repositories/filestore.py:51`
- `backend/api/v1/endpoints/blob.py:55`

Assertions can be disabled with Python optimization and produce generic 500 responses.

Recommended fix: raise explicit domain exceptions and convert them to appropriate HTTP errors at the API boundary.

### 23. Debug `print()` calls remain in production paths — Medium

Examples include:

- `backend/api/v1/endpoints/auth.py:62`
- `backend/api/v1/endpoints/user_conversations.py:337`
- `backend/repositories/filestore.py:207`

Recommended fix: use structured logging with request IDs and appropriate log levels.

### 24. The code contains known unresolved TODOs and commented-out logic — Medium

The conversation repository contains a long TODO documenting broken behavior, and the file-store repository contains multiple disabled blocks.

- `backend/repositories/user_conversation.py:401`
- `backend/repositories/filestore.py:60`

Recommended fix: convert known defects into tracked issues/tests and remove dead code once behavior is settled.

### 25. Naming and typing are inconsistent — Low/Medium

Examples include `sync_bucket_structiure`, `newely_enqueued_task`, and `relivent_conversation`. File chunk code also uses `int` annotations for IDs that are UUIDs.

- Typing mismatch: `backend/repositories/file_chunk.py:30`
- Schema mismatch: `backend/schemas/file_chunk.py:14`

Recommended fix: run a type checker, standardize UUID types, and clean up naming before adding more features.

### 26. Mutable list default in a Pydantic schema — Low

`relevant_file_ids` uses a list literal as a default.

- `backend/schemas/user_conversation.py:11`

Recommended fix: use `Field(default_factory=list)`.

## Configuration and deployment issues

### 27. Configuration example is incomplete — Medium

The settings class requires many variables, but `.env.example` documents only `DATABASE_URL`.

- Required settings: `backend/core/config.py:4`
- Example file: `backend/.env.example:1`

New developers and deployments must guess required values and will fail at import time when variables are missing.

Recommended fix: document every required setting with safe placeholders and explain local versus production values.

### 28. Local environment contains real-looking credentials and API keys — High

The ignored local `.env` files contain credentials for external services and an OpenAI key. `.gitignore` helps prevent current tracking, but it does not protect against copying, logs, screenshots, or prior history.

Recommended fix: rotate credentials if they have been exposed, use a secret manager for deployment, and keep only placeholders in examples.

### 29. Development and production concerns are mixed — Medium

Compose runs Vite and Uvicorn with reload enabled, bind-mounts source code, and uses `restart: always`. The frontend image uses `npm install` rather than `npm ci`.

- Compose: `docker-compose.yaml:24`
- Frontend image: `frontend/Dockerfile:5`

Recommended fix: maintain separate development and production configurations, use deterministic dependency installation, and build a production frontend artifact.

### 30. Dependencies and images are not fully reproducible — Medium

The Compose file uses `redis:latest`, which can change without a code change.

- `docker-compose.yaml:63`

Recommended fix: pin image versions or digests and update them deliberately.

## Testing gaps

### 31. Backend coverage is effectively absent — Medium

There are no backend tests covering authentication, ownership, uploads, file jobs, or chat.

### 32. Frontend test coverage is minimal — Medium

Only a small About-page test exists, and the package has no test script.

- Test: `frontend/src/pages/About.test.js`
- Scripts: `frontend/package.json:6`

### 33. Existing lint warning indicates unstable hook dependencies — Low/Medium

`npm run lint` reports missing dependencies for `useMemo` in `AuthProvider`.

- `frontend/src/auth/AuthProvider.jsx:189`

Recommended fix: stabilize callback functions with `useCallback` or include the correct dependencies.

## Validation performed during review

- Frontend production build: passed.
- Python bytecode compilation: passed.
- Existing frontend test: passed.
- Frontend lint: one React hook dependency warning.
- `POST /api/v1/users/create`: returned `404`, confirming the registration route mismatch.
- `uuid.UUID(uuid.uuid4())`: raised `AttributeError`, confirming the conversation UUID conversion defect.

## Suggested repair order

1. Fix registration route/schema mismatches.
2. Remove incorrect UUID conversions.
3. Repair admin authorization dependencies.
4. Fix login/registration async form handling.
5. Fix cookie naming and environment-aware security flags.
6. Repair OpenAI conversation ID handling and streaming terminal events.
7. Enforce file ownership and upload limits.
8. Align file-chunk API response types.
9. Add backend integration tests for auth, files, jobs, and chat.
10. Separate development and production deployment configuration.
