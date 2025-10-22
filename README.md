# 🚀 FastProxy - FastAPI-Based Reverse Proxy

A production-ready, async reverse proxy server built with FastAPI. Think of it as a lightweight, Python-based alternative to Nginx, with dynamic configuration, rate limiting, and comprehensive audit logging.

## ✨ Features

- **🔄 Async Request Forwarding**: High-performance async HTTP forwarding using `httpx`
- **🛣️ Dynamic Routing**: Path-based routing with hot-reload configuration
- **⚡ Rate Limiting**: IP-based rate limiting with sliding window algorithm
- **📊 Audit Logging**: SQLite-based audit logs for all requests and admin actions
- **🔧 Admin API**: REST endpoints for configuration management
- **🎯 CORS Support**: Built-in CORS handling
- **📝 Request Logging**: Comprehensive access and error logging
- **🧪 Well-Tested**: Unit tests for all core functionality

## 📋 Requirements

- Python 3.8+
- FastAPI
- httpx
- PyYAML
- Pydantic

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
cd fastproxy

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Edit `config.yaml` to configure your routes:

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

### Running the Server

```bash
# Development mode with auto-reload
uvicorn main:app --reload

# Production mode
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

The server will start on `http://localhost:8000`

## 📚 API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔌 Endpoints

### Proxy Endpoints
- `/*` - All paths are proxied based on route configuration

### Health Check
- `GET /health` - Health check endpoint

### Admin Endpoints
- `POST /admin/reload` - Hot reload configuration
- `GET /admin/routes` - List all configured routes
- `GET /admin/config` - Get full configuration
- `GET /admin/status` - Get server status and statistics
- `POST /admin/ratelimit/clear/{ip}` - Clear rate limit for an IP
- `GET /admin/ratelimit/stats/{ip}` - Get rate limit stats for an IP

### Audit Endpoints
- `GET /audit/logs` - Query audit logs with filtering
  - Query params: `limit`, `offset`, `event_type`, `client_ip`
- `GET /audit/stats` - Get audit log statistics

## 🎯 Usage Examples

### Basic Proxy Request
```bash
# Request to /api/users will be forwarded to http://127.0.0.1:8001/api/users
curl http://localhost:8000/api/users
```

### Reload Configuration
```bash
curl -X POST http://localhost:8000/admin/reload
```

### View Audit Logs
```bash
# Get recent audit logs
curl "http://localhost:8000/audit/logs?limit=10"

# Filter by event type
curl "http://localhost:8000/audit/logs?event_type=request"

# Filter by IP
curl "http://localhost:8000/audit/logs?client_ip=192.168.1.1"
```

### Check Rate Limit Stats
```bash
curl http://localhost:8000/admin/ratelimit/stats/192.168.1.1
```

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_proxy.py

# Run with verbose output
pytest -v
```

## 📂 Project Structure

```
fastproxy/
│
├── main.py                     # FastAPI entrypoint
├── config.yaml                 # Routing and settings
├── requirements.txt            # Python dependencies
│
├── proxy/                      # Core proxy logic
│   ├── router.py               # Path-based routing
│   ├── forwarder.py            # Async request forwarding
│   ├── rate_limit.py           # IP-based rate limiter
│   ├── middleware.py           # Request logging middleware
│   └── __init__.py
│
├── audit/                      # Audit logging
│   ├── models.py               # SQLite schema
│   ├── logger.py               # Audit logger
│   ├── middleware.py           # Audit middleware
│   ├── api.py                  # Audit API endpoints
│   └── audit.db                # SQLite database (generated)
│
├── admin/                      # Admin endpoints
│   ├── api.py                  # Admin API
│   └── __init__.py
│
└── tests/
    ├── test_proxy.py           # Proxy tests
    ├── test_ratelimit.py       # Rate limit tests
    └── test_audit.py           # Audit tests
```

## 🔧 Configuration Options

### Routes
Define path-based routing rules:

```yaml
routes:
  - path: /api/          # Path prefix to match
    target: http://backend:8001  # Target backend URL
```

Routes use **longest prefix matching** - the most specific route wins.

### Rate Limiting
Configure IP-based rate limiting:

```yaml
rate_limit:
  requests_per_minute: 100  # Max requests per IP per minute
```

### CORS
Configure Cross-Origin Resource Sharing:

```yaml
cors:
  allow_origins: ["*"]
  allow_credentials: true
  allow_methods: ["*"]
  allow_headers: ["*"]
```

## 🔒 Security Features

- **Rate Limiting**: Prevents abuse with per-IP rate limits
- **Request Body Size Limits**: Configurable max body size
- **Audit Logging**: All requests and admin actions are logged
- **Header Sanitization**: Hop-by-hop headers are properly filtered

## 📊 Monitoring

### Logs
Application logs are written to stdout with the format:
```
TIMESTAMP - MODULE - LEVEL - MESSAGE
```

### Metrics
Each response includes custom headers:
- `X-Process-Time`: Request processing time in milliseconds
- `X-Proxy-By`: Always set to "FastProxy"

### Audit Database
All requests are stored in `audit/audit.db` with:
- Timestamp
- Client IP
- Method and path
- Status code
- Duration
- User agent

## 🎯 Use Cases

- **API Gateway**: Route requests to multiple microservices
- **Load Balancer**: Distribute traffic across backend servers
- **Rate Limiting**: Protect backends from abuse
- **Audit Trail**: Track all API usage
- **Development Proxy**: Local development with multiple services

## 🚀 Production Deployment

### Using Uvicorn with Multiple Workers

```bash
uvicorn main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4 \
  --access-log \
  --log-level info
```

### Using Gunicorn with Uvicorn Workers

```bash
gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile -
```

### Environment Variables

```bash
# Example environment configuration
export FASTPROXY_CONFIG=config.yaml
export FASTPROXY_LOG_LEVEL=INFO
export FASTPROXY_WORKERS=4
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

MIT License - feel free to use this project for any purpose.

## 🙏 Acknowledgments

Built with:
- [FastAPI](https://fastapi.tiangolo.com/) - Modern, fast web framework
- [httpx](https://www.python-httpx.org/) - Async HTTP client
- [Pydantic](https://pydantic-docs.helpmanual.io/) - Data validation
- [Uvicorn](https://www.uvicorn.org/) - ASGI server

## 📞 Support

For issues, questions, or contributions, please open an issue on the repository.

---

**FastProxy** - A lightweight, Python-based reverse proxy for modern applications. 🚀

