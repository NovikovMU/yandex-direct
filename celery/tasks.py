import os

from celery.exceptions import SoftTimeLimitExceeded
from dotenv import load_dotenv
import telebot

from celery_app import app

load_dotenv()
bot_helper = os.getenv('YANDEX_DIRECT_HELPER_API')
M_CHAT_ID = os.getenv('MANAGER_CHAT_ID')
bot = telebot.TeleBot(bot_helper)


@app.task(time_limit=2, max_retries=5)
def time_task():
    import time
    time.sleep(3)
    bot.send_message(M_CHAT_ID, 'task is finished.')


@app.task
def schedule_reminders():
    # Пример данных для демонстрации
    bot.send_message(M_CHAT_ID, 'task is finished.')
