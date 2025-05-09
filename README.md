
# FastAPI Project Structure

This repository represents a FastAPI-based backend application. It is structured with modularity, scalability, and maintainability in mind, following feature-based API design principles.

## Project Structure

```
app/                      # Main application package
├── main.py               # FastAPI app entrypoint
├── api/                  # API routing layer (feature-based)
│   ├── v1/               # API version 1
│   │   ├── __init__.py
│   │   ├── user/         # User feature module
│   │   │   ├── endpoints.py  # API routes
│   │   │   ├── schema.py     # Pydantic models
│   │   │   ├── service.py    # Business logic
│   │   │   ├── repository.py # DB interactions
│   │   │   └── model.py      # ORM models
│   │   └── auth/         # Auth feature module
│   │       ├── endpoints.py  # Auth routes
│   │       ├── schema.py     # Auth Pydantic models
│   │       ├── service.py    # Auth business logic
│   │       ├── repository.py # Auth DB interactions
│   │       └── model.py      # Auth ORM models
│   └── __init__.py
├── core/                 # Application core components
│   ├── config.py         # App-wide config (Pydantic settings)
│   ├── security.py       # JWT, password hashing
│   ├── logging.py        # Logging setup
│   ├── events.py         # Startup/shutdown handlers
│   └── db/               # Database core
│       ├── base.py       # Base class for ORM models
│       ├── session.py    # DB session management
│       └── migrations/   # Alembic migrations
├── services/             # Cross-domain services
│   ├── email_service.py  # Email service integration
│   ├── mock_email_service.py  # Mock email service for testing
│   └── ...              # Other services (SMS, files, etc.)
└── utils/                # Utility functions
├── exceptions.py         # Custom exceptions
├── hashing.py            # Hashing utilities
└── ...
```

## Installation

To get started, clone the repository and set up a Python virtual environment:

```bash
git clone <repository-url>
cd <repository-folder>
python3 -m venv venv
source venv/bin/activate
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Configuration

The application configuration is handled via Pydantic settings in the `core/config.py` file. Adjust the environment variables for your database, JWT, and other services in this file.

### Example:

```python
class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    ...
```

## Database Setup

Database configurations and session management are handled in `core/db/session.py`. If you are using PostgreSQL or another database, adjust the connection URL and other settings.

To set up the database, run Alembic migrations:

```bash
alembic upgrade head
```

## Running the Application

To run the FastAPI application locally, use the following command:

```bash
uvicorn app.main:app --reload
```

This will start the development server at `http://127.0.0.1:8000`.

## API Documentation

Once the application is running, you can access the auto-generated API documentation at:

- [Swagger UI](http://127.0.0.1:8000/docs)
- [ReDoc](http://127.0.0.1:8000/redoc)

## Features

### Authentication & User Management
- User sign-up and login.
- JWT-based authentication.
- Google OAuth 2.0 authentication.

### Database & Models
- PostgreSQL database with SQLAlchemy ORM models.
- Pydantic models for data validation and serialization.
- Alembic migrations for database schema versioning.

### Services
- Email service for notifications (mock and real implementations).

### Utils
- Custom utility functions for hashing, exception handling, etc.

## Tests

Run the tests with:

```bash
pytest
```

## Contributing

We welcome contributions! Please feel free to open an issue or submit a pull request.

## License

This project is licensed under the MIT License.
