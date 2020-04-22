from services.BureauActif.libbureauactif.db.models.BureauActifCalendarDay import BureauActifCalendarDay
from services.BureauActif.libbureauactif.db.models.BureauActifCalendarData import BureauActifCalendarData
import datetime


class DBManagerBureauActifCalendarAccess:

    def query_calendar_day_by_month(self, date: datetime):
        month = date.month
        year = date.year
        calendar_days = BureauActifCalendarDay.get_calendar_day_by_month(month, year)

        return calendar_days

    def query_calendar_data(self, id_calendar_day: int, id_data_type: int):
        calendar_data = BureauActifCalendarData.get_calendar_data(id_calendar_day, id_data_type)
        return calendar_data
