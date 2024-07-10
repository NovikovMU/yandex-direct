import json
import os

from dotenv import load_dotenv
import telebot
from telebot.types import Message

from create_connection import PostgreSQLConnection
from telegram_manager import confirm_account


load_dotenv()
bot_token = os.getenv('YANDEX_DIRECT_HELPER_API')
bot = telebot.TeleBot(bot_token)


M_CHAT_ID = os.getenv('MANAGER_CHAT_ID')


@bot.message_handler(commands=['start'])
def start(message: Message):
    text = ('Hello')
    bot.send_message(message.chat.id, text)


@bot.message_handler(commands=['how_add'])
def how_add(message: Message):
    text = (
        'Текст как добавить аккаунт для обозрения'
    )
    bot.send_message(message.chat.id, text)


@bot.message_handler(commands=['set_account'])
def set_account(message: Message):
    text = (
        'Напишите свой ник.'
    )
    bot.send_message(message.chat.id, text)
    bot.register_next_step_handler(
        message,
        lambda m: enter_data_in_db(m)
    )


@bot.message_handler(commands=['set_limit'])
def add_limit(message: Message):
    text = (
        'Введите сумму, которую не должен превышать дневной расход.'
    )
    bot.send_message(message.chat.id, text)
    bot.register_next_step_handler(message, change_limit_in_db)


@bot.message_handler(commands=['set_time'])
def add_time(message: Message):
    text = (
        'Пользователь может настроить рассылку на состояние кампаний по '
        'времени. Если ведено время + timezone, то появится запись в бд'
    )
    bot.send_message(message.chat.id, text)


@bot.message_handler(commands=['my_accounts'])
def accounts(message: Message):
    with PostgreSQLConnection() as cursor:
        cursor.execute(
            '''
                SELECT name, upper_limit, is_verified
                FROM accounts WHERE user_id = %s
            ''',
            (message.chat.id,)
        )
        data = cursor.fetchall()
    if not data:
        bot.send_message(
            message.chat.id,
            'У вас нет никаких аккаунтов, запустите команду /set_account'
        )
        return
    markup = telebot.types.InlineKeyboardMarkup()
    ar = []
    for i in range(len(data)):
        account = data[i]
        name = account[0]
        str_account = json.dumps(account)
        button = telebot.types.InlineKeyboardButton(
            name,
            callback_data='account|' + str_account
        )
        ar.append(button)
    markup.add(*ar)
    bot.send_message(
        message.chat.id,
        'Ваши аккаунты.',
        reply_markup=markup
    )


@bot.message_handler(commands=['help'])
def help(message: Message):
    text = (
        'Перечисление всех команд'
    )
    bot.send_message(message.chat.id, text)


def change_limit_in_db(message: Message):
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
        message.chat.id,
        'Подтвердите, что вы являетесь владельцем этого аккаунта'
    )
    bot.register_next_step_handler(message, verify_account)


def enter_data_in_db(message: Message, account_name=None):
    text = message.text.split()
    if len(text) > 1:
        bot.send_message(
            message.chat.id, 'Логин должен быть одним словом.'
        )
        bot.register_next_step_handler(
            message,
            lambda m: enter_data_in_db(m, account_name)
        )
        return
    # check if user call base function
    next_function = command_function.get(text[0])
    if next_function:
        next_function(message)
        return
    with PostgreSQLConnection() as cursor:
        cursor.execute(
                'SELECT 1 FROM accounts WHERE name = %s',
                (message.text,)
            )
        if cursor.fetchone() is not None:
            bot.send_message(
                message.chat.id, 'Вы ввели существующий аккаунт.'
            )
            bot.register_next_step_handler(
                message,
                lambda m: enter_data_in_db(m, account_name)
            )
            return
    account_name = account_name if account_name else message.text
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
            (account_name, message.chat.id)
        )
    confirm_account(text[0])
    bot.send_message(
        message.chat.id, 'Введите верхнюю границу расходов целым числом.'
    )
    bot.register_next_step_handler(message, change_limit_in_db)


def verify_account(message: Message):
    pass


@bot.message_handler(func=lambda message: True)
def handle_unknown_command(message: Message):
    if message.text.startswith('/'):
        command = command_function.get(message)
        if not command:
            bot.send_message(message.chat.id, "Такой команды нет.")
    else:
        bot.send_message(message.chat.id, "Я не понимаю этот запрос.")


@bot.callback_query_handler(
    func=lambda
    call: call.data.startswith('account')
)
def callback_query(call):
    data = json.loads(call.data.split('|')[1])
    is_auntification = 'подтверждён' if bool(data[2]) else 'не подтверждён'
    text = (
        f'Ваш аккуант - {data[0]}. Ваш лимит для аккаунта - {data[1]} ' +
        f'Ваш аккаунт {is_auntification}'
    )
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=text,
        # reply_markup=create_inline_button()
    )
    pass


command_function = {
    '/set_account': set_account,
    '/start': start,
}

if __name__ == '__main__':
    bot.polling(non_stop=True)
