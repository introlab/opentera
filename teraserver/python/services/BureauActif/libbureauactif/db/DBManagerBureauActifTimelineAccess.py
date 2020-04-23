import datetime
from datetime import timedelta

from services.BureauActif.libbureauactif.db.models.BureauActifTimelineDay import BureauActifTimelineDay
from services.BureauActif.libbureauactif.db.models.BureauActifTimelineDayEntry import BureauActifTimelineDayEntry


class DBManagerBureauActifTimelineAccess:

    def query_timeline_days(self, first_date: datetime):
        last_date = first_date + timedelta(days=6)
        days = BureauActifTimelineDay.get_timeline_data(first_date, last_date)

        return days

    def query_timeline_entries(self, timeline_day_id: int):
        data = BureauActifTimelineDayEntry.get_timeline_day_entries(timeline_day_id)
        return data
