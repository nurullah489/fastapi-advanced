# FastAPI Advanced

A production-grade FastAPI project built on top of the [fastapi-crud-template](https://github.com/nurullah489/fastapi-learning).

## Features

- **Database** — PostgreSQL with SQLAlchemy (async) and Alembic migrations
- **Authentication** — JWT-based auth with access and refresh tokens
- **Project Structure** — Modular routers, models, schemas, and services
- **Testing** — pytest with async test client
- **Containerization** — Docker and Docker Compose
- **RL Gym Integration** — FastAPI wrapper around OpenAI Gymnasium environments

## Project Structure

```
app/
├── main.py                  # Entry point
├── dependencies.py          # Shared dependencies
├── database.py              # DB connection and session
├── routers/
│   ├── users.py
│   ├── items.py
│   └── auth.py
├── models/
│   ├── user.py              # SQLAlchemy ORM models
│   └── item.py
├── schemas/
│   ├── user.py              # Pydantic schemas
│   └── item.py
├── services/
│   ├── user_service.py      # Business logic
│   └── item_service.py
└── core/
    ├── config.py            # Environment config
    └── security.py          # JWT utilities
```

## Requirements

- Python 3.12+
- PostgreSQL 16+
- Docker (optional)

## Setup

### 1. Clone the repo
```bash
git clone https://github.com/nurullah489/fastapi-advanced.git
cd fastapi-advanced
```

### 2. Create and activate virtual environment
```bash
uv venv .venv --python 3.12
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Linux/Mac
```

### 3. Install dependencies
```bash
uv pip install -r requirements.txt
```

### 4. Configure environment variables
```bash
cp .env.example .env
# Edit .env with your DB credentials and secret key
```

### 5. Run database migrations
```bash
alembic upgrade head
```

### 6. Run the application
```bash
uvicorn app.main:app --reload
```

### 7. Run with Docker
```bash
docker compose up --build
```

## API Documentation

Once running, visit:
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Running Tests

```bash
pytest -v
```

## Environment Variables

| Variable | Description | Example |
|---|---|---|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+asyncpg://user:pass@localhost/dbname` |
| `SECRET_KEY` | JWT signing key | `your-secret-key` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT expiry | `30` |
| `API_KEY` | API key for protected routes | `secret-key-123` |

## Roadmap

- [x] Basic CRUD with in-memory store
- [ ] PostgreSQL + SQLAlchemy integration
- [ ] Alembic migrations
- [ ] JWT authentication
- [ ] pytest test suite
- [ ] Docker + Docker Compose
- [ ] RL Gym API wrapper
