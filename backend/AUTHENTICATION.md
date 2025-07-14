# Authentication Middleware Guide

## Overview

The backend now includes a comprehensive authentication middleware system that uses session tokens stored in HTTP-only cookies for secure authentication.

## Usage Examples

### 1. Protected Route (Authentication Required)

```python
@router.get("/protected-endpoint")
def protected_endpoint(current_user = Depends(RequireActiveAuth)):
    """Only authenticated active users can access this"""
    return {"message": f"Hello {current_user.name}"}
```

### 2. User-Specific Resource Access

```python
@router.get("/users/{user_id}/profile")
def get_user_profile(
    user_id: int,
    current_user = Depends(RequireActiveAuth)
):
    """User can only access their own profile"""
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    return {"profile": "user data"}
```

## Current Implementation Status

### ✅ **Implemented & Protected Routes:**

#### Authentication Routes (`/auth/`)

- `POST /auth/passkey/register/challenge` - ❌ Public (no auth needed)
- `POST /auth/passkey/register/verify` - ❌ Public (no auth needed)
- `POST /auth/passkey/login/challenge` - ❌ Public (no auth needed)
- `POST /auth/passkey/login/verify` - ❌ Public (no auth needed)
- `GET /auth/passkey/user/{user_id}` - ✅ **Protected** (user ownership validation)
- `POST /auth/logout` - ✅ **Protected** (requires session cookie)
- `GET /auth/me` - ✅ **Protected** (returns current user info)

#### User Routes (`/users/`)

- `GET /users/` - ✅ **Protected** (prevents DOS attacks)
- `GET /users/{user_id}` - ✅ **Protected** (user ownership validation)
- `PUT /users/{user_id}` - ✅ **Protected** (user ownership validation)

## Frontend Integration

### Cookie Configuration

Session tokens are automatically managed via HTTP-only cookies:

```javascript
// All requests include credentials to send cookies
fetch("/api/v1/auth/me", {
  credentials: "include", // Important: includes session cookie
});
```

### Example Frontend Flow

```typescript
// 1. Login/Register - cookie set automatically
const loginResponse = await fetch("/api/v1/auth/passkey/login/verify", {
  method: "POST",
  credentials: "include",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(verificationData),
});

// 2. Access protected routes - cookie sent automatically
const userProfile = await fetch("/api/v1/auth/me", {
  credentials: "include",
});

// 3. Logout - clears cookie
await fetch("/api/v1/auth/logout", {
  method: "POST",
  credentials: "include",
});
```

## Adding Authentication to New Routes

### Step 1: Import the middleware

```python
from src.core.auth_middleware import RequireActiveAuth, OptionalAuth
```

### Step 2: Add dependency to route

```python
@router.get("/new-protected-route")
def new_route(current_user = Depends(RequireActiveAuth)):
    # Route implementation
    pass
```

## Error Responses

### 401 Unauthorized

- No session token provided
- Invalid or expired session token

### 403 Forbidden

- User account deactivated
- Attempting to access another user's resources
- Insufficient privileges

## Configuration

Session settings can be configured in `src/core/config.py`:

```python
class Settings:
    SESSION_TOKEN_EXPIRY = timedelta(hours=24)
    COOKIE_SECURE = False  # Set True in production
    COOKIE_EXPIRY = timedelta(hours=24)
```

## Testing Authentication

### Test Protected Endpoint

```bash
# Without authentication (should fail)
curl http://localhost:8000/api/v1/auth/me

# With authentication (after login)
curl http://localhost:8000/api/v1/auth/me \
  -H "Cookie: session_token=your_session_token"
```
