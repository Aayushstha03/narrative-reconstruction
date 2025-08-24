from src.bg_tasks.celery_worker import celery_app
import time


@celery_app.task
def sample_task(duration: int):
    """Simulate a time-consuming task."""
    time.sleep(duration)
    return f'Task completed in {duration} seconds!'
