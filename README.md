# local-radar

A backend API and scraping service for aggregating location-based data across many categories (e.g., restaurants, hospitals, parks). This README documents the repository layout, how to run the project locally, important environment variables (names only — do not commit secrets), and notes about the architecture and next steps.

## Quick overview

- Language & framework: Python + FastAPI
- Background workers: Celery (present in project structure and configs)
- Caching: Redis (cache helper present in `cache/redis_cache.py`)
- Database: MongoDB (connection helper in `database/mongo.py`)
- Purpose: Provide an HTTP API (mounted under `/api`) and a set of scrapers organized under `scrapers/` to collect data for many categories.

## Table of contents

- [Project structure](#project-structure)
- [Features](#features)
- [Requirements & prerequisites](#requirements--prerequisites)
- [Environment variables](#environment-variables)
- [Run locally (development)](#run-locally-development)
- [How the code is organized](#how-the-code-is-organized)
- [Adding a new scraper](#adding-a-new-scraper)
- [Notes, TODOs and assumptions](#notes-todos-and-assumptions)
- [Next steps and suggestions](#next-steps-and-suggestions)

## Project structure

Top-level folders and their purpose (high-level):

- `app/` - application logs
- `cache/` - Redis cache helpers (`redis_cache.py`)
- `config/` - configuration for Celery and app (`celery_config.py`, `config.py`)
- `core/` - custom exceptions and logging helpers
- `database/` - MongoDB helper (`mongo.py`)
- `middleware/` - request middleware (`header_validator.py`, `request_logger.py`)
- `models/` - Pydantic / domain models (`models.py`, `scrape_request.py`)
- `routes/` - API router(s) (`api_routes.py`) mounted at `/api`
- `scrapers/` - category-specific scrapers and shared scraper utilities
- `security/` - API key and rate limiting logic
- `services/` - scraping service implementation
- `tasks/` - Celery tasks (`tasks.py`)
- `main.py` - FastAPI application entrypoint

## Features

- REST API (FastAPI) with routers registered from `routes/api_routes.py`.
- Category-based scrapers for many domains under `scrapers/`.
- Redis cache helper and MongoDB persistence.
- Middleware for request logging and header validation.
- Security helpers: API key validation and rate limiting code present.
- Celery support for asynchronous/background scraping tasks.

## Requirements & prerequisites

- Python 3.10+ (assumption; the project uses modern packages). If you need a different interpreter version, adapt accordingly.
- Install dependencies from `requirements.txt`.

Recommended setup (create and activate a virtual environment):

```powershell
# Create a venv and activate (PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Environment variables

This project expects configuration via environment variables or a `.env` file. Do not commit secrets to version control. The repository includes a `.env` example in the workspace; the following variable names are referenced across the codebase and should be set in your environment:

- MONGO_URI
- DATABASE_NAME
- REDIS_HOST
- REDIS_PORT
- REDIS_PASSWORD
- REDIS_SSL
- RATE_LIMIT_CALLS
- RATE_LIMIT_PERIOD
- BLOCK_DURATION
- PERMANENT_BLOCK_THRESHOULD
- PERMANENT_BLOCK_DURATION
- JWT_SECRET_KEY
- JWT_ALGORITHM
- JWT_EXPIRATION_TIME_MINUTES
- JWT_REFRESH_EXPIRATION_TIME_MINUTES
- SECURE_API

Important: never paste real secret values into a public repository. The project repo already lists a `.gitignore` that excludes `.env` and log files.

## Run locally (development)

Start the FastAPI app using Uvicorn (development, auto-reload):

```powershell
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Notes:
- The API routes are included with `app.include_router(api_router, prefix='/api')` in `main.py`.
- `main.py` also registers middleware (`header_validator`, `log_request`).

If you plan to use background tasks with Celery, configure and start a worker using the Celery settings in `config/celery_config.py` (Celery broker/ backend values must be set via env/config). The repository contains Celery-related files but not an explicit run command — adapt to your broker (Redis, RabbitMQ, etc.).

## How the code is organized (details)

- `main.py` — FastAPI app initialization, CORS settings, middleware registration, startup/shutdown hooks. Note: some route handlers and exception handlers in `main.py` appear to be placeholders and may require completion.
- `routes/api_routes.py` — registers API endpoints. All API endpoints are served under the `/api` prefix.
- `scrapers/` — each subfolder implements a scraper for a single category; shared utilities live in `_common.py` and `scraper_config.py`.
- `security/` — contains `api_key_validator.py` and `rate_limiter.py` used to secure endpoints.
- `database/mongo.py` — MongoDB connection wrapper used for persistence.
- `cache/redis_cache.py` — Redis helper for caching.

## Adding a new scraper

1. Add a new folder under `scrapers/` named after the category (e.g. `mycategory/`).
2. Implement the scraper module (follow conventions used by existing scrapers). Check `scrapers/_common.py` and `scraper_config.py` for helper functions and configuration.
3. Expose the scraper or its entrypoint in the same pattern used by other scrapers so the service or tasks can import and run it.

## Notes, TODOs and assumptions

- I intentionally did not include secret values from any `.env` file. Only environment variable names are listed above.
- Observed items that likely need attention in the repository:
	- `main.py` contains route handlers and exception handlers that appear to be placeholders/unimplemented. Confirm and implement them before production use.
	- No unit tests were found in the repository snapshot. Adding tests is recommended.
- Assumptions made:
	- Python 3.10+ is available for development. Adjust as needed.

## Next steps & suggestions

- Implement the missing handlers in `main.py` (root, health, and exception handlers) if not already done.
- Add unit tests for critical pieces: scrapers, services, security middleware.
- Add CI workflow to run linting and tests (the repo already contains `.github/workflows/`).
- Consider adding a short CONTRIBUTING.md and a LICENSE file if you plan to open-source the project.

## Contact / contribution

If you want changes to this README or additional docs (API reference, sample requests, Postman collection), tell me which area to expand and I will update the README accordingly.

---