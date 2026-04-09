# Scrappy - Full Stack Application

A modern full-stack application with React frontend and FastAPI backend, featuring user authentication, file storage, and document management capabilities.

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
- Responsive design with dark mode support

### Backend (scrappysScrapyard)
- FastAPI with async/await support
- PostgreSQL database with SQLAlchemy ORM
- Redis caching layer
- MinIO object storage integration
- JWT authentication via external auth service
- RESTful API endpoints
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
- RabbitMQ 4

## Getting Started

### Prerequisites
- Docker and Docker Compose
- Python 3.14+ (for local development)
- Node.js 20+ (for local development)

### Environment Setup

1. Copy environment files:
```bash
cp scrappysScrapyard/.env.example scrappysScrapyard/.env
cp .env.example .env
```

2. Update the environment variables in both files with your configuration.

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
- RabbitMQ Management: http://localhost:15672

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

### Health Checks
- `GET /api/v1/health` - Basic health check
- `GET /api/v1/health/ready` - Readiness probe
- `GET /api/v1/health/live` - Liveness probe

## Database Schema

The application uses PostgreSQL with the following main tables:
- `app.user_filestore` - User file storage metadata

Database migrations are managed with Alembic in the `alembic/` directory.

## Authentication Flow

The application uses an external authentication service. Users authenticate through the backend API which communicates with the auth service to validate credentials and manage sessions using HTTP-only cookies.

## File Storage

Files are stored in MinIO object storage with a bucket per user. The application maintains metadata about file structure in PostgreSQL and provides a web interface for file management.

## Development

### Project Structure
```
scrappy/
├── scrappysHouse/          # React frontend
│   ├── src/
│   │   ├── components/     # Reusable components
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
│   ├── repositories/       # Data access layer
│   ├── schemas/            # Pydantic schemas
│   └── alembic/            # Database migrations
└── conveyor/               # Message queue utilities
```

## License

MIT License - see LICENSE file for details.