import os
import io
import hashlib
import json
from tests.services.FileTransferService.BaseFileTransferServiceAPITest import BaseFileTransferServiceAPITest
from opentera.db.models.TeraUser import TeraUser
from opentera.db.models.TeraParticipant import TeraParticipant
from opentera.db.models.TeraDevice import TeraDevice
from opentera.db.models.TeraService import TeraService
from opentera.db.models.TeraSession import TeraSession
from opentera.db.models.TeraAsset import TeraAsset
from opentera.services.ServiceAccessManager import ServiceAccessManager
from services.FileTransferService.libfiletransferservice.db.models.AssetFileData import AssetFileData


class FileTransferAssetFileAndInfosTest(BaseFileTransferServiceAPITest):

    test_endpoint = '/api/file/assets/infos'
    asset_endpoint = '/api/file/assets'

    def setUp(self):
        super().setUp()
        with self.app_context():
            self.user_token = TeraUser.get_user_by_username('admin').get_token(ServiceAccessManager.api_user_token_key)
            self.device_token = TeraDevice.get_device_by_id(1).device_token
            self.participant_static_token = TeraParticipant.get_participant_by_id(1).participant_token
            self.participant_dynamic_token = TeraParticipant.get_participant_by_id(1).dynamic_token(
                ServiceAccessManager.api_participant_token_key)
            self.service_token = TeraService.get_service_by_key('FileTransferService').get_token(
                ServiceAccessManager.api_service_token_key)

        # Create test file to stream
        self.test_file_size = 1024 * 1024 * 100
        f = open('testfile', 'wb')
        f.write(os.urandom(self.test_file_size))
        f.close()

    def tearDown(self):
        super().tearDown()
        if os.path.exists('testfile'):
            os.remove('testfile')

    def test_get_endpoint_with_invalid_token(self):
        with self.app_context():
            response = self._get_with_token_auth(self.test_client, token="invalid")
            self.assertEqual(403, response.status_code)

    def test_post_endpoint_with_invalid_token(self):
        with self.app_context():
            response = self._post_with_token_auth(self.test_client, token="invalid")
            self.assertEqual(403, response.status_code)

    def test_delete_endpoint_with_invalid_token(self):
        with self.app_context():
            response = self._delete_with_token_auth(self.test_client, token="invalid")
            self.assertEqual(405, response.status_code)

    def test_get_endpoint_with_user_admin_token_no_params(self):
        with self.app_context():
            user: TeraUser = TeraUser.get_user_by_username('admin')
            self.assertIsNotNone(user)
            admin_token = user.get_token(ServiceAccessManager.api_user_token_key)
            self.assertGreater(len(admin_token), 0)
            response = self._get_with_token_auth(self.test_client, token=admin_token)
            self.assertEqual(400, response.status_code)

    def test_get_endpoint_with_participant_static_token_no_params(self):
        with self.app_context():
            for participant in TeraParticipant.query.all():
                self.assertIsNotNone(participant)
                if participant.participant_enabled and participant.participant_token:
                    self.assertIsNotNone(participant.participant_token)
                    self.assertGreater(len(participant.participant_token), 0)
                    response = self._get_with_token_auth(self.test_client, token=participant.participant_token)
                    self.assertEqual(403, response.status_code)

    def test_get_endpoint_with_participant_dynamic_token_no_params(self):
        with self.app_context():
            for participant in TeraParticipant.query.all():
                self.assertIsNotNone(participant)
                if participant.participant_enabled and participant.participant_login_enabled:
                    participant_token = participant.dynamic_token(ServiceAccessManager.api_participant_token_key)
                    self.assertIsNotNone(participant_token)
                    self.assertGreater(len(participant_token), 0)
                    response = self._get_with_token_auth(self.test_client, token=participant_token)
                    self.assertEqual(400, response.status_code)

    def test_get_endpoint_with_device_static_token_no_params(self):
        with self.app_context():
            for device in TeraDevice.query.all():
                self.assertIsNotNone(device)
                if device.device_enabled:
                    device_token = device.device_token
                    self.assertIsNotNone(device_token)
                    self.assertGreater(len(device_token), 0)
                    response = self._get_with_token_auth(self.test_client, token=device_token)
                    self.assertEqual(400, response.status_code)

    def test_get_endpoint_with_service_token_bad_param(self):
        with self.app_context():
            for service in TeraService.query.all():
                service_token = service.get_token(ServiceAccessManager.api_service_token_key)
                params = {'id_invalid': 1}
                self.assertIsNotNone(service)
                self.assertIsNotNone(service_token)
                response = self._get_with_token_auth(self.test_client, token=service_token, params=params)
                self.assertEqual(400, response.status_code)

    @staticmethod
    def calc_md5(data):
        hash_md5 = hashlib.md5()
        for chunk in iter(lambda: data.read(4096), b""):
            hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def delete_asset(self, asset_uuid: str):
        asset = AssetFileData.get_asset_for_uuid(asset_uuid)
        if asset:
            asset.delete_file_asset(self._service.flask_app.config['UPLOAD_FOLDER'])
            return True
        return False

    def test_full_as_user(self):
        with self.app_context():
            file_asset = {}
            with open('testfile', 'rb') as f:
                files = {'file': (f, 'testfile'),
                         'file_asset': json.dumps(file_asset)}

                response = self._post_file_with_token_auth(self.test_client, token=self.user_token, files=files,
                                                           endpoint=self.asset_endpoint)
                self.assertEqual(400, response.status_code, 'Missing infos in file_asset')

            file_asset['id_session'] = 100
            file_asset['asset_name'] = "Test Asset"
            file_asset['asset_type'] = 'application/octet-stream'
            with open('testfile', 'rb') as f:
                files = {'file': (f, 'testfile'),
                         'file_asset': json.dumps(file_asset)}

                response = self._post_file_with_token_auth(self.test_client, token=self.user_token, files=files,
                                                           endpoint=self.asset_endpoint)
                self.assertEqual(403, response.status_code, 'Forbidden access to session')

            service: TeraService = TeraService.get_service_by_key('FileTransferService')
            service_ses = TeraSession.query.filter(TeraSession.id_creator_service == service.id_service).first()
            file_asset['id_session'] = service_ses.id_session

            with open('testfile', 'rb') as f:
                files = {'file': (f, 'testfile'),
                         'file_asset': json.dumps(file_asset)}

                response = self._post_file_with_token_auth(self.test_client, token=self.user_token, files=files,
                                                           endpoint=self.asset_endpoint)
                self.assertEqual(200, response.status_code, 'Asset post OK')
                self.assertTrue(response.json.__contains__('asset_uuid'))
                self.assertTrue(response.json.__contains__('id_asset'))

            asset_uuid = response.json['asset_uuid']
            asset_id = response.json['id_asset']

            # Query asset information to make sure it was properly created
            params = {'id_asset': asset_id, 'with_urls': True}

            response = self._get_with_token_auth(self.test_client, token=self.user_token, params=params,
                                                 endpoint='/api/user/assets')
            self.assertEqual(200, response.status_code)
            self.assertTrue(len(response.json), 1)
            self.assertEqual(response.json[0]['id_asset'], asset_id)

            self.assertTrue('asset_infos_url' in response.json[0])
            self.assertTrue('asset_url' in response.json[0])
            self.assertTrue('access_token' in response.json[0])

            access_token = response.json[0]['access_token']

            # Get specific service information on that URL
            params = {'asset_uuid': asset_uuid}
            response = self._get_with_token_auth(self.test_client, token=self.user_token, params=params)
            self.assertEqual(400, response.status_code, 'Missing access token')
            params['access_token'] = 'invalid'
            response = self._get_with_token_auth(self.test_client, token=self.user_token, params=params)
            self.assertEqual(403, response.status_code, 'Forbidden - invalid token')

            params['access_token'] = access_token
            response = self._get_with_token_auth(self.test_client, token=self.user_token, params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.json.__contains__('asset_uuid'))
            self.assertEqual(response.json['asset_uuid'], asset_uuid)

            # Change original file name with a POST query
            json_data = {}
            response = self._post_with_token_auth(self.test_client, token=self.user_token, json=json_data)
            self.assertEqual(400, response.status_code, 'Missing file asset info')

            json_data = {'access_token': access_token}
            response = self._post_with_token_auth(self.test_client, token=self.user_token, json=json_data)
            self.assertEqual(400, response.status_code, 'Badly formatted request')

            json_data = {'file_asset': {}}
            response = self._post_with_token_auth(self.test_client, token=self.user_token, json=json_data)
            self.assertEqual(400, response.status_code, 'Missing asset UUID')

            json_data = {'file_asset': {'asset_uuid': '1111111', 'access_token': access_token}}
            response = self._post_with_token_auth(self.test_client, token=self.user_token, json=json_data)
            self.assertEqual(403, response.status_code, 'Forbidden access to UUID')
    
            json_data = {'file_asset': {'asset_uuid': asset_uuid, 'access_token': access_token}}
            response = self._post_with_token_auth(self.test_client, token=self.user_token, json=json_data)
            self.assertEqual(400, response.status_code, 'No file name')

            json_data = {'file_asset': {'asset_uuid': asset_uuid, 'asset_original_filename': 'testfile2',
                                        'access_token': access_token}}
            response = self._post_with_token_auth(self.test_client, token=self.user_token, json=json_data)
            self.assertEqual(200, response.status_code, 'Original file name changed')
            self.assertEqual(response.json['asset_original_filename'], 'testfile2')
    
            # Try to download that file now from the file URL
            params = {'asset_uuid': asset_uuid}
            response = self._get_with_token_auth(self.test_client, token=self.user_token, params=params,
                                                 endpoint=self.asset_endpoint)
            self.assertEqual(400, response.status_code, 'Missing access token')

            params = {'asset_uuid': asset_uuid, 'access_token': 'invalid'}
            response = self._get_with_token_auth(self.test_client, token=self.user_token, params=params,
                                                 endpoint=self.asset_endpoint)

            self.assertEqual(403, response.status_code, 'Forbidden access with invalid token')

            params = {'asset_uuid': asset_uuid, 'access_token': access_token}
            response = self._get_with_token_auth(self.test_client, token=self.user_token, params=params,
                                                 endpoint=self.asset_endpoint)

            self.assertEqual(200, response.status_code, 'Forbidden access with invalid token')
            self.assertEqual(self.test_file_size, response.content_length)
            self.assertEqual('application/octet-stream', response.content_type)
            received_file = io.BytesIO(response.data)
            local_file = io.FileIO('testfile')
            md5_received_file = self.calc_md5(received_file)
            md5_local_file = self.calc_md5(local_file)
            self.assertEqual(md5_received_file, md5_local_file)

            # Delete asset from service as user
            params = {}
            response = self._delete_with_token_auth(self.test_client, token=self.user_token, params=params,
                                                    endpoint=self.asset_endpoint)

            self.assertEqual(400, response.status_code, 'Missing access token and uuid')

            params = {'uuid': asset_uuid}
            response = self._delete_with_token_auth(self.test_client, token=self.user_token, params=params,
                                                    endpoint=self.asset_endpoint)

            self.assertEqual(400, response.status_code, 'Missing access token')

            params = {'access_token': access_token}
            response = self._delete_with_token_auth(self.test_client, token=self.user_token, params=params,
                                                    endpoint=self.asset_endpoint)

            self.assertEqual(400, response.status_code, 'Missing asset_uuid')

            params = {'uuid': asset_uuid, 'access_token': '1234'}
            response = self._delete_with_token_auth(self.test_client, token=self.user_token, params=params,
                                                    endpoint=self.asset_endpoint)

            self.assertEqual(403, response.status_code, 'Invalid access_token')

            params = {'uuid': asset_uuid, 'access_token': access_token}
            response = self._delete_with_token_auth(self.test_client, token=self.user_token, params=params,
                                                    endpoint=self.asset_endpoint)

            self.assertEqual(200, response.status_code, 'Delete OK')
            self.assertTrue(self.delete_asset(asset_uuid))

    def test_full_as_device(self):
        with self.app_context():
            file_asset = dict()
            file_asset['id_session'] = 100
            file_asset['asset_name'] = "Test Asset"
            file_asset['asset_type'] = 'application/octet-stream'
            with open('testfile', 'rb') as f:
                files = {'file': (f, 'testfile'),
                         'file_asset': json.dumps(file_asset)}
                
                response = self._post_file_with_token_auth(self.test_client, self.device_token, files=files,
                                                           endpoint=self.asset_endpoint)

                self.assertEqual(403, response.status_code, 'Forbidden access to session')

            file_asset['id_session'] = 9
            with open('testfile', 'rb') as f:
                files = {'file': (f, 'testfile'),
                         'file_asset': json.dumps(file_asset)}

                response = self._post_file_with_token_auth(self.test_client, self.device_token, files=files,
                                                           endpoint=self.asset_endpoint)

                self.assertEqual(200, response.status_code, 'Asset post OK')

            self.assertTrue(response.json.__contains__('asset_uuid'))
            self.assertTrue(response.json.__contains__('id_asset'))

            asset_uuid = response.json['asset_uuid']
            asset_id = response.json['id_asset']

            # Query asset information to make sure it was properly created
            params = {'id_asset': asset_id, 'with_urls': True}
            response = self._get_with_token_auth(self.test_client, token=self.device_token, params=params,
                                                 endpoint='api/device/assets')
            self.assertEqual(200, response.status_code)
            self.assertEqual(len(response.json), 1)
            self.assertEqual(response.json[0]['id_asset'], asset_id)
            access_token = response.json[0]['access_token']

            # Get specific service information on that URL
            params = {'asset_uuid': asset_uuid, 'access_token': '1234556'}
            response = self._get_with_token_auth(self.test_client, token=self.device_token, params=params)
            self.assertEqual(403, response.status_code, 'Forbidden - invalid token')
            params['access_token'] = access_token

            response = self._get_with_token_auth(self.test_client, token=self.device_token, params=params)
            self.assertEqual(200, response.status_code, 'Service asset infos OK')
            self.assertTrue(response.json.__contains__('asset_uuid'))
            self.assertEqual(response.json['asset_uuid'], asset_uuid)

            # Change original file name with a POST query
            json_data = {}
            response = self._post_with_token_auth(self.test_client, token=self.device_token, json=json_data)
            self.assertEqual(400, response.status_code, 'Missing file asset info')

            json_data = {'access_token': access_token}
            response = self._post_with_token_auth(self.test_client, token=self.device_token, json=json_data)
            self.assertEqual(400, response.status_code, 'Badly formatted request')

            json_data = {'file_asset': {}}
            response = self._post_with_token_auth(self.test_client, token=self.device_token, json=json_data)
            self.assertEqual(400, response.status_code, 'Missing asset UUID')

            json_data = {'file_asset': {'asset_uuid': '1111111', 'access_token': access_token}}
            response = self._post_with_token_auth(self.test_client, token=self.device_token, json=json_data)
            self.assertEqual(403, response.status_code, 'Forbidden access to UUID')

            json_data = {'file_asset': {'asset_uuid': asset_uuid, 'access_token': access_token}}
            response = self._post_with_token_auth(self.test_client, token=self.device_token, json=json_data)
            self.assertEqual(400, response.status_code, 'No file name')

            json_data = {'file_asset': {'asset_uuid': asset_uuid, 'asset_original_filename': 'testfile2',
                                        'access_token': access_token}}
            response = self._post_with_token_auth(self.test_client, token=self.device_token, json=json_data)
            self.assertEqual(200, response.status_code, 'Original file name changed')
            self.assertEqual(response.json['asset_original_filename'], 'testfile2')

            # Try to download that file now from the file URL
            params = {'asset_uuid': asset_uuid}
            response = self._get_with_token_auth(self.test_client, token=self.device_token, params=params,
                                                 endpoint=self.asset_endpoint)
            self.assertEqual(400, response.status_code, 'Missing access token')

            params = {'asset_uuid': asset_uuid, 'access_token': 'invalid'}
            response = self._get_with_token_auth(self.test_client, token=self.device_token, params=params,
                                                 endpoint=self.asset_endpoint)

            self.assertEqual(403, response.status_code, 'Forbidden access with invalid token')

            params = {'asset_uuid': asset_uuid, 'access_token': access_token}
            response = self._get_with_token_auth(self.test_client, token=self.device_token, params=params,
                                                 endpoint=self.asset_endpoint)

            self.assertEqual(200, response.status_code, 'Forbidden access with invalid token')
            self.assertEqual(self.test_file_size, response.content_length)
            self.assertEqual('application/octet-stream', response.content_type)
            received_file = io.BytesIO(response.data)
            local_file = io.FileIO('testfile')
            md5_received_file = self.calc_md5(received_file)
            md5_local_file = self.calc_md5(local_file)
            self.assertEqual(md5_received_file, md5_local_file)

            # Delete asset from service as user
            params = {}
            response = self._delete_with_token_auth(self.test_client, token=self.device_token, params=params,
                                                    endpoint=self.asset_endpoint)

            self.assertEqual(400, response.status_code, 'Missing access token and uuid')

            params = {'uuid': asset_uuid}
            response = self._delete_with_token_auth(self.test_client, token=self.device_token, params=params,
                                                    endpoint=self.asset_endpoint)

            self.assertEqual(400, response.status_code, 'Missing access token')

            params = {'access_token': access_token}
            response = self._delete_with_token_auth(self.test_client, token=self.device_token, params=params,
                                                    endpoint=self.asset_endpoint)

            self.assertEqual(400, response.status_code, 'Missing asset_uuid')

            params = {'uuid': asset_uuid, 'access_token': '1234'}
            response = self._delete_with_token_auth(self.test_client, token=self.device_token, params=params,
                                                    endpoint=self.asset_endpoint)

            self.assertEqual(403, response.status_code, 'Invalid access_token')

            params = {'uuid': asset_uuid, 'access_token': access_token}
            response = self._delete_with_token_auth(self.test_client, token=self.device_token, params=params,
                                                    endpoint=self.asset_endpoint)

            self.assertEqual(200, response.status_code, 'Delete OK')
            self.assertTrue(self.delete_asset(asset_uuid))

    def test_full_as_dynamic_participant(self):
        with self.app_context():
            file_asset = dict()
            file_asset['id_session'] = 100
            file_asset['asset_name'] = "Test Asset"
            file_asset['asset_type'] = 'application/octet-stream'
            with open('testfile', 'rb') as f:
                files = {'file': (f, 'testfile'),
                         'file_asset': json.dumps(file_asset)}

                response = self._post_file_with_token_auth(self.test_client, self.participant_dynamic_token,
                                                           files=files,
                                                           endpoint=self.asset_endpoint)

                self.assertEqual(403, response.status_code, 'Forbidden access to session')

            file_asset['id_session'] = 9
            with open('testfile', 'rb') as f:
                files = {'file': (f, 'testfile'),
                         'file_asset': json.dumps(file_asset)}

                response = self._post_file_with_token_auth(self.test_client, self.participant_dynamic_token,
                                                           files=files,
                                                           endpoint=self.asset_endpoint)

                self.assertEqual(200, response.status_code, 'Asset post OK')

            self.assertTrue(response.json.__contains__('asset_uuid'))
            self.assertTrue(response.json.__contains__('id_asset'))

            asset_uuid = response.json['asset_uuid']
            asset_id = response.json['id_asset']

            # Query asset information to make sure it was properly created
            params = {'id_asset': asset_id, 'with_urls': True}
            response = self._get_with_token_auth(self.test_client, token=self.participant_dynamic_token, params=params,
                                                 endpoint='api/participant/assets')
            self.assertEqual(200, response.status_code)
            self.assertEqual(len(response.json), 1)
            self.assertEqual(response.json[0]['id_asset'], asset_id)
            access_token = response.json[0]['access_token']

            # Get specific service information on that URL
            params = {'asset_uuid': asset_uuid, 'access_token': '1234556'}
            response = self._get_with_token_auth(self.test_client, token=self.participant_dynamic_token, params=params)
            self.assertEqual(403, response.status_code, 'Forbidden - invalid token')
            params['access_token'] = access_token

            response = self._get_with_token_auth(self.test_client, token=self.participant_dynamic_token, params=params)
            self.assertEqual(200, response.status_code, 'Service asset infos OK')
            self.assertTrue(response.json.__contains__('asset_uuid'))
            self.assertEqual(response.json['asset_uuid'], asset_uuid)

            # Change original file name with a POST query
            json_data = {}
            response = self._post_with_token_auth(self.test_client, token=self.participant_dynamic_token,
                                                  json=json_data)
            self.assertEqual(400, response.status_code, 'Missing file asset info')

            json_data = {'access_token': access_token}
            response = self._post_with_token_auth(self.test_client, token=self.participant_dynamic_token,
                                                  json=json_data)
            self.assertEqual(400, response.status_code, 'Badly formatted request')

            json_data = {'file_asset': {}}
            response = self._post_with_token_auth(self.test_client, token=self.participant_dynamic_token,
                                                  json=json_data)
            self.assertEqual(400, response.status_code, 'Missing asset UUID')

            json_data = {'file_asset': {'asset_uuid': '1111111', 'access_token': access_token}}
            response = self._post_with_token_auth(self.test_client, token=self.participant_dynamic_token,
                                                  json=json_data)
            self.assertEqual(403, response.status_code, 'Forbidden access to UUID')

            json_data = {'file_asset': {'asset_uuid': asset_uuid, 'access_token': access_token}}
            response = self._post_with_token_auth(self.test_client, token=self.participant_dynamic_token,
                                                  json=json_data)
            self.assertEqual(400, response.status_code, 'No file name')

            json_data = {'file_asset': {'asset_uuid': asset_uuid, 'asset_original_filename': 'testfile2',
                                        'access_token': access_token}}
            response = self._post_with_token_auth(self.test_client, token=self.participant_dynamic_token,
                                                  json=json_data)
            self.assertEqual(200, response.status_code, 'Original file name changed')
            self.assertEqual(response.json['asset_original_filename'], 'testfile2')

            # Try to download that file now from the file URL
            params = {'asset_uuid': asset_uuid}
            response = self._get_with_token_auth(self.test_client, token=self.participant_dynamic_token, params=params,
                                                 endpoint=self.asset_endpoint)
            self.assertEqual(400, response.status_code, 'Missing access token')

            params = {'asset_uuid': asset_uuid, 'access_token': 'invalid'}
            response = self._get_with_token_auth(self.test_client, token=self.participant_dynamic_token, params=params,
                                                 endpoint=self.asset_endpoint)

            self.assertEqual(403, response.status_code, 'Forbidden access with invalid token')

            params = {'asset_uuid': asset_uuid, 'access_token': access_token}
            response = self._get_with_token_auth(self.test_client, token=self.participant_dynamic_token, params=params,
                                                 endpoint=self.asset_endpoint)

            self.assertEqual(200, response.status_code, 'Forbidden access with invalid token')
            self.assertEqual(self.test_file_size, response.content_length)
            self.assertEqual('application/octet-stream', response.content_type)
            received_file = io.BytesIO(response.data)
            local_file = io.FileIO('testfile')
            md5_received_file = self.calc_md5(received_file)
            md5_local_file = self.calc_md5(local_file)
            self.assertEqual(md5_received_file, md5_local_file)

            # Delete asset from service as user
            params = {}
            response = self._delete_with_token_auth(self.test_client, token=self.participant_dynamic_token,
                                                    params=params,
                                                    endpoint=self.asset_endpoint)

            self.assertEqual(400, response.status_code, 'Missing access token and uuid')

            params = {'uuid': asset_uuid}
            response = self._delete_with_token_auth(self.test_client, token=self.participant_dynamic_token,
                                                    params=params,
                                                    endpoint=self.asset_endpoint)

            self.assertEqual(400, response.status_code, 'Missing access token')

            params = {'access_token': access_token}
            response = self._delete_with_token_auth(self.test_client, token=self.participant_dynamic_token,
                                                    params=params,
                                                    endpoint=self.asset_endpoint)

            self.assertEqual(400, response.status_code, 'Missing asset_uuid')

            params = {'uuid': asset_uuid, 'access_token': '1234'}
            response = self._delete_with_token_auth(self.test_client, token=self.participant_dynamic_token,
                                                    params=params,
                                                    endpoint=self.asset_endpoint)

            self.assertEqual(403, response.status_code, 'Invalid access_token')

            params = {'uuid': asset_uuid, 'access_token': access_token}
            response = self._delete_with_token_auth(self.test_client, token=self.participant_dynamic_token,
                                                    params=params,
                                                    endpoint=self.asset_endpoint)

            self.assertEqual(200, response.status_code, 'Delete OK')
            self.assertTrue(self.delete_asset(asset_uuid))

    def test_full_as_static_participant(self):
        with self.app_context():
            file_asset = dict()
            file_asset['id_session'] = 9
            file_asset['asset_name'] = "Test Asset"
            file_asset['asset_type'] = 'application/octet-stream'
            with open('testfile', 'rb') as f:
                files = {'file': (f, 'testfile'),
                         'file_asset': json.dumps(file_asset)}

                response = self._post_file_with_token_auth(self.test_client, self.participant_static_token,
                                                           files=files,
                                                           endpoint=self.asset_endpoint)

                self.assertEqual(200, response.status_code)

    def test_full_as_service(self):
        with self.app_context():
            file_asset = dict()
            file_asset['id_session'] = 100
            file_asset['asset_name'] = "Test Asset"
            file_asset['asset_type'] = 'application/octet-stream'
            with open('testfile', 'rb') as f:
                files = {'file': (f, 'testfile'),
                         'file_asset': json.dumps(file_asset)}

                response = self._post_file_with_token_auth(self.test_client, self.service_token, files=files,
                                                           endpoint=self.asset_endpoint)

                self.assertEqual(403, response.status_code, 'Forbidden access to session')

            service: TeraService = TeraService.get_service_by_key('FileTransferService')
            service_ses = TeraSession.query.filter(TeraSession.id_creator_service == service.id_service).first()
            file_asset['id_session'] = service_ses.id_session

            with open('testfile', 'rb') as f:
                files = {'file': (f, 'testfile'),
                         'file_asset': json.dumps(file_asset)}

                response = self._post_file_with_token_auth(self.test_client, self.service_token, files=files,
                                                           endpoint=self.asset_endpoint)

                self.assertEqual(400, response.status_code, 'Missing id_creator')

            file_asset['id_user'] = 2
            with open('testfile', 'rb') as f:
                files = {'file': (f, 'testfile'),
                         'file_asset': json.dumps(file_asset)}

                response = self._post_file_with_token_auth(self.test_client, self.service_token, files=files,
                                                           endpoint=self.asset_endpoint)

                self.assertEqual(200, response.status_code, 'Post OK')

            self.assertTrue(response.json.__contains__('asset_uuid'))
            self.assertTrue(response.json.__contains__('id_asset'))

            asset_uuid = response.json['asset_uuid']
            asset_id = response.json['id_asset']

            # Query asset information to make sure it was properly created
            params = {'id_asset': asset_id, 'with_urls': True}
            response = self._get_with_token_auth(self.test_client, token=self.service_token, params=params,
                                                 endpoint='api/service/assets')
            self.assertEqual(200, response.status_code)
            self.assertEqual(len(response.json), 1)
            self.assertEqual(response.json[0]['id_asset'], asset_id)
            access_token = response.json[0]['access_token']

            # Get specific service information on that URL
            params = {'asset_uuid': asset_uuid, 'access_token': '1234556'}
            response = self._get_with_token_auth(self.test_client, token=self.service_token, params=params)
            self.assertEqual(403, response.status_code, 'Forbidden - invalid token')
            params['access_token'] = access_token

            response = self._get_with_token_auth(self.test_client, token=self.service_token, params=params)
            self.assertEqual(200, response.status_code, 'Service asset infos OK')
            self.assertTrue(response.json.__contains__('asset_uuid'))
            self.assertEqual(response.json['asset_uuid'], asset_uuid)

            # Change original file name with a POST query
            json_data = {}
            response = self._post_with_token_auth(self.test_client, token=self.service_token,
                                                  json=json_data)
            self.assertEqual(400, response.status_code, 'Missing file asset info')

            json_data = {'access_token': access_token}
            response = self._post_with_token_auth(self.test_client, token=self.service_token,
                                                  json=json_data)
            self.assertEqual(400, response.status_code, 'Badly formatted request')

            json_data = {'file_asset': {}}
            response = self._post_with_token_auth(self.test_client, token=self.service_token,
                                                  json=json_data)
            self.assertEqual(400, response.status_code, 'Missing asset UUID')

            json_data = {'file_asset': {'asset_uuid': '1111111', 'access_token': access_token}}
            response = self._post_with_token_auth(self.test_client, token=self.service_token,
                                                  json=json_data)
            self.assertEqual(403, response.status_code, 'Forbidden access to UUID')

            json_data = {'file_asset': {'asset_uuid': asset_uuid, 'access_token': access_token}}
            response = self._post_with_token_auth(self.test_client, token=self.service_token,
                                                  json=json_data)
            self.assertEqual(400, response.status_code, 'No file name')

            json_data = {'file_asset': {'asset_uuid': asset_uuid, 'asset_original_filename': 'testfile2',
                                        'access_token': access_token}}
            response = self._post_with_token_auth(self.test_client, token=self.service_token,
                                                  json=json_data)
            self.assertEqual(200, response.status_code, 'Original file name changed')
            self.assertEqual(response.json['asset_original_filename'], 'testfile2')

            # Try to download that file now from the file URL
            params = {'asset_uuid': asset_uuid}
            response = self._get_with_token_auth(self.test_client, token=self.service_token, params=params,
                                                 endpoint=self.asset_endpoint)
            self.assertEqual(400, response.status_code, 'Missing access token')

            params = {'asset_uuid': asset_uuid, 'access_token': 'invalid'}
            response = self._get_with_token_auth(self.test_client, token=self.service_token, params=params,
                                                 endpoint=self.asset_endpoint)

            self.assertEqual(403, response.status_code, 'Forbidden access with invalid token')

            params = {'asset_uuid': asset_uuid, 'access_token': access_token}
            response = self._get_with_token_auth(self.test_client, token=self.service_token, params=params,
                                                 endpoint=self.asset_endpoint)

            self.assertEqual(200, response.status_code, 'Forbidden access with invalid token')
            self.assertEqual(self.test_file_size, response.content_length)
            self.assertEqual('application/octet-stream', response.content_type)
            received_file = io.BytesIO(response.data)
            local_file = io.FileIO('testfile')
            md5_received_file = self.calc_md5(received_file)
            md5_local_file = self.calc_md5(local_file)
            self.assertEqual(md5_received_file, md5_local_file)

            # Delete asset from service as user
            params = {}
            response = self._delete_with_token_auth(self.test_client, token=self.service_token,
                                                    params=params,
                                                    endpoint=self.asset_endpoint)

            self.assertEqual(400, response.status_code, 'Missing access token and uuid')

            params = {'uuid': asset_uuid}
            response = self._delete_with_token_auth(self.test_client, token=self.service_token,
                                                    params=params,
                                                    endpoint=self.asset_endpoint)

            self.assertEqual(400, response.status_code, 'Missing access token')

            params = {'access_token': access_token}
            response = self._delete_with_token_auth(self.test_client, token=self.service_token,
                                                    params=params,
                                                    endpoint=self.asset_endpoint)

            self.assertEqual(400, response.status_code, 'Missing asset_uuid')

            params = {'uuid': asset_uuid, 'access_token': '1234'}
            response = self._delete_with_token_auth(self.test_client, token=self.service_token,
                                                    params=params,
                                                    endpoint=self.asset_endpoint)

            self.assertEqual(403, response.status_code, 'Invalid access_token')

            params = {'uuid': asset_uuid, 'access_token': access_token}
            response = self._delete_with_token_auth(self.test_client, token=self.service_token,
                                                    params=params,
                                                    endpoint=self.asset_endpoint)

            self.assertEqual(200, response.status_code, 'Delete OK')
            self.assertTrue(self.delete_asset(asset_uuid))

    def test_multiple_queries_as_post(self):
        with self.app_context():
            # Create 3 assets
            asset_uuids = []
            # 1K data
            import io
            for i in range(3):
                f = io.BytesIO(os.urandom(1024 * 1))

                service: TeraService = TeraService.get_service_by_key('FileTransferService')
                service_ses = TeraSession.query.filter(TeraSession.id_creator_service == service.id_service).first()
                id_session = service_ses.id_session

                file_asset = {'id_session': id_session,
                              'asset_name': 'Test Asset #' + str(i),
                              'asset_type': 'application/octet-stream'
                              }

                files = {'file': (f, 'testfile'),
                         'file_asset': json.dumps(file_asset)}
                response = self._post_file_with_token_auth(self.test_client, token=self.user_token, files=files,
                                                           endpoint=self.asset_endpoint)
                self.assertEqual(200, response.status_code, 'Asset post OK')
                self.assertTrue(response.json.__contains__('asset_uuid'))
                asset_uuids.append(response.json['asset_uuid'])

            # Get access token
            params = {'id_session': id_session, 'with_urls': True}
            response = self._get_with_token_auth(self.test_client, token=self.user_token, params=params,
                                                 endpoint='/api/user/assets')
            self.assertEqual(200, response.status_code)

            target_count = len(TeraAsset.get_assets_for_session(id_session))

            self.assertEqual(len(response.json), target_count)
            assets = []
            for asset in response.json:
                assets.append({'asset_uuid': asset['asset_uuid'], 'access_token': asset['access_token']})

            # Try to post to query assets
            json_data = {'assets': [{'access_token': response.json[0]['access_token'],
                                     'asset_uuid': 'xxxxxxx'}]}
            response = self._post_with_token_auth(self.test_client, token=self.user_token, json=json_data)
            self.assertEqual(403, response.status_code, 'At least one bad asset in the query')

            json_data = {'assets': assets}
            response = self._post_with_token_auth(self.test_client, token=self.user_token, json=json_data)
            self.assertEqual(200, response.status_code, 'Asset query is fine')
            service_assets = (AssetFileData.query.filter(AssetFileData.asset_uuid.in_(
                [asset['asset_uuid'] for asset in assets])).all())
            service_assets_uuid = [asset.asset_uuid for asset in service_assets]
            self.assertEqual(len(response.json), len(service_assets))

            # Delete created assets
            for asset in assets:
                if asset['asset_uuid'] not in service_assets_uuid:
                    continue
                params = {'uuid': asset['asset_uuid'], 'access_token': asset['access_token']}
                response = self._delete_with_token_auth(self.test_client, token=self.user_token, params=params,
                                                        endpoint=self.asset_endpoint)
                self.assertEqual(200, response.status_code, 'Delete OK')
                self.assertTrue(self.delete_asset(asset['asset_uuid']))

    def test_get_endpoint_with_disabled_token(self):
        with self.app_context():
            login_response = self._get_with_user_http_auth(self.test_client, username='admin',
                                                           password='admin', endpoint=self.user_login_endpoint)
            self.assertEqual(200, login_response.status_code)
            token = login_response.json['user_token']

            logout_response = self._get_with_user_token_auth(self.test_client, token=token,
                                                             endpoint=self.user_logout_endpoint)
            self.assertEqual(200, logout_response.status_code)

            # Try to call endpoint with disabled token
            response = self._get_with_token_auth(self.test_client, token=token)
            self.assertEqual(403, response.status_code)
