import unittest
import uuid
from datetime import datetime, timedelta
from flask_restx import Resource, inputs

from opentera.services.ServiceAccessManager import ServiceAccessManager, current_test_invitation
from opentera.db.models.TeraUser import TeraUser
from opentera.db.models.TeraTestType import TeraTestType
from opentera.db.models.TeraTestInvitation import TeraTestInvitation
from tests.opentera.services.FakeService import FakeService, FakeFlaskModule
import tests.opentera.services.utils as utils


class TestQueryWithServiceRoles(Resource):
    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)
        self.test = kwargs.get('test', False)
        self.test_case = kwargs.get('testCase', None)

    @ServiceAccessManager.token_required(allow_dynamic_tokens=True, allow_static_tokens=False)
    @ServiceAccessManager.service_user_roles_required(['test-role'])
    def get(self):
        return 'OK', 200


class TestQueryWithServiceRolesAny(Resource):
    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)
        self.test = kwargs.get('test', False)
        self.test_case = kwargs.get('testCase', None)

    @ServiceAccessManager.token_required(allow_dynamic_tokens=True, allow_static_tokens=False)
    @ServiceAccessManager.service_user_roles_any_required(['test-role1', 'test-role2'])
    def get(self):
        return 'OK', 200


class TestQueryWithServiceRolesAll(Resource):
    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)
        self.test = kwargs.get('test', False)

    @ServiceAccessManager.token_required(allow_dynamic_tokens=True, allow_static_tokens=False)
    @ServiceAccessManager.service_user_roles_all_required(['test-role1', 'test-role2'])
    def get(self):
        return 'OK', 200


class TestQueryWithTestInvitationKey(Resource):
    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)
        self.test = kwargs.get('test', False)

    @ServiceAccessManager.service_test_invitation_required(invitation_key_param_name="test_invitation_key")
    def get(self):

        if current_test_invitation == None:
            return 'No invitation', 400

        return 'OK', 200


class ServiceAccessManagerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.__service = FakeService()

        # Create api endpoint
        # Default arguments
        kwargs = {'flaskModule': cls.__service.flask_module,
                  'test': True}

        # Resources
        cls.__service.flask_module.api.add_resource(TestQueryWithServiceRoles, '/test',
                                                    resource_class_kwargs=kwargs)
        cls.__service.flask_module.api.add_resource(TestQueryWithServiceRolesAny, '/test_any',
                                                    resource_class_kwargs=kwargs)
        cls.__service.flask_module.api.add_resource(TestQueryWithServiceRolesAll, '/test_all',
                                                    resource_class_kwargs=kwargs)
        cls.__service.flask_module.api.add_resource(TestQueryWithTestInvitationKey, '/test_invitations',
                                                    resource_class_kwargs=kwargs)

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_endpoint_no_token(self):
        with self.__service.app_context():
            # No token
            response = self.__service.test_client.get('/api/test')
            self.assertEqual(403, response.status_code)

    def test_endpoint_no_token_any(self):
        with self.__service.app_context():
            # No token
            response = self.__service.test_client.get('/api/test_any')
            self.assertEqual(403, response.status_code)

    def test_endpoint_no_token_all(self):
        with self.__service.app_context():
            # No token
            response = self.__service.test_client.get('/api/test_all')
            self.assertEqual(403, response.status_code)

    def test_endpoint_user_token_with_superadmin(self):
        with self.__service.app_context():
            # User token with no role
            user_token = utils._generate_fake_user_token(roles=[], superadmin=True)
            response = self.__service.test_client.get('/api/test',
                                                      headers={'Authorization': 'OpenTera ' + user_token})
            self.assertEqual(200, response.status_code)

    def test_endpoint_user_token_with_superadmin_any(self):
        with self.__service.app_context():
            # User token with no role
            user_token = utils._generate_fake_user_token(roles=[], superadmin=True)
            response = self.__service.test_client.get('/api/test_any',
                                                      headers={'Authorization': 'OpenTera ' + user_token})
            self.assertEqual(200, response.status_code)

    def test_endpoint_user_token_with_superadmin_all(self):
        with self.__service.app_context():
            # User token with no role
            user_token = utils._generate_fake_user_token(roles=[], superadmin=True)
            response = self.__service.test_client.get('/api/test_all',
                                                      headers={'Authorization': 'OpenTera ' + user_token})
            self.assertEqual(200, response.status_code)

    def test_endpoint_user_token_with_no_role(self):
        with self.__service.app_context():
            # User token with no role
            user_token = utils._generate_fake_user_token(roles=[])
            response = self.__service.test_client.get('/api/test',
                                                      headers={'Authorization': 'OpenTera ' + user_token})
            self.assertEqual(403, response.status_code)

    def test_endpoint_user_token_with_no_role_any(self):
        with self.__service.app_context():
            # User token with no role
            user_token = utils._generate_fake_user_token(roles=[])
            response = self.__service.test_client.get('/api/test_any',
                                                      headers={'Authorization': 'OpenTera ' + user_token})
            self.assertEqual(403, response.status_code)

    def test_endpoint_user_token_with_no_role_all(self):
        with self.__service.app_context():
            # User token with no role
            user_token = utils._generate_fake_user_token(roles=[])
            response = self.__service.test_client.get('/api/test_all',
                                                      headers={'Authorization': 'OpenTera ' + user_token})
            self.assertEqual(403, response.status_code)

    def test_endpoint_user_token_with_required_role(self):
        with self.__service.app_context():
            # User token with no role
            user_token = utils._generate_fake_user_token(roles=['test-role'])
            response = self.__service.test_client.get('/api/test',
                                                      headers={'Authorization': 'OpenTera ' + user_token})
            self.assertEqual(200, response.status_code)

    def test_endpoint_user_token_with_required_role_any(self):
        with self.__service.app_context():
            # User token with no role
            user_token = utils._generate_fake_user_token(roles=['test-role1'])
            response = self.__service.test_client.get('/api/test_any',
                                                      headers={'Authorization': 'OpenTera ' + user_token})
            self.assertEqual(200, response.status_code)

            user_token = utils._generate_fake_user_token(roles=['test-role2'])
            response = self.__service.test_client.get('/api/test_any',
                                                      headers={'Authorization': 'OpenTera ' + user_token})
            self.assertEqual(200, response.status_code)

            user_token = utils._generate_fake_user_token(roles=['test-role1', 'test-role2'])
            response = self.__service.test_client.get('/api/test_any',
                                                      headers={'Authorization': 'OpenTera ' + user_token})
            self.assertEqual(200, response.status_code)

    def test_endpoint_user_token_with_required_role_all(self):
        with self.__service.app_context():
            # User token with no role
            user_token = utils._generate_fake_user_token(roles=['test-role1'])
            response = self.__service.test_client.get('/api/test_all',
                                                      headers={'Authorization': 'OpenTera ' + user_token})
            self.assertEqual(403, response.status_code)

            user_token = utils._generate_fake_user_token(roles=['test-role2'])
            response = self.__service.test_client.get('/api/test_all',
                                                      headers={'Authorization': 'OpenTera ' + user_token})
            self.assertEqual(403, response.status_code)

            user_token = utils._generate_fake_user_token(roles=['test-role1', 'test-role2'])
            response = self.__service.test_client.get('/api/test_all',
                                                      headers={'Authorization': 'OpenTera ' + user_token})
            self.assertEqual(200, response.status_code)

    def test_endpoint_participant_token_should_fail(self):
        with self.__service.app_context():
            # User token with no role
            participant_token = utils._generate_fake_dynamic_participant_token()
            response = self.__service.test_client.get('/api/test',
                                                      headers={'Authorization': 'OpenTera ' + participant_token})
            self.assertEqual(403, response.status_code)

    def test_endpoint_participant_token_should_fail_any(self):
        with self.__service.app_context():
            # User token with no role
            participant_token = utils._generate_fake_dynamic_participant_token()
            response = self.__service.test_client.get('/api/test_any',
                                                      headers={'Authorization': 'OpenTera ' + participant_token})
            self.assertEqual(403, response.status_code)

    def test_endpoint_participant_token_should_fail_all(self):
        with self.__service.app_context():
            # User token with no role
            participant_token = utils._generate_fake_dynamic_participant_token()
            response = self.__service.test_client.get('/api/test_any',
                                                      headers={'Authorization': 'OpenTera ' + participant_token})
            self.assertEqual(403, response.status_code)

    def test_endpoint_invitation_key_with_no_key(self):
        with self.__service.app_context():
            # No key
            response = self.__service.test_client.get('/api/test_invitations')
            self.assertEqual(400, response.status_code)

    def test_endpoint_invitation_key_with_key_for_user(self):
        with self.__service.app_context():
            # Create test type for this service
            test_type : TeraTestType = TeraTestType()
            test_type.test_type_name = 'TestType'
            test_type.test_type_description = 'TestType description'
            test_type.test_type_key = str(uuid.uuid4())
            test_type.id_service = self.__service.get_service_id()
            TeraTestType.insert(test_type)

            # Create test invitation with user
            user_invitation : TeraTestInvitation = TeraTestInvitation()
            user_invitation.id_test_type = test_type.id_test_type
            user_invitation.test_invitation_key = str(uuid.uuid4())
            user_invitation.id_user = 1 # admin
            user_invitation.test_invitation_expiration_date = datetime.now() + timedelta(days=1)
            TeraTestInvitation.insert(user_invitation)

            # Create test invitation with participant
            participant_invitation : TeraTestInvitation = TeraTestInvitation()
            participant_invitation.id_test_type = test_type.id_test_type
            participant_invitation.test_invitation_key = str(uuid.uuid4())
            participant_invitation.id_participant = 1
            participant_invitation.test_invitation_expiration_date = datetime.now() + timedelta(days=1)
            TeraTestInvitation.insert(participant_invitation)

            # Create test invitation with device
            device_invitation : TeraTestInvitation = TeraTestInvitation()
            device_invitation.id_test_type = test_type.id_test_type
            device_invitation.test_invitation_key = str(uuid.uuid4())
            device_invitation.id_device = 1
            device_invitation.test_invitation_expiration_date = datetime.now() + timedelta(days=1)
            TeraTestInvitation.insert(device_invitation)

            # Call API with newly created key
            response = self.__service.test_client.get('/api/test_invitations',
                                                      query_string={'test_invitation_key': user_invitation.test_invitation_key})
            self.assertEqual(200, response.status_code)

            response = self.__service.test_client.get('/api/test_invitations',
                                                      query_string={'test_invitation_key': participant_invitation.test_invitation_key})
            self.assertEqual(200, response.status_code)

            response = self.__service.test_client.get('/api/test_invitations',
                                                        query_string={'test_invitation_key': device_invitation.test_invitation_key})
            self.assertEqual(200, response.status_code)
