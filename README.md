# Django API Project

This is a Django-based backend service that connects to external APIs and provides authentication.

## Setup Instructions

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a .env file in the root directory with your environment variables:
```
DEBUG=True
SECRET_KEY=your-secret-key-here
```

4. Run migrations:
```bash
python manage.py migrate
```

5. Create a superuser:
```bash
python manage.py createsuperuser
```

6. Run the development server:
```bash
python manage.py runserver
```

## Project Structure

- `api/` - Contains API endpoints and external API integration
- `core/` - Core Django project settings
- `users/` - User authentication and management
- `utils/` - Utility functions and helpers

## API Documentation

API documentation will be available at `/api/docs/` when the server is running. 