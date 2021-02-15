from services.BureauActif.libbureauactif.db.Base import db, BaseModel
import datetime
import os


class BureauActifTimelineDayEntry(db.Model, BaseModel):
    __tablename__ = "ba_timeline_day_entry"
    id_timeline_day_entry = db.Column(db.Integer, db.Sequence('id_timeline_day_entry_sequence'), primary_key=True,
                                      autoincrement=True)
    id_timeline_day = db.Column(db.Integer, db.ForeignKey('ba_timeline_day.id_timeline_day', ondelete='cascade'),
                                nullable=True)
    id_timeline_entry_type = db.Column(db.Integer,
                                       db.ForeignKey('ba_timeline_entry_type.id_timeline_entry_type',
                                                     ondelete='cascade'),
                                       nullable=True)
    value = db.Column(db.Float, nullable=False)
    start_time = db.Column(db.TIMESTAMP(timezone=True), nullable=True)
    end_time = db.Column(db.TIMESTAMP(timezone=True), nullable=True)
    entry_type = db.relationship('BureauActifTimelineEntryType')

    def to_json(self, ignore_fields=None, minimal=False):
        if ignore_fields is None:
            ignore_fields = []
        ignore_fields.append('entry_type')

        return super().to_json(ignore_fields=ignore_fields)

    @staticmethod
    def get_timeline_day_entries(timeline_day_id: int):
        return BureauActifTimelineDayEntry.query.filter_by(id_timeline_day=timeline_day_id).order_by(
            BureauActifTimelineDayEntry.id_timeline_day_entry).all()

    @classmethod
    def insert(cls, new_entry):
        super().insert(new_entry)
        db.session.commit()
        return new_entry

    @staticmethod
    def update_entry(id_entry, value):
        BureauActifTimelineDayEntry.query.filter_by(id_timeline_day_entry=id_entry).update(dict(value=value))
        db.session.commit()

    @classmethod
    def update(cls, id_entry, value):
        super().update(id_entry, dict(value=value))

    @staticmethod
    def create_defaults():
        first_day1 = BureauActifTimelineDayEntry()
        first_day1.id_timeline_entry_type = 1
        first_day1.value = 7.8
        first_day1.id_timeline_day = 1
        db.session.add(first_day1)

        first_day2 = BureauActifTimelineDayEntry()
        first_day2.id_timeline_entry_type = 2
        first_day2.value = 0.5
        first_day2.id_timeline_day = 1
        db.session.add(first_day2)

        first_day3 = BureauActifTimelineDayEntry()
        first_day3.id_timeline_entry_type = 5
        first_day3.value = 0.5
        first_day3.id_timeline_day = 1
        db.session.add(first_day3)

        first_day4 = BureauActifTimelineDayEntry()
        first_day4.id_timeline_entry_type = 3
        first_day4.value = 0.1
        first_day4.id_timeline_day = 1
        db.session.add(first_day4)

        first_day5 = BureauActifTimelineDayEntry()
        first_day5.id_timeline_entry_type = 4
        first_day5.value = 0.02
        first_day5.id_timeline_day = 1
        db.session.add(first_day5)

        first_day6 = BureauActifTimelineDayEntry()
        first_day6.id_timeline_entry_type = 2
        first_day6.value = 0.4
        first_day6.id_timeline_day = 1
        db.session.add(first_day6)

        first_day7 = BureauActifTimelineDayEntry()
        first_day7.id_timeline_entry_type = 3
        first_day7.value = 0.5
        first_day7.id_timeline_day = 1
        db.session.add(first_day7)

        first_day8 = BureauActifTimelineDayEntry()
        first_day8.id_timeline_entry_type = 5
        first_day8.value = 0.5
        first_day8.id_timeline_day = 1
        db.session.add(first_day8)

        first_day9 = BureauActifTimelineDayEntry()
        first_day9.id_timeline_entry_type = 3
        first_day9.value = 0.5
        first_day9.id_timeline_day = 1
        db.session.add(first_day9)

        first_day10 = BureauActifTimelineDayEntry()
        first_day10.id_timeline_entry_type = 5
        first_day10.value = 0.5
        first_day10.id_timeline_day = 1
        db.session.add(first_day10)

        first_day11 = BureauActifTimelineDayEntry()
        first_day11.id_timeline_entry_type = 6
        first_day11.value = 0.5
        first_day11.id_timeline_day = 1
        db.session.add(first_day11)

        first_day12 = BureauActifTimelineDayEntry()
        first_day12.id_timeline_entry_type = 2
        first_day12.value = 0.4
        first_day12.id_timeline_day = 1
        db.session.add(first_day12)

        first_day13 = BureauActifTimelineDayEntry()
        first_day13.id_timeline_entry_type = 4
        first_day13.value = 0.1
        first_day13.id_timeline_day = 1
        db.session.add(first_day13)

        first_day14 = BureauActifTimelineDayEntry()
        first_day14.id_timeline_entry_type = 3
        first_day14.value = 0.5
        first_day14.id_timeline_day = 1
        db.session.add(first_day14)

        first_day15 = BureauActifTimelineDayEntry()
        first_day15.id_timeline_entry_type = 5
        first_day15.value = 0.5
        first_day15.id_timeline_day = 1
        db.session.add(first_day15)

        first_day16 = BureauActifTimelineDayEntry()
        first_day16.id_timeline_entry_type = 3
        first_day16.value = 0.5
        first_day16.id_timeline_day = 1
        db.session.add(first_day16)

        first_day17 = BureauActifTimelineDayEntry()
        first_day17.id_timeline_entry_type = 5
        first_day17.value = 0.5
        first_day17.id_timeline_day = 1
        db.session.add(first_day17)

        first_day18 = BureauActifTimelineDayEntry()
        first_day18.id_timeline_entry_type = 6
        first_day18.value = 0.5
        first_day18.id_timeline_day = 1
        db.session.add(first_day18)

        first_day19 = BureauActifTimelineDayEntry()
        first_day19.id_timeline_entry_type = 5
        first_day19.value = 0.5
        first_day19.id_timeline_day = 1
        db.session.add(first_day19)

        first_day20 = BureauActifTimelineDayEntry()
        first_day20.id_timeline_entry_type = 2
        first_day20.value = 0.4
        first_day20.id_timeline_day = 1
        db.session.add(first_day20)

        first_day21 = BureauActifTimelineDayEntry()
        first_day21.id_timeline_entry_type = 5
        first_day21.value = 0.1
        first_day21.id_timeline_day = 1
        db.session.add(first_day21)

        first_day22 = BureauActifTimelineDayEntry()
        first_day22.id_timeline_entry_type = 3
        first_day22.value = 0.5
        first_day22.id_timeline_day = 1
        db.session.add(first_day22)

        second_day1 = BureauActifTimelineDayEntry()
        second_day1.id_timeline_entry_type = 1
        second_day1.value = 8
        second_day1.id_timeline_day = 2
        db.session.add(second_day1)

        second_day2 = BureauActifTimelineDayEntry()
        second_day2.id_timeline_entry_type = 3
        second_day2.value = 0.5
        second_day2.id_timeline_day = 2
        db.session.add(second_day2)

        second_day3 = BureauActifTimelineDayEntry()
        second_day3.id_timeline_entry_type = 2
        second_day3.value = 0.5
        second_day3.id_timeline_day = 2
        db.session.add(second_day3)

        second_day4 = BureauActifTimelineDayEntry()
        second_day4.id_timeline_entry_type = 3
        second_day4.value = 0.5
        second_day4.id_timeline_day = 2
        db.session.add(second_day4)

        second_day5 = BureauActifTimelineDayEntry()
        second_day5.id_timeline_entry_type = 2
        second_day5.value = 0.5
        second_day5.id_timeline_day = 2
        db.session.add(second_day5)

        second_day6 = BureauActifTimelineDayEntry()
        second_day6.id_timeline_entry_type = 4
        second_day6.value = 0.2
        second_day6.id_timeline_day = 2
        db.session.add(second_day6)

        second_day7 = BureauActifTimelineDayEntry()
        second_day7.id_timeline_entry_type = 3
        second_day7.value = 0.5
        second_day7.id_timeline_day = 2
        db.session.add(second_day7)

        second_day8 = BureauActifTimelineDayEntry()
        second_day8.id_timeline_entry_type = 2
        second_day8.value = 0.5
        second_day8.id_timeline_day = 2
        db.session.add(second_day8)

        second_day9 = BureauActifTimelineDayEntry()
        second_day9.id_timeline_entry_type = 3
        second_day9.value = 0.5
        second_day9.id_timeline_day = 2
        db.session.add(second_day9)

        second_day10 = BureauActifTimelineDayEntry()
        second_day10.id_timeline_entry_type = 5
        second_day10.value = 0.5
        second_day10.id_timeline_day = 2
        db.session.add(second_day10)

        second_day11 = BureauActifTimelineDayEntry()
        second_day11.id_timeline_entry_type = 3
        second_day11.value = 0.5
        second_day11.id_timeline_day = 2
        db.session.add(second_day11)

        second_day12 = BureauActifTimelineDayEntry()
        second_day12.id_timeline_entry_type = 2
        second_day12.value = 0.5
        second_day12.id_timeline_day = 2
        db.session.add(second_day12)

        second_day13 = BureauActifTimelineDayEntry()
        second_day13.id_timeline_entry_type = 3
        second_day13.value = 0.5
        second_day13.id_timeline_day = 2
        db.session.add(second_day13)

        second_day14 = BureauActifTimelineDayEntry()
        second_day14.id_timeline_entry_type = 4
        second_day14.value = 0.87
        second_day14.id_timeline_day = 2
        db.session.add(second_day14)

        second_day15 = BureauActifTimelineDayEntry()
        second_day15.id_timeline_entry_type = 3
        second_day15.value = 0.5
        second_day15.id_timeline_day = 2
        db.session.add(second_day15)

        second_day16 = BureauActifTimelineDayEntry()
        second_day16.id_timeline_entry_type = 5
        second_day16.value = 0.5
        second_day16.id_timeline_day = 2
        db.session.add(second_day16)

        second_day17 = BureauActifTimelineDayEntry()
        second_day17.id_timeline_entry_type = 3
        second_day17.value = 0.5
        second_day17.id_timeline_day = 2
        db.session.add(second_day17)

        third_day1 = BureauActifTimelineDayEntry()
        third_day1.id_timeline_entry_type = 1
        third_day1.value = 7.45
        third_day1.id_timeline_day = 3
        db.session.add(third_day1)

        third_day2 = BureauActifTimelineDayEntry()
        third_day2.id_timeline_entry_type = 3
        third_day2.value = 0.5
        third_day2.id_timeline_day = 3
        db.session.add(third_day2)

        third_day3 = BureauActifTimelineDayEntry()
        third_day3.id_timeline_entry_type = 5
        third_day3.value = 0.5
        third_day3.id_timeline_day = 3
        db.session.add(third_day3)

        third_day4 = BureauActifTimelineDayEntry()
        third_day4.id_timeline_entry_type = 3
        third_day4.value = 0.5
        third_day4.id_timeline_day = 3
        db.session.add(third_day4)

        third_day5 = BureauActifTimelineDayEntry()
        third_day5.id_timeline_entry_type = 2
        third_day5.value = 0.1
        third_day5.id_timeline_day = 3
        db.session.add(third_day5)

        third_day6 = BureauActifTimelineDayEntry()
        third_day6.id_timeline_entry_type = 5
        third_day6.value = 0.4
        third_day6.id_timeline_day = 3
        db.session.add(third_day6)

        third_day7 = BureauActifTimelineDayEntry()
        third_day7.id_timeline_entry_type = 3
        third_day7.value = 0.5
        third_day7.id_timeline_day = 3
        db.session.add(third_day7)

        third_day8 = BureauActifTimelineDayEntry()
        third_day8.id_timeline_entry_type = 5
        third_day8.value = 0.5
        third_day8.id_timeline_day = 3
        db.session.add(third_day8)

        third_day9 = BureauActifTimelineDayEntry()
        third_day9.id_timeline_entry_type = 3
        third_day9.value = 0.5
        third_day9.id_timeline_day = 3
        db.session.add(third_day9)

        third_day10 = BureauActifTimelineDayEntry()
        third_day10.id_timeline_entry_type = 4
        third_day10.value = 0.7
        third_day10.id_timeline_day = 3
        db.session.add(third_day10)

        third_day11 = BureauActifTimelineDayEntry()
        third_day11.id_timeline_entry_type = 6
        third_day11.value = 0.5
        third_day11.id_timeline_day = 3
        db.session.add(third_day11)

        third_day12 = BureauActifTimelineDayEntry()
        third_day12.id_timeline_entry_type = 5
        third_day12.value = 0.5
        third_day12.id_timeline_day = 3
        db.session.add(third_day12)

        third_day13 = BureauActifTimelineDayEntry()
        third_day13.id_timeline_entry_type = 6
        third_day13.value = 0.1
        third_day13.id_timeline_day = 3
        db.session.add(third_day13)

        third_day14 = BureauActifTimelineDayEntry()
        third_day14.id_timeline_entry_type = 5
        third_day14.value = 0.5
        third_day14.id_timeline_day = 3
        db.session.add(third_day14)

        third_day15 = BureauActifTimelineDayEntry()
        third_day15.id_timeline_entry_type = 3
        third_day15.value = 0.5
        third_day15.id_timeline_day = 3
        db.session.add(third_day15)

        third_day16 = BureauActifTimelineDayEntry()
        third_day16.id_timeline_entry_type = 2
        third_day16.value = 0.3
        third_day16.id_timeline_day = 3
        db.session.add(third_day16)

        third_day17 = BureauActifTimelineDayEntry()
        third_day17.id_timeline_entry_type = 5
        third_day17.value = 0.5
        third_day17.id_timeline_day = 3
        db.session.add(third_day17)

        third_day18 = BureauActifTimelineDayEntry()
        third_day18.id_timeline_entry_type = 3
        third_day18.value = 0.2
        third_day18.id_timeline_day = 3
        db.session.add(third_day18)

        third_day19 = BureauActifTimelineDayEntry()
        third_day19.id_timeline_entry_type = 4
        third_day19.value = 0.2
        third_day19.id_timeline_day = 3
        db.session.add(third_day19)

        third_day20 = BureauActifTimelineDayEntry()
        third_day20.id_timeline_entry_type = 3
        third_day20.value = 0.3
        third_day20.id_timeline_day = 3
        db.session.add(third_day20)

        db.session.commit()
