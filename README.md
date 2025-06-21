# 🍽️ Django Meal Planning Project

A Django-based meal planning system that uses LangChain, OpenAI, and Instacart APIs to generate personalized weekly meal plans and shopping carts based on user preferences.

## 🚀 Quick Start

### Option 1: Docker (Recommended)

The easiest way to get started is using Docker, which ensures a consistent environment across all machines:

```bash
# Clone the repository
git clone <your-repo-url>
cd django-project

# Run the setup script
./scripts/docker-setup.sh

# Start the development environment
make dev-up
# or: ./scripts/docker-commands.sh dev-up
```

**Access the application:**
- Django App: http://localhost:8000
- pgAdmin (PostgreSQL): http://localhost:8080 (admin@admin.com / admin)
- Redis Commander: http://localhost:8081

### Option 2: Local Development

If you prefer to run locally without Docker:

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file with your API keys
cp .env.example .env
# Edit .env with your actual API keys

# Start Redis
brew services start redis

# Run migrations
python manage.py migrate

# Start Celery worker (in new terminal)
celery -A core worker --loglevel=info

# Start Django server
python manage.py runserver
```

## 🏗️ Architecture

This project integrates multiple technologies:

- **Django**: Web framework and API
- **LangChain**: AI/LLM orchestration
- **OpenAI**: GPT models for meal planning
- **Instacart**: Shopping cart creation
- **Celery**: Background task processing
- **Redis**: Message broker and caching
- **PostgreSQL**: Database (Docker) / SQLite (local)

## 🧪 Testing

### Docker Testing
```bash
# Run all tests
make test

# Run specific test suites
make test-components
make test-integration
make test-instacart
```

### Local Testing
```bash
# Run test scripts
python test_services.py
python test_components.py
python test_integration.py
python test_instacart_api.py
```

## 📁 Project Structure

```
django-project/
├── api/                    # API endpoints
├── core/                   # Django settings and Celery config
│   ├── tasks.py           # Celery tasks for meal planning
│   ├── instacart_client.py # Instacart API client
│   └── settings.py        # Django settings
├── users/                  # User authentication and profiles
├── scripts/               # Docker and utility scripts
├── logs/                  # Application logs
├── test_*.py             # Test scripts
├── Dockerfile            # Docker configuration
├── docker-compose*.yml   # Docker services
├── Makefile              # Easy commands
└── DOCKER_README.md      # Docker documentation
```

## 🔧 Common Commands

### Docker Commands
```bash
# Development
make dev-up              # Start development environment
make dev-down            # Stop development environment
make dev-logs            # View logs
make rebuild             # Rebuild containers

# Testing
make test                # Run all tests
make test-components     # Run component tests
make test-integration    # Run integration tests

# Database
make migrate             # Run migrations
make superuser           # Create superuser
make shell               # Open Django shell

# Meal Plans
make check-meals         # Check meal plans
make view-meals          # View meal plans
make cleanup             # Cleanup failed plans
```

### Local Commands
```bash
# Django
python manage.py runserver
python manage.py migrate
python manage.py createsuperuser

# Celery
celery -A core worker --loglevel=info
celery -A core beat --loglevel=info

# Testing
python test_components.py
python test_integration.py
python check_meal_plans.py
```

## 🔑 Environment Variables

Create a `.env` file with the following variables:

```env
# Django Settings
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Database (Docker)
DATABASE_URL=postgresql://postgres:postgres@db:5432/meal_planning

# Redis (Docker)
REDIS_URL=redis://redis:6379/0

# API Keys
OPENAI_API_KEY=your-openai-api-key-here
INSTACART_API_KEY=your-instacart-api-key-here
```

## 🧪 Test Scripts

The project includes comprehensive test scripts:

- `test_services.py`: Redis and Celery connectivity
- `test_components.py`: Individual component testing
- `test_integration.py`: End-to-end workflow testing
- `test_instacart_api.py`: Instacart API integration
- `check_meal_plans.py`: Database inspection
- `view_meal_plan.py`: Meal plan viewer
- `cleanup_failed_plans.py`: Cleanup utility

## 📚 Documentation

- [Docker Setup Guide](DOCKER_README.md) - Comprehensive Docker documentation
- [Testing Guide](TESTING_GUIDE.md) - Detailed testing instructions
- [API Documentation](api/README.md) - API endpoints and usage

## 🐛 Troubleshooting

### Common Issues

1. **Celery not processing tasks**
   - Check if Redis is running
   - Verify Celery worker is started
   - Check logs: `make logs-celery`

2. **API key errors**
   - Verify `.env` file has correct API keys
   - Check environment variables are loaded
   - Test API keys with curl commands

3. **Database connection issues**
   - For Docker: Check if PostgreSQL container is running
   - For local: Ensure SQLite file is writable

4. **Port conflicts**
   - Check if ports 8000, 6379, 5432 are available
   - Use different ports in docker-compose files

### Getting Help

1. Check the logs: `make dev-logs`
2. Review the troubleshooting sections in documentation
3. Run test scripts to identify issues
4. Check service status: `make status`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `make test`
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

---

For detailed Docker setup and advanced usage, see [DOCKER_README.md](DOCKER_README.md). 