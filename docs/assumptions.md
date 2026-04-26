# Assumptions Made

## 1. Authentication scope
All endpoints except `/health`, `/auth/register`, and `/auth/login` require
JWT authentication. This reflects real-world API design where business data
is never publicly accessible.

## 2. Revenue calculation
Revenue per transaction is calculated as `price × quantity`. This represents
the total monetary value of each transaction line item.

## 3. CSV partial success
CSV uploads never fail entirely. Invalid rows are skipped and reported in the
response while valid rows are still imported. This matches the business team
expectation — a single bad row should not block an entire dataset upload.

## 4. Test database
Tests use SQLite instead of PostgreSQL to keep the test suite self-contained
and runnable without any external dependencies. The async SQLAlchemy setup
is identical in both — only the driver changes.

## 5. Docker default environment
The Docker image ships with default environment variables so the recruiter's
exact commands work without extra flags. In production, `SECRET_KEY` and
`DATABASE_URL` must always be overridden via environment variables.

## 6. Database switching
The entire database configuration is driven by the `DATABASE_URL` environment
variable. Switching from PostgreSQL to any other supported database requires
changing only that one value — no code changes needed.

## 7. Pagination defaults
`GET /transactions/` defaults to `skip=0` and `limit=10`. Maximum limit is
capped at 100 to prevent accidental full-table scans.

## 8. Analytics date filters
All analytics endpoints accept optional `start_date` and `end_date` filters.
When omitted, the query runs across all available data.

## 9. Top properties
`GET /analytics/top-properties` always returns a maximum of 3 results ordered
by total revenue descending. This matches the business requirement exactly.

## 10. MVC service layer
A service layer is added between controllers and models. Pure MVC places
business logic in controllers, but in FastAPI this makes routes untestable.
The service layer keeps controllers thin (HTTP only) and makes all business
logic independently unit-testable.