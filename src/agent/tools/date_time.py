from datetime import date, timedelta


def get_today_datetime():
    '''Get date of current day'''
    return str(date.today())

def get_yesterday_datetime():
    '''Get yesterday date'''
    return str(date.today() - timedelta(days=1))
