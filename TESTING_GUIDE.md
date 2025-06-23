# 🧪 Testing Guide for Django Meal Planning System

Welcome! This guide will help you (even if you're new to Django or APIs) test and verify your meal planning project, which uses LangChain, OpenAI, and Instacart APIs with secure email verification authentication. Follow the steps below to get your environment ready, run all the tests, and troubleshoot common issues.

---

## 🚀 Quickstart

1. **Clone the repo and set up your virtual environment:**
   ```bash
   git clone <your-repo-url>
   cd django-project
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Create a `.env` file in the project root:**
   ```env
   OPENAI_API_KEY=your_openai_api_key
   INSTACART_API_KEY=your_instacart_api_key
   REDIS_URL=redis://localhost:6379/0
   DJANGO_SECRET_KEY=your_django_secret_key
   DJANGO_DEBUG=True
   DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
   CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
   
   # Email settings (for testing email verification)
   EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
   DEFAULT_FROM_EMAIL=noreply@mealplanner.com
   FRONTEND_URL=http://localhost:3000
   ```
   > **Note:** You do NOT need `INSTACART_API_SECRET`.

3. **Start Redis:**
   ```bash
   brew services start redis
   # or, if you don't use Homebrew:
   redis-server &
   ```

4. **Apply database migrations:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create a superuser (for Django admin access):**
   ```bash
   python manage.py createsuperuser
   ```

6. **Start a Celery worker (in a new terminal):**
   ```bash
   source venv/bin/activate
   export $(grep -v '^#' .env | xargs)
   celery -A core worker --loglevel=info
   ```
   > **Tip:** Always start Celery from a shell where your `.env` is loaded!

7. **(Optional) Start Django server:**
   ```bash
   python manage.py runserver
   ```

---

## 🔐 Authentication Testing Overview

The system now includes a comprehensive authentication flow:

1. **Open Registration** - Anyone can create an account
2. **Email Verification** - Users must verify their email before creating meal plans
3. **Protected Meal Planning** - Only verified users can access premium features

### Authentication Flow Testing Priority:

1. **Service Tests** - Ensure Redis/Celery work
2. **Authentication Tests** - Test registration, verification, login
3. **Component Tests** - Test individual pieces
4. **Integration Tests** - Test full workflow with authentication
5. **Instacart Tests** - Test external API integration

---

## 🧩 Test Scripts Overview

### 1. **Service Tests** (`test_services.py`)
- **Purpose:** Check that Redis and Celery are running and can accept tasks.
- **Run:**
  ```bash
  python test_services.py
  ```

### 2. **Authentication Tests** (`test_authentication.py`) - **NEW**
- **Purpose:** Test the complete authentication and email verification flow.
- **Run:**
  ```bash
  python test_authentication.py
  ```
- **Tests:**
  - User registration with email sending
  - Email verification process
  - Login/logout functionality
  - Protected endpoint access
  - Rate limiting on auth endpoints

### 3. **Component Tests** (`test_components.py`)
- **Purpose:** Test individual pieces (LangChain, OpenAI, Instacart client, DB, Celery) in isolation.
- **Run:**
  ```bash
  python test_components.py
  ```

### 4. **Integration Tests** (`test_integration.py`) - **UPDATED**
- **Purpose:** Test the full workflow including authentication and meal plan creation.
- **Run:**
  ```bash
  python test_integration.py
  ```

### 5. **Instacart API Tests** (`test_instacart_api.py`)
- **Purpose:** Specifically test Instacart API key, client, and end-to-end cart creation.
- **Run:**
  ```bash
  python test_instacart_api.py
  ```

### 6. **Database Inspection** (`check_meal_plans.py`)
- **Purpose:** View all meal plans in the database, check their status, and create test plans.
- **Run:**
  ```bash
  python check_meal_plans.py
  ```

### 7. **Cleanup Script** (`cleanup_failed_plans.py`)
- **Purpose:** Clean up failed meal plans and reset pending ones.
- **Run:**
  ```bash
  python cleanup_failed_plans.py
  ```

### 8. **Meal Plan Viewer** (`view_meal_plan.py`)
- **Purpose:** View the full content of generated meal plans.
- **Run:**
  ```bash
  python view_meal_plan.py
  ```

---

## 🔐 Testing Authentication Flow

### Manual Authentication Testing

1. **Test User Registration:**
   ```bash
   curl -X POST http://localhost:8000/auth/register/ \
     -H "Content-Type: application/json" \
     -d '{
       "username": "testuser",
       "email": "test@example.com",
       "password": "SecurePassword123!"
     }'
   ```

2. **Check email verification in development:**
   ```bash
   # In development, emails are printed to console
   python manage.py runserver
   # Look for verification token in console output
   ```

3. **Verify email manually:**
   ```bash
   curl -X POST http://localhost:8000/auth/verify-email/ \
     -H "Content-Type: application/json" \
     -d '{
       "token": "your-verification-token-here"
     }'
   ```

4. **Test protected endpoint (should fail before verification):**
   ```bash
   curl -X POST http://localhost:8000/api/profiles/1/trigger-meal-plan/ \
     -H "Authorization: Token your-access-token"
   ```

5. **Test login:**
   ```bash
   curl -X POST http://localhost:8000/auth/login/ \
     -H "Content-Type: application/json" \
     -d '{
       "username": "testuser",
       "password": "SecurePassword123!"
     }'
   ```

### Django Shell Testing

```bash
python manage.py shell
```

```python
# Check email verification status
from django.contrib.auth.models import User
from users.models import EmailVerification

user = User.objects.get(username='testuser')
print(f"Email verified: {user.profile.is_email_verified}")

# Manually verify for testing
verification = user.email_verification
verification.is_verified = True
verification.save()
print("User manually verified")
```

---

## 🛒 Verifying Instacart API with curl

To quickly check if your Instacart API key works, run this (replace `YOUR_API_KEY`):

```bash
curl --request POST \
  --url https://connect.dev.instacart.tools/idp/v1/products/products_link \
  --header 'Accept: application/json' \
  --header 'Authorization: Bearer YOUR_API_KEY' \
  --header 'Content-Type: application/json' \
  --data '{
    "title": "Test Shopping List",
    "image_url": "",
    "link_type": "shopping_list",
    "expires_in": 7,
    "instructions": ["Test instruction"],
    "line_items": [
      {
        "name": "Test Item",
        "quantity": 1,
        "unit": "each",
        "display_text": "1 each Test Item",
        "line_item_measurements": [
          {"quantity": 1, "unit": "each"}
        ],
        "filters": {"brand_filters": [], "health_filters": []}
      }
    ],
    "landing_page_configuration": {"partner_linkback_url": "", "enable_pantry_items": true}
  }'
```
- **200 OK** means your key works!
- **401 Unauthorized** means your key is missing/invalid.

---

## 🧑‍💻 Step-by-Step: Running All Tests

### Recommended Testing Order:

1. **Check services first:**
   ```bash
   python test_services.py
   ```

2. **Test authentication system:**
   ```bash
   python test_authentication.py
   ```

3. **Test individual components:**
   ```bash
   python test_components.py
   ```

4. **Run full integration test:**
   ```bash
   python test_integration.py
   ```

5. **Test Instacart API:**
   ```bash
   python test_instacart_api.py
   ```

### Docker Testing

If using Docker:

```bash
# Start services
docker-compose -f docker-compose.dev.yml up -d

# Run authentication tests
docker-compose -f docker-compose.dev.yml exec web python test_authentication.py

# Run all tests
docker-compose -f docker-compose.dev.yml exec web python test_services.py
docker-compose -f docker-compose.dev.yml exec web python test_components.py
docker-compose -f docker-compose.dev.yml exec web python test_integration.py

# Check email verification in Docker logs
docker-compose -f docker-compose.dev.yml logs web | grep -i "verification"
```

---

## 🛠️ Troubleshooting & Tips

### Authentication Issues

- **Email verification not working?**
  - In development, emails print to console - check Django server output
  - Verify `FRONTEND_URL` is set correctly in your `.env`
  - Check that `EMAIL_BACKEND` is set to `console` for development

- **User can't create meal plans?**
  - Check if email is verified: `GET /api/email-verification-status/`
  - Verify the user is authenticated (has valid token)
  - Ensure user is accessing their own profile ID

- **Rate limiting errors?**
  - Authentication endpoints have rate limits (5 registrations/hour, 5 logins/minute)
  - Wait for rate limit to reset or test with different IPs

### General Issues

- **Celery/Redis not working?**
  - Make sure Redis is running: `brew services start redis` or `redis-server &`
  - Always start Celery with your environment loaded: `export $(grep -v '^#' .env | xargs)`
  - If you change your `.env`, restart Celery!

- **API key issues?**
  - Double-check your `.env` for typos or extra spaces.
  - Use the curl test above to verify your Instacart key.

- **Database errors?**
  - Run migrations: `python manage.py makemigrations && python manage.py migrate`

- **Missing packages?**
  - Install with: `pip install -r requirements.txt`

- **Logs:**
  - Check `logs/celery.log` and `logs/celery_error.log` for detailed errors.

- **Stuck tasks or weird errors?**
  - Stop all Celery/Redis processes: `pkill -f celery; pkill -f redis`
  - Restart everything from a fresh shell with the right environment.

### Debugging Authentication

```bash
# Check user verification status in database
python manage.py shell -c "
from django.contrib.auth.models import User
for user in User.objects.all():
    print(f'{user.username}: verified={user.profile.is_email_verified}')
"

# Manually verify a user for testing
python manage.py shell -c "
from users.models import EmailVerification
verification = EmailVerification.objects.get(user__username='testuser')
verification.is_verified = True
verification.save()
print('User verified')
"

# Check authentication tokens
python manage.py shell -c "
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
user = User.objects.get(username='testuser')
token, created = Token.objects.get_or_create(user=user)
print(f'Token: {token.key}')
"
```

---

## 🧹 Cleaning Up

### Test Data Cleanup
- Test users and data are created by the test scripts. You can safely delete them or use Django admin to inspect them.
- To reset your DB:
  ```bash
  python manage.py flush
  ```
  (This deletes all data!)

### Clean Failed/Test Users
```bash
# Remove test users
python manage.py shell -c "
from django.contrib.auth.models import User
User.objects.filter(username__startswith='test_').delete()
User.objects.filter(username__startswith='auth_test_').delete()
print('Test users cleaned up')
"
```

---

## 🎯 Quick Authentication Test

Run this quick test to verify your authentication system:

```bash
# 1. Register a user
curl -X POST http://localhost:8000/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username": "quicktest", "email": "quick@test.com", "password": "TestPass123!"}' \
  | jq '.access_token' | tr -d '"'

# 2. Save the token and try to create meal plan (should fail)
TOKEN="your-token-here"
curl -X POST http://localhost:8000/api/profiles/1/trigger-meal-plan/ \
  -H "Authorization: Token $TOKEN"

# 3. Check verification status
curl -X GET http://localhost:8000/api/email-verification-status/ \
  -H "Authorization: Token $TOKEN"

# 4. Look for verification email in console, then verify
# (Get token from console output)
curl -X POST http://localhost:8000/auth/verify-email/ \
  -H "Content-Type: application/json" \
  -d '{"token": "verification-token-from-console"}'

# 5. Try meal plan creation again (should work)
curl -X POST http://localhost:8000/api/profiles/1/trigger-meal-plan/ \
  -H "Authorization: Token $TOKEN"
```

---

## 🆘 Need Help?

- Read the logs in the `logs/` directory.
- Check your environment variables with: `python -c "import os; print(os.environ.get('OPENAI_API_KEY', 'Not set'))"`
- Make sure all services are running: `ps aux | grep -E "(redis|celery)"`
- Test authentication endpoints individually using the curl commands above
- Run `python test_authentication.py` for comprehensive authentication testing
- Check Django admin at http://localhost:8000/admin/ to inspect user data
- Ask a teammate or mentor if you get stuck—everyone was new once!

---

## 📊 Expected Test Results

When all tests pass, you should see:

- **Service Tests**: Redis connected, Celery workers active
- **Authentication Tests**: Registration → Email → Verification → Login → Protected access
- **Component Tests**: All individual pieces working
- **Integration Tests**: Full workflow including authenticated meal plan creation
- **Instacart Tests**: External API integration working

**Success indicators:**
- Users can register and receive verification emails (in console)
- Email verification works and enables meal plan creation
- Authenticated users can successfully trigger meal planning tasks
- Meal plans are generated and stored in the database
- Instacart integration creates shopping cart URLs

---

Happy testing! 🎉 