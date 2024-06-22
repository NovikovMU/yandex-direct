import os

from dotenv import load_dotenv
import telebot
from telebot import types

# from create_connection import PostgreSQLConnection
# from fetch_data import fetch_data, redis_connection


load_dotenv()
bot_token = os.getenv('YANDEX_DIRECT_MANAGER_API')
manager_bot = telebot.TeleBot(bot_token)
M_CHAT_ID = int(os.getenv('MANAGER_CHAT_ID'))


@manager_bot.message_handler(commands=['start'])
def start(message: types.Message):
    text = ('Hello')
    manager_bot.send_message(message.chat.id, text)


@manager_bot.message_handler(commands=['add'])
def add(message: types.Message):
    if message.chat.id == M_CHAT_ID:
        text = (
            'Написать свой ник в яндекс директе и лимит затрат, мне придёт '
            'уведомление, запись появится в бд.'
        )
        manager_bot.send_message(message.chat.id, text)
        manager_bot.register_next_step_handler(message, add_to_db)


# @manager_bot.message_handler(commands=['check'])
# def check(message: types.Message):
#     if message.chat.id == M_CHAT_ID:
#         with PostgreSQLConnection() as cursor:
#             cursor.execute("SELECT * FROM testusers")
#             query = cursor.fetchall()
#             for element in query:
#                 manager_bot.send_message(M_CHAT_ID, str(element))


def add_to_db(message: types.Message):
    # менять поле just_registered на false
    pass

if __name__ == '__main__':
    manager_bot.polling(non_stop=True)
