import datetime

current_time = None


def get_current_time():
    return datetime.datetime.strptime(current_time, '%H:%M').time()
