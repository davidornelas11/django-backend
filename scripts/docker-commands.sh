#!/bin/bash

# Docker Commands Script for Django Meal Planning Project
# Common commands for development and testing

case "$1" in
    "dev-up")
        echo "🚀 Starting development environment..."
        docker-compose -f docker-compose.dev.yml up -d
        echo "✅ Development environment started!"
        echo "   - Django: http://localhost:8000"
        echo "   - pgAdmin: http://localhost:8080"
        echo "   - Redis Commander: http://localhost:8081"
        ;;
    
    "dev-down")
        echo "🛑 Stopping development environment..."
        docker-compose -f docker-compose.dev.yml down
        echo "✅ Development environment stopped!"
        ;;
    
    "dev-logs")
        echo "📋 Showing development logs..."
        docker-compose -f docker-compose.dev.yml logs -f
        ;;
    
    "test")
        echo "🧪 Running tests in Docker..."
        docker-compose -f docker-compose.test.yml up --abort-on-container-exit
        docker-compose -f docker-compose.test.yml down
        ;;
    
    "test-clean")
        echo "🧹 Cleaning up test environment..."
        docker-compose -f docker-compose.test.yml down -v
        echo "✅ Test environment cleaned up!"
        ;;
    
    "test-auth")
        echo "🔐 Running authentication tests..."
        docker-compose -f docker-compose.dev.yml exec web python test_authentication.py
        ;;
    
    "prod-up")
        echo "🚀 Starting production environment..."
        docker-compose up -d
        echo "✅ Production environment started!"
        ;;
    
    "prod-down")
        echo "🛑 Stopping production environment..."
        docker-compose down
        echo "✅ Production environment stopped!"
        ;;
    
    "migrate")
        echo "🗄️  Running database migrations..."
        docker-compose -f docker-compose.dev.yml exec web python manage.py migrate
        ;;
    
    "superuser")
        echo "👤 Creating superuser..."
        docker-compose -f docker-compose.dev.yml exec web python manage.py createsuperuser
        ;;
    
    "shell")
        echo "🐍 Opening Django shell..."
        docker-compose -f docker-compose.dev.yml exec web python manage.py shell
        ;;
    
    "test-components")
        echo "🧪 Running component tests..."
        docker-compose -f docker-compose.dev.yml exec web python test_components.py
        ;;
    
    "test-integration")
        echo "🧪 Running integration tests..."
        docker-compose -f docker-compose.dev.yml exec web python test_integration.py
        ;;
    
    "test-instacart")
        echo "🧪 Running Instacart API tests..."
        docker-compose -f docker-compose.dev.yml exec web python test_instacart_api.py
        ;;
    
    "check-meals")
        echo "🍽️  Checking meal plans in database..."
        docker-compose -f docker-compose.dev.yml exec web python check_meal_plans.py
        ;;
    
    "view-meals")
        echo "🍽️  Viewing meal plans..."
        docker-compose -f docker-compose.dev.yml exec web python view_meal_plan.py
        ;;
    
    "cleanup")
        echo "🧹 Cleaning up failed meal plans..."
        docker-compose -f docker-compose.dev.yml exec web python cleanup_failed_plans.py
        ;;
    
    "rebuild")
        echo "🔨 Rebuilding Docker images..."
        docker-compose -f docker-compose.dev.yml down
        docker-compose -f docker-compose.dev.yml build --no-cache
        docker-compose -f docker-compose.dev.yml up -d
        echo "✅ Images rebuilt and services restarted!"
        ;;
    
    "logs-web")
        echo "📋 Showing web service logs..."
        docker-compose -f docker-compose.dev.yml logs -f web
        ;;
    
    "logs-celery")
        echo "📋 Showing Celery logs..."
        docker-compose -f docker-compose.dev.yml logs -f celery
        ;;
    
    "logs-celery-beat")
        echo "📋 Showing Celery Beat logs..."
        docker-compose -f docker-compose.dev.yml logs -f celery-beat
        ;;
    
    "status")
        echo "📊 Checking service status..."
        docker-compose -f docker-compose.dev.yml ps
        ;;
    
    "help"|*)
        echo "🐳 Docker Commands for Django Meal Planning Project"
        echo "=================================================="
        echo ""
        echo "Development:"
        echo "  ./scripts/docker-commands.sh dev-up          # Start development environment"
        echo "  ./scripts/docker-commands.sh dev-down        # Stop development environment"
        echo "  ./scripts/docker-commands.sh dev-logs        # View development logs"
        echo "  ./scripts/docker-commands.sh rebuild         # Rebuild and restart"
        echo ""
        echo "Testing:"
        echo "  ./scripts/docker-commands.sh test            # Run all tests"
        echo "  ./scripts/docker-commands.sh test-clean      # Clean test environment"
        echo "  ./scripts/docker-commands.sh test-auth       # Run authentication tests"
        echo "  ./scripts/docker-commands.sh test-components # Run component tests"
        echo "  ./scripts/docker-commands.sh test-integration # Run integration tests"
        echo "  ./scripts/docker-commands.sh test-instacart  # Run Instacart tests"
        echo ""
        echo "Database:"
        echo "  ./scripts/docker-commands.sh migrate         # Run migrations"
        echo "  ./scripts/docker-commands.sh superuser       # Create superuser"
        echo "  ./scripts/docker-commands.sh shell           # Open Django shell"
        echo ""
        echo "Meal Plans:"
        echo "  ./scripts/docker-commands.sh check-meals     # Check meal plans"
        echo "  ./scripts/docker-commands.sh view-meals      # View meal plans"
        echo "  ./scripts/docker-commands.sh cleanup         # Cleanup failed plans"
        echo ""
        echo "Logs:"
        echo "  ./scripts/docker-commands.sh logs-web        # Web service logs"
        echo "  ./scripts/docker-commands.sh logs-celery     # Celery logs"
        echo "  ./scripts/docker-commands.sh logs-celery-beat # Celery Beat logs"
        echo ""
        echo "Production:"
        echo "  ./scripts/docker-commands.sh prod-up         # Start production"
        echo "  ./scripts/docker-commands.sh prod-down       # Stop production"
        echo ""
        echo "Status:"
        echo "  ./scripts/docker-commands.sh status          # Check service status"
        echo ""
        echo "Help:"
        echo "  ./scripts/docker-commands.sh help            # Show this help"
        ;;
esac 