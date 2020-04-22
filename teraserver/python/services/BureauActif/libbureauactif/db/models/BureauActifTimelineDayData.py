from services.BureauActif.libbureauactif.db.Base import db
from libtera.db.Base import BaseModel
import datetime
import os


class BureauActifTimelineDayData(db.Model, BaseModel):
    __tablename__ = "ba_timeline_day_data"
    id_timeline_day_data = db.Column(db.Integer, db.Sequence('id_timeline_day_data_sequence'), primary_key=True,
                                     autoincrement=True)
    id_timeline_data = db.Column(db.Integer, db.ForeignKey('ba_timeline_data.id_timeline_data', ondelete='cascade'),
                                 nullable=True)
    id_timeline_data_type = db.Column(db.Integer,
                                      db.ForeignKey('ba_timeline_data_type.id_timeline_data_type', ondelete='cascade'),
                                      nullable=True)
    value = db.Column(db.Float, nullable=False)

    timeline_data_type = db.relationship("BureauActifTimelineDataType")

    def to_json(self, ignore_fields=None, minimal=False):
        if ignore_fields is None:
            ignore_fields = []

        return super().to_json(ignore_fields=ignore_fields)

    @staticmethod
    def create_defaults():
        first_day1 = BureauActifTimelineDayData()
        first_day1.id_timeline_data_type = 1
        first_day1.value = 7.8
        first_day1.id_timeline_data = 1
        db.session.add(first_day1)

        first_day2 = BureauActifTimelineDayData()
        first_day2.id_timeline_data_type = 2
        first_day2.value = 0.5
        first_day2.id_timeline_data = 1
        db.session.add(first_day2)

        first_day3 = BureauActifTimelineDayData()
        first_day3.id_timeline_data_type = 5
        first_day3.value = 0.5
        first_day3.id_timeline_data = 1
        db.session.add(first_day3)

        first_day4 = BureauActifTimelineDayData()
        first_day4.id_timeline_data_type = 3
        first_day4.value = 0.1
        first_day4.id_timeline_data = 1
        db.session.add(first_day4)

        first_day5 = BureauActifTimelineDayData()
        first_day5.id_timeline_data_type = 4
        first_day5.value = 0.02
        first_day5.id_timeline_data = 1
        db.session.add(first_day5)

        first_day6 = BureauActifTimelineDayData()
        first_day6.id_timeline_data_type = 2
        first_day6.value = 0.4
        first_day6.id_timeline_data = 1
        db.session.add(first_day6)

        first_day7 = BureauActifTimelineDayData()
        first_day7.id_timeline_data_type = 3
        first_day7.value = 0.5
        first_day7.id_timeline_data = 1
        db.session.add(first_day7)

        first_day8 = BureauActifTimelineDayData()
        first_day8.id_timeline_data_type = 5
        first_day8.value = 0.5
        first_day8.id_timeline_data = 1
        db.session.add(first_day8)

        first_day9 = BureauActifTimelineDayData()
        first_day9.id_timeline_data_type = 3
        first_day9.value = 0.5
        first_day9.id_timeline_data = 1
        db.session.add(first_day9)

        first_day10 = BureauActifTimelineDayData()
        first_day10.id_timeline_data_type = 5
        first_day10.value = 0.5
        first_day10.id_timeline_data = 1
        db.session.add(first_day10)

        first_day11 = BureauActifTimelineDayData()
        first_day11.id_timeline_data_type = 6
        first_day11.value = 0.5
        first_day11.id_timeline_data = 1
        db.session.add(first_day11)

        first_day12 = BureauActifTimelineDayData()
        first_day12.id_timeline_data_type = 2
        first_day12.value = 0.4
        first_day12.id_timeline_data = 1
        db.session.add(first_day12)

        first_day13 = BureauActifTimelineDayData()
        first_day13.id_timeline_data_type = 4
        first_day13.value = 0.1
        first_day13.id_timeline_data = 1
        db.session.add(first_day13)

        first_day14 = BureauActifTimelineDayData()
        first_day14.id_timeline_data_type = 3
        first_day14.value = 0.5
        first_day14.id_timeline_data = 1
        db.session.add(first_day14)

        first_day15 = BureauActifTimelineDayData()
        first_day15.id_timeline_data_type = 5
        first_day15.value = 0.5
        first_day15.id_timeline_data = 1
        db.session.add(first_day15)

        first_day16 = BureauActifTimelineDayData()
        first_day16.id_timeline_data_type = 3
        first_day16.value = 0.5
        first_day16.id_timeline_data = 1
        db.session.add(first_day16)

        first_day17 = BureauActifTimelineDayData()
        first_day17.id_timeline_data_type = 5
        first_day17.value = 0.5
        first_day17.id_timeline_data = 1
        db.session.add(first_day17)

        first_day18 = BureauActifTimelineDayData()
        first_day18.id_timeline_data_type = 6
        first_day18.value = 0.5
        first_day18.id_timeline_data = 1
        db.session.add(first_day18)

        first_day19 = BureauActifTimelineDayData()
        first_day19.id_timeline_data_type = 5
        first_day19.value = 0.5
        first_day19.id_timeline_data = 1
        db.session.add(first_day19)

        first_day20 = BureauActifTimelineDayData()
        first_day20.id_timeline_data_type = 2
        first_day20.value = 0.4
        first_day20.id_timeline_data = 1
        db.session.add(first_day20)

        first_day21 = BureauActifTimelineDayData()
        first_day21.id_timeline_data_type = 5
        first_day21.value = 0.1
        first_day21.id_timeline_data = 1
        db.session.add(first_day21)

        first_day22 = BureauActifTimelineDayData()
        first_day22.id_timeline_data_type = 3
        first_day22.value = 0.5
        first_day22.id_timeline_data = 1
        db.session.add(first_day22)

        second_day1 = BureauActifTimelineDayData()
        second_day1.id_timeline_data_type = 1
        second_day1.value = 8
        second_day1.id_timeline_data = 2
        db.session.add(second_day1)

        second_day2 = BureauActifTimelineDayData()
        second_day2.id_timeline_data_type = 3
        second_day2.value = 0.5
        second_day2.id_timeline_data = 2
        db.session.add(second_day2)

        second_day3 = BureauActifTimelineDayData()
        second_day3.id_timeline_data_type = 2
        second_day3.value = 0.5
        second_day3.id_timeline_data = 2
        db.session.add(second_day3)

        second_day4 = BureauActifTimelineDayData()
        second_day4.id_timeline_data_type = 3
        second_day4.value = 0.5
        second_day4.id_timeline_data = 2
        db.session.add(second_day4)

        second_day5 = BureauActifTimelineDayData()
        second_day5.id_timeline_data_type = 2
        second_day5.value = 0.5
        second_day5.id_timeline_data = 2
        db.session.add(second_day5)

        second_day6 = BureauActifTimelineDayData()
        second_day6.id_timeline_data_type = 4
        second_day6.value = 0.2
        second_day6.id_timeline_data = 2
        db.session.add(second_day6)

        second_day7 = BureauActifTimelineDayData()
        second_day7.id_timeline_data_type = 3
        second_day7.value = 0.5
        second_day7.id_timeline_data = 2
        db.session.add(second_day7)

        second_day8 = BureauActifTimelineDayData()
        second_day8.id_timeline_data_type = 2
        second_day8.value = 0.5
        second_day8.id_timeline_data = 2
        db.session.add(second_day8)

        second_day9 = BureauActifTimelineDayData()
        second_day9.id_timeline_data_type = 3
        second_day9.value = 0.5
        second_day9.id_timeline_data = 2
        db.session.add(second_day9)

        second_day10 = BureauActifTimelineDayData()
        second_day10.id_timeline_data_type = 5
        second_day10.value = 0.5
        second_day10.id_timeline_data = 2
        db.session.add(second_day10)

        second_day11 = BureauActifTimelineDayData()
        second_day11.id_timeline_data_type = 3
        second_day11.value = 0.5
        second_day11.id_timeline_data = 2
        db.session.add(second_day11)

        second_day12 = BureauActifTimelineDayData()
        second_day12.id_timeline_data_type = 2
        second_day12.value = 0.5
        second_day12.id_timeline_data = 2
        db.session.add(second_day12)

        second_day13 = BureauActifTimelineDayData()
        second_day13.id_timeline_data_type = 3
        second_day13.value = 0.5
        second_day13.id_timeline_data = 2
        db.session.add(second_day13)

        second_day14 = BureauActifTimelineDayData()
        second_day14.id_timeline_data_type = 4
        second_day14.value = 0.87
        second_day14.id_timeline_data = 2
        db.session.add(second_day14)

        second_day15 = BureauActifTimelineDayData()
        second_day15.id_timeline_data_type = 3
        second_day15.value = 0.5
        second_day15.id_timeline_data = 2
        db.session.add(second_day15)

        second_day16 = BureauActifTimelineDayData()
        second_day16.id_timeline_data_type = 5
        second_day16.value = 0.5
        second_day16.id_timeline_data = 2
        db.session.add(second_day16)

        second_day17 = BureauActifTimelineDayData()
        second_day17.id_timeline_data_type = 3
        second_day17.value = 0.5
        second_day17.id_timeline_data = 2
        db.session.add(second_day17)

        third_day1 = BureauActifTimelineDayData()
        third_day1.id_timeline_data_type = 1
        third_day1.value = 7.45
        third_day1.id_timeline_data = 3
        db.session.add(third_day1)

        third_day2 = BureauActifTimelineDayData()
        third_day2.id_timeline_data_type = 3
        third_day2.value = 0.5
        third_day2.id_timeline_data = 3
        db.session.add(third_day2)

        third_day3 = BureauActifTimelineDayData()
        third_day3.id_timeline_data_type = 5
        third_day3.value = 0.5
        third_day3.id_timeline_data = 3
        db.session.add(third_day3)

        third_day4 = BureauActifTimelineDayData()
        third_day4.id_timeline_data_type = 3
        third_day4.value = 0.5
        third_day4.id_timeline_data = 3
        db.session.add(third_day4)

        third_day5 = BureauActifTimelineDayData()
        third_day5.id_timeline_data_type = 2
        third_day5.value = 0.1
        third_day5.id_timeline_data = 3
        db.session.add(third_day5)

        third_day6 = BureauActifTimelineDayData()
        third_day6.id_timeline_data_type = 5
        third_day6.value = 0.4
        third_day6.id_timeline_data = 3
        db.session.add(third_day6)

        third_day7 = BureauActifTimelineDayData()
        third_day7.id_timeline_data_type = 3
        third_day7.value = 0.5
        third_day7.id_timeline_data = 3
        db.session.add(third_day7)

        third_day8 = BureauActifTimelineDayData()
        third_day8.id_timeline_data_type = 5
        third_day8.value = 0.5
        third_day8.id_timeline_data = 3
        db.session.add(third_day8)

        third_day9 = BureauActifTimelineDayData()
        third_day9.id_timeline_data_type = 3
        third_day9.value = 0.5
        third_day9.id_timeline_data = 3
        db.session.add(third_day9)

        third_day10 = BureauActifTimelineDayData()
        third_day10.id_timeline_data_type = 4
        third_day10.value = 0.7
        third_day10.id_timeline_data = 3
        db.session.add(third_day10)

        third_day11 = BureauActifTimelineDayData()
        third_day11.id_timeline_data_type = 6
        third_day11.value = 0.5
        third_day11.id_timeline_data = 3
        db.session.add(third_day11)

        third_day12 = BureauActifTimelineDayData()
        third_day12.id_timeline_data_type = 5
        third_day12.value = 0.5
        third_day12.id_timeline_data = 3
        db.session.add(third_day12)

        third_day13 = BureauActifTimelineDayData()
        third_day13.id_timeline_data_type = 6
        third_day13.value = 0.1
        third_day13.id_timeline_data = 3
        db.session.add(third_day13)

        third_day14 = BureauActifTimelineDayData()
        third_day14.id_timeline_data_type = 5
        third_day14.value = 0.5
        third_day14.id_timeline_data = 3
        db.session.add(third_day14)

        third_day15 = BureauActifTimelineDayData()
        third_day15.id_timeline_data_type = 3
        third_day15.value = 0.5
        third_day15.id_timeline_data = 3
        db.session.add(third_day15)

        third_day16 = BureauActifTimelineDayData()
        third_day16.id_timeline_data_type = 2
        third_day16.value = 0.3
        third_day16.id_timeline_data = 3
        db.session.add(third_day16)

        third_day17 = BureauActifTimelineDayData()
        third_day17.id_timeline_data_type = 5
        third_day17.value = 0.5
        third_day17.id_timeline_data = 3
        db.session.add(third_day17)

        third_day18 = BureauActifTimelineDayData()
        third_day18.id_timeline_data_type = 3
        third_day18.value = 0.2
        third_day18.id_timeline_data = 3
        db.session.add(third_day18)

        third_day19 = BureauActifTimelineDayData()
        third_day19.id_timeline_data_type = 4
        third_day19.value = 0.2
        third_day19.id_timeline_data = 3
        db.session.add(third_day19)

        third_day20 = BureauActifTimelineDayData()
        third_day20.id_timeline_data_type = 3
        third_day20.value = 0.3
        third_day20.id_timeline_data = 3
        db.session.add(third_day20)

        db.session.commit()
