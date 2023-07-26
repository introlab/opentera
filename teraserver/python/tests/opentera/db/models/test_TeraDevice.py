from opentera.db.models.TeraAsset import TeraAsset
from opentera.db.models.TeraTest import TeraTest
from opentera.db.models.TeraService import TeraService
from opentera.db.models.TeraDevice import TeraDevice
from opentera.db.models.TeraDeviceType import TeraDeviceType
from opentera.db.models.TeraDeviceProject import TeraDeviceProject
from opentera.db.models.TeraDeviceSite import TeraDeviceSite
from opentera.db.models.TeraDeviceParticipant import TeraDeviceParticipant
from opentera.db.models.TeraServiceConfig import TeraServiceConfig
from opentera.db.models.TeraSession import TeraSession

from tests.opentera.db.models.BaseModelsTest import BaseModelsTest


class TeraDeviceTest(BaseModelsTest):

    def test_defaults(self):
        with self._flask_app.app_context():
            devices = TeraDevice.query.all()
            self.assertGreater(len(devices), 0)

    def test_json_full_and_minimal(self):
        with self._flask_app.app_context():
            devices = TeraDevice.query.all()
            self.assertGreater(len(devices), 0)
            for minimal in [False, True]:
                for device in devices:
                    self.assertIsNotNone(device)
                    json = device.to_json(minimal=minimal)
                    self.assertNotEqual(None, json)

                    if not minimal:
                        # Full fields only
                        self.assertTrue('device_config' in json)
                        self.assertTrue('device_infos' in json)
                        self.assertTrue('device_lastonline' in json)
                        self.assertTrue('device_notes' in json)
                        self.assertTrue('device_onlineable' in json)
                        self.assertTrue('device_token' in json)

                    # Minimal + full fields
                    self.assertTrue('device_enabled' in json)
                    self.assertTrue('device_name' in json)
                    self.assertTrue('device_uuid' in json)
                    self.assertTrue('id_device' in json)
                    self.assertTrue('id_device_type' in json)
                    self.assertTrue('id_device_subtype' in json)

                    # Make sure deleted at field not there
                    self.assertFalse('deleted_at' in json)

    def test_insert_with_minimal_config(self):
        with self._flask_app.app_context():
            # Create a new device
            device = TeraDeviceTest.new_test_device()
            self.assertIsNotNone(device.id_device)
            self.assertIsNotNone(device.device_token)
            self.assertIsNotNone(device.device_uuid)
            self.assertFalse(device.device_enabled)
            self.assertFalse(device.device_onlineable)
            self.assertIsNone(device.device_config)
            self.assertIsNone(device.device_infos)
            self.assertIsNone(device.device_lastonline)
            self.assertIsNone(device.device_notes)

            # Destroy device
            TeraDevice.delete(device.id_device)

    def test_update(self):
        with self._flask_app.app_context():
            device: TeraDevice = TeraDevice.get_device_by_id(1)
            self.assertIsNotNone(device)
            update_info = {'device_notes': 'Test notes'}
            # device.device_notes = 'Test notes'
            TeraDevice.update(device.id_device, update_info)
            # TeraDevice.update(device.id_device, device.to_json(minimal=True))
            device = TeraDevice.get_device_by_id(1)
            self.assertIsNotNone(device)
            self.assertEqual('Test notes', device.device_notes)

    def test_delete(self):
        with self._flask_app.app_context():
            # Create a new device
            device = TeraDeviceTest.new_test_device()
            self.assertIsNotNone(device.id_device)
            id_device = device.id_device
            # Delete device
            TeraDevice.delete(device.id_device)
            # Make sure device is deleted
            # Warning, device was deleted, device object is not valid anymore
            self.assertIsNone(TeraDevice.get_device_by_id(id_device))

    def test_soft_delete(self):
        with self._flask_app.app_context():
            # Create a new device
            device = TeraDeviceTest.new_test_device()
            self.assertIsNotNone(device.id_device)
            id_device = device.id_device
            # Delete device
            TeraDevice.delete(device.id_device)
            # Make sure device is deleted
            # Warning, device was deleted, device object is not valid anymore
            self.assertIsNone(TeraDevice.get_device_by_id(id_device))

            # Query device, with soft delete flag
            device = TeraDevice.query.filter_by(id_device=id_device).execution_options(include_deleted=True).first()
            self.assertIsNotNone(device)
            self.assertIsNotNone(device.deleted_at)

    def test_hard_delete(self):
        with self._flask_app.app_context():
            # Create a new device
            device = TeraDeviceTest.new_test_device()
            self.assertIsNotNone(device.id_device)
            id_device = device.id_device

            # Assign device to site
            from test_TeraDeviceSite import TeraDeviceSiteTest
            device_site = TeraDeviceSiteTest.new_test_device_site(id_device=id_device, id_site=1)
            id_device_site = device_site.id_device_site

            # Assign device to project
            from test_TeraDeviceProject import TeraDeviceProjectTest
            device_project = TeraDeviceProjectTest.new_test_device_project(id_device=id_device, id_project=1)
            id_device_project = device_project.id_device_project

            # Assign device to participants
            from test_TeraDeviceParticipant import TeraDeviceParticipantTest
            device_participant = TeraDeviceParticipantTest.new_test_device_participant(id_device=id_device,
                                                                                       id_participant=1)
            id_device_participant = device_participant.id_device_participant

            # Assign device to sessions
            from test_TeraSession import TeraSessionTest
            device_session = TeraSessionTest.new_test_session(id_creator_device=id_device)
            id_session = device_session.id_session

            device_session = TeraSessionTest.new_test_session(id_creator_service=1, devices=[device])
            id_session_invitee = device_session.id_session

            # Attach asset
            from test_TeraAsset import TeraAssetTest
            asset = TeraAssetTest.new_test_asset(id_session=id_session,
                                                 service_uuid=TeraService.get_openteraserver_service().service_uuid,
                                                 id_device=id_device)
            id_asset = asset.id_asset

            # ... and test
            from test_TeraTest import TeraTestTest
            test = TeraTestTest.new_test_test(id_session=id_session, id_device=id_device)
            id_test = test.id_test

            # Create service config for device
            from test_TeraServiceConfig import TeraServiceConfigTest
            device_service_config = TeraServiceConfigTest.new_test_service_config(id_device=id_device, id_service=2)
            id_service_config = device_service_config.id_service_config

            # Soft delete device to prevent relationship integrity errors as we want to test hard-delete cascade here
            TeraDeviceParticipant.delete(id_device_participant)
            TeraSession.delete(id_session)
            TeraSession.delete(id_session_invitee)
            TeraDevice.delete(id_device)

            # Check that device and relationships are still there
            self.assertIsNone(TeraDevice.get_device_by_id(id_device))
            self.assertIsNotNone(TeraDevice.get_device_by_id(id_device, True))
            self.assertIsNone(TeraDeviceProject.get_device_project_by_id(id_device_project))
            self.assertIsNotNone(TeraDeviceProject.get_device_project_by_id(id_device_project, True))
            self.assertIsNone(TeraDeviceParticipant.get_device_participant_by_id(id_device_participant))
            self.assertIsNotNone(TeraDeviceParticipant.get_device_participant_by_id(id_device_participant, True))
            self.assertIsNone(TeraSession.get_session_by_id(id_session))
            self.assertIsNotNone(TeraSession.get_session_by_id(id_session, True))
            self.assertIsNone(TeraSession.get_session_by_id(id_session_invitee))
            self.assertIsNotNone(TeraSession.get_session_by_id(id_session_invitee, True))
            self.assertIsNone(TeraDeviceSite.get_device_site_by_id(id_device_site))
            self.assertIsNotNone(TeraDeviceSite.get_device_site_by_id(id_device_site, True))
            self.assertIsNone(TeraAsset.get_asset_by_id(id_asset))
            self.assertIsNotNone(TeraAsset.get_asset_by_id(id_asset, True))
            self.assertIsNone(TeraTest.get_test_by_id(id_test))
            self.assertIsNotNone(TeraTest.get_test_by_id(id_test, True))
            self.assertIsNone(TeraServiceConfig.get_service_config_by_id(id_service_config))
            self.assertIsNotNone(TeraServiceConfig.get_service_config_by_id(id_service_config, True))

            # Hard delete device
            TeraDevice.delete(device.id_device, hard_delete=True)

            # Make sure device and associations are deleted
            self.assertIsNone(TeraDevice.get_device_by_id(id_device, True))
            self.assertIsNone(TeraDeviceProject.get_device_project_by_id(id_device_project, True))
            self.assertIsNone(TeraDeviceParticipant.get_device_participant_by_id(id_device_participant, True))
            self.assertIsNone(TeraSession.get_session_by_id(id_session, True))
            self.assertIsNone(TeraSession.get_session_by_id(id_session_invitee, True))
            self.assertIsNone(TeraAsset.get_asset_by_id(id_asset, True))
            self.assertIsNone(TeraTest.get_test_by_id(id_test, True))
            self.assertIsNone(TeraServiceConfig.get_service_config_by_id(id_service_config, True))
            self.assertIsNone(TeraDeviceSite.get_device_site_by_id(id_device_site, True))

    def test_undelete(self):
        with self._flask_app.app_context():
            # Create a new device
            device = TeraDeviceTest.new_test_device()
            self.assertIsNotNone(device.id_device)
            id_device = device.id_device

            # Assign device to site
            from test_TeraDeviceSite import TeraDeviceSiteTest
            device_site = TeraDeviceSiteTest.new_test_device_site(id_device=id_device, id_site=1)
            id_device_site = device_site.id_device_site

            # Assign device to project
            from test_TeraDeviceProject import TeraDeviceProjectTest
            device_project = TeraDeviceProjectTest.new_test_device_project(id_device=id_device, id_project=1)
            id_device_project = device_project.id_device_project

            # Assign device to participants
            from test_TeraDeviceParticipant import TeraDeviceParticipantTest
            device_participant = TeraDeviceParticipantTest.new_test_device_participant(id_device=id_device,
                                                                                       id_participant=1)
            id_device_participant = device_participant.id_device_participant

            # Assign device to sessions
            from test_TeraSession import TeraSessionTest
            device_session = TeraSessionTest.new_test_session(id_creator_device=id_device)
            id_session = device_session.id_session

            device_session = TeraSessionTest.new_test_session(id_creator_service=1, devices=[device])
            id_session_invitee = device_session.id_session

            # Attach asset
            from test_TeraAsset import TeraAssetTest
            asset = TeraAssetTest.new_test_asset(id_session=id_session,
                                                 service_uuid=TeraService.get_openteraserver_service().service_uuid,
                                                 id_device=id_device)
            id_asset = asset.id_asset

            # ... and test
            from test_TeraTest import TeraTestTest
            test = TeraTestTest.new_test_test(id_session=id_session, id_device=id_device)
            id_test = test.id_test

            # Create service config for device
            from test_TeraServiceConfig import TeraServiceConfigTest
            device_service_config = TeraServiceConfigTest.new_test_service_config(id_device=id_device, id_service=2)
            id_service_config = device_service_config.id_service_config

            # Delete other items too to prevent integrity errors (as this is not what we want to test here)
            TeraDeviceParticipant.delete(id_device_participant)
            TeraSession.delete(id_session)
            TeraSession.delete(id_session_invitee)
            TeraDevice.delete(id_device)

            # Other checks are done in other tests - just make sure device is deleted for now
            self.assertIsNone(TeraDevice.get_device_by_id(id_device))

            # Undelete
            TeraDevice.undelete(id_device)

            # Check that everything was undeleted
            device = TeraDevice.get_device_by_id(id_device)
            self.assertIsNotNone(device)
            self.assertIsNone(device.deleted_at)
            device_site = TeraDeviceSite.get_device_site_by_id(id_device_site)
            self.assertIsNotNone(device_site)
            device_project = TeraDeviceProject.get_device_project_by_id(id_device_project)
            self.assertIsNotNone(device_project)
            device_participant = TeraDeviceParticipant.get_device_participant_by_id(id_device_participant)
            self.assertIsNotNone(device_participant)
            device_session = TeraSession.get_session_by_id(id_session_invitee)
            self.assertIsNone(device_session)
            device_session = TeraSession.get_session_by_id(id_session)
            self.assertIsNone(device_session)  # Not undeleted
            asset = TeraAsset.get_asset_by_id(id_asset)
            self.assertIsNone(asset)  # Asset stays deleted
            test = TeraTest.get_test_by_id(id_test)
            self.assertIsNone(test)  # Test stays deleted

    @staticmethod
    def new_test_device() -> TeraDevice:
        device = TeraDevice()
        device.device_name = 'Test device'
        device.id_device_type = TeraDeviceType.get_device_type_by_key('capteur').id_device_type
        TeraDevice.insert(device)

        return device
