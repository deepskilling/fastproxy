# 🔒 Auto-SSL Setup (Caddy-like)

**Zero-configuration HTTPS with automatic Let's Encrypt certificates!**

FastProxy can automatically obtain and renew SSL certificates, just like Caddy. No manual certificate management required!

---

## 🎯 Features

- ✅ **Zero-configuration** - Just set domain and email
- ✅ **Automatic provisioning** - Gets Let's Encrypt certificates automatically
- ✅ **Automatic renewal** - Renews certificates 30 days before expiry
- ✅ **No downtime** - Handles renewals in the background
- ✅ **Production-ready** - Uses trusted Let's Encrypt CA
- ✅ **Caddy-like simplicity** - Works just like Caddy's auto-HTTPS

---

## ⚡ Quick Start (2 Steps!)

### Step 1: Set Environment Variables

```bash
# Just 2 variables - that's it!
export FASTPROXY_DOMAIN=example.com
export FASTPROXY_SSL_EMAIL=admin@example.com
```

### Step 2: Run FastProxy

```bash
python main.py
```

**That's it!** FastProxy will:
1. Detect domain & email are set
2. Check if certificate exists
3. If not, automatically get one from Let's Encrypt
4. Start HTTPS server on port 443
5. Auto-renew certificate before expiry

---

## 📋 Requirements

### 1. **certbot** Must Be Installed

```bash
# Ubuntu/Debian
sudo apt-get update && sudo apt-get install certbot

# CentOS/RHEL
sudo yum install certbot

# macOS
brew install certbot

# Check installation
certbot --version
```

### 2. **Port 80 Must Be Available**

Let's Encrypt uses HTTP-01 challenge, which requires port 80:

```bash
# Check if port 80 is in use
sudo lsof -i :80

# If something is running, stop it
sudo systemctl stop nginx  # or apache2, etc.
```

### 3. **Domain Must Point to Your Server**

```bash
# Verify DNS points to your server
dig +short example.com
# Should return your server's IP address

# Or use nslookup
nslookup example.com
```

### 4. **Must Run as Root** (for port 443)

```bash
# Port 443 requires root privileges
sudo -E python main.py
```

---

## 🚀 Usage Examples

### Example 1: Basic Auto-SSL

```bash
# Set environment variables
export FASTPROXY_DOMAIN=api.example.com
export FASTPROXY_SSL_EMAIL=admin@example.com

# Run as root (port 443 requires root)
sudo -E python main.py

# Output:
# 🔒 Auto-SSL enabled (Caddy-like)
# 📜 No valid certificate found. Provisioning new certificate...
# 🔒 Requesting Let's Encrypt certificate for api.example.com...
# ✅ Certificate obtained successfully!
# ✅ Auto-SSL context created successfully
# 🔒 Starting FastProxy with HTTPS on port 443
```

### Example 2: With Systemd Service

```ini
# /etc/systemd/system/fastproxy.service
[Unit]
Description=FastProxy with Auto-SSL
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/fastproxy
Environment="FASTPROXY_DOMAIN=example.com"
Environment="FASTPROXY_SSL_EMAIL=admin@example.com"
Environment="FASTPROXY_SSL_PORT=443"
ExecStart=/usr/bin/python3 main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable fastproxy
sudo systemctl start fastproxy

# Check status
sudo systemctl status fastproxy

# View logs
sudo journalctl -u fastproxy -f
```

### Example 3: Multiple Domains (Not Yet Supported)

```bash
# Future feature - coming soon!
export FASTPROXY_DOMAINS=example.com,www.example.com,api.example.com
export FASTPROXY_SSL_EMAIL=admin@example.com

python main.py
```

---

## 🔧 Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `FASTPROXY_DOMAIN` | ✅ Yes | - | Your domain name |
| `FASTPROXY_SSL_EMAIL` | ✅ Yes | - | Email for Let's Encrypt |
| `FASTPROXY_AUTO_SSL` | ❌ No | `true` | Enable/disable auto-SSL |
| `FASTPROXY_SSL_PORT` | ❌ No | `443` | HTTPS port |
| `FASTPROXY_CERT_DIR` | ❌ No | `./certs` | Certificate storage directory |

### Full Configuration Example

```bash
# Required
export FASTPROXY_DOMAIN=example.com
export FASTPROXY_SSL_EMAIL=admin@example.com

# Optional
export FASTPROXY_AUTO_SSL=true          # Enable auto-SSL
export FASTPROXY_SSL_PORT=443           # HTTPS port
export FASTPROXY_CERT_DIR=./certs       # Cert storage
export FASTPROXY_ADMIN_USERNAME=admin
export FASTPROXY_ADMIN_PASSWORD=secret
export FASTPROXY_JWT_SECRET=jwt_secret

# Run
sudo -E python main.py
```

---

## 🔄 Automatic Renewal

FastProxy automatically renews certificates **30 days before expiry**.

### How It Works

1. Background thread checks certificate daily
2. If < 30 days until expiry, triggers renewal
3. Gets new certificate from Let's Encrypt
4. Replaces old certificate
5. No server restart required

### Manual Renewal

```python
# In Python
from security.auto_ssl import AutoSSL

auto_ssl = AutoSSL(domain="example.com", email="admin@example.com")
auto_ssl.renew_now()
```

Or use certbot directly:

```bash
# Manual renewal
sudo certbot renew

# Dry run (test renewal)
sudo certbot renew --dry-run
```

---

## 📁 Certificate Storage

Certificates are stored in `./certs/` by default:

```
certs/
├── example.com.crt         # Certificate
├── example.com.key         # Private key
├── example.com.fullchain.crt  # Full chain
└── letsencrypt/            # certbot data (if not root)
    ├── config/
    ├── work/
    └── logs/
```

**⚠️ Never commit certificates to Git!** They're already in `.gitignore`.

---

## 🔐 Security

### Certificate Verification

FastProxy automatically:
- ✅ Checks certificate expiry daily
- ✅ Renews 30 days before expiry
- ✅ Uses TLS 1.2+ only
- ✅ Uses strong cipher suites
- ✅ Validates certificate chain

### Let's Encrypt Rate Limits

Be aware of Let's Encrypt rate limits:
- 50 certificates per registered domain per week
- 5 duplicate certificates per week

**Solution:** Test with `--dry-run` first!

```bash
certbot certonly --standalone --dry-run -d example.com
```

---

## 🐛 Troubleshooting

### Issue 1: "certbot not found"

**Problem:** certbot not installed

**Solution:**

```bash
# Ubuntu/Debian
sudo apt-get install certbot

# CentOS/RHEL
sudo yum install certbot

# macOS
brew install certbot

# Verify
certbot --version
```

### Issue 2: "Port 80 already in use"

**Problem:** Another service using port 80

**Solution:**

```bash
# Find what's using port 80
sudo lsof -i :80

# Stop the service
sudo systemctl stop nginx  # or apache2

# Or use certbot in webroot mode instead
```

### Issue 3: "Permission denied" (port 443)

**Problem:** Non-root user can't bind to port 443

**Solution:**

```bash
# Option 1: Run as root
sudo -E python main.py

# Option 2: Use capabilities
sudo setcap 'cap_net_bind_service=+ep' $(which python3)

# Option 3: Use different port
export FASTPROXY_SSL_PORT=8443
python main.py
```

### Issue 4: "Domain doesn't point to this server"

**Problem:** DNS not configured correctly

**Solution:**

```bash
# Check DNS
dig +short example.com
# Should return your server IP

# If not, update DNS A record
# Point example.com to your server's IP
# Wait for DNS propagation (can take up to 48 hours)
```

### Issue 5: "Certificate provisioning failed"

**Problem:** Let's Encrypt validation failed

**Possible causes:**
- Port 80 not accessible from internet
- Firewall blocking port 80
- Domain not pointing to server
- Rate limit exceeded

**Solution:**

```bash
# Check firewall
sudo ufw status
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Check if port 80 is accessible from outside
curl http://your-server-ip

# Check certbot logs
sudo tail -f /var/log/letsencrypt/letsencrypt.log

# Test with dry-run
certbot certonly --standalone --dry-run -d example.com
```

### Issue 6: "Certificate expired"

**Problem:** Certificate not auto-renewed

**Solution:**

```bash
# Check certificate expiry
openssl x509 -in certs/example.com.crt -noout -dates

# Manually renew
sudo certbot renew

# Check auto-renewal timer (if using systemd)
sudo systemctl status certbot.timer
```

---

## 🔄 Fallback Modes

If auto-SSL fails, FastProxy falls back gracefully:

### Mode 1: Auto-SSL (Default)

```bash
export FASTPROXY_DOMAIN=example.com
export FASTPROXY_SSL_EMAIL=admin@example.com
python main.py
# ✅ Uses auto-SSL
```

### Mode 2: Manual SSL

```bash
export FASTPROXY_SSL_CERT=/path/to/cert.pem
export FASTPROXY_SSL_KEY=/path/to/key.pem
python main.py
# ✅ Uses manual certificates
```

### Mode 3: HTTP (No SSL)

```bash
python main.py
# ⚠️  Runs in HTTP mode (development only)
```

---

## 🆚 Comparison with Other Tools

| Feature | FastProxy Auto-SSL | Caddy | Traefik | Nginx |
|---------|-------------------|-------|---------|-------|
| Zero-config SSL | ✅ | ✅ | ✅ | ❌ |
| Auto-renewal | ✅ | ✅ | ✅ | ❌ Manual |
| Python-based | ✅ | ❌ Go | ❌ Go | ❌ C |
| Built-in auth | ✅ JWT + API keys | ❌ | ❌ | ❌ |
| Audit logging | ✅ | ❌ | ❌ | Limited |
| Rate limiting | ✅ | ✅ | ✅ | ✅ |
| Setup complexity | **2 env vars!** | Config file | Config file | Complex |

---

## 📊 How Auto-SSL Works

```
┌─────────┐
│  Start  │
└────┬────┘
     │
     ▼
┌────────────────────┐
│ Check if domain &  │
│ email are set?     │
└────┬────┬──────────┘
     │Yes │No
     │    └───────────────┐
     ▼                    ▼
┌────────────────────┐ ┌──────────┐
│ Check if valid     │ │ Manual   │
│ certificate exists?│ │ SSL mode │
└────┬────┬──────────┘ └──────────┘
     │Yes │No
     │    └───────────────┐
     ▼                    ▼
┌────────────────────┐ ┌────────────────────┐
│ Use existing cert  │ │ Request Let's      │
│                    │ │ Encrypt cert       │
└────┬───────────────┘ └────┬───────────────┘
     │                      │
     │                      ▼
     │                 ┌────────────────────┐
     │                 │ Start HTTP server  │
     │                 │ on port 80 for     │
     │                 │ ACME challenge     │
     │                 └────┬───────────────┘
     │                      │
     │                      ▼
     │                 ┌────────────────────┐
     │                 │ Let's Encrypt      │
     │                 │ validates domain   │
     │                 └────┬───────────────┘
     │                      │
     │                      ▼
     │                 ┌────────────────────┐
     │                 │ Save certificate   │
     │                 │ to ./certs/        │
     │                 └────┬───────────────┘
     │                      │
     └──────────┬───────────┘
                ▼
    ┌──────────────────────┐
    │ Start HTTPS server   │
    │ on port 443          │
    └──────┬───────────────┘
           │
           ▼
    ┌──────────────────────┐
    │ Start renewal thread │
    │ (checks daily)       │
    └──────────────────────┘
```

---

## 🎯 Best Practices

### 1. **Use Production Email**

```bash
# Bad
❌ export FASTPROXY_SSL_EMAIL=test@localhost

# Good
✅ export FASTPROXY_SSL_EMAIL=admin@example.com
```

### 2. **Test First with Dry Run**

```bash
# Test before getting real cert
certbot certonly --standalone --dry-run \
  -d example.com \
  --email admin@example.com
```

### 3. **Monitor Certificate Expiry**

```bash
# Check expiry date
openssl x509 -in certs/example.com.crt -noout -dates

# Check renewal status
sudo certbot certificates
```

### 4. **Set Up Monitoring**

```bash
# Monitor SSL certificate expiry
curl https://example.com | openssl s_client -connect example.com:443 \
  | openssl x509 -noout -dates
```

### 5. **Backup Certificates**

```bash
# Backup certificate directory
tar -czf certs-backup-$(date +%Y%m%d).tar.gz certs/

# Restore if needed
tar -xzf certs-backup-20250122.tar.gz
```

---

## ⚙️ Advanced Configuration

### Custom Certificate Directory

```bash
export FASTPROXY_DOMAIN=example.com
export FASTPROXY_SSL_EMAIL=admin@example.com
export FASTPROXY_CERT_DIR=/etc/fastproxy/certs

sudo mkdir -p /etc/fastproxy/certs
sudo -E python main.py
```

### Disable Auto-SSL

```bash
# Use manual certificates instead
export FASTPROXY_AUTO_SSL=false
export FASTPROXY_SSL_CERT=/path/to/cert.pem
export FASTPROXY_SSL_KEY=/path/to/key.pem

python main.py
```

### Custom Renewal Period

```python
# In code
from security.auto_ssl import AutoSSL

auto_ssl = AutoSSL(
    domain="example.com",
    email="admin@example.com"
)
auto_ssl.renewal_days = 60  # Renew 60 days before expiry
```

---

## 🔗 Related Documentation

- **Manual SSL Setup:** `/docs/SSL_TLS_SETUP.md`
- **Authentication:** `/docs/AUTHENTICATION.md`
- **Next.js Setup:** `/docs/NEXTJS_SETUP.md`
- **Let's Encrypt:** https://letsencrypt.org/

---

## ✅ Checklist

Before deploying with auto-SSL:

- [ ] Domain points to your server
- [ ] Port 80 is available (for ACME challenge)
- [ ] Port 443 is available (for HTTPS)
- [ ] certbot is installed
- [ ] Running as root (or have cap_net_bind_service)
- [ ] `FASTPROXY_DOMAIN` set
- [ ] `FASTPROXY_SSL_EMAIL` set
- [ ] Firewall allows ports 80 and 443
- [ ] Tested with `--dry-run` first
- [ ] Monitoring set up for certificate expiry

---

## 🎉 Example: Complete Setup

```bash
#!/bin/bash
# complete-autossl-setup.sh

# 1. Install certbot
sudo apt-get update
sudo apt-get install -y certbot

# 2. Configure FastProxy
cat > .env << EOF
FASTPROXY_DOMAIN=example.com
FASTPROXY_SSL_EMAIL=admin@example.com
FASTPROXY_ADMIN_USERNAME=admin
FASTPROXY_ADMIN_PASSWORD=$(openssl rand -base64 16)
FASTPROXY_JWT_SECRET=$(openssl rand -base64 32)
EOF

# 3. Test certificate provisioning (dry run)
sudo certbot certonly --standalone --dry-run \
  -d example.com \
  --email admin@example.com \
  --agree-tos \
  --non-interactive

# 4. Start FastProxy
source .env
sudo -E python main.py

echo "✅ FastProxy is running with auto-SSL!"
echo "   Access: https://example.com"
```

---

**Last Updated:** January 22, 2025  
**FastProxy Version:** 1.0.0  
**Auto-SSL Status:** ✅ Production Ready

