from modules.DatabaseModule.DBManager import DBManager
from modules.DatabaseModule.DBManagerTeraParticipantAccess import DBManagerTeraParticipantAccess
from opentera.db.models.TeraParticipant import TeraParticipant
from opentera.db.models.TeraDeviceParticipant import TeraDeviceParticipant
from opentera.db.models.TeraParticipantGroup import TeraParticipantGroup
from opentera.db.models.TeraAsset import TeraAsset
from opentera.db.models.TeraSession import TeraSession
from opentera.db.models.TeraSessionType import TeraSessionType
from opentera.db.models.TeraSessionTypeProject import TeraSessionTypeProject
from opentera.db.models.TeraTestType import TeraTestType
from opentera.db.models.TeraTestTypeProject import TeraTestTypeProject
from opentera.db.models.TeraService import TeraService
from opentera.db.models.TeraServiceProject import TeraServiceProject
# from opentera.db.models.TeraSessionParticipants import TeraSessionParticipants
from tests.opentera.db.models.BaseModelsTest import BaseModelsTest


class DBManagerTeraParticipantAccessTest(BaseModelsTest):

    def test_participant_query_device(self):
        """
        Query devices for a participant
        """
        with self._flask_app.app_context():

            participants = TeraParticipant.query.all()
            for participant in participants:
                participant_access : DBManagerTeraParticipantAccess = DBManager.participantAccess(participant)
                devices = participant_access.query_device({})

                # Make a query to get all devices for this participant
                queried_devices = TeraDeviceParticipant.query.filter_by(id_participant=participant.id_participant).all()
                self.assertEqual(len(devices), len(queried_devices))
                # self.assertEqual(devices, queried_devices)


                # Make a query with a filter with invalid device id
                queried_devices = participant_access.query_device({'id_device': 0})
                self.assertEqual(len(queried_devices), 0)

    def test_participant_get_accessible_assets(self):
        """
        Get accessible assets for a participant
        """
        with self._flask_app.app_context():

            participants = TeraParticipant.query.all()
            for participant in participants:
                participant_access : DBManagerTeraParticipantAccess = DBManager.participantAccess(participant)
                assets = participant_access.get_accessible_assets()

                # Verify valid filters
                for asset in assets:
                    test_query = participant_access.get_accessible_assets(id_asset=asset.id_asset)
                    self.assertEqual(len(test_query), 1)

                    test_query = participant_access.get_accessible_assets(uuid_asset=asset.asset_uuid)
                    self.assertEqual(len(test_query), 1)

                    test_query = participant_access.get_accessible_assets(session_id=asset.id_session)
                    self.assertEqual(len(test_query), 1)

                # Verify that we get the same result from db queries
                # This query returns all assets for sessions where the participant is in
                # get_accessible_assets() is more restrictive and only returns assets where the participant is assigned
                # all_assets = TeraAsset.query.join(TeraSessionParticipants, TeraSessionParticipants.id_session == TeraAsset.id_session).filter(
                #     TeraSessionParticipants.id_participant == participant.id_participant).distinct().all()

                queried_assets = TeraAsset.query.filter(TeraAsset.id_participant == participant.id_participant).all()
                self.assertEqual(len(assets), len(queried_assets))
                self.assertEqual(assets, queried_assets)

                # Make a query with a filter with invalid asset id
                queried_assets = participant_access.get_accessible_assets(id_asset=1000)
                self.assertEqual(len(queried_assets), 0)

                # Make a query with a filter with invalid asset uuid
                queried_assets = participant_access.get_accessible_assets(uuid_asset='invalid_uuid')
                self.assertEqual(len(queried_assets), 0)

                # Make a query with a filter with invalid session id
                queried_assets = participant_access.get_accessible_assets(session_id=1000)
                self.assertEqual(len(queried_assets), 0)

    def test_participant_get_accessible_services(self):
        """
        Get accessible services for a participant
        """
        with self._flask_app.app_context():

            participants = TeraParticipant.query.all()
            for participant in participants:
                participant_access : DBManagerTeraParticipantAccess = DBManager.participantAccess(participant)
                services = participant_access.get_accessible_services()

                queried_services = TeraService.query.join(TeraServiceProject, TeraServiceProject.id_service == TeraService.id_service).\
                    filter(TeraServiceProject.id_project == participant.id_project).all()

                self.assertEqual(len(services), len(queried_services))
                self.assertEqual(services, queried_services)

    def test_participant_get_accessible_session_types_ids(self):
        """
        Get accessible session types for a participant, with ids, will also test get_accessible_session_types()
        """
        with self._flask_app.app_context():

            participants = TeraParticipant.query.all()
            for participant in participants:
                participant_access : DBManagerTeraParticipantAccess = DBManager.participantAccess(participant)
                session_types_ids = participant_access.get_accessible_session_types_ids()

                queried_session_types = TeraSessionType.query.join(
                    TeraSessionTypeProject, TeraSessionTypeProject.id_session_type == TeraSessionType.id_session_type).filter(
                        TeraSessionTypeProject.id_project == participant.id_project).all()
                queried_session_types_ids = [session_type.id_session_type for session_type in queried_session_types]
                self.assertEqual(len(session_types_ids), len(queried_session_types_ids))
                self.assertEqual(session_types_ids, queried_session_types_ids)


    def test_participant_query_existing_sessions_ids(self):
        """
        Query existing session for a participant. Will also test get_accessible_sessions
        """
        with self._flask_app.app_context():

            participants = TeraParticipant.query.all()
            for participant in participants:
                participant_access : DBManagerTeraParticipantAccess = DBManager.participantAccess(participant)

                sessions_ids = participant_access.get_accessible_sessions_ids()

                queried_sessions = TeraSession.query.filter_by(id_creator_participant=participant.id_participant).all()
                queried_sessions_ids = [session.id_session for session in queried_sessions]
                self.assertEqual(len(sessions_ids), len(queried_sessions_ids))
                self.assertEqual(sessions_ids, queried_sessions_ids)


    def test_participant_get_accessible_tests_types_ids(self):
        """
        Get accessible test types for a participant, with ids, will also test get_accessible_tests_types()
        """
        with self._flask_app.app_context():

            participants = TeraParticipant.query.all()
            for participant in participants:
                participant_access : DBManagerTeraParticipantAccess = DBManager.participantAccess(participant)
                test_types_ids = participant_access.get_accessible_tests_types_ids()

                queried_test_types = TeraTestType.query.join(
                    TeraTestTypeProject, TeraTestTypeProject.id_test_type == TeraTestType.id_test_type).filter(
                        TeraTestTypeProject.id_project == participant.id_project).all()
                queried_test_types_ids = [test_type.id_test_type for test_type in queried_test_types]
                self.assertEqual(len(test_types_ids), len(queried_test_types_ids))
                self.assertEqual(test_types_ids, queried_test_types_ids)
