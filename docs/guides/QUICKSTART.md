# 🚀 FastProxy Quickstart Guide

Get FastProxy up and running with the demo management webapp in under 5 minutes!

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Demo Setup](#quick-demo-setup)
- [Manual Setup](#manual-setup)
- [Testing the Demo](#testing-the-demo)
- [Architecture Overview](#architecture-overview)
- [Troubleshooting](#troubleshooting)
- [Next Steps](#next-steps)

## Prerequisites

Before you begin, ensure you have:

- **Python 3.8+** installed
- **Node.js 18+** and npm installed
- **Terminal/Command Line** access
- **8000, 8001, and 3000** ports available

Check your versions:
```bash
python --version  # or python3 --version
node --version
npm --version
```

## 🎯 Quick Demo Setup

### Option 1: One-Command Start (Recommended)

Use the all-in-one startup script:

```bash
# Make script executable (first time only)
chmod +x start-demo.sh

# Start everything
./start-demo.sh
```

This will start:
1. ✅ FastProxy (port 8000)
2. ✅ Management API Backend (port 8001)
3. ✅ Management UI Frontend (port 3000)

### Option 2: Individual Services

Start each service in a separate terminal:

**Terminal 1 - FastProxy:**
```bash
# Activate your Python environment
conda activate fastapi  # or: source venv/bin/activate

# Start FastProxy with demo config
python main.py --config config.demo.yaml
```

**Terminal 2 - Management API Backend:**
```bash
cd webapp
./start-backend.sh
```

**Terminal 3 - Management UI Frontend:**
```bash
cd webapp
./start-frontend.sh
```

## 📦 Manual Setup

If the startup scripts don't work, follow these steps:

### Step 1: Setup Python Environment

```bash
# Create virtual environment (if not already created)
python -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install FastProxy dependencies
pip install -r requirements.txt
```

### Step 2: Setup Management Backend

```bash
cd webapp/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Return to project root
cd ../..
```

### Step 3: Setup Management Frontend

```bash
cd webapp/frontend

# Install dependencies
npm install

# Create environment file
cp .env.example .env.local

# Edit .env.local if needed (default should work)
# NEXT_PUBLIC_API_URL=http://localhost:8001

# Return to project root
cd ../..
```

### Step 4: Start Services

**Terminal 1 - FastProxy:**
```bash
# From project root with activated venv
python main.py
```

**Terminal 2 - Management API:**
```bash
cd webapp/backend
source venv/bin/activate  # If not activated
python main.py
```

**Terminal 3 - Management UI:**
```bash
cd webapp/frontend
npm run dev
```

## 🧪 Testing the Demo

Once all services are running, access the demo:

### 1. Open the Management UI

Navigate to: **http://localhost:8000**

> Note: You're accessing through FastProxy (port 8000), which proxies to the frontend (port 3000)

### 2. Explore the Interface

You'll see the FastProxy Management Dashboard with:

- **Dashboard** - System health and statistics
- **Routes** - Proxy route management
- **API Keys** - Authentication key management
- **Configuration** - Edit FastProxy settings
- **Logs** - View system logs

### 3. Test Proxy Functionality

**Add a Test Route:**

1. Navigate to "Routes" page
2. Click "Add Route"
3. Fill in:
   - Path: `/test`
   - Target: `https://jsonplaceholder.typicode.com`
   - Methods: GET, POST
   - Auth: Optional
4. Click "Create Route"

**Test the Route:**

```bash
# Request through FastProxy
curl http://localhost:8000/test/posts/1

# This proxies to: https://jsonplaceholder.typicode.com/posts/1
```

### 4. View API Documentation

FastAPI auto-generates API documentation:

- **Backend API Docs**: http://localhost:8001/docs
- **FastProxy Admin API**: http://localhost:8000/admin/config

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    Client Browser                        │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
            ┌────────────────┐
            │   FastProxy    │  ← YOU ARE HERE
            │   Port 8000    │     (Reverse Proxy)
            └────────┬───────┘
                     │
        ┌────────────┴────────────┐
        │                         │
        ▼                         ▼
┌──────────────┐         ┌──────────────┐
│  Frontend    │         │   Backend    │
│  Next.js     │         │   FastAPI    │
│  Port 3000   │         │   Port 8001  │
└──────────────┘         └──────────────┘
```

**Request Flow:**

1. Client requests `http://localhost:8000/`
2. FastProxy routes to Frontend (3000)
3. Frontend loads in browser
4. Frontend makes API calls to `http://localhost:8000/api/*`
5. FastProxy routes `/api/*` to Backend (8001)
6. Backend processes and responds

**Key Points:**

- All traffic goes through FastProxy (port 8000)
- Frontend (3000) and Backend (8001) are never accessed directly
- This demonstrates FastProxy's routing and proxying capabilities

## 🎛️ Configuration

### Demo Configuration

The demo uses `config.demo.yaml` which is optimized for local development:

- HTTPS: Disabled (for easy testing)
- CORS: Configured for localhost
- Rate Limiting: 100 requests/minute
- Logging: INFO level

### Modifying Configuration

Edit `config.demo.yaml` or `config.yaml`:

```yaml
# Add a new route
routes:
  - path: /myapi
    target: http://backend.example.com
    strip_path: true

# Update rate limit
rate_limit:
  requests_per_minute: 1000

# Enable HTTPS
auto_https:
  enabled: true
  domain: "your-domain.com"
  email: "admin@your-domain.com"
```

After changes, restart FastProxy to apply.

## 🐛 Troubleshooting

### Port Already in Use

**Error:** `Address already in use: 8000`

**Solution:**
```bash
# Find process using the port
lsof -ti:8000 | xargs kill -9  # macOS/Linux
# Or on Windows: netstat -ano | findstr :8000

# Then restart
```

### Cannot Connect to Backend

**Error:** Frontend shows "Network Error" or "Cannot connect"

**Solution:**
1. Verify backend is running: `curl http://localhost:8001/api/health`
2. Check CORS settings in `webapp/backend/main.py`
3. Verify `NEXT_PUBLIC_API_URL` in `webapp/frontend/.env.local`

### Module Not Found

**Error:** `ModuleNotFoundError: No module named 'fastapi'`

**Solution:**
```bash
# Make sure virtual environment is activated
source venv/bin/activate  # or conda activate fastapi

# Reinstall dependencies
pip install -r requirements.txt
```

### Frontend Build Errors

**Error:** TypeScript or build errors

**Solution:**
```bash
cd webapp/frontend

# Clear cache
rm -rf .next node_modules package-lock.json

# Reinstall
npm install

# Try again
npm run dev
```

### FastProxy Routes Not Working

**Check these:**

1. Config file is valid YAML
2. Backend services are running
3. Routes are defined correctly
4. Check FastProxy logs for errors

```bash
# Test route matching
curl -v http://localhost:8000/api/health
```

## 📝 Common Commands

### Start Services

```bash
# FastProxy
python main.py

# Backend
cd webapp/backend && python main.py

# Frontend
cd webapp/frontend && npm run dev
```

### Stop Services

- Press `Ctrl+C` in each terminal
- Or kill processes: `pkill -f "python main.py"`

### View Logs

```bash
# FastProxy logs (in terminal where it's running)
# Or check: logs/ directory if configured

# Backend logs
cd webapp/backend && tail -f *.log

# Frontend logs
# Available in the npm run dev terminal
```

### Reset Demo

```bash
# Stop all services
pkill -f "python main.py"
pkill -f "node"

# Clean frontend
cd webapp/frontend
rm -rf .next node_modules
npm install

# Restart everything
./start-demo.sh
```

## 🎓 Next Steps

Now that you have the demo running:

### 1. Learn the Features

- **Add Routes**: Configure proxy routes for your backends
- **Set Rate Limits**: Protect your services from abuse
- **Enable HTTPS**: Use Let's Encrypt for automatic SSL
- **Monitor**: Use the dashboard to track metrics

### 2. Customize for Your Use Case

- Modify routes to proxy your actual backends
- Adjust rate limits based on your traffic
- Configure authentication for API endpoints
- Enable audit logging for compliance

### 3. Deploy to Production

See deployment guides:
- [DEPLOYMENT.md](./DEPLOYMENT.md) - Production deployment
- [SECURITY.md](./SECURITY.md) - Security best practices
- [AUTO_SSL_SETUP.md](./docs/AUTO_SSL_SETUP.md) - HTTPS setup

### 4. Explore Advanced Features

- **Authentication**: JWT, API keys, OAuth
- **Load Balancing**: Multiple backend servers
- **Circuit Breaking**: Fault tolerance
- **Metrics**: Prometheus integration
- **Logging**: Centralized log aggregation

## 📚 Additional Resources

- **Main README**: [README.md](./README.md)
- **API Documentation**: http://localhost:8001/docs (when running)
- **Architecture**: [docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md)
- **Contributing**: [docs/CONTRIBUTING.md](./docs/CONTRIBUTING.md)

## 🤝 Getting Help

- **Issues**: Report bugs on GitHub Issues
- **Discussions**: Ask questions on GitHub Discussions
- **Documentation**: Check the docs/ directory

## ⚡ Quick Reference

| Service | URL | Purpose |
|---------|-----|---------|
| FastProxy | http://localhost:8000 | Main reverse proxy |
| Management UI | http://localhost:3000 | Direct frontend access |
| Backend API | http://localhost:8001 | Direct API access |
| API Docs | http://localhost:8001/docs | OpenAPI documentation |

**Environment Variables:**

```bash
# Backend
BACKEND_PORT=8001
JWT_SECRET_KEY=your-secret-key

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8001
```

**Key Files:**

- `config.yaml` - Production config
- `config.demo.yaml` - Demo config
- `main.py` - FastProxy entry point
- `webapp/backend/main.py` - Backend API
- `webapp/frontend/` - Frontend UI

---

**🎉 Congratulations!** You now have FastProxy running with a full management interface. Start building your proxy configuration!

For production deployment, see [DEPLOYMENT.md](./DEPLOYMENT.md)

