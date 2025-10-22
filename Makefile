.PHONY: help install run test clean format lint

help:
	@echo "FastProxy - Makefile Commands"
	@echo "=============================="
	@echo "install    - Install dependencies"
	@echo "run        - Run the server (development mode)"
	@echo "test       - Run tests"
	@echo "clean      - Clean up generated files"
	@echo "format     - Format code with black"
	@echo "lint       - Lint code with ruff"

install:
	pip install -r requirements.txt

run:
	uvicorn main:app --reload --host 0.0.0.0 --port 8000

run-prod:
	uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

test:
	pytest -v

test-cov:
	pytest --cov=. --cov-report=html --cov-report=term

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	rm -rf htmlcov/
	rm -f .coverage
	rm -f audit/audit.db*

format:
	black .

lint:
	ruff check .

