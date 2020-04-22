from services.BureauActif.libbureauactif.db.Base import db
from libtera.db.Base import BaseModel


class BureauActifCalendarDataType(db.Model, BaseModel):
    __tablename__ = "ba_calendar_data_type"
    id_calendar_data_type = db.Column(db.Integer, db.Sequence('id_calendar_data_type_sequence'), primary_key=True,
                                      autoincrement=True)
    name = db.Column(db.String, nullable=False)

    def to_json(self, ignore_fields=None, minimal=False):
        if ignore_fields is None:
            ignore_fields = []

        return super().to_json(ignore_fields=ignore_fields)

    @staticmethod
    def create_defaults():
        data = BureauActifCalendarDataType()
        data.name = 'seating'
        db.session.add(data)

        data2 = BureauActifCalendarDataType()
        data2.name = 'standing'
        db.session.add(data2)

        data3 = BureauActifCalendarDataType()
        data3.name = 'positionChanges'
        db.session.add(data3)

        db.session.commit()
