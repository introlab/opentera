from opentera.db.Base import db, BaseModel
from enum import Enum
import uuid


class TeraTestStatus(Enum):
    TEST_INCOMPLETE = 0
    TEST_INPROGRESS = 1
    TEST_COMPLETED = 2


class TeraTest(db.Model, BaseModel):
    __tablename__ = 't_tests'
    id_test = db.Column(db.Integer, db.Sequence('id_test_sequence'), primary_key=True, autoincrement=True)
    id_test_type = db.Column(db.Integer, db.ForeignKey('t_tests_types.id_test_type'), nullable=False)
    id_session = db.Column(db.Integer, db.ForeignKey('t_sessions.id_session', ondelete='cascade'), nullable=False)

    # Item to which that test is associated. At least one of it should be selected, but multiple can also be specified
    # Of course, that item needs to be in the associated session for data integrity
    id_device = db.Column(db.Integer, db.ForeignKey("t_devices.id_device"), nullable=True)
    id_participant = db.Column(db.Integer, db.ForeignKey("t_participants.id_participant"), nullable=True)
    id_user = db.Column(db.Integer, db.ForeignKey("t_users.id_user"), nullable=True)
    id_service = db.Column(db.Integer, db.ForeignKey("t_services.id_service"), nullable=True)

    test_uuid = db.Column(db.String(36), nullable=False, unique=True)
    test_name = db.Column(db.String, nullable=False)
    test_datetime = db.Column(db.TIMESTAMP(timezone=True), nullable=False)
    test_status = db.Column(db.Integer, nullable=False, default=0)
    test_summary = db.Column(db.String, nullable=True)  # This contains a json formatted summary for results display

    test_session = db.relationship("TeraSession", back_populates='test_assets')
    test_device = db.relationship("TeraDevice")
    test_user = db.relationship("TeraUser")
    test_participant = db.relationship("TeraParticipant")
    test_service = db.relationship("TeraService")
    test_test_type = db.relationship('TeraTestType')

    def from_json(self, json, ignore_fields=None):
        if ignore_fields is None:
            ignore_fields = []

        ignore_fields.extend(['test_session', 'test_device', 'test_user', 'test_participant', 'test_service',
                              'test_test_type'])

        super().from_json(json, ignore_fields)

    def to_json(self, ignore_fields=None, minimal=False):
        if ignore_fields is None:
            ignore_fields = []

        ignore_fields.extend(['test_session', 'test_device', 'test_user', 'test_participant', 'test_service',
                              'test_test_type'])

        test_json = super().to_json(ignore_fields=ignore_fields)
        if not minimal:
            test_json['test_session_name'] = self.test_session.session_name
            if self.id_device:
                test_json['test_device'] = self.test_device.device_name
            if self.id_user:
                test_json['test_user'] = self.test_user.get_fullname()
            if self.id_participant:
                test_json['test_participant'] = self.test_participant.participant_name
            if self.id_service:
                test_json['test_service'] = self.test_service.service_name

        return test_json

    def to_json_create_event(self):
        return self.to_json(minimal=True)

    def to_json_update_event(self):
        return self.to_json(minimal=True)

    def to_json_delete_event(self):
        # Minimal information, delete can not be filtered
        return {'id_test': self.id_test, 'test_uuid': self.test_uuid}

    @staticmethod
    def create_defaults(test=False):
        if test:
            from opentera.db.models.TeraSession import TeraSession
            from opentera.db.models.TeraDevice import TeraDevice
            from opentera.db.models.TeraParticipant import TeraParticipant
            from opentera.db.models.TeraUser import TeraUser
            from opentera.db.models.TeraTestType import TeraTestType

            session2 = TeraSession.get_session_by_name("Séance #2")
            session3 = TeraSession.get_session_by_name("Séance #3")

            pretesttype = TeraTestType.get_test_type_by_id(1)
            posttesttype = TeraTestType.get_test_type_by_id(2)

            for i in range(4):
                new_test = TeraTest()
                new_test.test_name = "Test #" + str(i)
                new_test.test_session = session2
                new_test.test_uuid = str(uuid.uuid4())
                if i == 0:
                    new_test.id_test_type = pretesttype.id_test_type
                    new_test.id_participant = TeraParticipant.get_participant_by_name('Participant #1').id_participant
                if i == 1:
                    new_test.id_test_type = posttesttype.id_test_type
                    new_test.id_user = TeraUser.get_user_by_id(2).id_user
                if i == 2:
                    new_test.id_test_type = pretesttype.id_test_type
                    new_test.id_device = TeraDevice.get_device_by_id(1).id_device
                if i == 3:
                    new_test.test_session = session3
                    new_test.id_test_type = pretesttype.id_test_type
                    new_test.id_participant = TeraParticipant.get_participant_by_name('Participant #1').id_participant
                db.session.add(new_test)

            db.session.commit()

    @staticmethod
    def get_test_by_id(test_id: int):
        return TeraTest.query.filter_by(id_test=test_id).first()

    @staticmethod
    def get_test_by_uuid(test_uuid: str):
        return TeraTest.query.filter_by(test_uuid=test_uuid).first()

    @staticmethod
    def gettests_for_device(device_id: int):
        return TeraTest.query.filter_by(id_device=device_id).all()

    @staticmethod
    def get_tests_for_user(user_id: int):
        return TeraTest.query.filter_by(id_user=user_id).all()

    @staticmethod
    def get_tests_for_session(session_id: int):
        return TeraTest.query.filter_by(id_session=session_id).all()

    @staticmethod
    def get_tests_for_participant(part_id: int):
        return TeraTest.query.filter_by(id_participant=part_id).all()

    @staticmethod
    def get_tests_for_service(service_id: int):
        return TeraTest.query.filter_by(id_service=service_id).all()

    @staticmethod
    def get_access_token(test_uuids: list, token_key: str, requester_uuid: str, expiration=3600):
        import time
        import jwt

        # Creating token with user info
        now = time.time()
        payload = {
            'iat': int(now),
            'exp': int(now) + expiration,
            'iss': 'TeraServer',
            'test_uuids': test_uuids,
            'requester_uuid': requester_uuid
        }

        return jwt.encode(payload, token_key, algorithm='HS256')

    @classmethod
    def insert(cls, test):
        # Generate UUID
        test.test_uuid = str(uuid.uuid4())

        super().insert(test)
