# 🎯 FastProxy Demo - Quick Reference Card

## 🚀 Start the Demo

```bash
./start-demo.sh
```

Then open: **http://localhost:8000**

## 📍 Access Points

| Service | URL | Purpose |
|---------|-----|---------|
| **Main App** | http://localhost:8000 | Access everything through FastProxy |
| Frontend | http://localhost:3000 | Direct frontend access (debug) |
| Backend | http://localhost:8001 | Direct backend access (debug) |
| API Docs | http://localhost:8001/docs | Interactive API documentation |

## 🛠️ Common Commands

### Start Services

```bash
# All at once
./start-demo.sh

# Individual services
cd webapp && ./start-backend.sh    # Terminal 1
cd webapp && ./start-frontend.sh   # Terminal 2
python main.py                      # Terminal 3
```

### Stop Services

```bash
# Ctrl+C in each terminal

# Or kill all
pkill -f "python main.py"
pkill -f "next dev"
```

### View Logs

```bash
tail -f fastproxy.log              # FastProxy logs
tail -f webapp/backend/backend.log # Backend logs
tail -f webapp/frontend/frontend.log # Frontend logs
```

### Reset Demo

```bash
# Clean everything
cd webapp/frontend
rm -rf .next node_modules
npm install

# Restart
./start-demo.sh
```

## 📁 Key Files

| File | Purpose |
|------|---------|
| `config.yaml` | Production FastProxy config |
| `config.demo.yaml` | Demo configuration |
| `QUICKSTART.md` | Detailed setup guide |
| `webapp/README.md` | WebApp documentation |
| `start-demo.sh` | All-in-one startup script |

## 🔧 Configuration

### Edit Routes

**Via UI**: http://localhost:8000/routes → Click "Add Route"

**Via Config**:
```yaml
# Edit config.yaml or config.demo.yaml
routes:
  - path: /myapi
    target: http://backend.example.com
    strip_path: false
```

### Change Rate Limit

```yaml
rate_limit:
  requests_per_minute: 100  # Adjust as needed
```

### Enable HTTPS

```yaml
auto_https:
  enabled: true
  domain: "your-domain.com"
  email: "admin@your-domain.com"
  staging: true  # false for production
```

## 🧪 Test the Demo

### 1. View Dashboard
```
http://localhost:8000/
```

### 2. Add a Test Route

1. Go to http://localhost:8000/routes
2. Click "Add Route"
3. Fill in:
   - Path: `/test`
   - Target: `https://jsonplaceholder.typicode.com`
   - Methods: GET, POST
4. Click "Create Route"

### 3. Test the Route

```bash
curl http://localhost:8000/test/posts/1
```

### 4. View Logs

Go to http://localhost:8000/logs

## 🎨 UI Pages

| Page | Path | Features |
|------|------|----------|
| **Dashboard** | `/` | Health status, statistics, recent activity |
| **Routes** | `/routes` | Add, edit, delete proxy routes |
| **API Keys** | `/api-keys` | Create, view, revoke API keys |
| **Config** | `/config` | Edit FastProxy configuration |
| **Logs** | `/logs` | View and filter system logs |

## 🔌 API Endpoints

### FastProxy Admin
- `GET /health` - Health check
- `POST /admin/reload` - Reload config
- `GET /admin/routes` - List routes
- `GET /admin/status` - Server status

### Management Backend
- `GET /api/health` - Backend health
- `GET /api/config` - Get configuration
- `PUT /api/config` - Update configuration
- `GET /api/routes` - List routes
- `POST /api/routes` - Add route
- `DELETE /api/routes/{path}` - Delete route
- `GET /api/stats` - Statistics
- `GET /api/keys` - List API keys
- `POST /api/keys` - Create API key
- `GET /api/logs` - Get logs

## 🐛 Troubleshooting

### Port Already in Use

```bash
# Find and kill process
lsof -ti:8000 | xargs kill -9
lsof -ti:8001 | xargs kill -9
lsof -ti:3000 | xargs kill -9
```

### Cannot Connect to Backend

1. Check backend is running: `curl http://localhost:8001/api/health`
2. Check CORS settings in `webapp/backend/main.py`
3. Verify `NEXT_PUBLIC_API_URL` in `webapp/frontend/.env.local`

### Module Not Found

```bash
# Activate environment
source venv/bin/activate  # or: conda activate fastapi

# Reinstall dependencies
pip install -r requirements.txt
```

### Frontend Build Errors

```bash
cd webapp/frontend
rm -rf .next node_modules package-lock.json
npm install
npm run dev
```

## 🎓 Learning Path

### Day 1: Basic Setup
1. ✅ Run `./start-demo.sh`
2. ✅ Open http://localhost:8000
3. ✅ Explore the dashboard
4. ✅ View existing routes

### Day 2: Configuration
1. ✅ Add a new route via UI
2. ✅ Test the route with curl
3. ✅ View logs for the request
4. ✅ Edit rate limit in config

### Day 3: Advanced
1. ✅ Create an API key
2. ✅ Edit configuration directly
3. ✅ Enable HTTPS (staging)
4. ✅ Monitor statistics

### Day 4: Production
1. ✅ Deploy to server
2. ✅ Configure real domain
3. ✅ Enable production HTTPS
4. ✅ Set up monitoring

## 📚 Documentation Links

- **[QUICKSTART.md](QUICKSTART.md)** - Detailed setup guide
- **[README.md](README.md)** - Main documentation
- **[webapp/README.md](webapp/README.md)** - WebApp guide
- **[webapp/DEMO_ARCHITECTURE.md](webapp/DEMO_ARCHITECTURE.md)** - Architecture details

## 🔑 Default Credentials

The demo runs **without authentication** for easy testing.

For production:
1. Set `JWT_SECRET_KEY` in backend `.env`
2. Configure authentication in FastProxy
3. Enable API key requirement for routes

## 💡 Pro Tips

1. **Use the UI**: It's faster than editing YAML
2. **Check Logs**: The logs page shows real-time activity
3. **Test First**: Use staging mode for HTTPS testing
4. **Backup Config**: Keep a copy of working config
5. **Monitor Stats**: Dashboard shows request counts
6. **Rate Limits**: Start conservative, increase as needed
7. **Hot Reload**: Most changes don't require restart
8. **API Docs**: Use /docs for interactive API testing

## 🎯 Common Use Cases

### Microservices Gateway
```yaml
routes:
  - path: /users
    target: http://users-service:8001
  - path: /orders
    target: http://orders-service:8002
  - path: /products
    target: http://products-service:8003
```

### Frontend + Backend
```yaml
routes:
  - path: /api
    target: http://backend:8001
    strip_path: true
  - path: /
    target: http://frontend:3000
```

### Load Balancing
```yaml
routes:
  - path: /api
    target: http://backend-1:8001
  # Add multiple backends with load balancer
```

### SSL Termination
```yaml
auto_https:
  enabled: true
  domain: "api.example.com"
  # FastProxy handles SSL, backends use HTTP
```

## ⚡ Performance Tuning

```yaml
# Increase throughput
rate_limit:
  requests_per_minute: 10000

proxy_settings:
  timeout: 60.0
  max_keepalive_connections: 500
  max_connections: 1000

# Or run multiple workers
uvicorn main:app --workers 4
```

## 🆘 Quick Help

**Question**: How do I add a route?
**Answer**: Go to http://localhost:8000/routes → "Add Route"

**Question**: How do I enable HTTPS?
**Answer**: Edit `auto_https` in config.yaml, set domain and email

**Question**: How do I test a route?
**Answer**: `curl http://localhost:8000/your-path`

**Question**: Where are the logs?
**Answer**: http://localhost:8000/logs or `tail -f *.log`

**Question**: How do I stop everything?
**Answer**: Press Ctrl+C in the terminal running start-demo.sh

---

**🎉 Happy Proxying!**

For more help, see [QUICKSTART.md](QUICKSTART.md) or open an issue on GitHub.

