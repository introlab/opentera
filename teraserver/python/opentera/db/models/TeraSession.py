from opentera.db.Base import db, BaseModel

from enum import Enum
import random
from datetime import datetime, timedelta
import uuid


class TeraSessionStatus(Enum):
    STATUS_NOTSTARTED = 0
    STATUS_INPROGRESS = 1
    STATUS_COMPLETED = 2
    STATUS_CANCELLED = 3
    STATUS_TERMINATED = 4


class TeraSession(db.Model, BaseModel):
    __tablename__ = 't_sessions'
    id_session = db.Column(db.Integer, db.Sequence('id_session_sequence'), primary_key=True, autoincrement=True)
    session_uuid = db.Column(db.String(36), nullable=False, unique=True)

    id_session_type = db.Column(db.Integer, db.ForeignKey('t_sessions_types.id_session_type'), nullable=False)
    id_creator_user = db.Column(db.Integer, db.ForeignKey('t_users.id_user'), nullable=True)
    id_creator_device = db.Column(db.Integer, db.ForeignKey('t_devices.id_device'), nullable=True)
    id_creator_participant = db.Column(db.Integer, db.ForeignKey('t_participants.id_participant'), nullable=True)
    id_creator_service = db.Column(db.Integer, db.ForeignKey('t_services.id_service', ondelete='set null'),
                                   nullable=True)

    session_name = db.Column(db.String, nullable=False)
    session_start_datetime = db.Column(db.TIMESTAMP(timezone=True), nullable=False)
    session_duration = db.Column(db.Integer, nullable=False, default=0)
    session_status = db.Column(db.Integer, nullable=False)
    session_comments = db.Column(db.String, nullable=True)
    session_parameters = db.Column(db.String, nullable=True)

    session_participants = db.relationship("TeraParticipant", secondary="t_sessions_participants",
                                           back_populates="participant_sessions")
    session_users = db.relationship("TeraUser", secondary="t_sessions_users", back_populates="user_sessions")
    session_devices = db.relationship("TeraDevice", secondary="t_sessions_devices",
                                      back_populates="device_sessions")

    session_creator_user = db.relationship('TeraUser')
    session_creator_device = db.relationship('TeraDevice')
    session_creator_participant = db.relationship('TeraParticipant')
    session_creator_service = db.relationship('TeraService')

    session_session_type = db.relationship('TeraSessionType')
    session_events = db.relationship('TeraSessionEvent', cascade="delete")
    session_assets = db.relationship('TeraAsset', cascade='delete')

    def to_json(self, ignore_fields=None, minimal=False):
        if ignore_fields is None:
            ignore_fields = []

        ignore_fields.extend(['session_participants', 'session_creator_user', 'session_creator_device',
                              'session_creator_participant', 'session_creator_service', 'session_session_type',
                              'session_events', 'session_users', 'session_devices', 'session_assets'])
        if minimal:
            ignore_fields.extend(['session_comments', 'session_duration', 'session_start_datetime',
                                  'session_parameters'])

        rval = super().to_json(ignore_fields=ignore_fields)

        if not minimal:
            # Append list of participants ids and names
            rval['session_participants'] = [{'id_participant': part.id_participant,
                                             'participant_uuid': part.participant_uuid,
                                             'participant_name': part.participant_name,
                                             'id_project': part.id_project}
                                            for part in self.session_participants]

            # Append list of users ids and names
            rval['session_users'] = [{'id_user': user.id_user,
                                      'user_uuid': user.user_uuid,
                                      'user_name': user.get_fullname()}
                                     for user in self.session_users]

            # Append list of devices ids and names
            rval['session_devices'] = [{'id_device': device.id_device,
                                        'device_uuid': device.device_uuid,
                                        'device_name': device.device_name}
                                       for device in self.session_devices]

            # Append user name
            if self.session_creator_user:
                rval['session_creator_user'] = self.session_creator_user.get_fullname()
                rval['session_creator_user_uuid'] = self.session_creator_user.user_uuid
            elif self.session_creator_device:
                rval['session_creator_device'] = self.session_creator_device.device_name
                rval['session_creator_device_uuid'] = self.session_creator_device.device_uuid
            elif self.session_creator_participant:
                rval['session_creator_participant'] = self.session_creator_participant.participant_name
                rval['session_creator_participant_uuid'] = self.session_creator_participant.participant_uuid
            elif self.session_creator_service:
                rval['session_creator_service'] = self.session_creator_service.service_name
                rval['session_creator_service_uuid'] = self.session_creator_service.service_uuid

            # Append session components
            # from opentera.db.models.TeraDeviceData import TeraDeviceData
            # rval['session_has_device_data'] = len(TeraDeviceData.get_data_for_session(self.id_session)) > 0
        return rval

    def to_json_create_event(self):
        return self.to_json(minimal=True)

    def to_json_update_event(self):
        return self.to_json(minimal=True)

    def to_json_delete_event(self):
        # Minimal information, delete can not be filtered
        return {'id_session': self.id_session, 'session_uuid': self.session_uuid}

    @staticmethod
    def create_defaults(test=False):
        if test:
            from opentera.db.models.TeraUser import TeraUser
            from opentera.db.models.TeraDevice import TeraDevice
            from opentera.db.models.TeraSessionType import TeraSessionType
            from opentera.db.models.TeraParticipant import TeraParticipant
            from opentera.db.models.TeraService import TeraService

            session_user = TeraUser.get_user_by_id(1)
            session_user2 = TeraUser.get_user_by_id(2)
            session_part = TeraParticipant.get_participant_by_name('Participant #1')
            session_part2 = TeraParticipant.get_participant_by_name('Participant #2')
            session_service = TeraService.get_service_by_key('VideoRehabService')
            session_device = TeraDevice.get_device_by_id(2)

            # Create user sessions
            for i in range(8):
                base_session = TeraSession()
                base_session.session_creator_user = session_user
                ses_type = random.randint(1, 4)
                base_session.session_session_type = TeraSessionType.get_session_type_by_id(ses_type)
                base_session.session_name = "Séance #" + str(i + 1)
                base_session.session_start_datetime = datetime.now() - timedelta(days=random.randint(0, 30))
                base_session.session_duration = random.randint(60, 4800)
                ses_status = random.randint(0, 4)
                base_session.session_status = ses_status
                if i < 7:
                    base_session.session_participants = [session_part]
                else:
                    base_session.session_participants = [session_part, session_part2]
                if i < 4:
                    base_session.session_users = [base_session.session_creator_user]
                else:
                    base_session.session_users = [base_session.session_creator_user, session_user2]
                if i == 3:
                    base_session.session_devices = [session_device]
                base_session.session_uuid = str(uuid.uuid4())
                db.session.add(base_session)

            # Create device sessions
            for i in range(8):
                base_session = TeraSession()
                base_session.session_creator_device = TeraDevice.get_device_by_id(1)
                ses_type = random.randint(1, 4)
                base_session.session_session_type = TeraSessionType.get_session_type_by_id(ses_type)
                base_session.session_name = "Séance #" + str(i + 1)
                base_session.session_start_datetime = datetime.now() - timedelta(days=random.randint(0, 30))
                base_session.session_duration = random.randint(60, 4800)
                ses_status = random.randint(0, 4)
                base_session.session_status = ses_status
                if i < 7:
                    base_session.session_participants = [session_part]
                else:
                    base_session.session_participants = [session_part, session_part2]
                base_session.session_uuid = str(uuid.uuid4())
                db.session.add(base_session)

            # Create participant sessions
            for i in range(8):
                base_session = TeraSession()
                base_session.session_creator_participant = TeraParticipant.get_participant_by_id(1)
                ses_type = random.randint(1, 4)
                base_session.session_session_type = TeraSessionType.get_session_type_by_id(ses_type)
                base_session.session_name = "Séance #" + str(i + 1)
                base_session.session_start_datetime = datetime.now() - timedelta(days=random.randint(0, 30))
                base_session.session_duration = random.randint(60, 4800)
                ses_status = random.randint(0, 4)
                base_session.session_status = ses_status
                base_session.session_participants = [base_session.session_creator_participant]
                base_session.session_uuid = str(uuid.uuid4())
                db.session.add(base_session)

            # Create service sessions
            for i in range(4):
                base_session = TeraSession()
                base_session.session_creator_service = session_service
                ses_type = random.randint(1, 4)
                base_session.session_session_type = TeraSessionType.get_session_type_by_id(ses_type)
                base_session.session_name = "Séance #" + str(i + 1)
                base_session.session_start_datetime = datetime.now() - timedelta(days=random.randint(0, 30))
                base_session.session_duration = random.randint(60, 4800)
                ses_status = random.randint(0, 4)
                base_session.session_status = ses_status
                if i < 3:
                    base_session.session_participants = [session_part]
                else:
                    base_session.session_participants = [session_part, session_part2]
                base_session.session_uuid = str(uuid.uuid4())
                db.session.add(base_session)

            db.session.commit()

    @staticmethod
    def get_session_by_id(ses_id: int):
        return TeraSession.query.filter_by(id_session=ses_id).first()

    @staticmethod
    def get_session_by_uuid(s_uuid):
        session = TeraSession.query.filter_by(session_uuid=s_uuid).first()
        if session:
            return session

        return None

    @staticmethod
    def get_session_by_name(name: str):
        return TeraSession.query.filter_by(session_name=name).first()

    @staticmethod
    def get_sessions_for_participant(part_id: int):
        from opentera.db.models.TeraParticipant import TeraParticipant
        return TeraSession.query.join(TeraSession.session_participants).filter(TeraParticipant.id_participant ==
                                                                               part_id) \
            .order_by(TeraSession.session_start_datetime.desc()).all()

    @staticmethod
    def get_sessions_for_user(user_id: int):
        from opentera.db.models.TeraUser import TeraUser
        return TeraSession.query.join(TeraSession.session_users).filter(TeraUser.id_user == user_id) \
            .order_by(TeraSession.session_start_datetime.desc()).all()

    @staticmethod
    def get_sessions_for_device(device_id: int):
        from opentera.db.models.TeraDevice import TeraDevice
        return TeraSession.query.join(TeraSession.session_devices).filter(TeraDevice.id_device == device_id) \
            .order_by(TeraSession.session_start_datetime.desc()).all()

    @staticmethod
    def get_sessions_for_type(session_type_id: int):
        return TeraSession.query.filter_by(id_session_type=session_type_id).all()

    @staticmethod
    def is_user_in_session(session_uuid: str, user_uuid: str) -> bool:
        session = TeraSession.get_session_by_uuid(session_uuid)
        user_uuids = [user.user_uuid for user in session.session_users]
        return user_uuid in user_uuids

    @staticmethod
    def is_device_in_session(session_uuid: str, device_uuid: str) -> bool:
        session = TeraSession.get_session_by_uuid(session_uuid)
        device_uuids = [device.device_uuid for device in session.session_devices]
        return device_uuid in device_uuids

    @staticmethod
    def is_participant_in_session(session_uuid: str, participant_uuid: str) -> bool:
        session = TeraSession.get_session_by_uuid(session_uuid)
        participant_uuids = [participant.participant_uuid for participant in session.session_participants]
        return participant_uuid in participant_uuids

    def has_user(self, id_user: int) -> bool:
        user_ids = [user.id_user for user in self.session_users]
        return id_user in user_ids

    def has_device(self, id_device: int) -> bool:
        device_ids = [device.id_device for device in self.session_devices]
        return id_device in device_ids

    def has_participant(self, id_participant: int) -> bool:
        participant_ids = [participant.id_participant for participant in self.session_participants]
        return id_participant in participant_ids

    def get_associated_project_id(self):
        project_id = None
        if self.session_participants:
            # Return project id for the first participant, since they should all be the same...
            project_id = self.session_participants[0].id_project

        return project_id

    # THIS SHOULD NOT BE USED ANYMORE, AS DELETES CAN'T OCCUR IF THERE'S STILL ASSOCIATED SESSIONS
    # @staticmethod
    # def delete_orphaned_sessions(commit_changes=True):
    #     from opentera.db.models.TeraDeviceData import TeraDeviceData
    #     orphans_parts = TeraSession.query.outerjoin(TeraSession.session_participants).filter(
    #         TeraSession.session_participants == None).all()
    #
    #     orphans_users = TeraSession.query.outerjoin(TeraSession.session_users).filter(
    #         TeraSession.session_users == None).all()
    #
    #     orphans = list(set(orphans_parts + orphans_users))  # Keep unique sessions only!
    #
    #     if orphans:
    #         for orphan in orphans:
    #             TeraDeviceData.delete_files_for_session(orphan.id_session)
    #             db.session.delete(orphan)
    #             # TeraSession.delete(orphan.id_session)
    #
    #     if commit_changes:
    #         db.session.commit()

    @classmethod
    def delete(cls, id_todel):
        # from opentera.db.models.TeraDeviceData import TeraDeviceData
        # TeraDeviceData.delete_files_for_session(id_todel)
        super().delete(id_todel)

    @classmethod
    def insert(cls, session):
        session.session_uuid = str(uuid.uuid4())
        super().insert(session)
