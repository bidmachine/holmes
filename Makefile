.PHONY: help install dev test lint format clean run docker-build docker-run docker-stop

help:
	@echo "Available commands:"
	@echo "  make install       - Install dependencies using Poetry"
	@echo "  make dev          - Install dev dependencies"
	@echo "  make test         - Run tests"
	@echo "  make lint         - Run linters (flake8, mypy)"
	@echo "  make format       - Format code with black"
	@echo "  make clean        - Clean up cache files"
	@echo "  make run          - Run the Slack bot locally"
	@echo "  make docker-build - Build Docker image"
	@echo "  make docker-run   - Run with docker-compose"
	@echo "  make docker-stop  - Stop docker-compose"

install:
	poetry install --no-dev

dev:
	poetry install

test:
	poetry run pytest tests/ -v --cov=app --cov-report=term-missing

lint:
	poetry run flake8 app/
	poetry run mypy app/

format:
	poetry run black app/ tests/

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true

run:
	poetry run python -m app.main

docker-build:
	docker-compose build

docker-run:
	docker-compose up -d

docker-stop:
	docker-compose down

docker-logs:
	docker-compose logs -f holmes-bot