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
        end_date = datetime.date(year, month, num_days)

        calendar_days = BureauActifCalendarDay.get_calendar_day_by_month(start_date, end_date, participant_uuid)

        return calendar_days

    def query_calendar_data(self, id_calendar_day: int, id_data_type: int):
        calendar_data = BureauActifCalendarData.get_calendar_data(id_calendar_day, id_data_type)
        return calendar_data
