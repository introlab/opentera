from services.BureauActif.libbureauactif.db.Base import db
from libtera.db.Base import BaseModel
import datetime
import os


class BureauActifTimelineData(db.Model, BaseModel):
    __tablename__ = "ba_timeline_data"
    id_timeline_data = db.Column(db.Integer, db.Sequence('id_timeline_data_sequence'), primary_key=True,
                                 autoincrement=True)
    name = db.Column(db.TIMESTAMP, nullable=False)

    series = db.relationship('BureauActifTimelineDayData')

    def to_json(self, ignore_fields=None, minimal=False):
        if ignore_fields is None:
            ignore_fields = []

        return super().to_json(ignore_fields=ignore_fields)

    @staticmethod
    def create_defaults():
        timeline_data = BureauActifTimelineData()
        timeline_data.name = datetime.datetime.strptime('02-03-2020', '%d-%m-%Y').date()
        db.session.add(timeline_data)

        timeline_data2 = BureauActifTimelineData()
        timeline_data2.name = datetime.datetime.strptime('03-03-2020', '%d-%m-%Y').date()
        db.session.add(timeline_data2)

        timeline_data3 = BureauActifTimelineData()
        timeline_data3.name = datetime.datetime.strptime('04-03-2020', '%d-%m-%Y').date()
        db.session.add(timeline_data3)

        db.session.commit()
