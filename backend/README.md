# Healthcare Management System - Backend

A modular FastAPI backend for a healthcare management system with authentication, appointments, and medical records.

## Tech Stack

- FastAPI 0.115.6
- PostgreSQL (production) / SQLite (local development)
- Session-based authentication with Passkey (WebAuthn) support
- Twilio integration for phone verification
- AWS S3 compatible storage
- Google Gemini integration
- Redis caching
- Pytest with coverage

## Features

- User management (registration, login, profiles)
- Healthcare provider profiles and specializations
- Appointment scheduling and management
- Medical record storage and retrieval
- Emergency contact management
- Medication tracking
- Secure authentication with Passkey support
- SMS phone verification

## Project Structure

```
backend/
├── main.py                     # FastAPI app entry point
├── requirements.txt            # Python dependencies
├── setup.sh                   # Quick setup script
├── alembic/                   # Database migrations
├── src/                       # Source code
│   ├── api/                   # API routes
│   ├── core/                  # Core application logic & auth
│   ├── db/                    # Database configuration
│   ├── models/                # SQLAlchemy models
│   ├── schemas/               # Pydantic schemas
│   ├── services/              # Business logic
│   └── utils/                 # Utilities
└── tests/                     # Test files
```

## Quick Setup

### Prerequisites

- Python 3.11+
- PostgreSQL (optional, SQLite works for development)

### Installation

1. **Run the setup script:**

   ```bash
   cd backend
   chmod +x setup.sh
   ./setup.sh
   ```

2. **Manual setup:**

   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate  # On macOS/Linux
   pip install -r requirements.txt
   ```

3. **Configure environment variables:**

   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

4. **Start the server:**
   ```bash
   python main.py
   ```

## Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```bash
# Database (required)
DATABASE_URL=sqlite:///./app.db  # or postgresql://user:pass@localhost/dbname

# Security (required)
SECRET_KEY=your-secret-key-here

# SMS Verification via Twilio (optional)
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=+1234567890
SMS_VERIFICATION_ENABLED=True

# AWS S3 for file storage (optional)
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1
S3_BUCKET_NAME=your_bucket_name

# Google Gemini AI (optional)
GOOGLE_API_KEY=your_gemini_api_key

# Redis for caching (optional)
REDIS_URL=redis://localhost:6379/0
```

### Where to Get API Keys

- Twilio: [console.twilio.com](https://console.twilio.com) → Account SID & Auth Token
- AWS S3: [AWS IAM Console](https://console.aws.amazon.com/iam/) → Create access key
- Google Gemini: [Google AI Studio](https://makersuite.google.com/app/apikey) → Create API key

## API Documentation

Once running, visit:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Authentication

For detailed authentication setup and usage, see [AUTHENTICATION.md](./AUTHENTICATION.md).

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Use test script
./run_tests.sh
```

## Database Migrations

```bash
# Create migration after model changes
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head
```

## Deployment

The project includes config files for Railway, Nixpacks, and Heroku. For production:

1. Set `DATABASE_URL` to PostgreSQL
2. Ensure all required environment variables are set
3. Run migrations: `alembic upgrade head`
