# Authentication System Guide

## Overview

The backend uses session-based authentication with HTTP-only cookies and supports:

- Passkey authentication (WebAuthn) for secure, passwordless login
- SMS verification for phone number validation before registration

## Authentication Flow

### 1. SMS Verification (Required First)

Users must verify their phone number before they can register:

```http
POST /api/v1/auth/sms/send
{"phone": "+1234567890"}

POST /api/v1/auth/sms/verify
{"phone": "+1234567890", "code": "123456"}
```

### 2. Passkey Registration & Login

After SMS verification, users register and login using Passkeys (WebAuthn). Check `/docs` for detailed endpoints.

## Frontend Integration

All requests must include credentials to send session cookies:

```javascript
// Login/Register - cookie set automatically
fetch("/api/v1/auth/passkey/login/verify", {
  method: "POST",
  credentials: "include",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(verificationData),
});

// Access protected routes - cookie sent automatically
fetch("/api/v1/auth/me", {
  credentials: "include",
});

// Logout - clears cookie
fetch("/api/v1/auth/logout", {
  method: "POST",
  credentials: "include",
});
```

## Error Responses

- 401 Unauthorized: No/invalid session token
- 403 Forbidden: User deactivated or accessing another user's resources
