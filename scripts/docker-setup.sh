#!/bin/bash

# Docker Setup Script for Django Meal Planning Project
# This script helps developers set up the Docker environment

set -e

echo "🚀 Setting up Docker environment for Django Meal Planning Project"
echo "================================================================"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first:"
    echo "   https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first:"
    echo "   https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating a template..."
    cat > .env << EOF
# Django Settings
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Database
DATABASE_URL=postgresql://postgres:postgres@db:5432/meal_planning

# Redis
REDIS_URL=redis://redis:6379/0

# API Keys (replace with your actual keys)
OPENAI_API_KEY=your-openai-api-key-here
INSTACART_API_KEY=your-instacart-api-key-here

# Optional: External database (if not using Docker)
# DATABASE_URL=postgresql://user:password@localhost:5432/meal_planning
# REDIS_URL=redis://localhost:6379/0
EOF
    echo "✅ Created .env template. Please edit it with your actual API keys."
    echo "   You can get your API keys from:"
    echo "   - OpenAI: https://platform.openai.com/api-keys"
    echo "   - Instacart: https://www.instacart.com/developers"
else
    echo "✅ .env file found"
fi

# Create logs directory
mkdir -p logs

echo ""
echo "🔧 Available Docker commands:"
echo "============================="
echo ""
echo "Development environment:"
echo "  docker-compose -f docker-compose.dev.yml up -d    # Start all services"
echo "  docker-compose -f docker-compose.dev.yml down     # Stop all services"
echo "  docker-compose -f docker-compose.dev.yml logs     # View logs"
echo ""
echo "Production environment:"
echo "  docker-compose up -d                              # Start production services"
echo "  docker-compose down                               # Stop production services"
echo ""
echo "Testing:"
echo "  docker-compose -f docker-compose.test.yml up      # Run tests"
echo "  docker-compose -f docker-compose.test.yml down    # Clean up test environment"
echo ""
echo "Individual services:"
echo "  docker-compose -f docker-compose.dev.yml up web   # Start only Django"
echo "  docker-compose -f docker-compose.dev.yml up celery # Start only Celery"
echo ""
echo "Management commands:"
echo "  docker-compose -f docker-compose.dev.yml exec web python manage.py migrate"
echo "  docker-compose -f docker-compose.dev.yml exec web python manage.py createsuperuser"
echo "  docker-compose -f docker-compose.dev.yml exec web python test_components.py"
echo ""
echo "Web interfaces:"
echo "  - Django app: http://localhost:8000"
echo "  - pgAdmin (PostgreSQL): http://localhost:8080 (admin@admin.com / admin)"
echo "  - Redis Commander: http://localhost:8081"
echo ""
echo "🎯 Quick start:"
echo "  1. Edit .env with your API keys"
echo "  2. Run: docker-compose -f docker-compose.dev.yml up -d"
echo "  3. Visit: http://localhost:8000"
echo ""
echo "Happy coding! 🎉" 