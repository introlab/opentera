from math import floor
import datetime
from services.BureauActif.libbureauactif.db.Base import db
from services.BureauActif.libbureauactif.db.models.BureauActifCalendarDay import BureauActifCalendarDay
from services.BureauActif.libbureauactif.db.models.BureauActifCalendarData import BureauActifCalendarData
from services.BureauActif.libbureauactif.db.models.BureauActifTimelineDay import BureauActifTimelineDay
from services.BureauActif.libbureauactif.db.models.BureauActifTimelineDayEntry import BureauActifTimelineDayEntry


class Interval(object):
    def __init__(self, middle, deviation):
        self.lower = middle - abs(deviation)
        self.upper = middle + abs(deviation)

    def __contains__(self, item):
        return self.lower <= item <= self.upper


def get_calendar_day(uuid_participant, date):
    return BureauActifCalendarDay.get_calendar_day(uuid_participant, date.date())


def create_new_calendar_data(id_calendar_day, id_calendar_data_type):
    calendar_data = BureauActifCalendarData()
    calendar_data.id_calendar_data = 0
    calendar_data.remaining = 0
    calendar_data.done = 0
    calendar_data.id_calendar_data_type = id_calendar_data_type
    calendar_data.id_calendar_day = id_calendar_day
    return calendar_data


def create_new_calendar_day(date, uuid_participant):
    calendar_day = BureauActifCalendarDay()
    calendar_day.participant_uuid = uuid_participant
    calendar_day.date = date
    return calendar_day


def get_timeline_day(uuid_participant, date):
    return BureauActifTimelineDay.get_timeline_day(uuid_participant, date.date())


def create_new_timeline_day(date, uuid_participant):
    timeline_day = BureauActifTimelineDay()
    timeline_day.participant_uuid = uuid_participant
    timeline_day.name = date
    return timeline_day


def interval(middle, deviation):
    return Interval(middle, deviation)


class DBManagerBureauActifDataProcess:
    data = []
    desk_config = {}
    timers = {}

    first_position_timer = 1  # Timer for the first position of the day
    second_position_timer = 1  # Timer for the second position of the day
    config_is_respected = True  # Participant is in the expected position
    actual_config_is_up = True  # True if expected position is standing
    middle_of_interval = 0  # Interval between which the index must be to be in the correct position
    half_timer_starting_position = 0  # Half of the timer
    button_pressed = False  # True if button was pressed

    calendar_day = BureauActifCalendarDay()
    seating = BureauActifCalendarData()
    standing = BureauActifCalendarData()
    position_changes = BureauActifCalendarData()

    timeline_day = BureauActifTimelineDay()
    timeline_day_entries = []

    def process_data(self, raw_data, file_db_entry):
        self.initialize()
        self.data = raw_data['data']
        self.desk_config = raw_data['config']
        self.timers = raw_data['timers']

        # Sort data by time -> to remove once the time on pi is fixed
        self.data = sorted(self.data, key=lambda x: datetime.datetime.fromisoformat(x[0].lstrip(' ')))
        uuid_participant = file_db_entry.data_participant_uuid
        date_str = raw_data['data'][0][0].lstrip(' ')
        date = datetime.datetime.fromisoformat(date_str)

        self.create_calendar_objects(uuid_participant, date)
        self.create_timeline(uuid_participant, date)

        self.get_starting_position()

        self.half_timer_starting_position = self.first_position_timer / 2  # Half of the timer of the first position
        self.middle_of_interval = self.half_timer_starting_position  # Initialize starting interval
        entries_before_position_change = 0  # Counter of loops before a change of position
        is_standing = False
        for index, val in enumerate(self.data):
            desk_height = float(val[1])
            button_state = val[2]
            was_standing = is_standing  # Save previous position to check if it changed
            previous_button_state = self.button_pressed  # Save previous button state

            # Check if desk is in standing position (true) or in seating position (false)
            is_standing = self.is_desk_up(desk_height)

            # Find the position expected for the index, defined by timers
            self.find_expected_position(index)

            # Check if button was pressed
            if button_state != '--':
                self.button_pressed = not self.button_pressed

            # Check if gap between timestamp of data, meaning no one was present in front of the sensor
            absent_time = self.get_absent_time(index)

            self.check_if_config_is_respected(was_standing)
            # Check if last entry or position changed or gap in the timeline (absence)
            if self.is_last_data(index) or was_standing != is_standing or \
                    absent_time != 0 or previous_button_state != self.button_pressed:
                self.position_changes.done += 1
                self.update_position(was_standing, index, entries_before_position_change)
                self.update_last_timeline_entry(absent_time, 4)
                entries_before_position_change = 0
            else:
                entries_before_position_change += 1

        self.save_calendar_data()

    def get_absent_time(self, current_index):
        if current_index > 0:
            past_data = self.get_time(current_index - 1)
            current_data = self.get_time(current_index)
            delta = current_data - past_data
            if delta.seconds > 60:
                delta_in_hour = delta.seconds / 3600
                return delta_in_hour
        return 0

    def create_calendar_objects(self, uuid_participant, date):
        entry = get_calendar_day(uuid_participant, date)

        if entry is None:
            self.calendar_day = BureauActifCalendarDay.insert(create_new_calendar_day(date, uuid_participant))
            self.seating = create_new_calendar_data(self.calendar_day.id_calendar_day, 1)
            self.standing = create_new_calendar_data(self.calendar_day.id_calendar_day, 2)
            self.position_changes = create_new_calendar_data(self.calendar_day.id_calendar_day, 3)
        else:
            self.calendar_day = entry
            self.seating = BureauActifCalendarData.get_calendar_data(self.calendar_day.id_calendar_day, 1)
            self.standing = BureauActifCalendarData.get_calendar_data(self.calendar_day.id_calendar_day, 2)
            self.position_changes = BureauActifCalendarData.get_calendar_data(self.calendar_day.id_calendar_day, 3)

    def create_timeline(self, uuid_participant, date):
        entry = get_timeline_day(uuid_participant, date)

        if entry is None:
            self.timeline_day = BureauActifTimelineDay.insert(create_new_timeline_day(date, uuid_participant))
            self.set_starting_hour(date)  # Add starting bloc in timeline
        else:
            self.timeline_day = entry
            self.timeline_day_entries = BureauActifTimelineDayEntry.get_timeline_day_entries(
                self.timeline_day.id_timeline_day)

    def is_desk_up(self, desk_height):
        max_height = float(self.desk_config['max_height'])
        delta = abs(desk_height - max_height)
        return delta <= 5 or desk_height > max_height

    def is_last_data(self, index):
        return index == len(self.data) - 1

    def position_has_changed(self, index, desk_height):
        if index != 0:
            previous_height = float(self.data[index - 1][1])
            diff = abs(previous_height - desk_height)
            if diff > 10:
                return True
        return False

    def update_position(self, was_standing, index, entries_before_position_change):
        if was_standing:
            self.update_standing(index, entries_before_position_change)
        elif not was_standing:
            self.update_seating(index, entries_before_position_change)

    def update_seating(self, index, entries_before_position_change):
        delta = self.get_time_difference(index, entries_before_position_change)
        self.update_last_timeline_entry(delta, 3)
        self.seating.done += delta
        self.update_remaining_data(index)

    def update_standing(self, index, entries_before_position_change):
        delta = self.get_time_difference(index, entries_before_position_change)
        self.update_last_timeline_entry(delta, 2)
        self.standing.done += delta
        self.update_remaining_data(index)

    def get_time_difference(self, index, entries_count):
        if index != 0 and entries_count != 0 and entries_count <= index:
            start_time = self.get_time(index - entries_count)
            end_time = self.get_time(index - 1)
            delta = end_time - start_time
            delta_in_hour = delta.seconds / 3600
            return delta_in_hour
        return 0

    def get_time(self, index):
        date_str = self.data[index][0].lstrip(' ')
        return datetime.datetime.fromisoformat(date_str)

    def update_remaining_data(self, current_index):
        up = self.timers['up_secs']
        down = self.timers['down_secs']
        total = up + down
        up_ratio = up / total if total > 0 else 0
        down_ratio = down / total if total > 0 else 0

        start_of_day = self.calendar_day.date
        current = self.get_time(current_index)
        delta = current - start_of_day
        work_time = delta.seconds / 3600

        up_to_do = work_time * up_ratio
        down_to_do = work_time * down_ratio

        if up > 0:
            position_changes_to_do = floor(work_time / up)
        elif down > 0:
            position_changes_to_do = floor(work_time / down)
        else:
            position_changes_to_do = 0

        self.seating.remaining = down_to_do - self.seating.done if down_to_do - self.seating.done >= 0 else 0
        self.standing.remaining = up_to_do - self.standing.done if up_to_do - self.standing.done >= 0 else 0
        self.position_changes.remaining = position_changes_to_do - self.position_changes.done \
            if position_changes_to_do - self.position_changes.done >= 0 else 0

    def save_calendar_data(self):
        if self.position_changes.id_calendar_data > 0 \
                and self.seating.id_calendar_data > 0 \
                and self.standing.id_calendar_data > 0:
            db.session.commit()
        else:
            BureauActifCalendarData.insert(self.position_changes)
            BureauActifCalendarData.insert(self.seating)
            BureauActifCalendarData.insert(self.standing)

    def update_last_timeline_entry(self, delta, id_type):
        if delta > 0:
            last_entry = self.timeline_day_entries[len(self.timeline_day_entries) - 1]
            if last_entry.id_timeline_entry_type == id_type:
                last_entry.value += delta
                db.session.commit()
            else:
                color_type = self.get_right_timeline_color(id_type)
                new_entry = BureauActifTimelineDayEntry.insert(self.create_new_timeline_entry(color_type, delta))
                self.timeline_day_entries.append(new_entry)

    def get_right_timeline_color(self, id_type):
        if id_type == 2:  # Standing
            if not self.config_is_respected and self.button_pressed:  # Supposed to be seating
                return 6
        elif id_type == 3:  # Seating
            if not self.config_is_respected and self.button_pressed:  # Supposed to be standing
                return 5
        return id_type

    def create_new_timeline_entry(self, id_type, delta):
        entry = BureauActifTimelineDayEntry()
        entry.id_timeline_entry_type = id_type
        entry.value = delta
        entry.id_timeline_day = self.timeline_day.id_timeline_day
        return entry

    def set_starting_hour(self, date):
        starting_time = date.time()
        time = starting_time.hour + (starting_time.minute / 60)
        first_entry = BureauActifTimelineDayEntry.insert(self.create_new_timeline_entry(1, time))
        self.timeline_day_entries.append(first_entry)

    def get_starting_position(self):
        if self.is_desk_up(float(self.data[0][1])):
            self.first_position_timer = self.timers['up_secs']
            self.second_position_timer = self.timers['down_secs']
        else:
            self.first_position_timer = self.timers['down_secs']
            self.second_position_timer = self.timers['up_secs']

    def find_expected_position(self, index):
        # Difference between current index and max value of the current interval
        temp = (index - 1) - (self.middle_of_interval + self.half_timer_starting_position)
        if temp == 0:  # If true, means the interval is completed and the position should change
            self.middle_of_interval += self.first_position_timer + self.second_position_timer  # Get next interval to check
        if index in interval(self.middle_of_interval,
                             self.half_timer_starting_position):  # Position is supposed to be same as the starting one
            self.actual_config_is_up = True
        else:  # Position is supposed to be the opposite of the starting one
            self.actual_config_is_up = False

    def check_if_config_is_respected(self, is_standing):
        self.config_is_respected = self.actual_config_is_up == is_standing

    def initialize(self):
        self.config_is_respected = True
        self.actual_config_is_up = True
        self.button_pressed = False

        self.calendar_day = BureauActifCalendarDay()
        self.seating = BureauActifCalendarData()
        self.standing = BureauActifCalendarData()
        self.position_changes = BureauActifCalendarData()

        self.timeline_day = BureauActifTimelineDay()
        self.timeline_day_entries = []
