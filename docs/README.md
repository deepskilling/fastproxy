# FastProxy Documentation

Welcome to the FastProxy documentation! This guide will help you get started, configure, and deploy FastProxy for your needs.

## 📚 Documentation Index

### Getting Started
- **[Quickstart Guide](guides/QUICKSTART.md)** - Get running in 2 minutes
- **[Installation](guides/QUICKSTART.md#quick-demo-setup)** - Installation options
- **[Configuration Basics](#configuration)** - Basic configuration
- **[First Steps](#)** - Your first proxy route

### Guides
- **[Quick Reference](guides/DEMO_QUICK_REFERENCE.md)** - One-page cheat sheet
- **[Demo Architecture](../webapp/DEMO_ARCHITECTURE.md)** - System architecture
- **[Docker Guide](../docker/README.md)** - Docker deployment
- **[Production Deployment](#)** - Production best practices

### Features
- **[Automatic HTTPS](#automatic-https)** - Let's Encrypt integration
- **[Rate Limiting](#rate-limiting)** - Protect your services
- **[Authentication](#authentication)** - Secure your proxy
- **[Audit Logging](#audit-logging)** - Track all requests
- **[Management UI](../webapp/README.md)** - Web-based management

### API Reference
- **[FastProxy API](#)** - Main proxy endpoints
- **[Management API](../webapp/backend/README.md)** - Management endpoints
- **[Configuration Schema](#)** - YAML configuration reference

### Development
- **[Contributing](../CONTRIBUTING.md)** - How to contribute
- **[Code of Conduct](../CODE_OF_CONDUCT.md)** - Community guidelines
- **[Architecture](DEMO_IMPLEMENTATION_SUMMARY.md)** - Internal architecture

### Operations
- **[Deployment](../docker/README.md)** - Deployment guide
- **[Monitoring](#)** - Monitoring and metrics
- **[Troubleshooting](guides/QUICKSTART.md#troubleshooting)** - Common issues
- **[Security](../SECURITY.md)** - Security best practices

## 🚀 Quick Links

### For Users
- [Get Started](guides/QUICKSTART.md) - Start here!
- [Configuration Examples](../examples/) - Real-world configs
- [Docker Quickstart](../docker/DOCKER_QUICKSTART.md) - Docker in 2 minutes

### For Developers
- [API Documentation](../webapp/backend/README.md) - API reference
- [Frontend Guide](../webapp/frontend/README.md) - UI development
- [Contributing Guide](../CONTRIBUTING.md) - Contribute code

### For DevOps
- [Docker Deployment](../docker/README.md) - Container deployment
- [Production Guide](#production-deployment) - Production setup
- [Monitoring Setup](#monitoring) - Observability

## 📖 Core Concepts

### Reverse Proxy

FastProxy acts as a reverse proxy, forwarding client requests to backend services based on configured routes.

```
Client → FastProxy → Backend Services
```

### Path-Based Routing

Routes are matched by URL path prefix:

```yaml
routes:
  - path: /api
    target: http://backend:8001
  - path: /
    target: http://frontend:3000
```

### Rate Limiting

IP-based rate limiting protects your services:

```yaml
rate_limit:
  requests_per_minute: 100
```

### Automatic HTTPS

Let's Encrypt integration provides automatic SSL/TLS:

```yaml
auto_https:
  enabled: true
  domain: "yourdomain.com"
  email: "admin@yourdomain.com"
```

## ⚙️ Configuration

### Basic Configuration

Minimal configuration to get started:

```yaml
routes:
  - path: /api
    target: http://backend:8001

rate_limit:
  requests_per_minute: 100

cors:
  allow_origins: ["*"]
```

See [Configuration Examples](../examples/) for more.

### Environment Variables

Configure via environment variables:

```bash
LOG_LEVEL=INFO
BACKEND_PORT=8001
JWT_SECRET_KEY=your-secret-key
```

### Configuration Files

- `config.yaml` - Main configuration
- `config.demo.yaml` - Demo configuration
- `.env` - Environment variables

## 🔒 Security

FastProxy includes enterprise security features:

- **Authentication**: JWT, API keys, Basic auth
- **SSRF Protection**: URL validation
- **Rate Limiting**: Per-IP rate limits
- **HTTPS**: Automatic Let's Encrypt
- **Audit Logging**: Complete request logs
- **CORS**: Configurable CORS policies

See [Security Policy](../SECURITY.md) for details.

## 🐳 Docker Deployment

Quick Docker start:

```bash
cd docker
./docker-start.sh
```

See [Docker Guide](../docker/README.md) for complete documentation.

## 🎨 Management UI

FastProxy includes a beautiful web UI:

- Real-time dashboard
- Visual route management
- API key generation
- Configuration editor
- Live log viewer

Access at `http://localhost:8000` after starting the demo.

## 📊 Monitoring

### Health Checks

```bash
curl http://localhost:8000/health
```

### Metrics

- Request count
- Response times
- Error rates
- Active connections

### Logs

```bash
# View logs
docker logs fastproxy

# With docker-compose
docker compose logs -f
```

## 🛠️ Troubleshooting

### Common Issues

**Port already in use**:
```bash
lsof -ti:8000 | xargs kill -9
```

**Cannot connect to backend**:
- Check backend is running
- Verify configuration
- Check network connectivity

**HTTPS not working**:
- Verify domain DNS
- Check ports 80/443 are open
- Review Let's Encrypt logs

See [Troubleshooting Guide](guides/QUICKSTART.md#troubleshooting) for more.

## 🌟 Examples

### Simple Proxy

```yaml
routes:
  - path: /
    target: http://backend:8080
```

### Microservices

```yaml
routes:
  - path: /users
    target: http://user-service:8001
  - path: /products
    target: http://product-service:8002
  - path: /orders
    target: http://order-service:8003
```

### With Authentication

```yaml
routes:
  - path: /api
    target: http://backend:8001
    auth_required: true
```

More in [Examples](../examples/).

## 📝 API Reference

### FastProxy Endpoints

- `GET /health` - Health check
- `POST /admin/reload` - Reload configuration
- `GET /admin/routes` - List routes
- `GET /admin/status` - Server status

### Management API

- `GET /api/routes` - List routes
- `POST /api/routes` - Add route
- `DELETE /api/routes/{path}` - Delete route
- `GET /api/stats` - Statistics

Full API docs: [Management API](../webapp/backend/README.md)

## 🤝 Community

- **GitHub Issues**: Bug reports and feature requests
- **Discussions**: Questions and ideas
- **Contributing**: See [Contributing Guide](../CONTRIBUTING.md)
- **Code of Conduct**: See [Code of Conduct](../CODE_OF_CONDUCT.md)

## 📄 License

MIT License - see [LICENSE](../LICENSE)

## 🙏 Acknowledgments

Built with:
- [FastAPI](https://fastapi.tiangolo.com/) - Web framework
- [Next.js](https://nextjs.org/) - Frontend framework
- [httpx](https://www.python-httpx.org/) - HTTP client
- [uvicorn](https://www.uvicorn.org/) - ASGI server

## 📞 Support

- **Documentation**: You're here!
- **Issues**: [GitHub Issues](https://github.com/yourusername/fastproxy/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/fastproxy/discussions)
- **Email**: support@yourdomain.com

---

**Made with ❤️ by the FastProxy Team**

[⬆ Back to Top](#fastproxy-documentation)

