# Knowledge Assistant

A production-oriented Knowledge Assistant backend built with **Django, Django REST Framework, PostgreSQL (pgvector), FastAPI, Ollama, and Docker**.

Users upload documents (PDF, TXT, DOCX), the backend chunks and embeds them, and users can ask questions that are answered from the content of their own documents using **Retrieval-Augmented Generation (RAG)**.

Everything runs locally with free, open-source components. No paid API keys are required.

The project is being developed incrementally with an emphasis on:

- Clean domain-based architecture
- Secure authentication and authorization
- Strict per-user data isolation, including during retrieval
- REST API design and OpenAPI documentation
- Automated testing
- Containerization
- Code quality and repository hygiene

---

# Table of Contents

- [Project Status](#project-status)
- [How It Works](#how-it-works)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Application Responsibilities](#application-responsibilities)
- [Database Design](#database-design)
- [Environment Configuration](#environment-configuration)
- [Running the Project](#running-the-project)
- [Quick Walkthrough](#quick-walkthrough)
- [REST API](#rest-api)
- [Testing](#testing)
- [Code Quality](#code-quality)
- [Known Limitations](#known-limitations)
- [Development Roadmap](#development-roadmap)
- [Milestones](#milestones)
- [Contributing](#contributing)
- [License](#license)

---

# Project Status

✅ **Phase 1 — Backend Foundation: Complete**

✅ **Phase 2 — REST API & Authentication: Complete**

✅ **Phase 3 — Document CRUD API: Complete**

✅ **Phase 4 — RAG Pipeline: Implementation complete; clean-build verification and v0.5 release pending**

Implemented so far:

- JWT authentication and owner-scoped document management
- Document parsing (PDF, TXT, DOCX) and paragraph-aware chunking
- Embedding generation through a separate FastAPI `ai_service`
- Vector storage and cosine-similarity search with pgvector
- Local LLM generation through Ollama
- An authenticated question-answering endpoint that returns an answer plus source references
- Automated tests, OpenAPI documentation, Docker Compose, and code-quality tooling

The next milestone is **Phase 5 — Knowledge Assistant**: conversation history and a chat API built on top of the `rag` app.

---

# How It Works

**Ingestion** (runs synchronously when a document is uploaded):

```text
Upload document
      │
      ▼
Validate (type, size) ── owner assigned server-side
      │
      ▼
Extract text (PDF / TXT / DOCX)
      │
      ▼
Split into overlapping chunks
      │
      ▼
ai_service /embed  →  384-dimensional vectors
      │
      ▼
Store chunks + embeddings in PostgreSQL (pgvector)
      │
      ▼
Document status: READY   (FAILED if any step errors)
```

**Question answering:**

```text
POST /api/rag/query/  { question, document_id? }
      │
      ▼
Embed the question (ai_service /embed)
      │
      ▼
Find the nearest chunks by cosine distance
— only chunks from the authenticated user's own documents
      │
      ▼
Build a prompt: instructions + retrieved context + question
      │
      ▼
ai_service /generate  →  Ollama
      │
      ▼
{ answer, sources: [{ document_title, chunk_index }] }
```

If the user has no eligible chunks, the API answers "I don't know based on the available documents." and does not call the LLM.

---

# Tech Stack

## Currently Implemented

### Backend

- Python
- Django
- Django REST Framework

### Authentication

- `djangorestframework-simplejwt` — JWT authentication

### Database and Vector Search

- PostgreSQL
- pgvector — vector storage and cosine-similarity search (`pgvector/pgvector:pg16` image, `pgvector` Django package)

### AI Service

- FastAPI + Uvicorn — separate `ai_service` microservice
- sentence-transformers — local embeddings (`all-MiniLM-L6-v2`, 384 dimensions)
- Ollama — local LLM serving (default: `llama3.2:1b` with a small-context configuration)
- httpx — HTTP client for service-to-service calls

### Document Processing

- `pypdf` — PDF text extraction
- `python-docx` — DOCX text extraction

### Infrastructure

- Docker
- Docker Compose

### Configuration

- django-environ

### Testing

- pytest
- pytest-django

### API Documentation

- drf-spectacular — OpenAPI / Swagger documentation

### Code Quality

- Black — formatting
- Ruff — linting

### Development

- Git
- GitHub

---

## Planned Technologies

### Phase 5 — Knowledge Assistant

- Conversation and message models
- Chat API with multi-turn context

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
- CI/CD (GitHub Actions)
- Production deployment

---

# Architecture

## Services

The application runs as four containers on one Docker Compose network:

```text
                      Client (API consumer)
                               │
                               ▼
                  ┌────────────────────────┐
                  │  web  (Django, :8000)  │
                  │  auth · documents · rag│
                  └───────┬────────┬───────┘
                          │        │
              HTTP        │        │  SQL
                          ▼        ▼
        ┌─────────────────────┐  ┌────────────────────────────┐
        │ ai_service (:8001)  │  │ db (:5432)                 │
        │ FastAPI             │  │ PostgreSQL + pgvector      │
        │ /embed  /generate   │  │ documents, chunks, vectors │
        └──────────┬──────────┘  └────────────────────────────┘
                   │ HTTP
                   ▼
        ┌─────────────────────┐
        │ ollama (:11434)     │
        │ local LLM           │
        └─────────────────────┘
```

| Compose service | Container name               | Port  | Role                                   |
| --------------- | ---------------------------- | ----- | -------------------------------------- |
| `web`           | `knowledge_assistant_web`    | 8000  | Django REST API                        |
| `db`            | `knowledge_assistant_db`     | 5432  | PostgreSQL with the pgvector extension |
| `ai_service`    | `knowledge_assistant_ai`     | 8001  | Embeddings and LLM calls               |
| `ollama`        | `knowledge_assistant_ollama` | 11434 | Local LLM server                       |

Persistent data lives in two named volumes: `postgres_data` and `ollama_data`.

## Design Decisions

- **`rag` is a separate Django app** alongside `documents`. `documents` owns CRUD, ownership, and storage; `rag` owns parsing, chunking, embedding orchestration, retrieval, and the query endpoint.
- **ML dependencies are isolated in `ai_service`.** `sentence-transformers` and the Ollama calls never need to be installed in the Django container, and the model backend can be swapped without touching Django.
- **`ai_service` is deliberately generic.** It exposes `/embed` and `/generate` and knows nothing about RAG. Prompt construction lives in Django, where it is version-controlled and tested with the rest of the app.
- **pgvector instead of a separate vector database.** One fewer service to run, back up, and secure.
- **`rag/ai_client.py` is the only module that calls `ai_service`.** Tests mock this single seam, so the test suite never needs a model server.
- **Ingestion is a plain callable** (`rag/pipeline.py`, `process_document(document_id)`). It currently runs synchronously from the upload view and takes only a primitive ID, so it can be wrapped in a Celery task in Phase 6 without restructuring.
- **Ownership is enforced at retrieval time.** Retrieval filters on `document__owner` before ranking, so one user's document content can never appear in another user's answer, even when a `document_id` belonging to someone else is supplied.

---

# Project Structure

```text
Knowledge-Assistant/
│
├── backend/                        # Django project
│   ├── config/                     # settings, root urls, wsgi/asgi
│   │
│   ├── accounts/                   # registration, JWT auth
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   ├── views.py
│   │   └── tests/
│   │       └── test_auth.py
│   │
│   ├── documents/                  # Document + DocumentChunk models, CRUD API
│   │   ├── migrations/
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── tests/
│   │       └── test_documents.py
│   │
│   ├── rag/                        # RAG pipeline and query API
│   │   ├── parsers.py              # text extraction per file type
│   │   ├── chunking.py             # paragraph-aware chunking with overlap
│   │   ├── pipeline.py             # process_document(document_id)
│   │   ├── ai_client.py            # only module that calls ai_service
│   │   ├── retrieval.py            # owner-scoped pgvector similarity search
│   │   ├── serializers.py          # query request/response serializers
│   │   ├── views.py                # QueryView
│   │   ├── urls.py
│   │   ├── tests.py                # chunking tests
│   │   ├── test_parsers.py
│   │   ├── test_pipeline.py
│   │   ├── test_retrieval.py
│   │   └── test_views.py
│   │
│   ├── chat/                       # reserved for Phase 5
│   │
│   ├── manage.py
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── pytest.ini
│   └── ruff.toml
│
├── ai_service/                     # FastAPI microservice
│   ├── main.py                     # /health, /embed, /generate
│   ├── embeddings.py               # sentence-transformers wrapper
│   ├── llm.py                      # Ollama client wrapper
│   ├── schemas.py                  # pydantic request/response models
│   ├── requirements.txt
│   └── Dockerfile
│
├── Modelfile                       # lightweight Ollama model configuration
├── docker-compose.yml
├── .env.example
├── .gitignore
├── CONTRIBUTING.md
├── LICENSE
└── README.md
```

---

# Application Responsibilities

## `accounts`

- User registration
- JWT login and token refresh (access token: 15 minutes, refresh token: 7 days)
- Password hashing and validation
- Authentication tests

## `documents`

- `Document` and `DocumentChunk` models
- Document REST API: upload, list, retrieve, update, delete
- Owner-based access control: users only ever see their own documents
- File validation (type and size) and pagination
- Triggers `rag.pipeline.process_document` after a successful upload

## `rag`

- **`parsers.py`** — extracts text from PDF, TXT, and DOCX; raises a specific `DocumentParsingError` for unsupported types, unreadable files, or files with no extractable text
- **`chunking.py`** — packs paragraphs into chunks of up to 900 characters, splitting oversized paragraphs with a 120-character overlap
- **`pipeline.py`** — `process_document(document_id)`: sets the status to `PROCESSING`, parses, chunks, embeds, and replaces the document's chunks inside a transaction; sets `READY` on success and `FAILED` (then re-raises) on any error
- **`ai_client.py`** — HTTP client for `ai_service` (`get_embeddings`, `generate`); wraps transport errors in `AIServiceError`
- **`retrieval.py`** — embeds the question and returns the nearest chunks by cosine distance, restricted to the requesting user's documents
- **`views.py`** — `QueryView` builds a grounded prompt from the retrieved chunks, calls the LLM, and returns the answer with sources. Returns `503` with a clear message if `ai_service` is unavailable

`rag` depends on `documents` for its models. It does not depend on `chat`.

## `ai_service`

A small FastAPI service:

- `GET /health` — liveness check
- `POST /embed` — `{ "texts": [...] }` → `{ "embeddings": [[...], ...] }` (order preserved)
- `POST /generate` — `{ "prompt": "..." }` → `{ "text": "..." }` (non-streaming)

## `chat`

Reserved for Phase 5. It will depend on `rag` for retrieval and generation and add conversation state on top, rather than duplicating retrieval logic.

---

# Database Design

```text
User
  │ 1
  │
  ▼ N
Document
  │ 1
  │
  ▼ N
DocumentChunk
```

## Document

| Field         | Description                                     |
| ------------- | ----------------------------------------------- |
| `id`          | Primary key                                     |
| `title`       | Document title                                  |
| `file`        | Uploaded file (stored under `media/documents/`) |
| `owner`       | User who owns the document (set server-side)    |
| `uploaded_at` | Upload time                                     |
| `status`      | `UPLOADING`, `PROCESSING`, `READY`, or `FAILED` |

## DocumentChunk

| Field         | Description                                       |
| ------------- | ------------------------------------------------- |
| `id`          | Primary key                                       |
| `document`    | Parent document                                   |
| `chunk_index` | Position of the chunk within the document         |
| `text`        | Chunk text                                        |
| `embedding`   | 384-dimensional pgvector `VectorField` (nullable) |
| `created_at`  | Chunk creation time                               |

The 384 dimensions come from the default embedding model (`all-MiniLM-L6-v2`). **If you change `EMBEDDING_MODEL_NAME` to a model with a different output size, `DocumentChunk.embedding` must change to match** (new migration, re-embed existing documents).

The `vector` extension is enabled by a migration, and the database image is `pgvector/pgvector:pg16`. Similarity search is currently an exact scan; an approximate-nearest-neighbour index (HNSW or IVFFlat) is a future optimisation for larger collections.

---

# Environment Configuration

Environment-specific configuration lives in `.env`, which is excluded from Git. A template is provided:

```bash
cp .env.example .env
```

```env
# Django
SECRET_KEY=replace-with-a-long-random-development-secret
DEBUG=True

# Django database connection (Docker Compose service hostname)
DB_NAME=knowledge_assistant
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432

# PostgreSQL container initialization; keep these aligned with DB_*
POSTGRES_DB=knowledge_assistant
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres

# AI service
AI_SERVICE_URL=http://ai_service:8001
EMBEDDING_MODEL_NAME=all-MiniLM-L6-v2
OLLAMA_URL=http://ollama:11434
OLLAMA_MODEL=llama3.2:1b-smallctx
```

| Variable               | Used by                     | Purpose                                                  |
| ---------------------- | --------------------------- | -------------------------------------------------------- |
| `DB_*`                 | Django                      | Database connection                                      |
| `POSTGRES_*`           | `db` container              | Initial database, user, and password (must match `DB_*`) |
| `AI_SERVICE_URL`       | Django (`rag/ai_client.py`) | Where to reach `ai_service` on the Compose network       |
| `EMBEDDING_MODEL_NAME` | `ai_service`                | sentence-transformers model used for embeddings          |
| `OLLAMA_URL`           | `ai_service`                | Where to reach Ollama on the Compose network             |
| `OLLAMA_MODEL`         | `ai_service`                | Ollama model used for generation                         |

Inside the Compose network, services reach each other by service name (`db`, `ai_service`, `ollama`), not `localhost`.

**Never commit `.env` or real secrets.** For anything beyond local development, use a strong `SECRET_KEY`, `DEBUG=False`, and real credentials.

---

# Running the Project

## Prerequisites

- Git
- Docker
- Docker Compose

```bash
docker --version
docker compose version
```

If your system requires it, prefix the `docker compose` commands below with `sudo`.

Resources: the first run downloads the embedding model and an Ollama model, so expect a few gigabytes of downloads and a few gigabytes of RAM in use.

## 1. Clone the repository

```bash
git clone https://github.com/Cybaries/Knowledge-Assistant.git
cd Knowledge-Assistant
```

## 2. Create the environment file

```bash
cp .env.example .env
```

## 3. Build and start the services

```bash
docker compose up --build
```

Or in the background:

```bash
docker compose up -d --build
```

On first start, `ai_service` downloads the embedding model (internet access required), so it can take a while before `/embed` responds. Confirm all four containers are running:

```bash
docker compose ps
```

## 4. Apply database migrations

```bash
docker compose exec web python manage.py migrate
```

## 5. Create the Ollama model

A fresh Ollama container has no models, so this step is required before questions can be answered. The repository-root `Modelfile` defines a lightweight configuration (2048-token context, 384 max output tokens) on top of `llama3.2:1b`:

```bash
docker compose exec ollama ollama pull llama3.2:1b
docker compose cp Modelfile ollama:/tmp/Modelfile
docker compose exec -T ollama ollama create llama3.2:1b-smallctx -f /tmp/Modelfile
docker compose exec ollama ollama list
```

Make sure `.env` contains `OLLAMA_MODEL=llama3.2:1b-smallctx`. The model is stored in the `ollama_data` volume and survives restarts.

To use a different model, pull it, set `OLLAMA_MODEL` accordingly, and restart `ai_service`:

```bash
docker compose restart ai_service
```

## 6. Create an admin user (optional)

```bash
docker compose exec web python manage.py createsuperuser
```

Django Admin: <http://127.0.0.1:8000/admin/>

## Stopping and restarting

```bash
docker compose down        # stop containers, keep data
docker compose up -d       # start again
```

**Do not use `docker compose down -v` unless you intend to delete the PostgreSQL data and downloaded Ollama models.**

---

# Quick Walkthrough

The interactive Swagger UI at <http://127.0.0.1:8000/api/docs/> can do all of this. The same flow with `curl`:

```bash
# 1. Register
curl -X POST http://127.0.0.1:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username": "demo", "email": "demo@example.com", "password": "a-strong-password"}'

# 2. Log in and copy the "access" token
curl -X POST http://127.0.0.1:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "demo", "password": "a-strong-password"}'

export TOKEN="<paste access token>"

# 3. Upload a document (processing runs before the response returns)
curl -X POST http://127.0.0.1:8000/api/documents/ \
  -H "Authorization: Bearer $TOKEN" \
  -F "title=Demo notes" \
  -F "file=@notes.txt"

# 4. Check that its status is READY
curl http://127.0.0.1:8000/api/documents/ -H "Authorization: Bearer $TOKEN"

# 5. Ask a question about it
curl -X POST http://127.0.0.1:8000/api/rag/query/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"question": "What does the document say about pgvector?"}'
```

The first generation after startup can be slow while Ollama loads the model.

---

# REST API

## Authentication

```text
POST /api/auth/register/        create an account
POST /api/auth/token/           log in → access + refresh tokens
POST /api/auth/token/refresh/   exchange a refresh token for a new access token
```

All other endpoints require `Authorization: Bearer <access token>`.

## Documents

```text
GET    /api/documents/          list your documents (paginated)
POST   /api/documents/          upload a document
GET    /api/documents/{id}/     retrieve one of your documents
PUT    /api/documents/{id}/     update
PATCH  /api/documents/{id}/     partial update
DELETE /api/documents/{id}/     delete
```

- Documents are scoped to the authenticated user. Requesting another user's document returns `404`, not `403`, so its existence is not revealed.
- The owner is assigned server-side and cannot be set through the API.
- Supported file types: **PDF, TXT, DOCX**. Maximum size: **10 MB**.
- List responses are page-number paginated (page size 10) and include `count`, `next`, `previous`, and `results`.
- Each document has a `status`: `UPLOADING` → `PROCESSING` → `READY`, or `FAILED` if processing errored.

## RAG Query

```text
POST /api/rag/query/
```

Request:

```json
{
  "question": "Which database extension stores the document embeddings?",
  "document_id": 1
}
```

`document_id` is optional and restricts the search to one of your documents. Response:

```json
{
  "answer": "PostgreSQL using the pgvector extension.",
  "sources": [
    {
      "document_title": "RAG Test Document",
      "chunk_index": 0
    }
  ]
}
```

| Situation                         | Response                                                                                        |
| --------------------------------- | ----------------------------------------------------------------------------------------------- |
| Not authenticated                 | `401`                                                                                           |
| Missing or blank `question`       | `400`                                                                                           |
| You have no eligible chunks       | `200`, "I don't know based on the available documents.", empty `sources`; the LLM is not called |
| `ai_service` / Ollama unavailable | `503` with an explanatory message                                                               |

`sources` lists the chunks that were retrieved and included in the prompt. It does not guarantee that every statement in the answer is supported by them.

## API Documentation

```text
OpenAPI schema   http://127.0.0.1:8000/api/schema/
Swagger UI       http://127.0.0.1:8000/api/docs/
```

---

# Testing

```bash
docker compose exec web pytest
```

Tests run against the real PostgreSQL + pgvector database in the Docker environment. Calls to `ai_service` are mocked at the `rag/ai_client.py` boundary, so the suite is fast and does not need Ollama or the embedding model.

Coverage includes:

- Registration (including duplicates), login, token refresh, invalid and missing credentials
- Document upload, listing, retrieval, update, and deletion
- Ownership isolation, file validation, and pagination
- Text parsing and chunking
- The ingestion pipeline: success, parse failure, and embedding-service failure (status `FAILED`, no partial chunks)
- Vector retrieval: cosine ranking, owner-only results, `document_id` filtering, and refusal to return another user's document
- The query endpoint: answer and sources, no-chunks behaviour, 401 when unauthenticated, 400 on a blank question, and 503 when `ai_service` fails during retrieval or generation

Mocked unit tests do not prove the real models behave well. Before a release, also run the manual end-to-end check: upload a document, ask a question it answers, ask one it doesn't, and confirm a second user cannot retrieve the first user's content.

---

# Code Quality

The project uses **Black** for formatting and **Ruff** for linting. Both run in the `web` container:

```bash
docker compose exec web black --check .
docker compose exec web black .

docker compose exec web ruff check .
```

Typical pre-commit routine:

```bash
docker compose exec web black --check .
docker compose exec web ruff check .
docker compose exec web python manage.py check
docker compose exec web python manage.py migrate
docker compose exec web pytest
git diff --check
git status
```

## Repository hygiene

Never commit: `.env`, virtual environments, `__pycache__/`, `*.pyc`, SQLite databases, `backend/media/` (uploaded documents), logs, or editor folders.

Always keep tracked: `.env.example`, `Dockerfile`s, `docker-compose.yml`, `requirements.txt` files, `Modelfile`, `ruff.toml`, `pytest.ini`, `README.md`, `CONTRIBUTING.md`, `LICENSE`, source code, and Django migrations.

---

# Known Limitations

- **Ingestion is synchronous.** Uploads do not return until the document has been parsed, chunked, and embedded, so large documents make the upload request slow. Background processing with Celery and Redis is planned for Phase 6.
- **Small default LLM.** The default `llama3.2:1b` configuration (2048-token context, 384 output tokens) favours running on modest hardware over answer quality, and a small model may occasionally ignore the "answer only from the context" instruction. Use a larger model by changing `OLLAMA_MODEL` and the `Modelfile`.
- **Retrieval has no relevance threshold.** The top 5 chunks by cosine distance are always used if the user has any chunks, however weak the match. Saying "I don't know" for off-topic questions then depends on the model following the prompt.
- **PDF and DOCX extraction is basic.** Scanned/image-only PDFs have no extractable text and fail processing (OCR is not included). DOCX extraction reads paragraphs only, not tables, headers, or footers.
- **Exact vector search.** Fine for small collections; larger ones will want an HNSW or IVFFlat index.
- **No streaming.** Answers are returned in one response after generation completes.
- **Sources are retrieved chunks**, not verified citations.

---

# Development Roadmap

## Phase 1 — Backend Foundation

**Status: ✅ Complete**

- [x] Django project setup and domain-based app structure
- [x] `accounts`, `documents`, and `chat` applications
- [x] PostgreSQL configuration, Docker, and Docker Compose
- [x] Environment variable configuration and `.gitignore`
- [x] `Document` and `DocumentChunk` models, processing status
- [x] Database migrations and Django Admin
- [x] Basic repository documentation

## Phase 2 — REST API & Authentication

**Status: ✅ Complete**

- [x] Django REST Framework and `djangorestframework-simplejwt`
- [x] Login, refresh, and registration endpoints
- [x] Access/refresh token lifetimes
- [x] Authentication permissions (`AllowAny` only on public auth endpoints)
- [x] Password hashing and validation
- [x] `pytest-django` setup; authentication, invalid-token, and duplicate-registration tests

## Phase 3 — Document CRUD API

**Status: ✅ Complete**

- [x] `DocumentSerializer` and `DocumentViewSet`
- [x] Upload, list, retrieve, update, delete
- [x] Owner-based queryset filtering and server-side owner assignment
- [x] File extension and size validation
- [x] Pagination and API error handling
- [x] Ownership isolation tests
- [x] OpenAPI schema and Swagger UI

## Phase 4 — RAG Pipeline

**Status: ✅ Implementation complete — clean-build verification and v0.5 release pending**

### Week 5 — Infrastructure

- [x] Switch `db` image to `pgvector/pgvector:pg16`
- [x] Migration enabling the `vector` extension
- [x] Migrate `DocumentChunk.embedding` from `JSONField` to `VectorField`
- [x] Scaffold `ai_service/` (FastAPI + Dockerfile)
- [x] Add `ai_service` and `ollama` to `docker-compose.yml`
- [x] Add `AI_SERVICE_URL`, `OLLAMA_URL`, `OLLAMA_MODEL`, `EMBEDDING_MODEL_NAME` to `.env.example`

### Week 6 — Ingestion Pipeline

- [x] `rag/parsers.py` — text extraction (PDF, TXT, DOCX)
- [x] `rag/chunking.py` — paragraph-aware chunking with overlap
- [x] `ai_service` `/embed` endpoint (sentence-transformers)
- [x] `rag/ai_client.py`
- [x] `rag/pipeline.py` — `process_document(document_id)`
- [x] Wire `process_document` into the upload flow
- [x] Tests for parsing, chunking, and the pipeline with `ai_client` mocked

### Week 7 — Retrieval + Generation

- [x] `ai_service` `/generate` endpoint (Ollama wrapper)
- [x] `rag/retrieval.py` — owner-scoped pgvector similarity search
- [x] `rag/views.py`, serializers, and urls — `QueryView`
- [x] Manual end-to-end pass: upload → ask → grounded answer
- [x] Automated tests for retrieval and the query endpoint

### Week 8 — Polish and Release

- [x] Update API docs to reflect the query endpoint
- [x] Update README and milestones for Phase 4
- [ ] Full clean `docker compose down -v && docker compose up --build` verification, following this README only
- [ ] Tag and release `v0.5`

## Phase 5 — Knowledge Assistant

**Status: 🔜 Planned**

Question answering, retrieval, and source references already exist from Phase 4. This phase adds conversations on top of them.

- [ ] Conversation and message models in `chat`
- [ ] Chat API: create a conversation, send a message, list history
- [ ] Multi-turn context (use recent messages when answering follow-up questions)
- [ ] Per-message source references
- [ ] Retrieval tuning (top-k, relevance threshold)
- [ ] Optional: streaming responses

```text
User message
      │
      ▼
Load conversation history
      │
      ▼
Question processing
      │
      ▼
rag: vector search → context construction → LLM
      │
      ▼
Store message + answer + sources
```

## Phase 6 — Production Engineering & CI/CD

**Status: 🔜 Planned**

- [ ] Expanded integration and end-to-end test coverage
- [ ] GitHub Actions and continuous integration
- [ ] Background processing with Redis and Celery (wrap `process_document`)
- [ ] Caching
- [ ] Rate limiting
- [ ] Structured logging
- [ ] Health checks
- [ ] Observability
- [ ] Performance optimization
- [ ] Production deployment

---

# Milestones

| Version | Milestone                                               | Status                       |
| ------- | ------------------------------------------------------- | ---------------------------- |
| v0.1    | Initial Project Foundation                              | Complete                     |
| v0.2    | JWT Authentication                                      | Complete                     |
| v0.3    | Document CRUD API                                       | Complete                     |
| v0.4    | Repository Hygiene, Documentation & Release Preparation | Complete                     |
| v0.5    | RAG Pipeline                                            | Verification/release pending |
| v0.6    | Knowledge Assistant                                     | Planned                      |

---

# Contributing

Contributions, suggestions, bug reports, and improvements are welcome. Please read [`CONTRIBUTING.md`](CONTRIBUTING.md) for local setup, branching conventions, code style, testing requirements, and pull request expectations.

Before submitting a change:

1. Create a branch for your work.
2. Make focused changes.
3. Run Black and Ruff.
4. Run the test suite.
5. Update documentation when necessary.
6. Open a pull request describing the change.

---

# License

This project is licensed under the **MIT License**. See [`LICENSE`](LICENSE) for the full text.

---

# Project Philosophy

The project is built in phases, and each phase ends in a working, tested milestone before the next layer is added:

```text
Django → REST API → Authentication → Document Management → PostgreSQL
      → RAG Pipeline → Knowledge Assistant → Production Engineering
```
