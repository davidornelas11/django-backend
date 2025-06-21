# 🐳 Docker Setup for Django Meal Planning Project

This guide helps you set up and run the Django Meal Planning project using Docker, ensuring a consistent development environment across all machines.

## 🚀 Quick Start

### Prerequisites
- [Docker](https://docs.docker.com/get-docker/) installed
- [Docker Compose](https://docs.docker.com/compose/install/) installed

### 1. Initial Setup
```bash
# Clone the repository
git clone <your-repo-url>
cd django-project

# Run the setup script
./scripts/docker-setup.sh
```

### 2. Configure Environment
Edit the `.env` file with your API keys:
```env
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
```

### 3. Start Development Environment
```bash
# Start all services
./scripts/docker-commands.sh dev-up

# Or manually:
docker-compose -f docker-compose.dev.yml up -d
```

### 4. Access the Application
- **Django App**: http://localhost:8000
- **pgAdmin** (PostgreSQL): http://localhost:8080 (admin@admin.com / admin)
- **Redis Commander**: http://localhost:8081

---

## 🏗️ Architecture

The Docker setup includes the following services:

### Development Environment (`docker-compose.dev.yml`)
- **web**: Django application
- **celery**: Celery worker for background tasks
- **celery-beat**: Celery beat for scheduled tasks
- **redis**: Redis broker for Celery
- **db**: PostgreSQL database
- **redis-commander**: Web UI for Redis management
- **pgadmin**: Web UI for PostgreSQL management

### Production Environment (`docker-compose.yml`)
- **web**: Django application
- **celery**: Celery worker
- **celery-beat**: Celery beat
- **redis**: Redis broker
- **db**: PostgreSQL database

### Test Environment (`docker-compose.test.yml`)
- **test**: Test runner
- **test-celery**: Celery worker for tests
- **test-db**: Test database
- **test-redis**: Test Redis instance

---

## 🛠️ Common Commands

### Development
```bash
# Start development environment
./scripts/docker-commands.sh dev-up

# Stop development environment
./scripts/docker-commands.sh dev-down

# View logs
./scripts/docker-commands.sh dev-logs

# Rebuild and restart
./scripts/docker-commands.sh rebuild
```

### Testing
```bash
# Run all tests
./scripts/docker-commands.sh test

# Run specific tests
./scripts/docker-commands.sh test-components
./scripts/docker-commands.sh test-integration
./scripts/docker-commands.sh test-instacart

# Clean test environment
./scripts/docker-commands.sh test-clean
```

### Database Management
```bash
# Run migrations
./scripts/docker-commands.sh migrate

# Create superuser
./scripts/docker-commands.sh superuser

# Open Django shell
./scripts/docker-commands.sh shell
```

### Meal Plan Management
```bash
# Check meal plans
./scripts/docker-commands.sh check-meals

# View meal plans
./scripts/docker-commands.sh view-meals

# Cleanup failed plans
./scripts/docker-commands.sh cleanup
```

### Logs
```bash
# View specific service logs
./scripts/docker-commands.sh logs-web
./scripts/docker-commands.sh logs-celery
./scripts/docker-commands.sh logs-celery-beat
```

### Production
```bash
# Start production environment
./scripts/docker-commands.sh prod-up

# Stop production environment
./scripts/docker-commands.sh prod-down
```

---

## 🔧 Manual Docker Commands

If you prefer to use Docker commands directly:

### Development
```bash
# Start services
docker-compose -f docker-compose.dev.yml up -d

# Stop services
docker-compose -f docker-compose.dev.yml down

# View logs
docker-compose -f docker-compose.dev.yml logs -f

# Execute commands in containers
docker-compose -f docker-compose.dev.yml exec web python manage.py migrate
docker-compose -f docker-compose.dev.yml exec web python test_components.py
```

### Testing
```bash
# Run tests
docker-compose -f docker-compose.test.yml up --abort-on-container-exit

# Clean up
docker-compose -f docker-compose.test.yml down -v
```

---

## 🐛 Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# Check what's using the port
lsof -i :8000

# Kill the process or change ports in docker-compose files
```

#### 2. Database Connection Issues
```bash
# Check if database is running
docker-compose -f docker-compose.dev.yml ps

# Restart database
docker-compose -f docker-compose.dev.yml restart db
```

#### 3. Celery Not Processing Tasks
```bash
# Check Celery logs
./scripts/docker-commands.sh logs-celery

# Restart Celery
docker-compose -f docker-compose.dev.yml restart celery
```

#### 4. Environment Variables Not Loading
```bash
# Check if .env file exists and has correct format
cat .env

# Restart services to reload environment
./scripts/docker-commands.sh rebuild
```

#### 5. Permission Issues
```bash
# Fix file permissions
chmod +x scripts/*.sh

# Rebuild containers
./scripts/docker-commands.sh rebuild
```

### Debugging

#### View Container Logs
```bash
# All services
docker-compose -f docker-compose.dev.yml logs

# Specific service
docker-compose -f docker-compose.dev.yml logs web
docker-compose -f docker-compose.dev.yml logs celery
```

#### Access Container Shell
```bash
# Django container
docker-compose -f docker-compose.dev.yml exec web bash

# Database container
docker-compose -f docker-compose.dev.yml exec db psql -U postgres -d meal_planning
```

#### Check Service Status
```bash
# All services
./scripts/docker-commands.sh status

# Individual containers
docker-compose -f docker-compose.dev.yml ps
```

---

## 📁 File Structure

```
django-project/
├── Dockerfile                    # Main application container
├── docker-compose.yml           # Production services
├── docker-compose.dev.yml       # Development services
├── docker-compose.test.yml      # Test services
├── .dockerignore                # Files to exclude from Docker build
├── init.sql                     # Database initialization
├── scripts/
│   ├── docker-setup.sh         # Initial setup script
│   └── docker-commands.sh      # Common commands script
├── .env                         # Environment variables (create this)
└── DOCKER_README.md            # This file
```

---

## 🔄 Development Workflow

### 1. Daily Development
```bash
# Start environment
./scripts/docker-commands.sh dev-up

# Make code changes (they're automatically reflected due to volume mounting)

# Run tests
./scripts/docker-commands.sh test-components

# Check logs if needed
./scripts/docker-commands.sh logs-web
```

### 2. Testing Changes
```bash
# Run all tests
./scripts/docker-commands.sh test

# Run specific test suites
./scripts/docker-commands.sh test-integration
./scripts/docker-commands.sh test-instacart
```

### 3. Database Changes
```bash
# Create migrations
docker-compose -f docker-compose.dev.yml exec web python manage.py makemigrations

# Apply migrations
./scripts/docker-commands.sh migrate
```

### 4. Stopping Work
```bash
# Stop all services
./scripts/docker-commands.sh dev-down

# Or keep running for next session
```

---

## 🚀 Production Deployment

For production deployment, use the production compose file:

```bash
# Start production services
./scripts/docker-commands.sh prod-up

# Monitor logs
docker-compose logs -f

# Stop production services
./scripts/docker-commands.sh prod-down
```

---

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Django Documentation](https://docs.djangoproject.com/)
- [Celery Documentation](https://docs.celeryproject.org/)

---

## 🆘 Getting Help

If you encounter issues:

1. Check the troubleshooting section above
2. Review the logs: `./scripts/docker-commands.sh dev-logs`
3. Check service status: `./scripts/docker-commands.sh status`
4. Rebuild containers: `./scripts/docker-commands.sh rebuild`
5. Ask for help in your team's communication channel

Happy coding! 🎉 