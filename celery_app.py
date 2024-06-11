from celery import Celery

app = Celery(
    'reminder',
    broker='redis://localhost:6379/1',
    backend='redis://localhost:6379/1'
)


@app.task
def check_limits(chat_id):
    print(chat_id)


app.conf.update(
    result_expires=3600,
    timezone='UTC',
    enable_utc=True,
)
