# App Structure Blueprint

This repository is a full-stack app organized as two primary applications plus local infrastructure:

- `scrappysHouse/`: React/Vite frontend.
- `scrappysScrapyard/`: FastAPI backend.
- `docker-compose.yaml`: local multi-service runtime for frontend, backend, Postgres, and Redis.
- `postgres/`: Postgres initialization mount used by Docker Compose when present.

Use this document as the structural blueprint when creating new apps with the same architecture.

## Root Layout

```text
scrappy/
├── APP_STRUCTURE_BLUEPRINT.md
├── README.md
├── LICENSE
├── docker-compose.yaml
├── scrappysHouse/
├── postgres/
└── scrappysScrapyard/
```

### Root Files And Directories

| Path | Purpose |
| --- | --- |
| `README.md` | Human-facing overview, setup instructions, service URLs, and high-level feature list. |
| `LICENSE` | Project license. |
| `.env` | Root infrastructure environment variables used by Docker Compose, especially Postgres settings. Do not commit secrets in real projects. |
| `.gitignore` | Repository ignore rules. |
| `docker-compose.yaml` | Defines the local development stack and wires the frontend, backend, database, and cache together. |
| `postgres/` | Active Postgres initialization mount used by `docker-compose.yaml`. |
| `.venv/` | Local Python virtual environment. This is development state, not part of the app blueprint. |
| `scrappysHouse/` | Frontend application. |
| `scrappysScrapyard/` | Backend application. |

## Runtime Architecture

The app uses a browser frontend, an API backend, and supporting infrastructure.

```text
Browser
  |
  v
scrappysHouse React app
  |
  v
scrappysScrapyard FastAPI API
  |
  +--> PostgreSQL with pgvector
  +--> Redis cache
  +--> Celery/offload task publisher when configured
  +--> OpenAI Responses/Conversations API through the OpenAI repository
  +--> External/object storage integrations through repository/client modules
```

Docker Compose services:

| Service | Purpose | Port |
| --- | --- | --- |
| `scrappys-house` | Vite React frontend dev server. | `5173` |
| `scrappys-scrapyard` | FastAPI backend served by Uvicorn. | `8000` |
| `postgres` | PostgreSQL 17 with pgvector support. | `5432` |
| `db-cache` | Redis cache. | `6379` |
| `rabbitmq_data` volume | Declared volume reserved for queue/broker data; no RabbitMQ service is currently active in `docker-compose.yaml`. | n/a |

## Frontend: `scrappysHouse/`

```text
scrappysHouse/
├── Dockerfile
├── index.html
├── package.json
├── package-lock.json
├── vite.config.js
├── eslint.config.js
├── public/
└── src/
```

### Frontend Root Files

| Path | Purpose |
| --- | --- |
| `package.json` | Frontend package metadata, scripts, and dependencies. Scripts include `dev`, `build`, `lint`, and `preview`. |
| `package-lock.json` | Locked npm dependency graph. |
| `Dockerfile` | Container image definition for the frontend service. |
| `index.html` | Vite HTML entry point. |
| `vite.config.js` | Vite configuration, including React and Tailwind integration. |
| `eslint.config.js` | ESLint configuration. |
| `public/` | Static files served directly by Vite, such as icons and favicons. |

### Frontend Source Layout

```text
scrappysHouse/src/
├── main.jsx
├── App.jsx
├── App.css
├── index.css
├── assets/
├── auth/
├── components/
├── layouts/
├── pages/
└── services/
```

| Path | Purpose |
| --- | --- |
| `src/main.jsx` | React bootstrap file. Mounts the app into the DOM and wraps it with top-level providers. |
| `src/App.jsx` | Main application shell. Defines navigation and route structure. |
| `src/App.css` | App-specific styles. |
| `src/index.css` | Global CSS and Tailwind entry styles. |
| `src/assets/` | Frontend-managed static assets imported by React components. |
| `src/auth/` | Authentication context and auth state management. |
| `src/components/` | Reusable UI and workflow components. |
| `src/layouts/` | Route layout components for grouped pages. |
| `src/pages/` | Route-level page components. |
| `src/services/` | Browser-side API clients and service wrappers, including Axios JSON calls and fetch-based chat streaming helpers. |

### Frontend Routing Pattern

Routes are declared in `src/App.jsx`.

| Route Area | Purpose |
| --- | --- |
| `/user/login` | Login page under `UserLayout`. |
| `/user/create` | User creation page under `UserLayout`. |
| `/auth/admin` | Admin page under `AuthLayout`, protected by `read:admin`. |
| `/about` | Public about page. |
| `/`, `/home` | Authenticated home page. |
| `/store` | Authenticated file store page. |
| `/chat/:conversationId?` | Authenticated document chat page. Optional conversation id selects an existing chat; `/chat/new` starts a new chat. |
| `*` | Not found page. |

Protected routes are handled through `src/components/ProtectedRoute.jsx`, using auth state from `src/auth/AuthProvider.jsx`.

### Frontend Component Organization

`src/components/fileStoreComs/` contains file-store-specific components:

| Component | Purpose |
| --- | --- |
| `FileStoreHeader.jsx` | Header controls for the file store view. |
| `FileDisplay.jsx` | Displays files/folders in the file store. |
| `CreateFolder.jsx` | Folder creation UI. |
| `NewFolderButton.jsx` | Trigger for folder creation. |
| `UploadFileButton.jsx` | File upload trigger. |
| `UploadProgress.jsx` | Upload progress display. |
| `FileRename.jsx` | File rename UI. |
| `SyncBlobButton.jsx` | Sync action for blob/file metadata. |

`src/components/documentChat/` contains document-chat-specific components:

| Component | Purpose |
| --- | --- |
| `ChatPanelHeader.jsx` | Header and controls for the active chat panel. |
| `ChatSidebar.jsx` | Conversation list and selection controls. |
| `ChatThread.jsx` | Message thread display, including streamed/pending agent response state. |
| `ChatComposer.jsx` | Message input and send workflow. Plain Enter submits; Shift+Enter keeps textarea newline behavior. |


Document chat frontend behavior:

- `src/pages/DocumentChat.jsx` owns chat state, optimistic message insertion, active conversation routing, and stream event handling.
- New and existing chat sends append the user message immediately and show a pending agent bubble while the backend streams text deltas.
- The final streamed agent message replaces the pending bubble after the backend persists it.
- `src/services/user_conversations.jsx` keeps standard JSON API helpers and adds fetch-based streaming helpers for Server-Sent Event responses.

For new apps using this structure:

- Put route screens in `src/pages/`.
- Put reusable route wrappers in `src/layouts/`.
- Put app-wide state providers in a domain directory such as `src/auth/`.
- Put API and integration calls in `src/services/`.
- Create feature subdirectories under `src/components/` when a feature has several related components.

## Backend: `scrappysScrapyard/`

```text
scrappysScrapyard/
├── Dockerfile
├── requirements.txt
├── alembic.ini
├── main.py
├── api/
├── auth/
├── cache/
├── core/
├── db/
├── httpxC/
├── middleware/
├── models/
├── offload_tasks/
├── repositories/
├── schemas/
└── alembic/
```

### Backend Root Files

| Path | Purpose |
| --- | --- |
| `main.py` | FastAPI application entry point. Creates the app, registers middleware, manages lifespan startup/shutdown, connects Redis, closes HTTP clients, and mounts the API router at `/api/v1`. |
| `requirements.txt` | Python dependency list. |
| `Dockerfile` | Container image definition for the backend API service. |
| `alembic.ini` | Alembic configuration. |
| `__init__.py` | Marks the backend as a Python package. |

### Backend Source Directories

| Path | Purpose |
| --- | --- |
| `api/` | API router composition and versioned endpoint modules. |
| `auth/` | Authentication dependencies used by endpoints and protected routes. |
| `cache/` | Redis connection management, cache dependencies, and helper functions. |
| `core/` | App configuration, retry utilities, and other cross-cutting core helpers. |
| `db/` | Database engine/session setup and FastAPI database dependencies. |
| `httpxC/` | Shared HTTP client wrapper for outbound HTTP calls. |
| `middleware/` | Custom request middleware, currently request ID handling. |
| `models/` | SQLAlchemy ORM models. |
| `offload_tasks/` | Celery application configuration for publishing/handling background offload tasks when a broker and worker are configured. |
| `repositories/` | Data access and integration layer for database records, auth, MinIO, file store, OpenAI, offload tasks, and token blacklist operations. |
| `schemas/` | Pydantic schemas for request/response validation. |
| `alembic/` | Database migration environment and migration versions. |

### Backend API Pattern

The backend uses versioned routing:

```text
api/
└── v1/
    ├── api.py
    └── endpoints/
        ├── auth.py
        ├── blob.py
        ├── file_chunks.py
        ├── file_jobs.py
        ├── health.py
        ├── user_conversations.py
        └── user_files.py
```

`api/v1/api.py` creates the version router and includes feature routers:

| Router | Prefix | Purpose |
| --- | --- | --- |
| `auth.router` | `/api/v1/auth` | Login, logout, registration, and current-user behavior. |
| `health.router` | `/api/v1/health` | Basic, readiness, and liveness health checks. |
| `blob.router` | `/api/v1/blob` | User file/blob store operations, upload, delete, bulk delete, and sync behavior. |
| `file_chunks.router` | `/api/v1/file-chunks` | Admin-only file chunk CRUD and filtering. |
| `file_jobs.router` | `/api/v1/file-jobs` | Admin-only file job CRUD and filtering. |
| `user_files.router` | `/api/v1/files` | Admin-only user file metadata CRUD and lookup. |
| `user_conversations.router` | `/api/v1/conversations` | Authenticated user conversations, nested conversation messages, and chat streaming endpoints. |


Conversation API conventions:

- JSON endpoints remain available for standard conversation and message CRUD.
- Streaming endpoints live beside the existing conversation routes:
  - `POST /api/v1/conversations/stream` creates a conversation and streams the first agent response.
  - `POST /api/v1/conversations/{conversation_id}/messages/stream` creates a user message and streams the agent response.
- Streaming responses use Server-Sent Events with small event payloads such as `conversation`, `user_message`, `delta`, `message`, `error`, and `done`.
- Endpoint functions stay thin: they create user records, translate repository errors into HTTP/SSE errors, and delegate OpenAI work to repositories.

For new apps using this structure:

- Add new endpoint files under `api/v1/endpoints/`.
- Register them in `api/v1/api.py`.
- Keep endpoint functions thin: validate input, call dependencies/repositories, and return schemas.
- Put database access in `repositories/`, not directly in route handlers.
- Put request/response contracts in `schemas/`.
- Put database tables in `models/`.
- Add migrations under `alembic/versions/` for model-backed schema changes.

### Backend Data Layer Pattern

```text
Endpoint
  |
  v
Dependency modules
  |
  v
Repository
  |
  v
Database / Redis / object storage / external service
```

Directory responsibilities:

| Layer | Directory | Rule Of Thumb |
| --- | --- | --- |
| API routing | `api/v1/endpoints/` | HTTP-specific behavior, request parsing, response codes. |
| Dependencies | `auth/`, `db/`, `cache/` | FastAPI dependency functions and shared resource access. |
| Business/data access | `repositories/` | Query and integration logic. |
| Persistence models | `models/` | SQLAlchemy table definitions and relationships. |
| Data contracts | `schemas/` | Pydantic request and response models. |
| Migrations | `alembic/versions/` | Incremental database schema changes. |


Conversation repository conventions:

- `repositories/user_conversation.py` owns conversation/message persistence, dynamic conversation naming from the first user message, and saving completed agent messages.
- Conversation names are generated from normalized first-message text, truncated for sidebar display, with `New Conversation` as the empty-message fallback.
- Streaming document chat retrieves context per selected file: each `relevant_file_id` is queried separately and contributes up to five embedding-ranked chunks to the OpenAI instruction payload.
- `repositories/openai.py` owns OpenAI HTTP integration for conversations, non-streaming responses, streaming response parsing, and output text extraction.
- The repository layer bridges streamed OpenAI deltas to persisted `conversation_message` rows only after the final response is complete.

## Database And Migrations

The app uses PostgreSQL with SQLAlchemy and Alembic.

```text
scrappysScrapyard/alembic/
├── env.py
├── script.py.mako
├── README
└── versions/
```

Migration files in `alembic/versions/` define the database history, including users, user file stores, user files, file jobs, file chunks, conversations, messages, embeddings, and uniqueness constraints.

For new apps:

- Keep SQLAlchemy models in `scrappysScrapyard/models/`.
- Import models through the database metadata path used by Alembic.
- Generate one migration per schema change.
- Keep seed/init SQL limited to database extensions or bootstrap behavior in `postgres/init/`.

## Infrastructure Pattern

`docker-compose.yaml` is the local orchestration layer. It should remain the first place agents check when they need to understand service names, ports, volumes, and environment file expectations.

Important conventions:

- Frontend environment belongs in `scrappysHouse/.env`.
- Backend environment belongs in `scrappysScrapyard/.env`.
- Shared infrastructure environment belongs in root `.env`.
- Postgres data is stored in the named Docker volume `postgres_data_scrappys_metadata`.
- Redis data/cache volume is `db_redis_cache_scrappys_cache`.
- `rabbitmq_data` is declared, but no RabbitMQ service is currently active. Add a broker service before relying on Celery task publishing in the local stack.

## Naming Conventions

The current app uses project-specific names:

- `scrappysHouse`: frontend.
- `scrappysScrapyard`: backend.
- `scrappys-house`: frontend Docker Compose service.
- `scrappys-scrapyard`: backend Docker Compose service.

When creating a new app from this blueprint, preserve the roles but rename consistently:

| Current Name | New App Equivalent |
| --- | --- |
| `scrappysHouse` | `<appName>House` or `frontend` |
| `scrappysScrapyard` | `<appName>Scrapyard` or `backend` |
| `scrappys-house` | `<app-name>-frontend` |
| `scrappys-scrapyard` | `<app-name>-backend` |

Pick either themed names or generic names. Do not mix both in a new app.

## Agent Build Checklist

When using this as a blueprint for a new app, create the structure in this order:

1. Create root project files: `README.md`, `.gitignore`, `.env.example`, and `docker-compose.yaml`.
2. Create the frontend app directory with Vite, React, Tailwind, routing, layouts, pages, components, auth, and services.
3. Create the backend app directory with FastAPI, versioned routers, dependencies, repositories, models, schemas, middleware, cache, and database setup.
4. Add Dockerfiles for frontend and backend.
5. Add Postgres, Redis, and a queue/broker service to Compose only if the app actually needs them.
6. Add Alembic and an initial migration once backend models exist.
7. Keep feature code grouped by layer: pages/components on the frontend, endpoints/repositories/models/schemas on the backend.
8. Update the README with service URLs, setup commands, and the API surface.

## What To Avoid Carrying Forward

Do not copy generated or machine-local state into new apps:

- `node_modules/`
- `__pycache__/`
- `.venv/`
- Local `.env` files with secrets
- Docker volumes or database data directories

These should be recreated by package managers, Python tooling, or Docker during setup.

