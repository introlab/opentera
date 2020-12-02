from sqlalchemy import and_, func, desc
from services.BureauActif.libbureauactif.db.Base import db, BaseModel
import datetime


class BureauActifCalendarDay(db.Model, BaseModel):
    __tablename__ = "ba_calendar_day"
    id_calendar_day = db.Column(db.Integer, db.Sequence('id_calendar_day_sequence'), primary_key=True,
                                autoincrement=True)
    participant_uuid = db.Column(db.String(36), nullable=True)
    date = db.Column(db.TIMESTAMP(timezone=True), nullable=False)

    seating = db.relationship("BureauActifCalendarData",
                              primaryjoin="and_(BureauActifCalendarDay.id_calendar_day==BureauActifCalendarData"
                                          ".id_calendar_day, BureauActifCalendarData.id_calendar_data_type==1)",
                              uselist=False)
    standing = db.relationship("BureauActifCalendarData",
                               primaryjoin="and_(BureauActifCalendarDay.id_calendar_day==BureauActifCalendarData"
                                           ".id_calendar_day, BureauActifCalendarData.id_calendar_data_type==2)",
                               uselist=False)
    positionChanges = db.relationship("BureauActifCalendarData",
                                      primaryjoin="and_(BureauActifCalendarDay.id_calendar_day"
                                                  "==BureauActifCalendarData.id_calendar_day, "
                                                  "BureauActifCalendarData.id_calendar_data_type==3)",
                                      uselist=False)

    def to_json(self, ignore_fields=None, minimal=False):
        if ignore_fields is None:
            ignore_fields = []

        return super().to_json(ignore_fields=ignore_fields)

    @staticmethod
    def get_calendar_day_by_month(start_date, end_date, participant_uuid):
        days = BureauActifCalendarDay.query.filter(BureauActifCalendarDay.date.between(start_date, end_date),
                                                   BureauActifCalendarDay.participant_uuid == participant_uuid) \
            .order_by(BureauActifCalendarDay.date).all()
        if days:
            return days
        return None

    @staticmethod
    def get_last_entry(participant_uuid):
        day = BureauActifCalendarDay.query.filter(
            BureauActifCalendarDay.participant_uuid == participant_uuid).order_by(desc('date')).first()
        if day:
            return day
        return None

    @staticmethod
    def get_calendar_day(uuid_participant, date):
        entry = BureauActifCalendarDay.query.filter(
            and_(func.DATE(BureauActifCalendarDay.date) == date,
                 BureauActifCalendarDay.participant_uuid == uuid_participant)).first()
        if entry:
            return entry
        return None

    @classmethod
    def insert(cls, new_day):
        super().insert(new_day)
        db.session.commit()
        return new_day

    @classmethod
    def update(cls, update_id, values):
        super().update(update_id, values)

    @staticmethod
    def create_defaults():
        calendar_day = BureauActifCalendarDay()
        calendar_day.date = datetime.datetime.strptime('23-03-2020', '%d-%m-%Y').date()
        db.session.add(calendar_day)

        calendar_day2 = BureauActifCalendarDay()
        calendar_day2.date = datetime.datetime.strptime('24-03-2020', '%d-%m-%Y').date()
        db.session.add(calendar_day2)

        calendar_day3 = BureauActifCalendarDay()
        calendar_day3.date = datetime.datetime.strptime('25-03-2020', '%d-%m-%Y').date()
        db.session.add(calendar_day3)

        calendar_day4 = BureauActifCalendarDay()
        calendar_day4.date = datetime.datetime.strptime('26-03-2020', '%d-%m-%Y').date()
        db.session.add(calendar_day4)

        calendar_day5 = BureauActifCalendarDay()
        calendar_day5.date = datetime.datetime.strptime('27-03-2020', '%d-%m-%Y').date()
        db.session.add(calendar_day5)

        calendar_day6 = BureauActifCalendarDay()
        calendar_day6.date = datetime.datetime.strptime('30-03-2020', '%d-%m-%Y').date()
        db.session.add(calendar_day6)

        calendar_day7 = BureauActifCalendarDay()
        calendar_day7.date = datetime.datetime.strptime('31-03-2020', '%d-%m-%Y').date()
        db.session.add(calendar_day7)

        calendar_day8 = BureauActifCalendarDay()
        calendar_day8.date = datetime.datetime.strptime('01-04-2020', '%d-%m-%Y').date()
        db.session.add(calendar_day8)

        calendar_day9 = BureauActifCalendarDay()
        calendar_day9.date = datetime.datetime.strptime('02-04-2020', '%d-%m-%Y').date()
        db.session.add(calendar_day9)

        calendar_day10 = BureauActifCalendarDay()
        calendar_day10.date = datetime.datetime.strptime('03-04-2020', '%d-%m-%Y').date()
        db.session.add(calendar_day10)

        calendar_day11 = BureauActifCalendarDay()
        calendar_day11.date = datetime.datetime.strptime('06-04-2020', '%d-%m-%Y').date()
        db.session.add(calendar_day11)

        calendar_day12 = BureauActifCalendarDay()
        calendar_day12.date = datetime.datetime.strptime('07-04-2020', '%d-%m-%Y').date()
        db.session.add(calendar_day12)

        calendar_day13 = BureauActifCalendarDay()
        calendar_day13.date = datetime.datetime.strptime('08-04-2020', '%d-%m-%Y').date()
        db.session.add(calendar_day13)

        db.session.commit()
