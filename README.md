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

## 🏗️ Project Structure (MVC Architecture)

The app follows the **Model-View-Controller (MVC)** pattern. Each concern lives in its own folder so the codebase stays organized as it grows:

```
Alumni-Web-Programming/
├── app.py                              # Entry point: creates the Flask app, wires up Swagger, registers controllers
├── models/
│   ├── __init__.py
│   ├── db.py                            # Shared PostgreSQL connection helper
│   ├── user.py                         # Model: User CRUD, backed by the `users` table
│   └── announcement.py                 # Model: Announcement CRUD, backed by the `announcements` table
├── controllers/
│   ├── __init__.py
│   ├── user_controller.py              # Controller: HTML pages for /users (list, create, edit, delete)
│   ├── api_user_controller.py          # Controller: JSON API for /api/users (same data, machine-readable)
│   ├── announcement_controller.py      # Controller: HTML pages for /announcements (list, create, edit, delete)
│   └── api_announcement_controller.py  # Controller: JSON API for /api/announcements
├── templates/                          # View: HTML pages rendered by the controllers (Jinja2 templates)
│   ├── index.html
│   ├── about.html
│   ├── users/
│   │   ├── list.html                   # Lists all users + a form to create a new one
│   │   └── edit.html                   # Pre-filled form to edit a single user
│   └── announcements/
│       ├── list.html                   # Lists all announcements + a form to create a new one
│       └── edit.html                   # Pre-filled form to edit a single announcement
├── migrations/
│   └── 001_create_tables.sql           # Creates the `users` and `announcements` tables (see DDD.md)
├── factories/
│   ├── __init__.py
│   ├── user_factory.py                 # Generates realistic fake user data (via Faker)
│   └── announcement_factory.py         # Generates realistic fake announcement data (via Faker)
├── seed.py                              # Uses the factories to insert sample rows directly into PostgreSQL
├── requirements.txt                     # Python dependencies
├── Dockerfile                           # Container image definition
└── docker-compose.yml                   # Local orchestration (build + run)
```

**How the layers map to MVC:**

- **Model** (`models/`) — owns the data and the rules for changing it (create, read, update, delete). Knows nothing about HTTP, HTML, or JSON.
- **View** (`templates/`) — the HTML the user actually sees. Knows nothing about where the data came from, it just renders whatever it's given.
- **Controller** (`controllers/`) — the bridge. Receives the HTTP request, asks the Model for data, hands that data to a View (or turns it straight into JSON), and returns the result. Each resource (`User`, `Announcement`) has two controllers on purpose: one serves human users through HTML pages (`UserController`, `AnnouncementController`), the other serves other programs through JSON (`ApiUserController`, `ApiAnnouncementController`) — both talk to the exact same Model underneath.

## Prerequisites

- Docker and Docker Compose installed (recommended way to run this project)
- Python 3.12 (only needed for the local, non-Docker alternative)

## How to Run (Recommended: Docker Compose)

First, create your local `.env` file from the provided example (this holds database credentials and is never committed to git):

```bash
cp .env.example .env
```

Then run:

```bash
docker compose up --build
```

This starts two containers: the Flask app (`web`) and a PostgreSQL database (`db`). The app reads and writes directly to PostgreSQL for both `User` and `Announcement` — data now survives restarts. The app will be available at `http://localhost:5000`. Stop everything with `Ctrl+C`, then `docker compose down`.

### Seeding sample data into the database

Once the containers are running, you can fill the database with realistic fake data (10 users, 5 announcements) using the Factory + Seed scripts:

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

| Method | Path                          | Description                          |
|--------|-------------------------------|---------------------------------------|
| GET    | `/`                           | Temporary main page                   |
| GET    | `/hello`                      | Returns `Hello, World!`               |
| GET    | `/hello/<name>`               | Returns `Hello, <name>!`              |
| GET    | `/sum/<number1>/<number2>`    | Returns the sum of two numbers        |
| GET    | `/about`                      | Temporary about page                  |
| GET    | `/users`                      | HTML page listing alumni, with a form to create a new one (UserController) |
| POST   | `/users`                      | Creates an alumni record from the HTML form and redirects back to the list |
| GET    | `/users/<id>/edit`            | HTML form pre-filled with the record's current data |
| POST   | `/users/<id>/edit`             | Saves the edited record and redirects back to the list |
| POST   | `/users/<id>/delete`           | Deletes the record and redirects back to the list |
| GET    | `/api/health`                 | Returns `{"status": "ok"}` as JSON    |
| POST   | `/api/users`                  | Creates an alumni record from form data (`first_name`, `last_name`, `graduation_year`, `email`) and returns it (with an auto-generated `id`) as JSON |
| GET    | `/api/users`                  | Returns all alumni records created so far, as a JSON list |
| PUT    | `/api/users/<id>`             | Replaces all fields of the record with the given `id` and returns it as JSON |
| PATCH  | `/api/users/<id>`             | Updates only the given fields of the record with the given `id` and returns it as JSON |
| DELETE | `/api/users/<id>`             | Deletes the record with the given `id` and returns the deleted record as JSON |
| GET    | `/announcements`              | HTML page listing announcements, with a form to create a new one (AnnouncementController) |
| POST   | `/announcements`              | Creates an announcement from the HTML form and redirects back to the list |
| GET    | `/announcements/<id>/edit`    | HTML form pre-filled with the announcement's current data |
| POST   | `/announcements/<id>/edit`    | Saves the edited announcement and redirects back to the list |
| POST   | `/announcements/<id>/delete`  | Deletes the announcement and redirects back to the list |
| POST   | `/api/announcements`          | Creates an announcement from form data (`title`, `content`, `date`) and returns it (with an auto-generated `id`) as JSON |
| GET    | `/api/announcements`          | Returns all announcements created so far, as a JSON list |
| PUT    | `/api/announcements/<id>`     | Replaces all fields of the announcement with the given `id` and returns it as JSON |
| PATCH  | `/api/announcements/<id>`     | Updates only the given fields of the announcement with the given `id` and returns it as JSON |
| DELETE | `/api/announcements/<id>`     | Deletes the announcement with the given `id` and returns the deleted record as JSON |
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
