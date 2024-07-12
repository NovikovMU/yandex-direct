import os

from dotenv import load_dotenv
import telebot
from telebot import types

from create_table import create_table
from create_connection import PostgreSQLConnection


load_dotenv()
bot_token = os.getenv('YANDEX_DIRECT_HELPER_API')
bot = telebot.TeleBot(bot_token)

bot_token = os.getenv('YANDEX_DIRECT_MANAGER_API')
manager_bot = telebot.TeleBot(bot_token)
M_CHAT_ID = int(os.getenv('MANAGER_CHAT_ID'))


@manager_bot.message_handler(commands=['create'])
def start(message: types.Message):
    if message.chat.id == M_CHAT_ID:
        create_table()
        manager_bot.send_message(message.chat.id, 'Таблица создана.')


# @manager_bot.message_handler(commands=['check'])
# def check(message: types.Message):
#     if message.chat.id == M_CHAT_ID:
#         with PostgreSQLConnection() as cursor:
#             cursor.execute("SELECT * FROM testusers")
#             query = cursor.fetchall()
#             for element in query:
#                 manager_bot.send_message(M_CHAT_ID, str(element))


def confirm_account(account_name: str, user_id: int) -> None:
    markup = telebot.types.InlineKeyboardMarkup()
    button1 = telebot.types.InlineKeyboardButton(
        'Да',
        callback_data=f'Да|{account_name}|{user_id}'
    )
    button2 = telebot.types.InlineKeyboardButton(
        'Нет',
        callback_data=f'Нет|{account_name}|{user_id}'
    )
    markup.add(button1, button2)
    manager_bot.send_message(
        M_CHAT_ID, account_name, reply_markup=markup
    )


@manager_bot.callback_query_handler(
    func=lambda call: call.data.startswith('Да') or
    call.data.startswith('Нет')
)
def callback_query(call):
    callback, account_name, user_id = call.data.split('|')
    if callback == 'Да':
        with PostgreSQLConnection() as cursor:
            cursor.execute(
                """
                UPDATE accounts
                SET is_entered_into_user_list = True
                WHERE name = %s;
                """,
                (account_name,)
            )
        bot.send_message(
            user_id,
            f'Вы успешно зарегистрировали аккаунт {account_name}.'
        )
    else:
        bot.send_message(
            user_id,
            f'Мы не смогли найти аккаунт {account_name}.'
        )
    manager_bot.edit_message_reply_markup(
        call.message.chat.id,
        call.message.message_id,
        reply_markup=None
    )


if __name__ == '__main__':
    create_table()
    manager_bot.polling(non_stop=True)
