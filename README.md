# Scrappy - Full Stack Application

A modern full-stack application with React frontend and FastAPI backend, featuring user authentication, file storage, document chat, and document metadata management capabilities.

## Architecture

This project consists of two main components:

- **scrappysHouse** - React frontend with Vite
- **scrappysScrapyard** - FastAPI backend with PostgreSQL

## Features

### Frontend (scrappysHouse)
- Modern React 19 with hooks and context
- React Router for navigation
- Tailwind CSS for styling
- User authentication with protected routes
- Role-based access control
- File store interface with drag & drop upload
- Document chat interface with conversation history
- Responsive design with dark mode support

### Backend (scrappysScrapyard)
- FastAPI with async/await support
- PostgreSQL database with SQLAlchemy ORM
- Redis caching layer
- MinIO object storage integration
- JWT authentication via external auth service
- RESTful API endpoints for auth, blob storage, file metadata, file jobs, file chunks, and conversations
- Celery task publishing support for document ingestion/offload workflows
- Database migrations with Alembic
- Health check endpoints

## Tech Stack

### Frontend
- React 19.2.4
- React Router 7.14.0
- Tailwind CSS 4.2.2
- Axios for API calls
- Vite for build tooling

### Backend
- FastAPI 0.135.1
- SQLAlchemy 2.0.48 (async)
- PostgreSQL with AsyncPG
- Redis for caching
- MinIO for object storage
- Pydantic for data validation
- Alembic for database migrations

### Infrastructure
- Docker & Docker Compose
- PostgreSQL 17
- Redis
- RabbitMQ-compatible Celery broker support when configured

## Getting Started

### Prerequisites
- Docker and Docker Compose
- Python 3.14+ (for local development)
- Node.js 20+ (for local development)

### Environment Setup

1. Copy the backend environment template:
```bash
cp scrappysScrapyard/.env.example scrappysScrapyard/.env
```

2. Create a root `.env` for Docker Compose with the Postgres variables used by `docker-compose.yaml`:
```bash
POSTGRES_MAIN_USER=postgres
POSTGRES_MAIN_PASSWORD=postgres
POSTGRES_MAIN_DB=postgres
```

3. Create `scrappysHouse/.env` if needed and set the backend URL for Vite:
```bash
VITE_SCRAPPYS_SCRAPYARD_URL=http://localhost:8000
```

4. Update the environment variables with your local configuration.

### Running with Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

Services will be available at:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- PostgreSQL: localhost:5432
- Redis: localhost:6379

### Local Development

#### Backend Setup
```bash
cd scrappysScrapyard
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start development server
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup
```bash
cd scrappysHouse
npm install
npm run dev
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/logout` - User logout
- `POST /api/v1/auth/register` - User registration
- `GET /api/v1/auth/me` - Get current user

### File Storage
- `GET /api/v1/blob` - Get user's bucket structure
- `POST /api/v1/blob/sync` - Sync bucket structure
- `POST /api/v1/blob/upload` - Upload a file into the bucket structure
- `DELETE /api/v1/blob/delete` - Delete a file from the bucket structure
- `DELETE /api/v1/blob/bulk-delete` - Delete a folder and its files from the bucket structure

### File Metadata Admin
- `GET /api/v1/files` / `POST /api/v1/files` - List or create user file metadata
- `GET /api/v1/files/{user_file_id}` / `PATCH /api/v1/files/{user_file_id}` / `DELETE /api/v1/files/{user_file_id}` - Read, update, or delete user file metadata
- `GET /api/v1/files/file-id/{file_id}` - Look up user file metadata by file UUID

### File Jobs Admin
- `GET /api/v1/file-jobs` / `POST /api/v1/file-jobs` - List or create file jobs
- `GET /api/v1/file-jobs/{job_id}` / `PATCH /api/v1/file-jobs/{job_id}` / `DELETE /api/v1/file-jobs/{job_id}` - Read, update, or delete file jobs

### File Chunks Admin
- `GET /api/v1/file-chunks` / `POST /api/v1/file-chunks` - List or create file chunks
- `GET /api/v1/file-chunks/{file_chunk_id}` / `PATCH /api/v1/file-chunks/{file_chunk_id}` / `DELETE /api/v1/file-chunks/{file_chunk_id}` - Read, update, or delete file chunks

### Conversations
- `GET /api/v1/conversations` / `POST /api/v1/conversations` - List or create user conversations
- `GET /api/v1/conversations/{conversation_id}` / `PATCH /api/v1/conversations/{conversation_id}` / `DELETE /api/v1/conversations/{conversation_id}` - Read, update, or delete a conversation
- `GET /api/v1/conversations/{conversation_id}/messages` / `POST /api/v1/conversations/{conversation_id}/messages` - List or create conversation messages
- `GET /api/v1/conversations/{conversation_id}/messages/{message_id}` / `PATCH /api/v1/conversations/{conversation_id}/messages/{message_id}` / `DELETE /api/v1/conversations/{conversation_id}/messages/{message_id}` - Read, update, or delete a conversation message

### Health Checks
- `GET /api/v1/health` - Basic health check
- `GET /api/v1/health/ready` - Readiness probe
- `GET /api/v1/health/live` - Liveness probe

## Database Schema

The application uses PostgreSQL with the following main tables:
- `app.user_filestore` - User file storage structure metadata
- `app.user_file` - Uploaded file metadata
- `app.file_job` - File processing job metadata
- `app.file_chunk` - Chunked document text and embedding status
- `app.user_conversation` - User conversation records
- `app.conversation_message` - Conversation message records
- `app.agent_query_log` and `app.retrieval_log` - Query and retrieval logging

Database migrations are managed with Alembic in the `alembic/` directory.

## Authentication Flow

The application uses an external authentication service. Users authenticate through the backend API which communicates with the auth service to validate credentials and manage sessions using HTTP-only cookies.

## File Storage

Files are stored in MinIO object storage with a bucket per user. The application maintains metadata about file structure and uploaded files in PostgreSQL and provides a web interface for file management.

## Development

### Project Structure
```
scrappy/
├── scrappysHouse/          # React frontend
│   ├── src/
│   │   ├── components/     # Reusable and feature components, including file store and document chat
│   │   ├── pages/          # Page components
│   │   ├── auth/           # Authentication logic
│   │   ├── services/       # API service calls
│   │   └── layouts/        # Layout components
├── scrappysScrapyard/      # FastAPI backend
│   ├── api/                # API routes
│   ├── auth/               # Authentication dependencies
│   ├── cache/              # Redis caching
│   ├── core/               # Configuration
│   ├── db/                 # Database setup
│   ├── models/             # SQLAlchemy models
│   ├── repositories/       # Data access and integration layer
│   ├── schemas/            # Pydantic schemas
│   ├── offload_tasks/      # Celery application configuration
│   └── alembic/            # Database migrations
└── docker-compose.yaml     # Local frontend, backend, Postgres, and Redis stack
```

## License

MIT License - see LICENSE file for details.