import datetime

from data.google_api import get_sheet_values

cache_data_dict = dict()
cache_data_time = dict()


class Day:
    day: datetime.datetime = None
    days_names_full = ['понедельник', 'вторник', 'среду', 'четверг', 'пятницу', 'субботу']

    def __init__(self, day_of_week: int or None, is_tomorrow: bool = False, is_even: bool or None = None):
        first_week = datetime.date(2020, 9, 1)
        self.today = datetime.datetime.now()
        if day_of_week is None:
            self.day = self.today + datetime.timedelta(days=is_tomorrow)
            if self.day.weekday() == 6:
                self.day += datetime.timedelta(days=1)
        elif 6 > day_of_week >= 0:
            now_day_of_week = self.today.weekday()
            self.day = self.today + datetime.timedelta(days=day_of_week - now_day_of_week)
        else:
            raise ValueError("No correct date")

        self.is_even_week = (self.day.isocalendar()[1] - first_week.isocalendar()[1]) % 2 == 1
        if is_even is not None and self.is_even_week != is_even:
            self.day += datetime.timedelta(days=7)
            self.is_even_week = is_even
        self.day_of_week = self.day.weekday()

    def get_full_day_name(self):
        return self.days_names_full[self.day_of_week]

    def __str__(self):
        return self.day.strftime("%d.%m.%Y")


# def cache_data(func):
#     global cache_data_dict
#
#     def memoized_func(group: int, course: int, day: Day, is_need_clean_end: bool = True, is_even: bool or None = None):
#         today = datetime.datetime.now()
#         cache_idx = str(day) + f'-{group}:{int(is_need_clean_end)}'
#
#         if cache_idx in cache_data_dict and cache_data_dict[cache_idx].get('time').day == today.day \
#                 and cache_data_dict[cache_idx].get('time').hour + 4 >= today.hour:
#             return cache_data_dict[cache_idx]['result']
#         result = func(group=group, course=course, day=day, is_need_clean_end=is_need_clean_end)
#         cache_data_dict[cache_idx] = {
#             "result": result,
#             "time": datetime.datetime.now()
#         }
#         init_cache()
#         return result
#
#     return memoized_func


# @cache_data
def get_table(group: int, course: int, day: Day, is_need_clean_end: bool = True):
    # group = 19144
    # is_tomorrow = int(is_tomorrow)
    # if day_of_week is None:
    #     today = datetime.datetime.now().weekday() + is_tomorrow
    # else:
    #     today = day_of_week
    start_column_index = 0 if str(group)[-2:] == "37" else 8

    data = get_sheet_values(
        f'{course} курс 2 недели!{"D3:Q7" if  day.is_even_week else "D10:Q14"}')
    time_data = [time[0] for time in get_sheet_values(f'{course} курс 2 недели!C3:C7')]

    today_idx = start_column_index + day.day_of_week

    for row in data:
        while len(row) < 14:
            row.append('')

    timetable = [row[today_idx].replace(
        '\n', ' ') if row[today_idx] != '' else 'Окно' for row in data]

    while is_need_clean_end and timetable[-1] == 'Окно':
        timetable.pop(-1)

    lessons = list(zip(time_data, timetable))

    return lessons


def init_cache():
    # import threading
    # threads = list()
    print('Start caching')
    for day_of_week in range(6):
        day = Day(day_of_week=day_of_week, is_tomorrow=False, is_even=True)
        day2 = Day(day_of_week=day_of_week, is_tomorrow=False, is_even=False)
        for group, course in [(19137, 2), (19144, 2), (20137, 1), (20144, 1)]:
            get_table(group=group, course=course, day=day)
            get_table(group=group, course=course, day=day2)
            # x = threading.Thread(target=get_table, kwargs=dict(group=group, course=course, day=day))
            # threads.append(x)
            # x.start()
            # x = threading.Thread(target=get_table, kwargs=dict(group=group, course=course, day=day2))
            # threads.append(x)
            # x.start()

    # for index, thread in enumerate(threads):
    #     thread.join()

if __name__ == '__main__':
    d = Day(day_of_week=None, is_tomorrow=True)
    print(d.get_full_day_name())
    print(get_table(19137, 2, d, is_need_clean_end=False))
    print(get_table(19137, 2, d, is_need_clean_end=False))
