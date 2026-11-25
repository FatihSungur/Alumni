# 🎓 Alumni Web Programming

A web platform built for the Web Programming course to connect graduates with their alma mater. The goal is to give alumni a place to keep their career info up to date and give the institution a simple way to track alumni outcomes over time. The project is under active, incremental development, with each course milestone adding a new capability on top of the last.

## 🚀 Key Features (Planned & In Progress)

- **Alumni Directory:** Basic profile and listing endpoints for graduates.
- **Greeting & Utility Endpoints:** Early API building blocks (`/hello`, `/sum`, etc.) used to learn and validate the routing layer.
- **Static Pages:** Home and About pages describing the project.
- **Containerized Deployment:** Docker & Docker Compose setup so the app runs identically on any machine.
- **Future Milestones:** Alumni profile management and search/filtering will be added in upcoming weeks.

## Tech Stack

- **Language:** Python 3.12
- **Framework:** Flask
- **Database:** PostgreSQL — `users` and `announcements` are fully backed by it (see [DDD.md](./DDD.md) for the schema)
- **Containerization:** Docker & Docker Compose
- **Design:** see [brand.md](./brand.md) for the visual identity (colors, fonts, logo) and [DESIGN.md](./DESIGN.md) for how it's applied across pages

## 🏗️ Project Structure (MVC Architecture)

The app follows the **Model-View-Controller (MVC)** pattern. Each concern lives in its own folder so the codebase stays organized as it grows:

```
Alumni-Web-Programming/
├── brand.md                             # Visual identity: color palette, fonts, logo
├── DESIGN.md                            # How the brand gets applied: components, layout, spacing
├── app.py                              # Entry point: creates the Flask app, wires up Swagger, registers controllers
├── models/
│   ├── __init__.py
│   ├── db.py                            # Shared PostgreSQL connection helper
│   ├── user.py                         # Model: User CRUD, backed by the `users` table
│   ├── announcement.py                 # Model: Announcement CRUD, backed by the `announcements` table
│   ├── job_posting.py                  # Model: JobPosting CRUD, backed by the `job_postings` table
│   └── job_application.py              # Model: JobApplication CRUD, backed by the `job_applications` table
├── controllers/
│   ├── __init__.py
│   ├── user_controller.py              # Controller: HTML pages for /users (list, create, edit, delete)
│   ├── api_user_controller.py          # Controller: JSON API for /api/users (same data, machine-readable)
│   ├── announcement_controller.py      # Controller: HTML pages for /announcements (list, create, edit, delete)
│   ├── api_announcement_controller.py  # Controller: JSON API for /api/announcements
│   ├── api_job_posting_controller.py   # Controller: JSON API for /api/job-postings (direct + nested /applications)
│   ├── api_job_application_controller.py # Controller: JSON API for /api/applications (direct routes only)
│   ├── job_posting_controller.py       # Controller: HTML pages for /job-postings (list, create, edit, delete)
│   ├── job_application_controller.py   # Controller: HTML pages for /applications (list, apply, delete)
│   └── auth_controller.py              # Controller: HTML pages for /register (account creation)
├── middleware/
│   ├── __init__.py
│   ├── logger.py                       # Request logger: logs method/path/status/duration for every request
│   ├── error_handlers.py               # 404 guardian (generic 404 page) + 5xx guardian (logs to logs/error.log)
│   └── auth.py                         # Auth guardian: login_required/staff_required/require_role(_api) (see DDD.md)
├── static/
│   └── style.css                       # Shared stylesheet: CSS variables for the brand, nav/button/card/table components
├── templates/                          # View: HTML pages rendered by the controllers (Jinja2 templates)
│   ├── index.html
│   ├── about.html
│   ├── 404.html                        # Generic "page not found" page, shown by the 404 guardian
│   ├── register.html                   # Account creation form (role: alumni or student)
│   ├── login.html                      # Login form
│   ├── users/
│   │   ├── list.html                   # Lists all users + a form to create a new one
│   │   └── edit.html                   # Pre-filled form to edit a single user
│   ├── announcements/
│   │   ├── list.html                   # Lists all announcements + a form to create a new one
│   │   └── edit.html                   # Pre-filled form to edit a single announcement
│   ├── job_postings/
│   │   ├── list.html                   # Lists all job postings + a form to create a new one
│   │   └── edit.html                   # Pre-filled form to edit a single job posting
│   └── job_applications/
│       └── list.html                   # Lists all applications + a form to apply to a job
├── migrations/
│   ├── 001_create_tables.sql           # Creates the `users` and `announcements` tables (see DDD.md)
│   ├── 002_create_job_postings_and_applications.sql # Creates `job_postings` + `job_applications`
│   ├── 003_add_user_roles_and_auth.sql  # Adds `role` and `password_hash` to `users` (see DDD.md)
│   └── 004_add_staff_roles.sql          # Adds `staff_role` ('admin'/'moderator') to `users` (see DDD.md)
├── factories/
│   ├── __init__.py
│   ├── user_factory.py                 # Generates realistic fake user data (via Faker)
│   ├── announcement_factory.py         # Generates realistic fake announcement data (via Faker)
│   ├── job_posting_factory.py          # Generates realistic fake job posting data (via Faker)
│   └── job_application_factory.py      # Generates realistic fake job application data (via Faker)
├── seed.py                              # Uses the factories to insert sample rows directly into PostgreSQL
├── logs/                                # Created automatically at startup; holds error.log (gitignored, not committed)
├── requirements.txt                     # Python dependencies
├── Dockerfile                           # Container image definition
└── docker-compose.yml                   # Local orchestration (build + run)
```

**How the layers map to MVC:**

- **Model** (`models/`) — owns the data and the rules for changing it (create, read, update, delete). Knows nothing about HTTP, HTML, or JSON.
- **View** (`templates/`) — the HTML the user actually sees. Knows nothing about where the data came from, it just renders whatever it's given.
- **Controller** (`controllers/`) — the bridge. Receives the HTTP request, asks the Model for data, hands that data to a View (or turns it straight into JSON), and returns the result. Each resource (`User`, `Announcement`) has two controllers on purpose: one serves human users through HTML pages (`UserController`, `AnnouncementController`), the other serves other programs through JSON (`ApiUserController`, `ApiAnnouncementController`) — both talk to the exact same Model underneath.
- **Middleware** (`middleware/`) — cross-cutting code that runs for every request regardless of route: request logging and the 404/5xx error guardians. See [DDD.md](./DDD.md#middleware--error-handling) for details.

## Prerequisites

- Docker and Docker Compose installed (recommended way to run this project)
- Python 3.12 (only needed for the local, non-Docker alternative)

## How to Run (Recommended: Docker Compose)

First, create your local `.env` file from the provided example (this holds database credentials and is never committed to git):

```bash
cp .env.example .env
```

Fill in `POSTGRES_USER`/`POSTGRES_PASSWORD`/`POSTGRES_DB`/`DATABASE_URL` as usual, and generate a `SECRET_KEY` (used to sign login sessions — without it, `/login` and `/register` raise an error):

```bash
python3 -c "import secrets; print(secrets.token_hex(24))"
```

Then run:

```bash
docker compose up --build
```

This starts two containers: the Flask app (`web`) and a PostgreSQL database (`db`). The app reads and writes directly to PostgreSQL for both `User` and `Announcement` — data now survives restarts. The app will be available at `http://localhost:5000`. Stop everything with `Ctrl+C`, then `docker compose down`.

### Seeding sample data into the database

Once the containers are running, you can fill the database with realistic fake data (10 users, 5 announcements, 8 job postings, up to 10 job applications) using the Factory + Seed scripts:

```bash
docker compose exec web python seed.py
```

This writes directly to PostgreSQL via `psycopg2`, using the `UserFactory`/`AnnouncementFactory` to generate the fake data. Since the app is now wired to the same database, the seeded rows show up immediately on `/users`, `/announcements`, and their `/api/...` equivalents.

## Alternative: Run Locally with Python

Since the app now requires PostgreSQL (`DATABASE_URL`), this only works if you have a local Postgres instance running and your `.env` points to it:

```bash
pip install -r requirements.txt
python app.py
```

The app will be available at `http://localhost:5000`. In practice, Docker Compose above is much simpler since it provisions the database for you.

## API Endpoints

> **Auth guardian:** routes marked 🔒 require a login session, and 🔒staff require `admin`/`moderator`. A guest hitting an HTML 🔒 route is redirected to `/login`; an API 🔒 route returns `401`. The wrong role on either returns `403`. See [DDD.md](./DDD.md#auth-guardian-middlewareauthpy) for the full permissions table.

| Method | Path                          | Description                          |
|--------|-------------------------------|---------------------------------------|
| GET    | `/`                           | Temporary main page                   |
| GET    | `/hello`                      | Returns `Hello, World!`               |
| GET    | `/hello/<name>`               | Returns `Hello, <name>!`              |
| GET    | `/sum/<number1>/<number2>`    | Returns the sum of two numbers        |
| GET    | `/about`                      | Temporary about page                  |
| GET    | `/register`                   | HTML registration form (role: alumni or student) |
| POST   | `/register`                   | Creates an account (hashes the password) and redirects home; redirects back with `?error=...` on invalid data or a duplicate email (see DDD.md) |
| GET    | `/login`                      | HTML login form |
| POST   | `/login`                      | Verifies email/password and starts a session; redirects back with `?error=...` on failure |
| POST   | `/logout`                     | Clears the session and redirects home |
| GET    | 🔒 `/users`                   | HTML page listing alumni, with a form to create a new one (UserController) |
| POST   | 🔒 `/users`                   | Creates an alumni record from the HTML form and redirects back to the list |
| GET    | `/users/<id>/edit`            | HTML form pre-filled with the record's current data |
| POST   | `/users/<id>/edit`             | Saves the edited record and redirects back to the list |
| POST   | 🔒staff `/users/<id>/delete`  | Deletes the record and redirects back to the list |
| GET    | `/api/health`                 | Returns `{"status": "ok"}` as JSON    |
| POST   | 🔒 `/api/users`               | Creates an alumni record from form data (`first_name`, `last_name`, `graduation_year`, `email`) and returns it (with an auto-generated `id`) as JSON |
| GET    | 🔒 `/api/users`               | Returns all alumni records created so far, as a JSON list |
| PUT    | `/api/users/<id>`             | Replaces all fields of the record with the given `id` and returns it as JSON |
| PATCH  | `/api/users/<id>`             | Updates only the given fields of the record with the given `id` and returns it as JSON |
| DELETE | 🔒staff `/api/users/<id>`     | Deletes the record with the given `id` and returns the deleted record as JSON |
| GET    | `/announcements`              | HTML page listing announcements, with a form to create a new one (AnnouncementController) |
| POST   | `/announcements`              | Creates an announcement from the HTML form and redirects back to the list |
| GET    | `/announcements/<id>/edit`    | HTML form pre-filled with the announcement's current data |
| POST   | `/announcements/<id>/edit`    | Saves the edited announcement and redirects back to the list |
| POST   | 🔒staff `/announcements/<id>/delete` | Deletes the announcement and redirects back to the list |
| POST   | `/api/announcements`          | Creates an announcement from form data (`title`, `content`, `date`) and returns it (with an auto-generated `id`) as JSON |
| GET    | `/api/announcements`          | Returns all announcements created so far, as a JSON list |
| PUT    | `/api/announcements/<id>`     | Replaces all fields of the announcement with the given `id` and returns it as JSON |
| PATCH  | `/api/announcements/<id>`     | Updates only the given fields of the announcement with the given `id` and returns it as JSON |
| DELETE | 🔒staff `/api/announcements/<id>` | Deletes the announcement with the given `id` and returns the deleted record as JSON |
| GET    | `/job-postings`               | HTML page listing job postings, with a form to create a new one (JobPostingController) |
| POST   | 🔒 `/job-postings`            | Creates a job posting from the HTML form (`alumni` role only, `403` otherwise) and redirects back to the list; redirects back with `?error=...` instead if `title`/`company` fail validation (see DDD.md) |
| GET    | `/job-postings/<id>/edit`     | HTML form pre-filled with the job posting's current data |
| POST   | `/job-postings/<id>/edit`     | Saves the edited job posting and redirects back to the list |
| POST   | 🔒staff `/job-postings/<id>/delete` | Deletes the job posting and redirects back to the list |
| GET    | `/applications`               | HTML page listing job applications, with a form to apply to a job (JobApplicationController) |
| POST   | 🔒 `/applications`            | Creates an application from the HTML form (`user_id`, `job_posting_id`, `applied_date`); returns `409` if already applied |
| POST   | 🔒staff `/applications/<id>/delete` | Deletes the application and redirects back to the list |
| GET/POST | `/api/job-postings`         | Direct route: list all job postings, or 🔒 create one (`alumni` role only, `403` otherwise); returns `400` if `title`/`company` fail validation (see DDD.md) |
| GET/PUT/PATCH/🔒staff DELETE | `/api/job-postings/<id>` | Direct route: get, replace, partially update, or delete a job posting |
| GET    | `/api/applications`           | Direct route: list every job application in the system |
| GET/🔒staff DELETE | `/api/applications/<id>`  | Direct route: get or delete a single application |
| GET/🔒POST | `/api/job-postings/<id>/applications` | Nested route: list who applied to this job posting, or apply to it (`user_id`, `applied_date`) |
| GET    | `/api/users/<id>/job-postings` | Nested route: list every job posting created by this user (one-to-many) |
| GET    | `/api/users/<id>/applications` | Nested route: list every job this user applied to (many-to-many) |
| GET    | `/api/swagger`                | Interactive Swagger UI (powered by [flasgger](https://github.com/flasgger/flasgger)) listing every documented route |

> **Project rule:** `/api/swagger` is generated dynamically from the docstrings on each route, so it always reflects the current endpoints automatically. Whenever a new endpoint is added, give it a short YAML docstring (see the existing routes for examples) so it shows up in Swagger — then just visit `/api/swagger` in a browser to confirm it picked it up.

`POST`, `PUT`, `PATCH` and `DELETE` on `/api/users` can't be tested from a browser address bar (it only sends GET) — use Postman (or curl) instead:

```bash
curl -X POST http://localhost:5000/api/users \
  -d "first_name=Fatih" \
  -d "last_name=Sungur" \
  -d "graduation_year=2026" \
  -d "email=fatih@example.com"
```

In Postman: for POST, set the URL to `http://localhost:5000/api/users`; for PUT/PATCH/DELETE, set it to `http://localhost:5000/api/users/<id>` (the `id` from the POST response). Go to the **Body** tab, select **form-data**, and add the relevant fields as key/value pairs (DELETE needs no body).

Afterwards, visit `http://localhost:5000/api/users` in a browser (GET) to see the list of alumni records created so far. Records are now stored in PostgreSQL, so they persist across restarts (`docker compose down` / `up`).
