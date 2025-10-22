# 🔒 SSL/TLS Configuration Guide

Complete guide to setting up HTTPS for FastProxy in development, staging, and production environments.

---

## 📋 Table of Contents

1. [Why HTTPS?](#why-https)
2. [Development Setup (Self-Signed)](#development-setup-self-signed)
3. [Production Setup (Let's Encrypt)](#production-setup-lets-encrypt)
4. [Production Setup (Reverse Proxy)](#production-setup-reverse-proxy)
5. [Testing HTTPS](#testing-https)
6. [Troubleshooting](#troubleshooting)

---

## Why HTTPS?

### ⚠️ **Running HTTP in production is DANGEROUS!**

Without HTTPS:
- ❌ Credentials sent in **plain text**
- ❌ API keys visible in network traffic
- ❌ Session tokens can be stolen
- ❌ Data can be modified in transit (MITM attacks)
- ❌ No client verification

With HTTPS:
- ✅ All traffic encrypted (TLS 1.2+)
- ✅ Credentials protected
- ✅ Data integrity verified
- ✅ Server identity authenticated
- ✅ Modern browsers won't block

---

## Development Setup (Self-Signed)

### Quick Start

FastProxy includes a built-in self-signed certificate generator.

```bash
# Step 1: Generate certificate
python ssl_config.py

# Output:
# ✅ Generated self-signed certificate:
#    Certificate: certs/cert.pem
#    Private Key: certs/key.pem
# ⚠️  Self-signed certificate for DEVELOPMENT ONLY!
```

```bash
# Step 2: Configure environment
export FASTPROXY_SSL_CERT=certs/cert.pem
export FASTPROXY_SSL_KEY=certs/key.pem
export FASTPROXY_SSL_PORT=8443

# Step 3: Run server
python main.py

# Output:
# 🔒 Starting FastProxy with HTTPS on port 8443
```

```bash
# Step 4: Test
curl -k https://localhost:8443/health
# Note: -k flag skips certificate verification (self-signed)
```

### Manual Certificate Generation

If you prefer OpenSSL:

```bash
# Create certs directory
mkdir -p certs

# Generate private key
openssl genrsa -out certs/key.pem 2048

# Generate self-signed certificate (valid 365 days)
openssl req -new -x509 -key certs/key.pem -out certs/cert.pem -days 365 \
  -subj "/CN=localhost"

# Set permissions
chmod 600 certs/key.pem
chmod 644 certs/cert.pem
```

### Docker with Self-Signed Certificate

```dockerfile
# docker/Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Generate self-signed certificate
COPY ssl_config.py .
RUN python ssl_config.py

COPY . .

ENV FASTPROXY_SSL_CERT=certs/cert.pem
ENV FASTPROXY_SSL_KEY=certs/key.pem
ENV FASTPROXY_SSL_PORT=8443

EXPOSE 8443

CMD ["python", "main.py"]
```

### Browser Trust (Development)

To avoid browser warnings:

#### macOS

```bash
# Add certificate to keychain
sudo security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain certs/cert.pem
```

#### Linux

```bash
# Copy certificate to trusted store
sudo cp certs/cert.pem /usr/local/share/ca-certificates/fastproxy.crt
sudo update-ca-certificates
```

#### Windows

```powershell
# Import certificate to Trusted Root
Import-Certificate -FilePath certs\cert.pem -CertStoreLocation Cert:\LocalMachine\Root
```

---

## Production Setup (Let's Encrypt)

### Prerequisites

- Domain name pointing to your server
- Port 80 and 443 open in firewall
- Root or sudo access

### Method 1: Certbot (Standalone)

```bash
# Step 1: Install Certbot
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install certbot

# CentOS/RHEL
sudo yum install certbot

# macOS
brew install certbot
```

```bash
# Step 2: Stop FastProxy (if running on port 80)
# Certbot needs port 80 for verification

# Step 3: Get certificate
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# Follow prompts:
# - Enter email address
# - Agree to Terms of Service
# - Choose whether to share email with EFF

# Certificates saved to:
# /etc/letsencrypt/live/yourdomain.com/fullchain.pem
# /etc/letsencrypt/live/yourdomain.com/privkey.pem
```

```bash
# Step 4: Configure FastProxy
export FASTPROXY_SSL_CERT=/etc/letsencrypt/live/yourdomain.com/fullchain.pem
export FASTPROXY_SSL_KEY=/etc/letsencrypt/live/yourdomain.com/privkey.pem
export FASTPROXY_SSL_PORT=443

# Step 5: Run as root (port 443 requires root)
sudo -E python main.py
```

```bash
# Step 6: Set up auto-renewal
sudo certbot renew --dry-run  # Test renewal

# Add to crontab for auto-renewal (daily check)
sudo crontab -e
# Add line:
0 12 * * * /usr/bin/certbot renew --quiet
```

### Method 2: Certbot (Webroot)

If FastProxy is already running:

```bash
# Step 1: Create webroot directory
mkdir -p /var/www/certbot

# Step 2: Configure FastProxy to serve .well-known directory
# Add route in config.yaml:
routes:
  - path: /.well-known/
    target: file:///var/www/certbot

# Step 3: Get certificate
sudo certbot certonly --webroot -w /var/www/certbot \
  -d yourdomain.com -d www.yourdomain.com

# Step 4: Configure and restart
export FASTPROXY_SSL_CERT=/etc/letsencrypt/live/yourdomain.com/fullchain.pem
export FASTPROXY_SSL_KEY=/etc/letsencrypt/live/yourdomain.com/privkey.pem
export FASTPROXY_SSL_PORT=443

sudo -E python main.py
```

### Systemd Service with Let's Encrypt

```ini
# /etc/systemd/system/fastproxy.service
[Unit]
Description=FastProxy Server
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/fastproxy
Environment="FASTPROXY_SSL_CERT=/etc/letsencrypt/live/yourdomain.com/fullchain.pem"
Environment="FASTPROXY_SSL_KEY=/etc/letsencrypt/live/yourdomain.com/privkey.pem"
Environment="FASTPROXY_SSL_PORT=443"
ExecStart=/usr/bin/python3 main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable fastproxy
sudo systemctl start fastproxy

# Check status
sudo systemctl status fastproxy
```

---

## Production Setup (Reverse Proxy) **⭐ RECOMMENDED**

Using Nginx or Traefik as a reverse proxy is the **best practice** for production.

### Option A: Nginx

#### Install Nginx

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install nginx

# CentOS/RHEL
sudo yum install nginx
```

#### Get Let's Encrypt Certificate

```bash
# Install certbot for Nginx
sudo apt-get install python3-certbot-nginx

# Get certificate and auto-configure Nginx
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

#### Configure Nginx

```nginx
# /etc/nginx/sites-available/fastproxy
upstream fastproxy {
    server 127.0.0.1:8000;
    keepalive 32;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;
    
    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    # Modern SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';
    ssl_prefer_server_ciphers off;
    
    # HSTS (optional but recommended)
    add_header Strict-Transport-Security "max-age=63072000" always;
    
    # Proxy settings
    location / {
        proxy_pass http://fastproxy;
        proxy_http_version 1.1;
        
        # Headers
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Connection "";
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Health check endpoint (no auth required)
    location /health {
        proxy_pass http://fastproxy;
        access_log off;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/fastproxy /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

#### Run FastProxy (HTTP mode, behind Nginx)

```bash
# No SSL needed - Nginx handles it
python main.py  # Runs on http://localhost:8000
```

### Option B: Traefik

Traefik automatically handles Let's Encrypt certificates.

#### docker-compose.yml

```yaml
version: '3.8'

services:
  traefik:
    image: traefik:v2.10
    command:
      - "--api.insecure=true"
      - "--providers.docker=true"
      - "--entrypoints.web.address=:80"
      - "--entrypoints.websecure.address=:443"
      - "--certificatesresolvers.letsencrypt.acme.email=your@email.com"
      - "--certificatesresolvers.letsencrypt.acme.storage=/letsencrypt/acme.json"
      - "--certificatesresolvers.letsencrypt.acme.httpchallenge.entrypoint=web"
    ports:
      - "80:80"
      - "443:443"
      - "8080:8080"  # Traefik dashboard
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - ./letsencrypt:/letsencrypt
    restart: unless-stopped

  fastproxy:
    build: ./docker
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.fastproxy.rule=Host(`yourdomain.com`)"
      - "traefik.http.routers.fastproxy.entrypoints=websecure"
      - "traefik.http.routers.fastproxy.tls.certresolver=letsencrypt"
      - "traefik.http.services.fastproxy.loadbalancer.server.port=8000"
      # HTTP to HTTPS redirect
      - "traefik.http.routers.fastproxy-http.rule=Host(`yourdomain.com`)"
      - "traefik.http.routers.fastproxy-http.entrypoints=web"
      - "traefik.http.routers.fastproxy-http.middlewares=redirect-to-https"
      - "traefik.http.middlewares.redirect-to-https.redirectscheme.scheme=https"
    environment:
      - FASTPROXY_ADMIN_USERNAME=admin
      - FASTPROXY_ADMIN_PASSWORD=${ADMIN_PASSWORD}
      - FASTPROXY_JWT_SECRET=${JWT_SECRET}
    restart: unless-stopped

networks:
  default:
    name: fastproxy-network
```

```bash
# Start services
docker-compose up -d

# Traefik automatically:
# - Gets Let's Encrypt certificate
# - Renews certificates automatically
# - Redirects HTTP to HTTPS
```

---

## Testing HTTPS

### Test with curl

```bash
# Test health endpoint
curl https://yourdomain.com/health

# Test with verbose output (shows SSL handshake)
curl -v https://yourdomain.com/health

# Test certificate
curl --head https://yourdomain.com
```

### Test SSL Configuration

```bash
# Check certificate details
openssl s_client -connect yourdomain.com:443 -servername yourdomain.com

# Test SSL strength (using testssl.sh)
git clone https://github.com/drwetter/testssl.sh.git
cd testssl.sh
./testssl.sh yourdomain.com
```

### Online SSL Test

- **SSL Labs:** https://www.ssllabs.com/ssltest/
- Enter your domain
- Wait for scan
- Target: A+ rating

### Test Authentication Over HTTPS

```bash
# Login with JWT
curl -X POST https://yourdomain.com/auth/login \
  -u admin:password

# Use API key
curl https://yourdomain.com/admin/status \
  -H "X-API-Key: fpx_your_key"
```

---

## Troubleshooting

### "Certificate not found"

```bash
# Check file exists
ls -la /etc/letsencrypt/live/yourdomain.com/

# Check permissions
sudo chmod 644 /etc/letsencrypt/live/yourdomain.com/fullchain.pem
sudo chmod 600 /etc/letsencrypt/live/yourdomain.com/privkey.pem
```

### "Permission denied" (Port 443)

```bash
# Option 1: Run as root
sudo -E python main.py

# Option 2: Allow binding to privileged ports
sudo setcap 'cap_net_bind_service=+ep' $(which python3)

# Option 3: Use reverse proxy (Nginx) - RECOMMENDED
```

### "Certificate has expired"

```bash
# Renew Let's Encrypt certificate
sudo certbot renew

# Check expiration
sudo certbot certificates
```

### "SSL handshake failed"

```bash
# Check TLS version
openssl s_client -connect yourdomain.com:443 -tls1_2

# Check cipher suites
openssl s_client -connect yourdomain.com:443 -cipher 'HIGH:!aNULL'
```

### "Mixed content warnings" (Browser)

Ensure all resources loaded over HTTPS:
```bash
# Bad
❌ http://yourdomain.com/api/data

# Good
✅ https://yourdomain.com/api/data
```

---

## Security Checklist

### ✅ Production SSL/TLS Checklist

- [ ] Using valid SSL certificate (not self-signed)
- [ ] Certificate from trusted CA (Let's Encrypt, DigiCert, etc.)
- [ ] TLS 1.2+ enabled (TLS 1.0/1.1 disabled)
- [ ] Strong cipher suites configured
- [ ] HSTS header enabled
- [ ] HTTP redirects to HTTPS
- [ ] Certificate auto-renewal configured
- [ ] Monitoring certificate expiration
- [ ] Private key protected (chmod 600)
- [ ] Using reverse proxy for SSL termination
- [ ] Tested with SSL Labs (A+ rating)

---

## Quick Reference

### Environment Variables

```bash
# SSL/TLS Configuration
FASTPROXY_SSL_CERT=/path/to/cert.pem
FASTPROXY_SSL_KEY=/path/to/key.pem
FASTPROXY_SSL_PORT=8443  # Default: 8443
FASTPROXY_SSL_CA_BUNDLE=/path/to/ca-bundle.pem  # Optional
```

### Common Ports

| Port | Protocol | Usage |
|------|----------|-------|
| 80 | HTTP | Redirect to HTTPS |
| 443 | HTTPS | Production |
| 8000 | HTTP | Development (behind reverse proxy) |
| 8443 | HTTPS | Development (direct SSL) |

### Certificate Locations

| Provider | Certificate Path |
|----------|------------------|
| Let's Encrypt | `/etc/letsencrypt/live/domain/fullchain.pem` |
| Custom | User-defined location |
| Self-signed | `./certs/cert.pem` |

---

## Additional Resources

- **Let's Encrypt:** https://letsencrypt.org/
- **SSL Labs Test:** https://www.ssllabs.com/ssltest/
- **Mozilla SSL Config:** https://ssl-config.mozilla.org/
- **Certbot Docs:** https://certbot.eff.org/

---

**Last Updated:** 2025-01-22  
**FastProxy Version:** 1.0.0

