import os

from dotenv import load_dotenv
import telebot
from telebot import types

from create_connection import PostgreSQLConnection


load_dotenv()
bot_token = os.getenv('YANDEX_DIRECT_HELPER_API')
bot = telebot.TeleBot(bot_token)

bot_manager_token = os.getenv('YANDEX_DIRECT_MANAGER_API')
bot_manager = telebot.TeleBot(bot_manager_token)

M_CHAT_ID = os.getenv('MANAGER_CHAT_ID')


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
def set_account(message: types.Message):
    text = (
        'Напишите свой ник.'
    )
    bot.send_message(message.chat.id, text)
    bot.register_next_step_handler(message, enter_data_in_db)


@bot.message_handler(commands=['set_limit'])
def add_limit(message: types.Message):
    text = (
        'Введите сумму, которую не должен превышать дневной расход.'
    )
    bot.send_message(message.chat.id, text)
    bot.register_next_step_handler(message, change_limit_in_db)


@bot.message_handler(commands=['set_time'])
def add_time(message: types.Message):
    text = (
        'Пользователь может настроить рассылку на состояние кампаний по '
        'времени. Если ведено время + timezone, то появится запись в бд'
    )
    bot.send_message(message.chat.id, text)


@bot.message_handler(commands=['my_accounts'])
def accounts(message: types.Message):
    # необходимо добавить reply_markup
    bot.send_message(
        message.chat.id,
        'Доступные вам аккаунты яндекса директа'
    )


@bot.message_handler(commands=['help'])
def help(message: types.Message):
    text = (
        'Перечисление всех команд'
    )
    bot.send_message(message.chat.id, text)


def change_limit_in_db(message: types.Message):
    text = message.text.split()
    if len(text) > 1:
        bot.send_message(
            message.chat.id,
            'Верхняя граница расходов должна быть без пробелов.'
        )
        bot.register_next_step_handler(message, change_limit_in_db)
        return
    # check if user call base function
    next_function = command_function.get(text[0])
    if next_function:
        next_function(message)
        return
    try:
        upper_limit = int(text[0])
    except ValueError:
        bot.send_message(
            message.chat.id,
            'Верхняя граница расходов должна быть целым числом.'
        )
        bot.register_next_step_handler(message, change_limit_in_db)
        return
    with PostgreSQLConnection() as cursor:
        cursor.execute(
            """
            UPDATE accounts
            SET upper_limit = %s
            WHERE user_id = %s AND upper_limit is NULL;
            """,
            (upper_limit, message.chat.id)
        )
    bot.send_message(
        message.chat.id, 'Регистрация закончилась.'
    )


def enter_data_in_db(message: types.Message):
    text = message.text.split()
    if len(text) > 1:
        bot.send_message(
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

    first_name = message.chat.first_name
    last_name = message.chat.last_name
    username = message.chat.username
    with PostgreSQLConnection() as cursor:
        cursor.execute(
            """
            INSERT INTO users (telegram_id, first_name, last_name, username)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (telegram_id) DO NOTHING
            """,
            (message.chat.id, first_name, last_name, username)
        )

    with PostgreSQLConnection() as cursor:
        cursor.execute(
            """
            INSERT INTO accounts (name, user_id)
            VALUES (%s, %s)
            """,
            (text[0], message.chat.id)
        )
    user_data = text[0] + ' ' + str(message.chat.id)
    bot_manager.send_message(
        M_CHAT_ID, user_data
    )
    bot.send_message(
        message.chat.id, 'Введите верхнюю границу расходов целым числом.'
    )
    bot.register_next_step_handler(message, change_limit_in_db)


@bot.message_handler(func=lambda message: True)
def handle_unknown_command(message):
    if message.text.startswith('/'):
        command = command_function.get(message)
        if not command:
            bot.send_message(message.chat.id, "Такой команды нет.")
    else:
        bot.send_message(message.chat.id, "Я не понимаю этот запрос.")


command_function = {
    '/set_account': set_account,
    '/start': start,
}

if __name__ == '__main__':
    bot.polling(non_stop=True)
