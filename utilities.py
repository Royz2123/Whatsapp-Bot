from threading import Lock
from datetime import datetime, timedelta
import pickle

mutex = Lock()

################ Utility Constants ################

DATE_FORMAT = "%H:%M,%d-%m-%Y"
DATE_FORMAT_FOR_FORMAT = "{0:0>2}:{0:0>2},{0:0>2}-{0:0>2}-{0:0>2}"

PARTS_ERROR = "There is not the right amount of parts, should be \"hour,date\""
HOUR_PARTS_ERROR = "There is not the right amount of parts in the hour section, should be \"hour:" \
                   "minute\""
HOUR_ERROR = "The hour should be between 00 and 23"
MINUTE_ERROR = "The minutes should be between 00 and 59"
DATE_PARTS_ERROR = "There is not the right amount of parts in the date section, should be \"day-" \
                   "month-year\""
DAY_ERROR = "The hour should be between 00 and 23"
MONTH_ERROR = "The minutes should be between 00 and 59"
TYPE_ERROR = "All the parts of the hour and date should be integers"

MONTH_TO_DAY_CONVERTER = {
    1: 31,
    2: 28,
    3: 31,
    4: 30,
    5: 31,
    6: 30,
    7: 31,
    8: 31,
    9: 30,
    10: 31,
    11: 30,
    12: 31
}

STILL_ONLINE = "Still Online"


################ Utility Functions ################

def get_hour_from_format(hour):
    hours = hour.split(",")
    return [int(t) for t in hours[0].split(":")]


def get_date_from_format(date):
    dates = date.split(",")
    return [int(t) for t in dates[-1].split("-")]


def get_format_from_hour_date(*args):
    return DATE_FORMAT_FOR_FORMAT.format(*args)


def separate_act_hours_by_dates(act_hours):
    hours_by_date = []

    for hour in act_hours:
        start_hour = get_hour_from_format(hour[0])
        end_hour = get_hour_from_format(hour[-1])

        start_date = get_date_from_format(hour[0])
        end_date = get_date_from_format(hour[-1])

        if start_date == end_date:
            hours_by_date.append(hour)
        else:
            hours_by_date += [[hour[0], get_format_from_hour_date(24, 00,
                                                                  start_date[0],
                                                                  start_date[1],
                                                                  start_date[2])],
                              [get_format_from_hour_date(00, 00,
                                                         end_date[0],
                                                         end_date[1],
                                                         end_date[2]), hour[-1]]]

    return hours_by_date


def read_pkl(file_name):
    global mutex

    data = {}

    with mutex:
        # Read File
        with (open(file_name, "rb")) as f:
            data = pickle.load(f)

    return data


def write_pkl(data, file_name):
    global mutex

    with mutex:
        # Write File
        with (open(file_name, "wb")) as f:
            pickle.dump(data, f)


def get_current_date_time():
    current_date_time = datetime.now()
    return current_date_time.strftime(DATE_FORMAT)


def fix_hourdates(hourdate1, hourdate2):
    new_hourdate1 = hourdate1
    if hourdate1 == STILL_ONLINE:
        new_hourdate1 = get_current_date_time()

    new_hourdate2 = hourdate2
    if hourdate2 == STILL_ONLINE:
        new_hourdate2 = get_current_date_time()

    return new_hourdate1, new_hourdate2


def max_hour_date(hourdate1, hourdate2):
    hourdate1, hourdate2 = fix_hourdates(hourdate1, hourdate2)

    hour1 = get_hour_from_format(hourdate1)
    hour2 = get_hour_from_format(hourdate2)
    date1 = get_date_from_format(hourdate1)
    date2 = get_date_from_format(hourdate2)

    if date1 != date2:
        if date1 == max_date(date1, date2):
            return hourdate1
        else:
            return hourdate2
    else:
        if hour1 == max_hour(hour1, hour2):
            return hourdate1
        else:
            return hourdate2


def min_hour_date(hourdate1, hourdate2):
    hourdate1, hourdate2 = fix_hourdates(hourdate1, hourdate2)

    hour1 = get_hour_from_format(hourdate1)
    hour2 = get_hour_from_format(hourdate2)
    date1 = get_date_from_format(hourdate1)
    date2 = get_date_from_format(hourdate2)

    if date1 != date2:
        if date1 == min_date(date1, date2):
            return hourdate1
        else:
            return hourdate2
    else:
        if hour1 == min_hour(hour1, hour2):
            return hourdate1
        else:
            return hourdate2


def max_date(date1, date2):
    if date1[-1] > date2[-1]:
        return date1
    elif date1[-1] < date2[-1]:
        return date2
    else:
        if date1[1] > date2[1]:
            return date1
        elif date1[1] < date2[1]:
            return date2
        else:
            if date1[0] > date2[0]:
                return date1
            else:
                return date2


def min_date(date1, date2):
    if date1[-1] > date2[-1]:
        return date2
    elif date1[-1] < date2[-1]:
        return date1
    else:
        if date1[1] > date2[1]:
            return date2
        elif date1[1] < date2[1]:
            return date1
        else:
            if date1[0] > date2[0]:
                return date2
            else:
                return date1


def max_hour(hour1, hour2):
    if hour1[0] > hour2[0]:
        return hour1
    elif hour1[0] < hour2[0]:
        return hour2
    else:
        if hour1[1] > hour2[1]:
            return hour1
        else:
            return hour2


def min_hour(hour1, hour2):
    if hour1[0] > hour2[0]:
        return hour2
    elif hour1[0] < hour2[0]:
        return hour1
    else:
        if hour1[1] > hour2[1]:
            return hour2
        else:
            return hour1


def distance_in_hourdates(hourdate1, hourdate2):
    hourdate1, hourdate2 = fix_hourdates(hourdate1, hourdate2)

    hour1 = get_hour_from_format(hourdate1)
    hour2 = get_hour_from_format(hourdate2)
    date1 = get_date_from_format(hourdate1)
    date2 = get_date_from_format(hourdate2)

    return distance_in_hours(hour1, hour2) + distance_in_days(date1, date2)


def distance_in_days(date1, date2):
    day_diff = (date1[0] - date2[0]) * 24
    month_diff = (date1[1] - date2[1]) * 30 * 24
    year_diff = (date1[2] - date2[2]) * 365 * 24
    return day_diff + month_diff + year_diff


def distance_of_hours(hourdate1, hourdate2):
    hour1, _ = hourdate1.split(",")
    hour2, _ = hourdate2.split(",")

    hours1 = [int(t) for t in hour1.split(":")]
    hours2 = [int(t) for t in hour2.split(":")]

    return distance_in_hours(hours1, hours2)


def distance_in_hours(hour1, hour2):
    hour_diff = hour1[0] - hour2[0]
    minute_diff = (hour1[1] - hour2[1]) / 60
    return hour_diff + minute_diff


def get_yesterday(hourdate):
    return add_x(hourdate, -24*60)



def get_weekday(hourdate):
    date = datetime.strptime(hourdate, DATE_FORMAT)
    day = date.weekday()

    return (day + 1) % 7 + 1


def weekend(hourdate):
    if get_weekday(hourdate) >= 6:
        return True
    return False


def add_x(hourdate, x):
    date = datetime.strptime(hourdate, DATE_FORMAT)
    return (date + timedelta(minutes=x)).strftime(DATE_FORMAT)


def print_db(db):
    for contact in db:
        print("==================================")
        print(contact)
        print("Information:")
        for info in db[contact]:
            print("\t", info, ":", db[contact][info])
