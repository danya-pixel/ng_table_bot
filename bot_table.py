import datetime
import os

import telebot
from telebot import types

from get_table import get_table, Day

token = os.getenv('TG_TOKEN')
if not token:
    raise ValueError('Token not found. Put it in ENV:TG_TOKEN')
bot = telebot.TeleBot(token)

cache_user = dict()

days_names = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб']
days_names_lower = ['пн', 'вт', 'ср', 'чт', 'пт', 'сб']


def get_user_cache(chat_id):
    user = cache_user[chat_id]
    return user


def send_timetable(user, day_of_week, is_tomorrow, **kwargs):
    day = Day(day_of_week=day_of_week, is_tomorrow=is_tomorrow)
    timetable = get_table(group=user['group'], course=user['course'], day=day)
    print(user, timetable)
    timetable_prepared = [f'{item[0]}: {item[1]}\n' for item in timetable]

    str_timetable = "\n".join(timetable_prepared)

    bot.send_message(user["user_id"],
                     text=f'Группа {user["group"]} и ты с{"" if user["course"] == 1 else "о"} {user["course"]} курса!\n'
                          f'Вот твое расписание на {day.get_full_day_name()} ({"не" if not day.is_even_week else ""}'
                          f'четная неделя):\n\n{str_timetable}',
                     **kwargs)


def generate_keyboard(btns_title):
    keyboard = types.ReplyKeyboardMarkup(row_width=7, resize_keyboard=True)
    for btn_row in btns_title:
        btns = [types.KeyboardButton(text=btn) for btn in btn_row]
        keyboard.add(*btns)
    return keyboard


@bot.message_handler(commands=['start'])
def start_message(message):
    try:
        user = get_user_cache(message.chat.id)
        bot.send_message(message.from_user.id,
                         text=f'Привет{", @" + user["username"] if user["username"] is not None else ""}!\n'
                              f'Я правильно помню, что твоя группа: {user["group"]}?\n'
                              f'Если я не прав подскажи мне свою группу',
                         reply_markup=None)

    except KeyError:
        bot.send_message(message.from_user.id, text='Привет! Какая у тебя группа?',
                         reply_markup=generate_keyboard([['19137', '19144'], ['20137', '20144']]))

    # bot.register_next_step_handler(message, get_group)


@bot.message_handler(regexp='^\\d{5}$')
def set_group(message):
    try:
        cache_user[message.chat.id] = {
            "group": int(message.text),
            "username": message.chat.username,
            "course": (datetime.datetime.now().year // 100 - int(message.text[:2])) + 1,
            "user_id": message.from_user.id
        }
        user = cache_user[message.chat.id]

    except ValueError:
        try:
            user = cache_user[message.chat.id]
        except KeyError:
            return

    today = datetime.datetime.now().weekday()
    days_names_without_current = ['Сегодня', 'Завтра', *[day for day_idx, day in enumerate(days_names) if
                                                         day_idx not in (today, (today + 1) % 6)]]
    btns_title = [['Сегодня', 'Завтра'], days_names, ['Поменять группу']]

    print(days_names_without_current)
    send_timetable(user=user, day_of_week=None, is_tomorrow=False, reply_markup=generate_keyboard(btns_title))


@bot.message_handler(content_types=['text'])
def catch_day_of_week(message):
    try:
        user = cache_user[message.chat.id]
        chosen_day = message.text.lower()
    except KeyError as err:
        start_message(message)
        return

    if chosen_day == 'сегодня':
        send_timetable(user=user, day_of_week=None, is_tomorrow=False)
    elif chosen_day == 'завтра':
        send_timetable(user=user, day_of_week=None, is_tomorrow=True)
    elif chosen_day in days_names_lower:
        send_timetable(user=user, day_of_week=days_names_lower.index(chosen_day), is_tomorrow=False)
    elif chosen_day == 'поменять группу':
        bot.send_message(message.from_user.id, text='Какая у тебя группа?',
                         reply_markup=generate_keyboard([['19137', '19144'], ['20137', '20144']]))


bot.polling()
