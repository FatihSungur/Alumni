# 🎓 Alumni Web Programming

A web platform built for the Web Programming course to connect graduates with their alma mater. The goal is to give alumni a place to keep their career info up to date and give the institution a simple way to track alumni outcomes over time. The project is under active, incremental development, with each course milestone adding a new capability on top of the last.

## 🚀 Key Features (Planned & In Progress)

- **Alumni Directory:** Basic profile and listing endpoints for graduates.
- **Greeting & Utility Endpoints:** Early API building blocks (`/hello`, `/sum`, etc.) used to learn and validate the routing layer.
- **Static Pages:** Home and About pages describing the project.
- **Containerized Deployment:** Docker & Docker Compose setup so the app runs identically on any machine.
- **Future Milestones:** Alumni profile management, search/filtering, and a persistent database layer will be added in upcoming weeks.

## Tech Stack

- **Language:** Python 3.12
- **Framework:** Flask
- **Containerization:** Docker & Docker Compose

## Prerequisites

- Docker and Docker Compose installed (recommended way to run this project)
- Python 3.12 (only needed for the local, non-Docker alternative)

## How to Run (Recommended: Docker Compose)

Run these exact commands from the project root:

```bash
docker compose up --build
```

The app will start and be available at `http://localhost:5000`. Stop it with `Ctrl+C`, then `docker compose down`.

## Alternative: Run Locally with Python

```bash
pip install -r requirements.txt
python app.py
```

The app will be available at `http://localhost:5000`.

## API Endpoints

| Method | Path                          | Description                          |
|--------|-------------------------------|---------------------------------------|
| GET    | `/`                           | Temporary main page                   |
| GET    | `/hello`                      | Returns `Hello, World!`               |
| GET    | `/hello/<name>`               | Returns `Hello, <name>!`              |
| GET    | `/sum/<number1>/<number2>`    | Returns the sum of two numbers        |
| GET    | `/about`                      | Temporary about page                  |
| GET    | `/api/health`                 | Returns `{"status": "ok"}` as JSON    |
| POST   | `/api/users`                  | Creates an alumni record from form data (`first_name`, `last_name`, `graduation_year`, `email`) and returns it (with an auto-generated `id`) as JSON |
| GET    | `/api/users`                  | Returns all alumni records created so far, as a JSON list |
| PUT    | `/api/users/<id>`             | Replaces all fields of the record with the given `id` and returns it as JSON |
| PATCH  | `/api/users/<id>`             | Updates only the given fields of the record with the given `id` and returns it as JSON |
| DELETE | `/api/users/<id>`             | Deletes the record with the given `id` and returns the deleted record as JSON |
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

Afterwards, visit `http://localhost:5000/api/users` in a browser (GET) to see the list of alumni records created so far. Records are kept in memory only, so they reset when the server restarts.
