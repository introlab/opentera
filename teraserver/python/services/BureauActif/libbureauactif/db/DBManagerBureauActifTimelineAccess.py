import datetime
from datetime import timedelta

from services.BureauActif.libbureauactif.db.models.BureauActifTimelineDay import BureauActifTimelineDay
from services.BureauActif.libbureauactif.db.models.BureauActifTimelineEntryType import BureauActifTimelineEntryType


class DBManagerBureauActifTimelineAccess:

    def query_timeline_days(self, first_date: datetime):
        last_date = first_date + timedelta(days=6)
        days = BureauActifTimelineDay.get_timeline_data(first_date, last_date)

        return days

    def query_timeline_type_by_id(self, type_id: int):
        entry_type = BureauActifTimelineEntryType.get_timeline_type_by_id(type_id)
        return entry_type
