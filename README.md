# Ask AI — Async Q&A Interface

A FastAPI-powered web application that lets users ask natural-language questions about a university scheduling database. Questions are answered by an AI that generates and executes safe, read-only SQLAlchemy queries against the database.

---

## Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [Architecture](#architecture)
- [Database Schema](#database-schema)
- [Setup & Installation](#setup--installation)
- [Environment Variables](#environment-variables)
- [Running the App](#running-the-app)
- [Seeding the Database](#seeding-the-database)
- [API Endpoints](#api-endpoints)
- [How It Works](#how-it-works)
- [Frontend](#frontend)
- [Testing](#testing)
- [Security](#security)

---

## Overview

Users type a question (e.g. *"Which lessons are scheduled as tests?"*), and the system:
1. Sends the question to an AI model (GPT-4.1-mini via OpenAI).
2. The AI generates a safe, read-only SQLAlchemy ORM query.
3. The query is executed against a PostgreSQL database.
4. The result is returned and displayed to the user.
5. Useful answers can be **saved** and re-run later from the "Ask Again" panel.

---

## Project Structure

```
.
├── app.py                        # FastAPI app entry point
├── main.py                       # Entry point — run with: python main.py
├── db.py                         # SQLAlchemy engine & session setup
├── models.py                     # ORM models (Lecturer, Room, Course, Lesson, Category, Question)
├── seed.py                       # Database seed script
│
├── ai_service/
│   ├── executor.py               # Executes AI-generated code in a sandboxed local scope
│   ├── service.py                # Calls OpenAI API, builds prompt, returns structured response
│   ├── prompt.py                 # Full system prompt template for the AI
│   ├── utility.py                # JSON parsing, category helpers
│   └── model.txt                 # Schema snapshot passed to the AI as context
│
├── question_service/
│   ├── service.py                # Save/retrieve saved questions; re-execute stored code
│   └── executor.py               # Executes stored code with a live session
│
├── crud/
│   └── question.py               # CRUD operations for the Question model
│
├── ui_server/
│   ├── utility.py                # Fallback task helper
│   └── routes/
│       ├── ask_route.py          # POST /ask, GET /ask/{task_id}, POST /ask/{task_id}/save
│       └── ask_again_route.py    # GET /ask/again/questions/{q_id}, GET /ask/again/titles
│
└── templates/
    └── static/
        ├── index.html            # Jinja2 HTML template
        ├── style.css             # Dark-mode UI styles
        └── main.js               # Frontend async logic (fetch, polling, save)
```

---

## Architecture

```
Browser  ──POST /ask──►  ask_route.py  ──►  ai_service/executor.py
                                                    │
                              OpenAI API ◄──── service.py ◄────┘
                                    │
                              executor.py  (exec AI code in sandboxed scope)
                                    │
                             PostgreSQL DB  (read-only ORM queries)
                                    │
                         ◄── task result stored in memory ──► GET /ask/{task_id}
                                    │
                         POST /ask/{task_id}/save  ──►  question_service/service.py
                                    │
                              Question saved to DB
                                    │
                         GET /ask/again/titles  +  GET /ask/again/questions/{id}
```

---

## Database Schema

### `lecturers`
| Column | Type        | Notes                         |
|--------|-------------|-------------------------------|
| id     | Integer, PK |                               |
| name   | String(40)  | Min 2 words, min 2 chars each |

### `rooms`
| Column   | Type        | Notes               |
|----------|-------------|---------------------|
| id       | Integer, PK |                     |
| building | Integer     |                     |
| number   | Integer     | Unique per building |
| capacity | Integer     | >= 0                |

### `courses`
| Column      | Type           | Notes                   |
|-------------|----------------|-------------------------|
| id          | Integer, PK    |                         |
| name        | String(40)     |                         |
| lecturer_id | FK → lecturers |                         |
| year        | Integer        |                         |
| semester    | String(1)      | e.g. `"A"` or `"B"`    |

### `lessons`
| Column    | Type         | Notes           |
|-----------|--------------|-----------------|
| id        | Integer, PK  |                 |
| course_id | FK → courses |                 |
| room_id   | FK → rooms   |                 |
| date      | DateTime     |                 |
| is_test   | Boolean      | Default `False` |

### `categories`
| Column | Type        | Notes  |
|--------|-------------|--------|
| id     | Integer, PK |        |
| name   | String(30)  | Unique |

Default categories: `Schedule`, `General Information`, `Technical Issue`

### `questions` (saved Q&A)
| Column      | Type            | Notes                  |
|-------------|-----------------|------------------------|
| id          | Integer, PK     |                        |
| category_id | FK → categories |                        |
| title       | String(50)      |                        |
| code        | Text            | Stored SQLAlchemy code |

---

## Setup & Installation

### Prerequisites
- Python 3.11+
- PostgreSQL
- An OpenAI API key

### Install dependencies

```bash
pip install -r requirements.txt
```



---

## Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

```env
DATABASE_URL=postgresql+psycopg2://<username>:<password>@localhost:5432/Campus_Project
OPENAI_API_KEY=<your openAI key>
```

| Variable | Description |
|---|---|
| `DATABASE_URL` | PostgreSQL connection string — replace `<username>` and `<password>` |
| `OPENAI_API_KEY` | Your OpenAI API key |

---

## Running the App

```bash
python main.py
```

Then open [http://localhost:8000](http://localhost:8000) in your browser.

> Internally this runs `uvicorn ui_server.app:app --host 0.0.0.0 --port 8000 --reload`. To disable hot reload or change the port, edit `main.py`.

---

## Seeding the Database

Populates the database with sample lecturers, rooms, courses, lessons, and categories:

```bash
python seed.py
```

**Seed data includes:**
- 2 lecturers: Daniel Cohen, Sarah Miller
- 3 rooms in building 1 (capacity 30, 50, 120)
- 3 courses: Introduction to Algorithms, Operating Systems, Database Systems
- 24 lessons across 8 weeks, including test lessons and early-start slots
- 3 categories: Schedule, General Information, Technical Issue

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET`  | `/` | Serve the main UI |
| `GET`  | `/get_token` | Generate a unique user session token |
| `POST` | `/ask/` | Submit a question (async, returns `task_id`) |
| `GET`  | `/ask/{task_id}` | Poll for result status and answer |
| `POST` | `/ask/{task_id}/save` | Save a completed answer to the database |
| `GET`  | `/ask/again/titles` | List all saved question titles |
| `GET`  | `/ask/again/questions/{q_id}` | Re-execute and return a saved question |

### Example Flow

**POST `/ask/`**
```json
// Header:  user-token: <token>
// Body:
{ "question": "How many lessons are scheduled as tests?" }

// Response:
{ "task_id": "uuid-..." }
```

**GET `/ask/{task_id}`**
```json
// Header:  user-token: <token>
{
  "status": "done",
  "title": "Total Test Lessons",
  "category": "Schedule",
  "answer": "Total number of test lessons: 3",
  "save": 1
}
```

---

## How It Works

1. **Token** — Each browser session obtains a UUID token via `GET /get_token`.
2. **Submit** — The question is POSTed and a background thread begins processing.
3. **Prompt** — `ai_service/service.py` builds a prompt from `prompt.py`, injecting the DB schema (`model.txt`) and available categories.
4. **Code Generation** — The AI returns a strict JSON object with `title`, `category`, and `code` fields. The `code` value contains a one-liner SQLAlchemy ORM query.
5. **Execution** — `ai_service/executor.py` runs the code via `exec()` with only the four ORM models and the active session in scope.
6. **Result** — The human-readable string assigned to `s` inside the generated code is returned as the answer.
7. **Polling** — The frontend polls `GET /ask/{task_id}` every second until `status == "done"` (times out after 10 polls).
8. **Save** — If the answer is valid (category ≠ error), the user may save it. Saved questions store the generated code so they can be re-executed on demand from the "Ask Again" panel.

---

## Frontend

Built with vanilla HTML, CSS, and JavaScript — no framework required.

- **Ask section** — Textarea input, async polling with a status spinner, answer display with title and category tag, and an optional Save button.
- **Ask Again section** — Lists all saved question titles; clicking one re-fetches and displays the live answer in an expandable panel.
- **Keyboard shortcut** — `Ctrl+Enter` / `Cmd+Enter` submits the question.
- Fonts: [Syne](https://fonts.google.com/specimen/Syne) (headings) + [DM Mono](https://fonts.google.com/specimen/DM+Mono) (body/code).

---

## Testing

The project uses a **manual test script** (no test framework) to verify the AI pipeline end-to-end — from question input through OpenAI response, code execution, and final answer output.

### Location

```
tests/
└── ai_test.py
```

### How to run

Make sure your `.env` is configured and the database is seeded, then run:

```bash
python -m tests.ai_test
```

Or from inside the `tests/` folder:

```bash
python ai_test.py
```

### What it tests

The script runs a curated list of 45 questions through the full `execute()` pipeline and prints the `title`, `category`, and `answer` for each. The questions are organized into groups:

| Group | Count | Purpose |
|---|---|---|
| ✅ Simple legitimate queries | 5 | Basic selects — lessons, lecturers, rooms, courses, counts |
| ✅ Legitimate with JOINs | 5 | Multi-model queries with relationships |
| ✅ Legitimate with filters | 5 | Filtered queries by ID, name, null values |
| ❌ Mutation attempts | 5 | DELETE, UPDATE, INSERT, DROP, ALTER — should all return fallback |
| ❌ External import / scope tricks | 5 | CSV export, `sorted()`, `func.count()`, `desc()` — tests import handling |
| ❌ Prompt injection | 5 | Embedded instructions trying to override the AI's rules |
| ❌ Out of scope | 5 | Weather, poems, non-existent tables — should return fallback |
| 🧠 Edge cases | 5 | Borderline inputs: raw SQL via `session.execute()`, inline deletes, schema probing |

### What to look for

**For ✅ legitimate questions** — expect a real answer with a meaningful `title`, a valid `category` (Schedule / General Information / Technical Issue), and a formatted `answer` string.

**For ❌ invalid questions** — expect the fallback:
```
title    → "Invalid Request"
category → "error"
answer   → "Error: <reason>"
```

**For 🧠 edge cases** — these are intentionally ambiguous. Review whether the AI correctly refuses or safely handles them.

### Example output

```
Total Lesson Count
Schedule
Total number of lessons currently in the database: 24

Invalid Request
error
Error: Mutation operations are not permitted.
```

---

## Security

The AI is strictly constrained to **read-only** operations:

- `INSERT`, `UPDATE`, `DELETE`, `DROP`, and raw SQL are all forbidden.
- Only SQLAlchemy ORM queries through the four provided models are permitted.
- No new session creation — the session is pre-injected by the executor.
- Prompt injection attempts in user questions trigger an immediate fallback response.
- The `exec()` sandbox exposes only the four ORM models, the active session, and Python builtins — nothing else.
- User tokens ensure that task results are only accessible by the session that created them.
