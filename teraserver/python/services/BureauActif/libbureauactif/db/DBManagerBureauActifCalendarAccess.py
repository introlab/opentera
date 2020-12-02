from services.BureauActif.libbureauactif.db.models.BureauActifCalendarDay import BureauActifCalendarDay
from services.BureauActif.libbureauactif.db.models.BureauActifCalendarData import BureauActifCalendarData
import datetime
import calendar


class DBManagerBureauActifCalendarAccess:

    def query_calendar_day_by_month(self, date: datetime, participant_uuid):
        month = date.month
        year = date.year

        num_days = calendar.monthrange(year, month)[1]
        start_date = datetime.date(year, month, 1)
        end_date = datetime.datetime(year, month, num_days, 23, 59)

        calendar_days = BureauActifCalendarDay.get_calendar_day_by_month(start_date, end_date, participant_uuid)

        return calendar_days

    def query_last_calendar_days(self, participant_uuid):
        last_day = BureauActifCalendarDay.get_last_entry(participant_uuid)

        if last_day is not None:
            month = last_day.date.month
            year = last_day.date.year

            num_days = calendar.monthrange(year, month)[1]
            start_date = datetime.date(year, month, 1)
            end_date = datetime.datetime(year, month, num_days, 23, 59)

            calendar_days = BureauActifCalendarDay.get_calendar_day_by_month(start_date, end_date, participant_uuid)

            return calendar_days
        return None
