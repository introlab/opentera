from modules.DatabaseModule.DBManager import DBManager
from modules.DatabaseModule.DBManagerTeraParticipantAccess import DBManagerTeraParticipantAccess
from opentera.db.models.TeraUser import TeraUser
from opentera.db.models.TeraParticipant import TeraParticipant
from opentera.db.models.TeraDeviceParticipant import TeraDeviceParticipant
from opentera.db.models.TeraParticipantGroup import TeraParticipantGroup
from opentera.db.models.TeraAsset import TeraAsset
from opentera.db.models.TeraSessionParticipants import TeraSessionParticipants
from tests.opentera.db.models.BaseModelsTest import BaseModelsTest


class DBManagerTeraParticipantAccessTest(BaseModelsTest):

    def test_participant_query_device(self):
        """
        Query devices for a participant
        """
        with self._flask_app.app_context():

            participants = TeraParticipant.query.all()
            for participant in participants:
                participant_access = DBManager.participantAccess(participant)
                devices = participant_access.query_device({})

                # Make a query to get all devices for this participant
                all_devices = TeraDeviceParticipant.query.filter_by(id_participant=participant.id_participant).all()
                self.assertEqual(len(devices), len(all_devices))


                # Make a query with a filter with invalid device id
                devices = participant_access.query_device({'id_device': 0})
                self.assertEqual(len(devices), 0)

    def test_participant_get_accessible_assets(self):
        """
        Get accessible assets for a participant
        """
        with self._flask_app.app_context():

            participants = TeraParticipant.query.all()
            for participant in participants:
                participant_access = DBManager.participantAccess(participant)
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

                # Make a query with a filter with invalid asset id
                queried_assets = participant_access.get_accessible_assets(id_asset=1000)
                self.assertEqual(len(queried_assets), 0)

                # Make a query with a filter with invalid asset uuid
                queried_assets = participant_access.get_accessible_assets(uuid_asset='invalid_uuid')
                self.assertEqual(len(queried_assets), 0)

                # Make a query with a filter with invalid session id
                queried_assets = participant_access.get_accessible_assets(session_id=1000)
                self.assertEqual(len(queried_assets), 0)
