# Project Structure
hospitality-analytics/
│
├── app/                            # Application source code
│   ├── main.py                     # FastAPI app factory, router registration,
│   │                               # middleware setup, lifespan events
│   │
│   ├── core/                       # Shared infrastructure (not a module)
│   │   ├── config.py               # pydantic-settings — reads all env variables
│   │   ├── database.py             # Async SQLAlchemy engine, session factory,
│   │   │                           # Base ORM class, init_db()
│   │   ├── dependencies.py         # get_db() and get_current_user() FastAPI deps
│   │   ├── security.py             # bcrypt hashing, JWT encode/decode
│   │   ├── middleware.py           # RequestIDMiddleware — injects x-request-id
│   │   ├── logging.py              # structlog JSON processor configuration
│   │   └── exceptions.py          # Global HTTP exception handlers
│   │
│   └── modules/                    # Feature modules (MVC pattern)
│       │
│       ├── auth/                   # Authentication module
│       │   ├── model.py            # M — User SQLAlchemy ORM model
│       │   ├── schemas.py          # V — UserCreate, UserOut, TokenOut, LoginRequest
│       │   ├── controller.py       # C — /auth/register, /auth/login, /auth/me
│       │   └── service.py          # register_user(), authenticate_user()
│       │
│       ├── transactions/           # Transaction management module
│       │   ├── model.py            # M — Transaction SQLAlchemy ORM model
│       │   ├── schemas.py          # V — TransactionCreate, TransactionOut,
│       │   │                       #     BulkCreateRequest, CSVUploadResult,
│       │   │                       #     PaginatedTransactions
│       │   ├── controller.py       # C — POST /, POST /bulk, POST /upload-csv,
│       │   │                       #     GET /
│       │   └── service.py          # create_one(), create_bulk(),
│       │                           # bulk_from_csv(), get_all()
│       │
│       └── analytics/             # Analytics module
│           ├── schemas.py          # V — TotalSalesOut, TopPropertyOut,
│           │                       #     CategoryBreakdownOut
│           ├── controller.py       # C — GET /total-sales, GET /top-properties,
│           │                       #     GET /category-breakdown
│           └── service.py          # get_total_sales(), get_top_properties(),
│                                   # get_category_breakdown()
│
├── alembic/                        # Database migration system
│   ├── env.py                      # Async-compatible Alembic environment
│   ├── script.py.mako              # Migration file template
│   └── versions/
│       └── xxxx_initial_tables.py  # Initial users + transactions tables
│
├── tests/                          # Automated test suite
│   ├── conftest.py                 # Fixtures: test engine, db session,
│   │                               # async client, auth headers
│   ├── modules/
│   │   ├── test_auth.py            # 9 tests — register, login, /me
│   │   ├── test_transactions.py    # 8 tests — CRUD, bulk, filters, pagination
│   │   ├── test_csv_upload.py      # 6 tests — valid, mixed, wrong format
│   │   └── test_analytics.py      # 6 tests — total sales, top properties,
│   │                               #            category breakdown, date filters
│   └── fixtures/
│       ├── valid_sample.csv        # 10 clean rows for testing
│       └── mixed_sample.csv        # 7 valid + 3 broken rows for error testing
│
├── docs/                           # Project documentation
│   ├── er_diagram.md               # Database schema and relationships
│   ├── project_structure.md        # This file
│   ├── api_reference.md            # Full API documentation with examples
│   ├── architecture.md             # MVC + modular architecture explanation
│   └── assumptions.md              # Design decisions and reasoning
│
├── data/                           # SQLite database for tests (gitignored)
│   └── .gitkeep
│
├── .env                            # Local environment variables (gitignored)
├── .env.example                    # Environment variable template
├── .gitignore                      # Ignored files
├── .dockerignore                   # Files excluded from Docker build
├── alembic.ini                     # Alembic configuration
├── pyproject.toml                  # Pytest configuration
├── requirements.txt                # Pinned Python dependencies
├── Dockerfile                      # Single-container Docker image
├── docker-compose.yml              # Full stack (web + PostgreSQL)
└── README.md                       # Project overview and setup guide

## Design Principles

### Why modular?
Each module (`auth`, `transactions`, `analytics`) is fully self-contained.
Deleting any module folder breaks zero code in other modules. Adding a new
module means creating one new folder and one line in `main.py`.

### Why a service layer?
Pure MVC places business logic in controllers. In FastAPI this makes route
handlers impossible to unit test without spinning up HTTP. Services keep
controllers thin (HTTP only) and all business logic independently testable.

### Why `core/` is not a module?
`core/` has no Model, View, or Controller. It only provides shared
infrastructure that every module depends on. It is infrastructure, not a feature.