# Entity Relationship Diagram

## Tables

### users
| Column           | Type         | Constraints                  |
|------------------|--------------|------------------------------|
| id               | INTEGER      | PRIMARY KEY, AUTOINCREMENT   |
| email            | VARCHAR(255) | NOT NULL, UNIQUE, INDEX      |
| hashed_password  | VARCHAR(255) | NOT NULL                     |
| is_active        | BOOLEAN      | NOT NULL, DEFAULT TRUE       |
| created_at       | DATETIME     | NOT NULL                     |

### transactions
| Column        | Type         | Constraints                  |
|---------------|--------------|------------------------------|
| id            | INTEGER      | PRIMARY KEY, AUTOINCREMENT   |
| property_name | VARCHAR(120) | NOT NULL, INDEX              |
| category      | VARCHAR(60)  | NOT NULL, INDEX              |
| price         | FLOAT        | NOT NULL, > 0                |
| quantity      | INTEGER      | NOT NULL, > 0                |
| date          | DATE         | NOT NULL, INDEX              |
| created_at    | DATETIME     | NOT NULL                     |

### alembic_version
| Column      | Type        | Constraints  |
|-------------|-------------|--------------|
| version_num | VARCHAR(32) | PRIMARY KEY  |

## Relationships
users ──────────────── transactions
(no FK relationship)
Users authenticate to access the API.
Transactions are not owned by a specific user —
they represent company-wide operational data.

## Indexes

| Table        | Column        | Type   | Purpose                        |
|--------------|---------------|--------|--------------------------------|
| users        | email         | UNIQUE | Fast login lookup, uniqueness  |
| transactions | property_name | INDEX  | Filter/group by property       |
| transactions | category      | INDEX  | Filter/group by category       |
| transactions | date          | INDEX  | Date range filtering           |

## Notes

- The `analytics` module has no dedicated table. It queries the
  `transactions` table using SQLAlchemy aggregation functions
  (`func.sum`, `func.count`, `group_by`).
- All timestamps are stored in UTC.
- Revenue is derived at query time as `price × quantity` — it is
  never stored as a separate column.