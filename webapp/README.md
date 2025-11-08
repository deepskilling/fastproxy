# FastProxy Management WebApp

Complete management interface for FastProxy with separate backend and frontend applications.

## Overview

This webapp provides a comprehensive management interface for FastProxy, allowing you to:

- Monitor proxy health and statistics
- Manage proxy routes (add, edit, delete)
- Create and manage API keys
- Edit configuration
- View and filter logs
- Control the proxy service

## Architecture

```
webapp/
├── backend/           # FastAPI backend (Python)
│   ├── main.py       # API server
│   ├── requirements.txt
│   └── README.md
│
└── frontend/         # Next.js frontend (React/TypeScript)
    ├── app/          # Pages and routes
    ├── components/   # React components
    ├── lib/          # Utilities
    └── README.md
```

## Quick Start

### Backend Setup

1. Navigate to backend directory:
```bash
cd webapp/backend
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the backend server:
```bash
python main.py
```

Backend will be available at `http://localhost:8001`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd webapp/frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create environment file:
```bash
echo "NEXT_PUBLIC_API_URL=http://localhost:8001" > .env.local
```

4. Run the development server:
```bash
npm run dev
```

Frontend will be available at `http://localhost:3000`

## Features

### 🎯 Dashboard
- Real-time system health monitoring
- Key performance metrics
- Recent activity feed
- Quick action shortcuts

### 🛣️ Route Management
- Visual route configuration
- Support for multiple HTTP methods
- Authentication requirements
- Rate limiting per route
- Easy add/edit/delete operations

### 🔑 API Key Management
- Generate secure API keys
- Set permissions (read, write, admin)
- Optional expiration dates
- One-time key display for security
- Easy key revocation

### ⚙️ Configuration Editor
- Direct configuration editing
- JSON format with validation
- Real-time syntax checking
- Backup and restore functionality

### 📝 Log Viewer
- Real-time log streaming
- Filter by log level (error, warning, info)
- Auto-refresh option
- Export logs for analysis
- Detailed log entries with context

## Technology Stack

### Backend
- **FastAPI**: Modern, fast Python web framework
- **Uvicorn**: ASGI server
- **Pydantic**: Data validation
- **PyYAML**: Configuration management
- **CORS Middleware**: Cross-origin support

### Frontend
- **Next.js 14**: React framework with App Router
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first styling
- **Axios**: HTTP client
- **Lucide React**: Beautiful icons
- **date-fns**: Date formatting

## API Endpoints

### Health & Status
- `GET /` - Health check
- `GET /api/health` - Detailed health status

### Configuration
- `GET /api/config` - Get configuration
- `PUT /api/config` - Update configuration

### Routes
- `GET /api/routes` - List all routes
- `POST /api/routes` - Add new route
- `DELETE /api/routes/{path}` - Delete route

### Statistics
- `GET /api/stats` - Get proxy statistics

### API Keys
- `GET /api/keys` - List API keys
- `POST /api/keys` - Create new API key
- `DELETE /api/keys/{id}` - Revoke API key

### Administration
- `POST /api/proxy/restart` - Restart proxy
- `GET /api/logs` - Get logs (with filtering)

## Authentication

All API endpoints (except health checks) require authentication via Bearer token:

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:8001/api/routes
```

## Development

### Running Both Services

You can run both services simultaneously:

Terminal 1 (Backend):
```bash
cd webapp/backend
python main.py
```

Terminal 2 (Frontend):
```bash
cd webapp/frontend
npm run dev
```

### Hot Reload

Both backend and frontend support hot reload:
- Backend: Uses uvicorn's `--reload` flag
- Frontend: Next.js built-in Fast Refresh

## Production Deployment

### Backend

1. Set production environment variables
2. Use a production ASGI server
3. Configure proper CORS origins
4. Enable HTTPS
5. Set up monitoring

```bash
uvicorn main:app --host 0.0.0.0 --port 8001 --workers 4
```

### Frontend

1. Build the production bundle:
```bash
npm run build
```

2. Start the production server:
```bash
npm start
```

Or deploy to platforms like:
- Vercel (recommended for Next.js)
- Netlify
- AWS Amplify
- Docker container

## Docker Support

Create a `docker-compose.yml` to run both services:

```yaml
version: '3.8'

services:
  backend:
    build: ./webapp/backend
    ports:
      - "8001:8001"
    environment:
      - BACKEND_PORT=8001
    volumes:
      - ../../config.yaml:/app/config.yaml

  frontend:
    build: ./webapp/frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://backend:8001
    depends_on:
      - backend
```

## Configuration

### Backend Configuration

Edit `backend/.env`:
```env
BACKEND_PORT=8001
JWT_SECRET_KEY=your-secret-key
CORS_ORIGINS=http://localhost:3000
```

### Frontend Configuration

Edit `frontend/.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8001
```

## Security Considerations

1. **Always use HTTPS in production**
2. **Set strong JWT secret keys**
3. **Configure restrictive CORS origins**
4. **Implement rate limiting**
5. **Regular security updates**
6. **Monitor access logs**
7. **Use secure session storage**
8. **Validate all inputs**

## Troubleshooting

### Backend won't start
- Check if port 8001 is available
- Verify Python dependencies are installed
- Check config.yaml path is correct

### Frontend won't connect to backend
- Verify backend is running
- Check NEXT_PUBLIC_API_URL in .env.local
- Verify CORS settings in backend

### Routes not updating
- Check FastProxy configuration
- Restart FastProxy service
- Verify file permissions

## Contributing

See individual README files in backend/ and frontend/ directories for component-specific contribution guidelines.

## License

Same as FastProxy main project

## Support

For issues and questions:
1. Check the documentation
2. Review troubleshooting section
3. Check existing issues
4. Create a new issue with detailed information

## Roadmap

- [ ] User authentication system
- [ ] Role-based access control
- [ ] Multi-tenant support
- [ ] Advanced analytics
- [ ] WebSocket support for real-time updates
- [ ] Audit log viewer
- [ ] Configuration version control
- [ ] Backup/restore functionality
- [ ] Dark mode support
- [ ] Mobile app

## Acknowledgments

Built with modern web technologies for the FastProxy project.

