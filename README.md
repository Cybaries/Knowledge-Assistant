# Knowledge Assistant

A production-oriented Knowledge Assistant backend built with **Django, Django REST Framework, PostgreSQL, and Docker**.

The goal of this project is to build a backend that allows users to upload documents and, eventually, ask questions about their content using **Retrieval-Augmented Generation (RAG)**.

The project is being developed incrementally, with an emphasis on clean architecture, testing, API design, containerization, documentation, and production-oriented engineering practices.

---

## Project Status

🚧 **Currently in Phase 1 — Backend Foundation**

The core Django application, PostgreSQL database, Docker environment, document data models, migrations, and Django Admin are implemented.

AI/RAG functionality will be introduced in later phases.

---

## Tech Stack

### Backend

* Python
* Django
* Django REST Framework
* django-environ

### Database

* PostgreSQL

### Infrastructure

* Docker
* Docker Compose

### Development

* Git
* GitHub

---

## Architecture

Current architecture:

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

The backend is containerized using Docker Compose:

```text
                    Docker Compose
                         │
              ┌──────────┴──────────┐
              │                     │
              ▼                     ▼
        Django Container      PostgreSQL Container
           web:8000                db:5432
```

The Django application communicates with PostgreSQL over the Docker Compose network.

---

## Project Structure

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

### Application responsibilities

#### `accounts`

Responsible for user-related functionality.

Authentication and authorization functionality will be expanded in Phase 2.

#### `documents`

Responsible for document-related functionality.

Currently contains:

* `Document`
* `DocumentChunk`

#### `chat`

Reserved for the future conversational/assistant functionality.

---

# Database Design

The current database model is:

```text
                    User
                     │
                     │ 1
                     │
                     ▼
                 Document
                     │
                     │ 1
                     │
                     ▼
              DocumentChunk
```

## User

Django's built-in User model is currently used.

A user can own multiple documents.

```text
User
 │
 ├── Document 1
 ├── Document 2
 └── Document 3
```

---

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

Document chunks will become an important part of the RAG pipeline in Phase 2.

---

# Environment Configuration

Environment-specific configuration is stored using `.env`.

The `.env` file is intentionally excluded from Git.

A template is provided through:

```text
.env.example
```

Create your local environment file with:

```bash
cp .env.example .env
```

Then configure the required values.

Example:

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

## 1. Clone the repository

```bash
git clone <repository-url>
cd Knowledge-Assistant
```

Replace `<repository-url>` with the actual GitHub repository URL.

---

## 2. Create the environment file

```bash
cp .env.example .env
```

Edit `.env` and provide the required configuration.

---

## 3. Start the application

From the repository root:

```bash
docker compose up -d
```

This starts:

```text
Django
PostgreSQL
```

in separate containers.

---

## 4. Check running containers

```bash
docker compose ps
```

You should see both services running.

Expected services:

```text
knowledge_assistant_web
knowledge_assistant_db
```

---

# Database Setup

After starting the containers, apply Django migrations:

```bash
docker compose run --rm web python manage.py migrate
```

This creates the required Django and application tables in PostgreSQL.

---

# Creating an Admin User

Create a Django superuser:

```bash
docker compose run --rm web python manage.py createsuperuser
```

Follow the prompts to create your administrator account.

---

# Django Admin

Once the application is running, open:

```text
http://127.0.0.1:8000/admin/
```

Log in using the superuser credentials.

The admin interface currently provides access to:

* Users
* Groups
* Documents
* Document Chunks

---

# Document Storage

Uploaded documents are stored under the Django media directory:

```text
backend/
└── media/
    └── documents/
```

The `media/` directory is excluded from Git.

This prevents uploaded files from accidentally becoming part of the source repository.

---

# Stopping the Application

To stop the Django and PostgreSQL containers:

```bash
docker compose down
```

The PostgreSQL data is stored in a Docker named volume, so running `docker compose down` does not remove the database data.

To start the application again:

```bash
docker compose up -d
```

### Important

Do not use:

```bash
docker compose down -v
```

unless you intentionally want to delete the PostgreSQL volume and its data.

---

# Database Migrations

Create migrations after changing Django models:

```bash
docker compose run --rm web python manage.py makemigrations
```

Apply migrations:

```bash
docker compose run --rm web python manage.py migrate
```

Migration files are part of the source code and should be committed to Git.

For example:

```text
backend/documents/migrations/0001_initial.py
```

---

# Development Checks

Run Django's system checks with:

```bash
docker compose run --rm web python manage.py check
```

Check the database configuration:

```bash
docker compose run --rm web python manage.py check --database default
```

---

# Git and Repository Hygiene

The repository intentionally ignores development-specific files such as:

```text
.env
.venv/
__pycache__/
*.pyc
*.sqlite3
media/
staticfiles/
```

These files should not be committed to the repository.

Migration files, source code, Docker configuration, and documentation should be committed.

---

# Development Workflow

The intended development workflow is:

```text
1. Modify Django models/code
          ↓
2. Run Django checks
          ↓
3. Create migrations if models changed
          ↓
4. Apply migrations
          ↓
5. Test functionality
          ↓
6. Update documentation if required
          ↓
7. Commit changes
```

Example:

```bash
docker compose run --rm web python manage.py check

docker compose run --rm web python manage.py makemigrations

docker compose run --rm web python manage.py migrate

docker compose up -d
```

---

# Current Implementation

## Phase 1 — Backend Foundation

* [x] Django project setup
* [x] Domain-based application structure
* [x] `accounts` application
* [x] `documents` application
* [x] `chat` application
* [x] PostgreSQL configuration
* [x] Docker environment
* [x] Docker Compose
* [x] Environment variable configuration
* [x] `.gitignore` configuration
* [x] `Document` model
* [x] `DocumentChunk` model
* [x] Document processing status
* [x] Database migrations
* [x] PostgreSQL integration
* [x] Django Admin configuration
* [x] Basic repository documentation

---

# Roadmap

## Phase 1 — Backend Foundation

**Status: In progress / checkpoint**

Django, PostgreSQL, Docker, models, migrations, and project structure.

---

## Phase 2 — Authentication & RAG Foundation

Planned:

* [ ] Django REST Framework API configuration
* [ ] JWT authentication
* [ ] User registration
* [ ] Login and token refresh
* [ ] Authentication permissions
* [ ] Document ownership enforcement
* [ ] Document upload API
* [ ] Document CRUD API
* [ ] File validation
* [ ] API pagination
* [ ] OpenAPI / Swagger documentation
* [ ] Document text extraction
* [ ] Text chunking
* [ ] Embedding generation
* [ ] Vector search

---

## Phase 3 — Knowledge Assistant

Planned:

* [ ] Question-answering API
* [ ] Semantic document retrieval
* [ ] Retrieval-Augmented Generation
* [ ] Source/reference information in responses
* [ ] Conversation history
* [ ] Chat API
* [ ] Improved prompt management

---

## Phase 4 — Production Engineering

Planned:

* [ ] Background document processing
* [ ] Redis
* [ ] Celery
* [ ] Caching
* [ ] Rate limiting
* [ ] Structured logging
* [ ] Error handling
* [ ] Health checks
* [ ] Observability
* [ ] Performance optimization

---

## Phase 5 — Testing, CI/CD & Deployment

Planned:

* [ ] Unit tests
* [ ] API tests
* [ ] Integration tests
* [ ] pytest
* [ ] GitHub Actions
* [ ] Automated test pipeline
* [ ] Docker image optimization
* [ ] Production deployment
* [ ] Production database
* [ ] Environment-specific configuration

---

# Versioning

Current checkpoint:

```text
v0.1 — Backend Foundation
```

Future versions will be tagged as major project milestones are completed.

---

# Contributing

Contributions, suggestions, bug reports, and improvements are welcome.

Before submitting a change:

1. Create a branch for your work.
2. Make focused changes.
3. Run the available checks and tests.
4. Update documentation when necessary.
5. Submit a pull request describing the change.

A detailed `CONTRIBUTING.md` will be added before the project becomes fully open for external contributions.

---

# License

This project is currently under development.

A project license will be added before public distribution.
