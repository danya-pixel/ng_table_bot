import telebot
from telebot import types
import datetime
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
        keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=False)
        for group in ('19137', '19144', '20137', '20144'):
            btn = types.KeyboardButton(text=group)
            keyboard.add(btn)
        bot.send_message(message.from_user.id, text='Привет! Какая у тебя группа?', reply_markup=keyboard)

    # bot.register_next_step_handler(message, get_group)

@bot.message_handler(regexp='^\\d{5}$')
@bot.message_handler(content_types=['text'])
def get_timetable(message):
    try:
        cache[message.chat.id] = {
                                "group": int(message.text), 
                                "username": message.chat.username, 
                                "course":  (datetime.datetime.now().year // 100 - int(message.text[:2])) + 1
                                }
    except ValueError:
        try:
            user = cache[message.chat.id]
        except KeyError:
            return
    user = cache[message.chat.id]
    timetable = get_table(user['group'], day_of_week=None, course=user['course'])
    print(user, timetable)
    timetable_prepared = [f'{item[0]}: {item[1]}\n' for item in timetable ]

    str_timetable = "\n".join(timetable_prepared)
    bot.send_message(message.from_user.id,
                     text=f'Я запомнил, что твоя группа {user["group"]} и ты с {user["course"]} курса!\n'
                          f'Вот твое расписание на сегодня:\n{str_timetable}',
                     reply_markup=None)
    # TODO: add keyboard to reply markup with сегодня, завтра . Пн, вт, ср, чт, пт, сб

bot.polling()
