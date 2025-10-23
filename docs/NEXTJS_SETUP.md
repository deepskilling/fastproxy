# ⚡ Using FastProxy with Next.js

Complete guide to proxying Next.js applications through FastProxy.

---

## 🎯 Overview

FastProxy can act as a reverse proxy for your Next.js application, providing:
- ✅ Rate limiting
- ✅ Audit logging
- ✅ Authentication/authorization
- ✅ CORS management
- ✅ Security headers
- ✅ Multiple backend routing

---

## 📋 Configuration

### Basic Next.js Setup

Next.js typically runs on **port 3000**. Configure FastProxy to route all traffic to it:

```yaml
# config.yaml
routes:
  # Next.js static assets (CSS, JS, images)
  - path: /_next/
    target: http://127.0.0.1:3000
  
  # Next.js API routes (if using)
  - path: /api/
    target: http://127.0.0.1:3000
  
  # Root path - all Next.js pages (MUST BE LAST!)
  - path: /
    target: http://127.0.0.1:3000

rate_limit:
  requests_per_minute: 100

cors:
  allow_origins: ["*"]
  allow_credentials: true
  allow_methods: ["*"]
  allow_headers: ["*"]

max_body_size: 10485760  # 10 MB
```

**⚠️ Important:** The `/` route **MUST BE LAST** because FastProxy uses prefix matching (longest match wins).

---

## 🏗️ Architecture Options

### Option 1: FastProxy → Next.js (Recommended for Production)

```
┌─────────┐      ┌───────────┐      ┌─────────┐
│ Browser │─────▶│ FastProxy │─────▶│ Next.js │
│         │      │  :8000    │      │  :3000  │
└─────────┘      └───────────┘      └─────────┘
                      │
                      ├─ Rate Limiting
                      ├─ Auth
                      ├─ Audit Logs
                      └─ Security Headers
```

**Best for:** Production, when you need centralized auth/logging/security

### Option 2: Multiple Backends

```
┌─────────┐      ┌───────────┐      ┌─────────────┐
│ Browser │─────▶│ FastProxy │─────▶│ Next.js     │ :3000
│         │      │  :8000    │      │ (Frontend)  │
└─────────┘      └───────────┘      └─────────────┘
                      │
                      ├─────────────▶┌─────────────┐
                      │              │ FastAPI     │ :8001
                      │              │ (API)       │
                      │              └─────────────┘
                      │
                      └─────────────▶┌─────────────┐
                                     │ Auth Service│ :8002
                                     └─────────────┘
```

**Configuration:**

```yaml
routes:
  # Next.js static assets
  - path: /_next/
    target: http://127.0.0.1:3000
  
  # Backend API (FastAPI, Django, etc.)
  - path: /api/v1/
    target: http://127.0.0.1:8001
  
  # Auth service
  - path: /auth/
    target: http://127.0.0.1:8002
  
  # Next.js pages (must be last)
  - path: /
    target: http://127.0.0.1:3000
```

**Best for:** Microservices architecture

---

## 🚀 Quick Start

### Step 1: Start Next.js

```bash
cd your-nextjs-app
npm run dev
# Server running on http://localhost:3000
```

### Step 2: Configure FastProxy

```bash
cd /path/to/fastproxy

# Edit config.yaml
cat > config.yaml << 'EOF'
routes:
  - path: /_next/
    target: http://127.0.0.1:3000
  - path: /api/
    target: http://127.0.0.1:3000
  - path: /
    target: http://127.0.0.1:3000

rate_limit:
  requests_per_minute: 100

cors:
  allow_origins: ["*"]
  allow_credentials: true
  allow_methods: ["*"]
  allow_headers: ["*"]

max_body_size: 10485760
EOF
```

### Step 3: Start FastProxy

```bash
python main.py
# Server running on http://localhost:8000
```

### Step 4: Test

```bash
# Access Next.js through FastProxy
curl http://localhost:8000/

# Or open in browser
open http://localhost:8000
```

---

## 🔥 Development Mode (Hot Reload)

Next.js uses WebSockets for hot module replacement (HMR). FastProxy **already supports WebSockets** through the forwarder!

**No additional configuration needed** - hot reload works automatically. ✅

### Verify Hot Reload Works

1. Start Next.js: `npm run dev`
2. Start FastProxy: `python main.py`
3. Open browser: `http://localhost:8000`
4. Edit a Next.js file
5. Page should auto-reload

---

## 🌐 Production Deployment

### Option A: FastProxy with SSL (Direct)

```bash
# Get SSL certificate
sudo certbot certonly --standalone -d yourdomain.com

# Configure environment
export FASTPROXY_SSL_CERT=/etc/letsencrypt/live/yourdomain.com/fullchain.pem
export FASTPROXY_SSL_KEY=/etc/letsencrypt/live/yourdomain.com/privkey.pem
export FASTPROXY_SSL_PORT=443

# Build Next.js
cd your-nextjs-app
npm run build

# Start Next.js (production)
npm start  # Runs on port 3000

# Start FastProxy (HTTPS)
cd /path/to/fastproxy
sudo -E python main.py  # Runs on port 443
```

### Option B: Nginx → FastProxy → Next.js (Recommended)

```nginx
# /etc/nginx/sites-available/app
upstream fastproxy {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    location / {
        proxy_pass http://fastproxy;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**Flow:** Nginx (SSL) → FastProxy (Auth/Logs) → Next.js (App)

---

## 🎨 Next.js API Routes

If your Next.js app has API routes (`/api/*`), they'll be proxied automatically:

```yaml
# config.yaml
routes:
  # Next.js API routes
  - path: /api/
    target: http://127.0.0.1:3000
  
  # Static assets
  - path: /_next/
    target: http://127.0.0.1:3000
  
  # Pages
  - path: /
    target: http://127.0.0.1:3000
```

**Example Next.js API route:**

```javascript
// pages/api/hello.js
export default function handler(req, res) {
  res.status(200).json({ message: 'Hello from Next.js API!' })
}
```

**Access through FastProxy:**

```bash
curl http://localhost:8000/api/hello
# {"message": "Hello from Next.js API!"}
```

---

## 🔐 Adding Authentication

Protect Next.js routes with FastProxy authentication:

### Scenario 1: Public Next.js, Protected API

```yaml
# config.yaml
routes:
  # Protected API backend (requires auth)
  - path: /api/v1/
    target: http://127.0.0.1:8001
    # Note: Auth enforced by backend API
  
  # Public Next.js (no auth)
  - path: /
    target: http://127.0.0.1:3000
```

Then in your backend API, use FastProxy JWT/API key auth.

### Scenario 2: Protected Next.js Pages

Add authentication middleware in Next.js:

```javascript
// middleware.js (Next.js 13+)
import { NextResponse } from 'next/server'

export function middleware(request) {
  // Check for FastProxy auth headers
  const authHeader = request.headers.get('authorization')
  const apiKey = request.headers.get('x-api-key')
  
  if (!authHeader && !apiKey) {
    return NextResponse.json(
      { error: 'Unauthorized' },
      { status: 401 }
    )
  }
  
  return NextResponse.next()
}

export const config = {
  matcher: ['/dashboard/:path*', '/admin/:path*']
}
```

---

## 📊 Rate Limiting Next.js

Protect Next.js from abuse:

```yaml
# config.yaml
rate_limit:
  requests_per_minute: 100  # Global limit
```

**Per-route rate limiting** (future feature):

```yaml
routes:
  - path: /api/expensive-operation
    target: http://127.0.0.1:3000
    rate_limit:
      requests_per_minute: 10  # Stricter limit
  
  - path: /
    target: http://127.0.0.1:3000
    rate_limit:
      requests_per_minute: 100  # Normal limit
```

---

## 🐛 Troubleshooting

### Issue 1: "No matching route found"

**Problem:** FastProxy can't match your path

**Solution:** Ensure `/` route exists and is **last** in config:

```yaml
routes:
  - path: /_next/
    target: http://127.0.0.1:3000
  - path: /  # Must be last!
    target: http://127.0.0.1:3000
```

### Issue 2: Next.js not loading assets

**Problem:** CSS/JS files returning 404

**Solution:** Add `/_next/` route for static assets:

```yaml
routes:
  - path: /_next/  # Static assets
    target: http://127.0.0.1:3000
  - path: /
    target: http://127.0.0.1:3000
```

### Issue 3: Hot reload not working

**Problem:** Changes don't reflect in browser

**Solution:** Check:
1. Next.js is running: `curl http://localhost:3000`
2. FastProxy is running: `curl http://localhost:8000`
3. WebSocket connection in browser console (should see no errors)

### Issue 4: Next.js API routes returning 502

**Problem:** `/api/*` routes fail

**Cause:** Next.js not running or wrong port

**Solution:**

```bash
# Check Next.js is running
curl http://localhost:3000/api/hello

# If not, start Next.js
cd your-nextjs-app
npm run dev

# Verify FastProxy config
grep -A 2 'path: /api/' config.yaml
```

### Issue 5: CORS errors in browser

**Problem:** Browser blocks requests

**Solution:** Configure CORS properly:

```yaml
cors:
  allow_origins: ["http://localhost:8000", "https://yourdomain.com"]
  allow_credentials: true
  allow_methods: ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]
  allow_headers: ["*"]
```

### Issue 6: Images not loading

**Problem:** Next.js images return 404

**Solution:** Next.js images are served from `/_next/image`. Ensure root route exists:

```yaml
routes:
  - path: /_next/  # Includes /_next/image
    target: http://127.0.0.1:3000
  - path: /
    target: http://127.0.0.1:3000
```

---

## 📁 Example: Full Stack App

### Directory Structure

```
project/
├── fastproxy/          # This repo
│   ├── main.py
│   ├── config.yaml
│   └── ...
├── frontend/           # Next.js
│   ├── pages/
│   ├── public/
│   ├── package.json
│   └── ...
└── backend/            # FastAPI/Django
    ├── main.py
    └── ...
```

### Configuration

```yaml
# fastproxy/config.yaml
routes:
  # Next.js assets
  - path: /_next/
    target: http://127.0.0.1:3000
  
  # Backend API
  - path: /api/v1/
    target: http://127.0.0.1:8001
  
  # Next.js pages (must be last)
  - path: /
    target: http://127.0.0.1:3000

rate_limit:
  requests_per_minute: 100
```

### Start Script

```bash
#!/bin/bash
# start-all.sh

# Start backend API
cd backend
python main.py &
BACKEND_PID=$!

# Start Next.js
cd ../frontend
npm run dev &
NEXTJS_PID=$!

# Start FastProxy
cd ../fastproxy
python main.py &
PROXY_PID=$!

echo "Started:"
echo "  Backend API: http://localhost:8001 (PID: $BACKEND_PID)"
echo "  Next.js: http://localhost:3000 (PID: $NEXTJS_PID)"
echo "  FastProxy: http://localhost:8000 (PID: $PROXY_PID)"
echo ""
echo "Access your app at: http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for Ctrl+C
trap "kill $BACKEND_PID $NEXTJS_PID $PROXY_PID" EXIT
wait
```

---

## 🎯 Best Practices

### 1. Use Environment Variables

```javascript
// next.config.js
module.exports = {
  env: {
    API_URL: process.env.API_URL || 'http://localhost:8000/api/v1',
  },
}
```

### 2. Handle FastProxy Headers in Next.js

```javascript
// pages/api/example.js
export default function handler(req, res) {
  // Get client IP from FastProxy headers
  const clientIP = req.headers['x-forwarded-for'] || req.connection.remoteAddress
  
  console.log(`Request from: ${clientIP}`)
  
  res.status(200).json({ ip: clientIP })
}
```

### 3. Use Next.js Rewrites (Alternative)

Instead of FastProxy routing, use Next.js rewrites:

```javascript
// next.config.js
module.exports = {
  async rewrites() {
    return [
      {
        source: '/api/v1/:path*',
        destination: 'http://localhost:8001/api/v1/:path*',
      },
    ]
  },
}
```

Then proxy **everything** through FastProxy:

```yaml
# config.yaml
routes:
  - path: /
    target: http://127.0.0.1:3000  # Next.js handles routing
```

### 4. Monitor Performance

Check FastProxy logs for slow requests:

```bash
tail -f logs/fastproxy.log | grep "ms)"
# ← GET / → 200 (123.45ms)
# ← GET /_next/static/... → 200 (5.23ms)
```

---

## 📊 Performance Considerations

### Latency

FastProxy adds minimal latency (~1-5ms overhead):

```
Direct: Browser → Next.js (20ms)
FastProxy: Browser → FastProxy → Next.js (25ms)
```

### Caching

For static assets, consider adding Nginx in front:

```
Browser → Nginx (cache) → FastProxy → Next.js
```

### Load Balancing

For multiple Next.js instances:

```yaml
# Future feature - not yet implemented
routes:
  - path: /
    targets:
      - http://127.0.0.1:3000  # Instance 1
      - http://127.0.0.1:3001  # Instance 2
      - http://127.0.0.1:3002  # Instance 3
    load_balance: round_robin
```

---

## 🔗 Related Docs

- **FastProxy Setup:** `/docs/QUICKSTART.md`
- **Authentication:** `/docs/AUTHENTICATION.md`
- **SSL/TLS:** `/docs/SSL_TLS_SETUP.md`
- **Next.js Docs:** https://nextjs.org/docs

---

## ✅ Checklist

- [ ] Next.js running on port 3000
- [ ] FastProxy configured with `/` route (last in list)
- [ ] `/_next/` route configured for assets
- [ ] CORS configured if needed
- [ ] Test hot reload works
- [ ] Test API routes work
- [ ] Test static assets load
- [ ] Monitor logs for errors

---

**Last Updated:** January 22, 2025  
**FastProxy Version:** 1.0.0  
**Next.js Version:** 13+ (works with 12, 13, 14)

