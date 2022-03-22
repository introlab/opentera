import os
from requests import get
import json
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
        with open('testfile', 'rb') as f:
            files = {'file': ('testfile', f, 'application/octet-stream',
                              {'Content-Length': self.test_file_size}),
                     'file_asset': (None, json.dumps(file_asset), 'application/json')}
            response = self._post_file_with_token(self.user_token, files=files)
            self.assertEqual(response.status_code, 400, 'Missing infos in file_asset')

        file_asset['id_session'] = 100
        file_asset['asset_name'] = "Test Asset"
        file_asset['asset_type'] = 'application/octet-stream'
        with open('testfile', 'rb') as f:
            files = {'file': ('testfile', f, 'application/octet-stream',
                              {'Content-Length': self.test_file_size}),
                     'file_asset': (None, json.dumps(file_asset), 'application/json')}
            response = self._post_file_with_token(self.user_token, files=files)
            self.assertEqual(response.status_code, 403, 'Forbidden access to session')

        file_asset['id_session'] = 1  # OK, OK... I'll do something right for once!
        with open('testfile', 'rb') as f:
            files = {'file': ('testfile', f, 'application/octet-stream',
                              {'Content-Length': self.test_file_size}),
                     'file_asset': (None, json.dumps(file_asset), 'application/json')}
            response = self._post_file_with_token(self.user_token, files=files)
            self.assertEqual(response.status_code, 200, 'Asset post OK')
            json_data = response.json()
            self.assertTrue(json_data.__contains__('asset_uuid'))
            self.assertTrue(json_data.__contains__('id_asset'))

        asset_uuid = json_data['asset_uuid']
        asset_id = json_data['id_asset']

        # Query asset information to make sure it was properly created
        payload = {'id_asset': asset_id, 'with_urls': True}
        response = self._request_with_http_auth(username='admin', password='admin', payload=payload,
                                                endpoint='/api/user/assets')
        self.assertEqual(response.status_code, 200)

        json_data = response.json()
        self.assertTrue(len(json_data), 1)
        self.assertEqual(json_data[0]['id_asset'], asset_id)

        asset_infos_url = json_data[0]['asset_infos_url'] + '?asset_uuid=' + asset_uuid
        asset_url = json_data[0]['asset_url'] + '?asset_uuid=' + asset_uuid
        access_token = json_data[0]['access_token']

        # Get specific service information on that URL
        response = self._request_full_url_with_token_auth(token=self.user_token, full_url=asset_infos_url)
        self.assertEqual(response.status_code, 400, 'Missing access token')

        response = self._request_full_url_with_token_auth(token=self.user_token,
                                                          full_url=asset_infos_url + '&access_token=123124')
        self.assertEqual(response.status_code, 403, 'Forbidden - invalid token')

        response = self._request_full_url_with_token_auth(token=self.user_token,
                                                          full_url=asset_infos_url + '&access_token=' + access_token)
        self.assertEqual(response.status_code, 200, 'Service asset infos OK')
        json_data = response.json()
        self.assertTrue(json_data.__contains__('asset_uuid'))
        self.assertEqual(json_data['asset_uuid'], asset_uuid)

        # Change original file name with a POST query
        params = {}
        response = self._post_with_token(token=self.user_token, payload=params, endpoint=self.test_infos_endpoint)
        self.assertEqual(response.status_code, 400, 'Missing file asset info')

        params = {'access_token': access_token}
        response = self._post_with_token(token=self.user_token, payload=params, endpoint=self.test_infos_endpoint)
        self.assertEqual(response.status_code, 400, 'Badly formatted request')

        params = {'file_asset': {}}
        response = self._post_with_token(token=self.user_token, payload=params, endpoint=self.test_infos_endpoint)
        self.assertEqual(response.status_code, 400, 'Missing asset UUID')

        params = {'file_asset': {'asset_uuid': '1111111', 'access_token': access_token}}
        response = self._post_with_token(token=self.user_token, payload=params, endpoint=self.test_infos_endpoint)
        self.assertEqual(response.status_code, 403, 'Forbidden access to UUID')

        params = {'file_asset': {'asset_uuid': asset_uuid, 'access_token': access_token}}
        response = self._post_with_token(token=self.user_token, payload=params, endpoint=self.test_infos_endpoint)
        self.assertEqual(response.status_code, 400, 'No file name')

        params = {'file_asset': {'asset_uuid': asset_uuid, 'asset_original_filename': 'testfile2',
                                 'access_token': access_token}}
        response = self._post_with_token(token=self.user_token, payload=params, endpoint=self.test_infos_endpoint)
        self.assertEqual(response.status_code, 200, 'Original file name changed')
        self.assertEqual(response.json()['asset_original_filename'], 'testfile2')

        # Try to download that file now from the file URL
        response = self._request_full_url_with_token_auth(token=self.user_token, full_url=asset_url)
        self.assertEqual(response.status_code, 400, 'Missing access token')

        response = self._request_full_url_with_token_auth(token=self.user_token,
                                                          full_url=asset_url + '&access_token=123124')
        self.assertEqual(response.status_code, 403, 'Forbidden access with invalid token')

        request_headers = {'Authorization': 'OpenTera ' + self.user_token}
        response = get(url=asset_url + '&access_token=' + access_token, headers=request_headers, verify=False,
                       stream=True)
        self.assertEqual(response.status_code, 200, 'Downloading file')
        with open('testfile2', 'wb') as download_file:
            for chunk in response.iter_content(chunk_size=4096):
                download_file.write(chunk)

        import filecmp
        self.assertTrue(filecmp.cmp('testfile', 'testfile2'))
        os.remove('testfile2')

        # Delete asset from service
        response = self._delete_with_token_plus(token=self.user_token)
        self.assertEqual(response.status_code, 400, 'Missing uuid')

        response = self._delete_with_token_plus(token=self.user_token, payload={'uuid': asset_uuid})
        self.assertEqual(response.status_code, 400, 'Missing access token')

        response = self._delete_with_token_plus(token=self.user_token, payload={'uuid': asset_uuid,
                                                                                'access_token': 123})
        self.assertEqual(response.status_code, 403, 'Forbidden access')

        response = self._delete_with_token_plus(token=self.user_token, payload={'uuid': asset_uuid,
                                                                                'access_token': access_token})
        self.assertEqual(response.status_code, 200, 'Delete OK')

    def test_full_as_device(self):
        file_asset = dict()
        file_asset['id_session'] = 100
        file_asset['asset_name'] = "Test Asset"
        file_asset['asset_type'] = 'application/octet-stream'
        with open('testfile', 'rb') as f:
            files = {'file': ('testfile', f, 'application/octet-stream',
                              {'Content-Length': self.test_file_size}),
                     'file_asset': (None, json.dumps(file_asset), 'application/json')}
            response = self._post_file_with_token(self.device_token, files=files)
            self.assertEqual(response.status_code, 403, 'Forbidden access to session')

        file_asset['id_session'] = 9
        with open('testfile', 'rb') as f:
            files = {'file': ('testfile', f, 'application/octet-stream',
                              {'Content-Length': self.test_file_size}),
                     'file_asset': (None, json.dumps(file_asset), 'application/json')}
            response = self._post_file_with_token(self.device_token, files=files)
            self.assertEqual(response.status_code, 200, 'Asset post OK')
            json_data = response.json()
            self.assertTrue(json_data.__contains__('asset_uuid'))
            self.assertTrue(json_data.__contains__('id_asset'))

        asset_uuid = json_data['asset_uuid']
        asset_id = json_data['id_asset']

        # Query asset information to make sure it was properly created
        payload = {'id_asset': asset_id, 'with_urls': True}
        response = self._request_with_token_auth(token=self.device_token, payload=payload,
                                                 endpoint='/api/device/assets')
        self.assertEqual(response.status_code, 200)

        json_data = response.json()
        self.assertEqual(len(json_data), 1)
        self.assertEqual(json_data[0]['id_asset'], asset_id)

        asset_infos_url = json_data[0]['asset_infos_url'] + '?asset_uuid=' + asset_uuid
        asset_url = json_data[0]['asset_url'] + '?asset_uuid=' + asset_uuid
        access_token = json_data[0]['access_token']

        # Get specific service information on that URL
        response = self._request_full_url_with_token_auth(token=self.device_token,
                                                          full_url=asset_infos_url + '&access_token=123124')
        self.assertEqual(response.status_code, 403, 'Forbidden - invalid token')

        response = self._request_full_url_with_token_auth(token=self.device_token,
                                                          full_url=asset_infos_url + '&access_token=' + access_token)
        self.assertEqual(response.status_code, 200, 'Service asset infos OK')
        json_data = response.json()
        self.assertTrue(json_data.__contains__('asset_uuid'))
        self.assertEqual(json_data['asset_uuid'], asset_uuid)

        # Change original file name with a POST query
        params = {'file_asset': {'asset_uuid': '1111111', 'access_token': access_token}}
        response = self._post_with_token(token=self.device_token, payload=params, endpoint=self.test_infos_endpoint)
        self.assertEqual(response.status_code, 403, 'Forbidden access to UUID')

        params = {'file_asset': {'asset_uuid': asset_uuid, 'asset_original_filename': 'testfile2',
                                 'access_token': access_token}}
        response = self._post_with_token(token=self.device_token, payload=params, endpoint=self.test_infos_endpoint)
        self.assertEqual(response.status_code, 200, 'Original file name changed')
        self.assertEqual(response.json()['asset_original_filename'], 'testfile2')

        # Try to download that file now from the file URL
        response = self._request_full_url_with_token_auth(token=self.device_token,
                                                          full_url=asset_url + '&access_token=123124')
        self.assertEqual(response.status_code, 403, 'Forbidden access with invalid token')

        request_headers = {'Authorization': 'OpenTera ' + self.device_token}
        response = get(url=asset_url + '&access_token=' + access_token, headers=request_headers, verify=False,
                       stream=True)
        self.assertEqual(response.status_code, 200, 'Downloading file')
        with open('testfile2', 'wb') as download_file:
            for chunk in response.iter_content(chunk_size=4096):
                download_file.write(chunk)

        import filecmp
        self.assertTrue(filecmp.cmp('testfile', 'testfile2'))
        os.remove('testfile2')

        # Delete asset from service
        response = self._delete_with_token_plus(token=self.device_token, payload={'uuid': asset_uuid,
                                                                                  'access_token': 123})
        self.assertEqual(response.status_code, 403, 'Forbidden access')

        response = self._delete_with_token_plus(token=self.device_token, payload={'uuid': asset_uuid,
                                                                                  'access_token': access_token})
        self.assertEqual(response.status_code, 200, 'Delete OK')

    def test_full_as_dynamic_participant(self):
        file_asset = dict()
        file_asset['id_session'] = 100
        file_asset['asset_name'] = "Test Asset"
        file_asset['asset_type'] = 'application/octet-stream'
        with open('testfile', 'rb') as f:
            files = {'file': ('testfile', f, 'application/octet-stream',
                              {'Content-Length': self.test_file_size}),
                     'file_asset': (None, json.dumps(file_asset), 'application/json')}
            response = self._post_file_with_token(self.participant_dynamic_token, files=files)
            self.assertEqual(response.status_code, 403, 'Forbidden access to session')

        file_asset['id_session'] = 9
        with open('testfile', 'rb') as f:
            files = {'file': ('testfile', f, 'application/octet-stream',
                              {'Content-Length': self.test_file_size}),
                     'file_asset': (None, json.dumps(file_asset), 'application/json')}
            response = self._post_file_with_token(self.participant_dynamic_token, files=files)
            self.assertEqual(response.status_code, 200, 'Asset post OK')
            json_data = response.json()
            self.assertTrue(json_data.__contains__('asset_uuid'))
            self.assertTrue(json_data.__contains__('id_asset'))

        asset_uuid = json_data['asset_uuid']
        asset_id = json_data['id_asset']

        # Query asset information to make sure it was properly created
        payload = {'id_asset': asset_id, 'with_urls': True}
        response = self._request_with_token_auth(token=self.participant_dynamic_token, payload=payload,
                                                 endpoint='/api/participant/assets')
        self.assertEqual(response.status_code, 200)

        json_data = response.json()
        self.assertTrue(len(json_data), 1)
        self.assertEqual(json_data[0]['id_asset'], asset_id)

        asset_infos_url = json_data[0]['asset_infos_url'] + '?asset_uuid=' + asset_uuid
        asset_url = json_data[0]['asset_url'] + '?asset_uuid=' + asset_uuid
        access_token = json_data[0]['access_token']

        # Get specific service information on that URL
        response = self._request_full_url_with_token_auth(token=self.participant_dynamic_token,
                                                          full_url=asset_infos_url + '&access_token=123124')
        self.assertEqual(response.status_code, 403, 'Forbidden - invalid token')

        response = self._request_full_url_with_token_auth(token=self.participant_dynamic_token,
                                                          full_url=asset_infos_url + '&access_token=' + access_token)
        self.assertEqual(response.status_code, 200, 'Service asset infos OK')
        json_data = response.json()
        self.assertTrue(json_data.__contains__('asset_uuid'))
        self.assertEqual(json_data['asset_uuid'], asset_uuid)

        # Change original file name with a POST query
        params = {'file_asset': {'asset_uuid': '1111111', 'access_token': access_token}}
        response = self._post_with_token(token=self.participant_dynamic_token, payload=params,
                                         endpoint=self.test_infos_endpoint)
        self.assertEqual(response.status_code, 403, 'Forbidden access to UUID')

        params = {'file_asset': {'asset_uuid': asset_uuid, 'asset_original_filename': 'testfile2',
                                 'access_token': access_token}}
        response = self._post_with_token(token=self.participant_dynamic_token, payload=params,
                                         endpoint=self.test_infos_endpoint)
        self.assertEqual(response.status_code, 200, 'Original file name changed')
        self.assertEqual(response.json()['asset_original_filename'], 'testfile2')

        # Try to download that file now from the file URL
        response = self._request_full_url_with_token_auth(token=self.participant_dynamic_token,
                                                          full_url=asset_url + '&access_token=123124')
        self.assertEqual(response.status_code, 403, 'Forbidden access with invalid token')

        request_headers = {'Authorization': 'OpenTera ' + self.participant_dynamic_token}
        response = get(url=asset_url + '&access_token=' + access_token, headers=request_headers, verify=False,
                       stream=True)
        self.assertEqual(response.status_code, 200, 'Downloading file')
        with open('testfile2', 'wb') as download_file:
            for chunk in response.iter_content(chunk_size=4096):
                download_file.write(chunk)

        import filecmp
        self.assertTrue(filecmp.cmp('testfile', 'testfile2'))
        os.remove('testfile2')

        # Delete asset from service
        response = self._delete_with_token_plus(token=self.participant_dynamic_token, payload={'uuid': asset_uuid,
                                                                                               'access_token': 123})
        self.assertEqual(response.status_code, 403, 'Forbidden access')

        response = self._delete_with_token_plus(token=self.participant_dynamic_token,
                                                payload={'uuid': asset_uuid, 'access_token': access_token})
        self.assertEqual(response.status_code, 200, 'Delete OK')

    def test_full_as_static_participant(self):
        file_asset = dict()
        file_asset['id_session'] = 9
        file_asset['asset_name'] = "Test Asset"
        file_asset['asset_type'] = 'application/octet-stream'
        with open('testfile', 'rb') as f:
            files = {'file': ('testfile', f, 'application/octet-stream',
                              {'Content-Length': self.test_file_size}),
                     'file_asset': (None, json.dumps(file_asset), 'application/json')}
            response = self._post_file_with_token(self.participant_static_token, files=files)
            self.assertEqual(response.status_code, 403, 'Asset post forbidden for static token')

    def test_full_as_service(self):
        file_asset = dict()
        file_asset['id_session'] = 100
        file_asset['asset_name'] = "Test Asset"
        file_asset['asset_type'] = 'application/octet-stream'
        with open('testfile', 'rb') as f:
            files = {'file': ('testfile', f, 'application/octet-stream',
                              {'Content-Length': self.test_file_size}),
                     'file_asset': (None, json.dumps(file_asset), 'application/json')}
            response = self._post_file_with_token(self.service_token, files=files)
            self.assertEqual(response.status_code, 403, 'Forbidden access to session')

        file_asset['id_session'] = 27
        with open('testfile', 'rb') as f:
            files = {'file': ('testfile', f, 'application/octet-stream',
                              {'Content-Length': self.test_file_size}),
                     'file_asset': (None, json.dumps(file_asset), 'application/json')}
            response = self._post_file_with_token(self.service_token, files=files)
            self.assertEqual(response.status_code, 400, 'Missing id creator')

        file_asset['id_user'] = 2
        with open('testfile', 'rb') as f:
            files = {'file': ('testfile', f, 'application/octet-stream',
                              {'Content-Length': self.test_file_size}),
                     'file_asset': (None, json.dumps(file_asset), 'application/json')}
            response = self._post_file_with_token(self.service_token, files=files)
            self.assertEqual(response.status_code, 200, 'Asset Post OK')

            json_data = response.json()
            self.assertTrue(json_data.__contains__('asset_uuid'))
            self.assertTrue(json_data.__contains__('id_asset'))

        asset_uuid = json_data['asset_uuid']
        asset_id = json_data['id_asset']

        # Query asset information to make sure it was properly created
        payload = {'id_asset': asset_id, 'with_urls': True}
        response = self._request_with_token_auth(token=self.service_token, payload=payload,
                                                 endpoint='/api/service/assets')
        self.assertEqual(response.status_code, 200)

        json_data = response.json()
        self.assertTrue(len(json_data), 1)
        self.assertEqual(json_data[0]['id_asset'], asset_id)

        asset_infos_url = json_data[0]['asset_infos_url'] + '?asset_uuid=' + asset_uuid
        asset_url = json_data[0]['asset_url'] + '?asset_uuid=' + asset_uuid
        access_token = json_data[0]['access_token']

        # Get specific service information on that URL
        response = self._request_full_url_with_token_auth(token=self.service_token,
                                                          full_url=asset_infos_url + '&access_token=123124')
        self.assertEqual(response.status_code, 403, 'Forbidden - invalid token')

        response = self._request_full_url_with_token_auth(token=self.service_token,
                                                          full_url=asset_infos_url + '&access_token=' + access_token)
        self.assertEqual(response.status_code, 200, 'Service asset infos OK')
        json_data = response.json()
        self.assertTrue(json_data.__contains__('asset_uuid'))
        self.assertEqual(json_data['asset_uuid'], asset_uuid)

        # Change original file name with a POST query
        params = {'file_asset': {'asset_uuid': '1111111', 'access_token': access_token}}
        response = self._post_with_token(token=self.service_token, payload=params,
                                         endpoint=self.test_infos_endpoint)
        self.assertEqual(response.status_code, 403, 'Forbidden access to UUID')

        params = {'file_asset': {'asset_uuid': asset_uuid, 'asset_original_filename': 'testfile2',
                                 'access_token': access_token}}
        response = self._post_with_token(token=self.service_token, payload=params,
                                         endpoint=self.test_infos_endpoint)
        self.assertEqual(response.status_code, 200, 'Original file name changed')
        self.assertEqual(response.json()['asset_original_filename'], 'testfile2')

        # Try to download that file now from the file URL
        response = self._request_full_url_with_token_auth(token=self.service_token,
                                                          full_url=asset_url + '&access_token=123124')
        self.assertEqual(response.status_code, 403, 'Forbidden access with invalid token')

        request_headers = {'Authorization': 'OpenTera ' + self.service_token}
        response = get(url=asset_url + '&access_token=' + access_token, headers=request_headers, verify=False,
                       stream=True)
        self.assertEqual(response.status_code, 200, 'Downloading file')
        with open('testfile2', 'wb') as download_file:
            for chunk in response.iter_content(chunk_size=4096):
                download_file.write(chunk)

        import filecmp
        self.assertTrue(filecmp.cmp('testfile', 'testfile2'))
        os.remove('testfile2')

        # Delete asset from service
        response = self._delete_with_token_plus(token=self.service_token, payload={'uuid': asset_uuid,
                                                                                   'access_token': 123})
        self.assertEqual(response.status_code, 403, 'Forbidden access')

        response = self._delete_with_token_plus(token=self.service_token,
                                                payload={'uuid': asset_uuid, 'access_token': access_token})
        self.assertEqual(response.status_code, 200, 'Delete OK')

    def test_multiple_queries_as_post(self):
        # Create 3 assets
        asset_uuids = []
        # 1K data
        import io
        for i in range(3):
            f = io.BytesIO(os.urandom(1024 * 1))

            file_asset = {'id_session': 5,
                          'asset_name': 'Test Asset #' + str(i),
                          'asset_type': 'application/octet-stream'
                          }

            files = {'file': ('testfile', f, 'application/octet-stream',
                              {'Content-Length': 1024}),
                     'file_asset': (None, json.dumps(file_asset), 'application/json')}
            response = self._post_file_with_token(self.user_token, files=files)
            self.assertEqual(response.status_code, 200, 'Asset post OK')
            json_data = response.json()
            self.assertTrue(json_data.__contains__('asset_uuid'))
            asset_uuids.append(json_data['asset_uuid'])

        # Get access token
        payload = {'id_session': 5, 'with_urls': True}
        response = self._request_with_http_auth(username='admin', password='admin', payload=payload,
                                                endpoint='/api/user/assets')
        self.assertEqual(response.status_code, 200)

        json_data = response.json()
        self.assertEqual(len(json_data), 3)

        # Try to post to query assets
        params = {'assets': [{'access_token': json_data[0]['access_token'],
                              'asset_uuid': 'xxxxxxx'}]}
        response = self._post_with_token(token=self.user_token, payload=params,
                                         endpoint=self.test_infos_endpoint)
        self.assertEqual(response.status_code, 403, 'At least one bad asset in the query')

        assets = []
        for asset in json_data:
            assets.append({'asset_uuid': asset['asset_uuid'], 'access_token': asset['access_token']})
        params = {'assets': assets}
        response = self._post_with_token(token=self.user_token, payload=params,
                                         endpoint=self.test_infos_endpoint)
        self.assertEqual(response.status_code, 200, 'Asset query is fine')
        json_data = response.json()
        self.assertEqual(len(json_data), 3)

        # Delete created assets
        for asset in assets:
            response = self._delete_with_token_plus(token=self.user_token, payload={'uuid': asset['asset_uuid'],
                                                                                    'access_token':
                                                                                        asset['access_token']})
            self.assertEqual(response.status_code, 200, 'Delete OK')
