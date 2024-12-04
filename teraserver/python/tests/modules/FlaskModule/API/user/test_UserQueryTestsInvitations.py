from datetime import datetime, timedelta
from tests.modules.FlaskModule.API.user.BaseUserAPITest import BaseUserAPITest
from opentera.db.models.TeraTestInvitation import TeraTestInvitation
from opentera.db.models.TeraParticipant import TeraParticipant
from opentera.db.models.TeraUser import TeraUser
from opentera.db.models.TeraDevice import TeraDevice
from opentera.db.models.TeraTestType import TeraTestType
from opentera.db.models.TeraSession import TeraSession

class UserQueryTestsInvitationsTest(BaseUserAPITest):
    """
    Test UserQueryTestsInvitations API
    """
    test_endpoint = '/api/user/tests/invitations'

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

    def test_get_endpoint_invalid_http_auth(self):
        """
        Test that a get request with invalid http auth returns 401
        """
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='invalid', password='invalid')
            self.assertEqual(401, response.status_code)

    def test_get_endpoint_invalid_token_auth(self):
        """
        Test that a get request with invalid token returns 401
        """
        with self._flask_app.app_context():
            response = self._get_with_user_token_auth(self.test_client, token='invalid')
            self.assertEqual(401, response.status_code)

    def test_post_endpoint_invalid_token_auth(self):
        """
        Test that a post request with invalid token returns 401
        """
        with self._flask_app.app_context():
            response = self._post_with_user_token_auth(self.test_client, token='invalid')
            self.assertEqual(401, response.status_code)

    def test_post_endpoint_invalid_http_auth(self):
        """
        Test that a post request with invalid http auth returns 401
        """
        with self._flask_app.app_context():
            response = self._post_with_user_http_auth(self.test_client, username='invalid', password='invalid')
            self.assertEqual(401, response.status_code)

    def test_delete_endpoint_invalid_http_auth(self):
        """
        Test that a delete request with invalid http auth returns 401
        """
        with self._flask_app.app_context():
            response = self._delete_with_user_http_auth(self.test_client, username='invalid', password='invalid')
            self.assertEqual(401, response.status_code)

    def test_delete_endpoint_invalid_token_auth(self):
        """
        Test that a delete request with invalid token returns 401
        """
        with self._flask_app.app_context():
            response = self._delete_with_user_token_auth(self.test_client, token='invalid')
            self.assertEqual(401, response.status_code)

    def test_get_query_bad_params_as_admin(self):
        """
        Bad params should return 400
        """
        with self._flask_app.app_context():
            params = {'id_invalid': 1}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(400, response.status_code)

    def test_get_query_no_params_as_admin_returns_all_accessible_invitations(self):
        """
        Test that an admin can access all invitations
        """
        with self._flask_app.app_context():
            create_count = 10
            # Create 10 invitations
            self._create_invitations(create_count, id_test_type=1, id_user=1)

            # Admin should access all invitations
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin')
            self.assertEqual(200, response.status_code)
            self.assertEqual(create_count, len(response.json))

            # Verify that invitations are not accessible to no access user
            response = self._get_with_user_http_auth(self.test_client, username='user4', password='user4')
            self.assertEqual(200, response.status_code)
            self.assertEqual(0, len(response.json))

    def test_get_query_with_id_test_invitation_or_key_as_admin(self):
        """
        Test that an admin can access an invitation with id_test_invitation or test_invitation_key
        """
        with self._flask_app.app_context():
            create_count = 10
            # Create 10 invitations
            invitations = self._create_invitations(create_count, id_test_type=1, id_user=1)

            # Admin should access all invitations
            for invitation in invitations:
                response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                        params={'id_test_invitation': invitation.id_test_invitation})
                self.assertEqual(200, response.status_code)
                self.assertEqual(1, len(response.json))

                # Also test with test_invitation_key
                response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                        params={'test_invitation_key': invitation.test_invitation_key})
                self.assertEqual(200, response.status_code)
                self.assertEqual(1, len(response.json))

                # Verify that invitations are not accessible to no access user
                response = self._get_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                        params={'id_test_invitation': invitation.id_test_invitation})
                self.assertEqual(200, response.status_code)
                self.assertEqual(0, len(response.json))

            # Also test with invalid id_test_invitation
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                    params={'id_test_invitation': 0})
            self.assertEqual(200, response.status_code)
            self.assertEqual(0, len(response.json))

            # Also test with invalid test_invitation_key
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                    params={'test_invitation_key': 'invalid'})
            self.assertEqual(200, response.status_code)
            self.assertEqual(0, len(response.json))

    def test_get_query_with_id_user_as_admin_returns_only_invitation_for_specific_id_user(self):
        """
        Test that an admin can access only invitations for a specific user
        """
        with self._flask_app.app_context():
            create_count = 10
            # Create 10 invitations
            self._create_invitations(create_count, id_test_type=1, id_user=1)
            self._create_invitations(create_count, id_test_type=1, id_user=2)

            # Admin should access only invitations of id_user=1
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_user': 1})
            self.assertEqual(200, response.status_code)
            self.assertEqual(create_count, len(response.json))

            # Also test with user_uuid
            user = TeraUser.get_user_by_id(1)
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'user_uuid': user.user_uuid})
            self.assertEqual(200, response.status_code)
            self.assertEqual(create_count, len(response.json))

            # Verify that invitations are not accessible to no access user
            response = self._get_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                     params={'id_user': 1})
            self.assertEqual(200, response.status_code)
            self.assertEqual(0, len(response.json))

        # Also test invalid id_user
        response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                params={'id_user': 0})
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, len(response.json))

    def test_get_query_with_id_participant_as_admin_returns_only_invitation_for_specific_id_participant(self):
        """
        Test that an admin can access only invitations for a specific participant
        """
        with self._flask_app.app_context():
            create_count = 10
            # Create 10 invitations
            self._create_invitations(create_count, id_test_type=1, id_participant=1)
            self._create_invitations(create_count, id_test_type=1, id_participant=2)

            # Admin should access all invitations
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_participant': 1})
            self.assertEqual(200, response.status_code)
            self.assertEqual(create_count, len(response.json))

            # Also test with participant_uuid
            participant = TeraParticipant.get_participant_by_id(1)
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'participant_uuid': participant.participant_uuid})
            self.assertEqual(200, response.status_code)
            self.assertEqual(create_count, len(response.json))

            # Verify that invitations are not accessible to no access user
            response = self._get_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                     params={'id_participant': 1})
            self.assertEqual(200, response.status_code)
            self.assertEqual(0, len(response.json))

        # Also test invalid id_participant
        response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                params={'id_participant': 0})
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, len(response.json))

    def test_get_query_with_id_device_as_admin_returns_only_invitation_for_specific_id_device(self):
        """
        Test that an admin can access only invitations for a specific device
        """
        with self._flask_app.app_context():
            create_count = 10
            # Create 10 invitations
            self._create_invitations(create_count, id_test_type=1, id_device=1)
            self._create_invitations(create_count, id_test_type=1, id_device=2)

            # Admin should access all invitations
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_device': 1})
            self.assertEqual(200, response.status_code)
            self.assertEqual(create_count, len(response.json))

            # Also test with device_uuid
            device = TeraDevice.get_device_by_id(1)
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'device_uuid': device.device_uuid})
            self.assertEqual(200, response.status_code)
            self.assertEqual(create_count, len(response.json))

            # Verify that invitations are not accessible to no access user
            response = self._get_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                     params={'id_device': 1})
            self.assertEqual(200, response.status_code)
            self.assertEqual(0, len(response.json))

        # Also test invalid id_device
        response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                params={'id_device': 0})
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, len(response.json))

    def test_get_query_with_id_test_type_as_admin_returns_only_invitation_for_specific_id_test_type(self):
        """
        Test that an admin can access only invitations for a specific test type
        """
        with self._flask_app.app_context():
            create_count = 10
            # Create 10 invitations
            self._create_invitations(create_count, id_test_type=1, id_user=1)
            self._create_invitations(create_count, id_test_type=2, id_user=1)

            # Admin should access all invitations
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_test_type': 1})
            self.assertEqual(200, response.status_code)
            self.assertEqual(create_count, len(response.json))

            # Also test with test_type_uuid
            test_type = TeraTestType.get_test_type_by_id(1)
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                        params={'test_type_uuid': test_type.test_type_uuid})
            self.assertEqual(200, response.status_code)
            self.assertEqual(create_count, len(response.json))

            # Verify that invitations are not accessible to no access user
            response = self._get_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                     params={'id_test_type': 1})
            self.assertEqual(200, response.status_code)
            self.assertEqual(0, len(response.json))

            # Create more invitations with a different user
            self._create_invitations(create_count, id_test_type=1, id_user=2)
            self._create_invitations(create_count, id_test_type=2, id_user=2)

            # Admin should access all invitations of test type 1
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_test_type': 1})
            self.assertEqual(200, response.status_code)
            self.assertEqual(create_count * 2, len(response.json))

    def test_get_query_with_id_session_as_admin_returns_only_invitation_for_specific_id_session(self):
        """
        Test that an admin can access only invitations for a specific session
        """
        with self._flask_app.app_context():
            create_count = 10
            # Create 10 invitations
            self._create_invitations(create_count, id_test_type=1, id_session=1, id_user=1)
            self._create_invitations(create_count, id_test_type=1, id_session=2, id_user=1)

            # Admin should access all invitations
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_session': 1})
            self.assertEqual(200, response.status_code)
            self.assertEqual(create_count, len(response.json))

            # Test with session_uuid
            session = TeraSession.get_session_by_id(1)
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                        params={'session_uuid': session.session_uuid})
            self.assertEqual(200, response.status_code)
            self.assertEqual(create_count, len(response.json))

            # Verify that invitations are not accessible to no access user
            response = self._get_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                     params={'id_session': 1})
            self.assertEqual(200, response.status_code)
            self.assertEqual(0, len(response.json))

        # Also test invalid id_session
        response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                params={'id_session': 0})
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, len(response.json))


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
