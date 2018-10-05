date_format = ('%b %d', '%H:%M:%S')


def set_monthday(event=None):
    global date_format
    date_format = ('%b %d', '%H:%M:%S')


def set_julian(event=None):
    global date_format
    date_format = ('%Y-%j', '%H:%M:%S')


def get_format(linebreak=True):
    if linebreak:
        spacer = '\n'
    else:
        spacer = ' '
    return date_format[0] + spacer + date_format[1]


def get_datetime(time, linebreak=True):

    fmt = get_format(linebreak)

    from datetime import datetime
    date = datetime.fromtimestamp(time)
    return date.strftime(fmt)
