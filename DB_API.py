from utilities import *
import csv
import pandas as pd
import os
from functools import reduce
from copy import deepcopy

################ API Constants ################

PKL_FILE = "./Database4.pkl"

ONLINE = "Online"
ACTIVE_HOURS = "Active Hours"
IMAGE = "User Image"
LAST_SEEN = "Last Seen"
STILL_ONLINE = "Still Online"
INDEX = "Index"

SLEEP_THRESHOLD = 5
SLEEP_START_FORMAT = "22:00,{0:0>2}-{0:0>2}-{0:0>2}"
SLEEP_END_FORMAT = "10:00,{0:0>2}-{0:0>2}-{0:0>2}"

CURRENT_PATH = "./"
ACTIVITY_PATH = "activity_hours.csv"
CONTACTS_PATH = "contacts.csv"
ALL_DATA_PATH = "all_data.csv"

WAIT = 2
THRESHOLD_BLOCK = 24
REPEAT = 3

TODAY_LAST = "today"
YESTERDAT_LAST = "yesterday"
MONTHS_LAST = {
    "Jan": "01",
    "Feb": "02",
    "Mar": "03",
    "April": "04",
    "May": "05",
    "Jun": "06",
    "Jul": "07",
    "Aug": "08",
    "Sep": "09",
    "Oct": "10",
    "Nov": "11",
    "Dec": "12",

}


############### Whatsapp DB API ###############

# Function init_db:
#   Input:
#       names: List of Strings, A list of names of the people in the database
#       active_hours: List of lists of size 2 where the elements are Strings in the format in the
#       utilities file, A corresponding list of active hours of each contact
#   Output:
#       no output
#   Description:
#       This function creates the database and saves it into the file

def init_db(names, active_hours):
    db = {}

    for i, contact in enumerate(names):
        db[contact] = {}
        db[contact][ONLINE] = False
        db[contact][LAST_SEEN] = ""
        db[contact][ACTIVE_HOURS] = active_hours[i]
        db[contact][IMAGE] = ""
        db[contact][INDEX] = i + 1

    write_pkl(db, PKL_FILE)


# Function online_now:
#   Input:
#       contact_name: String, The name of the contact who just became online
#   Output:
#       no output
#   Description:
#       This function updates the active hours, effective last seen and the online flag if necessary


def online_now(contact_name):
    db = read_pkl(PKL_FILE)

    if db:
        # Update Active Hours in the DB
        # Get Current Date and Time
        current_date_time_str = get_current_date_time()

        # If the Contact isn't Online in the DB
        if not db[contact_name][ONLINE]:
            # Update Hours
            if not db[contact_name][ACTIVE_HOURS] or current_date_time_str != \
                    db[contact_name][ACTIVE_HOURS][-1][-1]:
                db[contact_name][ACTIVE_HOURS].append(
                    [current_date_time_str, STILL_ONLINE])

            while abs(distance_in_hourdates(current_date_time_str,
                                            db[contact_name][
                                                ACTIVE_HOURS][0][-1])) > abs(
                distance_in_hourdates("00:00,1-1-0", "00:00,15-1-0")):
                db[contact_name][ACTIVE_HOURS] = db[contact_name][
                                                     ACTIVE_HOURS][1:]

            # Update Online Status
            db[contact_name][ONLINE] = True

        # Update Last Seen
        db[contact_name][LAST_SEEN] = current_date_time_str

    write_pkl(db, PKL_FILE)


# Function not_online_now:
#   Input:
#       contact_name: String, The name of the contact who just disconnected
#   Output:
#       no output
#   Description:
#       This function updates the active hours, effective last seen and the online flag if necessary

def not_online_now(contact_name):
    db = read_pkl(PKL_FILE)

    if db:
        # Update Active Hours in the DB
        # Get Current Date and Time
        current_date_time_str = get_current_date_time()

        # If the Contact is Online in the DB
        if db[contact_name][ONLINE]:
            # Update Hours
            db[contact_name][ACTIVE_HOURS][-1][-1] = current_date_time_str

            # Update Online Status
            db[contact_name][ONLINE] = False

            while abs(distance_in_hourdates(current_date_time_str,
                                            db[contact_name][
                                                ACTIVE_HOURS][0][-1])) > abs(
                distance_in_hourdates("00:00,1-1-0", "00:00,15-1-0")):
                db[contact_name][ACTIVE_HOURS] = db[contact_name][
                                                     ACTIVE_HOURS][1:]

    write_pkl(db, PKL_FILE)


# Function set_image:
#   Input:
#       contact_name: String, The name of the contact whose image we want to update
#       image: String, the link of the image, The new image
#   Output:
#       no output
#   Description:
#       This function updates the image of contact_name in the database

def set_image(contact_name, image):
    db = read_pkl(PKL_FILE)

    if db:
        # Update Image
        db[contact_name][IMAGE] = image

    write_pkl(db, PKL_FILE)


# Function last_seen_update:
#   Input:
#       contact_name: String, The name of the contact whose last seen we want to update
#       last_seen: String, using the format in the file utilities, The new last_seen information we
#       got
#   Output:
#       no output
#   Description:
#       This function updates the last seen field of contact_name

def lastseen_update(contact_name, last_seen):
    db = read_pkl(PKL_FILE)

    if db:
        current_date = get_current_date_time()
        year = current_date.split("-")[-1]

        last_seen_date = last_seen.split(" ")[:-1]
        last_seen_hours = last_seen.split(" ")[-1]

        if last_seen_date[0] == TODAY_LAST:
            last_seen_update = last_seen_hours + "," + current_date.split(",")[
                -1]
        elif last_seen_date[0] == YESTERDAT_LAST:
            yesterday = get_yesterday(current_date)
            last_seen_update = last_seen_hours + "," + yesterday.split(",")[-1]
        else:
            month, day = last_seen_date[:-1].split(" ")
            month = MONTHS_LAST[month]
            last_seen_update = last_seen_hours + "," + day + "-" + month + "-" + year

        # Update Last Seen
        db[contact_name][LAST_SEEN] = last_seen_update

    write_pkl(db, PKL_FILE)


################# Web DB API #################

# Function get_image:
#   Input:
#       contact_name: String, The name of the contact whose image we want to get
#   Output:
#       String, The string of the link to the image of the contact
#   Description:
#       This function returns the image of a certain contact

def get_image(contact_name):
    db = read_pkl(PKL_FILE)

    if db:
        return db[contact_name][IMAGE]


# Function last_seen:
#   Input:
#       contact_name: String, The name of the contact whose last seen we want to get
#   Output:
#       String, The string of the hour and date using the format in the utilities file
#   Description:
#       This function returns the last seen parameter of a certain contact

def lastseen(contact_name):
    db = read_pkl(PKL_FILE)

    if db:
        return db[contact_name][LAST_SEEN].split(",")[::-1]


def get_blocking(contact_name):
    activity_hours = get_total_activity_hours(contact_name)

    if not activity_hours:
        return True

    if activity_hours[-1][-1] == STILL_ONLINE:
        return False

    dists = []
    for i in range(len(activity_hours) - 1):
        dists.append(abs(distance_in_hourdates(activity_hours[i + 1][0],
                                               activity_hours[i][-1])))
    if dists:
        max_wait = max(dists)
    else:
        max_wait = 0
    time_since_last = abs(
        distance_in_hourdates(get_current_date_time(), activity_hours[-1][-1]))

    if time_since_last > max(WAIT * max_wait, THRESHOLD_BLOCK):
        return True

    return False


# Function get_total_activity_hours:
#   Input:
#       contact_name: String, The name of the contact whose activity we want to get
#   Output:
#       List, A list of all the activity hours saved in the database
#   Description:
#       This function returns the activity hours of a contact

def get_total_activity_hours(contact_name):
    db = read_pkl(PKL_FILE)

    if db:
        return db[contact_name][ACTIVE_HOURS]


# Function get_activity_hours:
#   Input:
#       contact_name: String, The name of the contact whose activity we want to get
#   Output:
#       List, A list of all the activity hours saved in the database from the last 24 hours
#   Description:
#       This function returns the activity hours of a contact from the last 24 hours

def get_activity_hours(contact_name, minutes):
    db = read_pkl(PKL_FILE)

    if db:
        act_hours = db[contact_name][ACTIVE_HOURS]

        current_date_time_str = get_current_date_time()

        for i, hours in enumerate(act_hours):
            if abs(distance_in_hourdates(current_date_time_str,
                                         hours[-1])) < abs(
                distance_in_hourdates("00:00,1-1-0", "00:00,2-1-0")):
                act_hours = act_hours[i:]
                break
        else:
            start_time = add_x(current_date_time_str, -24 * 60)
            steps = int(24 * 60 / minutes)
            return [[add_x(start_time, minutes * i).split(",")[0], 0] for i in
                    range(steps)]

        if abs(distance_in_hourdates(current_date_time_str,
                                     act_hours[0][0])) > abs(
            distance_in_hourdates("00:00,1-1-0", "00:00,2-1-0")):
            act_hours[0][0] = add_x(current_date_time_str, -24 * 60)

        activity = []

        start_hour = add_x(current_date_time_str, -24 * 60)
        current_hour = start_hour
        while (distance_in_hourdates(current_date_time_str, current_hour) > 0):
            next_time = add_x(current_hour, minutes)
            start_index = 0
            finish_index = 0
            for i, hours in enumerate(act_hours):
                if distance_in_hourdates(current_hour, hours[-1]) > 0:
                    start_index = i + 1
                if distance_in_hourdates(next_time, hours[0]) > 0:
                    finish_index = i

            relevant_hours = deepcopy(act_hours[start_index:finish_index + 1])
            if relevant_hours:
                if distance_in_hourdates(relevant_hours[0][0],
                                         current_hour) < 0:
                    relevant_hours[0][0] = current_hour
                if distance_in_hourdates(relevant_hours[-1][-1],
                                         next_time) > 0:
                    relevant_hours[-1][-1] = next_time
                if distance_in_hourdates(relevant_hours[-1][-1],
                                         relevant_hours[0][0]) < 0:
                    relevant_hours = []

            sum_time = sum(
                map(lambda x: abs(distance_in_hourdates(x[0], x[1])),
                    relevant_hours))
            activity.append([current_hour.split(",")[0], round(sum_time * 60)])

            current_hour = next_time

        return activity


# Function get_complement_activity_hours:
#   Input:
#       contact_name: String, The name of the contact whose activity we want to get
#       hour_range: List, The hour range we want to know the activities in
#   Output:
#       List, A list of all the activity hours saved in the database
#   Description:
#       This function returns the complement of the activity hours in the specified hour range

def get_complement_activity_hours(contact, hour_range):
    contacts = get_contacts_by_activity_hours([hour_range])

    if contact not in contacts:
        return [hour_range]

    hours_in_range = contacts[contact]

    if not hours_in_range:
        return [hour_range]

    complement = []

    if hour_range[0] != hours_in_range[0][0]:
        complement.append([hour_range[0], hours_in_range[0][0]])

    for i in range(len(hours_in_range) - 1):
        complement.append([hours_in_range[i][-1], hours_in_range[i + 1][0]])

    if hours_in_range[-1][-1] != hour_range[-1]:
        complement.append([hours_in_range[-1][-1], hour_range[-1]])

    return complement


# Function get_contact_by_activity_hours:
#   Input:
#       activity_hours: List, The list of activity hours in which we want to get the contact from
#   Output:
#       Dictionary, A dictionary of the contacts to their respective activity hours in the
#       specified range
#   Description:
#       This function returns the activity hours of each contact in the range specified in
#       activity_hours

def get_contacts_by_activity_hours(activity_hours):
    db = read_pkl(PKL_FILE)

    if db:
        filtered = {}
        for contact in db:
            act_hours = get_total_activity_hours(contact)

            if act_hours:
                if act_hours[-1][-1] == STILL_ONLINE:
                    act_hours[-1][-1] = get_current_date_time()

                act_hours = separate_act_hours_by_dates(act_hours)

                ranges = []

                for hourdate1 in act_hours:
                    for hourdate2 in activity_hours:
                        mutual_beginning = max_hour_date(hourdate1[0],
                                                         hourdate2[0])
                        mutual_end = min_hour_date(hourdate1[1], hourdate2[1])
                        if mutual_beginning == min_hour_date(mutual_beginning,
                                                             mutual_end):
                            ranges.append([mutual_beginning, mutual_end])

                if ranges:
                    filtered[contact] = ranges
                else:
                    filtered[contact] = []

        return filtered


# Function get_sleeping_hours:
#   Input:
#       contact_name: String, The name of the contact whose sleeping hours we want to get
#       start_date: List, a list of the start date from which we want to count
#       end_date: List, a list of the end date on which we want to end the count
#   Output:
#       List, A list of the sleeping hours each day from start_date to end_date
#   Description:
#       This function returns the sleeping hours of the specified contact from start_date to
#       end_date

def get_sleeping_hours(contact, start_date, end_date):
    sleeping_hours = []

    day = start_date[0]
    month = start_date[1]
    for year in range(start_date[-1], end_date[-1] + 1):
        if year == end_date[-1]:
            end_month = end_date[1]
        else:
            end_month = 12

        while month <= end_month:
            if year == end_date[-1] and month == end_date[1]:
                end_day = end_date[0]
            else:
                end_day = MONTH_TO_DAY_CONVERTER[month]

            while day <= end_day:
                start_hour = SLEEP_START_FORMAT.format(day, month, year)

                if day == MONTH_TO_DAY_CONVERTER[month]:
                    if month == 12:
                        end_hour = SLEEP_END_FORMAT.format(1, 1, year + 1)
                    else:
                        end_hour = SLEEP_END_FORMAT.format(1, month + 1, year)
                else:
                    end_hour = SLEEP_END_FORMAT.format(day + 1, month, year)

                hour_range = [start_hour, end_hour]

                potential_sleep = get_complement_activity_hours(contact,
                                                                hour_range)

                sleeping_hours.append(
                    max(potential_sleep,
                        key=lambda x: distance_in_hourdates(x[1], x[0])))
                day += 1

            day = 1
            month += 1
        month = 1

    return sleeping_hours


def get_end_together(contact1, contact2, epsilon):
    active_hours1 = get_total_activity_hours(contact1)
    active_hours2 = get_total_activity_hours(contact2)

    end_together = []

    for i, date1 in enumerate(active_hours1):
        for j, date2 in enumerate(active_hours2):
            if abs(distance_in_hourdates(date1[-1], date2[-1])) < epsilon / 60:
                end_together.append((date1, date2))

    return end_together


def get_start_together(contact1, contact2, epsilon):
    active_hours1 = get_total_activity_hours(contact1)
    active_hours2 = get_total_activity_hours(contact2)

    start_together = []

    for i, date1 in enumerate(active_hours1):
        for j, date2 in enumerate(active_hours2):
            if abs(distance_in_hourdates(date1[0], date2[0])) < epsilon / 60:
                start_together.append((date1, date2))

    return start_together


def get_contact_start_together(epsilon):
    db = read_pkl(PKL_FILE)

    if db:
        start_together = {}
        for contact1 in db:
            for contact2 in db:
                if contact1 == contact2:
                    continue

                start = get_start_together(contact1, contact2, epsilon)

                if start and start[0] is not None:
                    if (contact1, contact2) not in start_together and (
                            contact2, contact1) not in \
                            start_together:
                        start_together[(contact1, contact2)] = start

        return start_together


def get_contact_end_together(epsilon):
    db = read_pkl(PKL_FILE)

    if db:
        end_together = {}
        for contact1 in db:
            for contact2 in db:
                if contact1 == contact2:
                    continue

                end = get_end_together(contact1, contact2, epsilon)

                if end and end[0] is not None:
                    if (contact1, contact2) not in end_together and (
                            contact2, contact1) not in end_together:
                        end_together[(contact1, contact2)] = end

        return end_together


def get_total_activity(active_hours):
    return sum([abs(distance_in_hourdates(hour[0], hour[1])) for hour in
                active_hours])


def get_total_active_time_on_day(contact_name, date):
    active_hours = get_total_activity_hours(contact_name)

    separated_hours = separate_act_hours_by_dates(active_hours)

    filtered_hours = [hour for hour in separated_hours if
                      date in hour[0] or date in hour[1]]

    return get_total_activity(filtered_hours) / 24


def get_mutual_intersection(contact1, contact2, date):
    active_hours2 = get_total_activity_hours(contact2)

    separated_hours2 = separate_act_hours_by_dates(active_hours2)
    filtered_hours2 = [hour for hour in separated_hours2 if
                       date in hour[0] or date in hour[1]]

    intersection = get_contacts_by_activity_hours(filtered_hours2)

    print(separated_hours2, intersection)

    if contact1 in intersection:
        return intersection[contact1]

    return []


def get_mutual_intersection_on_day(contact1, contact2, date):
    active_hours1 = get_total_activity_hours(contact1)
    active_hours2 = get_total_activity_hours(contact2)

    active_hours1[-1] = list(fix_hourdates(*active_hours1[-1]))
    active_hours2[-1] = list(fix_hourdates(*active_hours2[-1]))

    separated_hours1 = separate_act_hours_by_dates(active_hours1)
    filtered_hours1 = [hour for hour in separated_hours1 if
                       date in hour[0] or date in hour[1]]

    total_activity1 = get_total_activity(filtered_hours1)

    separated_hours2 = separate_act_hours_by_dates(active_hours2)
    filtered_hours2 = [hour for hour in separated_hours2 if
                       date in hour[0] or date in hour[1]]

    total_activity2 = get_total_activity(filtered_hours2)

    intersection = get_mutual_intersection(contact1, contact2, date)

    print(intersection)

    total_activity_intersection = get_total_activity(intersection)

    print(total_activity_intersection, total_activity1, total_activity2)

    return total_activity_intersection / total_activity1, total_activity_intersection / total_activity2


def get_repeating_times(contact_name, epsilon):
    activity_hours = get_total_activity_hours(contact_name)
    weekday_activity_hours = list(
        filter(lambda x: not weekend(x[0]), activity_hours))

    if not weekday_activity_hours:
        return []

    day_index = 0
    for i, hour in enumerate(weekday_activity_hours):
        if abs(distance_in_hourdates(hour[1],
                                     weekday_activity_hours[0][0])) < abs(
            distance_in_hourdates("00:00,1-1-0", "00:00,2-1-0")):
            day_index = i

    first_day = weekday_activity_hours[:day_index + 1]

    repeating_hours = []
    for hour1 in first_day:
        repeating = []
        for hour2 in weekday_activity_hours:
            if abs(distance_of_hours(hour2[0],
                                     hour1[0])) < epsilon / 60 and abs(
                distance_of_hours(hour2[1], hour1[1])) < epsilon / 60:
                repeating.append(hour2)
        repeating = set([t[0].split(",")[1] for t in repeating])
        if len(repeating) >= REPEAT:
            repeating_hours.append([t.split(",")[0] for t in hour1])

    return repeating_hours


def save_activity_hours(contact_name):
    db = read_pkl(PKL_FILE)

    if db:
        activity_hours = get_total_activity_hours(contact_name)

        with open(os.path.join(CURRENT_PATH, ACTIVITY_PATH), 'w',
                  newline='') as f:
            writer = csv.writer(f, delimiter=',')

            writer.writerow(['Index', 'Start Time', 'End Time'])
            for i, line in enumerate(activity_hours):
                line = [i + 1] + line
                if line[-1] == STILL_ONLINE:
                    line[-1] = get_current_date_time()
                writer.writerow(line)


def save_contacts_by_activity_hours(activity_hours):
    db = read_pkl(PKL_FILE)

    if db:
        filtered_contacts = get_contacts_by_activity_hours(activity_hours)
        first_row = [[contact, '', ''] for contact in filtered_contacts]
        first_row = reduce(lambda x, y: x + y, first_row)
        elements = ['Index', 'Start Time', 'End Time']
        second_row = elements * len(filtered_contacts)

        max_hours = max(
            [len(filtered_contacts[contact]) for contact in filtered_contacts])

        rows = []
        for i in range(max_hours):
            rows.append([''] * len(filtered_contacts) * len(elements))

        for i, contact in enumerate(filtered_contacts):
            for j, hours in enumerate(filtered_contacts[contact]):
                rows[j][i * len(elements)] = j + 1
                rows[j][i * len(elements) + 1] = hours[0]

                if hours[1] == STILL_ONLINE:
                    hours[1] = get_current_date_time()

                rows[j][i * len(elements) + 2] = hours[1]

        rows = [first_row, second_row] + rows

        df = pd.DataFrame(rows)
        df.to_csv(os.path.join(CURRENT_PATH, CONTACTS_PATH), encoding="UTF-8",
                  index=False)


def save_all():
    db = read_pkl(PKL_FILE)

    if db:
        names = []
        last_seen = []
        active_hours = []
        image = []
        index = []
        online = []

        for contact in db:
            names.append(contact)
            last_seen.append(db[contact][LAST_SEEN])
            active_hours.append(db[contact][ACTIVE_HOURS])
            image.append(db[contact][IMAGE])
            index.append(db[contact][INDEX])
            online.append(db[contact][ONLINE])

        data = {
            'Name': names,
            'Index': index,
            'Online': online,
            'Last Seen': last_seen,
            'Activity Hours': active_hours,
            'Image': image,
        }

        df = pd.DataFrame(data)
        df.to_csv(os.path.join(CURRENT_PATH, ALL_DATA_PATH), encoding="UTF-8",
                  index=False)


def save_contacts_by_activity_hours_no_names(activity_hours):
    db = read_pkl(PKL_FILE)

    if db:
        filtered_contacts = get_contacts_by_activity_hours(activity_hours)
        first_row = [[db[contact][INDEX], '', ''] for contact in
                     filtered_contacts]
        first_row = reduce(lambda x, y: x + y, first_row)
        elements = ['Index', 'Start Time', 'End Time']
        second_row = elements * len(filtered_contacts)

        max_hours = max(
            [len(filtered_contacts[contact]) for contact in filtered_contacts])

        rows = []
        for i in range(max_hours):
            rows.append([''] * len(filtered_contacts) * len(elements))

        for i, contact in enumerate(filtered_contacts):
            for j, hours in enumerate(filtered_contacts[contact]):
                rows[j][i * len(elements)] = j + 1
                rows[j][i * len(elements) + 1] = hours[0]

                if hours[1] == STILL_ONLINE:
                    hours[1] = get_current_date_time()

                rows[j][i * len(elements) + 2] = hours[1]

        rows = [first_row, second_row] + rows

        df = pd.DataFrame(rows)
        df.to_csv(os.path.join(CURRENT_PATH, CONTACTS_PATH), encoding="UTF-8",
                  index=False)


def save_all_no_names():
    db = read_pkl(PKL_FILE)

    if db:
        last_seen = []
        active_hours = []
        image = []
        index = []
        online = []

        for contact in db:
            last_seen.append(db[contact][LAST_SEEN])
            active_hours.append(db[contact][ACTIVE_HOURS])
            image.append(db[contact][IMAGE])
            index.append(db[contact][INDEX])
            online.append(db[contact][ONLINE])

        data = {
            'Index': index,
            'Online': online,
            'Last Seen': last_seen,
            'Activity Hours': active_hours,
            'Image': image,
        }

        df = pd.DataFrame(data)
        df.to_csv(os.path.join(CURRENT_PATH, ALL_DATA_PATH), encoding="UTF-8",
                  index=False)


def get_contacts_dict():
    db = read_pkl(PKL_FILE)

    if db:
        return {contact: db[contact][INDEX] for contact in db}

    return {}


def get_index_by_contact(contact_name):
    contacts_dict = get_contacts_dict()

    if contacts_dict and contact_name in contacts_dict:
        return contacts_dict[contact_name]


def get_contact_by_index(i):
    db = read_pkl(PKL_FILE)

    if db:
        for contact in db:
            if i == db[contact][INDEX]:
                return contact

    return None


def valid_hourdate(hourdate):
    parts = hourdate.split(",")

    if len(parts) != 2:
        return False, PARTS_ERROR

    hours, date = parts

    hour_parts = hours.split(":")

    if len(hour_parts) != 2:
        return False, HOUR_PARTS_ERROR

    hour, minute = hour_parts

    date_parts = date.split("-")

    if len(date_parts) != 3:
        return False, DATE_PARTS_ERROR

    day, month, year = date_parts

    try:
        hour = int(hour)
        minute = int(minute)
        day = int(day)
        month = int(month)
        year = int(year)
    except:
        return False, TYPE_ERROR

    if hour < 0 or hour > 23:
        return False, HOUR_ERROR

    if minute < 0 or minute > 59:
        return False, MINUTE_ERROR

    if month < 1 or month > 12:
        return False, MONTH_ERROR

    if day < 1 or day > MONTH_TO_DAY_CONVERTER[month]:
        return False, DAY_ERROR

    return True, None

"""
def add_new_contact(contact_name):
    names = list(get_contacts_dict().keys())
    hours = []
    for name in names:
        hs = get_total_activity_hours(name)
        hours.append(hs)
    names.append(contact_name)
    hours.append([])
    init_db(names, hours)


def del_contact(contact_name):
    names = list(get_contacts_dict().keys())
    if not contact_name in names:
        print("contact name {0} not found in db".format(contact_name))
        return
    names.remove(contact_name)
    hours = []
    for name in names:
        hs = get_total_activity_hours(name)
        hours.append(hs)
    init_db(names, hours)
"""
################# Test DB API #################

#TEST_NAMES = ['גיא גולניק - 40', 'איתי הראל', 'תומר שראל', 'אריאל שניץ - 40']

TEST_NAMES = ['גיא גולניק - 40', 'עומר בצרי', 'עידו רוזבל', 'אריאל שניץ - 40']
TEST_HOURS = [[] for i in range(len(TEST_NAMES))]


#TEST_NAMES = ["אריאל שניץ - 40","עידו רוזבל"]
"""
TEST_HOURS = [
    [["08:01,02-06-2020","08:03,02-06-2020"],["08:10,02-06-2020","08:11,02-06-2020"],["12:02,02-06-2020","13:03,02-06-2020"],
     ["07:59,03-06-2020", "08:02,03-06-2020"],["08:11,03-06-2020", "08:13,03-06-2020"],["12:03,03-06-2020", "13:04,03-06-2020"],
     ["08:02,04-06-2020", "08:03,04-06-2020"], ["08:09,04-06-2020", "08:10,04-06-2020"],["12:04,04-06-2020", "13:03,04-06-2020"],
     ["08:02,04-06-2020", "08:02,05-06-2020"],["08:09,05-06-2020", "08:11,05-06-2020"],["11:59,05-06-2020", "13:00,05-06-2020"]]
    ,[]
]
"""

if __name__ == '__main__':
    #init_db(TEST_NAMES, TEST_HOURS)
    db = read_pkl(PKL_FILE)
    print_db(db)

    # external API
    # print(get_repeating_times("אריאל שניץ - 40", 3))
    # print(get_contacts_by_activity_hours([["17:00,06-06-2020", "19:00,06-06-2020"]]))
    # print(get_total_activity_hours("אריאל שניץ - 40"))

    # save_activity_hours("אריאל שניץ - 40")
    # save_contacts_by_activity_hours([["17:00,30-05-2020", "19:00,30-05-2020"]])
    # save_all()

    # print(get_contacts_by_activity_hours([["17:00,21-05-2020","18:00,24-05-2020"]]))
