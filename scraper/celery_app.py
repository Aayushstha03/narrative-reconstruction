from celery import Celery

app = Celery('scraper', broker='redis://redis:6379/0')

import scraper.tasks  # noqa

app.conf.update(
    result_backend='redis://redis:6379/0',
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
)


app.conf.beat_schedule = {
    'scrape-every-10-sec': {
        'task': 'scraper.tasks.scrape_and_save',
        'schedule': 10.0,
    },
}
