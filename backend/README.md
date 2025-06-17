# FastAPI Backend Setup

A clean, modular FastAPI backend with PostgreSQL/SQLite, Redis caching, and Celery for background tasks.

## Tech Stack

- **Framework**: FastAPI 0.115.6
- **Database**: PostgreSQL (production) / SQLite (local development) with SQLAlchemy ORM 2.0.36
- **Database Drivers**: psycopg2-binary + psycopg[binary] for PostgreSQL
- **Caching**: Redis
- **Background Tasks**: Celery with Redis broker
- **Authentication**: Ready for implementation (JWT, Passkey support planned)
- **Migrations**: Alembic
- **Testing**: Pytest

## Project Structure

```
backend/
├── main.py                     # FastAPI app entry point
├── celery_worker.py           # Celery worker entry point
├── alembic.ini               # Alembic configuration
├── requirements.txt          # Python dependencies
├── .env                     # Environment variables (local)
├── .env.example             # Environment variables template
├── setup.sh                 # Quick setup script
├── alembic/                 # Database migrations
│   ├── env.py
│   └── versions/
├── src/                     # Source code
│   ├── api/                 # API routes
│   │   ├── __init__.py      # API router setup
│   │   └── users.py         # User endpoints (register, login, logout, session)
│   ├── core/                # Core application logic
│   │   ├── config.py        # Configuration with SQLite/PostgreSQL support
│   │   └── celery_app.py    # Celery configuration
│   ├── db/                  # Database configuration
│   │   └── database.py      # Database connection with auto-detection
│   ├── models/              # SQLAlchemy models
│   │   └── user.py          # User model (id, name, email, created_at)
│   ├── schemas/             # Pydantic schemas
│   │   └── user.py          # User schemas (Create, Update, Response, Login, Session)
│   ├── services/            # Business logic
│   │   └── user_service.py  # User service (register_user, login_user, logout_user, issue_session)
│   └── utils/               # Utilities
│       ├── cache.py         # Redis caching utilities
│       └── tasks.py         # Background tasks (notifications, reminders)
└── tests/                   # Test files
    ├── test_main.py
    └── test_user.py         # User functionality tests
```

│ │ └── notification_service.py
│ └── utils/ # Utilities
│ ├── **init**.py
│ ├── cache.py # Redis caching
│ └── tasks.py # Background tasks
└── tests/ # Test files
├── **init**.py
└── test_main.py

````

## Setup Instructions

### Quick Setup (Recommended)

```bash
cd backend
chmod +x setup.sh
./setup.sh
````

### Manual Setup

1. **Create virtual environment:**

   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate  # On macOS/Linux
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Database Setup:**

   **Option A: SQLite (Local Development - Default)**

   ```bash
   # Copy environment file
   cp .env.example .env
   # Keep DATABASE_URL=sqlite:///./app.db in .env
   # No additional setup needed - database file created automatically
   ```

   **Option B: PostgreSQL (Production/Local)**

   ```bash
   # Install PostgreSQL (if not already installed)
   brew install postgresql  # On macOS

   # Start PostgreSQL service
   brew services start postgresql

   # Create database
   createdb college_project

   # Update .env file:
   # DATABASE_URL=postgresql://username:password@localhost:5432/college_project
   ```

4. **Redis Setup (Optional - for caching and background tasks):**

   ```bash
   # Install Redis if not already installed
   brew install redis  # On macOS

   # Start Redis server
   redis-server
   # or as a service:
   brew services start redis
   ```

   or

   update `.env` to use Redis:

   ```bash
   # In .env
   REDIS_URL=YOUR_REDIS_URL
   ```

5. **Start the FastAPI server:**

   ```bash
   python main.py
   # or
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

6. **Start Celery worker (optional - for background tasks):**

   ```bash
   # In another terminal
   celery -A celery_worker worker --loglevel=info
   ```

## Database Configuration

The application automatically detects the database type from `DATABASE_URL`:

### SQLite (Default for Local Development)

- **URL**: `sqlite:///./app.db`
- **Benefits**: No setup required, file-based, great for development
- **File location**: `./app.db` in the backend directory

### PostgreSQL (Recommended for Production)

- **URL**: `postgresql://user:password@host:port/database`
- **Benefits**: Production-ready, better performance, concurrent access
- **Setup**: Requires PostgreSQL server installation

## API Endpoints

### Base URLs

- **Local Development**: `http://localhost:8000`
- **API Documentation**: `http://localhost:8000/docs` (Swagger UI)
- **Alternative Docs**: `http://localhost:8000/redoc`

### Health Checks

- `GET /` - Basic health check
- `GET /health` - Detailed health status

### Users API (`/api/v1/users`)

#### User Management

- `POST /register` - Register new user

  ```json
  {
    "name": "John Doe",
    "email": "john@example.com"
  }
  ```

- `POST /login` - User login

  ```json
  {
    "email": "john@example.com"
  }
  ```

- `POST /logout` - User logout (requires user_id)

- `POST /session/{user_id}` - Issue new session for user

#### Implemented User Functions (UML Schema)

- ✅ `register_user()` - User registration
- ✅ `login_user()` - User authentication
- ✅ `logout_user()` - User logout
- ✅ `issue_session()` - Session management

### Testing the API

```bash
# Health check
curl http://localhost:8000/health

# Register a user
curl -X POST "http://localhost:8000/api/v1/users/register" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test User", "email": "test@example.com"}'

# Login user
curl -X POST "http://localhost:8000/api/v1/users/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'
```

## Development Guidelines

### Adding New Models (For Team Members)

The project is structured to easily add new models. Here's how to add the remaining models:

#### 1. PasskeyCredential Model

```bash
# Add to src/models/passkey_credential.py
# Add to src/schemas/passkey_credential.py
# Add to src/services/passkey_service.py
# Add to src/api/passkey.py
```

#### 2. Medicine Model

```bash
# Add to src/models/medicine.py
# Add to src/schemas/medicine.py
# Add to src/services/medicine_service.py
# Add to src/api/medicines.py
```

#### 3. Appointment Model

```bash
# Add to src/models/appointment.py
# Add to src/schemas/appointment.py
# Add to src/services/appointment_service.py
# Add to src/api/appointments.py
```

#### 4. EmergencyContact Model

```bash
# Add to src/models/emergency_contact.py
# Add to src/schemas/emergency_contact.py
# Add to src/services/emergency_contact_service.py
# Add to src/api/emergency_contacts.py
```

#### 5. Document Model

```bash
# Add to src/models/document.py
# Add to src/schemas/document.py
# Add to src/services/document_service.py
# Add to src/api/documents.py
```

### Database Migrations

```bash
# When you add new models, create migrations:
alembic revision --autogenerate -m "Add [ModelName] table"

# Apply migrations
alembic upgrade head

# Check migration status
alembic current
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_user.py -v

# Run tests with output
pytest -s
```

### Environment Variables

Create a `.env` file based on `.env.example`:

```bash
# Database Configuration
DATABASE_URL=sqlite:///./app.db  # or PostgreSQL URL

# Redis Configuration (Optional)
REDIS_URL=redis://localhost:6379/0

# App Configuration
SECRET_KEY=your-secret-key-change-this-in-production
DEBUG=True

# Celery Configuration (Optional)
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```
