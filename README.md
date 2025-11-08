# 🚀 FastProxy

**Lightning-Fast Async Reverse Proxy Built with FastAPI**

[![Build Status](https://github.com/deepskilling/fastproxy/workflows/Python%20CI/badge.svg)](https://github.com/deepskilling/fastproxy/actions)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com)

A production-ready, Python-based reverse proxy alternative to Nginx for modern microservices.

**✨ NEW**: Now includes a complete **Management WebApp** with a beautiful Next.js UI! See it in action with our [Quick Demo →](#-try-the-demo)

## ✨ Features

### Core Proxy Features
- ⚡️ **Async Request Forwarding** using httpx
- 🛣️ **Path-Based Routing** with hot-reload configuration
- 🔄 **Automatic HTTPS** with Let's Encrypt integration
- 🛡️ **IP-Based Rate Limiting** with sliding window algorithm
- 🔐 **Authentication & Authorization** (JWT, API Keys, Basic Auth)
- 🚫 **SSRF Protection** with URL validation
- 📊 **SQLite Audit Logging** for all requests and admin actions
- 🌐 **Secure CORS Configuration**
- 🔒 **Security Headers** and request body size limits
- 🐳 **Docker Ready** with docker-compose support

### 🎨 Management WebApp (NEW!)
- 📱 **Beautiful Web UI** - Modern Next.js + React interface
- 📊 **Real-Time Dashboard** - Monitor health, stats, and metrics
- 🛣️ **Route Management** - Add, edit, delete routes visually
- 🔑 **API Key Management** - Generate and manage authentication keys
- ⚙️ **Configuration Editor** - Edit FastProxy config in the browser
- 📝 **Log Viewer** - View and filter logs with auto-refresh
- 🎯 **One-Command Demo** - Get started in under 2 minutes!

## 🎯 Try the Demo

Experience FastProxy with the full management UI in under 2 minutes:

```bash
# Clone the repository
git clone https://github.com/deepskilling/fastproxy.git
cd fastproxy

# Start everything (FastProxy + Management UI)
./start-demo.sh

# Open your browser to http://localhost:8000
```

That's it! You now have:
- ✅ FastProxy running on port 8000
- ✅ Management API on port 8001  
- ✅ Beautiful Web UI accessible through FastProxy
- ✅ Interactive dashboard to manage routes, keys, and config

**📖 For detailed instructions, see [QUICKSTART.md](QUICKSTART.md)**

## 🚀 Production Quick Start

For production deployment without the demo UI:

```bash
# Install dependencies
pip install -r requirements.txt

# Configure your routes
nano config.yaml

# Start the proxy
python main.py
```

## 📚 Documentation

### Getting Started
- **[🎯 QUICKSTART.md](QUICKSTART.md)** - **Start here!** Demo setup in 2 minutes
- **[📱 Management WebApp](webapp/README.md)** - Web UI documentation
- **[⚙️ Configuration Guide](docs/QUICKSTART.md)** - Detailed configuration

### Advanced Topics
- **[🏗️ Architecture](docs/ARCHITECTURE.md)** - System design and internals
- **[🔒 Auto SSL Setup](docs/AUTO_SSL_SETUP.md)** - Let's Encrypt HTTPS
- **[🛡️ Security Features](SECURITY_FEATURES_IMPLEMENTED.md)** - Security guide
- **[🤝 Contributing](docs/CONTRIBUTING.md)** - Development guidelines

### API Documentation
- **[Backend API Docs](http://localhost:8001/docs)** - Management API (when running)
- **[FastProxy Admin API](http://localhost:8000/admin/routes)** - Proxy admin endpoints

## 🐳 Docker Deployment

### Quick Docker Start

```bash
# Start demo stack (FastProxy + Management UI)
cd docker
./docker-start.sh

# Or using docker-compose
docker compose -f docker-compose.demo.yml up -d

# Or using make
make demo
```

Access at: **http://localhost:8000**

### Docker Features

- ✅ **Multi-stage builds** for optimized images
- ✅ **Health checks** for all services
- ✅ **Persistent volumes** for data storage
- ✅ **Bridge networking** for service communication
- ✅ **Interactive startup** script
- ✅ **Make commands** for easy management
- ✅ **Production-ready** configurations

**📚 Full Docker documentation**: [docker/README.md](docker/README.md)

## 📁 Project Structure

```
fastproxy/
├── main.py                 # FastProxy entry point
├── config.yaml             # Production configuration
├── config.demo.yaml        # Demo configuration
├── start-demo.sh          # One-command demo startup
├── QUICKSTART.md          # Quick start guide ⭐
│
├── proxy/                 # Core proxy logic
├── audit/                 # Audit logging
├── admin/                 # Admin API
├── security/              # Authentication & security
├── cert_manager/          # Automatic HTTPS/SSL
├── tests/                 # Test suite
│
├── webapp/                # Management WebApp ⭐ NEW
│   ├── README.md          # WebApp documentation
│   ├── backend/           # FastAPI management API
│   │   ├── main.py
│   │   └── requirements.txt
│   └── frontend/          # Next.js React UI
│       ├── app/           # Pages (dashboard, routes, etc.)
│       ├── components/    # React components
│       ├── lib/           # API client
│       └── package.json
│
├── docs/                  # Documentation
└── docker/                # Docker configuration
```

## 🔒 Security

FastProxy includes enterprise-grade security features:

- ✅ HTTP Basic Authentication for admin/audit endpoints
- ✅ SSRF protection with URL validation
- ✅ Secure CORS configuration
- ✅ Request body size limits (DoS protection)
- ✅ Security headers (CSP, HSTS, X-Frame-Options, etc.)
- ✅ Input validation and sanitization
- ✅ Information disclosure prevention

**Security Score**: 8.5/10 ✅ GOOD

## 📊 API Endpoints

### Proxy
- `/*` - All paths proxied based on configuration

### Health
- `GET /health` - Health check endpoint

### Admin (Requires Authentication)
- `POST /admin/reload` - Hot reload configuration
- `GET /admin/routes` - List configured routes
- `GET /admin/status` - Server status and statistics

### Audit (Requires Authentication)
- `GET /audit/logs` - Query audit logs
- `GET /audit/stats` - Audit statistics

## ⚙️ Configuration

Edit `config.yaml`:

```yaml
routes:
  - path: /api/
    target: http://127.0.0.1:8001

rate_limit:
  requests_per_minute: 100

cors:
  allow_origins: ["*"]
```

Set environment variables in `.env`:

```bash
FASTPROXY_ADMIN_USERNAME=admin
FASTPROXY_ADMIN_PASSWORD=your_secure_password
FASTPROXY_CORS_ORIGINS=https://yourdomain.com
```

## 🧪 Testing

```bash
# Run all tests
pytest

# With coverage
pytest --cov=. --cov-report=html

# Specific tests
pytest tests/test_proxy.py -v
```

## 📝 License

MIT License - Copyright © 2025 [Deepskilling](https://github.com/deepskilling)

See [LICENSE](LICENSE) for details.

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines.

## 🎬 Demo Screenshots

The Management WebApp provides a beautiful interface to control FastProxy:

- **Dashboard**: Real-time monitoring with health status and metrics
- **Routes**: Visual route configuration with add/edit/delete
- **API Keys**: Secure key generation with permissions
- **Config**: In-browser configuration editor
- **Logs**: Live log viewer with filtering

*See [webapp/README.md](webapp/README.md) for detailed screenshots and features*

## 📞 Support

- **Quick Start**: [QUICKSTART.md](QUICKSTART.md) - Start here!
- **WebApp Guide**: [webapp/README.md](webapp/README.md)
- **Documentation**: [docs/README.md](docs/README.md)
- **Issues**: [GitHub Issues](https://github.com/deepskilling/fastproxy/issues)
- **Discussions**: [GitHub Discussions](https://github.com/deepskilling/fastproxy/discussions)

---

**Made with ❤️ by [Deepskilling](https://github.com/deepskilling)**

*FastProxy - Fast, Simple, Powerful*

