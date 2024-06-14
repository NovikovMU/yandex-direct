from celery import Celery

from datetime import timedelta

app = Celery(
    'reminder',
    broker='redis://localhost:6379/1',
)

app.conf.update(
    worker_max_memory_per_child=300 * 1024
)

app.conf.beat_schedule = {
    'check-reminders-every-minute': {
        'task': 'tasks.schedule_reminders',
        'schedule': 30.0,
    },
}
