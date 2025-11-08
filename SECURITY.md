# Security Policy

## Supported Versions

We release patches for security vulnerabilities in the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 2.0.x   | :white_check_mark: |
| 1.x.x   | :x:                |

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report them via email to: **[security@yourdomain.com]**

You should receive a response within 48 hours. If for some reason you do not, please follow up via email to ensure we received your original message.

Please include the following information (as much as you can provide) to help us better understand the nature and scope of the possible issue:

* Type of issue (e.g. buffer overflow, SQL injection, cross-site scripting, etc.)
* Full paths of source file(s) related to the manifestation of the issue
* The location of the affected source code (tag/branch/commit or direct URL)
* Any special configuration required to reproduce the issue
* Step-by-step instructions to reproduce the issue
* Proof-of-concept or exploit code (if possible)
* Impact of the issue, including how an attacker might exploit it

This information will help us triage your report more quickly.

## Security Measures

FastProxy implements several security measures:

### 1. Authentication & Authorization
- HTTP Basic Auth for admin endpoints
- JWT token support
- API key management
- Role-based access control (RBAC) ready

### 2. Input Validation
- Request validation
- URL validation (SSRF protection)
- Request body size limits
- Rate limiting

### 3. Security Headers
- Content Security Policy (CSP)
- X-Frame-Options
- X-Content-Type-Options
- Strict-Transport-Security (HSTS)

### 4. Network Security
- CORS configuration
- Private IP blocking (optional)
- SSL/TLS support (Let's Encrypt)
- Certificate management

### 5. Audit Logging
- Request logging
- Admin action logging
- SQLite audit database
- Configurable log retention

### 6. Docker Security
- Non-root user (frontend)
- Minimal base images
- Read-only volumes option
- Health checks
- Network isolation

## Best Practices for Deployment

### Production Deployment

1. **Enable HTTPS**
   ```yaml
   auto_https:
     enabled: true
     domain: "yourdomain.com"
     email: "admin@yourdomain.com"
   ```

2. **Set Strong Secrets**
   ```bash
   # Generate strong JWT secret
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

3. **Configure CORS Properly**
   ```yaml
   cors:
     allow_origins: 
       - "https://yourdomain.com"
     allow_credentials: true
   ```

4. **Enable Rate Limiting**
   ```yaml
   rate_limit:
     requests_per_minute: 100
   ```

5. **Restrict Admin Access**
   - Use environment variables for credentials
   - Don't commit secrets to git
   - Rotate credentials regularly

6. **Keep Updated**
   ```bash
   # Check for updates
   git pull
   docker compose pull
   ```

7. **Monitor Logs**
   ```bash
   # Check audit logs regularly
   docker compose logs -f fastproxy
   ```

8. **Backup Data**
   ```bash
   # Backup volumes regularly
   docker run --rm -v fastproxy-audit:/data \
     -v $(pwd):/backup alpine \
     tar czf /backup/audit-backup.tar.gz /data
   ```

### Network Security

1. **Firewall Rules**
   - Only expose necessary ports (80, 443)
   - Block direct access to backend services
   - Use private networks for service communication

2. **SSL/TLS**
   - Always use HTTPS in production
   - Enable HSTS
   - Use strong ciphers
   - Rotate certificates before expiry

3. **Private IPs**
   - Configure `allow_private_ips` based on your use case
   - Block if proxying to public internet
   - Allow if proxying to internal services

### Application Security

1. **Environment Variables**
   - Never commit `.env` files
   - Use secrets management (Vault, etc.)
   - Rotate secrets regularly

2. **Dependencies**
   - Keep Python packages updated
   - Check for vulnerabilities: `pip-audit`
   - Use fixed versions in production

3. **Access Control**
   - Implement authentication on all admin endpoints
   - Use API keys for service-to-service
   - Implement rate limiting per user/IP

## Vulnerability Disclosure Policy

We believe in responsible disclosure of security vulnerabilities. We ask that:

1. **Provide us reasonable time** to investigate and mitigate before public disclosure
2. **Make a good faith effort** to avoid privacy violations, data destruction, and service interruption
3. **Do not exploit** a security issue for any purpose other than verification
4. **Do not publicly disclose** the vulnerability until we've had a chance to address it

In return, we commit to:

1. **Respond promptly** to your report (within 48 hours)
2. **Keep you informed** of our progress fixing the issue
3. **Credit you** in release notes (if desired) when the issue is fixed
4. **Not pursue legal action** against researchers who follow this policy

## Security Hall of Fame

We recognize and thank security researchers who have responsibly disclosed vulnerabilities:

<!-- This section will be updated as researchers report issues -->

*Be the first to responsibly disclose a vulnerability!*

## Contact

For security issues: **[security@yourdomain.com]**

For general questions: **[support@yourdomain.com]**

PGP Key: [Link to PGP public key]

---

**Thank you for helping keep FastProxy and its users safe!** 🔒

