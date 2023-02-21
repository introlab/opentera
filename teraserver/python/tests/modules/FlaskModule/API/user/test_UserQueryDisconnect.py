from BaseUserAPITest import BaseUserAPITest
from opentera.db.models.TeraDevice import TeraDevice
from opentera.db.models.TeraUser import TeraUser
from opentera.db.models.TeraParticipant import TeraParticipant
from modules.DatabaseModule.DBManagerTeraUserAccess import DBManagerTeraUserAccess
import uuid


class UserQueryFormsTest(BaseUserAPITest):
    test_endpoint = '/api/user/disconnect'

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test_get_endpoint_no_auth(self):
        with self._flask_app.app_context():
            response = self.test_client.get(self.test_endpoint)
            self.assertEqual(401, response.status_code)

    def test_get_endpoint_with_token_auth_no_params(self):
        with self._flask_app.app_context():
            for user in TeraUser.query.all():
                user_token = user.get_token(self.user_token_key)
                response = self._get_with_user_token_auth(client=self.test_client, token=user_token,
                                                          params=None, endpoint=self.test_endpoint)
                self.assertEqual(400, response.status_code)

    def test_get_endpoint_with_invalid_id_user(self):
        with self._flask_app.app_context():
            for user in TeraUser.query.all():
                user_token = user.get_token(self.user_token_key)
                params = {'id_user': 12345}
                response = self._get_with_user_token_auth(client=self.test_client, token=user_token,
                                                          params=params, endpoint=self.test_endpoint)
                self.assertEqual(403, response.status_code)

    def test_get_endpoint_with_valid_id_user(self):
        with self._flask_app.app_context():
            for request_user in TeraUser.query.all():
                user_token = request_user.get_token(self.user_token_key)
                for user in TeraUser.query.all():
                    params = {'id_user': user.id_user}
                    response = self._get_with_user_token_auth(client=self.test_client, token=user_token,
                                                              params=params, endpoint=self.test_endpoint)

                    user_access: DBManagerTeraUserAccess = DBManagerTeraUserAccess(request_user)

                    if request_user.id_user == user.id_user:
                        self.assertEqual(400, response.status_code)
                    elif user.id_user in user_access.get_accessible_users_ids(admin_only=True):
                        self.assertEqual(200, response.status_code)
                    else:
                        self.assertEqual(403, response.status_code)

    def test_get_endpoint_with_invalid_user_uuid(self):
        with self._flask_app.app_context():
            for user in TeraUser.query.all():
                user_token = user.get_token(self.user_token_key)
                params = {'user_uuid': str(uuid.uuid4())}
                response = self._get_with_user_token_auth(client=self.test_client, token=user_token,
                                                          params=params, endpoint=self.test_endpoint)
                self.assertEqual(403, response.status_code)

    def test_get_endpoint_with_valid_user_uuid(self):
        with self._flask_app.app_context():
            for request_user in TeraUser.query.all():
                user_token = request_user.get_token(self.user_token_key)
                for user in TeraUser.query.all():
                    params = {'user_uuid': user.user_uuid}
                    response = self._get_with_user_token_auth(client=self.test_client, token=user_token,
                                                              params=params, endpoint=self.test_endpoint)

                    user_access: DBManagerTeraUserAccess = DBManagerTeraUserAccess(request_user)

                    if request_user.user_uuid == user.user_uuid:
                        self.assertEqual(400, response.status_code)
                    elif user.user_uuid in user_access.get_accessible_users_uuids(admin_only=True):
                        self.assertEqual(200, response.status_code)
                    else:
                        self.assertEqual(403, response.status_code)

    def test_get_endpoint_with_invalid_id_participant(self):
        with self._flask_app.app_context():
            for request_user in TeraUser.query.all():
                user_token = request_user.get_token(self.user_token_key)

                params = {'id_participant': 12345}
                response = self._get_with_user_token_auth(client=self.test_client, token=user_token,
                                                          params=params, endpoint=self.test_endpoint)
                self.assertEqual(403, response.status_code)

    def test_get_endpoint_with_valid_id_participant(self):
        with self._flask_app.app_context():
            for request_user in TeraUser.query.all():
                user_token = request_user.get_token(self.user_token_key)

                for participant in TeraParticipant.query.all():
                    params = {'id_participant': participant.id_participant}
                    response = self._get_with_user_token_auth(client=self.test_client, token=user_token,
                                                              params=params, endpoint=self.test_endpoint)

                    user_access: DBManagerTeraUserAccess = DBManagerTeraUserAccess(request_user)

                    if participant.id_participant in user_access.get_accessible_participants_ids(admin_only=True):
                        self.assertEqual(200, response.status_code)
                    else:
                        self.assertEqual(403, response.status_code)

    def test_get_endpoint_with_invalid_participant_uuid(self):
        with self._flask_app.app_context():
            for user in TeraUser.query.all():
                user_token = user.get_token(self.user_token_key)
                params = {'participant_uuid': str(uuid.uuid4())}
                response = self._get_with_user_token_auth(client=self.test_client, token=user_token,
                                                          params=params, endpoint=self.test_endpoint)
                self.assertEqual(403, response.status_code)

    def test_get_endpoint_with_valid_participant_uuid(self):
        with self._flask_app.app_context():
            for request_user in TeraUser.query.all():
                user_token = request_user.get_token(self.user_token_key)

                for participant in TeraParticipant.query.all():
                    params = {'participant_uuid': participant.participant_uuid}
                    response = self._get_with_user_token_auth(client=self.test_client, token=user_token,
                                                              params=params, endpoint=self.test_endpoint)

                    user_access: DBManagerTeraUserAccess = DBManagerTeraUserAccess(request_user)

                    if participant.participant_uuid in user_access.get_accessible_participants_uuids(admin_only=True):
                        self.assertEqual(200, response.status_code)
                    else:
                        self.assertEqual(403, response.status_code)

    def test_get_endpoint_with_invalid_id_device(self):
        with self._flask_app.app_context():
            for user in TeraUser.query.all():
                user_token = user.get_token(self.user_token_key)
                params = {'id_device': 12345}
                response = self._get_with_user_token_auth(client=self.test_client, token=user_token,
                                                          params=params, endpoint=self.test_endpoint)
                self.assertEqual(403, response.status_code)

    def test_get_endpoint_with_valid_id_device(self):
        with self._flask_app.app_context():
            for request_user in TeraUser.query.all():
                user_token = request_user.get_token(self.user_token_key)

                for device in TeraDevice.query.all():
                    params = {'id_device': device.id_device}
                    response = self._get_with_user_token_auth(client=self.test_client, token=user_token,
                                                              params=params, endpoint=self.test_endpoint)

                    user_access: DBManagerTeraUserAccess = DBManagerTeraUserAccess(request_user)

                    if device.id_device in user_access.get_accessible_devices_ids(admin_only=True):
                        self.assertEqual(200, response.status_code)
                    else:
                        self.assertEqual(403, response.status_code)

    def test_get_endpoint_with_invalid_device_uuid(self):
        with self._flask_app.app_context():
            for user in TeraUser.query.all():
                user_token = user.get_token(self.user_token_key)
                params = {'device_uuid': str(uuid.uuid4())}
                response = self._get_with_user_token_auth(client=self.test_client, token=user_token,
                                                          params=params, endpoint=self.test_endpoint)
                self.assertEqual(403, response.status_code)

    def test_get_endpoint_with_valid_device_uuid(self):
        with self._flask_app.app_context():
            for request_user in TeraUser.query.all():
                user_token = request_user.get_token(self.user_token_key)

                for device in TeraDevice.query.all():
                    params = {'device_uuid': device.device_uuid}
                    response = self._get_with_user_token_auth(client=self.test_client, token=user_token,
                                                              params=params, endpoint=self.test_endpoint)

                    user_access: DBManagerTeraUserAccess = DBManagerTeraUserAccess(request_user)

                    if device.device_uuid in user_access.get_accessible_devices_uuids(admin_only=True):
                        self.assertEqual(200, response.status_code)
                    else:
                        self.assertEqual(403, response.status_code)
