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

### SMS Verification Flow

1. **Send Verification Code:**

   ```http
   POST /api/v1/auth/sms/send
   Content-Type: application/json

   {
     "phone": "+1234567890"
   }
   ```

2. **Verify Code:**

   ```http
   POST /api/v1/auth/sms/verify
   Content-Type: application/json

   {
     "phone": "+1234567890",
     "code": "123456"
   }
   ```

3. **Check Verification Status:**
   ```http
   GET /api/v1/auth/sms/status/+1234567890
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

The project includes a comprehensive test suite covering server health, database operations, configuration, and API endpoints.

#### Quick Test Run

```bash
# Run all tests
pytest

# Run all tests with verbose output
pytest -v

# Run tests with coverage report
pytest --cov=src --cov-report=html --cov-report=term-missing

# Run specific test files
pytest tests/file_name.py        # Health checks
```

#### Test Configuration

Tests use an isolated in-memory SQLite database to ensure:

- Fast execution
- No interference with development data
- Consistent test environment
- Parallel test execution safety

#### Test Script

Use the provided test runner for comprehensive testing:

```bash
# Make executable and run
chmod +x run_tests.sh
./run_tests.sh
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

# Twilio SMS Configuration (Required for SMS verification)
TWILIO_ACCOUNT_SID=your_twilio_account_sid_here
TWILIO_AUTH_TOKEN=your_twilio_auth_token_here
TWILIO_PHONE_NUMBER=+1234567890
```

## SMS Verification Setup

This application includes SMS verification functionality powered by Twilio. Users must verify their phone numbers via SMS before registering with passkeys.

**Note:** SMS verification can be disabled by setting `SMS_VERIFICATION_ENABLED=False` in your environment variables. This is useful for testing or development environments where SMS verification is not needed.

### Twilio Configuration

1. **Create a Twilio Account:**

   - Go to [Twilio Console](https://console.twilio.com)
   - Sign up for a new account or log in to existing account
   - Verify your account (required for phone number provisioning)

2. **Get Your Credentials:**

   - Copy your **Account SID** from the Console Dashboard
   - Copy your **Auth Token** from the Console Dashboard

3. **Get a Phone Number:**

   - Go to Phone Numbers > Manage > Buy a number
   - Choose a phone number with SMS capabilities
   - Copy the phone number (include country code, e.g., +1234567890)

4. **Configure Environment Variables:**

   ```bash
   TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   TWILIO_AUTH_TOKEN=your_auth_token_here
   TWILIO_PHONE_NUMBER=+1234567890

   # Optional: Disable SMS verification for testing/development
   SMS_VERIFICATION_ENABLED=True  # Set to False to disable
   ```
