# Contributing

Thank you for your interest in contributing to Knowledge Assistant.

## Local Setup

Follow the setup instructions in the [README](README.md), under **Running the Project**.

The project is currently developed and tested using Docker, PostgreSQL, Django, and Django REST Framework.

## Branching

This project currently has a solo maintainer, so direct commits to `main` are acceptable during development.

For external contributions, please use a feature or fix branch:

- `feature/<short-description>`
- `fix/<short-description>`

Pull requests are welcome as the project develops.

## Code Style

The project uses:

- **Black** for Python formatting
- **Ruff** for linting

Run formatting with:

```bash
docker compose exec web black .