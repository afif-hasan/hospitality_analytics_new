# Hospitality Analytics Platform

A lightweight backend service for the hospitality industry that allows storing,
retrieving, and analyzing transaction data across hotels, resorts, and restaurants.

## Tech Stack

- **Framework**: FastAPI (async)
- **Database**: PostgreSQL with SQLAlchemy 2.0 (async ORM)
- **Migrations**: Alembic
- **Auth**: JWT (python-jose + bcrypt)
- **Validation**: Pydantic v2
- **Logging**: structlog (structured JSON logs with request_id)
- **Containerization**: Docker + docker-compose

## Architecture

This project follows **MVC architecture with a modular codebase**. Each feature
(auth, transactions, analytics) is a self-contained module with its own Model,
View (schema), Controller (router), and Service (business logic).
app/
├── core/          # Shared infrastructure (config, db, security, middleware)
└── modules/
├── auth/          # User registration, login, JWT
├── transactions/  # CRUD, bulk insert, CSV upload
└── analytics/     # Aggregation queries and business insights

See `docs/architecture.md` for the full breakdown.

## Features

- JWT-protected API endpoints
- Single and bulk transaction creation
- CSV file upload with per-row error handling
- Paginated transaction listing with filters
- Business analytics (total sales, top properties, category breakdown)
- Request ID middleware (every response includes `x-request-id`)
- Docker + docker-compose support
- 29 automated tests (100% pass rate)
- Alembic database migrations

## Getting Started

### Prerequisites

- Python 3.12+
- PostgreSQL 16
- Docker (optional)

### Local Development

**1. Clone the repository**

```bash
git clone https://github.com/your-username/hospitality-analytics.git
cd hospitality-analytics
```

**2. Create virtual environment**

```bash
python3 -m venv venv
source venv/bin/activate
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**4. Set up environment variables**

```bash
cp .env.example .env
```

Edit `.env` with your PostgreSQL credentials:

```env
DATABASE_URL=postgresql+asyncpg://hospitality_user:hospitality_pass@localhost:5432/hospitality_db
SECRET_KEY=your-super-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=60
DEBUG=True
```

**5. Set up PostgreSQL**

```bash
sudo -u postgres psql
```

```sql
CREATE USER hospitality_user WITH PASSWORD 'hospitality_pass';
CREATE DATABASE hospitality_db OWNER hospitality_user;
GRANT ALL PRIVILEGES ON DATABASE hospitality_db TO hospitality_user;
\q
```

**6. Run database migrations**

```bash
alembic upgrade head
```

**7. Start the server**

```bash
uvicorn app.main:app --reload
```

API is available at `http://127.0.0.1:8000`
Swagger UI is available at `http://127.0.0.1:8000/docs`

---

## Running with Docker

### Recommended — docker-compose (full stack)

This is the correct way to run the project. Docker handles all networking
internally — no IP addresses or external PostgreSQL needed.

```bash
docker-compose up --build
```

This automatically:
- Starts a PostgreSQL 16 container
- Runs Alembic migrations
- Starts the FastAPI server on port 8000

API available at `http://127.0.0.1:8000`
Swagger UI at `http://127.0.0.1:8000/docs`

To stop:
```bash
docker-compose down
```

To stop and remove all data:
```bash
docker-compose down -v
```

---

### Single container (recruiter command)

The recruiter's exact commands also work. You must supply `DATABASE_URL`
pointing to an accessible PostgreSQL instance:

```bash
docker build -t fastapi-app .

docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/dbname \
  -e SECRET_KEY=your-secret-key \
  fastapi-app
```

> Note: For local development, use docker-compose instead. The single
> container command requires an externally accessible PostgreSQL instance.

## API Endpoints

### Health

| Method | Endpoint  | Description      | Auth |
|--------|-----------|------------------|------|
| GET    | /health   | Health check     | No   |

### Auth

| Method | Endpoint        | Description              | Auth |
|--------|-----------------|--------------------------|------|
| POST   | /auth/register  | Register a new user      | No   |
| POST   | /auth/login     | Login and get JWT token  | No   |
| GET    | /auth/me        | Get current user         | Yes  |

### Transactions

| Method | Endpoint                      | Description                    | Auth |
|--------|-------------------------------|--------------------------------|------|
| POST   | /transactions/                | Create single transaction      | Yes  |
| POST   | /transactions/bulk            | Create multiple transactions   | Yes  |
| POST   | /transactions/upload-csv      | Upload transactions via CSV    | Yes  |
| GET    | /transactions/                | List transactions with filters | Yes  |

#### GET /transactions/ — Query Parameters

| Parameter  | Type   | Description                        |
|------------|--------|------------------------------------|
| category   | string | Filter by category                 |
| start_date | date   | Filter from date (YYYY-MM-DD)      |
| end_date   | date   | Filter to date (YYYY-MM-DD)        |
| skip       | int    | Pagination offset (default: 0)     |
| limit      | int    | Page size (default: 10, max: 100)  |

### Analytics

| Method | Endpoint                        | Description                    | Auth |
|--------|---------------------------------|--------------------------------|------|
| GET    | /analytics/total-sales          | Total revenue and count        | Yes  |
| GET    | /analytics/top-properties       | Top 3 properties by revenue    | Yes  |
| GET    | /analytics/category-breakdown   | Revenue breakdown by category  | Yes  |

All analytics endpoints accept optional `start_date` and `end_date` query parameters.

---

## CSV Upload Format

The CSV file must include these exact column headers:
property_name,category,price,quantity,date
Grand Hotel,room booking,150.00,2,2026-01-15
Ocean Resort,food,45.50,4,2026-01-16

- `price` must be greater than 0
- `quantity` must be a positive integer
- `date` must be in `YYYY-MM-DD` format
- Invalid rows are skipped and reported in the response — the upload never fails entirely

### Example CSV Response

```json
{
  "imported": 8,
  "skipped": 2,
  "errors": [
    { "row": 4, "error": "price must be greater than 0" },
    { "row": 7, "error": "Invalid isoformat string: 'bad-date'" }
  ]
}
```

---

## Authentication

All protected endpoints require a Bearer token in the Authorization header.

**Register:**

```bash
curl -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@hospitality.com", "password": "secret123"}'
```

**Login:**

```bash
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@hospitality.com", "password": "secret123"}'
```

**Use the token:**

```bash
curl http://127.0.0.1:8000/transactions/ \
  -H "Authorization: Bearer <your_token>"
```

---

## Running Tests

```bash
pytest tests/ -v
```

Tests use an in-memory SQLite database — no PostgreSQL required to run tests.

**Current test results: 29/29 passed**
tests/modules/test_analytics.py        6 passed
tests/modules/test_auth.py             9 passed
tests/modules/test_csv_upload.py       6 passed
tests/modules/test_transactions.py     8 passed

---

## Assumptions Made

1. **Authentication is required** for all write and read endpoints except
   `/health`, `/auth/register`, and `/auth/login`. This matches real-world
   business API design where data access is controlled.

2. **SQLite is used for tests** to keep the test suite self-contained and
   runnable without a PostgreSQL instance.

3. **CSV uploads never abort entirely** — invalid rows are collected and
   returned in the response while valid rows are still imported. This matches
   the business team's expectation of partial success.

4. **PostgreSQL is used in production** (both local and Docker) while the
   `DATABASE_URL` environment variable makes it trivial to switch databases
   by changing a single config value.

5. **The Docker image uses default environment variables** so the recruiter's
   exact commands (`docker build` and `docker run`) work without additional flags.
   In production, `SECRET_KEY` should always be overridden via environment variable.

6. **Revenue is calculated as `price × quantity`** per transaction, which
   represents the total value of each transaction line.

---

## Project Documentation

See the `docs/` folder for:

- `er_diagram.md` — Entity relationship diagram
- `project_structure.md` — Full folder structure with explanations
- `api_reference.md` — Detailed API documentation with examples
- `architecture.md` — MVC + modular architecture breakdown
- `assumptions.md` — Design decisions and reasoning