# Authentication System Documentation

## Overview

This project uses JWT (JSON Web Token) based authentication with bcrypt password hashing for secure user authentication and authorization.

## Features

- ✅ **Bcrypt Password Hashing** - Secure password storage
- ✅ **JWT Access Tokens** - Short-lived tokens (30 minutes default)
- ✅ **JWT Refresh Tokens** - Long-lived tokens (7 days default)
- ✅ **Session Management** - Database-backed session tracking
- ✅ **Token Refresh** - Seamless token renewal
- ✅ **Secure Logout** - Session invalidation

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Add these variables to your `.env` file:

```env
JWT_SECRET_KEY=your-secret-key-change-this-to-a-random-string
JWT_REFRESH_SECRET_KEY=your-refresh-secret-key-change-this-to-a-different-random-string
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

**⚠️ Important:** Use strong, random strings for the secret keys in production!

### 3. Create Database Tables

The `user_sessions` table will be automatically created when you run the application:

```sql
CREATE TABLE user_sessions (
    SessionId SERIAL PRIMARY KEY,
    UserId INTEGER NOT NULL REFERENCES users(UserId),
    RefreshToken VARCHAR(500) NOT NULL UNIQUE,
    ExpiresAt TIMESTAMP NOT NULL,
    IsValid BOOLEAN NOT NULL DEFAULT TRUE,
    CreatedAt TIMESTAMP DEFAULT NOW()
);
```

## API Endpoints

### 1. Signup (Register New User)

**POST** `/api/auth/signup`

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "full_name": "John Doe"
}
```

**Response (201):**
```json
{
  "success": true,
  "message": "User registered successfully",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user_id": 123,
  "token_type": "bearer"
}
```

### 2. Login

**POST** `/api/auth/login`

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response (200):**
```json
{
  "success": true,
  "message": "Login successful",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user_id": 123,
  "token_type": "bearer"
}
```

### 3. Refresh Token

**POST** `/api/auth/refresh`

**Request Body:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response (200):**
```json
{
  "success": true,
  "message": "Token refreshed successfully",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user_id": 123,
  "token_type": "bearer"
}
```

### 4. Logout

**POST** `/api/auth/logout`

**Request Body:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response (200):**
```json
{
  "success": true,
  "message": "Logged out successfully"
}
```

## Protecting Routes

### Using the Authentication Middleware

To protect a route, use the `get_current_user` dependency:

```python
from fastapi import Depends
from core.auth_middleware import get_current_user

@router.get("/protected-route")
def protected_route(current_user: dict = Depends(get_current_user)):
    """
    This route requires authentication.
    The current_user dict contains: user_id, email, exp, type
    """
    user_id = current_user["user_id"]
    email = current_user["email"]
    
    return {"message": f"Hello {email}!"}
```

### Making Authentication Optional

For routes that can work with or without authentication:

```python
from typing import Optional
from fastapi import Depends
from core.auth_middleware import get_optional_current_user

@router.get("/optional-auth-route")
def optional_auth_route(current_user: Optional[dict] = Depends(get_optional_current_user)):
    """
    This route works with or without authentication.
    """
    if current_user:
        return {"message": f"Hello {current_user['email']}!"}
    else:
        return {"message": "Hello guest!"}
```

## Client-Side Usage

### 1. Signup/Login Flow

```javascript
// Signup or Login
const response = await fetch('http://localhost:8000/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'password123'
  })
});

const data = await response.json();

// Store tokens
localStorage.setItem('access_token', data.access_token);
localStorage.setItem('refresh_token', data.refresh_token);
```

### 2. Making Authenticated Requests

```javascript
// Use access token in Authorization header
const response = await fetch('http://localhost:8000/api/protected-route', {
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
  }
});
```

### 3. Handling Token Expiration

```javascript
// If you get 401, refresh the token
if (response.status === 401) {
  const refreshResponse = await fetch('http://localhost:8000/api/auth/refresh', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      refresh_token: localStorage.getItem('refresh_token')
    })
  });
  
  const refreshData = await refreshResponse.json();
  
  // Update tokens
  localStorage.setItem('access_token', refreshData.access_token);
  localStorage.setItem('refresh_token', refreshData.refresh_token);
  
  // Retry the original request
  // ...
}
```

### 4. Logout

```javascript
await fetch('http://localhost:8000/api/auth/logout', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    refresh_token: localStorage.getItem('refresh_token')
  })
});

// Clear tokens
localStorage.removeItem('access_token');
localStorage.removeItem('refresh_token');
```

## Security Best Practices

1. **Use HTTPS in production** - Never send tokens over unencrypted connections
2. **Store tokens securely** - Use httpOnly cookies or secure storage
3. **Rotate secret keys regularly** - Change JWT secret keys periodically
4. **Set appropriate token expiration** - Balance security and user experience
5. **Validate all inputs** - Never trust client data
6. **Use strong passwords** - Enforce password complexity requirements
7. **Implement rate limiting** - Prevent brute force attacks
8. **Log authentication events** - Monitor for suspicious activity

## Token Structure

### Access Token Payload
```json
{
  "user_id": 123,
  "email": "user@example.com",
  "exp": 1234567890,
  "type": "access"
}
```

### Refresh Token Payload
```json
{
  "user_id": 123,
  "email": "user@example.com",
  "exp": 1234567890,
  "type": "refresh"
}
```

## Troubleshooting

### "Invalid or expired access token"
- The access token has expired (default: 30 minutes)
- Use the refresh token to get a new access token

### "Invalid or expired refresh token"
- The refresh token has expired (default: 7 days)
- User needs to log in again

### "Email already registered"
- The email is already in use
- User should log in instead or use a different email

### "Invalid email or password"
- Credentials are incorrect
- Check email and password

## File Structure

```
src/
├── core/
│   ├── auth_middleware.py      # Authentication middleware
│   ├── jwt_utils.py             # JWT token utilities
│   └── password_utils.py        # Password hashing utilities
├── models/DbModels/
│   └── user_session.py          # UserSession database model
├── api/modules/auth/
│   ├── services.py              # Authentication business logic
│   └── routers.py               # Authentication endpoints
└── schemas/
    └── backend_schemas.py       # Request/Response schemas
```

## Migration from Old System

The old SHA-256 based authentication has been replaced. Existing users will need to:

1. **Reset passwords** - Old SHA-256 hashes are incompatible with bcrypt
2. **Re-register** - Or implement a migration script to rehash passwords

## Support

For issues or questions, please refer to the main project documentation or contact the development team.
