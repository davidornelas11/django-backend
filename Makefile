# Makefile for Django Meal Planning Project
# Provides easy commands for Docker operations

.PHONY: help setup dev-up dev-down dev-logs test test-clean prod-up prod-down migrate superuser shell rebuild status logs-web logs-celery logs-celery-beat test-components test-integration test-instacart test-auth check-meals view-meals cleanup

# Default target
help:
	@echo "🐳 Django Meal Planning Project - Docker Commands"
	@echo "================================================"
	@echo ""
	@echo "Setup:"
	@echo "  make setup          # Initial Docker setup"
	@echo ""
	@echo "Development:"
	@echo "  make dev-up         # Start development environment"
	@echo "  make dev-down       # Stop development environment"
	@echo "  make dev-logs       # View development logs"
	@echo "  make rebuild        # Rebuild and restart containers"
	@echo ""
	@echo "Testing:"
	@echo "  make test           # Run all tests"
	@echo "  make test-clean     # Clean test environment"
	@echo "  make test-auth      # Run authentication tests"
	@echo "  make test-components # Run component tests"
	@echo "  make test-integration # Run integration tests"
	@echo "  make test-instacart # Run Instacart API tests"
	@echo ""
	@echo "Database:"
	@echo "  make migrate        # Run database migrations"
	@echo "  make superuser      # Create Django superuser"
	@echo "  make shell          # Open Django shell"
	@echo ""
	@echo "Meal Plans:"
	@echo "  make check-meals    # Check meal plans in database"
	@echo "  make view-meals     # View meal plans"
	@echo "  make cleanup        # Cleanup failed meal plans"
	@echo ""
	@echo "Logs:"
	@echo "  make logs-web       # View web service logs"
	@echo "  make logs-celery    # View Celery logs"
	@echo "  make logs-celery-beat # View Celery Beat logs"
	@echo ""
	@echo "Production:"
	@echo "  make prod-up        # Start production environment"
	@echo "  make prod-down      # Stop production environment"
	@echo ""
	@echo "Status:"
	@echo "  make status         # Check service status"
	@echo ""
	@echo "Help:"
	@echo "  make help           # Show this help"

# Setup
setup:
	@echo "🚀 Setting up Docker environment..."
	@./scripts/docker-setup.sh

# Development commands
dev-up:
	@echo "🚀 Starting development environment..."
	@./scripts/docker-commands.sh dev-up

dev-down:
	@echo "🛑 Stopping development environment..."
	@./scripts/docker-commands.sh dev-down

dev-logs:
	@echo "📋 Showing development logs..."
	@./scripts/docker-commands.sh dev-logs

rebuild:
	@echo "🔨 Rebuilding Docker images..."
	@./scripts/docker-commands.sh rebuild

# Testing commands
test:
	@echo "🧪 Running tests in Docker..."
	@./scripts/docker-commands.sh test

test-clean:
	@echo "🧹 Cleaning up test environment..."
	@./scripts/docker-commands.sh test-clean

test-auth:
	@echo "🔐 Running authentication tests..."
	@./scripts/docker-commands.sh test-auth

test-components:
	@echo "🧪 Running component tests..."
	@./scripts/docker-commands.sh test-components

test-integration:
	@echo "🧪 Running integration tests..."
	@./scripts/docker-commands.sh test-integration

test-instacart:
	@echo "🧪 Running Instacart API tests..."
	@./scripts/docker-commands.sh test-instacart

# Database commands
migrate:
	@echo "🗄️  Running database migrations..."
	@./scripts/docker-commands.sh migrate

superuser:
	@echo "👤 Creating superuser..."
	@./scripts/docker-commands.sh superuser

shell:
	@echo "🐍 Opening Django shell..."
	@./scripts/docker-commands.sh shell

# Meal plan commands
check-meals:
	@echo "🍽️  Checking meal plans in database..."
	@./scripts/docker-commands.sh check-meals

view-meals:
	@echo "🍽️  Viewing meal plans..."
	@./scripts/docker-commands.sh view-meals

cleanup:
	@echo "🧹 Cleaning up failed meal plans..."
	@./scripts/docker-commands.sh cleanup

# Log commands
logs-web:
	@echo "📋 Showing web service logs..."
	@./scripts/docker-commands.sh logs-web

logs-celery:
	@echo "📋 Showing Celery logs..."
	@./scripts/docker-commands.sh logs-celery

logs-celery-beat:
	@echo "📋 Showing Celery Beat logs..."
	@./scripts/docker-commands.sh logs-celery-beat

# Production commands
prod-up:
	@echo "🚀 Starting production environment..."
	@./scripts/docker-commands.sh prod-up

prod-down:
	@echo "🛑 Stopping production environment..."
	@./scripts/docker-commands.sh prod-down

# Status
status:
	@echo "📊 Checking service status..."
	@./scripts/docker-commands.sh status 