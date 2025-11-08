# FastProxy Configuration Examples

This directory contains example configurations for different use cases.

## Files

### Configuration Files

- **`config-basic.yaml`** - Simple configuration for local development
- **`config-microservices.yaml`** - Configuration for proxying multiple microservices
- **`config-production.yaml`** - Production-ready configuration with security best practices

### Docker Compose

- **`docker-compose-simple.yml`** - Minimal Docker Compose example

## Usage

### Using Configuration Examples

Copy the example that fits your use case:

```bash
# For local development
cp examples/config-basic.yaml config.yaml

# For microservices
cp examples/config-microservices.yaml config.yaml

# For production
cp examples/config-production.yaml config.yaml
```

Then edit the file to match your environment:

```bash
nano config.yaml
```

### Using Docker Compose Examples

```bash
# Copy the example
cp examples/docker-compose-simple.yml docker-compose.yml

# Edit to add your services
nano docker-compose.yml

# Start services
docker compose up -d
```

## Configuration Scenarios

### Scenario 1: Local Development

**Use**: `config-basic.yaml`

Features:
- No HTTPS (faster setup)
- Relaxed CORS
- Moderate rate limiting
- Debug logging

```bash
cp examples/config-basic.yaml config.yaml
python main.py
```

### Scenario 2: Microservices Gateway

**Use**: `config-microservices.yaml`

Features:
- Multiple service routes
- Path-based routing
- HTTPS enabled
- Higher rate limits

```bash
cp examples/config-microservices.yaml config.yaml
# Update service URLs
python main.py
```

### Scenario 3: Production Deployment

**Use**: `config-production.yaml`

Features:
- HTTPS with Let's Encrypt
- Strict CORS
- Conservative rate limiting
- Warning-level logging

```bash
cp examples/config-production.yaml config.yaml
# Set your domain and email
python main.py
```

## Customization Tips

### Adding Routes

```yaml
routes:
  - path: /newservice
    target: http://newservice:8080
    strip_path: true
```

### Adjusting Rate Limits

```yaml
rate_limit:
  requests_per_minute: 1000  # Increase for high traffic
```

### Configuring CORS

```yaml
cors:
  allow_origins:
    - "https://yourdomain.com"  # Add your domains
  allow_credentials: true
```

### HTTPS Setup

```yaml
auto_https:
  enabled: true
  domain: "yourdomain.com"  # Your domain
  email: "admin@yourdomain.com"  # Your email
  staging: false  # Use false for production certs
```

## Testing Configurations

```bash
# Test configuration validity
python -c "import yaml; yaml.safe_load(open('config.yaml'))"

# Start with your config
python main.py

# Test a route
curl http://localhost:8000/api/test
```

## More Examples

For more examples, see:
- [Main Documentation](../README.md)
- [Quickstart Guide](../docs/guides/QUICKSTART.md)
- [Docker Documentation](../docker/README.md)

## Need Help?

- Read the [documentation](../README.md)
- Check [troubleshooting guide](../docs/guides/QUICKSTART.md#troubleshooting)
- Open an [issue](https://github.com/yourusername/fastproxy/issues)
- Start a [discussion](https://github.com/yourusername/fastproxy/discussions)

