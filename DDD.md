# Database Design Document (DDD)

This document describes the **planned** PostgreSQL schema for this project. The application does **not** use a database yet — all data currently lives in memory (see `models/user.py` and `models/announcement.py`) and is lost whenever the process restarts. This document exists to plan ahead: once a real database is wired up, the tables below are the minimum needed to cover what the app already does.

## Status

- **Database engine:** PostgreSQL (planned, not yet connected)
- **Current storage:** In-memory Python lists, reset on every restart
- **Scope:** Only the two entities the app already manages — `users` and `announcements`

## Schema Overview

Each entity below maps directly to one of the existing in-memory models, so moving to a real database later should not require changing what the app stores — only how it stores it.

### Table: `users`

Backs the `User` model (`models/user.py`). Represents one alumni record.

| Column            | Type           | Constraints                | Notes                                   |
|-------------------|----------------|-----------------------------|------------------------------------------|
| `id`              | `SERIAL`       | `PRIMARY KEY`                | Auto-incrementing, matches today's `_next_id` behavior |
| `first_name`      | `VARCHAR(100)` | `NOT NULL`                   |                                           |
| `last_name`       | `VARCHAR(100)` | `NOT NULL`                   |                                           |
| `graduation_year` | `INTEGER`      | `NOT NULL`                   | Stored as text today; should become a real integer in the database |
| `email`           | `VARCHAR(255)` | `NOT NULL`, `UNIQUE`         | Two alumni records should not share an email |

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    graduation_year INTEGER NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE
);
```

### Table: `announcements`

Backs the `Announcement` model (`models/announcement.py`). Represents one announcement/duyuru.

| Column    | Type           | Constraints     | Notes                              |
|-----------|----------------|------------------|--------------------------------------|
| `id`      | `SERIAL`       | `PRIMARY KEY`     | Auto-incrementing                    |
| `title`   | `VARCHAR(200)` | `NOT NULL`        |                                       |
| `content` | `TEXT`         | `NOT NULL`        | Longer free text, unlike title       |
| `date`    | `DATE`         | `NOT NULL`        | Stored as text today; should become a real `DATE` in the database |

```sql
CREATE TABLE announcements (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    date DATE NOT NULL
);
```

## Relationships

There are currently no relationships between `users` and `announcements` — they are independent entities, matching how the two models work today (each has its own standalone in-memory list). A future iteration could add a `created_by` foreign key on `announcements` pointing to `users.id` if announcements need an author, but that is out of scope for now.

## Migration Notes (for later)

When the database is actually introduced:

- Replace the `_users` / `_announcements` in-memory lists with real queries (e.g. via SQLAlchemy or `psycopg2`).
- Keep the `User.create/get_all/get_by_id/update/patch/delete` and `Announcement` equivalents as the public interface — controllers should not need to change, only what happens inside the Model methods.
- `graduation_year` and `date` are currently plain strings coming from HTML form fields; they should be validated/converted to `INTEGER` and `DATE` respectively before being inserted into PostgreSQL.

## Infrastructure Already in Place

`docker-compose.yml` already defines a `db` service (`postgres:16`, with `POSTGRES_USER/PASSWORD/DB` all set to `alumni`, data persisted in a named volume) and passes the `web` service a `DATABASE_URL` environment variable pointing to it. The database container runs and accepts connections, but `app.py` does not read `DATABASE_URL` or connect to it yet — that wiring is the next step once the models above are implemented with real queries.
