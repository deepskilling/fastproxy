# Contributing to FastProxy

First off, thank you for considering contributing to FastProxy! It's people like you that make FastProxy such a great tool.

## 🎯 Code of Conduct

This project and everyone participating in it is governed by our commitment to provide a welcoming and inspiring community for all.

## 🚀 How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues list as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible:

- **Use a clear and descriptive title**
- **Describe the exact steps to reproduce the problem**
- **Provide specific examples**
- **Describe the behavior you observed and what you expected**
- **Include logs and error messages**
- **Note your environment** (OS, Python version, etc.)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

- **Use a clear and descriptive title**
- **Provide a detailed description of the suggested enhancement**
- **Provide specific examples to demonstrate the steps**
- **Describe the current behavior and expected behavior**
- **Explain why this enhancement would be useful**

### Pull Requests

1. **Fork the repo** and create your branch from `main`
2. **If you've added code**, add tests
3. **If you've changed APIs**, update the documentation
4. **Ensure the test suite passes**
5. **Make sure your code lints** (black, isort, flake8)
6. **Issue that pull request!**

## 🛠️ Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then:
git clone https://github.com/YOUR_USERNAME/fastproxy.git
cd fastproxy
```

### 2. Set Up Environment

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

## 📝 Coding Standards

### Python Style Guide

We follow PEP 8 with some modifications:

- **Line length**: 127 characters (not 79)
- **Use Black** for formatting
- **Use isort** for import sorting
- **Use flake8** for linting

### Format Your Code

```bash
# Format with black
black .

# Sort imports
isort .

# Check with flake8
flake8 .
```

### Naming Conventions

- **Functions/Variables**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private methods**: `_leading_underscore`

### Documentation

- Add docstrings to all functions, classes, and modules
- Use type hints for function arguments and return values
- Update README.md if you change functionality
- Add examples for new features

Example:

```python
def process_request(request: Request, config: Dict) -> Response:
    """
    Process incoming HTTP request and forward to backend.
    
    Args:
        request: FastAPI Request object
        config: Configuration dictionary
    
    Returns:
        Response from backend server
    
    Raises:
        HTTPException: If backend is unreachable
    """
    pass
```

## 🧪 Testing

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_proxy.py -v
```

### Writing Tests

- Write tests for all new features
- Maintain test coverage above 80%
- Use descriptive test names: `test_should_reject_invalid_config`
- Use fixtures for common setup
- Mock external dependencies

Example:

```python
def test_rate_limiter_should_block_after_limit():
    """Test that rate limiter blocks requests after limit is reached"""
    limiter = RateLimiter(requests_per_minute=5)
    
    # Allow first 5 requests
    for i in range(5):
        assert limiter.allow_request("192.168.1.1") is True
    
    # Block 6th request
    assert limiter.allow_request("192.168.1.1") is False
```

## 📋 Commit Messages

### Format

```
type(scope): subject

body (optional)

footer (optional)
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Examples

```bash
git commit -m "feat(proxy): add WebSocket support"
git commit -m "fix(rate-limit): correct sliding window calculation"
git commit -m "docs: update installation instructions"
git commit -m "test(audit): add tests for log filtering"
```

## 📁 Project Structure

```
fastproxy/
├── main.py                    # Application entry point
├── config.yaml                # Configuration
├── requirements.txt           # Dependencies
├── .env.example              # Environment template
├── proxy/                    # Core proxy module
├── audit/                    # Audit logging module
├── admin/                    # Admin API module
├── security/                 # Security features
├── tests/                    # Test suite
├── docs/                     # Documentation files
└── docker/                   # Docker configuration
```

## 🔄 Pull Request Process

### Before Submitting

1. ✅ Run the full test suite: `pytest`
2. ✅ Format your code: `black . && isort .`
3. ✅ Check linting: `flake8 .`
4. ✅ Update documentation if needed
5. ✅ Add tests for new features
6. ✅ Ensure all tests pass
7. ✅ Update CHANGELOG.md (if applicable)

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] Added new tests
- [ ] Updated existing tests

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] No new warnings generated
```

### Review Process

1. Submit your PR
2. Wait for CI checks to pass
3. Address review comments
4. Get approval from maintainer(s)
5. PR will be merged

## 🎨 Project Structure

```
fastproxy/
├── proxy/          # Core proxy logic
├── audit/          # Audit logging
├── admin/          # Admin endpoints
├── tests/          # Test suite
└── main.py         # Application entry
```

### Adding New Features

1. **Create module** in appropriate directory
2. **Add tests** in `tests/`
3. **Update documentation**
4. **Add to relevant `__init__.py`**
5. **Register endpoints** in `main.py`

## 🐛 Debugging

### Enable Debug Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Run with Debug Mode

```bash
uvicorn main:app --reload --log-level debug
```

### Using Python Debugger

```python
import pdb; pdb.set_trace()  # Add breakpoint
```

## 📚 Resources

- **FastAPI Documentation**: https://fastapi.tiangolo.com
- **httpx Documentation**: https://www.python-httpx.org
- **Pytest Documentation**: https://docs.pytest.org
- **Python Style Guide**: https://pep8.org

## ❓ Questions?

- **Check existing issues** on GitHub
- **Open a discussion** for questions
- **Join our community** (if applicable)

## 🙏 Thank You!

Your contributions make FastProxy better for everyone. We appreciate your time and effort!

---

**Happy Coding!** 🚀

