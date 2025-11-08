# Contributing to FastProxy

First off, thank you for considering contributing to FastProxy! It's people like you that make FastProxy such a great tool.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Documentation](#documentation)

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to [project email].

## Getting Started

### Ways to Contribute

- 🐛 **Bug Reports**: Found a bug? Let us know!
- ✨ **Feature Requests**: Have an idea? We'd love to hear it!
- 📝 **Documentation**: Help improve our docs
- 💻 **Code**: Fix bugs or add features
- 🧪 **Testing**: Write or improve tests
- 🎨 **Design**: Improve UI/UX
- 🌍 **Translations**: Help internationalize FastProxy

## How to Contribute

### Reporting Bugs

Before creating bug reports, please check existing issues. When you create a bug report, include as many details as possible:

- Use a clear and descriptive title
- Describe the exact steps to reproduce the problem
- Provide specific examples
- Describe the behavior you observed and what you expected
- Include logs, screenshots, or config files
- Note your environment (OS, Python version, etc.)

**Use the bug report template** when creating an issue.

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion:

- Use a clear and descriptive title
- Provide a detailed description of the suggested enhancement
- Explain why this enhancement would be useful
- List any alternative solutions you've considered

**Use the feature request template** when creating an issue.

## Development Setup

### Prerequisites

- Python 3.9 or higher
- Node.js 18 or higher (for webapp)
- Docker (optional, for testing)
- Git

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:

```bash
git clone https://github.com/YOUR-USERNAME/fastproxy.git
cd fastproxy
```

3. Add the upstream repository:

```bash
git remote add upstream https://github.com/ORIGINAL-OWNER/fastproxy.git
```

### Set Up Development Environment

#### Option 1: Native Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install
```

#### Option 2: Docker Setup

```bash
cd docker
docker compose -f docker-compose.demo.yml up -d
```

### Running FastProxy

```bash
# Native
./start-demo.sh

# Docker
cd docker && make demo
```

## Pull Request Process

### Before Submitting

1. **Create a branch** for your changes:
   ```bash
   git checkout -b feature/amazing-feature
   ```

2. **Make your changes** following our coding standards

3. **Test your changes**:
   ```bash
   pytest
   ./start-demo.sh  # Test the demo
   cd docker && make test  # Test Docker setup
   ```

4. **Update documentation** if needed

5. **Commit your changes**:
   ```bash
   git add .
   git commit -m "feat: add amazing feature"
   ```
   
   Follow [Conventional Commits](https://www.conventionalcommits.org/):
   - `feat:` new feature
   - `fix:` bug fix
   - `docs:` documentation changes
   - `style:` formatting changes
   - `refactor:` code refactoring
   - `test:` adding tests
   - `chore:` maintenance tasks

6. **Push to your fork**:
   ```bash
   git push origin feature/amazing-feature
   ```

### Submitting the Pull Request

1. Go to your fork on GitHub
2. Click "New Pull Request"
3. Fill out the PR template
4. Link any related issues
5. Wait for review

### PR Review Process

- Maintainers will review your PR
- Address any requested changes
- Once approved, your PR will be merged
- Your contribution will be included in the next release!

## Coding Standards

### Python

- Follow [PEP 8](https://peps.python.org/pep-0008/)
- Use type hints where appropriate
- Maximum line length: 120 characters
- Use descriptive variable names

```python
# Good
def calculate_request_rate(requests: int, time_window: int) -> float:
    """Calculate requests per second."""
    return requests / time_window

# Bad
def calc(r, t):
    return r/t
```

### TypeScript/React

- Follow the existing code style
- Use functional components with hooks
- Use TypeScript types properly
- Extract reusable components

### General

- Write clear, self-documenting code
- Add comments for complex logic
- Keep functions small and focused
- Avoid deep nesting (max 3-4 levels)

### Code Formatting

We use automated formatters:

```bash
# Python
black .
isort .
flake8 .

# TypeScript (in webapp/frontend)
npm run lint
npm run format
```

## Testing

### Writing Tests

- Write tests for new features
- Update tests for bug fixes
- Aim for >80% code coverage

### Running Tests

```bash
# Python tests
pytest
pytest --cov=. --cov-report=html

# Integration tests
./start-demo.sh  # Manual testing
cd docker && make test  # Docker tests
```

### Test Structure

```python
def test_route_matching():
    """Test that routes are matched correctly."""
    # Arrange
    router = Router()
    router.add_route("/api", "http://backend:8001")
    
    # Act
    match = router.match_route("/api/users")
    
    # Assert
    assert match is not None
    assert match["target"] == "http://backend:8001"
```

## Documentation

### Updating Docs

- Update README.md for user-facing changes
- Update code comments for internal changes
- Add examples for new features
- Keep CHANGELOG.md updated

### Documentation Style

- Use clear, concise language
- Provide examples
- Include code snippets
- Add diagrams where helpful

## Project Structure

```
fastproxy/
├── main.py              # Main application
├── proxy/               # Core proxy logic
├── webapp/              # Management webapp
│   ├── backend/        # FastAPI backend
│   └── frontend/       # Next.js frontend
├── docker/              # Docker configurations
├── tests/               # Test files
└── docs/                # Documentation
```

## Release Process

1. Update version numbers
2. Update CHANGELOG.md
3. Create a git tag: `git tag -a v1.0.0 -m "Version 1.0.0"`
4. Push tag: `git push origin v1.0.0`
5. GitHub Actions will build and publish

## Community

- 💬 [Discussions](https://github.com/yourusername/fastproxy/discussions) - Ask questions
- 🐛 [Issues](https://github.com/yourusername/fastproxy/issues) - Report bugs
- 📧 Email - [project email]
- 💼 LinkedIn - [link]

## Recognition

Contributors are recognized in:
- README.md contributors section
- CHANGELOG.md for specific contributions
- GitHub contributors page

## Questions?

Don't hesitate to ask! Create a discussion or reach out to maintainers.

## License

By contributing to FastProxy, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to FastProxy! 🚀**

