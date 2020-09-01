import datetime

from data.google_api import get_sheet_values


def get_table(group: int, is_tomorrow: bool, course: int):
    # group = 19144
    is_tomorrow = int(is_tomorrow)

    today = datetime.datetime.now().weekday() + is_tomorrow

    start_column_index = 0 if group == 19137 else 8

    data = get_sheet_values(f'{course} курс!C3:P7')
    time_data = [time[0] for time in get_sheet_values('2 курс!B3:B7')]

    today_idx = start_column_index + today

    for row in data:
        while len(row) < 14:
            row.append('')

    timetable = [row[today_idx].replace('\n', ' ') if row[today_idx] != '' else 'Окно' for row in data]

    lessons = list(zip(time_data, timetable))

    return lessons


if __name__ == '__main__':
    print(get_table(19137, False)[0])
