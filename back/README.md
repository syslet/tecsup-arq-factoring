# Backend Core Service

This is the backend service for the factoring core application. Built with **Flask** and **Python 3.11** under **Onion Architecture** and managed with **uv**.

---

## 1. Directory Structure

The codebase is structured following the Onion Architecture pattern to keep the Domain model isolated from frameworks and drivers:

```
back/
├── src/
│   ├── domain/             # Core business models, interfaces, and exceptions
│   │   ├── entities/       # Pure domain models
│   │   ├── value_objects/  # Immutable domain values
│   │   ├── exceptions/     # Domain-specific errors
│   │   └── repositories/   # Abstract repository interfaces
│   ├── application/        # Use cases and domain service interfaces
│   │   ├── use_cases/      # Application workflows
│   │   └── services/       # Third-party adapters abstract interfaces
│   ├── infrastructure/     # Database adapters, API clients, and DI setup
│   │   ├── db/             # SQLAlchemy ORM and repository implementations
│   │   ├── clients/        # Web clients for external services
│   │   └── di/             # Dependency injection container
│   └── presentation/       # API layer (Flask blueprints and Pydantic schemas)
│       ├── app.py          # Application factory
│       ├── routes/         # Flask blueprints (endpoints)
│       └── schemas/        # Request/Response validation schemas
└── tests/                  # Pytest unit and integration test suite
```

---

## 2. Local Development Setup

Ensure you have [uv](https://github.com/astral-sh/uv) installed on your system.

### Create Virtual Environment & Install Dependencies
Run the following command to automatically create a virtual environment and install all packages:
```bash
uv sync
```

### Run the Flask Application
Start the development server:
```bash
uv run flask run --port 8000
```

---

## 3. Testing, Linting & Formatting

### Run Tests
```bash
uv run pytest
```

### Run Ruff (Linter & Formatter)
```bash
uv run ruff check --fix
uv run ruff format
```

### Run Mypy (Static Type Checker)
```bash
uv run mypy src
```
