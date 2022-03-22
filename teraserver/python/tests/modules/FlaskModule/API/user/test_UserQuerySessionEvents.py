from BaseUserAPITest import BaseUserAPITest
from modules.FlaskModule.FlaskModule import flask_app


class UserQuerySessionEventsTest(BaseUserAPITest):
    test_endpoint = '/api/user/sessions/events'

    def setUp(self):
        super().setUp()
        from modules.FlaskModule.FlaskModule import user_api_ns
        from BaseUserAPITest import FakeFlaskModule
        # Setup minimal API
        from modules.FlaskModule.API.user.UserQuerySessionEvents import UserQuerySessionEvents
        kwargs = {'flaskModule': FakeFlaskModule(config=BaseUserAPITest.getConfig())}
        user_api_ns.add_resource(UserQuerySessionEvents, '/sessions/events', resource_class_kwargs=kwargs)

        # Create test client
        self.test_client = flask_app.test_client()

    def tearDown(self):
        super().tearDown()

    def test_get_endpoint_no_auth(self):
        response = self.test_client.get(self.test_endpoint)
        self.assertEqual(401, response.status_code)

    def test_get_endpoint_invalid_http_auth(self):
        response = self._get_with_user_http_auth(self.test_client)
        self.assertEqual(401, response.status_code)

    def test_get_endpoint_invalid_token_auth(self):
        response = self._get_with_user_token_auth(self.test_client)
        self.assertEqual(401, response.status_code)
