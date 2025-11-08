# FastProxy Management API Backend

RESTful API backend for managing FastProxy configuration, monitoring, and administration.

## Features

- 🔧 **Configuration Management**: Update proxy routes and settings via API
- 📊 **Statistics & Monitoring**: Real-time proxy statistics and health checks
- 🔑 **API Key Management**: Create and manage API keys
- 📝 **Log Access**: Query and filter proxy logs
- 🔒 **Secure**: JWT authentication and CORS protection

## Quick Start

### Installation

```bash
cd webapp/backend
pip install -r requirements.txt
```

### Configuration

1. Copy the environment template:
```bash
cp .env.example .env
```

2. Edit `.env` and set your configuration values

### Running the Server

```bash
# Development mode with auto-reload
python main.py

# Or using uvicorn directly
uvicorn main:app --reload --port 8001
```

The API will be available at `http://localhost:8001`

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8001/docs`
- ReDoc: `http://localhost:8001/redoc`

## API Endpoints

### Health & Status
- `GET /` - Basic health check
- `GET /api/health` - Detailed health check

### Configuration
- `GET /api/config` - Get current configuration
- `PUT /api/config` - Update configuration

### Routes Management
- `GET /api/routes` - List all proxy routes
- `POST /api/routes` - Add new route
- `DELETE /api/routes/{path}` - Delete route

### Statistics
- `GET /api/stats` - Get proxy statistics

### API Keys
- `GET /api/keys` - List API keys
- `POST /api/keys` - Create new API key
- `DELETE /api/keys/{key_id}` - Revoke API key

### Administration
- `POST /api/proxy/restart` - Restart proxy service
- `GET /api/logs` - Get recent logs

## Authentication

All endpoints (except health checks) require authentication via Bearer token:

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8001/api/routes
```

## Development

### Project Structure

```
backend/
├── main.py              # Main FastAPI application
├── requirements.txt     # Python dependencies
├── .env.example        # Environment variables template
└── README.md           # This file
```

### Adding New Endpoints

1. Define Pydantic models for request/response
2. Add endpoint handler function
3. Implement business logic
4. Update documentation

## Security Considerations

- Always use HTTPS in production
- Set strong JWT secret key
- Rotate API keys regularly
- Implement rate limiting
- Review CORS origins

## License

Same as FastProxy main project

