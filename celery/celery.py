from celery import Celery

app = Celery('reminder', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')

app.conf.update(
    result_expires=3600,
    timezone='UTC',
    enable_utc=True,
)