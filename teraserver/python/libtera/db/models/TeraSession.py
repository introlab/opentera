from libtera.db.Base import db, BaseModel

from enum import Enum
import random
from datetime import datetime, timedelta

sessions_participants_table = db.Table('t_sessions_participants', db.Column('id_session', db.Integer,
                                                                            db.ForeignKey('t_sessions.id_session',
                                                                                          ondelete='cascade')),
                                       db.Column('id_participant', db.Integer,
                                                 db.ForeignKey('t_participants.id_participant', ondelete='cascade')))


class TeraSessionStatus(Enum):
    STATUS_NOTSTARTED = 0
    STATUS_INPROGRESS = 1
    STATUS_COMPLETED = 2
    STATUS_CANCELLED = 3
    STATUS_TERMINATED = 4


class TeraSession(db.Model, BaseModel):
    __tablename__ = 't_sessions'
    id_session = db.Column(db.Integer, db.Sequence('id_session_sequence'), primary_key=True, autoincrement=True)
    id_session_type = db.Column(db.Integer, db.ForeignKey('t_sessions_types.id_session_type'), nullable=False)
    id_user = db.Column(db.Integer, db.ForeignKey('t_users.id_user'), nullable=False)
    session_name = db.Column(db.String, nullable=False)
    session_start_datetime = db.Column(db.TIMESTAMP, nullable=False)
    session_duration = db.Column(db.Integer, nullable=False, default=0)
    session_status = db.Column(db.Integer, nullable=False)
    session_comments = db.Column(db.String, nullable=True)
    session_participants = db.relationship("TeraParticipant", secondary=sessions_participants_table,
                                           back_populates="participant_sessions", cascade="all,delete")

    session_user = db.relationship('TeraUser')
    session_session_type = db.relationship('TeraSessionType')

    def to_json(self, ignore_fields=[], minimal=False):
        ignore_fields.extend(['session_participants', 'session_user',
                              'session_session_type'])
        if minimal:
            ignore_fields.extend([])

        rval = super().to_json(ignore_fields=ignore_fields)

        if not minimal:
            # Append list of participants ids
            session_part = []
            for part in self.session_participants:
                session_part.append(part.id_participant)
            rval["session_participants_ids"] = session_part

            # Append user name
            rval["session_user"] = self.session_user.get_fullname()

            # Append session type infos
            # rval["session_session_type"] = self.session_session_type.to_json(ignore_fields=['id_session_type',
            #                                                                                'session_type_profile'])
        return rval

    @staticmethod
    def create_defaults():
        from libtera.db.models.TeraUser import TeraUser
        from libtera.db.models.TeraSessionType import TeraSessionType
        from libtera.db.models.TeraParticipant import TeraParticipant

        session_user = TeraUser.get_user_by_id(1)
        session_part = TeraParticipant.get_participant_by_name('Test Participant #1')
        for i in range(8):
            base_session = TeraSession()
            base_session.session_user = session_user
            ses_type = random.randint(1, 4)
            base_session.session_session_type = TeraSessionType.get_session_type_by_id(ses_type)
            base_session.session_name = "Séance #" + str(i+1)
            base_session.session_start_datetime = datetime.now() - timedelta(days=random.randint(0, 30))
            base_session.session_duration = random.randint(60, 4800)
            ses_status = random.randint(0, 4)
            base_session.session_status = ses_status
            base_session.session_participants = [session_part]
            db.session.add(base_session)

        db.session.commit()

    @staticmethod
    def get_count():
        count = db.session.query(db.func.count(TeraSession.id_session))
        return count.first()[0]

    @staticmethod
    def get_session_by_id(ses_id: int):
        return TeraSession.query.filter_by(id_session=ses_id).first()

    @staticmethod
    def get_sessions_for_participant(part_id: int):
        from libtera.db.models.TeraParticipant import TeraParticipant
        return TeraSession.query.join(TeraSession.session_participants).filter(TeraParticipant.id_participant ==
                                                                               part_id)\
            .order_by(TeraSession.session_start_datetime.asc()).all()

    @staticmethod
    def get_sessions_for_type(session_type_id: int):
        return TeraSession.query.filter_by(id_session_type=session_type_id).all()

    @staticmethod
    def update_session(id_session: int, values={}):
        TeraSession.query.filter_by(id_session=id_session).update(values)
        db.session.commit()

    @staticmethod
    def insert_session(session):
        session.id_session = None
        db.session.add(session)
        db.session.commit()

    @staticmethod
    def delete_session(id_session: int):
        TeraSession.query.filter_by(id_session=id_session).delete()
        db.session.commit()
