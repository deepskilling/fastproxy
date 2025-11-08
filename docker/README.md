# 🐳 FastProxy Docker Deployment

Complete Docker implementation for FastProxy with management WebApp.

## 📦 What's Included

- **FastProxy**: Main reverse proxy service
- **Backend API**: Management REST API
- **Frontend UI**: Next.js management interface
- **Docker Compose**: Orchestration for all services
- **Volumes**: Persistent data storage
- **Health Checks**: Automatic service monitoring

## 🚀 Quick Start

### Option 1: Demo Stack (Recommended for Testing)

Run the complete demo with management UI:

```bash
cd docker
docker-compose -f docker-compose.demo.yml up -d
```

Access:
- **Main Application**: http://localhost:8000
- **Backend API Docs**: http://localhost:8001/docs
- **Frontend UI**: http://localhost:3000

### Option 2: Production Stack

Run FastProxy with your own backends:

```bash
cd docker
docker-compose up -d
```

## 📁 Files Overview

```
docker/
├── Dockerfile.fastproxy       # FastProxy image
├── Dockerfile.backend          # Backend API image
├── Dockerfile.frontend         # Frontend UI image
├── docker-compose.demo.yml     # Demo stack
├── docker-compose.yml          # Production stack
├── .dockerignore              # Files to exclude
└── README.md                  # This file
```

## 🔧 Configuration

### Environment Variables

#### FastProxy
- `LOG_LEVEL`: Logging level (INFO, DEBUG, WARNING, ERROR)
- `PYTHONUNBUFFERED`: Enable real-time logging (1)

#### Backend API
- `BACKEND_PORT`: Port to run on (default: 8001)
- `BACKEND_HOST`: Host to bind to (default: 0.0.0.0)
- `FASTPROXY_CONFIG_PATH`: Path to config file

#### Frontend UI
- `NEXT_PUBLIC_API_URL`: Backend API URL
- `NODE_ENV`: Node environment (production)

### Volumes

Persistent data is stored in named volumes:

- `fastproxy-audit`: Audit logs
- `fastproxy-certs`: SSL certificates
- `fastproxy-accounts`: Let's Encrypt accounts
- `fastproxy-backend-logs`: Backend logs

### Networks

All services run on the `fastproxy-network` bridge network for inter-service communication.

## 📋 Detailed Usage

### Build Images

```bash
# Build all images
docker-compose -f docker-compose.demo.yml build

# Build specific service
docker-compose -f docker-compose.demo.yml build fastproxy
```

### Start Services

```bash
# Start all services (detached)
docker-compose -f docker-compose.demo.yml up -d

# Start with logs
docker-compose -f docker-compose.demo.yml up

# Start specific service
docker-compose -f docker-compose.demo.yml up -d backend
```

### Stop Services

```bash
# Stop all services
docker-compose -f docker-compose.demo.yml down

# Stop and remove volumes (⚠️ deletes data)
docker-compose -f docker-compose.demo.yml down -v
```

### View Logs

```bash
# All services
docker-compose -f docker-compose.demo.yml logs -f

# Specific service
docker-compose -f docker-compose.demo.yml logs -f fastproxy

# Last 100 lines
docker-compose -f docker-compose.demo.yml logs --tail=100 fastproxy
```

### Check Status

```bash
# List running containers
docker-compose -f docker-compose.demo.yml ps

# Check health status
docker ps --filter "name=fastproxy" --format "table {{.Names}}\t{{.Status}}"
```

### Restart Services

```bash
# Restart all
docker-compose -f docker-compose.demo.yml restart

# Restart specific service
docker-compose -f docker-compose.demo.yml restart fastproxy
```

## 🏗️ Architecture

### Demo Stack

```
┌─────────────────────────────────────────────┐
│              Docker Host                     │
│                                              │
│  ┌────────────────────────────────────────┐ │
│  │     fastproxy-network (bridge)         │ │
│  │                                         │ │
│  │  ┌──────────────┐                      │ │
│  │  │  FastProxy   │  Port 8000 → Host   │ │
│  │  │   (8000)     │                      │ │
│  │  └──────┬───────┘                      │ │
│  │         │                               │ │
│  │    ┌────┴─────┐                        │ │
│  │    │          │                        │ │
│  │    ▼          ▼                        │ │
│  │  ┌────────┐ ┌────────┐                │ │
│  │  │Backend │ │Frontend│                │ │
│  │  │  API   │ │   UI   │                │ │
│  │  │ (8001) │ │ (3000) │                │ │
│  │  └────────┘ └────────┘                │ │
│  │                                         │ │
│  └─────────────────────────────────────────┘ │
│                                              │
│  Volumes:                                    │
│  • fastproxy-audit                          │
│  • fastproxy-certs                          │
│  • backend-logs                             │
└─────────────────────────────────────────────┘
```

### Request Flow

1. Client → http://localhost:8000
2. Docker routes to FastProxy container (port 8000)
3. FastProxy routes to backend/frontend containers
4. Response flows back through FastProxy
5. Client receives response

## 🔒 Security

### Production Recommendations

1. **Use HTTPS**
   ```yaml
   # In config.yaml
   auto_https:
     enabled: true
     domain: "your-domain.com"
   ```

2. **Restrict Ports**
   ```yaml
   # Only expose necessary ports
   ports:
     - "443:443"    # HTTPS only
     - "80:80"      # For Let's Encrypt
   ```

3. **Use Secrets**
   ```yaml
   # docker-compose.yml
   secrets:
     jwt_secret:
       file: ./secrets/jwt_secret.txt
   ```

4. **Read-Only Volumes**
   ```yaml
   volumes:
     - ../config.yaml:/app/config.yaml:ro  # read-only
   ```

5. **Non-Root User**
   Frontend already runs as non-root (user: nextjs)

## 📊 Monitoring

### Health Checks

All services include health checks:

```bash
# Check health status
docker inspect --format='{{.State.Health.Status}}' fastproxy
```

Health check endpoints:
- FastProxy: `http://localhost:8000/health`
- Backend: `http://localhost:8001/api/health`
- Frontend: `http://localhost:3000/`

### Resource Usage

```bash
# Monitor resource usage
docker stats

# Specific container
docker stats fastproxy
```

### Logs

```bash
# Real-time logs
docker-compose logs -f

# Export logs
docker logs fastproxy > fastproxy.log 2>&1
```

## 🔧 Customization

### Custom Configuration

1. **Edit config file**
   ```bash
   nano ../config.yaml
   ```

2. **Reload FastProxy**
   ```bash
   docker-compose restart fastproxy
   ```

### Add Custom Backend

```yaml
# docker-compose.yml
services:
  my-backend:
    image: my-backend:latest
    expose:
      - "8080"
    networks:
      - fastproxy-network
```

Then update config.yaml:
```yaml
routes:
  - path: /myapi
    target: http://my-backend:8080
```

### Environment Variables

Create `.env` file:
```bash
# .env
LOG_LEVEL=DEBUG
BACKEND_PORT=8001
```

Reference in docker-compose.yml:
```yaml
env_file:
  - .env
```

## 🐛 Troubleshooting

### Containers Won't Start

```bash
# Check logs
docker-compose logs

# Check specific service
docker-compose logs fastproxy

# Rebuild images
docker-compose build --no-cache
```

### Port Already in Use

```bash
# Find process using port
lsof -i :8000

# Change port in docker-compose.yml
ports:
  - "8080:8000"  # Use 8080 instead
```

### Network Issues

```bash
# Recreate network
docker-compose down
docker network prune
docker-compose up -d
```

### Volume Permission Issues

```bash
# Reset volumes
docker-compose down -v
docker-compose up -d
```

### Can't Connect to Backend

```bash
# Check if services are on same network
docker network inspect fastproxy-network

# Check DNS resolution
docker exec fastproxy ping backend -c 3
```

### Health Check Failing

```bash
# Check health status
docker inspect fastproxy | grep -A 10 Health

# Test endpoint manually
docker exec fastproxy curl http://localhost:8000/health
```

## 📈 Scaling

### Horizontal Scaling

Scale specific services:

```bash
# Scale backend API
docker-compose up -d --scale backend=3
```

Add load balancer (nginx example):
```yaml
services:
  nginx:
    image: nginx:alpine
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - backend
```

### Resource Limits

```yaml
services:
  fastproxy:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 1G
        reservations:
          cpus: '1'
          memory: 512M
```

## 🚢 Production Deployment

### Using Docker Swarm

```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml fastproxy

# Check services
docker service ls

# Scale service
docker service scale fastproxy_backend=3
```

### Using Kubernetes

Convert docker-compose to Kubernetes:

```bash
# Install kompose
curl -L https://github.com/kubernetes/kompose/releases/download/v1.28.0/kompose-linux-amd64 -o kompose

# Convert
kompose convert -f docker-compose.yml

# Deploy
kubectl apply -f .
```

## 🔄 Updates & Maintenance

### Update Images

```bash
# Pull latest images
docker-compose pull

# Rebuild and restart
docker-compose up -d --build
```

### Backup Data

```bash
# Backup volumes
docker run --rm -v fastproxy-audit:/data -v $(pwd):/backup \
  alpine tar czf /backup/fastproxy-audit-backup.tar.gz /data

# Restore volumes
docker run --rm -v fastproxy-audit:/data -v $(pwd):/backup \
  alpine tar xzf /backup/fastproxy-audit-backup.tar.gz -C /
```

### Clean Up

```bash
# Remove stopped containers
docker-compose rm

# Remove unused images
docker image prune

# Remove unused volumes (⚠️ careful!)
docker volume prune

# Full cleanup
docker system prune -a --volumes
```

## 📚 Additional Resources

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [FastProxy Documentation](../README.md)
- [Management WebApp Guide](../webapp/README.md)

## 💡 Tips

1. **Use docker-compose.demo.yml for testing**
2. **Always backup volumes before updates**
3. **Monitor logs regularly**: `docker-compose logs -f`
4. **Set resource limits in production**
5. **Use health checks for reliability**
6. **Keep images updated for security**
7. **Use .env files for configuration**
8. **Test changes in demo before production**

## 🆘 Getting Help

If you encounter issues:

1. Check logs: `docker-compose logs -f`
2. Verify configuration: `docker-compose config`
3. Check health: `docker ps`
4. Review documentation: [Main README](../README.md)
5. Open an issue on GitHub

---

**Happy Dockerizing! 🐳**

