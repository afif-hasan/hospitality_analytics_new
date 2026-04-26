# Architecture

## Pattern: MVC with Modular Codebase

This project follows **MVC (Model-View-Controller)** architecture organized
into self-contained feature modules.

## MVC Mapping

| MVC Role    | File in each module | Responsibility                              |
|-------------|---------------------|---------------------------------------------|
| Model       | `model.py`          | SQLAlchemy ORM — table columns and types    |
| View        | `schemas.py`        | Pydantic — request/response shapes          |
| Controller  | `controller.py`     | FastAPI router — HTTP handling only         |
| Service     | `service.py`        | Business logic — keeps controllers thin     |

The service layer is the one intentional addition beyond pure MVC. It exists
to keep controllers testable and business logic reusable.

## Layer Responsibilities

### Client layer
Swagger UI, curl, Postman, or any HTTP client.

### Middleware layer
Every request passes through:
- `RequestIDMiddleware` — generates a UUID and injects it as `x-request-id`
- `CORSMiddleware` — allows cross-origin requests
- Global exception handlers — converts all errors to clean JSON

### Router layer
FastAPI `APIRouter` instances registered in `main.py`:
- `/auth` — auth_router
- `/transactions` — transactions_router
- `/analytics` — analytics_router

### Service layer
Pure Python classes with static methods. No HTTP knowledge.
All database access goes through here, never directly from controllers.

### Data layer
- SQLAlchemy 2.0 async ORM with `AsyncSession`
- Pydantic v2 for input validation and output serialization
- `asyncpg` driver for PostgreSQL

### Database
PostgreSQL 16 in production and docker-compose.
SQLite with aiosqlite for the test suite.

## Module Structure

Each module follows the same internal structure:
module/
├── model.py       # SQLAlchemy ORM class (the M)
├── schemas.py     # Pydantic models (the V)
├── controller.py  # FastAPI router (the C)
└── service.py     # Business logic (service layer)

## Request Lifecycle
Client
↓
RequestIDMiddleware   (assigns x-request-id)
↓
CORSMiddleware
↓
FastAPI Router        (matches URL, validates auth)
↓
Controller            (parses request, calls service)
↓
Service               (business logic, calls ORM)
↓
SQLAlchemy ORM        (generates SQL)
↓
PostgreSQL            (executes query)
↑
Response flows back up through the same stack

## Bonus Features Implemented

| Feature       | Implementation                                      |
|---------------|-----------------------------------------------------|
| Pagination    | `skip` + `limit` on GET /transactions/ with `total` |
| JWT Auth      | `python-jose` + `bcrypt`, HTTPBearer scheme         |
| Async         | `async def` all routes, `AsyncSession` ORM          |
| Logging       | `structlog` JSON logs with `request_id` per request |
| CSV errors    | Per-row validation, partial success response        |
| Migrations    | Alembic with async-compatible `env.py`              |