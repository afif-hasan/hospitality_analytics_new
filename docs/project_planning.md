# Project Planning

## Overview

This document outlines the planning process followed to design and build
the Hospitality Analytics Platform — from requirements analysis through
to final submission.

---

## 1. Requirements Analysis

### Functional Requirements

| # | Requirement                              | Priority  | Status |
|---|------------------------------------------|-----------|--------|
| 1 | Accept transaction data via API          | Must have | ✅ Done |
| 2 | Bulk upload via JSON                     | Must have | ✅ Done |
| 3 | CSV file upload with Swagger support     | Must have | ✅ Done |
| 4 | Store data in a database                 | Must have | ✅ Done |
| 5 | Filter transactions by category and date | Must have | ✅ Done |
| 6 | Total sales analytics endpoint           | Must have | ✅ Done |
| 7 | Top 3 properties by revenue              | Must have | ✅ Done |
| 8 | Run inside Docker container              | Must have | ✅ Done |

### Non-Functional Requirements

| # | Requirement                              | Priority  | Status |
|---|------------------------------------------|-----------|--------|
| 1 | Clean and structured code                | Must have | ✅ Done |
| 2 | Proper use of FastAPI and SQLAlchemy     | Must have | ✅ Done |
| 3 | Input validation                         | Must have | ✅ Done |
| 4 | Error handling for CSV upload            | Must have | ✅ Done |
| 5 | Logical API design                       | Must have | ✅ Done |

### Optional Enhancements (Bonus)

| # | Enhancement                              | Status |
|---|------------------------------------------|--------|
| 1 | Pagination for transaction listing       | ✅ Done |
| 2 | JWT Authentication                       | ✅ Done |
| 3 | Async endpoints                          | ✅ Done |
| 4 | Logging                                  | ✅ Done |
| 5 | Graceful invalid CSV row handling        | ✅ Done |

---

## 2. Technology Decisions

### Why FastAPI?
- Native async support via Python's `asyncio`
- Automatic Swagger UI generation — critical for the CSV upload requirement
- Pydantic integration for automatic input validation
- Dependency injection system makes testing clean

### Why PostgreSQL over SQLite?
- Production-grade relational database
- Better concurrency handling with multiple connections
- docker-compose setup demonstrates full-stack deployment knowledge
- SQLite is still used for the test suite to keep tests self-contained

### Why SQLAlchemy 2.0 async?
- Modern async ORM that pairs natively with FastAPI's async model
- `Mapped[]` type annotations (SQLAlchemy 2.0 style)
- Single session factory shared across all modules

### Why Alembic?
- Production-grade migration management
- Demonstrates that `create_all()` is not acceptable in real projects

### Why bcrypt directly over passlib?
- `passlib` has a known compatibility issue with `bcrypt` 4.x on Python 3.12
- Direct `bcrypt` usage is cleaner and has no version conflicts
- Same security standard, fewer dependencies

### Why structlog?
- JSON-structured logs are machine-parseable
- `request_id` injected per request enables distributed tracing
- Shows production logging awareness beyond basic `print()` statements

### Why MVC with modular codebase?
- Each module is independently removable and testable
- Controllers stay thin — HTTP only
- Services hold business logic and are testable without HTTP
- New features can be added as new modules without touching existing code

---

## 3. Database Design

### Entities identified
After analyzing the requirements, two entities were identified:

**Transaction** — the core business entity storing all operational data.
Fields: `id`, `property_name`, `category`, `price`, `quantity`, `date`, `created_at`

**User** — required for JWT authentication (bonus feature).
Fields: `id`, `email`, `hashed_password`, `is_active`, `created_at`

### Indexing strategy
Indexes were added on columns most likely to appear in WHERE clauses:
- `transactions.property_name` — analytics grouping
- `transactions.category` — filter queries
- `transactions.date` — date range filtering
- `users.email` — login lookup (also UNIQUE)

### No foreign key between User and Transaction
Transactions represent company-wide operational data, not user-owned records.
Any authenticated user can read and write all transactions.

---

## 4. API Design Decisions

### URL structure
/auth/*          — authentication
/transactions/*  — transaction management
/analytics/*     — business insights
/health          — infrastructure health check

### HTTP status codes used
| Code | When used                              |
|------|----------------------------------------|
| 200  | Successful GET, CSV upload result      |
| 201  | Successful POST (resource created)     |
| 400  | Bad request (wrong file type, etc.)    |
| 401  | Invalid or expired token               |
| 403  | No token provided                      |
| 409  | Conflict (duplicate email)             |
| 422  | Validation error (Pydantic)            |
| 500  | Unexpected server error                |

### Pagination design
`GET /transactions/` uses `skip` and `limit` query parameters.
The response always includes `total` so clients can calculate page count
without a separate count request.

### Analytics design
All three analytics endpoints accept optional date filters so the business
team can generate reports for any time period without needing multiple endpoints.

---

## 5. Architecture Decision

### Pattern chosen: MVC with modular codebase

**Alternatives considered:**

| Pattern             | Rejected reason                                        |
|---------------------|--------------------------------------------------------|
| Pure MVC            | Business logic in controllers makes testing hard       |
| Layered (N-tier)    | Less modular — harder to add/remove features           |
| Microservices       | Over-engineered for this scale                         |
| Repository pattern  | Adds an extra abstraction layer without clear benefit  |

**Final decision:** MVC + service layer per module. The service layer is the
one addition beyond pure MVC. It keeps controllers to HTTP-only concerns and
makes all business logic independently testable.

---

## 6. Development Phases

| Phase | Task                          | Description                                      |
|-------|-------------------------------|--------------------------------------------------|
| 1     | Environment setup             | venv, requirements.txt, .env, .gitignore         |
| 2     | Core foundation               | config, database, logging, security, middleware  |
| 3     | Database models               | Transaction and User SQLAlchemy ORM models       |
| 4     | Alembic migrations            | Initial migration generating users + transactions|
| 5     | Pydantic schemas              | All input/output schemas for all modules         |
| 6     | Auth module                   | Register, login, /me endpoints                   |
| 7     | Transactions module           | CRUD, bulk insert, CSV upload, filtered listing  |
| 8     | Analytics module              | Total sales, top properties, category breakdown  |
| 9     | Middleware and exceptions      | Request ID, CORS, global error handlers          |
| 10    | Docker                        | Dockerfile, docker-compose, volume setup         |
| 11    | Tests                         | 29 tests across auth, transactions, CSV, analytics|
| 12    | Documentation                 | README, docs folder, project planning            |

---

## 7. Testing Strategy

### Test database
SQLite with `aiosqlite` — no external dependencies needed to run tests.

### Test isolation
Each test function gets a fresh database session via pytest fixtures.
The session is rolled back after every test to prevent data leaking
between tests.

### Coverage areas

| Area             | Tests | What is covered                               |
|------------------|-------|-----------------------------------------------|
| Auth             | 9     | Register, login, /me, invalid inputs, no token|
| Transactions     | 8     | Create, bulk, filters, pagination, validation |
| CSV upload       | 6     | Valid, mixed rows, wrong format, missing cols |
| Analytics        | 6     | All 3 endpoints, date filters, no auth        |
| **Total**        | **29**| **100% pass rate**                            |

### Test fixtures
- `test_engine` — session-scoped SQLite engine
- `db_session` — function-scoped session with rollback
- `client` — async HTTP client with DB override
- `auth_headers` — pre-authenticated headers for protected routes

---

## 8. Security Considerations

| Concern              | Solution                                          |
|----------------------|---------------------------------------------------|
| Password storage     | bcrypt hashing — never stored in plain text       |
| Token security       | JWT with expiry, signed with SECRET_KEY           |
| Secret management    | All secrets via environment variables, never hardcoded |
| Input validation     | Pydantic validates every incoming request         |
| SQL injection        | SQLAlchemy ORM — parameterized queries only       |
| Non-root Docker user | `appuser` created in Dockerfile, no root access  |

---

## 9. Known Limitations

| Limitation                        | Notes                                              |
|-----------------------------------|----------------------------------------------------|
| No role-based access control      | All authenticated users have equal access          |
| No refresh tokens                 | JWT expires and user must log in again             |
| Docker build requires network     | `--network host` needed on some Linux configurations |
| Single container needs external DB| Use docker-compose for zero-config local deployment |

---

## 10. Future Improvements

| Improvement                  | Description                                      |
|------------------------------|--------------------------------------------------|
| Role-based access control    | Admin vs read-only user roles                    |
| Refresh tokens               | Longer sessions without re-login                 |
| Monthly trend analytics      | Revenue over time endpoint                       |
| Property-level analytics     | Drill-down endpoint per property                 |