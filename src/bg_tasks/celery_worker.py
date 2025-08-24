from celery import Celery

# Initialize Celery with Redis as broker and backend
celery_app = Celery(
    'worker',
    broker='redis://redis:6379/0',
    backend='redis://redis:6379/0',
    include='src.bg_tasks.tasks',  # Ensure tasks are auto-discovered
)
