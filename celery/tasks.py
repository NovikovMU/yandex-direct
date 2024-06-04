from celery import app
import telebot
from models import Session, Reminder
from datetime import datetime

API_TOKEN = 'YOUR_TELEGRAM_BOT_API_TOKEN'
bot = telebot.TeleBot(API_TOKEN)

@app.task
def send_reminder(chat_id):
    bot.send_message(chat_id, "Вы попросили напомнить.")
    # Удаляем напоминание после отправки
    session = Session()
    session.query(Reminder).filter(Reminder.chat_id == chat_id).delete()
    session.commit()
    session.close()

def schedule_reminders():
    session = Session()
    now = datetime.now().time()
    reminders = session.query(Reminder).filter(Reminder.time <= now).all()
    for reminder in reminders:
        send_reminder.apply_async((reminder.chat_id,))
        session.delete(reminder)
    session.commit()
    session.close()

app.conf.beat_schedule = {
    'check-reminders-every-minute': {
        'task': 'tasks.schedule_reminders',
        'schedule': 60.0,  # Запускать каждые 60 секунд
    }
}
