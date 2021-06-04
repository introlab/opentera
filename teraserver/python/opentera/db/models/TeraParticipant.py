from opentera.db.Base import db, BaseModel
from opentera.db.models.TeraParticipantGroup import TeraParticipantGroup
from opentera.db.models.TeraServerSettings import TeraServerSettings

import uuid
import jwt
import time
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


class TeraParticipant(db.Model, BaseModel):
    __tablename__ = 't_participants'
    id_participant = db.Column(db.Integer, db.Sequence('id_participant_sequence'), primary_key=True, autoincrement=True)
    participant_uuid = db.Column(db.String(36), nullable=False, unique=True)
    participant_name = db.Column(db.String, nullable=False)
    participant_username = db.Column(db.String(50), nullable=True)
    participant_email = db.Column(db.String, nullable=True)
    participant_password = db.Column(db.String, nullable=True)
    participant_token_enabled = db.Column(db.Boolean, nullable=False, default=False)
    participant_token = db.Column(db.String, nullable=True, unique=True)
    participant_lastonline = db.Column(db.TIMESTAMP(timezone=True), nullable=True)
    participant_enabled = db.Column(db.Boolean, nullable=False, default=True)
    participant_login_enabled = db.Column(db.Boolean, nullable=False, default=False)
    id_participant_group = db.Column(db.Integer, db.ForeignKey('t_participants_groups.id_participant_group',
                                                               ondelete='cascade'), nullable=True)

    id_project = db.Column(db.Integer, db.ForeignKey('t_projects.id_project', ondelete='cascade'), nullable=False)

    participant_devices = db.relationship("TeraDevice", secondary="t_devices_participants",
                                          back_populates="device_participants")

    participant_sessions = db.relationship("TeraSession", secondary="t_sessions_participants",
                                           back_populates="session_participants", passive_deletes=True)

    participant_participant_group = db.relationship("TeraParticipantGroup")

    participant_project = db.relationship("TeraProject")

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
        import random
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
        db.session.commit()

    def to_json(self, ignore_fields=None, minimal=False):
        if ignore_fields is None:
            ignore_fields = []

        ignore_fields.extend(['authenticated', 'participant_devices',
                              'participant_sessions', 'participant_password',
                              'participant_project', 'participant_participant_group', 'fullAccess'
                              ])
        if minimal:
            ignore_fields.extend(['participant_username', 'participant_lastonline',
                                  'participant_login_enabled', 'participant_token'])

        return super().to_json(ignore_fields=ignore_fields)

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
        sessions = sorted(self.participant_sessions, key=lambda session: session.session_start_datetime)
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
    def get_participant_by_token(token):
        participant = TeraParticipant.query.filter_by(participant_token=token).first()

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
    def get_participant_by_uuid(p_uuid):
        participant = TeraParticipant.query.filter_by(participant_uuid=p_uuid).first()

        if participant:
            return participant

        return None

    @staticmethod
    def get_participant_by_username(username):
        return TeraParticipant.query.filter_by(participant_username=username).first()

    @staticmethod
    def get_participant_by_email(email: str):
        return TeraParticipant.query.filter_by(participant_email=email).first()

    @staticmethod
    def get_participant_by_name(name):
        return TeraParticipant.query.filter_by(participant_name=name).first()

    @staticmethod
    def get_participant_by_id(part_id: int):
        return TeraParticipant.query.filter_by(id_participant=part_id).first()

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

            db.session.add(participant1)

            participant2 = TeraParticipant()
            participant2.participant_name = 'Participant #2'
            participant2.participant_enabled = False
            participant2.participant_uuid = str(uuid.uuid4())
            participant2.participant_participant_group = None
            participant2.participant_project = project1

            db.session.add(participant2)

            participant2 = TeraParticipant()
            participant2.participant_name = 'Participant #3'
            participant2.participant_enabled = True
            participant2.participant_token_enabled = True
            participant2.participant_uuid = str(uuid.uuid4())
            participant2.participant_participant_group = None
            participant2.participant_project = project1

            # participant2.create_token()
            db.session.add(participant2)

            db.session.commit()

            # Create token with added participants, since we need to have the id_participant field set
            participant1.create_token()
            participant2.create_token()
            db.session.commit()

    @classmethod
    def update(cls, update_id: int, values: dict):
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
            update_participant = TeraParticipant.get_participant_by_id(update_id)
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
                    db.session.rollback()  # Don't save token here

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
        db.session.commit()

    @classmethod
    def delete(cls, id_todel: int):
        super().delete(id_todel)
        # Check if we need to delete orphan sessions (sessions that have no more participants left
        # from opentera.db.models.TeraSession import TeraSession
        # TeraSession.delete_orphaned_sessions(False)
        #
        # db.session.commit()
