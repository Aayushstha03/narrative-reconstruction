import os
from celery import Celery

celery_app = Celery(
    'celery_tasks',
    broker=os.getenv('CELERY_BROKER_URL'),
    backend=os.getenv('CELERY_RESULT_BACKEND'),
)
