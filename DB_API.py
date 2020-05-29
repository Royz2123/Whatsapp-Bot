from utilities import *
from matplotlib import pyplot as plt
import pickle
import time

################ API Constants ################

PKL_FILE = "Database.pkl"

ONLINE = "Online"
ACTIVE_HOURS = "Active Hours"
IMAGE = "User Image"
LAST_SEEN = "Last Seen"
STILL_ONLINE = "Still Online"

SLEEP_THRESHOLD = 5
SLEEP_START_FORMAT = "22:00,{}-{}-{}"
SLEEP_END_FORMAT = "10:00,{}-{}-{}"


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
            if current_date_time_str != db[contact_name][ACTIVE_HOURS][-1][-1]:
                db[contact_name][ACTIVE_HOURS].append(
                    [current_date_time_str, STILL_ONLINE])
            else:
                db[contact_name][ACTIVE_HOURS][-1][-1] = STILL_ONLINE

            while abs(distance_in_hourdates(current_date_time_str, db[contact_name][
                ACTIVE_HOURS][0][-1])) > abs(distance_in_hourdates("00:00,1-1-0", "00:00,15-1-0")):
                db[contact_name][ACTIVE_HOURS] = db[contact_name][ACTIVE_HOURS][1:]

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
            db[contact_name][ACTIVE_HOURS][-1][1] = current_date_time_str

            # Update Online Status
            db[contact_name][ONLINE] = False

            while abs(distance_in_hourdates(current_date_time_str, db[contact_name][
                ACTIVE_HOURS][0][-1])) > abs(distance_in_hourdates("00:00,1-1-0", "00:00,15-1-0")):
                db[contact_name][ACTIVE_HOURS] = db[contact_name][ACTIVE_HOURS][1:]

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
        # Update Last Seen
        db[contact_name][LAST_SEEN] = last_seen

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
        return db[contact_name][LAST_SEEN]


def get_blocking(contact_name):
    pass


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

def get_activity_hours(contact_name):
    db = read_pkl(PKL_FILE)

    if db:
        act_hours = db[contact_name][ACTIVE_HOURS]

        current_date_time_str = get_current_date_time()

        for i, hours in enumerate(act_hours):
            if abs(distance_in_hourdates(current_date_time_str, hours[0])) < abs(
                    distance_in_hourdates("00:00,1-1-0", "00:00,2-1-0")):
                return day_to_hours(act_hours[i:])

        return []


# Function get_complement_activity_hours:
#   Input:
#       contact_name: String, The name of the contact whose activity we want to get
#       hour_range: List, The hour range we want to know the activities in
#   Output:
#       List, A list of all the activity hours saved in the database
#   Description:
#       This function returns the complement of the activity hours in the specified hour range

def get_complement_activity_hours(contact, hour_range):
    contacts = get_contact_by_activity_hours([hour_range])

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

def get_contact_by_activity_hours(activity_hours):
    db = read_pkl(PKL_FILE)

    if db:
        filtered = {}
        for contact in db:
            act_hours = get_total_activity_hours(contact)
            if act_hours:
                if act_hours[-1][-1] == STILL_ONLINE:
                    act_hours[-1][-1] = get_current_date_time()

                ranges = []

                for hourdate1 in act_hours:
                    for hourdate2 in activity_hours:
                        mutual_beginning = max_hour_date(hourdate1[0], hourdate2[0])
                        mutual_end = min_hour_date(hourdate1[1], hourdate2[1])
                        if mutual_beginning == min_hour_date(mutual_beginning, mutual_end):
                            ranges.append([mutual_beginning, mutual_end])

                if ranges:
                    filtered[contact] = ranges

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

                potential_sleep = get_complement_activity_hours(contact, hour_range)

                sleeping_hours.append(
                    max(potential_sleep, key=lambda x: distance_in_hourdates(x[1], x[0])))
                day += 1

            day = 1
            month += 1
        month = 1

    return sleeping_hours


################# Test DB API #################

TEST_NAMES = ["אייל", "אלון שראל", "הדבר שאני הכי אוהב בעולם", "Maya"]
TEST_HOURS = [
    [["10:00,15-05-2020", "15:00,15-05-2020"], ["22:00,15-05-2020",
                                                "04:00,16-05-2020"],
     ["06:00,16-05-2020", "07:12,16-05-2020"], ["12:12,16-05-2020",
                                                "13:12,16-05-2020"],
     ["23:12,17-05-2020", "02:12,18-05-2020"], ["10:12,18-05-2020",
                                                "12:12,18-05-2020"]],
    [],
    [],
    []
]

if __name__ == '__main__':
    init_db(TEST_NAMES, TEST_HOURS)

    # Interesting Functions
    # online now, not online now, last seen update, set image

    online_now("Eyal")
    not_online_now("Eyal")
    online_now("Eyal")
    online_now("Eyal")
    not_online_now("Eyal")
    not_online_now("Eyal")
    # time.sleep(120)
    not_online_now("Eyal")
    online_now("Eyal")
    online_now("Eyal")
    not_online_now("Eyal")
    online_now("Eyal")

    lastseen_update("Eyal", "10:12,09-07-2030")

    db = read_pkl(PKL_FILE)

    print_db(db)

    print(lastseen("Eyal"))
    print(get_total_activity_hours("Eyal"))
    print(get_activity_hours("Eyal"))
    print(get_image("Eyal"))

    print(get_contact_by_activity_hours([["14:00,15-05-2020", "23:00,15-05-2020"]]))
    print(get_contact_by_activity_hours([["16:00,15-05-2020", "21:00,15-05-2020"]]))
    print(get_complement_activity_hours("Eyal", ["14:00,15-05-2020", "05:23,16-05-2020"]))

    print(get_sleeping_hours("Eyal", [15, 5, 2020], [18, 5, 2020]))
