from services.BureauActif.libbureauactif.db.Base import db, BaseModel


class BureauActifCalendarData(db.Model, BaseModel):
    __tablename__ = "ba_calendar_data"

    id_calendar_data = db.Column(db.Integer, db.Sequence('id_calendar_data_sequence'), primary_key=True,
                                 autoincrement=True)
    id_calendar_day = db.Column(db.Integer,
                                db.ForeignKey('ba_calendar_day.id_calendar_day', ondelete='cascade'),
                                nullable=True)
    id_calendar_data_type = db.Column(db.Integer,
                                      db.ForeignKey('ba_calendar_data_type.id_calendar_data_type', ondelete='cascade'),
                                      nullable=True)

    expected = db.Column(db.Float, nullable=False)
    done = db.Column(db.Float, nullable=False)

    # calendar_data_type = db.relationship('BureauActifCalendarDataType')

    def to_json(self, ignore_fields=None, minimal=False):
        if ignore_fields is None:
            ignore_fields = []

        return super().to_json(ignore_fields=ignore_fields)

    @staticmethod
    def get_calendar_data(id_calendar_day, id_data_type):
        data = BureauActifCalendarData.query.filter(BureauActifCalendarData.id_calendar_day == id_calendar_day,
                                                    BureauActifCalendarData.id_calendar_data_type == id_data_type).first()
        if data:
            return data

        return None

    @classmethod
    def insert(cls, new_data):
        super().insert(new_data)
        db.session.commit()
        return new_data

    @classmethod
    def update(cls, update_id, values):
        super().update(update_id, values)

    @staticmethod
    def create_defaults():
        first_data1 = BureauActifCalendarData()
        first_data1.expected = 3.5
        first_data1.done = 5.5
        first_data1.id_calendar_data_type = 1
        first_data1.id_calendar_day = 1
        db.session.add(first_data1)

        first_data2 = BureauActifCalendarData()
        first_data2.expected = 3.0
        first_data2.done = 0.5
        first_data2.id_calendar_data_type = 2
        first_data2.id_calendar_day = 1
        db.session.add(first_data2)

        first_data3 = BureauActifCalendarData()
        first_data3.expected = 11
        first_data3.done = 6
        first_data3.id_calendar_data_type = 3
        first_data3.id_calendar_day = 1
        db.session.add(first_data3)

        second_data1 = BureauActifCalendarData()
        second_data1.expected = 4.5
        second_data1.done = 4.5
        second_data1.id_calendar_data_type = 1
        second_data1.id_calendar_day = 2
        db.session.add(second_data1)

        second_data2 = BureauActifCalendarData()
        second_data2.expected = 3.5
        second_data2.done = 1.5
        second_data2.id_calendar_data_type = 2
        second_data2.id_calendar_day = 2
        db.session.add(second_data2)

        second_data3 = BureauActifCalendarData()
        second_data3.expected = 12
        second_data3.done = 9
        second_data3.id_calendar_data_type = 3
        second_data3.id_calendar_day = 2
        db.session.add(second_data3)

        third_data1 = BureauActifCalendarData()
        third_data1.expected = 5.5
        third_data1.done = 4.5
        third_data1.id_calendar_data_type = 1
        third_data1.id_calendar_day = 3
        db.session.add(third_data1)

        third_data2 = BureauActifCalendarData()
        third_data2.expected = 2.0
        third_data2.done = 2.5
        third_data2.id_calendar_data_type = 2
        third_data2.id_calendar_day = 3
        db.session.add(third_data2)

        third_data3 = BureauActifCalendarData()
        third_data3.expected = 11
        third_data3.done = 9
        third_data3.id_calendar_data_type = 3
        third_data3.id_calendar_day = 3
        db.session.add(third_data3)

        fourth_data1 = BureauActifCalendarData()
        fourth_data1.expected = 3.5
        fourth_data1.done = 3.5
        fourth_data1.id_calendar_data_type = 1
        fourth_data1.id_calendar_day = 4
        db.session.add(fourth_data1)

        fourth_data2 = BureauActifCalendarData()
        fourth_data2.expected = 3.5
        fourth_data2.done = 3.5
        fourth_data2.id_calendar_data_type = 2
        fourth_data2.id_calendar_day = 4
        db.session.add(fourth_data2)

        fourth_data3 = BureauActifCalendarData()
        fourth_data3.expected = 10
        fourth_data3.done = 14
        fourth_data3.id_calendar_data_type = 3
        fourth_data3.id_calendar_day = 4
        db.session.add(fourth_data3)

        fifth_data1 = BureauActifCalendarData()
        fifth_data1.expected = 4.5
        fifth_data1.done = 5.5
        fifth_data1.id_calendar_data_type = 1
        fifth_data1.id_calendar_day = 5
        db.session.add(fifth_data1)

        fifth_data2 = BureauActifCalendarData()
        fifth_data2.expected = 3.0
        fifth_data2.done = 0.5
        fifth_data2.id_calendar_data_type = 2
        fifth_data2.id_calendar_day = 5
        db.session.add(fifth_data2)

        fifth_data3 = BureauActifCalendarData()
        fifth_data3.expected = 9
        fifth_data3.done = 7
        fifth_data3.id_calendar_data_type = 3
        fifth_data3.id_calendar_day = 5
        db.session.add(fifth_data3)

        sixth_data1 = BureauActifCalendarData()
        sixth_data1.expected = 4
        sixth_data1.done = 4.5
        sixth_data1.id_calendar_data_type = 1
        sixth_data1.id_calendar_day = 6
        db.session.add(sixth_data1)

        sixth_data2 = BureauActifCalendarData()
        sixth_data2.expected = 3.5
        sixth_data2.done = 1.0
        sixth_data2.id_calendar_data_type = 2
        sixth_data2.id_calendar_day = 6
        db.session.add(sixth_data2)

        sixth_data3 = BureauActifCalendarData()
        sixth_data3.expected = 9
        sixth_data3.done = 6
        sixth_data3.id_calendar_data_type = 3
        sixth_data3.id_calendar_day = 6
        db.session.add(sixth_data3)

        seventh_data1 = BureauActifCalendarData()
        seventh_data1.expected = 4.0
        seventh_data1.done = 2.5
        seventh_data1.id_calendar_data_type = 1
        seventh_data1.id_calendar_day = 7
        db.session.add(seventh_data1)

        seventh_data2 = BureauActifCalendarData()
        seventh_data2.expected = 2.0
        seventh_data2.done = 1.0
        seventh_data2.id_calendar_data_type = 2
        seventh_data2.id_calendar_day = 7
        db.session.add(seventh_data2)

        seventh_data3 = BureauActifCalendarData()
        seventh_data3.expected = 10
        seventh_data3.done = 8
        seventh_data3.id_calendar_data_type = 3
        seventh_data3.id_calendar_day = 7
        db.session.add(seventh_data3)

        eighth_data1 = BureauActifCalendarData()
        eighth_data1.expected = 2.5
        eighth_data1.done = 3.0
        eighth_data1.id_calendar_data_type = 1
        eighth_data1.id_calendar_day = 8
        db.session.add(eighth_data1)

        eighth_data2 = BureauActifCalendarData()
        eighth_data2.expected = 3.0
        eighth_data2.done = 2.5
        eighth_data2.id_calendar_data_type = 2
        eighth_data2.id_calendar_day = 8
        db.session.add(eighth_data2)

        eighth_data3 = BureauActifCalendarData()
        eighth_data3.expected = 8
        eighth_data3.done = 10
        eighth_data3.id_calendar_data_type = 3
        eighth_data3.id_calendar_day = 8
        db.session.add(eighth_data3)

        ninth_data1 = BureauActifCalendarData()
        ninth_data1.expected = 5
        ninth_data1.done = 6.5
        ninth_data1.id_calendar_data_type = 1
        ninth_data1.id_calendar_day = 9
        db.session.add(ninth_data1)

        ninth_data2 = BureauActifCalendarData()
        ninth_data2.expected = 3.0
        ninth_data2.done = 0.5
        ninth_data2.id_calendar_data_type = 2
        ninth_data2.id_calendar_day = 9
        db.session.add(ninth_data2)

        ninth_data3 = BureauActifCalendarData()
        ninth_data3.expected = 11
        ninth_data3.done = 1
        ninth_data3.id_calendar_data_type = 3
        ninth_data3.id_calendar_day = 9
        db.session.add(ninth_data3)

        tenth_data1 = BureauActifCalendarData()
        tenth_data1.expected = 3.5
        tenth_data1.done = 4.5
        tenth_data1.id_calendar_data_type = 1
        tenth_data1.id_calendar_day = 10
        db.session.add(tenth_data1)

        tenth_data2 = BureauActifCalendarData()
        tenth_data2.expected = 2.5
        tenth_data2.done = 1.0
        tenth_data2.id_calendar_data_type = 2
        tenth_data2.id_calendar_day = 10
        db.session.add(tenth_data2)

        tenth_data3 = BureauActifCalendarData()
        tenth_data3.expected = 12
        tenth_data3.done = 6
        tenth_data3.id_calendar_data_type = 3
        tenth_data3.id_calendar_day = 10
        db.session.add(tenth_data3)

        eleventh_data1 = BureauActifCalendarData()
        eleventh_data1.expected = 2
        eleventh_data1.done = 3.3
        eleventh_data1.id_calendar_data_type = 1
        eleventh_data1.id_calendar_day = 11
        db.session.add(eleventh_data1)

        eleventh_data2 = BureauActifCalendarData()
        eleventh_data2.expected = 3.5
        eleventh_data2.done = 1.5
        eleventh_data2.id_calendar_data_type = 2
        eleventh_data2.id_calendar_day = 11
        db.session.add(eleventh_data2)

        eleventh_data3 = BureauActifCalendarData()
        eleventh_data3.expected = 9
        eleventh_data3.done = 3
        eleventh_data3.id_calendar_data_type = 3
        eleventh_data3.id_calendar_day = 11
        db.session.add(eleventh_data3)

        twelfth_data1 = BureauActifCalendarData()
        twelfth_data1.expected = 4.6
        twelfth_data1.done = 2.2
        twelfth_data1.id_calendar_data_type = 1
        twelfth_data1.id_calendar_day = 12
        db.session.add(twelfth_data1)

        twelfth_data2 = BureauActifCalendarData()
        twelfth_data2.expected = 2.5
        twelfth_data2.done = 0.5
        twelfth_data2.id_calendar_data_type = 2
        twelfth_data2.id_calendar_day = 12
        db.session.add(twelfth_data2)

        twelfth_data3 = BureauActifCalendarData()
        twelfth_data3.expected = 10
        twelfth_data3.done = 2
        twelfth_data3.id_calendar_data_type = 3
        twelfth_data3.id_calendar_day = 12
        db.session.add(twelfth_data3)

        thirteenth_data1 = BureauActifCalendarData()
        thirteenth_data1.expected = 3.0
        thirteenth_data1.done = 3.0
        thirteenth_data1.id_calendar_data_type = 1
        thirteenth_data1.id_calendar_day = 13
        db.session.add(thirteenth_data1)

        thirteenth_data2 = BureauActifCalendarData()
        thirteenth_data2.expected = 4.0
        thirteenth_data2.done = 2.0
        thirteenth_data2.id_calendar_data_type = 2
        thirteenth_data2.id_calendar_day = 13
        db.session.add(thirteenth_data2)

        thirteenth_data3 = BureauActifCalendarData()
        thirteenth_data3.expected = 12
        thirteenth_data3.done = 10
        thirteenth_data3.id_calendar_data_type = 3
        thirteenth_data3.id_calendar_day = 13
        db.session.add(thirteenth_data3)

        db.session.commit()
