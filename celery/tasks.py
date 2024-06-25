import os

from celery.exceptions import SoftTimeLimitExceeded
from dotenv import load_dotenv
import telebot

from celery_app import app

load_dotenv()
bot_helper = os.getenv('YANDEX_DIRECT_HELPER_API')
M_CHAT_ID = os.getenv('MANAGER_CHAT_ID')
bot = telebot.TeleBot(bot_helper)


@app.task
def donation_alert():
    # send all verified person about donation
    pass


@app.task
def daily_stat():
    # send statistic about your account
    pass


@app.task(time_limit=3, soft_time_limit=2)
def amount_check():
    # check all account's spend limit
    pass
