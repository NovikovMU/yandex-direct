from celery import Celery
from celery.schedules import crontab


app = Celery(
    'reminder',
    broker='redis://localhost:6379/1',
)


app.conf.update(
    worker_max_memory_per_child=300*1024
)

app.conf.beat_schedule = {
    'check-amount-every-minute': {
        'task': 'tasks.amount_check',
        'schedule': 60.0,
    },
    'send-donation-alert-every-month': {
        'task': 'tasks.donation_alert',
        'schedule': crontab(minute=0, hour=12, day_of_month=15)
    },
    'check-daily-stat-every-hour': {
        'task': 'tasks.daily_stat',
        'schedule': crontab(minute=0, hour='*')
    },
}
