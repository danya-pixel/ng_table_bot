import datetime

from data.google_api import get_sheet_values

cache_data_dict = dict()
cache_data_time = dict()


def cache_data(func):
    import json
    global cache_data_dict

    def memoized_func(**kwargs):
        str_kwargs = json.dumps(kwargs)
        today = datetime.datetime.now()
        if str_kwargs in cache_data_dict and cache_data_dict[str_kwargs].get('time').day == today.day \
                and cache_data_dict[str_kwargs].get('time').hour + 4 >= today.hour:
            return cache_data_dict[str_kwargs]["result"]
        result = func(**kwargs)
        cache_data_dict[str_kwargs] = {
            "result": result,
            "time": datetime.datetime.now()
        }
        return result

    return memoized_func


@cache_data
def get_table(group: int, day_of_week: int, course: int, is_tomorrow: bool = False):
    # group = 19144
    is_tomorrow = int(is_tomorrow)
    if day_of_week is None:
        today = datetime.datetime.now().weekday() + is_tomorrow
    else:
        today = day_of_week
    start_column_index = 0 if str(group)[-2:] == "37" else 8

    data = get_sheet_values(f'{course} курс!C3:P7')
    time_data = [time[0] for time in get_sheet_values(f'{course} курс!B3:B7')]

    today_idx = start_column_index + today

    for row in data:
        while len(row) < 14:
            row.append('')

    timetable = [row[today_idx].replace('\n', ' ') if row[today_idx] != '' else 'Окно' for row in data]

    lessons = list(zip(time_data, timetable))

    return lessons


if __name__ == '__main__':
    print(get_table(19137, False)[0])
