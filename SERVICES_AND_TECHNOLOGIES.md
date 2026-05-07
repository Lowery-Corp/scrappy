# Services and Technologies Overview

This is a high-level view of the current services, infrastructure, and major technologies used in this project.

## System Overview

Scrappy is a full-stack web application made of:

- A React frontend for the user interface.
- A FastAPI backend for API logic.
- PostgreSQL for persistent application data.
- Redis for caching.
- Docker Compose for local service orchestration.

## Services

| Service | Location | Technology | Purpose |
| --- | --- | --- | --- |
| Frontend | `scrappysHouse` | React, Vite, Tailwind CSS | Web UI for users, authentication screens, admin screens, and file store views |
| Backend API | `scrappysScrapyard` | FastAPI, Python, Uvicorn | REST API, authentication flow, file metadata, file jobs, health checks |
| Database | `postgres` Docker service | PostgreSQL 17 with pgvector | Stores users, file metadata, jobs, logs, conversations, and vector-related data |
| Cache | `db-cache` Docker service | Redis | Caching layer used by the backend |

## Frontend Stack

The frontend is located in `scrappysHouse`.

Main technologies:

- React `19.2.4`
- React Router `7.14.0`
- Vite `8.0.1`
- Tailwind CSS `4.2.2`
- Axios `1.14.0`
- ESLint `9.39.4`
- Node `20` in Docker

Primary responsibilities:

- User login and account creation pages.
- Protected routes for authenticated users.
- Admin route gated by permissions.
- File store interface.
- API communication with the backend through Axios.

## Backend Stack

The backend is located in `scrappysScrapyard`.

Main technologies:

- Python `3.14`
- FastAPI `0.135.1`
- Uvicorn `0.42.0`
- SQLAlchemy `2.0.48`
- AsyncPG `0.31.0`
- Alembic `1.18.4`
- Pydantic `2.12.5`
- Redis client `7.4.0`
- HTTPX `0.28.1`
- MinIO SDK `7.2.20`
- PyJWT `2.12.1`
- Argon2 password tooling

Primary responsibilities:

- API routing under `/api/v1`.
- Authentication endpoints.
- Health checks.
- Blob and file store endpoints.
- File job endpoints.
- Database access through repositories and SQLAlchemy models.
- Database migrations through Alembic.
- Redis connection lifecycle.
- External service communication through HTTPX.

## Infrastructure

Infrastructure is currently managed with `docker-compose.yaml`.

Active Compose services:

- `scrappys-house`
- `scrappys-scrapyard`
- `postgres`
- `db-cache`

Exposed local ports:

- Frontend: `5173`
- Backend API: `8000`
- PostgreSQL: `5432`
- Redis: `6379`

Docker images and runtimes:

- Frontend uses `node:20-alpine`.
- Backend uses `python:3.14-slim`.
- Database uses `pgvector/pgvector:pg17`.
- Cache uses `redis:latest`.

## Data Layer

PostgreSQL is the main persistent data store.

Current backend models indicate support for:

- Users
- User file storage
- File jobs
- File chunks
- Query logs
- Retrieval logs
- User conversations
- Conversation messages
- JWT token blacklist entries

Alembic is used for schema migrations.

## External or Related Services

The backend configuration references services that are not currently defined as active Docker Compose services:

- External authentication API through `auth_api_url`.
- Offload API through `offload_api_url`.
- MinIO-compatible object storage through `minio_api_url`.

MinIO support exists in backend dependencies and repository code, but there is no MinIO container currently defined in `docker-compose.yaml`.

RabbitMQ is mentioned by a declared Docker volume, but there is no active RabbitMQ service currently defined in `docker-compose.yaml`.

## Configuration

Configuration is environment-based.

Files used by Compose:

- Root `.env` for shared infrastructure values like PostgreSQL credentials.
- `scrappysHouse/.env` for frontend environment variables.
- `scrappysScrapyard/.env` for backend environment variables.

Important frontend variable:

- `VITE_SCRAPPYS_SCRAPYARD_URL`

Important backend variables:

- `database_url`
- `redis_url`
- `auth_api_url`
- `offload_api_url`
- `minio_api_url`
- `minio_root_user`
- `minio_root_password`
- `minio_secure`
- `internal_api_username`
- `internal_api_password`

## High-Level Request Flow

1. A user opens the React frontend on port `5173`.
2. The frontend sends API requests to the FastAPI backend.
3. The backend handles authentication, file store operations, jobs, and health checks.
4. The backend stores persistent data in PostgreSQL.
5. The backend uses Redis for cache-related operations.
6. The backend can communicate with external auth, offload, and object-storage services when configured.

