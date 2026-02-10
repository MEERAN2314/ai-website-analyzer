.PHONY: help install install-dev run dev docker-up docker-down docker-prod docker-logs docker-clean seed test lint format clean health

help:
	@echo "🚀 AI Website Analyzer - Development Commands"
	@echo ""
	@echo "📦 Setup & Installation:"
	@echo "  make install        - Install production dependencies"
	@echo "  make install-dev    - Install all dependencies including dev tools"
	@echo "  make playwright     - Install Playwright browsers"
	@echo ""
	@echo "🏃 Running Application:"
	@echo "  make run            - Run application locally"
	@echo "  make dev            - Run with auto-reload (development mode)"
	@echo ""
	@echo "🐳 Docker Commands:"
	@echo "  make docker-up      - Start with Docker Compose (development)"
	@echo "  make docker-prod    - Start with Docker Compose (production)"
	@echo "  make docker-down    - Stop Docker containers"
	@echo "  make docker-logs    - View Docker logs"
	@echo "  make docker-clean   - Remove all containers and volumes"
	@echo "  make docker-rebuild - Rebuild and restart containers"
	@echo ""
	@echo "🧪 Testing & Quality:"
	@echo "  make test           - Run all tests"
	@echo "  make test-cov       - Run tests with coverage report"
	@echo "  make lint           - Run code linting"
	@echo "  make format         - Format code with black and isort"
	@echo "  make health         - Check application health"
	@echo ""
	@echo "🗄️  Database:"
	@echo "  make seed           - Seed sample users"
	@echo ""
	@echo "🧹 Cleanup:"
	@echo "  make clean          - Clean up cache files"
	@echo "  make clean-all      - Deep clean (cache + outputs + logs)"

# Installation
install:
	@echo "📦 Installing production dependencies..."
	pip install -r requirements.txt

install-dev:
	@echo "📦 Installing all dependencies..."
	pip install -r requirements.txt
	pip install pytest pytest-asyncio pytest-cov black flake8 isort

playwright:
	@echo "🎭 Installing Playwright browsers..."
	playwright install chromium
	playwright install-deps chromium

# Running Application
run:
	@echo "🚀 Starting application..."
	uvicorn app.main:app --host 0.0.0.0 --port 8000

dev:
	@echo "🔥 Starting development server with auto-reload..."
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Docker Commands
docker-up:
	@echo "🐳 Starting Docker containers (development)..."
	docker-compose up --build

docker-prod:
	@echo "🐳 Starting Docker containers (production)..."
	docker-compose -f docker-compose.prod.yml up -d --build

docker-down:
	@echo "🛑 Stopping Docker containers..."
	docker-compose down

docker-logs:
	@echo "📋 Viewing Docker logs..."
	docker-compose logs -f

docker-clean:
	@echo "🧹 Cleaning Docker containers and volumes..."
	docker-compose down -v
	docker system prune -f

docker-rebuild:
	@echo "🔄 Rebuilding Docker containers..."
	docker-compose down
	docker-compose up --build -d

# Testing
test:
	@echo "🧪 Running tests..."
	pytest tests/ -v

test-cov:
	@echo "🧪 Running tests with coverage..."
	pytest tests/ -v --cov=app --cov-report=html --cov-report=term

# Code Quality
lint:
	@echo "🔍 Running linters..."
	flake8 app/ --max-line-length=120 --exclude=__pycache__,migrations
	@echo "✅ Linting complete!"

format:
	@echo "✨ Formatting code..."
	black app/ tests/ --line-length=120
	isort app/ tests/ --profile black
	@echo "✅ Formatting complete!"

# Health Check
health:
	@echo "🏥 Checking application health..."
	@curl -s http://localhost:8000/api/v1/health | python -m json.tool || echo "❌ Application not running"

# Database
seed:
	@echo "🌱 Seeding database with sample users..."
	python scripts/seed_users.py

# Cleanup
clean:
	@echo "🧹 Cleaning cache files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	@echo "✅ Cleanup complete!"

clean-all: clean
	@echo "🧹 Deep cleaning..."
	rm -rf logs/*.log
	rm -rf outputs/*
	rm -rf temp/*
	rm -rf app/static/pdfs/*.pdf
	@echo "✅ Deep cleanup complete!"
