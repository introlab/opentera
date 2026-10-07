from opentera.db.models import TeraParticipant
from tests.modules.FlaskModule.API.participant.BaseParticipantAPITest import BaseParticipantAPITest
from opentera.db.models.TeraService import TeraService


class ParticipantQueryServiceConfigsTest(BaseParticipantAPITest):
    test_endpoint = '/api/participant/services/configs'

    def setUp(self):
        super().setUp()
        with self._flask_app.app_context():
            self.participant_token = TeraParticipant.get_participant_by_name('Participant #1').participant_token

    def tearDown(self):
        super().tearDown()

    def test_get_no_auth(self):
        with self._flask_app.app_context():
            response = self.test_client.get(self.test_endpoint)
            self.assertEqual(401, response.status_code)

    def test_post_no_auth(self):
        with self._flask_app.app_context():
            response = self.test_client.post(self.test_endpoint)
            self.assertEqual(401, response.status_code)

    def test_delete_no_auth(self):
        with self._flask_app.app_context():
            response = self.test_client.delete(self.test_endpoint)
            self.assertEqual(401, response.status_code)

    def test_get_endpoint_invalid_http_auth(self):
        with self._flask_app.app_context():
            response = self._get_with_participant_http_auth(self.test_client, username='invalid', password='invalid')
            self.assertEqual(401, response.status_code)

    def test_get_endpoint_invalid_token_auth(self):
        with self._flask_app.app_context():
            response = self._get_with_participant_token_auth(self.test_client, token='invalid')
            self.assertEqual(401, response.status_code)

    def test_post_endpoint_invalid_token_auth(self):
        with self._flask_app.app_context():
            response = self._post_with_participant_token_auth(self.test_client, token='invalid')
            self.assertEqual(401, response.status_code)

    def test_post_endpoint_invalid_http_auth(self):
        with self._flask_app.app_context():
            response = self._post_with_participant_http_auth(self.test_client, username='invalid', password='invalid')
            self.assertEqual(401, response.status_code)

    def test_delete_endpoint_invalid_http_auth(self):
        with self._flask_app.app_context():
            response = self._delete_with_participant_http_auth(self.test_client, username='invalid', password='invalid')
            self.assertEqual(401, response.status_code)

    def test_delete_endpoint_invalid_token_auth(self):
        with self._flask_app.app_context():
            response = self._delete_with_participant_token_auth(self.test_client, token='invalid')
            self.assertEqual(401, response.status_code)

    def test_query_no_params(self):
        with self._flask_app.app_context():
            response = self._get_with_participant_token_auth(self.test_client, token=self.participant_token)
            self.assertEqual(400, response.status_code)

    def test_query_for_service(self):
        with self._flask_app.app_context():
            service_id = TeraService.get_service_by_key('VideoRehabService').id_service
            response = self._get_with_participant_token_auth(self.test_client, self.participant_token,
                                                     params={'id_service': service_id})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self._checkJson(response.json)
            self.assertEqual(response.json['id_service'], service_id)

            response = self._get_with_participant_token_auth(self.test_client, self.participant_token,
                                                     params={'service_key': 'VideoRehabService'})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self._checkJson(response.json)
            self.assertEqual(response.json['id_service'], service_id)
            self.assertEqual(response.json['service_config_name'], 'Télé-réadaptation vidéo')

    def test_query_for_invalid_service(self):
        with self._flask_app.app_context():
            response = self._get_with_participant_token_auth(self.test_client, self.participant_token,
                                                     params={'id_service': 33})
            self.assertEqual(200, response.status_code)
            self.assertTrue(not response.json)

    def test_query_specific_config(self):
        with self._flask_app.app_context():
            service_id = TeraService.get_service_by_key('VideoRehabService').id_service
            response = self._get_with_participant_token_auth(self.test_client, self.participant_token,
                                                     params={'id_service': service_id, 'id_specific': 'pc-001'})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self._checkJson(json_data=response.json)
            self.assertEqual(response.json['id_participant'], 1)
            self.assertEqual(response.json['service_config_specific_id'], 'pc-001')

            response = self._get_with_participant_token_auth(self.test_client, self.participant_token,
                                                     params={'id_service': service_id, 'id_specific': 'pc-xxx'})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self._checkJson(json_data=response.json)
            self.assertEqual(response.json['id_participant'], 1)
            self.assertEqual(response.json['service_config_specific_id'], None)

    def test_query_list_config(self):
        with self._flask_app.app_context():
            service_id = TeraService.get_service_by_key('VideoRehabService').id_service
            response = self._get_with_participant_token_auth(self.test_client, self.participant_token,
                                                             params={'id_service': service_id, 'list': 1})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self._checkJson(json_data=response.json)
            self.assertIn('service_config_specifics', response.json)
            self.assertGreater(len(response.json['service_config_specifics']), 0)

    def test_post_and_delete(self):
        with self._flask_app.app_context():
            json_data = {
                'service_config': {
                }
            }

            response = self._post_with_participant_token_auth(self.test_client, self.participant_token, json=json_data)
            self.assertEqual(400, response.status_code, msg="Missing id_service_config")  # Missing id_service_config

            json_data['service_config']['id_service_config'] = 0
            response = self._post_with_participant_token_auth(self.test_client, self.participant_token, json=json_data)
            self.assertEqual(400, response.status_code, msg="Missing id_service")

            json_data['service_config']['id_service'] = 2
            response = self._post_with_participant_token_auth(self.test_client, self.participant_token, json=json_data)
            self.assertEqual(403, response.status_code, msg="Forbidden service access")

            service_id = TeraService.get_service_by_key('FileTransferService').id_service
            json_data['service_config']['id_service'] = service_id
            json_data['service_config']['id_user'] = 2
            json_data['service_config']['id_device'] = 3
            response = self._post_with_participant_token_auth(self.test_client, self.participant_token, json=json_data)
            self.assertEqual(200, response.status_code, msg="Post new")  # All ok now!

            json_data = response.json
            self._checkJson(json_data)
            self.assertNotIn('id_user', json_data)
            self.assertNotIn('id_device', json_data)
            current_id = json_data['id_service_config']

            json_data = {
                'service_config': {
                    'id_service_config': current_id,
                    'service_config_config': '{"Test": "123"}'
                }
            }

            response = self._post_with_participant_token_auth(self.test_client, self.participant_token, json=json_data)
            self.assertEqual(200, response.status_code, msg="Post update OK")

            json_data['service_config']['service_config_config'] = '{"Test": "456"}'
            json_data['service_config']['id_specific'] = 'Test Spec'
            response = self._post_with_participant_token_auth(self.test_client, self.participant_token, json=json_data)
            self.assertEqual(200, response.status_code, msg="Post specific config OK")
            json_data = response.json
            self._checkJson(json_data)

            # Check config
            response = self._get_with_participant_token_auth(self.test_client, self.participant_token,
                                                     params={'id_service': service_id})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self._checkJson(response.json)
            self.assertEqual(response.json['service_config_config']['Test'], '123')
            self.assertEqual(response.json['service_config_specific_id'], None)

            response = self._get_with_participant_token_auth(self.test_client, self.participant_token,
                                                     params={'id_service': service_id, 'id_specific': 'Test Spec'})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            data_item = response.json
            self._checkJson(json_data=data_item)
            self.assertEqual(data_item['service_config_config']['Test'], '456')
            self.assertEqual(data_item['service_config_specific_id'], 'Test Spec')

            params = {'id': 1}
            response = self._delete_with_participant_token_auth(self.test_client, self.participant_token, params=params)
            self.assertEqual(403, response.status_code, msg="Delete denied")

            params = {'id': current_id}
            response = self._delete_with_participant_token_auth(self.test_client, self.participant_token, params=params)
            self.assertEqual(200, response.status_code, msg="Delete OK")

    def _checkJson(self, json_data, minimal=False):
        self.assertGreater(len(json_data), 0)
        self.assertTrue(json_data.__contains__('id_service_config'))
        self.assertTrue(json_data.__contains__('id_service'))
        self.assertTrue(json_data.__contains__('service_config_config'))
        self.assertTrue(json_data.__contains__('service_config_last_update_time'))
        self.assertTrue(json_data.__contains__('service_config_name'))
