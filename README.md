# Knowledge Assistant

A production-oriented Knowledge Assistant backend built with **Django, Django REST Framework, PostgreSQL, and Docker**.

The goal of this project is to build a backend that allows users to upload documents and, eventually, ask questions about their content using **Retrieval-Augmented Generation (RAG)**.

The project is being developed incrementally with an emphasis on:

* Clean domain-based architecture
* Secure authentication and authorization
* REST API design
* Database-backed document management
* Automated testing
* Containerization
* API documentation
* Production-oriented engineering practices

---

## Project Status

🚧 **Phase 1 — Backend Foundation: Complete**

The initial backend foundation has been implemented and verified.

Currently implemented:

* Django project structure
* Domain-based Django applications
* PostgreSQL
* Docker and Docker Compose
* Environment-based configuration
* Document and document chunk models
* Database migrations
* Django Admin
* Basic repository hygiene

The next milestone is **Phase 2 — REST API & Authentication**.

---

# Tech Stack

## Currently Implemented

### Backend

* Python
* Django
* Django REST Framework

### Database

* PostgreSQL

### Infrastructure

* Docker
* Docker Compose

### Configuration

* django-environ

### Development

* Git
* GitHub

---

## Planned Technologies

The following technologies will be introduced in upcoming phases:

* `djangorestframework-simplejwt` — JWT authentication
* `pytest-django` — automated testing
* `drf-spectacular` — OpenAPI / Swagger documentation

Additional technologies for the RAG and production phases will be introduced as those phases begin.

---

# Architecture

## Current Architecture

```text
                    Knowledge Assistant
                           │
                           ▼
                    Django Backend
                           │
                  ┌────────┴────────┐
                  │                 │
                  ▼                 ▼
             PostgreSQL        File Storage
```

The application is containerized using Docker Compose:

```text
                    Docker Compose
                         │
              ┌──────────┴──────────┐
              │                     │
              ▼                     ▼
        Django Container      PostgreSQL Container
           web:8000                db:5432
```

The Django application communicates with PostgreSQL through the Docker Compose network.

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
│   │   └── ...
│   │
│   ├── documents/
│   │   ├── migrations/
│   │   │   └── 0001_initial.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   └── ...
│   │
│   ├── chat/
│   │   ├── migrations/
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   └── ...
│   │
│   ├── config/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── asgi.py
│   │   └── wsgi.py
│   │
│   ├── manage.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── .env.example
├── .gitignore
├── docker-compose.yml
└── README.md
```

### Application Responsibilities

#### `accounts`

Responsible for user-related functionality.

Authentication and authorization will be implemented and expanded during Phase 2.

#### `documents`

Responsible for document-related functionality.

Currently contains:

* `Document`
* `DocumentChunk`

The REST API for document management will be implemented during Phase 3.

#### `chat`

Reserved for future conversational and Knowledge Assistant functionality.

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

| Field         | Description                    |
| ------------- | ------------------------------ |
| `id`          | Primary key                    |
| `title`       | Document title                 |
| `file`        | Uploaded file                  |
| `owner`       | User who owns the document     |
| `uploaded_at` | Time the document was uploaded |
| `status`      | Current processing state       |

Document status currently supports:

* Uploading
* Processing
* Ready
* Failed

---

## DocumentChunk

A `DocumentChunk` represents a section of a document.

Current fields:

| Field        | Description                       |
| ------------ | --------------------------------- |
| `id`         | Primary key                       |
| `document`   | Parent document                   |
| `text`       | Extracted chunk text              |
| `embedding`  | Placeholder for future embeddings |
| `created_at` | Chunk creation time               |

The `embedding` field is intentionally left empty at this stage.

Embedding generation and vector retrieval will be introduced during the RAG phase.

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
```

### Important

Never commit the actual `.env` file or production secrets to Git.

---

# Running the Project

## Prerequisites

Make sure the following are installed:

* Git
* Docker
* Docker Compose

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

Update `.env` with the required configuration.

---

## 3. Start the Application

```bash
docker compose up -d
```

This starts the Django and PostgreSQL services.

Check the running containers:

```bash
docker compose ps
```

---

# Database Setup

Create and apply Django migrations:

```bash
docker compose run --rm web python manage.py makemigrations
```

```bash
docker compose run --rm web python manage.py migrate
```

Migration files are part of the source code and should be committed to Git.

---

# Creating an Admin User

Create a Django superuser:

```bash
docker compose run --rm web python manage.py createsuperuser
```

Follow the prompts to create the administrator account.

---

# Django Admin

Once the application is running, open:

```text
http://127.0.0.1:8000/admin/
```

The Django Admin currently provides access to:

* Users
* Groups
* Documents
* Document Chunks

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

# Development Checks

Run Django's system checks:

```bash
docker compose run --rm web python manage.py check
```

Check the configured database:

```bash
docker compose run --rm web python manage.py check --database default
```

---

# Git Repository Hygiene

The repository intentionally ignores development-specific files:

```text
.env
.venv/
venv/
__pycache__/
*.pyc
*.sqlite3
db.sqlite3
media/
staticfiles/
.vscode/
.idea/
*.log
```

The following should remain tracked:

```text
.env.example
Dockerfile
docker-compose.yml
requirements.txt
README.md
Django source code
Django migration files
```

---

# Development Workflow

The intended development workflow is:

```text
Modify code
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
Test functionality
    │
    ▼
Update documentation
    │
    ▼
Commit changes
```

Example:

```bash
docker compose run --rm web python manage.py check

docker compose run --rm web python manage.py makemigrations

docker compose run --rm web python manage.py migrate

docker compose up -d
```

---

# Development Roadmap

## Phase 1 — Backend Foundation

**Status: ✅ Complete**

* [x] Django project setup
* [x] Domain-based application structure
* [x] `accounts` application
* [x] `documents` application
* [x] `chat` application
* [x] PostgreSQL configuration
* [x] Docker environment
* [x] Docker Compose
* [x] Environment variable configuration
* [x] `.gitignore`
* [x] `Document` model
* [x] `DocumentChunk` model
* [x] Document processing status
* [x] Database migrations
* [x] Django → PostgreSQL integration
* [x] Django Admin
* [x] Basic repository documentation

---

# Phase 2 — REST API & Authentication

**Status: ✅ Complete**

## Week 2 — DRF + JWT Authentication

Planned:

* [x] Install and configure Django REST Framework
* [x] Install `djangorestframework-simplejwt`
* [x] Configure JWT authentication
* [x] Configure access-token lifetime
* [x] Configure refresh-token lifetime
* [x] Login endpoint
* [x] Refresh-token endpoint
* [x] Registration endpoint
* [x] Authentication permissions
* [x] `AllowAny` for public authentication endpoints
* [x] Password hashing
* [x] Password validation
* [x] Authentication tests
* [x] `pytest-django` setup
* [x] Invalid and missing-token tests
* [x] Duplicate-registration tests

The authentication flow will follow:

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

**Status: 🔜 Upcoming**

## Week 3 — Document REST API

Planned:

* [ ] `DocumentSerializer`
* [ ] `DocumentViewSet`
* [ ] Document upload
* [ ] Document listing
* [ ] Document retrieval
* [ ] Document update
* [ ] Document deletion
* [ ] Owner-based queryset filtering
* [ ] Server-side owner assignment
* [ ] File extension validation
* [ ] File size validation
* [ ] Pagination
* [ ] API error handling
* [ ] Ownership isolation tests
* [ ] OpenAPI schema
* [ ] Swagger UI
* [ ] End-to-end API testing

Planned API structure:

```text
/api/auth/token/
/api/auth/token/refresh/
/api/auth/register/

/api/documents/
/api/documents/{id}/
```

Document ownership will be enforced server-side.

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

**Status: 🔜 Planned**

Planned:

* [ ] Document text extraction
* [ ] Document processing pipeline
* [ ] Text chunking
* [ ] Embedding generation
* [ ] Vector database integration
* [ ] Semantic search
* [ ] Retrieval pipeline

The existing `DocumentChunk.embedding` field is reserved for this phase.

---

# Phase 5 — Knowledge Assistant

**Status: 🔜 Planned**

Planned:

* [ ] Question-answering API
* [ ] Retrieval-Augmented Generation
* [ ] Relevant document retrieval
* [ ] Context construction
* [ ] LLM integration
* [ ] Source/reference information
* [ ] Conversation history
* [ ] Chat API

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

* [ ] Unit tests
* [ ] API integration tests
* [ ] Authentication tests
* [ ] Ownership/security tests
* [ ] GitHub Actions
* [ ] Continuous Integration
* [ ] Background processing
* [ ] Redis
* [ ] Celery
* [ ] Caching
* [ ] Rate limiting
* [ ] Structured logging
* [ ] Health checks
* [ ] Observability
* [ ] Performance optimization
* [ ] Production deployment

---

# Milestones

| Version | Milestone                | Status             |
| ------- | ------------------------ | ------------------ |
| `v0.1`  | Backend Foundation       | Current checkpoint |
| `v0.2`  | JWT Authentication       | Planned            |
| `v0.3`  | Document CRUD API        | Planned            |


---

# Contributing

Contributions, suggestions, bug reports, and improvements are welcome.

Before submitting a change:

1. Create a branch for your work.
2. Make focused changes.
3. Run the available checks and tests.
4. Update documentation when necessary.
5. Submit a pull request describing the change.

A detailed `CONTRIBUTING.md` will be added as the project becomes ready for external contributions.

---

# License

This project is currently under development.

A project license will be added before public distribution.
