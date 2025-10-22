# 🔐 FastProxy Authentication Guide

FastProxy now supports **three authentication methods** for securing admin, audit, and API endpoints.

---

## 📋 Table of Contents

1. [Authentication Methods](#authentication-methods)
2. [HTTP Basic Auth](#1-http-basic-auth)
3. [JWT Token Authentication](#2-jwt-token-authentication)
4. [API Key Authentication](#3-api-key-authentication)
5. [TLS/HTTPS Configuration](#tlshttps-configuration)
6. [Rate Limiting](#rate-limiting)
7. [Security Best Practices](#security-best-practices)

---

## Authentication Methods

| Method | Use Case | Lifespan | Recommended For |
|--------|----------|----------|-----------------|
| **HTTP Basic Auth** | Quick admin access | Per-request | Development, manual testing |
| **JWT Tokens** | Web applications | 30 minutes (access) / 7 days (refresh) | Web apps, mobile apps |
| **API Keys** | Service-to-service | Permanent (until revoked) | Automation, CI/CD, services |

---

## 1. HTTP Basic Auth

The simplest authentication method. Credentials sent with every request.

### Setup

```bash
# Set credentials in environment
export FASTPROXY_ADMIN_USERNAME=admin
export FASTPROXY_ADMIN_PASSWORD=secure_password_here
```

Or in `.env` file:
```env
FASTPROXY_ADMIN_USERNAME=admin
FASTPROXY_ADMIN_PASSWORD=secure_password_here
```

### Usage

```bash
# Using curl
curl -u admin:password http://localhost:8000/admin/status

# Using httpie
http -a admin:password localhost:8000/admin/status
```

### Python Example

```python
import requests
from requests.auth import HTTPBasicAuth

response = requests.get(
    "http://localhost:8000/admin/status",
    auth=HTTPBasicAuth("admin", "password")
)
print(response.json())
```

### Pros & Cons

✅ **Pros:**
- Simple to implement
- No token management needed
- Works with all HTTP clients

❌ **Cons:**
- Credentials sent with every request
- No session management
- Less secure without HTTPS

---

## 2. JWT Token Authentication

Modern token-based authentication with short-lived access tokens and refresh tokens.

### Setup

```bash
# Generate a secure JWT secret
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Set in environment
export FASTPROXY_JWT_SECRET=your_generated_secret_here
```

Or in `.env` file:
```env
FASTPROXY_JWT_SECRET=your_generated_secret_here
```

### Flow

1. **Login** → Get tokens
2. **Use access_token** for requests (30 min lifetime)
3. **Refresh** when access_token expires (using refresh_token)

### Usage

#### Step 1: Login

```bash
# Login to get tokens
curl -X POST http://localhost:8000/auth/login \
  -u admin:password

# Response:
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### Step 2: Use Access Token

```bash
# Make authenticated requests
curl http://localhost:8000/admin/status \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."
```

#### Step 3: Refresh Token

```bash
# When access token expires, refresh it
curl -X POST http://localhost:8000/auth/refresh \
  -H "Authorization: Bearer <refresh_token>"

# Returns new token pair
{
  "access_token": "new_access_token...",
  "refresh_token": "new_refresh_token...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### Python Example

```python
import requests

# 1. Login
login_response = requests.post(
    "http://localhost:8000/auth/login",
    auth=("admin", "password")
)
tokens = login_response.json()

access_token = tokens["access_token"]
refresh_token = tokens["refresh_token"]

# 2. Use access token
headers = {"Authorization": f"Bearer {access_token}"}
response = requests.get("http://localhost:8000/admin/status", headers=headers)
print(response.json())

# 3. Refresh when needed
def refresh_access_token(refresh_token):
    response = requests.post(
        "http://localhost:8000/auth/refresh",
        headers={"Authorization": f"Bearer {refresh_token}"}
    )
    return response.json()
```

### JavaScript Example

```javascript
// 1. Login
async function login(username, password) {
  const response = await fetch('http://localhost:8000/auth/login', {
    method: 'POST',
    headers: {
      'Authorization': 'Basic ' + btoa(`${username}:${password}`)
    }
  });
  return await response.json();
}

// 2. Make authenticated request
async function getStatus(accessToken) {
  const response = await fetch('http://localhost:8000/admin/status', {
    headers: {
      'Authorization': `Bearer ${accessToken}`
    }
  });
  return await response.json();
}

// 3. Refresh token
async function refreshToken(refreshToken) {
  const response = await fetch('http://localhost:8000/auth/refresh', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${refreshToken}`
    }
  });
  return await response.json();
}

// Usage
const tokens = await login('admin', 'password');
const status = await getStatus(tokens.access_token);
```

### Token Lifetimes

| Token Type | Lifetime | Purpose |
|------------|----------|---------|
| Access Token | 30 minutes | Short-lived, for API requests |
| Refresh Token | 7 days | Long-lived, to get new access tokens |

### Pros & Cons

✅ **Pros:**
- Stateless (no server-side session)
- Credentials only sent once (during login)
- Short-lived access tokens
- Refresh tokens for session management

❌ **Cons:**
- More complex implementation
- Requires token storage on client
- Need refresh logic

---

## 3. API Key Authentication

Permanent authentication tokens for service-to-service communication.

### Setup

No setup required - API keys are managed through the API.

### Create API Key

**⚠️ IMPORTANT:** You need an existing API key or Basic Auth to create new keys.

#### Option A: Using HTTP Basic Auth

```bash
curl -X POST http://localhost:8000/auth/keys \
  -u admin:password \
  -H "Content-Type: application/json" \
  -d '{
    "name": "CI/CD Pipeline",
    "description": "Key for automated deployments"
  }'

# Response:
{
  "key_id": "a1b2c3d4e5f6g7h8",
  "name": "CI/CD Pipeline",
  "api_key": "fpx_6m7n8o9p0q1r2s3t4u5v6w7x8y9z0a1b2c3d4e5f",
  "key_prefix": "fpx_6m7n8o9",
  "created_at": "2025-01-22T12:00:00",
  "warning": "⚠️  Save this API key securely. It will not be shown again!"
}
```

**🚨 SAVE THE API KEY IMMEDIATELY - IT WILL NOT BE SHOWN AGAIN!**

#### Option B: Using Existing API Key

```bash
curl -X POST http://localhost:8000/auth/keys \
  -H "X-API-Key: fpx_existing_key_here" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New Service Key",
    "description": "Key for monitoring service"
  }'
```

### Use API Key

```bash
# Make requests with API key
curl http://localhost:8000/admin/status \
  -H "X-API-Key: fpx_6m7n8o9p0q1r2s3t4u5v6w7x8y9z0a1b2c3d4e5f"
```

### Manage API Keys

#### List All Keys

```bash
curl http://localhost:8000/auth/keys \
  -H "X-API-Key: fpx_your_key_here"

# Response:
[
  {
    "key_id": "a1b2c3d4",
    "name": "CI/CD Pipeline",
    "key_prefix": "fpx_6m7n8o9",
    "created_at": "2025-01-22T12:00:00",
    "last_used": "2025-01-22T14:30:00",
    "is_active": true
  },
  ...
]
```

#### Revoke API Key

```bash
# Disable a key (can be re-enabled by admin)
curl -X POST http://localhost:8000/auth/keys/{key_id}/revoke \
  -H "X-API-Key: fpx_your_key_here"
```

#### Delete API Key

```bash
# Permanently delete a key
curl -X DELETE http://localhost:8000/auth/keys/{key_id} \
  -H "X-API-Key: fpx_your_key_here"
```

### Python Example

```python
import requests

API_KEY = "fpx_6m7n8o9p0q1r2s3t4u5v6w7x8y9z0a1b2c3d4e5f"
headers = {"X-API-Key": API_KEY}

# Make authenticated request
response = requests.get(
    "http://localhost:8000/admin/status",
    headers=headers
)
print(response.json())

# Create new API key
new_key_response = requests.post(
    "http://localhost:8000/auth/keys",
    headers=headers,
    json={
        "name": "Production Monitor",
        "description": "Monitoring service key"
    }
)
new_key = new_key_response.json()
print(f"New API Key: {new_key['api_key']}")  # Save this!
```

### Storage

API keys are stored in `security/api_keys.db` (SQLite database).

- Keys are hashed using SHA-256
- Only the hash is stored (like passwords)
- Actual key shown only once during creation

### Pros & Cons

✅ **Pros:**
- No expiration (until revoked)
- Perfect for automation
- Easy to rotate
- Track usage per key
- Revoke individual keys

❌ **Cons:**
- Must be stored securely
- If leaked, valid until revoked
- No built-in expiration

---

## TLS/HTTPS Configuration

**⚠️ ALWAYS use HTTPS in production!**

### Option 1: Self-Signed Certificate (Development Only)

```bash
# Generate self-signed certificate
python ssl_config.py

# Set environment variables
export FASTPROXY_SSL_CERT=certs/cert.pem
export FASTPROXY_SSL_KEY=certs/key.pem

# Run with HTTPS
python main.py
# Server starts on https://localhost:8443
```

### Option 2: Let's Encrypt (Production)

```bash
# Install certbot
sudo apt-get install certbot

# Get certificate
sudo certbot certonly --standalone -d yourdomain.com

# Set environment variables
export FASTPROXY_SSL_CERT=/etc/letsencrypt/live/yourdomain.com/fullchain.pem
export FASTPROXY_SSL_KEY=/etc/letsencrypt/live/yourdomain.com/privkey.pem
export FASTPROXY_SSL_PORT=443

# Run with HTTPS
sudo python main.py
```

### Option 3: Reverse Proxy (Recommended)

Let Nginx/Traefik handle SSL termination:

```nginx
# nginx.conf
server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## Rate Limiting

### Global Rate Limiting

Configured in `config.yaml`:

```yaml
rate_limit:
  requests_per_minute: 100
```

### Admin Endpoint Rate Limiting

**Automatic** rate limiting on sensitive endpoints:

- **Limit:** 5 attempts per 5 minutes per IP
- **Applies to:**
  - `/auth/login`
  - `/auth/keys` (POST)
  - `/admin/reload`
  - `/admin/ratelimit/clear/{ip}`
  - `/audit/logs`

#### Example Response (Rate Limited)

```json
{
  "detail": "Too many attempts. Try again in 300 seconds."
}
```

HTTP Status: `429 Too Many Requests`  
Header: `Retry-After: 300`

---

## Security Best Practices

### 1. **Always Use HTTPS in Production** 🔒

```bash
# NEVER do this in production:
❌ http://api.example.com

# Always use HTTPS:
✅ https://api.example.com
```

### 2. **Use Strong Passwords**

```bash
# Bad
❌ FASTPROXY_ADMIN_PASSWORD=admin123

# Good
✅ FASTPROXY_ADMIN_PASSWORD=9k$mP2@vL8#qX4!rW
```

### 3. **Rotate Credentials Regularly**

- Change admin password every 90 days
- Rotate JWT secret every 6 months
- Rotate API keys annually

### 4. **Never Commit Secrets to Git**

```bash
# Add to .gitignore
.env
*.pem
*.key
security/api_keys.db
```

### 5. **Use Different Credentials Per Environment**

```bash
# Development
FASTPROXY_ADMIN_PASSWORD=dev_password

# Staging
FASTPROXY_ADMIN_PASSWORD=staging_secure_password

# Production
FASTPROXY_ADMIN_PASSWORD=prod_ultra_secure_password
```

### 6. **Monitor Authentication Failures**

Check audit logs for suspicious activity:

```bash
curl http://localhost:8000/audit/logs?event_type=admin_action \
  -H "X-API-Key: your_key"
```

### 7. **Revoke Compromised Keys Immediately**

```bash
# If API key is leaked:
curl -X POST http://localhost:8000/auth/keys/{key_id}/revoke \
  -H "X-API-Key: admin_key"

# Then create new key:
curl -X POST http://localhost:8000/auth/keys \
  -H "X-API-Key: admin_key" \
  -d '{"name": "Replacement Key"}'
```

### 8. **Use API Keys for Automation**

```bash
# CI/CD Pipeline
❌ Don't use admin credentials in scripts

✅ Use dedicated API keys with descriptive names
```

### 9. **Enable Logging for Security Events**

All authentication events are automatically logged:
- Login attempts (success/failure)
- API key usage
- Admin actions

### 10. **Restrict CORS Origins**

```bash
# Bad (allows any origin)
❌ FASTPROXY_CORS_ORIGINS=*

# Good (specific origins)
✅ FASTPROXY_CORS_ORIGINS=https://app.example.com,https://admin.example.com
```

---

## Quick Reference

### Environment Variables

```bash
# Authentication
FASTPROXY_ADMIN_USERNAME=admin
FASTPROXY_ADMIN_PASSWORD=secure_password
FASTPROXY_JWT_SECRET=jwt_secret_key

# SSL/TLS
FASTPROXY_SSL_CERT=/path/to/cert.pem
FASTPROXY_SSL_KEY=/path/to/key.pem
FASTPROXY_SSL_PORT=8443

# CORS
FASTPROXY_CORS_ORIGINS=https://example.com
```

### Endpoints

| Endpoint | Method | Auth Required | Purpose |
|----------|--------|---------------|---------|
| `/auth/login` | POST | Basic Auth | Get JWT tokens |
| `/auth/refresh` | POST | Refresh Token | Refresh access token |
| `/auth/keys` | GET | API Key/Basic | List API keys |
| `/auth/keys` | POST | API Key/Basic | Create API key |
| `/auth/keys/{id}/revoke` | POST | API Key/Basic | Revoke API key |
| `/auth/keys/{id}` | DELETE | API Key/Basic | Delete API key |
| `/admin/*` | * | Any | Admin endpoints |
| `/audit/*` | * | Any | Audit endpoints |

---

## Troubleshooting

### "Invalid credentials"

- Check username/password in `.env`
- Ensure Basic Auth header is correct
- Check for typos in credentials

### "Invalid or revoked API key"

- Verify key starts with `fpx_`
- Check if key was revoked
- Confirm key exists: `GET /auth/keys`

### "Could not validate credentials" (JWT)

- Token expired (refresh it)
- Wrong token type (access vs refresh)
- Invalid JWT secret

### "Too many attempts"

- Rate limit exceeded
- Wait 5 minutes and try again
- Contact admin to clear rate limit

---

## Need Help?

- **Documentation:** `/docs/`
- **Security Roadmap:** `/docs/SECURITY_ROADMAP.md`
- **Architecture:** `/docs/ARCHITECTURE.md`
- **GitHub Issues:** https://github.com/deepskilling/fastproxy/issues

---

**Last Updated:** 2025-01-22  
**FastProxy Version:** 1.0.0

