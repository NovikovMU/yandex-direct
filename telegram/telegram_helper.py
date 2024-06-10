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


@bot.message_handler(commands=['test'])
def start(message: types.Message):
    bot.send_message(message.chat.id, message)


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


@bot.message_handler(commands=['set_account'])
def add_account(message: types.Message):
    text = (
        'Напишите свой ник.'
    )
    bot.send_message(message.chat.id, text)
    bot.register_next_step_handler(message, enter_data_in_db)


@bot.message_handler(commands=['set_amount'])
def add_amount(message: types.Message):
    text = (
        'Введите сумму, которую не должен превышать дневной.'
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


@bot.message_handler(commands=['my_accounts'])
def accounts(message: types.Message):

    bot.send_message(message.chat.id, 'Доступные вам аккаунты яндекса директа', reply_markup=create_account_buttons())


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
    for i in range(1,7):
        ar.append(button1)
    keyboard.add(*ar)
    # keyboard.add(button3)
    return keyboard


def change_amount_in_db(message: types.Message):
    text = message.text.split()
    if len(text) > 1:
        bot_manager.send_message(
            message.chat.id,
            'Верхняя граница расходов должна быть без пробелов.'
        )
        bot.register_next_step_handler(message, change_amount_in_db)
        return
    # check if user call base function
    next_function = command_function.get(text[0])
    if next_function:
        next_function(message)
        return
    if not isinstance(text[0], (int, float)):
        bot_manager.send_message(
            message.chat.id,
            'Верхняя граница расходов должна быть числом.'
        )
        bot.register_next_step_handler(message, change_amount_in_db)
    with PostgreSQLConnection() as cursor:
        cursor.execute(
            """
            UPDATE accounts
            SET amount = %s
            WHERE user_id = %s AND amount is NULL;
            """,
            (text[0], message.chat.id)
        )
    bot.send_message(
        message.chat.id, 'Регистрация закончилась.'
    )


def enter_data_in_db(message: types.Message):
    text = message.text.split()
    if len(text) > 1:
        bot_manager.send_message(
            message.chat.id, 'Логин должен быть одним словом.'
        )
        bot.register_next_step_handler(message, enter_data_in_db)
        return
    # check if user call base function
    next_function = command_function.get(text[0])
    if next_function:
        next_function(message)
        return
    with PostgreSQLConnection() as cursor:
        cursor.execute(
                'SELECT 1 FROM accounts WHERE name = %s',
                (text[0],)
            )
        if cursor.fetchone() is not None:
            bot.send_message(
                message.chat.id, 'Вы ввели существующий аккаунт.'
            )
            bot.register_next_step_handler(message, enter_data_in_db)
            return

    with PostgreSQLConnection() as cursor:
        cursor.execute(
            """
            INSERT INTO users (telegram_id)
            VALUES (%s)
            ON CONFLICT (telegram_id) DO NOTHING
            """,
            (message.chat.id,)
        )
        
    with PostgreSQLConnection() as cursor:
        cursor.execute(
            """
            INSERT INTO accounts (name, user_id)
            VALUES (%s, %s)
            """,
            (text[0], message.chat.id)
        )
    bot.send_message(
        message.chat.id, 'Введите количество.'
    )
    bot.register_next_step_handler(message, change_amount_in_db)


@bot.message_handler(func=lambda message: True)
def handle_unknown_command(message):
    if message.text.startswith('/'):
        command = command_function.get(message)
        if not command:
            bot.send_message(message.chat.id, "Такой команды нет.")
    else:
        bot.send_message(message.chat.id, "Я не понимаю этот запрос.")


command_function = {
    '/add_account': add_account,
    # '/locations': locations,
    '/start': start,
}

bot.polling(non_stop=True)
