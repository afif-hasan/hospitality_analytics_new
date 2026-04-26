# API Reference

Base URL: `http://127.0.0.1:8000`

All protected endpoints require:
Authorization: Bearer <your_jwt_token>

---

## Health

### GET /health
Check if the API is running.

**Response 200:**
```json
{ "status": "ok" }
```

---

## Auth

### POST /auth/register
Register a new user.

**Request:**
```json
{
  "email": "admin@hospitality.com",
  "password": "secret123"
}
```

**Response 201:**
```json
{
  "id": 1,
  "email": "admin@hospitality.com",
  "is_active": true,
  "created_at": "2026-01-15T10:00:00Z"
}
```

**Errors:**
- `409` — email already registered
- `422` — invalid email or password too short (min 6 chars)

---

### POST /auth/login
Login and receive a JWT token.

**Request:**
```json
{
  "email": "admin@hospitality.com",
  "password": "secret123"
}
```

**Response 200:**
```json
{
  "access_token": "eyJhbGci...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

**Errors:**
- `401` — invalid email or password

---

### GET /auth/me
Get the currently authenticated user.

**Response 200:**
```json
{
  "id": 1,
  "email": "admin@hospitality.com",
  "is_active": true,
  "created_at": "2026-01-15T10:00:00Z"
}
```

**Errors:**
- `401` — invalid or expired token
- `403` — no token provided

---

## Transactions

### POST /transactions/
Create a single transaction.

**Request:**
```json
{
  "property_name": "Grand Hotel",
  "category": "room booking",
  "price": 150.00,
  "quantity": 2,
  "date": "2026-01-15"
}
```

**Response 201:**
```json
{
  "id": 1,
  "property_name": "Grand Hotel",
  "category": "room booking",
  "price": 150.00,
  "quantity": 2,
  "date": "2026-01-15",
  "created_at": "2026-01-15T10:00:00Z"
}
```

**Validation rules:**
- `price` must be > 0
- `quantity` must be > 0
- `date` must be a valid date string

---

### POST /transactions/bulk
Create multiple transactions in one request.

**Request:**
```json
{
  "transactions": [
    {
      "property_name": "Ocean Resort",
      "category": "food",
      "price": 45.50,
      "quantity": 4,
      "date": "2026-01-16"
    },
    {
      "property_name": "City Inn",
      "category": "service",
      "price": 30.00,
      "quantity": 1,
      "date": "2026-01-17"
    }
  ]
}
```

**Response 201:** Array of created transactions.

---

### POST /transactions/upload-csv
Upload transactions from a CSV file.

**Form data:** `file` — a `.csv` file

**Required CSV columns:**
property_name, category, price, quantity, date

**Response 200:**
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

**Errors:**
- `400` — file is not a .csv
- `400` — missing required columns

---

### GET /transactions/
List transactions with optional filters and pagination.

**Query parameters:**

| Parameter  | Type   | Default | Description                    |
|------------|--------|---------|--------------------------------|
| category   | string | —       | Filter by category             |
| start_date | date   | —       | From date (YYYY-MM-DD)         |
| end_date   | date   | —       | To date (YYYY-MM-DD)           |
| skip       | int    | 0       | Pagination offset              |
| limit      | int    | 10      | Page size (max 100)            |

**Response 200:**
```json
{
  "items": [
    {
      "id": 1,
      "property_name": "Grand Hotel",
      "category": "room booking",
      "price": 150.00,
      "quantity": 2,
      "date": "2026-01-15",
      "created_at": "2026-01-15T10:00:00Z"
    }
  ],
  "total": 42,
  "skip": 0,
  "limit": 10
}
```

---

## Analytics

All analytics endpoints accept optional `start_date` and `end_date`
query parameters (`YYYY-MM-DD`).

---

### GET /analytics/total-sales
Get total revenue and transaction count.

**Response 200:**
```json
{
  "total_revenue": 12450.50,
  "total_transactions": 87,
  "average_order_value": 143.11
}
```

---

### GET /analytics/top-properties
Get the top 3 properties by total revenue.

**Response 200:**
```json
[
  {
    "rank": 1,
    "property_name": "Grand Hotel",
    "total_revenue": 5200.00,
    "total_transactions": 24
  },
  {
    "rank": 2,
    "property_name": "Ocean Resort",
    "total_revenue": 4100.50,
    "total_transactions": 18
  },
  {
    "rank": 3,
    "property_name": "Mountain Lodge",
    "total_revenue": 3150.00,
    "total_transactions": 15
  }
]
```

---

### GET /analytics/category-breakdown
Get revenue and transaction count broken down by category.

**Response 200:**
```json
[
  {
    "category": "room booking",
    "total_revenue": 7500.00,
    "total_transactions": 40
  },
  {
    "category": "food",
    "total_revenue": 3200.50,
    "total_transactions": 30
  },
  {
    "category": "service",
    "total_revenue": 1750.00,
    "total_transactions": 17
  }
]
```