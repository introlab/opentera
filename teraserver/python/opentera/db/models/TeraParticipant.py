from opentera.db.Base import BaseModel
from opentera.db.SoftDeleteMixin import SoftDeleteMixin
from sqlalchemy import Column, ForeignKey, Integer, String, Sequence, Boolean, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.exc import IntegrityError
from opentera.db.models.TeraParticipantGroup import TeraParticipantGroup
from opentera.db.models.TeraServerSettings import TeraServerSettings
from opentera.db.models.TeraSessionParticipants import TeraSessionParticipants
from opentera.db.models.TeraSession import TeraSession
from opentera.db.models.TeraAsset import TeraAsset
from opentera.db.models.TeraTest import TeraTest
from opentera.db.models.TeraProject import TeraProject

import uuid
import jwt
import datetime
from passlib.hash import bcrypt


# Generator for jti
def infinite_jti_sequence():
    num = 0
    while True:
        yield num
        num += 1


# Initialize generator, call next(participant_jti_generator) to get next sequence number
participant_jti_generator = infinite_jti_sequence()


class TeraParticipant(BaseModel, SoftDeleteMixin):
    __tablename__ = 't_participants'
    id_participant = Column(Integer, Sequence('id_participant_sequence'), primary_key=True, autoincrement=True)
    participant_uuid = Column(String(36), nullable=False, unique=True)
    participant_name = Column(String, nullable=False)
    participant_username = Column(String(50), nullable=True)
    participant_email = Column(String, nullable=True)
    participant_password = Column(String, nullable=True)
    participant_token_enabled = Column(Boolean, nullable=False, default=False)
    participant_token = Column(String, nullable=True, unique=True)
    participant_lastonline = Column(TIMESTAMP(timezone=True), nullable=True)
    participant_enabled = Column(Boolean, nullable=False, default=True)
    participant_login_enabled = Column(Boolean, nullable=False, default=False)
    id_participant_group = Column(Integer, ForeignKey('t_participants_groups.id_participant_group', ondelete='cascade'),
                                  nullable=True)

    id_project = Column(Integer, ForeignKey('t_projects.id_project', ondelete='cascade'), nullable=False)

    participant_devices = relationship("TeraDevice", secondary="t_devices_participants",
                                       back_populates="device_participants", viewonly=True)

    participant_sessions = relationship("TeraSession", secondary="t_sessions_participants",
                                        back_populates="session_participants", passive_deletes=True)

    participant_participant_group = relationship("TeraParticipantGroup",
                                                 back_populates='participant_group_participants')

    participant_project = relationship("TeraProject", back_populates='project_participants', lazy='selectin')

    participant_created_sessions = relationship("TeraSession", cascade='delete',
                                                back_populates='session_creator_participant', passive_deletes=True)

    participant_service_config = relationship("TeraServiceConfig", cascade='delete', passive_deletes=True)

    participant_assets = relationship("TeraAsset", cascade='delete', back_populates='asset_participant',
                                      passive_deletes=True)

    participant_tests = relationship("TeraTest", cascade='delete',
                                     back_populates='test_participant', passive_deletes=True)

    authenticated = False
    fullAccess = False

    def __init__(self):
        pass

    def __str__(self):
        return '<TeraParticipant ' + str(self.participant_name) + ' >'

    def __repr__(self):
        return self.__str__()

    def dynamic_token(self, token_key: str, expiration=3600):
        import time
        import jwt

        # Creating token with participant info
        now = time.time()
        payload = {
            'iat': int(now),
            'exp': int(now) + expiration,
            'iss': 'TeraServer',
            'jti': next(participant_jti_generator),
            'participant_uuid': self.participant_uuid,
            'id_participant': self.id_participant,
            'user_fullname': self.participant_name
        }

        return jwt.encode(payload, token_key, algorithm='HS256')

    def create_token(self):
        # Creating token with user info
        payload = {
            'iss': 'TeraServer',
            'jti': next(participant_jti_generator),
            'participant_uuid': self.participant_uuid,
            'id_participant': self.id_participant
        }

        self.participant_token = jwt.encode(payload, TeraServerSettings.get_server_setting_value(
            TeraServerSettings.ServerParticipantTokenKey), algorithm='HS256')

        return self.participant_token

    def update_last_online(self):
        self.participant_lastonline = datetime.datetime.now()
        TeraParticipant.db().session.commit()

    def to_json(self, ignore_fields=None, minimal=False):
        if ignore_fields is None:
            ignore_fields = []

        ignore_fields.extend(['authenticated', 'participant_devices',
                              'participant_sessions', 'participant_password',
                              'participant_project', 'participant_participant_group', 'fullAccess',
                              'participant_created_sessions', 'participant_service_config'
                              ])
        if minimal:
            ignore_fields.extend(['participant_username', 'participant_lastonline',
                                  'participant_login_enabled', 'participant_token'])

        participant_json = super().to_json(ignore_fields=ignore_fields)
        if self.participant_project and not minimal:
            participant_json['participant_project_enabled'] = self.participant_project.project_enabled
        return participant_json

    def to_json_create_event(self):
        return self.to_json(minimal=True)

    def to_json_update_event(self):
        return self.to_json(minimal=True)

    def to_json_delete_event(self):
        # Minimal information, delete can not be filtered
        return {'id_participant': self.id_participant, 'participant_uuid': self.participant_uuid}

    def is_authenticated(self):
        return self.authenticated

    def is_anonymous(self):
        return False

    def is_active(self):
        return self.participant_enabled

    def is_login_enabled(self):
        return self.participant_login_enabled

    def get_id(self):
        return self.participant_uuid

    def get_first_session(self):
        sessions = sorted(self.participant_sessions, key=lambda session: session.session_start_datetime)
        if sessions:
            return sessions[0]
        return None

    def get_last_session(self):
        from opentera.db.models.TeraSession import TeraSessionStatus
        sessions = [session for session in self.participant_sessions
                    if session.session_status == TeraSessionStatus.STATUS_COMPLETED.value or
                    session.session_status == TeraSessionStatus.STATUS_TERMINATED.value]
        sessions = sorted(sessions, key=lambda session: session.session_start_datetime)
        if sessions:
            return sessions[-1]
        return None

    @staticmethod
    def encrypt_password(password):
        return bcrypt.hash(password)

    # @staticmethod
    # def is_anonymous():
    #     return False

    @staticmethod
    def verify_password(username, password, participant=None):
        # Query User with that username
        if participant is None:
            participant = TeraParticipant.get_participant_by_username(username)

        if participant is None:
            print('TeraParticipant: verify_password - participant ' + username + ' not found.')
            return None

        # Check if enabled
        if not participant.participant_enabled or not participant.participant_login_enabled:
            print('TeraUser: verify_password - user ' + username + ' is inactive or login is disabled.')
            return None

        # Check password
        if bcrypt.verify(password, participant.participant_password):
            participant.authenticated = True
            return participant

        return None

    @staticmethod
    def get_participant_by_token(token, with_deleted: bool = False):
        participant = TeraParticipant.query.execution_options(include_deleted=with_deleted)\
            .filter_by(participant_token=token).first()

        if participant and participant.participant_enabled and participant.participant_token_enabled:
            # Validate token
            data = jwt.decode(token.encode('utf-8'), TeraServerSettings.get_server_setting_value(
                TeraServerSettings.ServerParticipantTokenKey), algorithms='HS256')

            if data['participant_uuid'] == participant.participant_uuid:
                participant.authenticated = True
                return participant
            else:
                return None

        return None

    @staticmethod
    def get_participant_by_uuid(p_uuid, with_deleted: bool = False):
        participant = TeraParticipant.query.execution_options(include_deleted=with_deleted)\
            .filter_by(participant_uuid=p_uuid).first()

        if participant:
            return participant

        return None

    @staticmethod
    def get_participant_by_username(username, with_deleted: bool = False):
        return TeraParticipant.query.execution_options(include_deleted=with_deleted)\
            .filter_by(participant_username=username).first()

    @staticmethod
    def get_participant_by_email(email: str, with_deleted: bool = False):
        return TeraParticipant.query.execution_options(include_deleted=with_deleted)\
            .filter_by(participant_email=email).first()

    @staticmethod
    def get_participant_by_name(name, with_deleted: bool = False):
        return TeraParticipant.query.execution_options(include_deleted=with_deleted)\
            .filter_by(participant_name=name).first()

    @staticmethod
    def get_participant_by_id(part_id: int, with_deleted: bool = False):
        return TeraParticipant.query.execution_options(include_deleted=with_deleted)\
            .filter_by(id_participant=part_id).first()

    @staticmethod
    def is_participant_username_available(username: str) -> bool:
        # No username = always available
        if username is None or username == '':
            return True

        return TeraParticipant.query.filter_by(participant_username=username).first() is None

    @staticmethod
    def create_defaults(test=False):
        if test:
            from opentera.db.models.TeraProject import TeraProject
            project1 = TeraProject.get_project_by_projectname('Default Project #1')
            project2 = TeraProject.get_project_by_projectname('Secret Project #1')

            participant1 = TeraParticipant()
            participant1.participant_name = 'Participant #1'
            participant1.participant_enabled = True
            participant1.participant_uuid = str(uuid.uuid4())
            participant1.participant_participant_group = \
                TeraParticipantGroup.get_participant_group_by_group_name('Default Participant Group A')
            participant1.participant_project = project1

            # participant1.create_token()
            participant1.participant_username = 'participant1'
            participant1.participant_password = TeraParticipant.encrypt_password('opentera')
            participant1.participant_login_enabled = True
            participant1.participant_token_enabled = True

            TeraParticipant.db().session.add(participant1)

            participant2 = TeraParticipant()
            participant2.participant_name = 'Participant #2'
            participant2.participant_enabled = False
            participant2.participant_uuid = str(uuid.uuid4())
            participant2.participant_participant_group = None
            participant2.participant_project = project1

            TeraParticipant.db().session.add(participant2)

            participant2 = TeraParticipant()
            participant2.participant_name = 'Participant #3'
            participant2.participant_enabled = True
            participant2.participant_token_enabled = True
            participant2.participant_uuid = str(uuid.uuid4())
            participant2.participant_participant_group = None
            participant2.participant_project = project1

            # participant2.create_token()
            TeraParticipant.db().session.add(participant2)

            participant2 = TeraParticipant()
            participant2.participant_name = 'Secret Participant'
            participant2.participant_enabled = True
            participant2.participant_token_enabled = True
            participant2.participant_uuid = str(uuid.uuid4())
            participant2.participant_participant_group = None
            participant2.participant_project = project2

            # participant2.create_token()
            TeraParticipant.db().session.add(participant2)

            TeraParticipant.db().session.commit()

            # Create token with added participants, since we need to have the id_participant field set
            participant1.create_token()
            participant2.create_token()
            TeraParticipant.db().session.commit()

    @classmethod
    def update(cls, update_id: int, values: dict):
        update_participant = TeraParticipant.get_participant_by_id(update_id)
        # Check if participant is an enabled project
        if 'participant_enabled' in values and values['participant_enabled'] and \
                not update_participant.participant_project.project_enabled:
            raise IntegrityError('Participant project disabled - no update allowed', update_id, 't_projects')

        # Check if username is available
        if 'participant_username' in values:
            if not TeraParticipant.is_participant_username_available(values['participant_username']):
                raise NameError('Participant username already in use.')

        # Prevent changes on UUID
        if 'participant_uuid' in values:
            del values['participant_uuid']

        # Remove the password field is present and if empty
        if 'participant_password' in values:
            if values['participant_password'] == '':
                del values['participant_password']
            else:
                # Forcing password to string
                values['participant_password'] = TeraParticipant.encrypt_password(str(values['participant_password']))

        # Check if we need to generate or delete tokens
        if 'participant_token_enabled' in values:
            if values['participant_token_enabled'] != update_participant.participant_token_enabled:
                if 'participant_enabled' in values:
                    participant_enabled = values['participant_enabled']
                else:
                    participant_enabled = update_participant.participant_enabled
                # Value changed
                if not values['participant_token_enabled'] or not participant_enabled:
                    values['participant_token'] = None  # Remove token
                else:
                    values['participant_token'] = update_participant.create_token()  # Generate new token
                    TeraParticipant.db().session.rollback()  # Don't save token here

        super().update(update_id, values)

    @classmethod
    def insert(cls, participant):
        # Encrypts password
        if participant.participant_password:
            # Forcing password to string
            participant.participant_password = TeraParticipant.encrypt_password(str(participant.participant_password))

        participant.participant_lastonline = None
        participant.participant_uuid = str(uuid.uuid4())
        participant.participant_token = None
        # participant.create_token()
        # Check if username is available
        if not TeraParticipant.is_participant_username_available(participant.participant_username):
            raise NameError('Participant username already in use.')
        super().insert(participant)

        # Token must be created after being inserted, since we need to have a valid ID participant into it
        if participant.participant_token_enabled and participant.participant_enabled:
            participant.create_token()

        # Check if participant project is enabled
        project = TeraProject.get_project_by_id(participant.id_project)
        if not project or not project.project_enabled:
            raise IntegrityError('Participant project disabled - no insert allowed', -1, 't_projects')
        TeraParticipant.db().session.commit()

    def delete_check_integrity(self) -> IntegrityError | None:
        # Safety check - can't delete participants with sessions
        if TeraSessionParticipants.get_session_count_for_participant(self.id_participant) > 0:
            return IntegrityError('Participant still has sessions', self.id_participant, 't_sessions_participants')

        if TeraSession.get_count(filters={'id_creator_participant': self.id_participant}) > 0:
            return IntegrityError('Participant still has created sessions', self.id_participant, 't_sessions')

        if TeraAsset.get_count(filters={'id_participant': self.id_participant}) > 0:
            return IntegrityError('Participant still has created assets', self.id_participant, 't_assets')

        if TeraTest.get_count(filters={'id_participant': self.id_participant}) > 0:
            return IntegrityError('Participant still has created tests', self.id_participant, 't_tests')

        return None
