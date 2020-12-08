from math import ceil
import datetime
from services.BureauActif.libbureauactif.db.Base import db
from services.BureauActif.libbureauactif.db.models.BureauActifCalendarDay import BureauActifCalendarDay
from services.BureauActif.libbureauactif.db.models.BureauActifCalendarData import BureauActifCalendarData
from services.BureauActif.libbureauactif.db.models.BureauActifTimelineDay import BureauActifTimelineDay
from services.BureauActif.libbureauactif.db.models.BureauActifTimelineDayEntry import BureauActifTimelineDayEntry


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


class DBManagerBureauActifDataProcess:
    def __init__(self):
        self.calendar_day = BureauActifCalendarDay()
        self.seating = BureauActifCalendarData()
        self.standing = BureauActifCalendarData()
        self.position_changes = BureauActifCalendarData()
        self.timeline_day = BureauActifTimelineDay()
        self.timeline_day_entries = []
        self.data = []
        self.desk_config = {}
        self.timers = {}

        self.expected_desk_height = None
        self.is_config_respected = True
        self.expected_standing = False
        self.expected_seating = False

    def process_data(self, raw_data, file_db_entry):
        self.data = raw_data['data']
        self.desk_config = raw_data['config']
        self.timers = raw_data['timers']

        # Sort data by time -> use when time on pi de-sync - to remove once the time on pi is fixed
        # self.data = sorted(self.data, key=lambda x: datetime.datetime.fromisoformat(x[0].lstrip(' ')))

        uuid_participant = file_db_entry.data_participant_uuid
        date_str = raw_data['data'][0][0].lstrip(' ')
        date = datetime.datetime.fromisoformat(date_str)
        self.create_calendar_objects(uuid_participant, date)
        self.create_timeline(uuid_participant, date)

        entries_before_position_change = 0  # Counter of loops before a change of position
        is_standing = False
        # 0: datetime, 1: height, 2: button state, 3: presence, 4: expected height
        for index, val in enumerate(self.data):

            desk_height = float(val[1])
            self.expected_desk_height = float(val[4])
            was_standing = is_standing  # Save previous position to check if it changed
            previous_is_config_respected = self.is_config_respected  # Save previous button state
            self.is_config_respected = self.check_if_config_respected(is_standing)

            # Check if desk is in standing position (true) or in seating position (false)
            is_standing = self.is_desk_up(desk_height)

            # Check if gap between timestamp of data, meaning no one was present in front of the sensor
            absent_time = self.get_absent_time(index)

            # Check if last entry or position changed or gap in the timeline (absence)
            if self.is_last_data(index) or was_standing != is_standing or \
                    absent_time != 0 or previous_is_config_respected != self.is_config_respected:
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
            if delta.seconds > 300:  # Absence is worth showing in timeline only if at least 5 minutes
                delta_in_hour = delta.seconds / 3600
                return delta_in_hour
        return 0

    def create_calendar_objects(self, uuid_participant, date):
        entry = get_calendar_day(uuid_participant, date)

        if entry is None:  # No data for the current day, starting a new one
            self.calendar_day = BureauActifCalendarDay.insert(create_new_calendar_day(date, uuid_participant))
            self.seating = create_new_calendar_data(self.calendar_day.id_calendar_day, 1)
            self.standing = create_new_calendar_data(self.calendar_day.id_calendar_day, 2)
            self.position_changes = create_new_calendar_data(self.calendar_day.id_calendar_day, 3)
        else:  # Data already present for the current day
            self.calendar_day = entry
            self.seating = BureauActifCalendarData.get_calendar_data(self.calendar_day.id_calendar_day, 1)
            self.standing = BureauActifCalendarData.get_calendar_data(self.calendar_day.id_calendar_day, 2)
            self.position_changes = BureauActifCalendarData.get_calendar_data(self.calendar_day.id_calendar_day, 3)

    # Get previous timeline entries for the day or start a new timeline day
    def create_timeline(self, uuid_participant, date):
        entry = get_timeline_day(uuid_participant, date)

        if entry is None:  # No data for the current day, starting a new one
            self.timeline_day = BureauActifTimelineDay.insert(create_new_timeline_day(date, uuid_participant))
            self.set_starting_hour(date)  # Add starting block in timeline
        else:  # Data already present for the current day
            self.timeline_day = entry
            self.timeline_day_entries = BureauActifTimelineDayEntry.get_timeline_day_entries(
                self.timeline_day.id_timeline_day)

    # Check if desk is at max height +- 5 cm meaning it's up
    def is_desk_up(self, desk_height):
        max_height = float(self.desk_config['max_height'])
        delta = abs(desk_height - max_height)
        return delta <= 5 or desk_height > max_height

    def check_if_config_respected(self, is_standing):
        self.expected_standing = self.check_if_should_be_standing()
        self.expected_seating = self.check_if_should_be_seating()
        return self.expected_standing == is_standing or self.expected_seating != is_standing

    def check_if_should_be_standing(self):
        max_height = float(self.desk_config['max_height'])
        return self.expected_desk_height - 5 <= max_height <= self.expected_desk_height + 5

    def check_if_should_be_seating(self):
        min_height = float(self.desk_config['min_height'])
        return self.expected_desk_height - 5 <= min_height <= self.expected_desk_height + 5

    # Check if it's the last entry in the data file received from pi
    def is_last_data(self, index):
        return index == len(self.data) - 1

    # Check if the participant's position changed by comparing desk height to the previous entry in the file
    def position_has_changed(self, index, desk_height):
        if index != 0:
            previous_height = float(self.data[index - 1][1])
            diff = abs(previous_height - desk_height)
            if diff > 10:  # Error interval of 10 cm
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
        up_time = self.timers['up_secs']
        down_time = self.timers['down_secs']
        total_timers = up_time + down_time
        up_ratio = up_time / total_timers if total_timers > 0 else 0
        down_ratio = down_time / total_timers if total_timers > 0 else 0

        start_of_day = self.calendar_day.date
        current_time = self.get_time(current_index)
        time_worked = current_time - start_of_day
        standing_position_to_do = time_worked.seconds / 3600 * up_ratio
        seated_position_to_do = time_worked.seconds / 3600 * down_ratio

        position_changes_to_do = 0
        if up_time != 0 and down_time <= up_time:
            position_changes_to_do = ceil(time_worked.seconds / up_time)
        elif down_time != 0 and down_time >= up_time:
            position_changes_to_do = ceil(time_worked.seconds / down_time)

        self.seating.remaining = seated_position_to_do - self.seating.done \
            if seated_position_to_do - self.seating.done >= 0 else 0
        self.standing.remaining = standing_position_to_do - self.standing.done \
            if standing_position_to_do - self.standing.done >= 0 else 0
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
                if color_type not in [5, 6] and not self.is_first_timeline_entry() \
                        and not self.is_back_from_absence() and not self.config_was_not_respected():
                    self.position_changes.done += 1  # Count as a position change
                new_entry = BureauActifTimelineDayEntry.insert(self.create_new_timeline_entry(color_type, delta))
                self.timeline_day_entries.append(new_entry)

    # Returns true if the only entry in the timeline is the starting block
    def is_first_timeline_entry(self):
        return len(self.timeline_day_entries) == 1

    # Returns true if the last entry in timeline is an absence block
    def is_back_from_absence(self):
        return self.timeline_day_entries[len(self.timeline_day_entries) - 1].id_timeline_entry_type == 4

    # Returns true if the button was previously pressed and the schedule was not respected
    def config_was_not_respected(self):
        return self.timeline_day_entries[len(self.timeline_day_entries) - 1].id_timeline_entry_type in [5, 6]

    # Set the right type of entry for the timeline color
    def get_right_timeline_color(self, id_type):
        if id_type == 2:  # Standing
            if not self.is_config_respected:  # Supposed to be seating
                return 6
        elif id_type == 3:  # Seating
            if not self.is_config_respected:  # Supposed to be standing
                return 5
        return id_type

    def create_new_timeline_entry(self, id_type, delta):
        entry = BureauActifTimelineDayEntry()
        entry.id_timeline_entry_type = id_type
        entry.value = delta
        entry.id_timeline_day = self.timeline_day.id_timeline_day
        return entry

    # Add the timeline block from midnight to first entry time to make the relative timeline
    def set_starting_hour(self, date):
        starting_time = date.time()
        time = starting_time.hour + (starting_time.minute / 60)
        first_entry = BureauActifTimelineDayEntry.insert(self.create_new_timeline_entry(1, time))
        self.timeline_day_entries.append(first_entry)
