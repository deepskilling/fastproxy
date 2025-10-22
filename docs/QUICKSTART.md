# 🚀 FastProxy Quick Start Guide

Get FastProxy up and running in under 5 minutes!

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## Option 1: Quick Start Script (Recommended)

The easiest way to get started:

```bash
# Make the script executable (if not already)
chmod +x start.sh

# Run the quick start script
./start.sh
```

This script will:
1. Create a virtual environment
2. Install all dependencies
3. Start the server on http://localhost:8000

## Option 2: Manual Setup

### Step 1: Install Dependencies

```bash
# Create virtual environment (optional but recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### Step 2: Configure Routes

Edit `config.yaml` to set up your backend services:

```yaml
routes:
  - path: /api/
    target: http://127.0.0.1:8001
  - path: /auth/
    target: http://127.0.0.1:8002

rate_limit:
  requests_per_minute: 100
```

### Step 3: Start the Server

```bash
# Development mode (with auto-reload)
uvicorn main:app --reload

# Production mode
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Step 4: Verify It's Working

Open your browser and visit:
- http://localhost:8000/health - Health check
- http://localhost:8000/docs - Interactive API documentation

## Option 3: Using Docker

### Quick Start with Docker Compose

```bash
# Start FastProxy and example backend services
docker-compose -f docker/docker-compose.yml up -d

# View logs
docker-compose -f docker/docker-compose.yml logs -f

# Stop services
docker-compose -f docker/docker-compose.yml down
```

This will start:
- FastProxy on port 8000
- Three example backend services (httpbin) on ports 8001, 8002, 8003

### Build and Run Manually

```bash
# Build the image
docker build -f docker/Dockerfile -t fastproxy .

# Run the container
docker run -p 8000:8000 -v $(pwd)/config.yaml:/app/config.yaml fastproxy
```

## Option 4: Using Make

If you have `make` installed:

```bash
# Install dependencies
make install

# Run the server
make run

# Run tests
make test

# Clean up
make clean
```

## Testing Your Setup

### 1. Test Health Check
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status": "healthy", "service": "fastproxy"}
```

### 2. Test Proxy Forwarding

First, start a backend service (or use the Docker Compose setup):

```bash
# Using Docker
docker run -p 8001:80 kennethreitz/httpbin
```

Then test the proxy:

```bash
# This will be forwarded to http://127.0.0.1:8001/api/get
curl http://localhost:8000/api/get
```

### 3. Test Admin Endpoints

```bash
# List configured routes
curl http://localhost:8000/admin/routes

# Get server status
curl http://localhost:8000/admin/status

# Reload configuration (after editing config.yaml)
curl -X POST http://localhost:8000/admin/reload
```

### 4. Test Audit Logs

```bash
# View recent audit logs
curl http://localhost:8000/audit/logs?limit=10

# Get audit statistics
curl http://localhost:8000/audit/stats
```

## Common Issues

### Issue: "Module not found" error
**Solution**: Make sure you've activated the virtual environment and installed all dependencies:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Issue: "Config file not found"
**Solution**: Ensure `config.yaml` exists in the same directory as `main.py`

### Issue: "Connection refused" when proxying
**Solution**: Make sure your backend services are running and accessible at the URLs specified in `config.yaml`

### Issue: Port 8000 already in use
**Solution**: Stop the other service using port 8000, or run FastProxy on a different port:
```bash
uvicorn main:app --port 8080
```

## Next Steps

1. **Configure Your Routes**: Edit `config.yaml` to point to your actual backend services
2. **Set Up Rate Limiting**: Adjust the `requests_per_minute` setting based on your needs
3. **Review Logs**: Check `audit/audit.db` for request logs
4. **Run Tests**: Execute `pytest` to ensure everything works correctly
5. **Deploy to Production**: See the README.md for production deployment options

## Useful Commands

```bash
# View application logs
tail -f logs/fastproxy.log

# Check SQLite audit database
sqlite3 audit/audit.db "SELECT * FROM audit_log ORDER BY timestamp DESC LIMIT 10;"

# Test rate limiting
for i in {1..150}; do curl http://localhost:8000/api/test; done

# Monitor server performance
curl http://localhost:8000/admin/status
```

## Getting Help

- **API Documentation**: http://localhost:8000/docs
- **Check Logs**: Look at the console output for error messages
- **Review Tests**: See the `tests/` directory for usage examples

## What's Next?

Now that FastProxy is running, you can:
- Add more routes to `config.yaml`
- Configure rate limits per route
- Set up monitoring and alerting
- Deploy to production
- Integrate with your existing infrastructure

Happy proxying! 🎉

