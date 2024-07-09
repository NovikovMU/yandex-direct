import os

from dotenv import load_dotenv
import telebot
from telebot import types

from create_table import create_table


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


def confirm_account(message: str) -> None:
    markup = telebot.types.InlineKeyboardMarkup()
    button1 = telebot.types.InlineKeyboardButton(
        'Да',
        callback_data=f'Да|{message}'
    )
    button2 = telebot.types.InlineKeyboardButton(
        'Нет',
        callback_data=f'Нет|{message}'
    )
    markup.add(button1, button2)
    manager_bot.send_message(
        M_CHAT_ID, message, reply_markup=markup
    )


@manager_bot.callback_query_handler(
    func=lambda call: call.data.startswith('Да') or
    call.data.startswith('Нет')
)
def callback_query(call):
    callback, message = call.data.split('|')
    if callback == 'Да':
        bot.send_message(
            call.message.chat.id,
            f'Вы успешно зарегистрировали аккаунт {message}.'
        )
    else:
        bot.send_message(
            call.message.chat.id,
            f'Мы не смогли найти аккаунт {message}.'
        )
    manager_bot.edit_message_reply_markup(
        call.message.chat.id,
        call.message.message_id,
        reply_markup=None
    )


if __name__ == '__main__':
    manager_bot.polling(non_stop=True)
