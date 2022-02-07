import os
from requests import get, delete
import json
from datetime import datetime, timedelta
from tests.modules.FlaskModule.API.BaseAPITest import BaseAPITest
from opentera.services.ServiceOpenTera import ServiceOpenTera
from opentera.services.ServiceConfigManager import ServiceConfigManager


class FileTransferAssetFileAndInfosTest(BaseAPITest):

    host = '127.0.0.1'
    port = 40075
    test_endpoint = '/file/api/assets'
    test_infos_endpoint = '/file/api/assets/infos'
    service_token = None
    user_token = None
    participant_static_token = None
    participant_dynamic_token = None
    device_token = None
    test_file_size = 0

    def setUp(self):
        # User - dynamic token only
        params = {}
        response = self._request_with_http_auth('admin', 'admin', params, '/api/user/login')
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertTrue(json_data.__contains__('user_token'))
        self.user_token = json_data['user_token']

        # Device - static token
        params = {'id_device': 1}
        response = self._request_with_http_auth('admin', 'admin', params, '/api/user/devices')
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertEqual(len(json_data), 1)
        self.assertTrue(json_data[0].__contains__('device_token'))
        self.device_token = json_data[0]['device_token']

        # Service
        # Initialize service from redis, posing as VideoRehabService
        # Use admin account to get service information (and tokens)
        response = self._request_with_http_auth(username='admin', password='admin', payload='key=VideoRehabService',
                                                endpoint='/api/user/services')
        self.assertEqual(response.status_code, 200)
        services = json.loads(response.text)
        self.assertEqual(len(services), 1)

        service_config = ServiceConfigManager()
        config_file = os.path.abspath(os.path.dirname(os.path.realpath(__file__)) +
                                      '../../../../services/VideoRehabService/VideoRehabService.json')
        service_config.load_config(filename=config_file)
        service_uuid = services[0]['service_uuid']
        service_config.service_config['ServiceUUID'] = service_uuid
        service = ServiceOpenTera(config_man=service_config, service_info=services[0])
        self.service_token = service.service_token

        # Participant static token
        params = {'id_participant': 1}
        response = self._request_with_http_auth('admin', 'admin', params, '/api/user/participants')
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertEqual(len(json_data), 1)
        self.assertTrue(json_data[0].__contains__('participant_token'))
        self.participant_static_token = json_data[0]['participant_token']

        # Participant dynamic token
        params = {}
        response = self._request_with_http_auth('participant1', 'opentera', params, '/api/participant/login')
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertTrue(json_data.__contains__('participant_token'))
        self.participant_dynamic_token = json_data['participant_token']

        # Create test file to stream
        self.test_file_size = 1024 * 1024 * 100
        f = open('testfile', 'wb')
        f.write(os.urandom(self.test_file_size))
        f.close()

    def tearDown(self):
        os.remove('testfile')

    def test_no_auth(self):
        response = self._request_with_no_auth()
        self.assertEqual(403, response.status_code)

    def test_post_no_auth(self):
        response = self._post_with_no_auth()
        self.assertEqual(403, response.status_code)

    def test_delete_no_auth(self):
        response = self._delete_with_no_auth(id_to_del=0)
        self.assertEqual(403, response.status_code)

    def test_query_no_params(self):
        response = self._request_with_token_auth(token=self.service_token)
        self.assertEqual(400, response.status_code)

    def test_query_bad_params(self):
        params = {'id_invalid': 1}
        response = self._request_with_token_auth(token=self.service_token, payload=params)
        self.assertEqual(response.status_code, 400)

    def test_full_as_user(self):
        file_asset = {}
        files = {'file': ('testfile', open('testfile', 'rb'), 'application/octet-stream'),
                 'file_asset': (None, json.dumps(file_asset), 'application/json')}
        response = self._post_file_with_token(self.user_token, files=files)
        self.assertEqual(response.status_code, 400, 'Missing infos in file_asset')

        file_asset['id_session'] = 100
        file_asset['asset_name'] = "Test Asset"
        file_asset['asset_type'] = 'application/octet-stream'
        files = {'file': ('testfile', open('testfile', 'rb'), 'application/octet-stream'),
                 'file_asset': (None, json.dumps(file_asset), 'application/json')}
        response = self._post_file_with_token(self.user_token, files=files)
        self.assertEqual(response.status_code, 403, 'Forbidden access to session')

        file_asset['id_session'] = 1  # OK, OK... I'll do something right for once!
        files = {'file': ('testfile', open('testfile', 'rb'), 'application/octet-stream'),
                 'file_asset': (None, json.dumps(file_asset), 'application/json')}
        response = self._post_file_with_token(self.user_token, files=files)
        self.assertEqual(response.status_code, 200, 'Asset post OK')


