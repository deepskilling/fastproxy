# FastProxy Project Organization

This document describes the organization and structure of the FastProxy repository.

## 📁 Repository Structure

```
fastproxy/
│
├── .github/                    # GitHub-specific files
│   ├── workflows/             # GitHub Actions CI/CD
│   ├── ISSUE_TEMPLATE/        # Issue templates
│   ├── FUNDING.yml            # Sponsorship info
│   └── dependabot.yml         # Dependency updates
│
├── docs/                       # Documentation
│   ├── guides/                # User guides
│   ├── images/                # Documentation images
│   ├── README.md              # Documentation index
│   ├── DEMO_IMPLEMENTATION_SUMMARY.md
│   └── COMPLETE_IMPLEMENTATION_SUMMARY.md
│
├── examples/                   # Configuration examples
│   ├── config-basic.yaml
│   ├── config-microservices.yaml
│   ├── config-production.yaml
│   └── docker-compose-simple.yml
│
├── docker/                     # Docker configurations
│   ├── Dockerfile.fastproxy
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   ├── docker-compose.yml
│   ├── docker-compose.demo.yml
│   ├── docker-start.sh
│   ├── Makefile
│   └── README.md
│
├── webapp/                     # Management WebApp
│   ├── backend/               # FastAPI backend
│   ├── frontend/              # Next.js frontend
│   ├── README.md
│   └── DEMO_ARCHITECTURE.md
│
├── proxy/                      # Core proxy logic
├── audit/                      # Audit logging
├── admin/                      # Admin API
├── auth/                       # Authentication
├── security/                   # Security features
├── cert_manager/              # SSL/TLS management
├── tests/                      # Test suite
│
├── README.md                   # Main README
├── QUICKSTART.md → docs/guides/ # Quickstart guide
├── CONTRIBUTING.md            # Contributing guidelines
├── CODE_OF_CONDUCT.md         # Code of conduct
├── SECURITY.md                # Security policy
├── CHANGELOG.md               # Version history
├── LICENSE                    # MIT License
│
├── main.py                    # Application entry point
├── config.yaml                # Production config
├── config.demo.yaml           # Demo config
├── requirements.txt           # Python dependencies
├── Makefile                   # Project commands
├── start-demo.sh              # Demo startup script
│
└── .gitignore, .dockerignore, etc.
```

## 📂 Directory Purposes

### Root Level

**Documentation Files**:
- `README.md` - Main project documentation
- `CONTRIBUTING.md` - How to contribute
- `CODE_OF_CONDUCT.md` - Community guidelines
- `SECURITY.md` - Security policy
- `CHANGELOG.md` - Version history
- `LICENSE` - MIT License

**Configuration Files**:
- `config.yaml` - Production configuration
- `config.demo.yaml` - Demo configuration
- `requirements.txt` - Python dependencies
- `Makefile` - Project commands

**Scripts**:
- `start-demo.sh` - Start demo environment
- `start.sh` - Start production

### `.github/` - GitHub Integration

Contains GitHub-specific configurations:

- **workflows/** - CI/CD pipelines
  - `ci.yml` - Continuous Integration
  - `docker-publish.yml` - Docker image publishing
  
- **ISSUE_TEMPLATE/** - Issue templates
  - `bug_report.md` - Bug report template
  - `feature_request.md` - Feature request template
  - `config.yml` - Template configuration
  
- **Other**:
  - `FUNDING.yml` - Sponsorship information
  - `dependabot.yml` - Automated dependency updates
  - `pull_request_template.md` - PR template

### `docs/` - Documentation

Comprehensive project documentation:

- **guides/** - User guides and tutorials
  - `QUICKSTART.md` - Getting started guide
  - `DEMO_QUICK_REFERENCE.md` - Quick reference card
  
- **images/** - Documentation images and diagrams

- **Root docs**:
  - `README.md` - Documentation index
  - `DEMO_IMPLEMENTATION_SUMMARY.md` - Demo overview
  - `COMPLETE_IMPLEMENTATION_SUMMARY.md` - Full summary

### `examples/` - Configuration Examples

Real-world configuration examples:

- `config-basic.yaml` - Basic setup
- `config-microservices.yaml` - Microservices gateway
- `config-production.yaml` - Production configuration
- `docker-compose-simple.yml` - Simple Docker setup
- `README.md` - Examples guide

### `docker/` - Docker Support

Complete Docker implementation:

- **Dockerfiles**:
  - `Dockerfile.fastproxy` - Main proxy image
  - `Dockerfile.backend` - Backend API image
  - `Dockerfile.frontend` - Frontend UI image

- **Compose Files**:
  - `docker-compose.yml` - Production stack
  - `docker-compose.demo.yml` - Demo stack

- **Tools**:
  - `docker-start.sh` - Interactive startup
  - `Makefile` - Docker commands
  - `.dockerignore` - Build optimization

- **Documentation**:
  - `README.md` - Docker guide
  - `DOCKER_QUICKSTART.md` - Quick start
  - `DOCKER_IMPLEMENTATION_SUMMARY.md` - Summary

### `webapp/` - Management Application

Web-based management interface:

- **backend/** - FastAPI REST API
  - `main.py` - API server
  - `requirements.txt` - Dependencies
  - `README.md` - Backend docs

- **frontend/** - Next.js UI
  - `app/` - Pages and routes
  - `components/` - React components
  - `lib/` - Utilities
  - `README.md` - Frontend docs

- **Documentation**:
  - `README.md` - WebApp overview
  - `DEMO_ARCHITECTURE.md` - Architecture

### Core Modules

**Application Code**:
- `main.py` - Application entry point
- `proxy/` - Core proxy logic
- `audit/` - Audit logging system
- `admin/` - Admin API endpoints
- `auth/` - Authentication
- `security/` - Security features
- `cert_manager/` - SSL/TLS management

**Tests**:
- `tests/` - Test suite
- `pytest.ini` - Pytest configuration

## 🏷️ File Naming Conventions

### Documentation
- `README.md` - Main documentation in each directory
- `UPPERCASE.md` - Important project files (CONTRIBUTING, etc.)
- `kebab-case.md` - Other documentation files

### Code Files
- `snake_case.py` - Python modules
- `PascalCase.tsx` - React components
- `camelCase.ts` - TypeScript utilities

### Configuration
- `kebab-case.yaml` - Configuration files
- `kebab-case.yml` - Compose files
- `.filename` - Hidden config files

### Scripts
- `kebab-case.sh` - Shell scripts
- `Makefile` - Build automation

## 📋 Best Practices

### Adding New Features

1. **Code**: Add to appropriate module directory
2. **Tests**: Add tests in `tests/`
3. **Docs**: Update relevant documentation
4. **Examples**: Add example if applicable
5. **Changelog**: Update `CHANGELOG.md`

### Documentation

- Keep README.md in each directory updated
- Add examples for complex features
- Include diagrams where helpful
- Link between related docs

### Configuration Examples

- Add to `examples/` directory
- Include inline comments
- Provide README explaining use case
- Test before committing

### Docker Changes

- Update relevant Dockerfile
- Test with docker-compose
- Update Docker documentation
- Verify image sizes

## 🔍 Finding What You Need

### For Users
- **Getting Started**: `docs/guides/QUICKSTART.md`
- **Configuration**: `examples/` directory
- **Docker**: `docker/README.md`
- **Troubleshooting**: `docs/guides/QUICKSTART.md#troubleshooting`

### For Developers
- **Contributing**: `CONTRIBUTING.md`
- **Architecture**: `webapp/DEMO_ARCHITECTURE.md`
- **API Docs**: `webapp/backend/README.md`
- **Frontend**: `webapp/frontend/README.md`

### For DevOps
- **Deployment**: `docker/README.md`
- **Configuration**: `examples/config-production.yaml`
- **Security**: `SECURITY.md`
- **Monitoring**: `docs/README.md#monitoring`

## 🔄 Maintenance

### Regular Updates

- **Dependencies**: Automated via Dependabot
- **Documentation**: Update with features
- **Examples**: Keep current with features
- **Changelog**: Update with each release

### Cleanup

- Remove obsolete files
- Update broken links
- Verify all examples work
- Check for outdated information

## 📊 Repository Health

### Badges (in README.md)

- Build status
- Test coverage
- License
- Version
- Docker pulls

### GitHub Features

- **Actions**: CI/CD workflows
- **Issues**: Bug tracking
- **Discussions**: Community Q&A
- **Projects**: Roadmap
- **Releases**: Version management
- **Security**: Vulnerability scanning

## 🎯 Goals

This organization aims to:

1. **Easy Navigation**: Find what you need quickly
2. **Clear Structure**: Logical file organization
3. **Good Documentation**: Comprehensive guides
4. **Easy Contribution**: Clear guidelines
5. **Professional**: GitHub best practices

---

**Questions?** See [Contributing Guide](../CONTRIBUTING.md) or open an issue.

