# Contributing

Thank you for your interest in contributing to Knowledge Assistant.

## Local Setup

Follow the setup instructions in the [README](README.md), under **Running the Project**.

The project is currently developed and tested using Docker, PostgreSQL, Django, and Django REST Framework.

## Branching

This project currently has a solo maintainer, so direct commits to `main` are acceptable during development.

For external contributions, please use a feature or fix branch:

* `feature/<short-description>`
* `fix/<short-description>`

Pull requests are welcome as the project develops.

## Code Style

The project uses:

* **Black** for Python formatting
* **Ruff** for linting

Run formatting with:

```bash
docker compose exec web black .
```

Run linting with:

```bash
docker compose exec web ruff check .
```

Please keep code readable, focused, and consistent with the existing project structure.

## Running Tests

Run the complete test suite with:

```bash
docker compose exec web pytest
```

All tests should pass before submitting a pull request.

## Pull Requests

When submitting a pull request:

1. Keep the change focused.
2. Add or update tests when appropriate.
3. Run the test suite.
4. Run Black and Ruff.
5. Update documentation if the change affects project usage or APIs.
6. Provide a clear description of what changed and why.
