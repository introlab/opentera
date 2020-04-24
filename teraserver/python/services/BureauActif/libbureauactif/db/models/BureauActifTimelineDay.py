from services.BureauActif.libbureauactif.db.Base import db
from libtera.db.Base import BaseModel
import datetime
import os


class BureauActifTimelineDay(db.Model, BaseModel):
    __tablename__ = "ba_timeline_day"
    id_timeline_day = db.Column(db.Integer, db.Sequence('id_timeline_day_sequence'), primary_key=True,
                                autoincrement=True)
    name = db.Column(db.TIMESTAMP, nullable=False)

    series = db.relationship('BureauActifTimelineDayEntry')

    def to_json(self, ignore_fields=None, minimal=False):
        if ignore_fields is None:
            ignore_fields = []

        return super().to_json(ignore_fields=ignore_fields)

    @staticmethod
    def get_timeline_data(start_date, end_date):
        print(start_date, end_date)
        days = BureauActifTimelineDay.query.filter(BureauActifTimelineDay.name.between(start_date, end_date)).all()

        if days:
            return days

        return None

    @staticmethod
    def create_defaults():
        timeline_data = BureauActifTimelineDay()
        timeline_data.name = datetime.datetime.strptime('23-03-2020', '%d-%m-%Y').date()
        db.session.add(timeline_data)

        timeline_data2 = BureauActifTimelineDay()
        timeline_data2.name = datetime.datetime.strptime('24-03-2020', '%d-%m-%Y').date()
        db.session.add(timeline_data2)

        timeline_data3 = BureauActifTimelineDay()
        timeline_data3.name = datetime.datetime.strptime('25-03-2020', '%d-%m-%Y').date()
        db.session.add(timeline_data3)

        db.session.commit()
