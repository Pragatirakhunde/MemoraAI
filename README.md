# Enterprise Memory Engine

AI-powered Organizational Knowledge Graph and Memory Platform.

Status:

🚧 Under Development


{
  "email": "admin@technova.com",
  "password": "Admin@123"
}

Terminal 1
Docker
docker compose up -d

Terminal 2
FastAPI
uvicorn app.main:app --reload

Terminal 3
Celery Worker
celery -A app.workers.celery_app:celery_app worker --loglevel=INFO --pool=solo

Terminal 4
Celery Beat
celery -A app.workers.celery_app:celery_app beat --loglevel=INFO

Terminal 5
Frontend
npm run dev