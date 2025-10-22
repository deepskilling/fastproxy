#cursor:generate
# Task: Generate full codebase for a FastAPI-based Nginx-lite reverse proxy MVP
# Goal: Implement async reverse proxy server with config-driven routing, rate limiting, and audit logging.
# Output: Create all files and folders as described below, ensuring modular, readable, and production-ready code.

---

# 🧱 FastAPI Reverse Proxy - MVP Specification

## 🎯 Objective
Build a **FastAPI-based reverse proxy (Nginx-lite)** that supports async request forwarding, dynamic routing, rate limiting, audit logging, and simple configuration reloads — production-ready but minimal.

---

## 📂 Project Structure (MVP)
```
fastproxy/
│
├── main.py                     # FastAPI entrypoint
├── config.yaml                 # Routing and settings file
│
├── proxy/                      # Core proxy logic
│   ├── router.py               # Path-based routing & config parsing
│   ├── forwarder.py            # HTTPX async request forwarding
│   ├── rate_limit.py           # Basic IP-based rate limiter
│   ├── middleware.py           # Logging, headers, and request hooks
│   └── __init__.py
│
├── audit/                      # Audit logging subsystem
│   ├── models.py               # SQLite schema for audit entries
│   ├── logger.py               # Record admin actions & requests
│   ├── middleware.py           # Intercepts config reloads / admin events
│   ├── api.py                  # Endpoint to query recent audit events
│   └── audit.db                # SQLite database for persistent logs
│
├── admin/                      # Minimal admin endpoints
│   ├── api.py                  # /admin/reload, /admin/routes
│   └── __init__.py
│
└── tests/
    ├── test_proxy.py
    ├── test_ratelimit.py
    └── test_audit.py
```

---

## ✅ MVP Feature Checklist

### 1. Core Proxy Functionality
- [x] **Async HTTP Forwarding** using `httpx.AsyncClient`
- [x] **Path-based Routing** via config file
- [x] **Header & Query Forwarding**
- [x] **Response Relay** with original status and headers
- [x] **Config File Loading (YAML/JSON)**

### 2. Security & Access Control
- [x] **Rate Limiting** (simple IP-based, per minute)
- [x] **CORS Handling**
- [x] **Request Body Size Limit**
- [ ] **Basic Auth for Admin Endpoints (optional)**

### 3. Observability & Logging
- [x] **Access Logging** (method, path, latency)
- [x] **Error Logging**
- [x] **Metrics Hook Placeholder (Prometheus-ready)**

### 4. Configuration Management
- [x] **Hot Reload Config Endpoint `/admin/reload`**
- [x] **List Current Routes `/admin/routes`**
- [x] **Validation Before Applying Config**

### 5. Audit Logging
- [x] **Request Audit Log (IP, path, status, time)**
- [x] **Admin Action Log (reload, config change)**
- [x] **SQLite Storage Backend**
- [x] **API to Query Recent Logs**

### 6. Developer Experience
- [x] **Single Command Startup (`uvicorn main:app --reload`)**
- [x] **Environment-based Configuration**
- [x] **Unit Tests for Proxy, Rate Limit, Audit**

---

## ⚙️ Example `config.yaml`
```yaml
routes:
  - path: /api/
    target: http://127.0.0.1:8001
  - path: /auth/
    target: http://127.0.0.1:8002

rate_limit:
  requests_per_minute: 100

cors:
  allow_origins: ["*"]
```

---

## 🧠 Notes for Code Generation
- Use **FastAPI** and **httpx** for async forwarding.
- Use **SQLite** (via `sqlite3` or `sqlmodel`) for audit logs.
- Keep code modular and under 200–250 lines where possible.
- Implement reusable **middlewares** for logging, audit, and rate limiting.
- Avoid external dependencies except `fastapi`, `httpx`, `pydantic`, `pyyaml`.
- Include minimal **unit tests** that confirm forwarding, rate limiting, and audit logging.

---

## 🏁 Deliverable
A runnable FastAPI reverse proxy MVP that:
- Loads routes from `config.yaml`
- Forwards requests asynchronously
- Logs requests, rate limits, and admin actions
- Supports dynamic reload and audit logging
