# 🧪 Testing Guide for Django Meal Planning System

Welcome! This guide will help you (even if you're new to Django or APIs) test and verify your meal planning project, which uses LangChain, OpenAI, and Instacart APIs. Follow the steps below to get your environment ready, run all the tests, and troubleshoot common issues.

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

5. **Start a Celery worker (in a new terminal):**
   ```bash
   source venv/bin/activate
   export $(grep -v '^#' .env | xargs)
   celery -A core worker --loglevel=info
   ```
   > **Tip:** Always start Celery from a shell where your `.env` is loaded!

6. **(Optional) Start Django server:**
   ```bash
   python manage.py runserver
   ```

---

## 🧩 Test Scripts Overview

We provide several scripts to test different parts of your system. Run them from your project root:

### 1. **Service Tests** (`test_services.py`)
- **Purpose:** Check that Redis and Celery are running and can accept tasks.
- **Run:**
  ```bash
  python test_services.py
  ```

### 2. **Component Tests** (`test_components.py`)
- **Purpose:** Test individual pieces (LangChain, OpenAI, Instacart client, DB, Celery) in isolation.
- **Run:**
  ```bash
  python test_components.py
  ```

### 3. **Integration Tests** (`test_integration.py`)
- **Purpose:** Test the full workflow: environment, DB, user/profile, Celery, Instacart, and result verification.
- **Run:**
  ```bash
  python test_integration.py
  ```

### 4. **Instacart API Tests** (`test_instacart_api.py`)
- **Purpose:** Specifically test Instacart API key, client, and end-to-end cart creation.
- **Run:**
  ```bash
  python test_instacart_api.py
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

1. **Check services:**
   ```bash
   python test_services.py
   ```
2. **Test components:**
   ```bash
   python test_components.py
   ```
3. **Run integration test:**
   ```bash
   python test_integration.py
   ```
4. **Test Instacart API:**
   ```bash
   python test_instacart_api.py
   ```

---

## 🛠️ Troubleshooting & Tips

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

---

## 🧹 Cleaning Up
- Test users and data are created by the test scripts. You can safely delete them or use Django admin to inspect them.
- To reset your DB, you can run:
  ```bash
  python manage.py flush
  ```
  (This deletes all data!)

---

## 🆘 Need Help?
- Read the logs in the `logs/` directory.
- Check your environment variables.
- Make sure all services are running.
- Ask a teammate or mentor if you get stuck—everyone was new once!

---

Happy testing! 🎉 