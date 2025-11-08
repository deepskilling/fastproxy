# 🐳 Docker Quickstart - 2 Minutes to Running!

Get FastProxy running with Docker in just a few commands.

## Prerequisites

- Docker installed ([Get Docker](https://docs.docker.com/get-docker/))
- Docker Compose installed (included with Docker Desktop)

Check your installation:
```bash
docker --version
docker compose version
```

## 🚀 Quick Start

### Option 1: Using the Startup Script (Easiest)

```bash
cd docker
./docker-start.sh
```

### Option 2: Using Docker Compose

```bash
cd docker
docker compose -f docker-compose.demo.yml up -d
```

### Option 3: Using Make

```bash
cd docker
make demo
```

## 🌐 Access the Application

Once started, access:

- **Main Application**: http://localhost:8000
- **Backend API**: http://localhost:8001/docs
- **Frontend UI**: http://localhost:3000

## 🎮 Common Commands

### View Logs
```bash
# All services
docker compose -f docker-compose.demo.yml logs -f

# Specific service
docker compose -f docker-compose.demo.yml logs -f fastproxy
```

### Stop Services
```bash
docker compose -f docker-compose.demo.yml down
```

### Restart Services
```bash
docker compose -f docker-compose.demo.yml restart
```

### Check Status
```bash
docker compose -f docker-compose.demo.yml ps
```

## 🔧 Using Make (Recommended)

If you have `make` installed:

```bash
# Start demo
make demo

# View logs
make logs

# Check health
make health

# Stop everything
make down

# See all commands
make help
```

## 🛠️ Troubleshooting

### Ports Already in Use

Edit `docker-compose.demo.yml` to use different ports:
```yaml
ports:
  - "8080:8000"  # Use 8080 instead of 8000
```

### Services Won't Start

```bash
# View logs to see what's wrong
docker compose -f docker-compose.demo.yml logs

# Rebuild images
docker compose -f docker-compose.demo.yml build --no-cache

# Try again
docker compose -f docker-compose.demo.yml up -d
```

### Need to Reset Everything

```bash
# Stop and remove everything
docker compose -f docker-compose.demo.yml down -v

# Start fresh
docker compose -f docker-compose.demo.yml up -d
```

## 📊 Monitoring

### Check Health
```bash
docker ps --filter "name=fastproxy"
```

### Resource Usage
```bash
docker stats
```

### Inspect Containers
```bash
docker inspect fastproxy
```

## 🎓 Next Steps

1. **Explore the UI**: Visit http://localhost:8000
2. **Read Full Docs**: See [README.md](README.md)
3. **Customize**: Edit configuration files
4. **Deploy**: Use for production

## 📚 More Information

- [Full Docker Documentation](README.md)
- [FastProxy Documentation](../README.md)
- [WebApp Guide](../webapp/README.md)

---

**That's it! You're running FastProxy in Docker! 🎉**

