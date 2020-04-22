from services.BureauActif.libbureauactif.db.Base import db
from libtera.db.Base import BaseModel


class BureauActifTimelineDataType(db.Model, BaseModel):
    __tablename__ = "ba_timeline_data_type"
    id_timeline_data_type = db.Column(db.Integer, db.Sequence('id_timeline_data_type_sequence'), primary_key=True,
                                      autoincrement=True)
    name = db.Column(db.String, nullable=False)

    def to_json(self, ignore_fields=None, minimal=False):
        if ignore_fields is None:
            ignore_fields = []

        return super().to_json(ignore_fields=ignore_fields)

    @staticmethod
    def create_defaults():
        data = BureauActifTimelineDataType()
        data.name = ' '
        db.session.add(data)

        data2 = BureauActifTimelineDataType()
        data2.name = 'Debout'
        db.session.add(data2)

        data3 = BureauActifTimelineDataType()
        data3.name = 'Assis'
        db.session.add(data3)

        data4 = BureauActifTimelineDataType()
        data4.name = 'Absent'
        db.session.add(data4)

        data5 = BureauActifTimelineDataType()
        data5.name = 'Bouton appuyé - Debout'
        db.session.add(data5)

        data6 = BureauActifTimelineDataType()
        data6.name = 'Bouton appuyé - Assis'
        db.session.add(data6)

        db.session.commit()
