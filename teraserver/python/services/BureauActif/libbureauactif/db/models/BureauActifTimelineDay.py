from sqlalchemy import and_

from services.BureauActif.libbureauactif.db.Base import db
from libtera.db.Base import BaseModel
import datetime
import os


class BureauActifTimelineDay(db.Model, BaseModel):
    __tablename__ = "ba_timeline_day"
    id_timeline_day = db.Column(db.Integer, db.Sequence('id_timeline_day_sequence'), primary_key=True,
                                autoincrement=True)
    participant_uuid = db.Column(db.String(36), nullable=True)
    name = db.Column(db.TIMESTAMP(timezone=True), nullable=False)

    series = db.relationship('BureauActifTimelineDayEntry')

    def to_json(self, ignore_fields=None, minimal=False):
        if ignore_fields is None:
            ignore_fields = []

        return super().to_json(ignore_fields=ignore_fields)

    @staticmethod
    def get_timeline_data(start_date, end_date, participant_uuid):
        days = BureauActifTimelineDay.query.filter(BureauActifTimelineDay.name.between(start_date, end_date),
                                                   BureauActifTimelineDay.participant_uuid == participant_uuid).all()
        if days:
            return days
        return None

    @staticmethod
    def get_timeline_day(uuid_participant, date):
        entry = BureauActifTimelineDay.query.filter(
            and_(BureauActifTimelineDay.name == date,
                 BureauActifTimelineDay.participant_uuid == uuid_participant)).first()
        if entry:
            return entry
        return None

    @classmethod
    def insert(cls, new_day):
        super().insert(new_day)
        db.session.commit()
        return new_day

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
