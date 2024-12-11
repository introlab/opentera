from datetime import datetime, timedelta
import uuid

from modules.DatabaseModule.DBManagerTeraServiceAccess import DBManagerTeraServiceAccess
from tests.modules.FlaskModule.API.service.BaseServiceAPITest import BaseServiceAPITest
from opentera.db.models.TeraTestInvitation import TeraTestInvitation
from opentera.db.models.TeraParticipant import TeraParticipant
from opentera.db.models.TeraUser import TeraUser
from opentera.db.models.TeraDevice import TeraDevice
from opentera.db.models.TeraTestType import TeraTestType
from opentera.db.models.TeraSession import TeraSession
from opentera.db.models.TeraService import TeraService

class ServiceQueryTestsInvitationsTest(BaseServiceAPITest):
    """
    Test ServiceQueryTestsInvitations API
    """
    test_endpoint = '/api/service/tests/invitations'

    def tearDown(self):
        # Will delete all invitations after each test
        self._delete_all_invitations()
        super().tearDown()

    def test_no_auth(self):
        """
        Test that a get request with no auth returns 401
        """
        with self._flask_app.app_context():
            response = self.test_client.get(self.test_endpoint)
            self.assertEqual(401, response.status_code)

    def test_post_no_auth(self):
        """
        Test that a post request with no auth returns 401
        """
        with self._flask_app.app_context():
            response = self.test_client.post(self.test_endpoint)
            self.assertEqual(401, response.status_code)

    def test_delete_no_auth(self):
        """
        Test that a delete request with no auth returns 401
        """
        with self._flask_app.app_context():
            response = self.test_client.delete(self.test_endpoint)
            self.assertEqual(401, response.status_code)

    def test_get_endpoint_invalid_token_auth(self):
        """
        Test that a get request with invalid token returns 401
        """
        with self._flask_app.app_context():
            response = self._get_with_service_token_auth(self.test_client, token='invalid')
            self.assertEqual(401, response.status_code)

    def test_post_endpoint_invalid_token_auth(self):
        """
        Test that a post request with invalid token returns 401
        """
        with self._flask_app.app_context():
            response = self._post_with_service_token_auth(self.test_client, token='invalid')
            self.assertEqual(401, response.status_code)

    def test_delete_endpoint_invalid_token_auth(self):
        """
        Test that a delete request with invalid token returns 401
        """
        with self._flask_app.app_context():
            response = self._delete_with_service_token_auth(self.test_client, token='invalid')
            self.assertEqual(401, response.status_code)

    def test_get_query_bad_params_with_token(self):
        """
        Bad params should return 400
        """
        with self._flask_app.app_context():
            params = {'id_invalid': 1}
            response = self._get_with_service_token_auth(self.test_client, token=self.service_token,
                                                     params=params)
            self.assertEqual(400, response.status_code)

    def test_get_query_no_params_with_token_returns_all_accessible_invitations(self):
        """
        Test that an admin can access all invitations
        """
        with self._flask_app.app_context():
            create_count = 10

            # Create Test type for service
            test_type_accessible = self._create_test_type_for_service(self.id_service)
            test_type_not_accessible = self._create_test_type_for_service(1)

            # Create invitations
            self._create_invitations(create_count, id_test_type=test_type_accessible.id_test_type, id_user=1)
            self._create_invitations(create_count, id_test_type=test_type_not_accessible.id_test_type, id_user=1)

            # Service should access only invitations of its test type
            response = self._get_with_service_token_auth(self.test_client, token=self.service_token)
            self.assertEqual(200, response.status_code)
            self.assertEqual(create_count, len(response.json))

            for json_invitation in response.json:
                self._validate_json(json_invitation)

            TeraTestType.delete(test_type_accessible.id_test_type)
            TeraTestType.delete(test_type_not_accessible.id_test_type)

    def test_get_query_no_params_with_token_returns_all_accessible_invitations_with_uuids(self):
        """
        Test that an admin can access all invitations
        """
        with self._flask_app.app_context():
            create_count = 10

            # Create Test type for service
            test_type_accessible = self._create_test_type_for_service(self.id_service)
            test_type_not_accessible = self._create_test_type_for_service(1)

            # Create invitations
            self._create_invitations(create_count, id_test_type=test_type_accessible.id_test_type, id_user=1)
            self._create_invitations(create_count, id_test_type=test_type_not_accessible.id_test_type, id_user=1)

            # Service should access only invitations of its test type
            response = self._get_with_service_token_auth(self.test_client, token=self.service_token, params={'with_uuids': True})
            self.assertEqual(200, response.status_code)
            self.assertEqual(create_count, len(response.json))

            for json_invitation in response.json:
                self._validate_json(json_invitation, with_uuids=True)

            TeraTestType.delete(test_type_accessible.id_test_type)
            TeraTestType.delete(test_type_not_accessible.id_test_type)

    def test_get_query_no_params_with_token_returns_all_accessible_invitations_with_urls(self):
        """
        Test that an admin can access all invitations
        """
        with self._flask_app.app_context():
            create_count = 10

            # Create Test type for service
            test_type_accessible = self._create_test_type_for_service(self.id_service)
            test_type_not_accessible = self._create_test_type_for_service(1)

            # Create invitations
            self._create_invitations(create_count, id_test_type=test_type_accessible.id_test_type, id_user=1)
            self._create_invitations(create_count, id_test_type=test_type_not_accessible.id_test_type, id_user=1)

            # Service should access only invitations of its test type
            response = self._get_with_service_token_auth(self.test_client, token=self.service_token, params={'with_urls': True})
            self.assertEqual(200, response.status_code)
            self.assertEqual(create_count, len(response.json))

            for json_invitation in response.json:
                self._validate_json(json_invitation, with_urls=True)

            TeraTestType.delete(test_type_accessible.id_test_type)
            TeraTestType.delete(test_type_not_accessible.id_test_type)

    def test_get_query_with_id_test_invitation_or_key_with_service_token(self):
        """
        Test that an service can access an invitation with id_test_invitation or test_invitation_key
        """
        with self._flask_app.app_context():
            create_count = 10

            # Create invitations
            test_type_accessible = self._create_test_type_for_service(self.id_service)
            invitations = self._create_invitations(create_count, id_test_type=test_type_accessible.id_test_type, id_user=1)

            # Service should access all invitations
            for invitation in invitations:
                response = self._get_with_service_token_auth(self.test_client, token=self.service_token,
                                                        params={'id_test_invitation': invitation.id_test_invitation})
                self.assertEqual(200, response.status_code)
                self.assertEqual(1, len(response.json))
                for json_invitation in response.json:
                    self._validate_json(json_invitation)

                # Also test with test_invitation_key
                response = self._get_with_service_token_auth(self.test_client, token=self.service_token,
                                                        params={'test_invitation_key': invitation.test_invitation_key})
                self.assertEqual(200, response.status_code)
                self.assertEqual(1, len(response.json))
                for json_invitation in response.json:
                    self._validate_json(json_invitation)

            # Also test with invalid id_test_invitation
            response = self._get_with_service_token_auth(self.test_client, token=self.service_token,
                                                    params={'id_test_invitation': 0})
            self.assertEqual(200, response.status_code)
            self.assertEqual(0, len(response.json))

            # Also test with invalid test_invitation_key
            response = self._get_with_service_token_auth(self.test_client, token=self.service_token,
                                                    params={'test_invitation_key': 'invalid'})
            self.assertEqual(200, response.status_code)
            self.assertEqual(0, len(response.json))

            TeraTestType.delete(test_type_accessible.id_test_type)

    def test_get_query_with_id_user_as_admin_returns_only_invitation_for_specific_id_user(self):
        """
        Test that an service can access only invitations for a specific user
        """
        with self._flask_app.app_context():
            create_count = 10

            # Create 10 invitations
            test_type_accessible = self._create_test_type_for_service(self.id_service)
            self._create_invitations(create_count, id_test_type=test_type_accessible.id_test_type, id_user=1)
            self._create_invitations(create_count, id_test_type=test_type_accessible.id_test_type, id_user=2)

            # Service should access only invitations of id_user=1
            response = self._get_with_service_token_auth(self.test_client, token=self.service_token,
                                                     params={'id_user': 1})
            self.assertEqual(200, response.status_code)
            self.assertEqual(create_count, len(response.json))
            for json_invitation in response.json:
                self._validate_json(json_invitation)

            # Also test with user_uuid
            user : TeraUser = TeraUser.get_user_by_id(1)
            response = self._get_with_service_token_auth(self.test_client, token=self.service_token,
                                                     params={'user_uuid': user.user_uuid})
            self.assertEqual(200, response.status_code)
            self.assertEqual(create_count, len(response.json))
            for json_invitation in response.json:
                self._validate_json(json_invitation)

            # Also test invalid id_user
            response = self._get_with_service_token_auth(self.test_client, token=self.service_token,
                                                    params={'id_user': 0})
            self.assertEqual(200, response.status_code)
            self.assertEqual(0, len(response.json))

            TeraTestType.delete(test_type_accessible.id_test_type)

    def test_get_query_with_id_participant_with_service_token_returns_only_invitation_for_specific_id_participant(self):
        """
        Test that service can access only invitations for a specific participant
        """
        with self._flask_app.app_context():
            create_count = 10
            # Create 10 invitations
            test_type_accessible = self._create_test_type_for_service(self.id_service)
            self._create_invitations(create_count, id_test_type=test_type_accessible.id_test_type, id_participant=1)
            self._create_invitations(create_count, id_test_type=test_type_accessible.id_test_type, id_participant=2)

            # Service should access all invitations
            response = self._get_with_service_token_auth(self.test_client, token=self.service_token,
                                                     params={'id_participant': 1})
            self.assertEqual(200, response.status_code)
            self.assertEqual(create_count, len(response.json))
            for json_invitation in response.json:
                self._validate_json(json_invitation)

            # Also test with participant_uuid
            participant : TeraParticipant = TeraParticipant.get_participant_by_id(1)
            response = self._get_with_service_token_auth(self.test_client, token=self.service_token,
                                                     params={'participant_uuid': participant.participant_uuid})
            self.assertEqual(200, response.status_code)
            self.assertEqual(create_count, len(response.json))


            # Also test invalid id_participant
            response = self._get_with_service_token_auth(self.test_client, token=self.service_token,
                                                    params={'id_participant': 0})
            self.assertEqual(200, response.status_code)
            self.assertEqual(0, len(response.json))
            TeraTestType.delete(test_type_accessible.id_test_type)


    def test_get_query_with_id_device_with_service_token_returns_only_invitation_for_specific_id_device(self):
        """
        Test that service can access only invitations for a specific device
        """
        with self._flask_app.app_context():
            create_count = 10
            # Create 10 invitations
            test_type_accessible = self._create_test_type_for_service(self.id_service)
            self._create_invitations(create_count, id_test_type=test_type_accessible.id_test_type, id_device=1)
            self._create_invitations(create_count, id_test_type=test_type_accessible.id_test_type, id_device=2)

            # Service should access all invitations
            response = self._get_with_service_token_auth(self.test_client, token=self.service_token,
                                                     params={'id_device': 1})
            self.assertEqual(200, response.status_code)
            self.assertEqual(create_count, len(response.json))
            for json_invitation in response.json:
                self._validate_json(json_invitation)

            # Also test with device_uuid
            device : TeraDevice = TeraDevice.get_device_by_id(1)
            response = self._get_with_service_token_auth(self.test_client, token=self.service_token,
                                                     params={'device_uuid': device.device_uuid})
            self.assertEqual(200, response.status_code)
            self.assertEqual(create_count, len(response.json))
            for json_invitation in response.json:
                self._validate_json(json_invitation)

            # Also test invalid id_device
            response = self._get_with_service_token_auth(self.test_client, token=self.service_token,
                                                    params={'id_device': 0})
            self.assertEqual(200, response.status_code)
            self.assertEqual(0, len(response.json))
            TeraTestType.delete(test_type_accessible.id_test_type)

    def test_get_query_with_id_test_type_with_service_token_returns_only_invitation_for_specific_id_test_type(self):
        """
        Test that a service can access only invitations for a specific test type
        """
        with self._flask_app.app_context():
            create_count = 10
            # Create 10 invitations
            test_type_accessible1 = self._create_test_type_for_service(self.id_service)
            test_type_accessible2 = self._create_test_type_for_service(self.id_service)
            self._create_invitations(create_count, id_test_type=test_type_accessible1.id_test_type, id_user=1)
            self._create_invitations(create_count, id_test_type=test_type_accessible2.id_test_type, id_user=1)

            # Service should access all invitations
            response = self._get_with_service_token_auth(self.test_client, token=self.service_token,
                                                     params={'id_test_type': test_type_accessible1.id_test_type})
            self.assertEqual(200, response.status_code)
            self.assertEqual(create_count, len(response.json))
            for json_invitation in response.json:
                self._validate_json(json_invitation)

            response = self._get_with_service_token_auth(self.test_client, token=self.service_token,
                                                     params={'id_test_type': test_type_accessible2.id_test_type})
            self.assertEqual(200, response.status_code)
            self.assertEqual(create_count, len(response.json))
            for json_invitation in response.json:
                self._validate_json(json_invitation)

            # Also test with test_type_uuid
            response = self._get_with_service_token_auth(self.test_client, token=self.service_token,
                                                        params={'test_type_uuid': test_type_accessible1.test_type_uuid})
            self.assertEqual(200, response.status_code)
            self.assertEqual(create_count, len(response.json))
            for json_invitation in response.json:
                self._validate_json(json_invitation)

            response = self._get_with_service_token_auth(self.test_client, token=self.service_token,
                                                        params={'test_type_uuid': test_type_accessible2.test_type_uuid})
            self.assertEqual(200, response.status_code)
            self.assertEqual(create_count, len(response.json))


            TeraTestType.delete(test_type_accessible1.id_test_type)
            TeraTestType.delete(test_type_accessible2.id_test_type)



    def test_get_query_with_id_session_with_service_token_returns_only_invitation_for_specific_id_session(self):
        """
        Test that service can access only invitations for a specific session
        """
        with self._flask_app.app_context():
            create_count = 10
            # Create 10 invitations
            test_type_accessible = self._create_test_type_for_service(self.id_service)
            self._create_invitations(create_count, id_test_type=test_type_accessible.id_test_type, id_session=1, id_user=1)
            self._create_invitations(create_count, id_test_type=test_type_accessible.id_test_type, id_session=2, id_user=1)

            # Service should access all invitations
            response = self._get_with_service_token_auth(self.test_client, token=self.service_token,
                                                     params={'id_session': 1})
            self.assertEqual(200, response.status_code)
            self.assertEqual(create_count, len(response.json))
            for json_invitation in response.json:
                self._validate_json(json_invitation)

            # Test with session_uuid
            session : TeraSession = TeraSession.get_session_by_id(1)
            response = self._get_with_service_token_auth(self.test_client, token=self.service_token,
                                                        params={'session_uuid': session.session_uuid})
            self.assertEqual(200, response.status_code)
            self.assertEqual(create_count, len(response.json))
            for json_invitation in response.json:
                self._validate_json(json_invitation)


            # Service should access all invitations
            response = self._get_with_service_token_auth(self.test_client, token=self.service_token,
                                                     params={'id_session': 2})
            self.assertEqual(200, response.status_code)
            self.assertEqual(create_count, len(response.json))

            # Test with session_uuid
            session : TeraSession = TeraSession.get_session_by_id(2)
            response = self._get_with_service_token_auth(self.test_client, token=self.service_token,
                                                        params={'session_uuid': session.session_uuid})
            self.assertEqual(200, response.status_code)
            self.assertEqual(create_count, len(response.json))
            for json_invitation in response.json:
                self._validate_json(json_invitation)


            # Also test invalid id_session
            response = self._get_with_service_token_auth(self.test_client, token=self.service_token,
                                                    params={'id_session': 0})
            self.assertEqual(200, response.status_code)
            self.assertEqual(0, len(response.json))
            TeraTestType.delete(test_type_accessible.id_test_type)

    def test_get_query_with_service_token_with_invalid_id_project(self):
        """
        Test that a get request with invalid id_project returns empty list
        """
        with self._flask_app.app_context():
            response = self._get_with_service_token_auth(self.test_client, token=self.service_token,
                                                     params={'id_project': 0})
            self.assertEqual(200, response.status_code)
            self.assertEqual(0, len(response.json))

    def test_get_query_with_service_token_with_valid_id_project(self):
        """
        Test that a get request with invalid id_project returns empty list
        """
        with self._flask_app.app_context():
            create_count = 10
            test_type_accessible = self._create_test_type_for_service(self.id_service)
            self._create_invitations(create_count, id_test_type=test_type_accessible.id_test_type, id_session=1, id_participant=1)
            self._create_invitations(create_count, id_test_type=test_type_accessible.id_test_type, id_session=2, id_participant=2)


            response = self._get_with_service_token_auth(self.test_client, token=self.service_token,
                                                     params={'id_project': 1})
            self.assertEqual(200, response.status_code)
            self.assertEqual(2 * create_count, len(response.json))

    def test_post_query_with_service_token_with_invalid_schema(self):
        """
        Test that a post request with invalid schema returns 400
        """
        with self._flask_app.app_context():
            response = self._post_with_service_token_auth(self.test_client,
                                                      token=self.service_token,
                                                      json={})
            self.assertEqual(400, response.status_code)

    def test_post_query_with_service_token_with_valid_schema_but_empty_array(self):
        """
        Test that a post request with valid schema but empty array returns 400
        """
        with self._flask_app.app_context():
            response = self._post_with_service_token_auth(self.test_client,
                                                      token=self.service_token,
                                                      json=[])
            self.assertEqual(400, response.status_code)

    def test_post_query_with_service_token_with_invalid_array_item_schema(self):
        """
        Test that a post request with invalid array item schema returns 400
        """
        with self._flask_app.app_context():
            response = self._post_with_service_token_auth(self.test_client,
                                                      token=self.service_token,
                                                      json=[{'invalid': 'invalid'}])
            self.assertEqual(400, response.status_code)

    def test_post_query_with_service_token_with_valid_schema_but_empty_array_item(self):
        """
        Test that a post request with valid schema but empty array item returns 400
        """
        with self._flask_app.app_context():
            response = self._post_with_service_token_auth(self.test_client,
                                                      token=self.service_token,
                                                      json={'tests_invitations': []})
            self.assertEqual(400, response.status_code)

    def test_post_query_with_service_token_with_valid_schema_but_invalid_array_item(self):
        """
        Test that a post request with valid schema but empty array item returns 400
        """
        with self._flask_app.app_context():
            response = self._post_with_service_token_auth(self.test_client,
                                                      token=self.service_token,
                                                      json={'tests_invitations': [{'invalid': 'invalid'}]})
            self.assertEqual(400, response.status_code)

    def test_post_query_with_service_token_with_valid_schema_but_missing_id_user_id_participant_id_device(self):
        """
        Test that a post request with valid schema but missing id_user, id_participant, id_device returns 400
        """
        with self._flask_app.app_context():
            response = self._post_with_service_token_auth(self.test_client,
                                                      token=self.service_token,
                                                      json=self._create_tests_invitations_json(id_test_type=1))
            self.assertEqual(400, response.status_code)

    def test_post_query_with_service_token_with_valid_schema_but_invalid_id_user_id_participant_(self):
        """
        Test that a post request with valid schema but invalid id_user, id_participant, id_device returns 403
        """
        with self._flask_app.app_context():
            response = self._post_with_service_token_auth(self.test_client,
                                                      self.service_token,
                                                      json=self._create_tests_invitations_json(id_test_type=1, id_user=0))
            self.assertEqual(403, response.status_code)

            response = self._post_with_service_token_auth(self.test_client,
                                            self.service_token,
                                            json=self._create_tests_invitations_json(id_test_type=1, id_participant=0))
            self.assertEqual(403, response.status_code)


            response = self._post_with_service_token_auth(self.test_client,
                                            self.service_token,
                                            json=self._create_tests_invitations_json(id_test_type=1, id_device=0))
            self.assertEqual(403, response.status_code)

    def test_post_query_with_service_token_with_valid_schema_with_multiple_user_participant_device(self):
        """
        Test that a post request with valid schema with multiple user, participant, device returns 400
        """
        with self._flask_app.app_context():
            response = self._post_with_service_token_auth(self.test_client,
                                                      token=self.service_token,
                                                      json=self._create_tests_invitations_json(id_test_type=1,
                                                                                              id_user=1,
                                                                                              id_participant=1))
            self.assertEqual(400, response.status_code)

            response = self._post_with_service_token_auth(self.test_client,
                                                      token=self.service_token,
                                                      json=self._create_tests_invitations_json(id_test_type=1,
                                                                                              id_user=1,
                                                                                              id_device=1))
            self.assertEqual(400, response.status_code)

            response = self._post_with_service_token_auth(self.test_client,
                                                      token=self.service_token,
                                                      json=self._create_tests_invitations_json(id_test_type=1,
                                                                                              id_user=1,
                                                                                              id_participant=1,
                                                                                              id_device=1))
            self.assertEqual(400, response.status_code)

    def test_post_query_with_service_token_with_valid_schema_with_no_session(self):
        """
        Test that a post request with valid schema with no session returns 200
        """
        with self._flask_app.app_context():
            response = self._post_with_service_token_auth(self.test_client,
                                                      token=self.service_token,
                                                      json=self._create_tests_invitations_json(id_test_type=1,
                                                                                              id_user=1))
            self.assertEqual(200, response.status_code)
            for json_invitation in response.json:
                self._validate_json(json_invitation, with_uuids=True)


    def test_post_query_with_service_token_with_valid_schema_with_invalid_session(self):
        """
        Test that a post request with valid schema with invalid session returns 403
        """
        with self._flask_app.app_context():
            response = self._post_with_service_token_auth(self.test_client,
                                                      token=self.service_token,
                                                      json=self._create_tests_invitations_json(id_test_type=1,
                                                                                              id_user=1,
                                                                                              id_session=0))
            self.assertEqual(403, response.status_code)

    def test_post_query_with_service_token_with_valid_schema_with_valid_session(self):
        """
        Test that a post request with valid schema with valid session returns 200
        """
        with self._flask_app.app_context():

            service_access : DBManagerTeraServiceAccess = DBManagerTeraServiceAccess(TeraService.get_service_by_id(self.id_service))

            for id_session in service_access.get_accessible_sessions_ids():
                response = self._post_with_service_token_auth(self.test_client,
                                                        token=self.service_token,
                                                        json=self._create_tests_invitations_json(id_test_type=1,
                                                                                                id_user=1,
                                                                                                id_session=id_session))
                self.assertEqual(200, response.status_code)
                for json_invitation in response.json:
                    self._validate_json(json_invitation, with_uuids=True)


    def test_post_query_with_service_token_with_valid_schema_update_count(self):
        """
        Test that a post request with valid schema updates count
        """
        with self._flask_app.app_context():
            # Post a new invitation
            response = self._post_with_service_token_auth(self.test_client,
                                                      token=self.service_token,
                                                      json=self._create_tests_invitations_json(id_test_type=1,
                                                                                              id_user=1))
            self.assertEqual(200, response.status_code)
            invitation_info = response.json[0]
            self.assertNotEqual(invitation_info['id_test_invitation'], 0)

            # increment count
            invitation_info['test_invitation_count'] += 1

            # Post the updated invitation
            response = self._post_with_service_token_auth(self.test_client,
                                                        self.service_token,
                                                        json={'tests_invitations': [{'id_test_invitation': invitation_info['id_test_invitation'],
                                                                                    'test_invitation_count': invitation_info['test_invitation_count']}]})
            self.assertEqual(200, response.status_code)
            self.assertEqual(1, len(response.json))
            self.assertEqual(invitation_info['test_invitation_count'], response.json[0]['test_invitation_count'])
            for json_invitation in response.json:
                self._validate_json(json_invitation, with_uuids=True)



    def _create_tests_invitations_json(self, id_test_type: int, id_user: int = None,
                                id_participant: int = None, id_device: int = None, id_session: int = None) -> dict:
        """
        Create a json for an invitation
        """
        tests_invitations = {'tests_invitations': [
                {
                    'id_test_invitation': 0, # New invitation
                    'id_test_type': id_test_type,
                    'test_invitation_max_count': 1,
                    'test_invitation_count': 0,
                    'test_invitation_expiration_date': (datetime.now() + timedelta(days=1)).isoformat()
                } | {k: v for k, v in {'id_user': id_user,
                                       'id_participant': id_participant,
                                       'id_device': id_device,
                                       'id_session': id_session}.items() if v is not None}
            ]}

        return tests_invitations

    def _create_test_type_for_service(self, id_service: int) -> TeraTestType:
        """
        Create a test type for a service
        """
        test_type = TeraTestType(id_test_type=1,
                                test_type_name='TestType',
                                test_type_description='TestType Description',
                                test_type_key='TEST' + str(uuid.uuid4()),
                                id_service=id_service)
        TeraTestType.insert(test_type)
        return test_type


    def _create_invitations(self, count: int,
                            id_test_type: int,
                            id_user: int = None,
                            id_participant: int = None,
                            id_device: int = None,
                            id_session: int = None) -> list[TeraTestInvitation]:
        """
        Create a number of invitations.
        """

        invitations: list[TeraTestInvitation] = []


        # Make sure test type has all required fields
        test_type: TeraTestType = TeraTestType.get_test_type_by_id(id_test_type)
        TeraTestType.update(test_type.id_test_type, {'test_type_has_json_format': True,
                                                     'test_type_has_web_editor': True,
                                                     'test_type_has_web_format': True})

        #  Make sure we have only one of id_user, id_participant, id_device
        if sum(x is not None for x in [id_user, id_participant, id_device]) != 1:
            raise ValueError('Only one of id_user, id_participant, id_device must be set')

        for _ in range(count):
            invitation = TeraTestInvitation(id_test_type=id_test_type,
                                            test_invitation_max_count=1,
                                            test_invitation_count=0,
                                            test_invitation_expiration_date=datetime.now() + timedelta(days=1),
                                            id_user=id_user,
                                            id_participant=id_participant,
                                            id_device=id_device,
                                            id_session=id_session)
            TeraTestInvitation.insert(invitation)
            invitations.append(invitation)

        return invitations

    def _delete_all_invitations(self):
        """
        Delete all invitations
        """
        with self._flask_app.app_context():
            invitations = TeraTestInvitation.query.all()
            for invitation in invitations:
                TeraTestInvitation.delete(invitation.id_test_invitation)

    def _validate_json(self, json: dict, with_uuids: bool = False, with_urls: bool = False):
        """
        Validate a json
        """
        self.assertTrue('id_test_invitation' in json)
        self.assertTrue('id_test_type' in json)
        self.assertTrue('test_invitation_max_count' in json)
        self.assertTrue('test_invitation_count' in json)
        self.assertTrue('test_invitation_expiration_date' in json)
        self.assertTrue('test_invitation_message' in json)
        self.assertTrue('test_invitation_creation_date' in json)
        self.assertTrue('id_user' in json)
        self.assertTrue('id_participant' in json)
        self.assertTrue('id_device' in json)
        self.assertTrue('id_session' in json)
        self.assertTrue('test_invitation_key' in json)

        if with_uuids:
            self.assertTrue('user_uuid' in json)
            self.assertTrue('participant_uuid' in json)
            self.assertTrue('device_uuid' in json)
            self.assertTrue('session_uuid' in json)
            self.assertTrue('test_type_uuid' in json)
        else:
            self.assertTrue('user_uuid' not in json)
            self.assertTrue('participant_uuid' not in json)
            self.assertTrue('device_uuid' not in json)
            self.assertTrue('session_uuid' not in json)
            self.assertTrue('test_type_uuid' not in json)

        if with_urls:
            self.assertTrue('test_invitation_url' in json)
        else:
            self.assertFalse('test_invitation_url' in json)
