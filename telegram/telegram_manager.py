import os

from dotenv import load_dotenv
import telebot
from telebot import types

from create_connection import PostgreSQLConnection


load_dotenv()
bot_token = os.getenv('YANDEX_DIRECT_MANAGER_API')
bot = telebot.TeleBot(bot_token)
maksim_chat_id = os.getenv('MAKSIM_CHAT_ID')


@bot.message_handler(commands=['add'])
def add(message: types.Message):
    if message.chat.id == maksim_chat_id:
        text = (
            'Написать свой ник в яндекс директе и лимит затрат, мне придёт '
            'уведомление, запись появится в бд.'
        )
        bot.send_message(message.chat.id, text)
        bot.register_next_step_handler(message, add_to_db)


@bot.message_handler(commands=['check'])
def check(message: types.Message):
    if message.chat.id == maksim_chat_id:
        with PostgreSQLConnection() as cursor:
            cursor.execute("SELECT * FROM testusers")
            query = cursor.fetchall()
            for element in query:
                bot.send_message(maksim_chat_id, str(element))


def add_to_db(message: types.Message):
    # менять поле just_registered на false
    pass


bot.polling(non_stop=True)
