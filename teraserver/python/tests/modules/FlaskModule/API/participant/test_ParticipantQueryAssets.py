from typing import List
from BaseParticipantAPITest import BaseParticipantAPITest
from opentera.db.models.TeraAsset import TeraAsset
from opentera.db.models.TeraParticipant import TeraParticipant
from opentera.db.models.TeraSession import TeraSession


class ParticipantQueryAssetsTest(BaseParticipantAPITest):
    login_endpoint = '/api/participant/login'
    test_endpoint = '/api/participant/assets'
    participant_static_token = None
    participant_dynamic_token = None

    def setUp(self):
        super().setUp()
        with self._flask_app.app_context():
            # Get participant static token
            response = self._get_with_participant_http_auth(self.test_client, username='participant1',
                                                            password='opentera', endpoint=self.login_endpoint)
            self.assertEqual(200, response.status_code)
            self.assertTrue('participant_token' in response.json)
            self.participant_dynamic_token = response.json['participant_token']
            self.assertTrue('base_token' in response.json)
            self.participant_static_token = response.json['base_token']

    def tearDown(self):
        super().tearDown()

    def test_query_invalid_http_auth(self):
        with self._flask_app.app_context():
            response = self._get_with_participant_http_auth(self.test_client, username='invalid', password='invalid')
            self.assertEqual(401, response.status_code)

    def test_query_invalid_token_auth(self):
        with self._flask_app.app_context():
            response = self._get_with_participant_token_auth(self.test_client, token='invalid')
            self.assertEqual(401, response.status_code)

    def test_static_token(self):
        with self._flask_app.app_context():
            params = {'with_urls': True}
            response = self._get_with_participant_token_auth(self.test_client,
                                                             token=self.participant_static_token, params=params)
            self.assertEqual(403, response.status_code)

    def test_static_token_forbidden_id(self):
        with self._flask_app.app_context():
            params = {'id_asset': 10, 'with_urls': True}
            response = self._get_with_participant_token_auth(self.test_client,
                                                             token=self.participant_static_token, params=params)
            self.assertEqual(200, response.status_code)
            self.assertEqual(0, len(response.json))

    def test_query_assets_get_id(self):
        with self._flask_app.app_context():
            params = {'id_asset': 1, 'with_urls': True}
            response = self._get_with_participant_token_auth(self.test_client,
                                                             token=self.participant_dynamic_token, params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(len(response.json), 1)
            self._checkJson(json_data=response.json[0])

    def test_query_assets_get_id_forbidden(self):
        with self._flask_app.app_context():
            params = {'id_asset': 2}
            response = self._get_with_participant_token_auth(self.test_client,
                                                             token=self.participant_dynamic_token, params=params)
            self.assertEqual(200, response.status_code)
            self.assertEqual(len(response.json), 0)

    def test_query_assets_get_uuid(self):
        with self._flask_app.app_context():
            params = {'id_asset': 1}

            response = self._get_with_participant_token_auth(self.test_client,
                                                             token=self.participant_dynamic_token, params=params)
            self.assertEqual(200, response.status_code)
            self.assertEqual(len(response.json), 1)
            asset_uuid = response.json[0]['asset_uuid']

            params = {'asset_uuid': asset_uuid}

            response = self._get_with_participant_token_auth(self.test_client,
                                                             token=self.participant_dynamic_token, params=params)

            self.assertEqual(200, response.status_code)
            self.assertEqual(len(response.json), 1)
            self._checkJson(json_data=response.json[0], minimal=True)

    def test_query_assets_get_uuid_forbidden(self):
        with self._flask_app.app_context():
            asset = TeraAsset.query.filter_by(id_asset=2).first()
            self.assertIsNotNone(asset)
            params = {'asset_uuid': asset.asset_uuid}
            response = self._get_with_participant_token_auth(self.test_client, token=self.participant_dynamic_token,
                                                             params=params)
            self.assertEqual(200, response.status_code)
            self.assertEqual(len(response.json), 0)

    def test_query_assets_all(self):
        with self._flask_app.app_context():
            response = self._get_with_participant_token_auth(self.test_client, token=self.participant_dynamic_token)
            self.assertEqual(200, response.status_code)
            self.assertEqual(len(response.json), 1)
            for asset_info in response.json:
                self._checkJson(json_data=asset_info, minimal=True)

    def test_query_assets_all_token_only(self):
        with self._flask_app.app_context():
            params = {'with_only_token': True}
            response = self._get_with_participant_token_auth(self.test_client, token=self.participant_dynamic_token,
                                                             params=params)
            self.assertEqual(200, response.status_code)
            self.assertEqual(len(response.json), 1)
            for data_item in response.json:
                self.assertFalse(data_item.__contains__("asset_name"))
                self.assertTrue(data_item.__contains__("asset_uuid"))
                self.assertTrue(data_item.__contains__("access_token"))

    def test_get_endpoint_with_token_auth_with_forbidden_id_session(self):
        with self._flask_app.app_context():
            participants: List[TeraParticipant] = TeraParticipant.query.all()

            for participant in participants:
                for session in TeraSession.query.all():
                    params = {
                        'id_session': session.id_session,
                        'with_urls': True
                    }

                    if participant.participant_token:
                        if session.id_creator_participant != participant.id_participant:
                            response = self._get_with_participant_token_auth(self.test_client,
                                                                             token=participant.participant_token,
                                                                             params=params)
                            self.assertEqual(403, response.status_code)

    def test_get_endpoint_with_token_auth_with_session_id(self):
        with self._flask_app.app_context():
            participants: List[TeraParticipant] = TeraParticipant.query.all()

            for participant in participants:
                for session in TeraSession.query.all():
                    params = {
                        'id_session': session.id_session,
                        'with_urls': True
                    }

                    if participant.participant_token:
                        if session.id_creator_participant == participant.id_participant:
                            response = self._get_with_participant_token_auth(self.test_client,
                                                                             token=participant.participant_token,
                                                                             params=params)
                            self.assertEqual(200, response.status_code)

                            assets_ids = [asset.id_asset for asset in
                                          TeraAsset.get_assets_for_session(session.id_session)
                                          if asset.id_participant == participant.id_participant]
                            for asset_json in response.json:
                                self.assertTrue(asset_json['id_asset'] in assets_ids)
                                self._checkJson(asset_json, minimal=True)  # Participant with token = never return url
                                assets_ids.remove(asset_json['id_asset'])
                            self.assertFalse(assets_ids)

    def test_get_endpoint_with_login_with_session_id(self):
        with self._flask_app.app_context():
            participants: List[TeraParticipant] = TeraParticipant.query.all()

            for participant in participants:
                for session in TeraSession.query.all():
                    params = {
                        'id_session': session.id_session,
                        'with_urls': True
                    }

                    if participant.participant_login_enabled:
                        if session.id_creator_participant == participant.id_participant:
                            response = self._get_with_participant_http_auth(self.test_client,
                                                                            username=participant.participant_username,
                                                                            password='opentera', params=params)
                            self.assertEqual(200, response.status_code)

                            assets_ids = [asset.id_asset for asset in
                                          TeraAsset.get_assets_for_session(session.id_session)
                                          if asset.id_participant == participant.id_participant]
                            for asset_json in response.json:
                                self.assertTrue(asset_json['id_asset'] in assets_ids)
                                self._checkJson(asset_json, minimal=False)  # Full infos
                                assets_ids.remove(asset_json['id_asset'])
                            self.assertFalse(assets_ids)

    def _checkJson(self, json_data, minimal=False):
        self.assertGreater(len(json_data), 0)
        self.assertTrue(json_data.__contains__('id_asset'))
        self.assertTrue(json_data.__contains__('id_session'))
        self.assertTrue(json_data.__contains__('id_device'))
        self.assertTrue(json_data.__contains__('id_participant'))
        self.assertTrue(json_data.__contains__('id_user'))
        self.assertTrue(json_data.__contains__('id_service'))
        self.assertTrue(json_data.__contains__('asset_name'))
        self.assertTrue(json_data.__contains__('asset_uuid'))
        self.assertTrue(json_data.__contains__('asset_service_uuid'))
        self.assertTrue(json_data.__contains__('asset_type'))
        self.assertTrue(json_data.__contains__('asset_datetime'))
        if not minimal:
            self.assertTrue(json_data.__contains__('asset_infos_url'))
            self.assertTrue(json_data.__contains__('asset_url'))
            self.assertTrue(json_data.__contains__('access_token'))
        else:
            self.assertFalse(json_data.__contains__('asset_infos_url'))
            self.assertFalse(json_data.__contains__('asset_url'))
            self.assertFalse(json_data.__contains__('access_token'))
