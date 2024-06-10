# from celery_app import app 
# import telebot
# from datetime import datetime

# API_TOKEN = 'YOUR_TELEGRAM_BOT_API_TOKEN'
# bot = telebot.TeleBot(API_TOKEN)

# @app.task
# def check_limits(chat_id):
#     print(chat_id)
#     # bot.send_message(chat_id, "Вы попросили напомнить.")


# def schedule_reminders():
#     results = fetch_data()
#     for element in results:
#         print(element)
#         check_limits.apply_async((element[2]))



# app.conf.beat_schedule = {
#     'check-reminders-every-minute': {
#         'task': 'tasks.schedule_reminders',
#         'schedule': 60.0,  # Запускать каждые 60 секунд
#     }
# }
