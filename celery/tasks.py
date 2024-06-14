from celery_app import app
from fetch_data import fetch_data

from telegram_helper import bot

@app.task(max_retries=5)
def check_limits(id):
    bot.send_message(253892073, f"Вы попросили напомнить {id}.")

@app.task
def schedule_reminders():
    # Пример данных для демонстрации
    results = [1, 2, 3, 5, 6, 7]
    for element in results:
        check_limits.apply_async((element,), soft_time_limit=10)
# celery -A tasks worker --loglevel=info -P eventlet
# celery -A celery_app beat --loglevel=info


@app.task(max_retries=5, time_limit=5)
def time(id):
    import time
    time.sleep(10)
    bot.send_message(253892073, f"Вы попросили напомнить {id}.")