import telebot
from telebot import types
import datetime
from get_table import get_table, isEven_week
import os

token = os.getenv('TG_TOKEN')
bot = telebot.TeleBot(token)

cache_user = dict()

days_names = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб']
days_names_lower = ['пн', 'вт', 'ср', 'чт', 'пт', 'сб']
days_names_full = ['понедельник', 'вторник', 'среду', 'четверг', 'пятницу', 'субботу']


def get_user_cache(chat_id):
    user = cache_user[chat_id]
    return user


def day_of_week(user, day, is_tomorrow, **kwargs):
    timetable = get_table(group=user['group'], day_of_week=day, course=user['course'], is_tomorrow=is_tomorrow)
    print(user, timetable)
    timetable_prepared = [f'{item[0]}: {item[1]}\n' for item in timetable]

    str_timetable = "\n".join(timetable_prepared)

    if day is None:
        day_name = "завтра" if is_tomorrow else "сегодня"
    else:
        day_name = days_names_full[day]
    bot.send_message(user["user_id"],
                     text=f'Группа {user["group"]} и ты {"с" if user["course"] == 1 else "со"} {user["course"]} курса!\n'
                          f'Вот твое расписание на {day_name} ({"не" if not isEven_week() else ""}четная неделя):\n\n{str_timetable}',
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
                              f'Если я не прав подскажи мне свою группу'
                         , reply_markup=None)

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
    day_of_week(user=user, day=None, is_tomorrow=False, reply_markup=generate_keyboard(btns_title))


@bot.message_handler(content_types=['text'])
def catch_day_of_week(message):
    try:
        user = cache_user[message.chat.id]
        chosen_day = message.text.lower()
    except KeyError as err:
        start_message(message)
        return

    if chosen_day == 'сегодня':
        day_of_week(user=user, day=None, is_tomorrow=False)
    elif chosen_day == 'завтра':
        day_of_week(user=user, day=None, is_tomorrow=True)
    elif chosen_day in days_names_lower:
        day_of_week(user=user, day=days_names_lower.index(chosen_day), is_tomorrow=False)
    elif chosen_day == 'поменять группу':
        bot.send_message(message.from_user.id, text='Какая у тебя группа?',
                         reply_markup=generate_keyboard([['19137', '19144'], ['20137', '20144']]))


bot.polling()
