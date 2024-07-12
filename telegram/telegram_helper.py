import json
import os

from dotenv import load_dotenv
import telebot
from telebot import types
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
    bot.register_next_step_handler(message, enter_data_in_db)


@bot.message_handler(commands=['set_time'])
def set_time(message: Message):
    text = (
        'Пользователь может настроить рассылку на состояние кампаний по '
        'времени. Если ведено время + timezone, то появится запись в бд'
    )
    bot.send_message(message.chat.id, text)


@bot.message_handler(commands=['my_accounts'])
def my_accounts(message: Message):
    with PostgreSQLConnection() as cursor:
        cursor.execute(
            '''
                SELECT
                    name,
                    upper_limit,
                    is_verified,
                    is_entered_into_user_list
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
    markup = types.InlineKeyboardMarkup()
    ar = []
    for i in range(len(data)):
        account = data[i]
        name = account[0]
        dumped_data = json.dumps(account)
        button = types.InlineKeyboardButton(
            name,
            callback_data='account|' + dumped_data
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
def account_query(call):
    # call.data looks like:
    # 'account|[account_name, amount, is_verified, is_entered_into_user_list]'
    dumped_json = call.data.split('|')[1]
    data = json.loads(dumped_json)
    is_verified = 'подтверждён' if data[2] else 'не подтверждён'
    is_has_limit = data[1] if data[1] else 'лимиты не введены'
    text = (
        f'Ваш аккуант - {data[0]}. '
        f'Ваш лимит для аккаунта - {is_has_limit}. '
        f'Ваш аккаунт {is_verified}'
    )
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=text,
        reply_markup=set_up_account(dumped_json)
    )
    pass


@bot.callback_query_handler(
    func=lambda
    call: call.data.startswith('delete')
)
def delete_query(call):
    dumped_data = call.data.split('|')[1]
    account_name = json.loads(dumped_data)[0]
    with PostgreSQLConnection() as cursor:
        cursor.execute(
            """
            DELETE FROM accounts
            WHERE name = %s;
            """,
            (account_name,)
        )
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f'Ваш аккаунт {account_name} удалён.',
    )


@bot.callback_query_handler(
    func=lambda
    call: call.data.startswith('set_up')
)
def set_up_query(call):
    # call.data looks like:
    # 'set_up|action|[account_name, amount, is_verified, is_entered_into_user_list]'
    call_data = call.data.split('|')
    dumped_json = call_data[2]
    data = json.loads(dumped_json)
    if call_data[1] == 'confirm':
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text='Логика подтверждения яндекс аккаунта',
        )
    elif call_data[1] == 'change_limmit':
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text='Введите верхнюю границу расходов целым числом.',
        )
        bot.register_next_step_handler(
            call.message,
            change_limit_in_db,
            data[0]
        )
    else:
        text = (
            'Вы точно хотите удалить яндекс аккаунт? Если захотите добавить '
            'его снова, вам придётся потверждать его снова.'
        )
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=text,
            reply_markup=delete_accuont(dumped_json)
        )


def change_limit_in_db(message: Message, account_name):
    text = message.text.split()
    if len(text) > 1:
        bot.send_message(
            message.chat.id,
            'Верхняя граница расходов должна быть без пробелов.'
        )
        bot.register_next_step_handler(
            message,
            change_limit_in_db,
            account_name
        )
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
        bot.register_next_step_handler(
            message,
            change_limit_in_db,
            account_name
        )
        return
    with PostgreSQLConnection() as cursor:
        cursor.execute(
            """
            UPDATE accounts
            SET upper_limit = %s
            WHERE name = %s;
            """,
            (upper_limit, account_name)
        )
    bot.send_message(
        message.chat.id,
        f'Лимиты для аккаунта {account_name} сохранены.'
    )


def enter_data_in_db(message: Message):
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
    # check account_name for uniqueness
    account_name = message.text
    with PostgreSQLConnection() as cursor:
        cursor.execute(
                'SELECT 1 FROM accounts WHERE name = %s',
                (account_name,)
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
            (account_name, message.chat.id)
        )
    confirm_account(account_name, message.chat.id)
    bot.send_message(
        message.chat.id,
        'Аккаунт создан. Введите верхнюю границу расходов целым числом.'
    )
    bot.register_next_step_handler(message, change_limit_in_db, account_name)


def set_up_account(account_data: str) -> types.InlineKeyboardMarkup:
    data = json.loads(account_data)
    keyboard = types.InlineKeyboardMarkup()
    confirm = types.InlineKeyboardButton(
        'Подтвердить аккаунт',
        callback_data=f'set_up|confirm|{account_data}'
    )
    change = types.InlineKeyboardButton(
        'Изменить верхнюю границу',
        callback_data=f'set_up|change_limmit|{account_data}'
    )
    delete = types.InlineKeyboardButton(
        'Удалить аккаунт',
        callback_data=f'set_up|delete|{account_data}'
    )
    keyboard.add(change, delete)
    if data[3]:
        keyboard.add(confirm)
    return keyboard


def delete_accuont(account_data: str) -> types.InlineKeyboardMarkup:
    keyboard = types.InlineKeyboardMarkup()
    delete = types.InlineKeyboardButton(
        'Да удалить',
        callback_data=f'delete|{account_data}'
    )
    cancel = types.InlineKeyboardButton(
        'Нет отсавить',
        callback_data=f'account|{account_data}'
    )
    keyboard.add(delete, cancel)
    return keyboard


command_function = {
    '/set_account': set_account,
    '/start': start,
    '/how_add': how_add,
    '/set_account': set_account,
    '/set_time': set_time,
    '/my_accounts': my_accounts,
    '/help': help,
}


if __name__ == '__main__':
    bot.polling(non_stop=True)
