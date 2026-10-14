# Database Design Document (DDD)

This document describes the PostgreSQL schema used by this project. The application is now connected to PostgreSQL — `models/user.py` and `models/announcement.py` read and write directly to the tables below via `models/db.py`. Data persists across restarts (`docker compose down` / `up`).

## Status

- **Database engine:** PostgreSQL — connected and in use
- **Current storage:** The `users` and `announcements` tables, queried directly via `psycopg2` (no ORM)
- **Scope:** Only the two entities the app manages — `users` and `announcements`

## Schema Overview

Each entity below maps directly to one of the existing in-memory models, so moving to a real database later should not require changing what the app stores — only how it stores it.

### Table: `users`

Backs the `User` model (`models/user.py`). Represents one alumni record.

| Column            | Type           | Constraints                | Notes                                   |
|-------------------|----------------|-----------------------------|------------------------------------------|
| `id`              | `SERIAL`       | `PRIMARY KEY`                | Auto-incrementing, matches today's `_next_id` behavior |
| `first_name`      | `VARCHAR(100)` | `NOT NULL`                   |                                           |
| `last_name`       | `VARCHAR(100)` | `NOT NULL`                   |                                           |
| `graduation_year` | `INTEGER`      | `NOT NULL`                   |                                           |
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
| `date`    | `DATE`         | `NOT NULL`        |                                       |

```sql
CREATE TABLE announcements (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    date DATE NOT NULL
);
```

## Relationships

There are currently no relationships between `users` and `announcements` — they are independent entities, matching how the two models work today. A future iteration could add a `created_by` foreign key on `announcements` pointing to `users.id` if announcements need an author, but that is out of scope for now.

## App ↔ Database Wiring

`models/db.py` exposes `get_connection()`, which opens a `psycopg2` connection using the `DATABASE_URL` environment variable (set via `.env` / `docker-compose.yml`) and returns rows as plain dictionaries (`RealDictCursor`), so controllers and templates can use `user["first_name"]` / `user.first_name` interchangeably.

`models/user.py` and `models/announcement.py` each open a new connection per method call (`create`, `get_all`, `get_by_id`, `update`, `patch`, `delete`), run the relevant SQL, `commit()` after any write, then close the connection. Controllers were **not changed** — they still call `User.create(...)`, `User.get_all()`, etc. exactly as before; only what happens inside those methods changed, from an in-memory list to real SQL. This is the MVC boundary doing its job: swapping storage didn't require touching a single controller or template.

Verified behavior: creating a record, running `docker compose down` then `docker compose up`, and the record is still there — the "forgetting test" from before no longer applies to `users`/`announcements`.

## Migrations

The `CREATE TABLE` statements above live in `migrations/001_create_tables.sql`. This file is mounted into the `db` container at `/docker-entrypoint-initdb.d/` (see `docker-compose.yml`), which is a built-in PostgreSQL image feature: on the **very first** startup of a fresh database (empty volume), it automatically runs every `.sql` file in that folder, in alphabetical order. That's why the file is named `001_...` — a future `002_...sql` would run right after it.

**Important:** this only runs once, when the database is created from scratch. If the volume already has data in it, adding a new migration file will **not** run it automatically. During development, the simplest way to re-apply migrations is to wipe the volume and start fresh:

```bash
docker compose down -v   # -v also removes the postgres_data volume
docker compose up --build
```

Verify the tables exist with:

```bash
docker exec alumni-web-programming-db-1 psql -U alumni -d alumni -c "\dt"
```

## Factory & Seed

Two separate concepts, often confused:

- **Factory** (`factories/user_factory.py`, `factories/announcement_factory.py`) — a class whose only job is to *generate* one fake-but-realistic record (via the [Faker](https://faker.readthedocs.io/) library). It does not touch the database at all; calling `UserFactory.create()` just returns a Python dict.
- **Seed** (`seed.py`) — a script that calls the factories in a loop and actually `INSERT`s the results into PostgreSQL via `psycopg2`, then `commit()`s the transaction.

Run it (containers must already be up):

```bash
docker compose exec web python seed.py
```

This inserts 10 fake users and 5 fake announcements directly into the `users` and `announcements` tables. It connects using the same `DATABASE_URL` the `web` container already has from `.env` — no extra configuration needed.

Since the app is now wired to the same database (see App ↔ Database Wiring above), seeded rows appear immediately on `/users`, `/announcements`, and their `/api/...` equivalents — no restart needed.
