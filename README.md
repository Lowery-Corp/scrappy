# Scrappy

Scrappy is a full-stack document workspace for uploading user files, tracking their processing state, and using ready documents as context in AI-assisted chat conversations. The app is currently under active development, but the main user-facing flows are in place: authenticated access, a file store, document chat, admin-oriented metadata endpoints, and an About landing page that explains the product and structure.

## Current App Status

### User Experience
- The app now lands on the About page after login and when clicking the authenticated Scrappy brand link.
- Unknown frontend routes redirect to `/about`.
- The top navigation groups the app links beside the Scrappy brand, with the user account action on the right.
- `Welcome, {username}` is a clickable button that routes to the landing page.
- The standalone Home page is no longer used by the router; `/` and `/home` render About.

### File Store
- Users can upload files into a protected file store.
- Files are stored in MinIO-compatible object storage using a per-user bucket naming pattern.
- File metadata is stored in PostgreSQL in `app.user_file`.
- Folder/bucket structure is stored in `app.user_filestore`.
- If a user loads the file store and does not yet have a file store record, the backend now creates the bucket/store record and returns an empty structure instead of failing the page load.
- The file store page shows persisted file metadata including status and size.
- File statuses render as colored badges:
  - `uploaded`: blue
  - `processing`: amber
  - `ready`: green
  - `error`: red
  - unknown statuses: gray

### Document Chat
- Users can create and revisit document chat conversations.
- The chat file sidebar only shows files with status `ready`.
- The sidebar still filters selectable files to PDFs.
- Conversations can retain selected file IDs as relevant context.
- Streaming chat message support exists through the frontend conversation services and backend conversation endpoints.

### Backend and Processing
- FastAPI exposes REST routes under `/api/v1`.
- Authentication is delegated to an external auth API and stored in HTTP-only cookies.
- File uploads create `UserFile` metadata, sync the user bucket structure, create a file job, and enqueue ingestion work when the queue is available.
- File jobs, chunks, conversations, messages, query logs, and retrieval logs are modeled in the backend.
- Redis support is present for backend caching.
- Celery/offload task publishing support exists for document ingestion workflows.

## Architecture

The repository is split into two application services plus supporting infrastructure:

- **scrappysHouse** - React frontend built with Vite, React Router, Tailwind CSS, and Axios.
- **scrappysScrapyard** - FastAPI backend using SQLAlchemy, PostgreSQL, Redis, MinIO-compatible object storage, and Alembic migrations.

## Features

### Frontend (`scrappysHouse`)
- React 19 UI with route-based pages.
- Protected routes for authenticated views.
- Role-aware admin navigation.
- About page as the product landing page.
- File store interface with drag-and-drop upload.
- File rows with status badges, file size, created date, and updated date.
- Document chat interface with conversation history.
- Chat file selector limited to ready PDF files.
- Responsive styling with Tailwind CSS and dark-mode classes.

### Backend (`scrappysScrapyard`)
- FastAPI async API service.
- SQLAlchemy ORM models and repositories.
- PostgreSQL persistence through AsyncPG.
- Alembic database migrations.
- Redis cache connection support.
- MinIO-compatible object storage integration.
- External authentication service integration.
- File metadata, file jobs, file chunks, and conversation APIs.
- Background/offload queue publishing support for document ingestion.
- Health check endpoints.

## Tech Stack

### Frontend
- React 19.2.4
- React Router 7.14.0
- Vite 8.0.1
- Tailwind CSS 4.2.2
- Axios 1.14.0

### Backend
- Python 3.14
- FastAPI 0.135.1
- Uvicorn 0.42.0
- SQLAlchemy 2.0.48
- AsyncPG 0.31.0
- Pydantic 2.12.5
- Alembic 1.18.4
- Redis client 7.4.0
- MinIO SDK 7.2.20
- HTTPX 0.28.1

### Infrastructure
- Docker and Docker Compose
- PostgreSQL 17 with pgvector image
- Redis
- External auth API when configured
- External/offload services when configured
- MinIO-compatible object storage when configured

## Getting Started

### Prerequisites
- Docker and Docker Compose
- Python 3.14+ for local backend development
- Node.js 20+ for local frontend development

### Environment Setup

Create a root `.env` for Docker Compose with PostgreSQL values:

```bash
POSTGRES_MAIN_USER=postgres
POSTGRES_MAIN_PASSWORD=postgres
POSTGRES_MAIN_DB=postgres
```

Create `scrappysHouse/.env` and point the frontend at the backend:

```bash
VITE_SCRAPPYS_SCRAPYARD_URL=http://localhost:8000
```

Create `scrappysScrapyard/.env` with backend settings. Important variables include:

```bash
database_url=postgresql+asyncpg://...
redis_url=redis://...
auth_api_url=http://...
offload_api_url=http://...
minio_api_url=http://...
minio_root_user=...
minio_root_password=...
minio_secure=false
internal_api_username=...
internal_api_password=...
```

### Running with Docker Compose

```bash
docker-compose up -d
```

Common local URLs:

- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:8000`
- API docs: `http://localhost:8000/docs`
- PostgreSQL: `localhost:5432`
- Redis: `localhost:6379`

Stop services:

```bash
docker-compose down
```

### Local Backend Development

```bash
cd scrappysScrapyard
pip install -r requirements.txt
alembic upgrade head
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Local Frontend Development

```bash
cd scrappysHouse
npm install
npm run dev
```

Build the frontend:

```bash
cd scrappysHouse
npm run build
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/login` - User login.
- `POST /api/v1/auth/logout` - User logout.
- `POST /api/v1/auth/register` - User registration plus initial user resources.
- `GET /api/v1/auth/me` - Current authenticated user.

### File Storage
- `GET /api/v1/blob` - Get the current user bucket structure and file metadata. Creates missing user file store resources when needed.
- `POST /api/v1/blob/sync` - Sync the stored bucket structure from object storage.
- `POST /api/v1/blob/upload` - Upload a file and create metadata/job records.
- `DELETE /api/v1/blob/delete` - Delete a file from object storage and metadata.
- `DELETE /api/v1/blob/bulk-delete` - Delete a folder path and mark matching metadata deleted.

### File Metadata
- `GET /api/v1/files` - List user file metadata. Non-admin users are scoped to their own files.
- `POST /api/v1/files` - Create file metadata. Admin-only.
- `GET /api/v1/files/{user_file_id}` - Read file metadata.
- `PATCH /api/v1/files/{user_file_id}` - Update file metadata.
- `DELETE /api/v1/files/{user_file_id}` - Delete file metadata.
- `GET /api/v1/files/file-id/{file_id}` - Look up file metadata by public file UUID.

Note: the file metadata routes currently have mixed naming around `user_file_id` and `file_id`. The model has an integer primary key `id` and a public UUID `file_id`; callers should verify the expected identifier before using these routes.

### File Jobs
- `GET /api/v1/file-jobs` / `POST /api/v1/file-jobs` - List or create file jobs.
- `GET /api/v1/file-jobs/{job_id}` - Read a file job.
- `PATCH /api/v1/file-jobs/{job_id}` - Update a file job.
- `DELETE /api/v1/file-jobs/{job_id}` - Delete a file job.

### File Chunks
- `GET /api/v1/file-chunks` / `POST /api/v1/file-chunks` - List or create file chunks.
- `GET /api/v1/file-chunks/{file_chunk_id}` - Read a file chunk.
- `PATCH /api/v1/file-chunks/{file_chunk_id}` - Update a file chunk.
- `DELETE /api/v1/file-chunks/{file_chunk_id}` - Delete a file chunk.

### Conversations
- `GET /api/v1/conversations` / `POST /api/v1/conversations` - List or create conversations.
- `GET /api/v1/conversations/{conversation_id}` - Read a conversation.
- `PATCH /api/v1/conversations/{conversation_id}` - Update a conversation.
- `DELETE /api/v1/conversations/{conversation_id}` - Delete a conversation.
- `GET /api/v1/conversations/{conversation_id}/messages` - List conversation messages.
- `POST /api/v1/conversations/{conversation_id}/messages` - Create a message.
- `POST /api/v1/conversations/{conversation_id}/files/{file_id}` - Add or remove a relevant file for a conversation.

### Health Checks
- `GET /api/v1/health` - Basic health check.
- `GET /api/v1/health/ready` - Readiness check.
- `GET /api/v1/health/live` - Liveness check.

## Database Schema

Main PostgreSQL tables include:

- `app.user_filestore` - Per-user file store bucket and structure metadata.
- `app.user_file` - Uploaded file metadata including storage key, size, MIME type, and processing status.
- `app.file_job` - File processing job metadata.
- `app.file_chunk` - Parsed/chunked document text and embedding status.
- `app.user_conversation` - User conversation records.
- `app.conversation_message` - Conversation messages.
- `app.agent_query_log` - Agent query logging.
- `app.retrieval_log` - Retrieval logging.

Migrations live in `scrappysScrapyard/alembic/`.

## Project Structure

```text
scrappy/
├── scrappysHouse/          # React frontend
│   ├── src/
│   │   ├── auth/           # Auth provider and session handling
│   │   ├── components/     # Shared and feature UI components
│   │   ├── layouts/        # Route layout components
│   │   ├── pages/          # Page-level views
│   │   └── services/       # Axios API wrappers
├── scrappysScrapyard/      # FastAPI backend
│   ├── api/                # API routers and endpoint modules
│   ├── auth/               # Auth dependencies
│   ├── cache/              # Redis helpers and lifecycle
│   ├── core/               # Settings and retry helpers
│   ├── db/                 # Database base/session/dependencies
│   ├── models/             # SQLAlchemy models
│   ├── repositories/       # Data access and external integrations
│   ├── schemas/            # Pydantic request/response schemas
│   ├── offload_tasks/      # Celery app/task queue configuration
│   └── alembic/            # Database migrations
└── docker-compose.yaml     # Local frontend, backend, Postgres, and Redis stack
```

## Known Gaps and Notes

- The app is still under active development.
- MinIO-compatible object storage is required by the file store, but a MinIO container is not currently defined in `docker-compose.yaml`.
- External auth and offload APIs must be configured for the full production-like workflow.
- File metadata identifier naming should be cleaned up so UUID and integer-ID routes are explicit.
- Folder creation and rename behavior in the UI is still mostly client-side and may need backend persistence work.

## License

MIT License - see `LICENSE` for details.
