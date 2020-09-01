import telebot
from telebot import types
from get_table import get_table

bot = telebot.TeleBot('1231314161:AAFNQ-RB_AIaihSEdL8cKoZhoe3YvgzIviQ')

cache = {}


def get_user_cache(chat_id):
    user = cache[chat_id]
    return user


@bot.message_handler(commands=['start'])
def start_message(message):
    try:
        user = get_user_cache(message.chat.id)
        bot.send_message(message.from_user.id,
                         text=f'Привет, @{user["username"]}!\nЯ правильно помню, что твоя группа: {user["group"]}?\nЕсли я не прав подскажи мне свою группу\n'
                              f'Твое расписание на сегодня: ', reply_markup=None)
        get_timetable(message)
    except KeyError:
        button_19137 = types.KeyboardButton(text="19137")
        button_19144 = types.KeyboardButton(text="19144")

        keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        keyboard.add(button_19137, button_19144)
        bot.send_message(message.from_user.id, text='Привет! Какая у тебя группа?', reply_markup=keyboard)

    # bot.register_next_step_handler(message, get_group)


@bot.message_handler(regexp='^\\d{5}$')
@bot.message_handler(content_types=['text'])
def get_timetable(message):

    try:
        cache[message.chat.id] = {"group": int(message.text), "username": message.chat.username}
    except ValueError:
        try:
            user = cache[message.chat.id]
        except KeyError:
            return
    user = cache[message.chat.id]

    timetable = [f'{item[0]}: {item[1]}\n' for item in get_table(user['group'], False)]

    str_timetable = "\n".join(timetable)
    bot.send_message(message.from_user.id,
                     text=f'Я запомнил, что твоя группа {user["group"]}!\n'
                          f'Вот твое расписание на сегодня:\n{str_timetable}',
                     reply_markup=None)


bot.polling()
