from typing import List

from BaseServiceAPITest import BaseServiceAPITest
from modules.FlaskModule.FlaskModule import flask_app
from opentera.db.models.TeraUser import TeraUser


class ServiceQueryUsersTest(BaseServiceAPITest):
    test_endpoint = '/api/service/users'

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
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params=None, endpoint=self.test_endpoint)
            self.assertEqual(400, response.status_code)

    def test_get_endpoint_with_token_auth_with_wrong_params(self):
        with self._flask_app.app_context():
            # Get all users from DB
            users: List[TeraUser] = TeraUser.query.all()
            for user in users:
                params = {'user_uuid_wrong': user.user_uuid}
                response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                             params=params, endpoint=self.test_endpoint)
                self.assertEqual(400, response.status_code)

    def test_get_endpoint_with_token_auth_with_user_uuid(self):
        with self._flask_app.app_context():
            # Get all users from DB
            users: List[TeraUser] = TeraUser.query.all()
            for user in users:
                params = {'user_uuid': user.user_uuid}
                response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                             params=params, endpoint=self.test_endpoint)
                self.assertEqual(200, response.status_code)
                user_json = user.to_json()
                self.assertEqual(user_json, response.json)
