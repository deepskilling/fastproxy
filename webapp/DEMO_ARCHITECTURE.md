# 🏗️ Demo Architecture

## Overview

The FastProxy demo showcases a complete reverse proxy setup with a modern management interface.

## Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                         Client Browser                            │
│                     http://localhost:8000                          │
└─────────────────────────┬────────────────────────────────────────┘
                          │
                          │ All traffic flows through FastProxy
                          │
                          ▼
       ┌──────────────────────────────────────────────────┐
       │              FastProxy (Port 8000)                │
       │                                                   │
       │  • Reverse Proxy                                 │
       │  • Route Matching                                │
       │  • Rate Limiting                                 │
       │  • CORS Handling                                 │
       │  • SSL/TLS (optional)                            │
       │  • Authentication                                │
       │  • Audit Logging                                 │
       └──────────┬─────────────────────────┬─────────────┘
                  │                         │
        ┌─────────┴─────────┐    ┌─────────┴─────────────┐
        │                   │    │                        │
        │ Route: /api/*     │    │ Route: /*              │
        │                   │    │                        │
        ▼                   │    ▼                        │
┌────────────────┐          │  ┌──────────────────────┐  │
│  Backend API   │          │  │   Frontend UI         │  │
│  (Port 8001)   │          │  │   (Port 3000)         │  │
│                │          │  │                       │  │
│  FastAPI       │◄─────────┘  │   Next.js             │◄─┘
│  • REST API    │             │   • React 18          │
│  • Config Mgmt │             │   • TypeScript        │
│  • Route CRUD  │             │   • Tailwind CSS      │
│  • API Keys    │             │   • SWR data fetch    │
│  • Statistics  │             │                       │
│  • Logs        │             │   Pages:              │
│                │             │   • Dashboard         │
└────────┬───────┘             │   • Routes            │
         │                     │   • API Keys          │
         │                     │   • Config            │
         │                     │   • Logs              │
         │                     │                       │
         │                     └───────────┬───────────┘
         │                                 │
         │                                 │
         │     ┌──────────────────────────┐│
         │     │   Makes API calls to:    ││
         │     │   /api/routes            ││
         │     │   /api/config            ││
         │     │   /api/keys              ││
         │     │   /api/stats             ││
         │     │   /api/logs              ││
         │     └──────────────────────────┘│
         │                                  │
         │                                  │
         └──────────────────────────────────┘
                        │
                        ▼
              ┌─────────────────┐
              │  config.yaml    │
              │  (FastProxy     │
              │   Config File)  │
              └─────────────────┘
```

## Request Flow

### 1. User Requests Dashboard
```
Browser → http://localhost:8000/
    ↓
FastProxy (matches route: /)
    ↓
Forward to: http://localhost:3000/
    ↓
Next.js Frontend renders Dashboard
    ↓
Returns HTML/CSS/JS to browser
```

### 2. Dashboard Makes API Call
```
Browser executes: fetch('/api/stats')
    ↓
Request to: http://localhost:8000/api/stats
    ↓
FastProxy (matches route: /api)
    ↓
Forward to: http://localhost:8001/api/stats
    ↓
Backend API queries data
    ↓
Returns JSON: {total_requests: 100, ...}
    ↓
FastProxy returns to Frontend
    ↓
Frontend updates UI
```

### 3. User Adds a New Route
```
User fills form in Frontend
    ↓
Frontend: POST /api/routes
    ↓
FastProxy forwards to Backend
    ↓
Backend updates config.yaml
    ↓
Success response to Frontend
    ↓
Frontend shows success message
    ↓
User can now use the new route!
```

## Components

### FastProxy (Port 8000)
**Purpose**: Central reverse proxy that routes all traffic

**Key Features**:
- Path-based routing (`/api/*` vs `/*`)
- Rate limiting (100 requests/min default)
- CORS middleware
- Authentication (JWT, API Keys)
- Audit logging
- Health monitoring

**Configuration**: `config.yaml` or `config.demo.yaml`

### Backend API (Port 8001)
**Purpose**: Management REST API for controlling FastProxy

**Technology**: FastAPI + Python
- Pydantic models for validation
- Async endpoints
- OpenAPI documentation
- JWT authentication

**Endpoints**:
- `/api/health` - Health check
- `/api/config` - Get/update configuration
- `/api/routes` - CRUD for routes
- `/api/keys` - API key management
- `/api/stats` - Statistics
- `/api/logs` - Log retrieval

### Frontend UI (Port 3000)
**Purpose**: Beautiful web interface for managing FastProxy

**Technology**: Next.js 14 + React + TypeScript
- App Router (Next.js 14)
- Tailwind CSS for styling
- Lucide icons
- Axios for HTTP
- SWR for data fetching

**Pages**:
- `/` - Dashboard with stats
- `/routes` - Route management
- `/api-keys` - API key management
- `/config` - Configuration editor
- `/logs` - Log viewer

## Data Flow

```
┌─────────────┐
│ config.yaml │ ← Source of truth for routing
└──────┬──────┘
       │
       │ Read on startup & hot-reload
       │
       ▼
┌──────────────┐
│  FastProxy   │ ← Active routing configuration
└──────┬───────┘
       │
       │ Backend can update via API
       │
       ▼
┌──────────────┐
│ Backend API  │ ← Reads/writes config.yaml
└──────┬───────┘
       │
       │ Frontend makes API calls
       │
       ▼
┌──────────────┐
│ Frontend UI  │ ← User interacts here
└──────────────┘
```

## Security Flow

```
User Request
    ↓
FastProxy receives request
    ↓
Check rate limit (IP-based)
    ↓
Check authentication (if required)
    ↓
Validate target URL (SSRF protection)
    ↓
Forward to backend
    ↓
Log request (audit trail)
    ↓
Return response
```

## Deployment Models

### Demo Mode (All on one machine)
```
localhost:8000 → FastProxy
localhost:8001 → Backend API  
localhost:3000 → Frontend UI
```

### Production Mode (Distributed)
```
yourdomain.com:443 → FastProxy (with HTTPS)
    ├→ /api → internal-api.local:8001
    └→ / → internal-frontend.local:3000
```

### Docker Mode
```
Container: fastproxy (8000)
Container: backend (8001)
Container: frontend (3000)
Network: fastproxy-net (internal)
```

## Why This Architecture?

### 1. **Single Entry Point**
All traffic goes through FastProxy on port 8000. This provides:
- Centralized access control
- Unified logging
- Easy SSL/TLS termination
- Rate limiting at the edge

### 2. **Service Isolation**
Backend and Frontend are separate services:
- Independent scaling
- Technology agnostic
- Clear separation of concerns
- Easy to replace/update

### 3. **API-First Design**
Backend provides REST API:
- Can be used by any client
- Not tied to web UI
- Easy to automate
- Can build mobile apps

### 4. **Developer Friendly**
- Hot reload on code changes
- Clear separation of concerns
- Modern tech stack
- Great developer experience

## Performance Characteristics

### Latency
```
Client → FastProxy: ~1ms
FastProxy → Backend/Frontend: ~1-5ms
Total added latency: ~2-10ms
```

### Throughput
- **Rate Limit**: 100 req/min (configurable)
- **Concurrent Connections**: 200 (configurable)
- **Keep-Alive**: Enabled for efficiency

### Scaling
- **Horizontal**: Deploy multiple FastProxy instances behind load balancer
- **Vertical**: Increase worker count (uvicorn workers)
- **Backend**: Scale API servers independently
- **Frontend**: Static build can be CDN-hosted

## Configuration Management

### File: config.yaml
```yaml
routes:
  - path: /api
    target: http://backend:8001
  - path: /
    target: http://frontend:3000

rate_limit:
  requests_per_minute: 100

cors:
  allow_origins: ["*"]
```

### Hot Reload
```
1. User updates config via UI
2. Frontend → POST /api/config
3. Backend writes config.yaml
4. Backend → POST /admin/reload (FastProxy)
5. FastProxy reloads routes
6. New config active immediately
```

## Monitoring

### Health Checks
- FastProxy: `GET /health`
- Backend: `GET /api/health`
- Frontend: `GET /` (HTTP 200)

### Metrics
- Request count
- Response times
- Error rates
- Rate limit hits
- Active connections

### Logs
- Access logs (all requests)
- Error logs (failures)
- Audit logs (admin actions)
- Application logs (debug info)

## Next Steps

To use this architecture in production:

1. **SSL/TLS**: Enable `auto_https` in config
2. **Authentication**: Configure JWT secrets
3. **Database**: Use PostgreSQL for audit logs
4. **Monitoring**: Add Prometheus metrics
5. **Scaling**: Deploy behind load balancer
6. **Backup**: Automate config backups

See [QUICKSTART.md](../QUICKSTART.md) for getting started!

