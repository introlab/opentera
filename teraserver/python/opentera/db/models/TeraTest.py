from opentera.db.Base import db, BaseModel
from enum import Enum


class TeraSessionStatus(Enum):
    TEST_INCOMPLETE = 0
    TEST_INPROGRESS = 1
    TEST_COMPLETED = 2


class TeraTest(db.Model, BaseModel):
    __tablename__ = 't_tests'
    id_test = db.Column(db.Integer, db.Sequence('id_test_sequence'), primary_key=True, autoincrement=True)
    id_test_type = db.Column(db.Integer, db.ForeignKey('t_tests_types.id_test_type', ondelete='cascade'),
                             nullable=False)
    id_session = db.Column(db.Integer, db.ForeignKey('t_sessions.id_session', ondelete='cascade'), nullable=False)
    test_name = db.Column(db.String, nullable=False)
    test_datetime = db.Column(db.TIMESTAMP(timezone=True), nullable=False)
    test_status = db.Column(db.Integer, nullable=False)
    test_answers = db.Column(db.String, nullable=True)

    test_session = db.relationship('TeraSession')
    test_test_type = db.relationship('TeraTestType')

