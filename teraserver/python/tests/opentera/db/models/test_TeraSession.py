from opentera.db.models.TeraParticipant import TeraParticipant
from opentera.db.models.TeraDevice import TeraDevice
from opentera.db.models.TeraSession import TeraSession, TeraSessionStatus
from opentera.db.models.TeraUser import TeraUser
from opentera.db.models.TeraSessionDevices import TeraSessionDevices
from opentera.db.models.TeraSessionUsers import TeraSessionUsers
from opentera.db.models.TeraSessionParticipants import TeraSessionParticipants
from opentera.db.models.TeraAsset import TeraAsset
from opentera.db.models.TeraTest import TeraTest
from opentera.db.models.TeraService import TeraService
from tests.opentera.db.models.BaseModelsTest import BaseModelsTest


class TeraSessionTest(BaseModelsTest):

    def test_session_defaults(self):
        with self._flask_app.app_context():
            for session in TeraSession.query.all():
                my_list = [session.id_creator_device, session.id_creator_participant,
                           session.id_creator_service, session.id_creator_user]
                # Only one not None
                self.assertEqual(1, len([x for x in my_list if x is not None]))

    def test_session_new(self):
        from datetime import datetime
        from modules.DatabaseModule.DBManagerTeraDeviceAccess import DBManagerTeraDeviceAccess

        with self._flask_app.app_context():
            session = TeraSession()

            device = TeraDevice.get_device_by_id(1)
            access = DBManagerTeraDeviceAccess(device)
            participant1 = TeraParticipant.get_participant_by_id(1)
            participant2 = TeraParticipant.get_participant_by_id(2)

            session_types = access.get_accessible_session_types()

            session.session_name = 'TEST'
            session.session_creator_device = device
            session.session_participants.append(participant1)
            session.session_participants.append(participant2)
            session.session_start_datetime = datetime.now()
            session.session_status = TeraSessionStatus.STATUS_NOTSTARTED.value

            if len(session_types) > 0:
                session.id_session_type = session_types[0].id_session_type
                TeraSession.insert(session)

    def test_session_from_json(self):
        with self._flask_app.app_context():
            pass
            #
            # session = {'session': {'id_session': 0,
            #                        'session_participants': participants_id_list,
            #                        'id_session_type': session_type['id_session_type'],
            #                        'session_name': 'TEST',
            #                        'session_status': 0,
            #                        'session_start_datetime': str(datetime.now())}}

    def test_soft_delete(self):
        with self._flask_app.app_context():
            # Create new
            ses = TeraSession()
            ses.id_creator_service = 1
            ses.id_session_type = 1
            ses.session_name = "Test session"
            ses.session_participants = [TeraParticipant.get_participant_by_id(1)]
            ses.session_devices = [TeraDevice.get_device_by_id(1)]
            ses.session_users = [TeraUser.get_user_by_id(2)]
            TeraSession.insert(ses)
            id_session = ses.id_session

            # Attach asset
            asset = TeraAsset()
            asset.asset_name = "Asset test"
            asset.id_device = 1
            asset.id_session = id_session
            asset.asset_service_uuid = TeraService.get_openteraserver_service().service_uuid
            asset.asset_type = 'Test'
            TeraAsset.insert(asset)
            id_asset = asset.id_asset

            # ... and test
            test = TeraTest()
            test.id_device = 1
            test.id_session = id_session
            test.id_test_type = 1
            test.test_name = "Test test!"
            TeraTest.insert(test)
            id_test = test.id_test

            # Soft delete
            TeraSession.delete(id_session)

            # Make sure it is deleted
            self.assertIsNone(TeraSession.get_session_by_id(id_session))

            # Query, with soft delete flag
            ses = TeraSession.query.filter_by(id_session=id_session).execution_options(include_deleted=True).first()
            self.assertIsNotNone(ses)
            self.assertIsNotNone(ses.deleted_at)
            self.assertIsNone(TeraSessionParticipants.query.filter_by(id_session=id_session).first())
            self.assertIsNone(TeraSessionUsers.query.filter_by(id_session=id_session).first())
            self.assertIsNone(TeraSessionDevices.query.filter_by(id_session=id_session).first())
            self.assertIsNone(TeraAsset.get_asset_by_id(id_asset))
            self.assertIsNone(TeraTest.get_test_by_id(id_test))
            self.assertIsNotNone(TeraSessionParticipants.query.filter_by(id_session=id_session)
                                 .execution_options(include_deleted=True).first())
            self.assertIsNotNone(TeraSessionUsers.query.filter_by(id_session=id_session)
                                 .execution_options(include_deleted=True).first())
            self.assertIsNotNone(TeraSessionDevices.query.filter_by(id_session=id_session)
                                 .execution_options(include_deleted=True).first())
            self.assertIsNotNone(TeraAsset.get_asset_by_id(id_asset, True))
            self.assertIsNotNone(TeraTest.get_test_by_id(id_test, True))

    def test_hard_delete(self):
        with self._flask_app.app_context():
            # Create new
            ses = TeraSession()
            ses.id_creator_service = 1
            ses.id_session_type = 1
            ses.session_name = "Test session"
            ses.session_participants = [TeraParticipant.get_participant_by_id(1)]
            ses.session_devices = [TeraDevice.get_device_by_id(1)]
            ses.session_users = [TeraUser.get_user_by_id(2)]
            TeraSession.insert(ses)
            id_session = ses.id_session

            # Attach asset
            asset = TeraAsset()
            asset.asset_name = "Asset test"
            asset.id_device = 1
            asset.id_session = id_session
            asset.asset_service_uuid = TeraService.get_openteraserver_service().service_uuid
            asset.asset_type = 'Test'
            TeraAsset.insert(asset)
            id_asset = asset.id_asset

            # ... and test
            test = TeraTest()
            test.id_device = 1
            test.id_session = id_session
            test.id_test_type = 1
            test.test_name = "Test test!"
            TeraTest.insert(test)
            id_test = test.id_test

            # Hard delete
            TeraSession.delete(id_session, hard_delete=True)

            # Make sure eveything is deleted
            self.assertIsNone(TeraSession.get_session_by_id(id_session, True))
            self.assertIsNone(TeraSessionParticipants.query.filter_by(id_session=id_session)
                              .execution_options(include_deleted=True).first())
            self.assertIsNone(TeraSessionUsers.query.filter_by(id_session=id_session)
                              .execution_options(include_deleted=True).first())
            self.assertIsNone(TeraSessionDevices.query.filter_by(id_session=id_session)
                              .execution_options(include_deleted=True).first())
            self.assertIsNone(TeraAsset.get_asset_by_id(id_asset, with_deleted=True))
            self.assertIsNone(TeraTest.get_test_by_id(id_test, with_deleted=True))

