from typing import List

from tests.modules.FlaskModule.API.service.BaseServiceAPITest import BaseServiceAPITest
from modules.FlaskModule.FlaskModule import flask_app
from opentera.db.models.TeraSessionType import TeraSessionType


class ServiceQuerySessionManagerTest(BaseServiceAPITest):
    test_endpoint = '/api/service/sessions/manager'

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test_get_endpoint_no_auth(self):
        with self._flask_app.app_context():
            response = self.test_client.get(self.test_endpoint)
            self.assertEqual(405, response.status_code)  # Not implemented

    def test_get_endpoint_with_token_auth_no_params(self):
        with self._flask_app.app_context():
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params=None, endpoint=self.test_endpoint)
            self.assertEqual(405, response.status_code)  # Not implemented

    def test_post_endpoint_without_token_no_params_no_json(self):
        with self._flask_app.app_context():
            response = self.test_client.post(self.test_endpoint, query_string=None, headers=None, json={})
            self.assertEqual(401, response.status_code)

    def test_post_endpoint_with_token_no_params_no_json(self):
        with self._flask_app.app_context():
            response = self._post_with_service_token_auth(client=self.test_client, token=self.service_token, json={},
                                                          params={}, endpoint=self.test_endpoint)
            self.assertEqual(400, response.status_code)

    def test_post_endpoint_with_token_no_params_session_invalid_schema(self):
        with self._flask_app.app_context():
            schema = {
                    'session_manage_invalid': {
                        'session_uuid': '',
                        'id_service': self.id_service,
                        'id_session': 0,
                        'id_creator_user': 0,
                        'id_creator_participant': 0,
                        'id_creator_device': 0,
                        'id_creator_service': 0,
                        'id_session_type': 0,
                        'session_users': [],
                        'session_participants': [],
                        'session_devices': [],
                        'action': 'start',
                        'parameters': ''
                    }
                }
            response = self._post_with_service_token_auth(client=self.test_client, token=self.service_token, json=schema,
                                                          params={}, endpoint=self.test_endpoint)
            self.assertEqual(400, response.status_code)

    def test_post_endpoint_with_token_no_params_session_valid_schema_missing_action(self):
        with self._flask_app.app_context():
            schema = {
                    'session_manage': {
                        'session_uuid': '',
                        'id_service': self.id_service,
                        'id_session': 0,
                        'id_creator_user': 0,
                        'id_creator_participant': 0,
                        'id_creator_device': 0,
                        'id_creator_service': 0,
                        'id_session_type': 0,
                        'session_users': [],
                        'session_participants': [],
                        'session_devices': [],
                        # 'action': 'start',
                        'parameters': ''
                    }
                }
            response = self._post_with_service_token_auth(client=self.test_client, token=self.service_token, json=schema,
                                                          params={}, endpoint=self.test_endpoint)
            self.assertEqual(400, response.status_code)

    def test_post_endpoint_with_token_no_params_session_valid_and_invalid_session_uuid(self):
        with self._flask_app.app_context():
            schema = {
                    'session_manage': {
                        'session_uuid': 'invalid',
                        'id_service': 0,
                        # 'id_session': 0,
                        'id_creator_user': 0,
                        'id_creator_participant': 0,
                        'id_creator_device': 0,
                        'id_creator_service': 0,
                        'id_session_type': 0,
                        'session_users': [],
                        'session_participants': [],
                        'session_devices': [],
                        'action': 'start',
                        'parameters': ''
                    }
                }
            response = self._post_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                          json=schema, params={}, endpoint=self.test_endpoint)
            self.assertEqual(400, response.status_code)

    def test_post_endpoint_with_token_session_valid_schema_and_invalid_id_service_empty_users_participants_devices(self):
        with self._flask_app.app_context():
            session_types: List[TeraSessionType] = TeraSessionType.query.all()

            for session_type in session_types:

                schema = {
                        'session_manage': {
                            'session_uuid': '',
                            'id_service': 0,
                            'id_session': 0,
                            'id_creator_user': 0,
                            'id_creator_participant': 0,
                            'id_creator_device': 0,
                            'id_creator_service': 0,
                            'id_session_type': session_type.id_session_type,
                            'session_users': [],
                            'session_participants': [],
                            'session_devices': [],
                            'action': 'start',
                            'parameters': ''
                        }
                    }
                response = self._post_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                              json=schema, params={}, endpoint=self.test_endpoint)
                if session_type.id_service is None:
                    self.assertEqual(400, response.status_code)
                else:
                    self.assertEqual(200, response.status_code)

    def test_post_endpoint_with_token_no_params_session_valid_schema_empty_users_participants_devices(self):
        with self._flask_app.app_context():
            session_types: List[TeraSessionType] = TeraSessionType.query.all()

            for session_type in session_types:

                schema = {
                        'session_manage': {
                            'session_uuid': '',
                            'id_service': self.id_service,
                            'id_session': 0,
                            'id_creator_user': 0,
                            'id_creator_participant': 0,
                            'id_creator_device': 0,
                            'id_creator_service': 0,
                            'id_session_type': session_type.id_session_type,
                            'session_users': [],
                            'session_participants': [],
                            'session_devices': [],
                            'action': 'start',
                            'parameters': ''
                        }
                    }
                response = self._post_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                              json=schema, params={}, endpoint=self.test_endpoint)
                self.assertEqual(200, response.status_code)
