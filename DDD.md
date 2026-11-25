# Database Design Document (DDD)

This document describes the PostgreSQL schema used by this project. The application is now connected to PostgreSQL — `models/user.py`, `models/announcement.py`, `models/job_posting.py`, and `models/job_application.py` all read and write directly to the tables below via `models/db.py`. Data persists across restarts (`docker compose down` / `up`).

## Status

- **Database engine:** PostgreSQL — connected and in use
- **Current storage:** `users`, `announcements`, `job_postings`, and `job_applications`, all queried directly via `psycopg2` (no ORM)
- **Scope:** All four tables are both designed here and implemented as models (see "App ↔ Database Wiring" below)

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
| `role`            | `VARCHAR(20)`  | `NOT NULL`, `DEFAULT 'alumni'`, `CHECK (role IN ('alumni', 'student'))` | Added in `migrations/003_...sql` — see **User Roles & Permissions** below |
| `password_hash`   | `VARCHAR(255)` | nullable                     | Added in the same migration. Nullable because seeded/demo users (created via `User.create`, not `User.register`) have no login credentials — only accounts created through `/register` get one |
| `staff_role`      | `VARCHAR(20)`  | nullable, `CHECK (staff_role IN ('admin', 'moderator'))` | Added in `migrations/004_...sql`. `NULL` = no elevated privileges. Never set by the user themselves — only via `/admin/users/<id>/role`, admin-only |
| `status`          | `VARCHAR(20)`  | `NOT NULL`, `DEFAULT 'approved'`, `CHECK (status IN ('pending', 'approved'))` | Added in `migrations/005_...sql`. `/register` inserts `'pending'` explicitly; everything else (factories, `/admin/users/new`) rides the default |

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    graduation_year INTEGER NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE
);

-- migrations/003_add_user_roles_and_auth.sql
ALTER TABLE users
    ADD COLUMN role VARCHAR(20) NOT NULL DEFAULT 'alumni' CHECK (role IN ('alumni', 'student')),
    ADD COLUMN password_hash VARCHAR(255);

-- migrations/004_add_staff_roles.sql
ALTER TABLE users
    ADD COLUMN staff_role VARCHAR(20) CHECK (staff_role IN ('admin', 'moderator'));

-- migrations/005_add_permissions_and_approval_status.sql
ALTER TABLE users
    ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT 'approved' CHECK (status IN ('pending', 'approved'));
```

### Table: `announcements`

Backs the `Announcement` model (`models/announcement.py`). Represents one announcement/duyuru.

| Column    | Type           | Constraints     | Notes                              |
|-----------|----------------|------------------|--------------------------------------|
| `id`      | `SERIAL`       | `PRIMARY KEY`     | Auto-incrementing                    |
| `title`   | `VARCHAR(200)` | `NOT NULL`        |                                       |
| `content` | `TEXT`         | `NOT NULL`        | Longer free text, unlike title       |
| `date`    | `DATE`         | `NOT NULL`        |                                       |
| `status`  | `VARCHAR(20)`  | `NOT NULL`, `DEFAULT 'approved'`, `CHECK (status IN ('pending', 'approved'))` | Added in `migrations/005_...sql` — see **Approval workflow** below |

```sql
CREATE TABLE announcements (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    date DATE NOT NULL
);

-- migrations/005_add_permissions_and_approval_status.sql
ALTER TABLE announcements
    ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT 'approved' CHECK (status IN ('pending', 'approved'));
```

### Table: `job_postings`

A new entity: one job posting shared by an alumnus. This is the first table with a relationship to another table — see **Relationships** below.

| Column        | Type           | Constraints                          | Notes                                              |
|---------------|----------------|----------------------------------------|------------------------------------------------------|
| `id`          | `SERIAL`       | `PRIMARY KEY`                          | Auto-incrementing                                    |
| `title`       | `VARCHAR(200)` | `NOT NULL`                             | e.g. "Backend Developer"                            |
| `company`     | `VARCHAR(150)` | `NOT NULL`                             |                                                       |
| `description` | `TEXT`         | `NOT NULL`                             | Full job description                                 |
| `location`    | `VARCHAR(150)` | `NOT NULL`                             |                                                       |
| `posted_by`   | `INTEGER`      | `NOT NULL`, `REFERENCES users(id)`     | The alumnus who posted this job — the "many" side of the one-to-many relationship with `users` |
| `posted_date` | `DATE`         | `NOT NULL`                             |                                                       |
| `status`      | `VARCHAR(20)`  | `NOT NULL`, `DEFAULT 'approved'`, `CHECK (status IN ('pending', 'approved'))` | Added in `migrations/005_...sql` — see **Approval workflow** below |

```sql
CREATE TABLE job_postings (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    company VARCHAR(150) NOT NULL,
    description TEXT NOT NULL,
    location VARCHAR(150) NOT NULL,
    posted_by INTEGER NOT NULL REFERENCES users(id),
    posted_date DATE NOT NULL
);

-- migrations/005_add_permissions_and_approval_status.sql
ALTER TABLE job_postings
    ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT 'approved' CHECK (status IN ('pending', 'approved'));
```

### Table: `job_applications`

A new entity: records that a given user applied to a given job posting. This is the **junction table** that makes applying possible — without it, `job_postings` only supports *creating* a listing, not *applying* to one.

| Column          | Type        | Constraints                                   | Notes                                               |
|-----------------|-------------|-------------------------------------------------|-------------------------------------------------------|
| `id`            | `SERIAL`    | `PRIMARY KEY`                                    | Auto-incrementing                                      |
| `user_id`       | `INTEGER`   | `NOT NULL`, `REFERENCES users(id)`               | The alumnus applying                                  |
| `job_posting_id`| `INTEGER`   | `NOT NULL`, `REFERENCES job_postings(id)`        | The job they're applying to                           |
| `applied_date`  | `DATE`      | `NOT NULL`                                       |                                                         |
| —               | —           | `UNIQUE (user_id, job_posting_id)`               | Prevents the same user from applying to the same job twice |

```sql
CREATE TABLE job_applications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    job_posting_id INTEGER NOT NULL REFERENCES job_postings(id),
    applied_date DATE NOT NULL,
    UNIQUE (user_id, job_posting_id)
);
```

## Relationships

**`users` → `job_postings` is one-to-many: one user can post many job postings, but each job posting belongs to exactly one user.** This is implemented with a foreign key: `job_postings.posted_by` points to `users.id`. In plain terms — every row in `job_postings` must name a `users.id` that actually exists; PostgreSQL enforces this automatically and will reject an insert/update that references a non-existent user.

**`users` ↔ `job_postings` is also many-to-many, for applications: one user can apply to many job postings, and one job posting can receive applications from many users.** A single foreign key can't express this (neither table could hold "many" values in one column), so it's modeled with the `job_applications` junction table: each row connects one `user_id` to one `job_posting_id`. To find "who applied to job #5", query `job_applications WHERE job_posting_id = 5`; to find "what has user #2 applied to", query `job_applications WHERE user_id = 2`. The `UNIQUE (user_id, job_posting_id)` constraint stops someone from applying to the same job twice.

There is currently no relationship between `announcements` and the other tables — it remains an independent entity. A future iteration could add a `created_by` foreign key on `announcements` pointing to `users.id` as well, following the same pattern as `job_postings`, but that is out of scope for now.

## App ↔ Database Wiring

`models/db.py` exposes `get_connection()`, which opens a `psycopg2` connection using the `DATABASE_URL` environment variable (set via `.env` / `docker-compose.yml`) and returns rows as plain dictionaries (`RealDictCursor`), so controllers and templates can use `user["first_name"]` / `user.first_name` interchangeably.

`models/user.py` and `models/announcement.py` each open a new connection per method call (`create`, `get_all`, `get_by_id`, `update`, `patch`, `delete`), run the relevant SQL, `commit()` after any write, then close the connection. Controllers were **not changed** — they still call `User.create(...)`, `User.get_all()`, etc. exactly as before; only what happens inside those methods changed, from an in-memory list to real SQL. This is the MVC boundary doing its job: swapping storage didn't require touching a single controller or template.

Verified behavior: creating a record, running `docker compose down` then `docker compose up`, and the record is still there — the "forgetting test" from before no longer applies to `users`/`announcements`.

### `JobPosting` and `JobApplication` models

`models/job_posting.py` follows the exact same pattern as `User`/`Announcement` (`create`, `get_all`, `get_by_id`, `update`, `patch`, `delete`), plus one relationship-specific method: **`JobPosting.get_by_user(user_id)`**, which queries `WHERE posted_by = %s` — this is the one-to-many relationship in action, fetching every posting made by a given user.

`models/job_application.py` has `create`, `get_all`, `get_by_id`, `delete` (no `update`/`patch` — an application either exists or doesn't, there's nothing partial to edit), plus two relationship-specific methods that each use a SQL `JOIN` to pull in useful details from the other side of the many-to-many relationship:

- **`JobApplication.get_by_user(user_id)`** — joins with `job_postings` to answer "what jobs has this user applied to", returning each application's `title`/`company` instead of just a bare `job_posting_id`.
- **`JobApplication.get_by_job_posting(job_posting_id)`** — joins with `users` to answer "who applied to this job", returning each applicant's `first_name`/`last_name`/`email` instead of just a bare `user_id`.

Both constraints from the schema are enforced by PostgreSQL itself, not by application code — verified directly:
- Applying the same user to the same job twice: `JobApplication.create(...)` returns `None` the second time (the `UniqueViolation` is caught and handled gracefully).
- Creating a job posting with a `posted_by` that doesn't exist in `users`: raises `psycopg2.errors.ForeignKeyViolation` — the insert is rejected outright.

## Direct vs. Nested Routes

The relationship methods above are now exposed as actual HTTP routes, split into two styles:

- **Direct routes** operate on one resource by itself: `/api/job-postings`, `/api/job-postings/<id>`, `/api/applications`, `/api/applications/<id>`. Standard CRUD, no relationship involved in the URL.
- **Nested routes** put a resource's URL *underneath* the resource it relates to, so the URL itself documents the relationship:
  - `GET/POST /api/job-postings/<id>/applications` — "the applications that belong to this job posting" (and applying to it)
  - `GET /api/users/<id>/job-postings` — "the job postings that belong to this user" (the one-to-many)
  - `GET /api/users/<id>/applications` — "the applications that belong to this user" (the many-to-many, other side)

Nested routes are implemented in whichever controller owns the *parent* resource in the URL — e.g. `/api/users/<id>/job-postings` lives in `api_user_controller.py`, not `api_job_posting_controller.py`, even though it returns `JobPosting` data. Each nested route first checks the parent exists (404 if not) before querying the relationship.

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

**`migrations/002_create_job_postings_and_applications.sql`** creates `job_postings` first, then `job_applications` right after (order matters here, since `job_applications` references `job_postings`). Since the existing database volume already had data in it (the auto-run-on-first-boot trick doesn't apply here, see the "Important" note above), it was applied **manually**:

```bash
docker exec -i alumni-web-programming-db-1 psql -U alumni -d alumni < migrations/002_create_job_postings_and_applications.sql
```

This is the standard way to apply a migration to a database that already exists — it ran the same `CREATE TABLE` statements against the live database without touching the existing `users`/`announcements` data.

## Factory & Seed

Two separate concepts, often confused:

- **Factory** (`factories/*_factory.py`) — a class whose only job is to *generate* one fake-but-realistic record (via the [Faker](https://faker.readthedocs.io/) library). It does not touch the database at all; calling `UserFactory.create()` just returns a Python dict.
- **Seed** (`seed.py`) — a script that calls the factories in a loop and actually `INSERT`s the results into PostgreSQL via `psycopg2`, then `commit()`s the transaction.

Run it (containers must already be up):

```bash
docker compose exec web python seed.py
```

This inserts 10 fake users, 5 fake announcements, 8 fake job postings, and up to 10 fake job applications. It connects using the same `DATABASE_URL` the `web` container already has from `.env` — no extra configuration needed.

**`job_postings` and `job_applications` need a bit more care than `users`/`announcements`**, because their factories can't invent a `posted_by`/`user_id`/`job_posting_id` out of thin air — those must be real foreign keys. So `seed.py`:
1. Seeds `users` first, then runs `SELECT id FROM users` to get real user ids.
2. Passes a random real `user_id` into `JobPostingFactory.create(posted_by)` for each job posting, then runs `SELECT id FROM job_postings` to get real job posting ids.
3. Passes a random real `user_id` + `job_posting_id` into `JobApplicationFactory.create(...)` for each application — using `INSERT ... ON CONFLICT (user_id, job_posting_id) DO NOTHING` so that if the random pick happens to collide with the `UNIQUE` constraint (someone "applying" to the same job twice), it's silently skipped instead of crashing the whole script. This is why the seeded application count is "up to 10", not always exactly 10.

Since the app is now wired to the same database (see App ↔ Database Wiring above), seeded rows appear immediately on `/users`, `/announcements`, `/job-postings`, `/applications`, and their `/api/...` equivalents — no restart needed.

## Middleware & Error Handling

Three pieces live in `middleware/`, wired into `app.py` once, app-wide, instead of being repeated per route:

- **`middleware/logger.py` — request logger.** A `before_request`/`after_request` pair that times every request and logs `METHOD PATH -> STATUS (Xms)` via `app.logger`. This is observability, not business logic — no route needs to know it's happening.
- **`middleware/error_handlers.py` — 404 guardian.** `@app.errorhandler(404)` catches any URL Flask can't match to a route and renders `templates/404.html` instead of Flask's default plain-text 404. This only catches *unmatched routes*; the per-resource "not found" responses returned directly by individual controllers (e.g. a missing `job_posting_id`) are a separate, explicit `return render_template("404.html"), 404` in each one — same page, reached a different way, so an HTML visitor always sees the same branded 404 regardless of which case it was. The JSON API controllers still return `jsonify(error="...")` instead, since a machine client has no use for an HTML page.
- **`middleware/error_handlers.py` — 5xx guardian.** `@app.errorhandler(Exception)` catches any unhandled exception (a real bug) that would otherwise crash the request. It logs the full method, path, and traceback to `logs/error.log` (via a dedicated `error_logger` with a `FileHandler`), then renders `templates/500.html` with a generic, non-technical message — the real stack trace (which can leak file paths, SQL, etc.) never reaches the client. HTTP exceptions that aren't plain 500s (e.g. a deliberate `abort(400)`) are re-raised as-is so Flask's normal handling still applies to them.
- **`templates/403.html`** — rendered by `middleware/auth.py`'s `require_role(...)` when a logged-in session has the wrong role (see **Auth guardian** below). Same idea as the other two: one branded page, reused everywhere a 403 can happen, instead of a bare string.

**Why `logs/error.log` isn't committed to git:** the log file is a generated, ever-growing runtime artifact (like a build output), not source code — this project's `.gitignore` already excludes `*.log`. The `logs/` directory itself is created automatically at startup via `os.makedirs(..., exist_ok=True)` in `error_handlers.py`, so nothing needs to be committed for it to exist.

**Why `PROPAGATE_EXCEPTIONS = False` is set in `app.py`:** with `debug=True` (used for local development), Flask/Werkzeug's interactive debugger intercepts unhandled exceptions before our own error handler gets a chance to run. Setting this explicitly to `False` makes the 5xx guardian fire even in debug mode.

### Validation rules & the 400 response

Without validation, bad input (e.g. a job posting with no title) either silently inserts garbage or crashes with a raw database error. Rather than scattering the same checks across every controller that touches `job_postings` (the "without middleware" problem — the same rule re-implemented slightly differently in each place), the rules live in one place, the Model, and every controller calls the same function before creating a record.

**Rules for creating a `job_posting`** (enforced by `JobPosting.validate(title, company)` in `models/job_posting.py`):

| Field | Rule |
|---|---|
| `title` | Required, max `JobPosting.MAX_TITLE_LENGTH` (120) characters |
| `company` | Required |
| `description`, `location` | Optional |

If `validate(...)` returns any errors, the request never reaches `JobPosting.create(...)`:
- `api_job_posting_controller.py` returns `400 {"error": "..."}` (JSON) — the client sent invalid data, so `400 Bad Request` is the correct status, distinct from `404` (resource doesn't exist) or `500` (our own bug).
- `job_posting_controller.py` (the HTML form) redirects back to `/job-postings` with the error message in a query parameter, which `templates/job_postings/list.html` displays above the table — the Post-Redirect-Get pattern, same as every other create/edit flow in this app, just carrying the failure reason along with it.

## User Roles & Permissions

Two concepts that are easy to conflate:
- **Authentication** ("who are you?") — verifying an identity, typically via email + password. Implemented today via `password_hash` on `users` (hashed with `werkzeug.security.generate_password_hash`, never stored or returned in plain text).
- **Authorization** ("are you allowed to do this?") — once identified, deciding what that identity can access. This is driven by the new `role` column.

**Roles:** every registered account has exactly one *base* role, `alumni` or `student` (the `CHECK` constraint above), chosen by the user at registration. A third "role", **guest**, is not a value in this column at all — it means *no account*, i.e. an unauthenticated visitor. There is no database row for a guest.

**Staff roles (`staff_role`):** separate from the base role, and orthogonal to it — a user is *always* alumni-or-student *and optionally also* `admin` or `moderator` at the same time (e.g. an alumnus who also moderates). This is why it's its own nullable column (`migrations/004_add_staff_roles.sql`) rather than another value crammed into `role`: `role` answers "what kind of member are they", `staff_role` answers "do they also have elevated privileges". `NULL` (the default) means no elevated privileges. **Nothing in the app ever lets a user set their own `staff_role`** — the register form only offers `alumni`/`student` (see `templates/register.html`); granting `admin`/`moderator` today means a direct SQL `UPDATE`, e.g.:

```sql
UPDATE users SET staff_role = 'admin' WHERE email = '...';
```

An admin UI to manage this is a natural future task, not built yet.

**Permissions** (now enforced — see "Auth guardian" below):

| Action | Guest | Student | Alumni | Moderator | Admin |
|---|:---:|:---:|:---:|:---:|:---:|
| View announcements | ✅ | ✅ | ✅ | ✅ | ✅ |
| View job postings | ✅ | ✅ | ✅ | ✅ | ✅ |
| View the alumni directory | ❌ | ✅ | ✅ | ✅ | ✅ |
| Apply to a job posting | ❌ | ✅ | ✅ | ✅ | ✅ |
| Create a job posting | ❌ | ❌ | ✅ | ❌* | ❌* |
| Delete any user / announcement / job posting / application | ❌ | ❌ | ❌ | ✅ | ✅ |
| Approve a pending user / job posting / announcement | ❌ | ❌ | ❌ | per permission† | ✅ |
| Manage users / add a user / grant roles | ❌ | ❌ | ❌ | per permission†, never roles | ✅ |
| Register an account | ✅ → becomes Student or Alumni | — | — | — | — |

\* a moderator/admin who is *also* `alumni` can create one — through the `alumni` role, not the staff role. `staff_role` only ever grants the delete/moderation row.

† unlike delete, these are **not** blanket "any staff member can" rows — each one requires a specific permission granted to that moderator individually (see **Moderator permissions** under "Admin panel" below). The table above shows what's *possible* for the role; `moderator_permissions` decides what's *actually granted* to a given moderator.

The reasoning: job postings represent an alumnus sharing an opportunity from their own career, so only the `alumni` role can create one; every logged-in account can apply. Destructive actions (delete) are the one thing that genuinely needs a step up from "any member" to "staff", which is exactly what `admin`/`moderator` are for. Read-only actions (announcements, job postings) stay open to guests, since there's no reason to gate information with no side effects.

**Registration** (`POST /register`, `controllers/auth_controller.py`): validated by `User.validate_registration(...)` (all fields required, `role` must be `alumni`/`student`, password at least 6 characters), then `User.register(...)` hashes the password and inserts the row. A duplicate email hits the same `UNIQUE` constraint as before — caught as `psycopg2.errors.UniqueViolation` and surfaced as a friendly redirect-with-reason, the same pattern used for job posting validation and duplicate job applications.

### Login & logout (session-based authentication)

The whiteboard's Client/Server diagram was token-based auth in the abstract; the concrete implementation here is Flask's built-in **session**, which is really the same idea: the server gives the client a token after login, the client sends it back automatically on every later request, and the server reads the identity from it instead of asking for a password again.

- `app.secret_key` (`app.py`, from the `SECRET_KEY` env var) signs the session cookie. Without it, Flask raises `RuntimeError: The session is unavailable...` the moment any route tries to write to `session` — caught live by our own 5xx guardian during testing, logged to `logs/error.log` with the full traceback, while the client only saw the generic error message. A nice real confirmation that last week's guardian actually works end to end.
- **`POST /login`** (`controllers/auth_controller.py`): looks the user up by email (`User.get_by_email`, the only query that selects `password_hash`), checks the password with `User.verify_password` (`werkzeug.security.check_password_hash`), and on success stores `user_id`, `first_name`, `role`, `staff_role` in `session`. On failure — wrong password *or* email that doesn't exist — the same generic `"Invalid email or password"` is shown; never revealing which one was wrong is a basic security habit (an attacker shouldn't be able to use the error message to enumerate real emails).
- **`POST /logout`**: `session.clear()`, redirect home.
- `templates/base.html` reads `session.user_id` directly (Flask injects `session` into every template automatically) to swap the nav between "Login/Register" and "Hi, {name} ({role})" + a Logout button.
- Flask's default session cookie is **signed, not encrypted** — its contents (`user_id`/`first_name`/`role`) are base64-readable by anyone who inspects the cookie, just not forgeable without `SECRET_KEY`. Fine here since nothing sensitive (like the password) is stored in it.

### Auth guardian (`middleware/auth.py`)

The piece that actually enforces the permissions table above — this is the "authorization" half of the Authentication/Authorization distinction made concrete. Two call styles, because this app's routes are a mix of two shapes:

- **`@login_required` / `@staff_required` (decorators)** — for routes that are *entirely* gated (no public branch at all), e.g. `GET/POST /users` (viewing the directory already requires login, so the whole route can be wrapped) or any single-purpose `POST .../delete` route (`@staff_required`).
- **`require_role(*roles)` (plain function, called inline)** — for routes that mix a public branch with a protected one, e.g. `GET/POST /job-postings`: the `GET` (viewing postings) must stay open to guests, so only the `POST` branch calls `guard = require_role("alumni"); if guard: return guard` before doing anything. A decorator can't express "only this branch", since it wraps the whole view function.

Both ultimately check `session` the same way: not logged in → **401 isn't used for HTML views on this project** (which have no concept of a non-browser caller) but a redirect to `/login`; logged in with the wrong role → **`403 Forbidden`**.

**`require_role_api(*roles)`** is the same logic for the JSON/API controllers, but returns JSON instead of a browser redirect — redirecting a Postman request to an HTML login page makes no sense for an API client. Here the status codes follow the standard convention precisely:
- **`401 Unauthorized`** — no session at all ("I don't know who you are").
- **`403 Forbidden`** — a session exists, but that role isn't allowed to do this ("I know who you are, and the answer is no").

**`require_permission(permission)`** is a third variant, for the admin panel specifically (see below): instead of a fixed list of roles, it checks a *named capability* — `admin` always passes, a `moderator` passes only if granted that exact permission, anyone else is `403`.

Guarded today: viewing the alumni directory (`/users`, `/api/users`), applying to a job posting, creating a job posting (`alumni` only), and every delete route across users/announcements/job postings/applications (`staff_required`, both HTML and API). Verified live with guest/student/alumni/admin accounts hitting each guarded route — a student gets `403` creating or deleting, a guest gets redirected/`401`, an alumnus can create but not delete, and only an account with `staff_role` set can delete.

**Still open:** editing (as opposed to deleting) a record isn't gated — e.g. any logged-in session can currently edit any job posting, not just its own. Doing that properly needs an *ownership* check (is this job posting's `posted_by` the current session's `user_id`?), which is a different, more granular kind of authorization than the role check here — left for a future task rather than guessed at now.

### Admin panel (`/admin`, `controllers/admin_controller.py`)

The one place `staff_role` itself gets assigned through the UI instead of a raw SQL `UPDATE`. The panel is now open to **both** `admin` and `moderator` (`@admin_bp.before_request` calls `require_role(*STAFF_ROLES)`), but what a moderator can actually *do* once inside is controlled feature-by-feature — see **Moderator permissions** below. One route is the deliberate exception and stays admin-only regardless: granting roles to someone else.

#### Moderator permissions (`moderator_permissions` table, `migrations/005_...sql`)

An `admin` always has every capability — nothing to configure, nothing to ask, it just works. A `moderator` has **only** the specific capabilities an admin has explicitly granted, tracked in a junction table (the same many-to-many pattern as `job_applications`: one moderator can hold many permissions, one permission can be held by many moderators):

```sql
CREATE TABLE moderator_permissions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    permission VARCHAR(30) NOT NULL CHECK (permission IN (
        'approve_users', 'manage_users', 'add_users',
        'approve_job_postings', 'approve_announcements'
    )),
    UNIQUE (user_id, permission)
);
```

`middleware/auth.py`'s **`require_permission(permission)`** is the check: an `admin` session passes immediately; a `moderator` session passes only if that exact string is in `session["permissions"]` (loaded once at login from `moderator_permissions`, not re-queried per request); anyone else — including a plain `alumni`/`student`, even one who is logged in — gets `403`. **Granting the roles and permissions themselves is never one of the permissions** — `POST /admin/users/<id>/role` calls `require_role("admin")` directly, bypassing the blueprint's more permissive moderator-admitting gate, so a moderator can never hand out admin/moderator or edit anyone's permission set, no matter what they've been granted elsewhere. That would be a privilege-escalation hole otherwise.

Routes and their permission:

| Route | Permission required |
|---|---|
| `GET /admin` | any staff (dashboard only shows the cards this session can use) |
| `GET /admin/users` | `manage_users` |
| `GET/POST /admin/users/new` | `add_users` |
| `GET /admin/users/pending`, `POST .../approve` | `approve_users` |
| `GET /admin/job-postings/pending`, `POST .../approve` | `approve_job_postings` |
| `GET /admin/announcements/pending`, `POST .../approve` | `approve_announcements` |
| `GET/POST /admin/users/<id>/role` | **`admin` only**, not delegable |

Verified live: a moderator granted only `approve_job_postings` sees exactly one feature card on the dashboard, gets `200` on `/admin/job-postings/pending` and can approve from there, but gets `403` on `/admin/users`, `/admin/announcements/pending`, and `/admin/users/<id>/role` — while a plain delete elsewhere (`staff_required`, unrelated to this permission system) still works, since that was never gated per-permission.

The nav (`templates/base.html`) shows the "Admin Panel" link for `session.staff_role in ("admin", "moderator")` — but as always, the hidden/shown link is a convenience, not the security boundary; the real check is server-side on every request.

#### Approval workflow (`status` column on `users`, `job_postings`, `announcements`)

Three tables gained a `status` column (`'pending'` / `'approved'`, `DEFAULT 'approved'` so every existing row — and anything inserted by factories/seed/the old ad-hoc create flows that don't mention it — is grandfathered in untouched):

- **`POST /register`** now inserts `status = 'pending'` explicitly. **`POST /login` refuses a pending account** with "Your account is still pending admin approval" — approval is a real access gate, not just a label. An admin, or a moderator with `approve_users`, approves from `/admin/users/pending`.
- **`POST /job-postings`** (alumni creating a listing) and **`POST /announcements`** (anyone) also insert `'pending'`. `JobPosting.get_approved()` / `Announcement.get_approved()` are what the public list pages and the JSON API now query — a pending posting or announcement simply doesn't exist yet as far as a guest, student, or alumnus browsing the site is concerned, until `approve_job_postings` / `approve_announcements` clears it.
- `User.create()` (the admin's "add a user" flow, and factories/seed) never sets `status` at all, so it rides the `DEFAULT 'approved'` — a user an admin adds directly doesn't need to also approve themselves.
