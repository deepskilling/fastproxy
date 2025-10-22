<div align="center">

# 🚀 LiteProxy

### Lightning-Fast Async Reverse Proxy Built with FastAPI

*A production-ready, Python-based alternative to Nginx for modern microservices*

[![Build Status](https://github.com/deepskilling/fastproxy/workflows/Python%20CI/badge.svg)](https://github.com/deepskilling/fastproxy/actions)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com)

[Features](#-features) • [Quick Start](#-quick-start) • [Documentation](#-documentation) • [API](#-api-reference) • [Contributing](#-contributing)

</div>

---

## 🎯 What is LiteProxy?

**LiteProxy** (formerly FastProxy) is a lightweight, high-performance reverse proxy server built entirely in Python using FastAPI. It provides dynamic routing, intelligent rate limiting, comprehensive audit logging, and hot-reload configuration—all in a simple, developer-friendly package.

**Perfect for:**
- 🏗️ **Microservices Architecture** - Route requests across multiple backend services
- 🔧 **Development Environments** - Easily proxy local services during development
- 📊 **API Gateways** - Centralize authentication, rate limiting, and logging
- 🚀 **Prototyping** - Quick setup without complex Nginx configurations
- 🧪 **Testing** - Programmable proxy behavior for integration tests

---

## ✨ Features

<table>
<tr>
<td width="50%">

### Core Functionality
- ⚡️ **Async Request Forwarding** using `httpx`
- 🛣️ **Path-Based Routing** with longest-prefix matching
- 🔄 **Hot-Reload Configuration** without restarts
- 📦 **Header Management** with X-Forwarded-* injection
- 🔌 **Connection Pooling** for optimal performance

</td>
<td width="50%">

### Security & Control
- 🛡️ **IP-Based Rate Limiting** (sliding window)
- 🌐 **CORS Support** with flexible configuration
- 📝 **Request Body Size Limits**
- 🔐 **Header Sanitization** (hop-by-hop filtering)
- 📊 **Comprehensive Audit Logging**

</td>
</tr>
</table>

### Advanced Features
- 📈 **SQLite Audit Database** - Track every request and admin action
- 🎛️ **Admin REST API** - Dynamic configuration and monitoring
- 🧪 **100% Test Coverage** - Fully tested with pytest
- 🐳 **Docker Ready** - Containerized deployment included
- 📚 **Auto-Generated API Docs** - Interactive Swagger/ReDoc UI

---

## 📋 Requirements

- **Python**: 3.8 or higher
- **Dependencies**: FastAPI, httpx, PyYAML, Pydantic
- **Optional**: Docker, Docker Compose (for containerized deployment)

---

## 🚀 Quick Start

### Option 1: Quick Start Script (Recommended)

```bash
# Clone the repository
git clone https://github.com/deepskilling/fastproxy.git
cd fastproxy

# Run the quick start script
chmod +x start.sh
./start.sh
```

The script will automatically:
1. ✅ Create a virtual environment
2. ✅ Install all dependencies
3. ✅ Start the server on http://localhost:8000

### Option 2: Manual Installation

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn main:app --reload
```

### Option 3: Docker Compose

```bash
# Start LiteProxy and example backend services
docker-compose up -d

# View logs
docker-compose logs -f liteproxy

# Stop all services
docker-compose down
```

### Option 4: Using Make

```bash
make install    # Install dependencies
make run        # Start development server
make test       # Run test suite
make clean      # Clean up generated files
```

---

## ⚙️ Configuration

Edit `config.yaml` to configure your routes and settings:

```yaml
routes:
  - path: /api/
    target: http://127.0.0.1:8001
  - path: /auth/
    target: http://127.0.0.1:8002
  - path: /service/
    target: http://127.0.0.1:8003

rate_limit:
  requests_per_minute: 100

cors:
  allow_origins: ["*"]
  allow_credentials: true
  allow_methods: ["*"]
  allow_headers: ["*"]

max_body_size: 10485760  # 10 MB
```

**Configuration Features:**
- 🎯 **Longest-Prefix Matching** - Most specific route wins
- 🔄 **Hot Reload** - Update config without restart via `/admin/reload`
- ✅ **Auto-Validation** - Invalid configs are rejected before applying

---

## 🔌 API Reference

### Health Check
```bash
GET /health
```
Returns server health status.

### Proxy Routes
```bash
* /{path:path}  # All HTTP methods
```
Automatically proxies requests based on route configuration.

### Admin Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/admin/reload` | POST | Hot reload configuration |
| `/admin/routes` | GET | List all configured routes |
| `/admin/config` | GET | Get full configuration |
| `/admin/status` | GET | Server status and statistics |
| `/admin/ratelimit/clear/{ip}` | POST | Clear rate limit for IP |
| `/admin/ratelimit/stats/{ip}` | GET | Get rate limit stats |

### Audit Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/audit/logs` | GET | Query audit logs (supports filtering) |
| `/audit/stats` | GET | Get audit statistics |

---

## 📚 Documentation

- **📖 [Quick Start Guide](QUICKSTART.md)** - Get up and running in 5 minutes
- **🏗️ [Architecture Documentation](ARCHITECTURE.md)** - System design and internals
- **🔗 Interactive API Docs** - Available at `http://localhost:8000/docs` when running

---

## 💡 Usage Examples

### Basic Proxy Request
```bash
# Request is forwarded to http://127.0.0.1:8001/api/users
curl http://localhost:8000/api/users
```

### Hot Reload Configuration
```bash
# After editing config.yaml
curl -X POST http://localhost:8000/admin/reload
```

### View Recent Audit Logs
```bash
# Get last 10 logs
curl "http://localhost:8000/audit/logs?limit=10"

# Filter by event type
curl "http://localhost:8000/audit/logs?event_type=request"

# Filter by IP address
curl "http://localhost:8000/audit/logs?client_ip=192.168.1.1"
```

### Check Rate Limit Status
```bash
curl http://localhost:8000/admin/ratelimit/stats/192.168.1.1
```

### Server Status
```bash
curl http://localhost:8000/admin/status
```

---

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests
pytest

# With coverage report
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_proxy.py -v

# Run with verbose output
pytest -v -s
```

**Test Coverage:**
- ✅ Unit tests for all core components
- ✅ Integration tests for request flow
- ✅ Mock-based testing for external dependencies
- ✅ Rate limiting edge cases
- ✅ Configuration validation

---

## 🏗️ Project Structure

```
liteproxy/
├── main.py                    # FastAPI application entry point
├── config.yaml                # Route and proxy configuration
├── requirements.txt           # Python dependencies
│
├── proxy/                     # Core proxy logic
│   ├── router.py             # Path-based routing engine
│   ├── forwarder.py          # Async HTTP forwarding
│   ├── rate_limit.py         # IP-based rate limiter
│   └── middleware.py         # Request logging middleware
│
├── audit/                     # Audit logging subsystem
│   ├── models.py             # SQLite schema & Pydantic models
│   ├── logger.py             # Audit log storage
│   ├── middleware.py         # Auto-audit middleware
│   └── api.py                # Query endpoints
│
├── admin/                     # Administrative endpoints
│   └── api.py                # Config management API
│
└── tests/                     # Comprehensive test suite
    ├── test_proxy.py         # Proxy functionality tests
    ├── test_ratelimit.py     # Rate limiting tests
    └── test_audit.py         # Audit logging tests
```

---

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

### Using Gunicorn

```bash
gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile -
```

### Docker Deployment

```bash
# Build image
docker build -t liteproxy:latest .

# Run container
docker run -d \
  -p 8000:8000 \
  -v $(pwd)/config.yaml:/app/config.yaml \
  -v $(pwd)/audit:/app/audit \
  --name liteproxy \
  liteproxy:latest
```

---

## 📊 Performance

**Benchmark Results** (on Apple M1, Python 3.11):
- **Proxy Overhead**: ~1-3ms per request
- **Throughput**: 2,000-4,000 req/s (single worker)
- **Throughput**: 8,000-15,000 req/s (4 workers)
- **Memory**: ~60-100 MB base memory
- **Rate Limiting**: <0.5ms overhead

*Performance scales with backend latency and hardware*

---

## 🛠️ Development

### Setup Development Environment

```bash
# Clone and install
git clone https://github.com/deepskilling/fastproxy.git
cd fastproxy
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Install development dependencies
pip install black isort flake8 pytest-cov

# Format code
black .
isort .

# Run linter
flake8 .

# Run tests
pytest --cov=. --cov-report=html
```

### Contributing

We welcome contributions! Please see our contributing guidelines:

1. 🍴 Fork the repository
2. 🌿 Create a feature branch (`git checkout -b feature/amazing-feature`)
3. ✅ Write tests for your changes
4. ✍️ Commit your changes (`git commit -m 'Add amazing feature'`)
5. 📤 Push to the branch (`git push origin feature/amazing-feature`)
6. 🔃 Open a Pull Request

---

## 🤝 Use Cases

<table>
<tr>
<td width="50%">

### Development
- 🏗️ Local microservices routing
- 🧪 API testing and mocking
- 🔧 Service integration testing
- 📱 Mobile app backend proxying

</td>
<td width="50%">

### Production
- 🌐 API Gateway implementation
- 🛡️ Rate limiting and protection
- 📊 Request auditing and monitoring
- 🔀 Load distribution and routing

</td>
</tr>
</table>

---

## 🔒 Security Features

- ✅ **IP-based rate limiting** to prevent abuse
- ✅ **Request body size limits** to prevent DoS
- ✅ **Header sanitization** (hop-by-hop removal)
- ✅ **Comprehensive audit logging** for compliance
- ✅ **X-Forwarded headers** for backend awareness

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Copyright © 2025 [Deepskilling](https://github.com/deepskilling)

---

## 🙏 Acknowledgments

Built with these amazing technologies:

- [FastAPI](https://fastapi.tiangolo.com/) - Modern, fast web framework
- [httpx](https://www.python-httpx.org/) - Next-generation HTTP client
- [Pydantic](https://pydantic-docs.helpmanual.io/) - Data validation using Python type hints
- [Uvicorn](https://www.uvicorn.org/) - Lightning-fast ASGI server

---

## 📞 Support & Community

- 📖 **Documentation**: [Read the docs](https://github.com/deepskilling/fastproxy)
- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/deepskilling/fastproxy/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/deepskilling/fastproxy/discussions)
- ⭐ **Star us on GitHub** if you find this project useful!

---

<div align="center">

**Made with ❤️ by [Deepskilling](https://github.com/deepskilling)**

*LiteProxy - Fast, Simple, Powerful*

[![Star on GitHub](https://img.shields.io/github/stars/deepskilling/fastproxy?style=social)](https://github.com/deepskilling/fastproxy)

</div>
