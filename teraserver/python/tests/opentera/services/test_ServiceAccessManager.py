import unittest
from tests.opentera.services.FakeService import FakeService, FakeFlaskModule
from opentera.services.ServiceAccessManager import ServiceAccessManager
import tests.opentera.services.utils as utils
from flask_restx import Resource, inputs


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
            response = self.__service.test_client.get('/test')
            self.assertEqual(403, response.status_code)

    def test_endpoint_no_token_any(self):
        with self.__service.app_context():
            # No token
            response = self.__service.test_client.get('/test_any')
            self.assertEqual(403, response.status_code)

    def test_endpoint_no_token_all(self):
        with self.__service.app_context():
            # No token
            response = self.__service.test_client.get('/test_all')
            self.assertEqual(403, response.status_code)

    def test_endpoint_user_token_with_superadmin(self):
        with self.__service.app_context():
            # User token with no role
            user_token = utils._generate_fake_user_token(roles=[], superadmin=True)
            response = self.__service.test_client.get('/test',
                                                      headers={'Authorization': 'OpenTera ' + user_token})
            self.assertEqual(200, response.status_code)

    def test_endpoint_user_token_with_superadmin_any(self):
        with self.__service.app_context():
            # User token with no role
            user_token = utils._generate_fake_user_token(roles=[], superadmin=True)
            response = self.__service.test_client.get('/test_any',
                                                      headers={'Authorization': 'OpenTera ' + user_token})
            self.assertEqual(200, response.status_code)

    def test_endpoint_user_token_with_superadmin_all(self):
        with self.__service.app_context():
            # User token with no role
            user_token = utils._generate_fake_user_token(roles=[], superadmin=True)
            response = self.__service.test_client.get('/test_all',
                                                      headers={'Authorization': 'OpenTera ' + user_token})
            self.assertEqual(200, response.status_code)

    def test_endpoint_user_token_with_no_role(self):
        with self.__service.app_context():
            # User token with no role
            user_token = utils._generate_fake_user_token(roles=[])
            response = self.__service.test_client.get('/test',
                                                      headers={'Authorization': 'OpenTera ' + user_token})
            self.assertEqual(403, response.status_code)

    def test_endpoint_user_token_with_no_role_any(self):
        with self.__service.app_context():
            # User token with no role
            user_token = utils._generate_fake_user_token(roles=[])
            response = self.__service.test_client.get('/test_any',
                                                      headers={'Authorization': 'OpenTera ' + user_token})
            self.assertEqual(403, response.status_code)

    def test_endpoint_user_token_with_no_role_all(self):
        with self.__service.app_context():
            # User token with no role
            user_token = utils._generate_fake_user_token(roles=[])
            response = self.__service.test_client.get('/test_all',
                                                      headers={'Authorization': 'OpenTera ' + user_token})
            self.assertEqual(403, response.status_code)

    def test_endpoint_user_token_with_required_role(self):
        with self.__service.app_context():
            # User token with no role
            user_token = utils._generate_fake_user_token(roles=['test-role'])
            response = self.__service.test_client.get('/test',
                                                      headers={'Authorization': 'OpenTera ' + user_token})
            self.assertEqual(200, response.status_code)

    def test_endpoint_user_token_with_required_role_any(self):
        with self.__service.app_context():
            # User token with no role
            user_token = utils._generate_fake_user_token(roles=['test-role1'])
            response = self.__service.test_client.get('/test_any',
                                                      headers={'Authorization': 'OpenTera ' + user_token})
            self.assertEqual(200, response.status_code)

            user_token = utils._generate_fake_user_token(roles=['test-role2'])
            response = self.__service.test_client.get('/test_any',
                                                      headers={'Authorization': 'OpenTera ' + user_token})
            self.assertEqual(200, response.status_code)

            user_token = utils._generate_fake_user_token(roles=['test-role1', 'test-role2'])
            response = self.__service.test_client.get('/test_any',
                                                      headers={'Authorization': 'OpenTera ' + user_token})
            self.assertEqual(200, response.status_code)

    def test_endpoint_user_token_with_required_role_all(self):
        with self.__service.app_context():
            # User token with no role
            user_token = utils._generate_fake_user_token(roles=['test-role1'])
            response = self.__service.test_client.get('/test_all',
                                                      headers={'Authorization': 'OpenTera ' + user_token})
            self.assertEqual(403, response.status_code)

            user_token = utils._generate_fake_user_token(roles=['test-role2'])
            response = self.__service.test_client.get('/test_all',
                                                      headers={'Authorization': 'OpenTera ' + user_token})
            self.assertEqual(403, response.status_code)

            user_token = utils._generate_fake_user_token(roles=['test-role1', 'test-role2'])
            response = self.__service.test_client.get('/test_all',
                                                      headers={'Authorization': 'OpenTera ' + user_token})
            self.assertEqual(200, response.status_code)

    def test_endpoint_participant_token_should_fail(self):
        with self.__service.app_context():
            # User token with no role
            participant_token = utils._generate_fake_dynamic_participant_token()
            response = self.__service.test_client.get('/test',
                                                      headers={'Authorization': 'OpenTera ' + participant_token})
            self.assertEqual(403, response.status_code)

    def test_endpoint_participant_token_should_fail_any(self):
        with self.__service.app_context():
            # User token with no role
            participant_token = utils._generate_fake_dynamic_participant_token()
            response = self.__service.test_client.get('/test_any',
                                                      headers={'Authorization': 'OpenTera ' + participant_token})
            self.assertEqual(403, response.status_code)

    def test_endpoint_participant_token_should_fail_all(self):
        with self.__service.app_context():
            # User token with no role
            participant_token = utils._generate_fake_dynamic_participant_token()
            response = self.__service.test_client.get('/test_any',
                                                      headers={'Authorization': 'OpenTera ' + participant_token})
            self.assertEqual(403, response.status_code)
