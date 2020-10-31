'''
Module providing methods for getting and formatting datetimes
'''
import datetime as dt

ERROR_DATETIME = 'xx-xx-xxxx xx:xx'


def convert_military_time(time):
    '''
    Converts 24-hour time to 12-hour

    :param time: 24-Hour time string value of form HH:MM
    '''
    tmp = dt.datetime.strptime(time, '%H:%M')
    return tmp.strftime('%I:%M %p')


def get_iso_timestamp():
    '''
    Get the current time in ISO format (xxxx-xx-xxTxx:xx:xx)

    :return: Current time in ISO format (precision = seconds)
    '''
    return dt.datetime.now().isoformat(timespec='seconds')


def format_timestamp(iso_timestamp, military=True):
    '''
    Formats ISO timestamp into string for displaying

    :param timestamp: ISO timestamp as string
    :param military: True for 24-hour time, false for 12-hour time
    :return: Properly formatted timestamp as string
    '''
    formatted_timestamp = ERROR_DATETIME

    try:
        # Separate ISO date and time
        sep_index = iso_timestamp.index('T')
        date = iso_timestamp[:sep_index]
        time = iso_timestamp[sep_index + 1:]

        # Format date and time
        if not military:
            time = convert_military_time(time)

        formatted_timestamp = date + ' ' + time

    except ValueError:
        # Something wrong with ISO date/time format
        pass

    return formatted_timestamp
