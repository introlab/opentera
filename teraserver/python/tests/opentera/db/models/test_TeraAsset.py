import jwt

from opentera.db.models.TeraAsset import TeraAsset
from opentera.db.models.TeraSession import TeraSession
from opentera.db.models.TeraService import TeraService
from opentera.db.models.TeraDevice import TeraDevice
from opentera.db.models.TeraUser import TeraUser
from opentera.db.models.TeraParticipant import TeraParticipant
from tests.opentera.db.models.BaseModelsTest import BaseModelsTest
from sqlalchemy.exc import IntegrityError


class TeraAssetTest(BaseModelsTest):

    def test_defaults(self):
        with self._flask_app.app_context():
            for asset in TeraAsset.query.all():
                self.assertGreater(len(asset.asset_name), 0)
                self.assertIsNotNone(asset.asset_session)
                self.assertIsNotNone(asset.asset_service_uuid)
                self.assertIsNotNone(asset.asset_uuid)

    def test_json_full_and_minimal(self):
        with self._flask_app.app_context():
            assets = TeraAsset.query.all()
            self.assertGreater(len(assets), 0)
            for minimal in [False, True]:
                for asset in assets:
                    self.assertIsNotNone(asset)
                    json = asset.to_json(minimal=minimal)
                    self.assertNotEqual(None, json)

                    if not minimal:
                        # Full fields only
                        self.assertTrue('asset_service_owner_name' in json)
                        self.assertTrue('asset_session_name' in json)
                        if asset.id_device:
                            self.assertTrue('asset_device' in json)
                        if asset.id_user:
                            self.assertTrue('asset_user' in json)
                        if asset.id_participant:
                            self.assertTrue('asset_participant' in json)
                        if asset.id_service:
                            self.assertTrue('asset_service' in json)

                    # Minimal + full fields
                    self.assertTrue('id_asset' in json)
                    self.assertTrue('id_session' in json)
                    self.assertTrue('id_device' in json)
                    self.assertTrue('id_participant' in json)
                    self.assertTrue('id_user' in json)
                    self.assertTrue('id_service' in json)
                    self.assertTrue('asset_name' in json)
                    self.assertTrue('asset_uuid' in json)
                    self.assertTrue('asset_service_uuid' in json)
                    self.assertTrue('asset_type' in json)
                    self.assertTrue('asset_datetime' in json)

                    # Make sure deleted at field not there
                    self.assertFalse('deleted_at' in json)

    def test_from_json(self):
        with self._flask_app.app_context():
            for asset in TeraAsset.query.all():
                json = asset.to_json()
                new_asset = TeraAsset()
                new_asset.from_json(json)
                self.assertEqual(new_asset.asset_name, asset.asset_name)
                self.assertEqual(new_asset.asset_service_uuid, asset.asset_service_uuid)
                self.assertEqual(new_asset.asset_type, asset.asset_type)
                self.assertEqual(new_asset.asset_uuid, asset.asset_uuid)
                self.assertEqual(new_asset.id_asset, asset.id_asset)
                self.assertEqual(new_asset.id_device, asset.id_device)
                self.assertEqual(new_asset.id_session, asset.id_session)

    def test_ids_uuids_get_methods(self):
        with self._flask_app.app_context():
            asset_ids = [asset.id_asset for asset in TeraAsset.query.all()]
            self.db.session.expire_all()  # Clear cache
            for asset_id in asset_ids:
                test_asset = TeraAsset.get_asset_by_id(asset_id)
                self.assertEqual(test_asset.id_asset, asset_id)

            asset_uuids = [asset.asset_uuid for asset in TeraAsset.query.all()]
            self.db.session.expire_all()  # Clear cache
            for asset_uuid in asset_uuids:
                test_asset = TeraAsset.get_asset_by_uuid(asset_uuid)
                self.assertEqual(test_asset.asset_uuid, asset_uuid)

    def test_get_assets_created_by_device(self):
        with self._flask_app.app_context():
            devices = [{'id_device': device.id_device, 'assets_count': len(device.device_assets)}
                       for device in TeraDevice.query.all()]
            self.db.session.expire_all()  # Clear cache
            for device in devices:
                assets = TeraAsset.get_assets_created_by_device(device['id_device'])
                self.assertEqual(len(assets), device['assets_count'])

    def test_get_assets_created_by_user(self):
        with self._flask_app.app_context():
            users = [{'id_user': user.id_user, 'assets_count': len(user.user_assets)}
                     for user in TeraUser.query.all()]
            self.db.session.expire_all()  # Clear cache
            for user in users:
                assets = TeraAsset.get_assets_created_by_user(user['id_user'])
                self.assertEqual(len(assets), user['assets_count'])

    def test_get_assets_created_by_participant(self):
        with self._flask_app.app_context():
            parts = [{'id_participant': part.id_participant, 'assets_count': len(part.participant_assets)}
                     for part in TeraParticipant.query.all()]
            self.db.session.expire_all()  # Clear cache
            for part in parts:
                assets = TeraAsset.get_assets_created_by_participant(part['id_participant'])
                self.assertEqual(len(assets), part['assets_count'])

    def test_get_assets_created_by_service(self):
        with self._flask_app.app_context():
            services = [{'id_service': service.id_service, 'assets_count': len(service.service_assets)}
                        for service in TeraService.query.all()]
            self.db.session.expire_all()  # Clear cache
            for service in services:
                assets = TeraAsset.get_assets_created_by_service(service['id_service'])
                self.assertEqual(len(assets), service['assets_count'])

    def test_get_assets_owned_by_service(self):
        with self._flask_app.app_context():
            services = [{'uuid_service': service.service_uuid, 'assets_count': len(service.service_owned_assets)}
                        for service in TeraService.query.all()]
            self.db.session.expire_all()
            for service in services:
                assets = TeraAsset.get_assets_owned_by_service(service['uuid_service'])
                self.assertEqual(len(assets), service['assets_count'])

    def test_get_assets_accessible_for_user(self):
        with self._flask_app.app_context():
            users = []
            id_sessions = []
            assets_infos = []
            for user in TeraUser.query.all():
                user_info = {'id_user': user.id_user}
                assets = 0
                for session in user.user_sessions:
                    assets += len(session.session_assets)
                    assets_infos.extend(session.session_assets)
                    if session.id_session not in id_sessions:
                        id_sessions.append(session.id_session)
                # Also add assets created but not in session we are part of
                for asset in user.user_assets:
                    if asset.id_session not in id_sessions:
                        assets += 1
                        assets_infos.append(asset)
                user_info['assets_count'] = assets
                user_info['assets_info'] = assets_infos
                users.append(user_info)
            self.db.session.expire_all()  # Clear cache
            for user in users:
                assets = TeraAsset.get_assets_for_user(user['id_user'])
                self.assertEqual(len(assets), user['assets_count'])

    def test_get_assets_accessible_for_device(self):
        with self._flask_app.app_context():
            devices = []
            id_sessions = []
            for device in TeraDevice.query.all():
                device_info = {'id_device': device.id_device}
                assets = 0
                for session in device.device_sessions:
                    assets += len(session.session_assets)
                    if session.id_session not in id_sessions:
                        id_sessions.append(session.id_session)
                # Also add assets created but not in session we are part of
                for asset in device.device_assets:
                    if asset.id_session not in id_sessions:
                        assets += 1
                device_info['assets_count'] = assets
                devices.append(device_info)
            self.db.session.expire_all()  # Clear cache
            for device in devices:
                assets = TeraAsset.get_assets_for_device(device['id_device'])
                self.assertEqual(len(assets), device['assets_count'])

    def test_get_assets_accessible_for_participant(self):
        with self._flask_app.app_context():
            parts = []
            id_sessions = []
            for part in TeraParticipant.query.all():
                part_info = {'id_participant': part.id_participant}
                assets = 0
                for session in part.participant_sessions:
                    assets += len(session.session_assets)
                    if session.id_session not in id_sessions:
                        id_sessions.append(session.id_session)
                # Also add assets created but not in session we are part of
                for asset in part.participant_assets:
                    if asset.id_session not in id_sessions:
                        assets += 1
                part_info['assets_count'] = assets
                parts.append(part_info)
            self.db.session.expire_all()  # Clear cache
            for part in parts:
                assets = TeraAsset.get_assets_for_participant(part['id_participant'])
                self.assertEqual(len(assets), part['assets_count'])

    def test_get_access_token(self):
        with self._flask_app.app_context():
            asset_uuids = [asset.asset_uuid for asset in TeraAsset.query.all()]
            token_key = 'test123456'
            requester_uuid = TeraUser.get_user_by_id(2).user_uuid
            expiration_time = 300

            token = TeraAsset.get_access_token(asset_uuids=asset_uuids, token_key=token_key,
                                               requester_uuid=requester_uuid, expiration=expiration_time)

            # Try to decode token
            decoded = jwt.decode(token, key=token_key, algorithms=['HS256'])
            self.assertTrue('iat' in decoded)
            self.assertTrue('exp' in decoded)
            self.assertEqual(int(decoded['iat']) + expiration_time, decoded['exp'])
            self.assertTrue('asset_uuids' in decoded)
            self.assertEqual(asset_uuids, decoded['asset_uuids'])
            self.assertTrue('requester_uuid' in decoded)
            self.assertEqual(requester_uuid, decoded['requester_uuid'])

    def test_insert_with_minimal_config(self):
        with self._flask_app.app_context():
            # Create a new item
            asset = TeraAsset()
            asset.asset_name = 'Test asset'
            asset.id_session = TeraSession.get_session_by_id(1).id_session
            asset.asset_type = 'application/zip'
            asset.asset_service_uuid = TeraService.get_service_by_id(3).service_uuid
            TeraAsset.insert(asset)
            self.assertIsNotNone(asset.id_asset)
            self.assertIsNotNone(asset.asset_uuid)
            self.assertIsNone(asset.id_device)
            self.assertIsNone(asset.id_participant)
            self.assertIsNone(asset.id_user)
            self.assertIsNone(asset.id_service)
            self.assertIsNone(asset.asset_datetime)

            # Destroy asset
            TeraAsset.delete(asset.id_asset)

    def test_update(self):
        with self._flask_app.app_context():
            asset: TeraAsset = TeraAsset.get_asset_by_id(1)
            self.assertIsNotNone(asset)
            update_info = {'asset_name': 'New asset name', 'asset_type': 'Unknown'}
            id_asset = asset.id_asset
            self.db.session.rollback()
            TeraAsset.update(id_asset, update_info)
            asset = TeraAsset.get_asset_by_id(1)
            self.assertIsNotNone(asset)
            self.assertEqual('New asset name', asset.asset_name)
            self.assertEqual('Unknown', asset.asset_type)

    def test_soft_delete(self):
        with self._flask_app.app_context():
            # Create new
            asset = TeraAssetTest.new_test_asset(id_session=2,
                                                 service_uuid=TeraService.get_service_by_id(1).service_uuid)
            self.assertIsNotNone(asset.id_asset)
            id_asset = asset.id_asset

            # Delete
            TeraAsset.delete(id_asset)
            # Make sure it is deleted
            # Warning, it was deleted, object is not valid anymore
            self.assertIsNone(TeraAsset.get_asset_by_id(id_asset))
            # Check session is still present
            self.db.session.expire_all()
            session = TeraSession.get_session_by_id(2)
            self.assertIsNotNone(session)

    def test_hard_delete(self):
        with self._flask_app.app_context():
            # Create new
            asset = TeraAssetTest.new_test_asset(id_session=2,
                                                 service_uuid=TeraService.get_service_by_id(1).service_uuid)
            self.assertIsNotNone(asset.id_asset)
            id_asset = asset.id_asset

            # Hard delete
            TeraAsset.delete(id_asset, hard_delete=True)

            # Make sure it is deleted
            # Warning, it was deleted, object is not valid anymore
            self.assertIsNone(TeraAsset.get_asset_by_id(id_asset, with_deleted=True))
            # Check session is still present
            self.db.session.expire_all()
            session = TeraSession.get_session_by_id(2)
            self.assertIsNotNone(session)

    def test_undelete(self):
        with self._flask_app.app_context():
            # Create new participant
            from test_TeraParticipant import TeraParticipantTest
            participant = TeraParticipantTest.new_test_participant(id_project=1)
            id_participant = participant.id_participant

            # Create new device
            from test_TeraDevice import TeraDeviceTest
            device = TeraDeviceTest.new_test_device()
            id_device = device.id_device

            # Create new user
            from test_TeraUser import TeraUserTest
            user = TeraUserTest.new_test_user(user_name="asset_user")
            id_user = user.id_user

            # Create new session
            from test_TeraSession import TeraSessionTest
            ses = TeraSessionTest.new_test_session(participants=[participant], users=[user], devices=[device])
            id_session = ses.id_session

            # Create new asset
            asset = TeraAssetTest.new_test_asset(id_session=ses.id_session,
                                                 service_uuid=TeraService.get_service_by_id(1).service_uuid,
                                                 id_user=id_user, id_participant=id_participant, id_device=id_device)
            self.assertIsNotNone(asset.id_asset)
            id_asset = asset.id_asset

            # Delete
            TeraAsset.delete(id_asset)
            # Make sure it is deleted
            # Warning, it was deleted, object is not valid anymore
            self.assertIsNone(TeraAsset.get_asset_by_id(id_asset))

            # Undelete
            TeraAsset.undelete(id_asset)

            # Make sure it is back!
            self.db.session.expire_all()
            asset = TeraAsset.get_asset_by_id(id_asset)
            self.assertIsNotNone(asset)
            self.assertIsNone(asset.deleted_at)

            # Now, delete again but with its dependencies...
            # Asset will be deleted with the session
            TeraSession.delete(id_session)
            TeraParticipant.delete(id_participant)
            TeraDevice.delete(id_device)
            TeraUser.delete(id_user)

            # Exception should be thrown when trying to undelete
            with self.assertRaises(IntegrityError):
                TeraAsset.undelete(id_asset)

            # Restore participant
            TeraParticipant.undelete(id_participant)
            participant = TeraParticipant.get_participant_by_id(id_participant)
            self.assertIsNotNone(participant)

            # Restore asset - still has dependencies issues...
            with self.assertRaises(IntegrityError):
                TeraAsset.undelete(id_asset)

            # Restore user
            TeraUser.undelete(id_user)
            user = TeraUser.get_user_by_id(id_user)
            self.assertIsNotNone(user)

            # Restore asset - still has dependencies issues...
            with self.assertRaises(IntegrityError):
                TeraAsset.undelete(id_asset)

            # Restore device
            TeraDevice.undelete(id_device)
            device = TeraDevice.get_device_by_id(id_device)
            self.assertIsNotNone(device)

            # Restore asset - still has dependencies issues...
            with self.assertRaises(IntegrityError):
                TeraAsset.undelete(id_asset)

            # Restore session
            TeraSession.undelete(id_session)

            ses = TeraSession.get_session_by_id(id_session)
            self.assertIsNotNone(ses)

            # Asset was restored with the session...
            self.db.session.expire_all()
            asset = TeraAsset.get_asset_by_id(id_asset)
            self.assertIsNotNone(asset)
            self.assertIsNone(asset.deleted_at)

    @staticmethod
    def new_test_asset(id_session: int, service_uuid: str, id_device: int | None = None,
                       id_participant: int | None = None, id_user: int | None = None,
                       id_service: int | None = None) -> TeraAsset:
        asset = TeraAsset()
        asset.asset_name = 'Test asset'
        asset.id_session = id_session
        if id_device:
            asset.id_device = id_device
        if id_participant:
            asset.id_participant = id_participant
        if id_user:
            asset.id_user = id_user
        if id_service:
            asset.id_service = id_service
        asset.asset_service_uuid = service_uuid
        asset.asset_type = 'application/test'
        TeraAsset.insert(asset)
        return asset

