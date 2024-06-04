import os
import sys
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from dotenv import load_dotenv
import telebot
from telebot import types

from postgresql.create_connection import PostgreSQLConnection

load_dotenv()
bot_token = os.getenv('YANDEX_DIRECT_HELPER_API')
bot = telebot.TeleBot(bot_token)

bot_manager_token = os.getenv('YANDEX_DIRECT_MANAGER_API')
bot_manager = telebot.TeleBot(bot_manager_token)


@bot.message_handler(commands=['start'])
def start(message: types.Message):
    text = ('Hello')
    bot.send_message(message.chat.id, text)


@bot.message_handler(commands=['how_add'])
def how_add(message: types.Message):
    text = (
        'Текст как добавить аккаунт для обозрения'
    )
    bot.send_message(message.chat.id, text)


@bot.message_handler(commands=['add'])
def add(message: types.Message):
    text = (
        'Напишите свой ник и границу расходов.'
    )
    bot.send_message(message.chat.id, text)
    bot.register_next_step_handler(message, enter_data_in_db)


@bot.message_handler(commands=['my_account'])
def add(message: types.Message):

    bot.send_message(message.chat.id, 'Доступные вам аккаунты яндекса директа', reply_markup=create_account_buttons())


@bot.message_handler(commands=['set_amount'])
def coordinates(message: types.Message):
    text = (
        'Сумма, за которую компании не должны выходить'
    )
    bot.send_message(message.chat.id, text)
    bot.register_next_step_handler(message, change_amount_in_db)


@bot.message_handler(commands=['set_time'])
def coordinates(message: types.Message):
    text = (
        'Пользователь может настроить рассылку на состояние кампаний по '
        'времени. Если ведено время + timezone, то появится запись в бд'
    )
    bot.send_message(message.chat.id, text)


@bot.message_handler(commands=['help'])
def coordinates(message: types.Message):
    text = (
        'Перечисление всех команд'
    )
    bot.send_message(message.chat.id, text)


def create_account_buttons():
    keyboard = types.InlineKeyboardMarkup()
    ar = []
    # if cash: fetch data from cash else: fetch data from db
    # element for list 
    button1 = types.InlineKeyboardButton("Креветки", callback_data='button1')
    button2 = types.InlineKeyboardButton("Крабы", callback_data='button2')
    button3 = types.InlineKeyboardButton("Длинная кнопка", callback_data='button3')
    button4 = types.InlineKeyboardButton("Длинная кнопка", callback_data='button3')
    button5 = types.InlineKeyboardButton("Длинная кнопка", callback_data='button3')
    button6 = types.InlineKeyboardButton("Длинная кнопка", callback_data='button3')
    for i in range(1,7):
        ar.append(button6)
    keyboard.add(*ar)
    # keyboard.add(button3)
    return keyboard


def change_amount_in_db(message: types.Message):
    # Ресет кеша
    pass


def enter_data_in_db(message: types.Message):
    text = message.text.split()
    # check if user call base function
    next_function = command_function.get(text[0])
    if next_function:
        next_function(message)
        return
    text.append(message.chat.id)
    insert_query = "INSERT INTO testusers (name, amount, user_id) VALUES (%s, %s, %s)"
    with PostgreSQLConnection() as cursor:
        cursor.execute(insert_query, text)
        bot_manager.send_message(message.chat.id, str(text))


@bot.message_handler(func=lambda message: True)
def handle_unknown_command(message):
    if message.text.startswith('/'):
        command = command_function.get(message)
        if not command:
            bot.send_message(message.chat.id, "Такой команды нет.")
    else:
        bot.send_message(message.chat.id, "Я не понимаю этот запрос.")


command_function = {
    '/add': add,
    # '/locations': locations,
    '/start': start,
}

bot.polling(non_stop=True)
