from libtera.db.Base import db, BaseModel

from enum import Enum
import random
from datetime import datetime, timedelta

from sqlalchemy import event


class TeraSessionStatus(Enum):
    STATUS_NOTSTARTED = 0
    STATUS_INPROGRESS = 1
    STATUS_COMPLETED = 2
    STATUS_CANCELLED = 3
    STATUS_TERMINATED = 4


class TeraSession(db.Model, BaseModel):
    __tablename__ = 't_sessions'
    id_session = db.Column(db.Integer, db.Sequence('id_session_sequence'), primary_key=True, autoincrement=True)
    id_session_type = db.Column(db.Integer, db.ForeignKey('t_sessions_types.id_session_type', ondelete='cascade'),
                                nullable=False)
    # TODO Update forms / c++ client, queries
    id_creator_user = db.Column(db.Integer, db.ForeignKey('t_users.id_user', ondelete='set null'), nullable=True)
    id_creator_device = db.Column(db.Integer, db.ForeignKey('t_devices.id_device', ondelete='set null'), nullable=True)
    id_creator_participant = db.Column(db.Integer, db.ForeignKey('t_participants.id_participant', ondelete='set null'),
                                       nullable=True)
    session_name = db.Column(db.String, nullable=False)
    session_start_datetime = db.Column(db.TIMESTAMP, nullable=False)
    session_duration = db.Column(db.Integer, nullable=False, default=0)
    session_status = db.Column(db.Integer, nullable=False)
    session_comments = db.Column(db.String, nullable=True)
    session_participants = db.relationship("TeraParticipant", secondary="t_sessions_participants",
                                           back_populates="participant_sessions", cascade="delete")

    session_creator_user = db.relationship('TeraUser')
    session_creator_device = db.relationship('TeraDevice')
    session_creator_participant = db.relationship('TeraParticipant')

    session_session_type = db.relationship('TeraSessionType')
    session_events = db.relationship('TeraSessionEvent', cascade="delete")

    def to_json(self, ignore_fields=[], minimal=False):
        ignore_fields.extend(['session_participants', 'session_creator_user', 'session_creator_device',
                              'session_creator_participant', 'session_session_type', 'session_events'])
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
            if self.session_creator_user:
                rval["session_creator_user"] = self.session_creator_user.get_fullname()
            elif self.session_creator_device:
                rval["session_creator_device"] = self.session_creator_device.device_name
            elif self.session_creator_participant:
                rval["session_creator_participant"] = self.session_creator_participant.participant_name

            # Append session type infos
            # rval["session_session_type"] = self.session_session_type.to_json(ignore_fields=['id_session_type',
            #                                                                                'session_type_profile'])

            # Append session components
            from libtera.db.models.TeraDeviceData import TeraDeviceData
            rval['session_has_device_data'] = len(TeraDeviceData.get_data_for_session(self.id_session)) > 0
        return rval

    @staticmethod
    def create_defaults():
        from libtera.db.models.TeraUser import TeraUser
        from libtera.db.models.TeraSessionType import TeraSessionType
        from libtera.db.models.TeraParticipant import TeraParticipant

        session_user = TeraUser.get_user_by_id(1)
        session_part = TeraParticipant.get_participant_by_name('Participant #1')
        session_part2 = TeraParticipant.get_participant_by_name('Participant #2')
        for i in range(8):
            base_session = TeraSession()
            base_session.session_creator_user = session_user
            ses_type = random.randint(1, 4)
            base_session.session_session_type = TeraSessionType.get_session_type_by_id(ses_type)
            base_session.session_name = "Séance #" + str(i+1)
            base_session.session_start_datetime = datetime.now() - timedelta(days=random.randint(0, 30))
            base_session.session_duration = random.randint(60, 4800)
            ses_status = random.randint(0, 4)
            base_session.session_status = ses_status
            if i < 7:
                base_session.session_participants = [session_part]
            else:
                base_session.session_participants = [session_part, session_part2]
            db.session.add(base_session)

        db.session.commit()

    @staticmethod
    def get_session_by_id(ses_id: int):
        return TeraSession.query.filter_by(id_session=ses_id).first()

    @staticmethod
    def get_session_by_name(name: str):
        return TeraSession.query.filter_by(session_name=name).first()

    @staticmethod
    def get_sessions_for_participant(part_id: int):
        from libtera.db.models.TeraParticipant import TeraParticipant
        return TeraSession.query.join(TeraSession.session_participants).filter(TeraParticipant.id_participant ==
                                                                               part_id)\
            .order_by(TeraSession.session_start_datetime.desc()).all()

    @staticmethod
    def get_sessions_for_type(session_type_id: int):
        return TeraSession.query.filter_by(id_session_type=session_type_id).all()

    @staticmethod
    def delete_orphaned_sessions(commit_changes=True):
        from libtera.db.models.TeraDeviceData import TeraDeviceData
        orphans = TeraSession.query.outerjoin(TeraSession.session_participants).filter(
            TeraSession.session_participants == None).all()

        if orphans:
            for orphan in orphans:
                TeraDeviceData.delete_files_for_session(orphan.id_session)
                db.session.delete(orphan)
                # TeraSession.delete(orphan.id_session)

        if commit_changes:
            db.session.commit()

    @classmethod
    def delete(cls, id_todel):
        from libtera.db.models.TeraDeviceData import TeraDeviceData
        TeraDeviceData.delete_files_for_session(id_todel)

        super().delete(id_todel)
