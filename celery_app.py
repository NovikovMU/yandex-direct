from celery import Celery

from datetime import timedelta


app = Celery(
    'reminder',
    broker='redis://localhost:6379/1',
    backend='redis://localhost:6379/1'
)

app.conf.beat_schedule = {
    'check-reminders-every-minute': {
        'task': 'tasks.schedule_reminders',
        'schedule': 30.0,
    },
}
