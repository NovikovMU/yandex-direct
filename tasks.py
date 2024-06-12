from celery_app import app
from fetch_data import fetch_data

from telegram_helper import bot

@app.task
def check_limits(id):
    bot.send_message(253892073, f"Вы попросили напомнить {id}.")

@app.task
def schedule_reminders():
    # Пример данных для демонстрации
    results = [1, 2, 3, 5, 6, 7]
    for element in results:
        check_limits.apply_async((element,))
# celery -A tasks worker --loglevel=info -P eventlet
# celery -A celery_app beat --loglevel=info