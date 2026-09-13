# Knowledge Assistant

A production-oriented Knowledge Assistant backend built with **Django, Django REST Framework, PostgreSQL, and Docker**.

The goal of this project is to build a backend that allows users to upload documents and, eventually, ask questions about their content using **Retrieval-Augmented Generation (RAG)**.

The project is being developed incrementally with an emphasis on:

- Clean domain-based architecture
- Secure authentication and authorization
- REST API design
- Database-backed document management
- Automated testing
- Containerization
- API documentation
- Code quality and repository hygiene
- Production-oriented engineering practices

---

# Project Status

🚧 **Phase 1 — Backend Foundation: Complete**

🚧 **Phase 2 — REST API & Authentication: Complete**

🚧 **Phase 3 — Document CRUD API: Complete**

The backend foundation, JWT authentication, document management API, ownership isolation, pagination, automated tests, OpenAPI documentation, Docker, and PostgreSQL integration have been implemented and verified.

The next milestone is:

**Phase 4 — RAG Pipeline**

The target architecture and folder structure for Phase 4 have been designed and are documented below, ahead of implementation, so the RAG pipeline can be built without restructuring the existing apps.

---

# Tech Stack

## Currently Implemented

### Backend

- Python
- Django
- Django REST Framework

### Database

- PostgreSQL

### Infrastructure

- Docker
- Docker Compose

### Configuration

- django-environ

### Authentication

- `djangorestframework-simplejwt` — JWT authentication

### Testing

- pytest
- pytest-django

### API Documentation

- drf-spectacular — OpenAPI / Swagger documentation

### Code Quality

- Black — Python formatting
- Ruff — Python linting

### Development

- Git
- GitHub

---

## Planned Technologies

### Phase 4 — RAG Pipeline

- FastAPI — new `ai_service` microservice for embeddings and LLM calls
- pgvector — Postgres extension for vector storage and similarity search
- sentence-transformers — local embedding generation
- Ollama — local LLM serving for generation
- Document text extraction (PDF, TXT, DOCX)
- Text chunking
- Vector similarity search
- Retrieval-Augmented Generation

### Phase 5 — Knowledge Assistant

- Question-answering API
- Conversation history
- Chat API

### Phase 6 — Production Engineering & CI/CD

- Background processing
- Redis
- Celery
- Caching
- Rate limiting
- Structured logging
- Health checks
- Observability
- Performance optimization
- CI/CD
- Production deployment

---

# Architecture

## Current Architecture

```text
                    Knowledge Assistant
                           │
                           ▼
                    Django Backend
                           │
                    ┌──────┴──────┐
                    │             │
                    ▼             ▼
               PostgreSQL     File Storage

```

The application is containerized using Docker Compose:

```text
                      Docker Compose
                           │
                    ┌──────┴──────┐
                    │             │
                    ▼             ▼
             Django Container  PostgreSQL Container
                 web:8000            db:5432

```

The Django application communicates with PostgreSQL through the Docker Compose network.

## Planned Architecture — Phase 4 (RAG Pipeline)

```text
                     Client request
                           │
                           ▼
                    Django Backend (web)
                     Auth, documents, rag app
                           │
                    ┌──────┴──────┐
                    │             │
                    ▼             ▼
              AI Service     PostgreSQL + pgvector
              (FastAPI)       Vector similarity search
              Embedding +
              LLM calls
                    │
                    ▼
                 Ollama
              (local LLM)

```

Design notes:

- The Django backend continues to own auth, document storage, and ownership — the new `rag` app is added alongside `documents` rather than folded into it.
- All embedding generation and LLM calls are isolated in a separate `ai_service` (FastAPI), so ML dependencies (`sentence-transformers`, the Ollama client) never need to be installed in the Django container.
- PostgreSQL gains the `pgvector` extension for storing and querying embeddings — no separate vector database is introduced.
- Document processing (chunking → embedding → storage) is implemented as a plain callable (`rag/pipeline.py`) rather than tied directly to a request or a background task, so it can be wrapped in a Celery task in Phase 6 without restructuring.

---

# Project Structure

```text
Knowledge-Assistant/
│
├── backend/
│   │
│   ├── accounts/
│   │   ├── migrations/
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   ├── views.py
│   │   └── tests/
│   │       └── test_auth.py
│   │
│   ├── documents/
│   │   ├── migrations/
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── tests/
│   │       └── test_documents.py
│   │
│   ├── rag/                        # planned — Phase 4
│   │   ├── migrations/
│   │   ├── pipeline.py             # process_document(document_id) — chunk, embed, store
│   │   ├── chunking.py             # text splitting strategy
│   │   ├── parsers.py              # per-filetype text extraction
│   │   ├── retrieval.py            # pgvector similarity search
│   │   ├── ai_client.py            # HTTP client wrapping calls to ai_service
│   │   ├── serializers.py          # QuerySerializer
│   │   ├── views.py                # QueryView
│   │   ├── urls.py
│   │   └── tests/
│   │       └── test_pipeline.py    # mocks ai_client
│   │
│   ├── chat/
│   │   ├── migrations/
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   └── views.py
│   │
│   ├── config/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── asgi.py
│   │   └── wsgi.py
│   │
│   ├── manage.py
│   ├── Dockerfile
│   ├── requirements.txt
│   └── pytest.ini
│
├── ai_service/                      # planned — Phase 4
│   ├── main.py                     # /embed and /generate endpoints
│   ├── embeddings.py                # sentence-transformers wrapper
│   ├── llm.py                       # Ollama client wrapper
│   ├── schemas.py                   # pydantic request/response models
│   ├── requirements.txt
│   └── Dockerfile
│
├── .env.example
├── .gitignore
├── CONTRIBUTING.md
├── LICENSE
├── docker-compose.yml
├── ruff.toml
└── README.md

```

---

# Application Responsibilities

## `accounts`

Responsible for user-related functionality.

Current functionality includes:

- User registration
- JWT authentication
- Token refresh
- Authentication permissions
- Password hashing
- Password validation
- Authentication tests

## `documents`

Responsible for document-related functionality.

Currently contains:

- `Document`
- `DocumentChunk`
- Document REST API
- Document upload
- Document listing
- Document retrieval
- Document update
- Document deletion
- Owner-based access control
- File validation
- Pagination

## `rag` (planned — Phase 4)

Responsible for turning uploaded documents into retrievable, embedded chunks, and answering questions against them.

Will contain:

- Document text extraction (`parsers.py`)
- Text chunking (`chunking.py`)
- The document processing pipeline (`pipeline.py`) — called synchronously from `documents` on upload, designed to be wrapped in a Celery task later without changes to its own logic
- A thin HTTP client (`ai_client.py`) — the only module permitted to make real network calls to `ai_service`, so tests can mock it directly
- Vector similarity search against `DocumentChunk` (`retrieval.py`)
- A question-answering endpoint (`views.py`) that retrieves relevant chunks and returns a generated answer with source references

`rag` depends on `documents` for the `Document` and `DocumentChunk` models. It does not depend on `chat`.

## `chat`

Reserved for future conversational and Knowledge Assistant functionality (Phase 5).

Will depend on `rag` for retrieval and generation, and add conversation/session state on top of it, rather than duplicating retrieval logic.

---

# Database Design

The current database relationship is:

```text
                    User
                      │
                      │ 1
                      │
                      ▼
                  Document
                      │
                      │ 1:N
                      │
                      ▼
                DocumentChunk

```

## Document

A `Document` represents a file uploaded by a user.

Current fields:

| Field Description |                                |
| ----------------- | ------------------------------ |
| `id`              | Primary key                    |
| `title`           | Document title                 |
| `file`            | Uploaded file                  |
| `owner`           | User who owns the document     |
| `uploaded_at`     | Time the document was uploaded |
| `status`          | Current processing state       |

Document status currently supports:

- Uploading
- Processing
- Ready
- Failed

## DocumentChunk

A `DocumentChunk` represents a section of a document.

Current fields:

| Field Description |                                   |
| ----------------- | --------------------------------- |
| `id`              | Primary key                       |
| `document`        | Parent document                   |
| `text`            | Extracted chunk text              |
| `embedding`       | Placeholder for future embeddings |
| `created_at`      | Chunk creation time               |

The `embedding` field is intentionally left empty at this stage.

**Planned change (Phase 4):** `embedding` will migrate from `JSONField` to a `VectorField` (via the `pgvector` Django package), and the `db` service's image will move from `postgres:16` to `pgvector/pgvector:pg16` so the `vector` extension is available. This is a schema change made deliberately early in Phase 4, before real embedding data exists, to avoid a harder migration later.

---

# Environment Configuration

Environment-specific configuration is stored in `.env`.

The `.env` file is intentionally excluded from Git.

A template is provided through:

```text
.env.example

```

Create your local environment file:

```bash
cp .env.example .env

```

Example configuration:

```env
SECRET_KEY=replace-with-a-secure-secret-key
DEBUG=True

DB_NAME=knowledge_assistant
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432

POSTGRES_DB=knowledge_assistant
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres

```

### Configuration Roles

The `DB_*` variables are used by Django.

The `POSTGRES_*` variables are used by the official PostgreSQL Docker image.

Both sets should contain matching database credentials.

### Planned additions (Phase 4)

```env
AI_SERVICE_URL=http://ai_service:8001
OLLAMA_MODEL=llama3.1:8b
EMBEDDING_MODEL_NAME=all-MiniLM-L6-v2

```

- `AI_SERVICE_URL` — used by `rag/ai_client.py` to reach the `ai_service` container over the Docker Compose network
- `OLLAMA_MODEL` — the model `ai_service` requests from Ollama for generation
- `EMBEDDING_MODEL_NAME` — the `sentence-transformers` model used for embedding generation

### Important

Never commit the actual `.env` file or production secrets to Git.

For production, use a strong secret key and secure credentials rather than the development values shown above.

---

# Running the Project

## Prerequisites

Make sure the following are installed:

- Git
- Docker
- Docker Compose

Verify Docker:

```bash
docker --version

```

Verify Docker Compose:

```bash
docker compose version

```

---

## 1. Clone the Repository

```bash
git clone <repository-url>
cd Knowledge-Assistant

```

Replace `<repository-url>` with the actual GitHub repository URL.

---

## 2. Create the Environment File

```bash
cp .env.example .env

```

Update `.env` with your local configuration if necessary.

---

## 3. Build and Start the Application

```bash
docker compose up --build

```

This builds the Django image and starts:

- Django
- PostgreSQL

For detached mode:

```bash
docker compose up -d --build

```

Check the running containers:

```bash
docker compose ps

```

Expected services:

```text
knowledge_assistant_web
knowledge_assistant_db

```

_(Phase 4 will add_ _`ai_service`_ _and_ _`ollama`_ _to this list — see Planned Architecture above.)_

---

# Database Setup

Apply the existing migrations:

```bash
docker compose exec web python manage.py migrate

```

Migration files are part of the source code and should be committed to Git.

If models have changed and new migrations are required:

```bash
docker compose exec web python manage.py makemigrations

```

Then apply them:

```bash
docker compose exec web python manage.py migrate

```

---

# Creating an Admin User

Create a Django superuser:

```bash
docker compose exec web python manage.py createsuperuser

```

Follow the prompts to create the administrator account.

---

# Django Admin

Once the application is running, open:

```text
http://127.0.0.1:8000/admin/

```

The Django Admin currently provides access to:

- Users
- Groups
- Documents
- Document Chunks

---

# REST API

The current API provides JWT authentication and document management.

## Authentication Endpoints

```text
/api/auth/token/
/api/auth/token/refresh/
/api/auth/register/

```

### Login

```text
POST /api/auth/token/

```

Returns an access token and refresh token.

### Refresh Token

```text
POST /api/auth/token/refresh/

```

Returns a new access token.

### Registration

```text
POST /api/auth/register/

```

Creates a new user account.

---

# Document API

The document API provides CRUD functionality:

```text
/api/documents/
/api/documents/{id}/

```

Supported operations include:

- Upload
- List
- Retrieve
- Update
- Delete

Documents are scoped to the authenticated user.

A user can only access documents that they own.

The owner is assigned server-side and cannot be supplied or modified through the serializer.

---

# Document Validation

Uploaded documents are validated before creation.

Supported file types:

- PDF
- TXT
- DOCX

Maximum file size:

```text
10 MB

```

Invalid file extensions and oversized files are rejected by the API.

---

# Pagination

The document list API uses page-number pagination.

Default page size:

```text
10

```

Example:

```text
GET /api/documents/?page=2

```

The API returns:

- Total count
- Next page
- Previous page
- Results

---

# API Documentation

The project uses `drf-spectacular` to generate an OpenAPI schema.

## OpenAPI Schema

```text
http://127.0.0.1:8000/api/schema/

```

## Swagger UI

```text
http://127.0.0.1:8000/api/docs/

```

Swagger UI can be used to explore and interact with the available API endpoints.

---

# Document Storage

Uploaded documents are stored under:

```text
backend/
└── media/
    └── documents/

```

The `media/` directory is excluded from Git.

This prevents locally uploaded documents from being accidentally committed to the repository.

---

# Testing

The project uses `pytest` and `pytest-django` for automated testing.

Run the complete test suite inside the Docker container:

```bash
docker compose exec web pytest

```

The test suite currently covers areas including:

- User registration
- Duplicate username registration
- JWT authentication
- Token refresh
- Invalid authentication
- Missing authentication
- Document creation
- Document listing
- Document ownership
- Ownership isolation
- Document validation
- Pagination

Tests are expected to pass against the PostgreSQL database used by the Docker environment.

**Planned (Phase 4):** `rag` app tests will mock `ai_client` rather than making real calls to `ai_service` or Ollama, so the suite stays fast and does not depend on a model server being available.

---

# Code Quality

The project uses **Black** for formatting and **Ruff** for linting.

## Black

Check formatting:

```bash
docker compose exec web black --check .

```

Format the project:

```bash
docker compose exec web black .

```

## Ruff

Run linting:

```bash
docker compose exec web ruff check .

```

Before submitting changes, make sure both checks pass.

---

# Development Checks

Run Django's system checks:

```bash
docker compose exec web python manage.py check

```

Check the configured database:

```bash
docker compose exec web python manage.py check --database default

```

---

# Stopping the Application

Stop the Django and PostgreSQL containers:

```bash
docker compose down

```

To start the application again:

```bash
docker compose up -d

```

PostgreSQL data is persisted using a Docker named volume.

### Important

Do not use:

```bash
docker compose down -v

```

unless you intentionally want to delete the PostgreSQL volume and its data.

---

# Git Repository Hygiene

The repository intentionally ignores development-specific files:

```text
.env
.venv/
venv/
__pycache__/
*.pyc
*.pyo
*.sqlite3
db.sqlite3
backend/media/
media/
staticfiles/
.vscode/
.idea/
*.log
.DS_Store

```

The following should remain tracked:

```text
.env.example
.gitignore
Dockerfile
docker-compose.yml
requirements.txt
ruff.toml
pytest.ini
README.md
CONTRIBUTING.md
LICENSE
Django source code
Django migration files

```

Development databases, environment files, Python cache files, logs, and uploaded media should never be committed.

---

# Development Workflow

The intended development workflow is:

```text
Modify code
    │
    ▼
Run code-quality checks
    │
    ▼
Run Django checks
    │
    ▼
Create migrations if models changed
    │
    ▼
Apply migrations
    │
    ▼
Run tests
    │
    ▼
Update documentation
    │
    ▼
Review git diff
    │
    ▼
Commit changes

```

Example:

```bash
docker compose exec web black --check .
docker compose exec web ruff check .
docker compose exec web python manage.py check
docker compose exec web python manage.py migrate
docker compose exec web pytest
git diff --check
git status

```

---

# Development Roadmap

## Phase 1 — Backend Foundation

**Status: ✅ Complete**

- [x] Django project setup
- [x] Domain-based application structure
- [x] `accounts` application
- [x] `documents` application
- [x] `chat` application
- [x] PostgreSQL configuration
- [x] Docker environment
- [x] Docker Compose
- [x] Environment variable configuration
- [x] `.gitignore`
- [x] `Document` model
- [x] `DocumentChunk` model
- [x] Document processing status
- [x] Database migrations
- [x] Django → PostgreSQL integration
- [x] Django Admin
- [x] Basic repository documentation

---

# Phase 2 — REST API & Authentication

**Status: ✅ Complete**

## Week 2 — DRF + JWT Authentication

Completed:

- [x] Install and configure Django REST Framework
- [x] Install `djangorestframework-simplejwt`
- [x] Configure JWT authentication
- [x] Configure access-token lifetime
- [x] Configure refresh-token lifetime
- [x] Login endpoint
- [x] Refresh-token endpoint
- [x] Registration endpoint
- [x] Authentication permissions
- [x] `AllowAny` for public authentication endpoints
- [x] Password hashing
- [x] Password validation
- [x] Authentication tests
- [x] `pytest-django` setup
- [x] Invalid and missing-token tests
- [x] Duplicate-registration tests

The authentication flow follows:

```text
Register
   │
   ▼
Login
   │
   ▼
Access Token + Refresh Token
   │
   ▼
Protected API
   │
   ▼
Refresh Access Token

```

---

# Phase 3 — Document CRUD API

**Status: ✅ Complete**

## Week 3 — Document REST API

Completed:

- [x] `DocumentSerializer`
- [x] `DocumentViewSet`
- [x] Document upload
- [x] Document listing
- [x] Document retrieval
- [x] Document update
- [x] Document deletion
- [x] Owner-based queryset filtering
- [x] Server-side owner assignment
- [x] File extension validation
- [x] File size validation
- [x] Pagination
- [x] API error handling
- [x] Ownership isolation tests
- [x] OpenAPI schema
- [x] Swagger UI
- [x] End-to-end API testing

Current API structure:

```text
/api/auth/token/
/api/auth/token/refresh/
/api/auth/register/

/api/documents/
/api/documents/{id}/

```

Document ownership is enforced server-side.

The intended security model is:

```text
User A
  │
  ├── Document A
  └── Document B

User B
  │
  └── Document C

User B cannot access Document A or B.

```

---

# Phase 4 — RAG Pipeline

**Status: 🔜 Upcoming — architecture and folder structure designed**

The target architecture, new applications, and folder structure for this phase are documented above under **Planned Architecture — Phase 4**, **Project Structure**, and **Application Responsibilities**, decided ahead of implementation to avoid restructuring mid-phase.

## Week 5 — Infrastructure

- [ ] Switch `db` image to `pgvector/pgvector:pg16`
- [ ] Migration enabling the `vector` extension
- [ ] Migrate `DocumentChunk.embedding` from `JSONField` to `VectorField`
- [ ] Scaffold `ai_service/` (FastAPI + Dockerfile)
- [ ] Add `ai_service` to `docker-compose.yml`
- [ ] Add `ollama` service to `docker-compose.yml`, pull a starting model
- [ ] Add `AI_SERVICE_URL`, `OLLAMA_MODEL`, `EMBEDDING_MODEL_NAME` to `.env.example`

## Week 6 — Ingestion Pipeline

- [ ] `rag/parsers.py` — text extraction per file type (PDF, TXT, DOCX)
- [ ] `rag/chunking.py` — chunking strategy
- [ ] `ai_service` `/embed` endpoint (sentence-transformers)
- [ ] `rag/ai_client.py`
- [ ] `rag/pipeline.py` — `process_document(document_id)`
- [ ] Wire `process_document` into the document upload flow
- [ ] Tests for parsing, chunking, and the pipeline, with `ai_client` mocked

## Week 7 — Retrieval + Generation

- [ ] `ai_service` `/generate` endpoint (Ollama wrapper)
- [ ] `rag/retrieval.py` — pgvector similarity search
- [ ] `rag/views.py` — `QueryView`, serializer, and urls
- [ ] Manual end-to-end pass: upload a document → ask a question → grounded answer
- [ ] Automated tests for retrieval and the query endpoint

## Week 8 — Polish and Release

- [ ] Update API docs to reflect the new query endpoint
- [ ] Update README and milestones for Phase 4 completion
- [ ] Full clean `docker compose up --build` verification with the new services
- [ ] Tag and release `v0.5`

## Planned Technologies

- pgvector
- Ollama
- sentence-transformers
- FastAPI

---

# Phase 5 — Knowledge Assistant

**Status: 🔜 Planned**

Planned:

- [ ] Question-answering API
- [ ] Retrieval-Augmented Generation
- [ ] Relevant document retrieval
- [ ] Context construction
- [ ] LLM integration
- [ ] Source/reference information
- [ ] Conversation history
- [ ] Chat API

Expected high-level flow:

```text
User Question
      │
      ▼
Question Processing
      │
      ▼
Vector Search
      │
      ▼
Relevant Document Chunks
      │
      ▼
Context Construction
      │
      ▼
LLM
      │
      ▼
Grounded Answer

```

---

# Phase 6 — Production Engineering & CI/CD

**Status: 🔜 Planned**

Planned:

- [ ] Expanded unit test coverage
- [ ] API integration tests
- [ ] Authentication tests
- [ ] Ownership/security tests
- [ ] GitHub Actions
- [ ] Continuous Integration
- [ ] Background processing
- [ ] Redis
- [ ] Celery
- [ ] Caching
- [ ] Rate limiting
- [ ] Structured logging
- [ ] Health checks
- [ ] Observability
- [ ] Performance optimization
- [ ] Production deployment

---

# Milestones

| Version | Milestone                                               | Status   |
| ------- | ------------------------------------------------------- | -------- |
| v0.1    | Initial Project Foundation                              | Complete |
| v0.2    | JWT Authentication                                      | Complete |
| v0.3    | Document CRUD API                                       | Complete |
| v0.4    | Repository Hygiene, Documentation & Release Preparation | Complete |
| v0.5    | RAG Pipeline                                            | Planned  |
| v0.6    | Knowledge Assistant                                     | Planned  |

---

# Contributing

Contributions, suggestions, bug reports, and improvements are welcome.

Please read [`CONTRIBUTING.md`](CONTRIBUTING.md) for:

- Local development setup
- Branching conventions
- Code style
- Testing requirements
- Pull request expectations

Before submitting a change:

1. Create a branch for your work.
2. Make focused changes.
3. Run Black.
4. Run Ruff.
5. Run the test suite.
6. Update documentation when necessary.
7. Submit a pull request describing the change.

---

# License

This project is licensed under the **MIT License**.

See the [`LICENSE`](LICENSE) file for the complete license text.

---

# Project Philosophy

This project is intentionally being developed in phases rather than attempting to build the entire Knowledge Assistant at once.

The focus is on establishing a reliable backend foundation first:

```text
Django
   │
   ▼
REST API
   │
   ▼
Authentication
   │
   ▼
Document Management
   │
   ▼
PostgreSQL
   │
   ▼
RAG Pipeline
   │
   ▼
Knowledge Assistant
   │
   ▼
Production Engineering
```
