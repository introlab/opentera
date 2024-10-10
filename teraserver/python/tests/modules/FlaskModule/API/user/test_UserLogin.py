from tests.modules.FlaskModule.API.user.BaseUserAPITest import BaseUserAPITest
from opentera.db.models.TeraUser import TeraUser


class UserLoginTest(BaseUserAPITest):
    test_endpoint = '/api/user/login'

    def setUp(self):
        super().setUp()
        # Create users with 2fa enabled
        with self._flask_app.app_context():
            self.user1: dict = self._create_2fa_enabled_user('test_user_2fa_1', 'Password12345!', set_secret=True)
            self.user2: dict = self._create_2fa_enabled_user('test_user_2fa_2', 'Password12345!', set_secret=False)

    def tearDown(self):
        # Delete users with 2fa enabled
        with self._flask_app.app_context():
            TeraUser.delete(self.user1['id_user'], hard_delete=True)
            TeraUser.delete(self.user2['id_user'], hard_delete=True)
        super().tearDown()

    def _create_2fa_enabled_user(self, username, password, set_secret:bool = True):
        user = TeraUser()
        user.id_user = 0 # New user
        user.user_username = username
        user.user_password = password
        user.user_firstname = username
        user.user_lastname = username
        user.user_email = f"{username}@test.com"
        user.user_enabled = True
        user.user_profile = {}
        if set_secret:
            user.enable_2fa_otp()
        else:
            user.user_2fa_enabled = True
            user.user_2fa_otp_enabled = False
            user.user_2fa_otp_secret = None

        TeraUser.insert(user)
        return user.to_json(minimal=False)


    def test_get_endpoint_no_auth(self):
        with self._flask_app.app_context():
            response = self.test_client.get(self.test_endpoint)
            self.assertEqual(401, response.status_code)

    def test_get_endpoint_invalid_token_auth(self):
        with self._flask_app.app_context():
            response = self._get_with_user_token_auth(self.test_client, 'invalid')
            self.assertEqual(401, response.status_code)

    def test_get_endpoint_login_admin_user_http_auth_with_websocket(self):
        with self._flask_app.app_context():
            # Using default participant information
            response = self._get_with_user_http_auth(self.test_client,
                                                     'admin', 'admin',
                                                     {'with_websocket': True})

            self.assertEqual(200, response.status_code)
            self.assertEqual('application/json', response.headers['Content-Type'])
            self.assertGreater(len(response.json), 0)

            # Validate fields in json response
            self.assertTrue('websocket_url' in response.json)
            self.assertTrue('user_uuid' in response.json)
            self.assertTrue('user_token' in response.json)

    def test_get_endpoint_login_admin_user_http_auth_no_websocket(self):
        with self._flask_app.app_context():
            # Using default participant information
            response = self._get_with_user_http_auth(self.test_client, 'admin', 'admin')

            self.assertEqual(200, response.status_code)
            self.assertEqual('application/json', response.headers['Content-Type'])
            self.assertGreater(len(response.json), 0)

            # Validate fields in json response
            self.assertTrue('user_uuid' in response.json)
            self.assertTrue('user_token' in response.json)
            self.assertFalse('websocket_url' in response.json)

    def test_get_endpoint_login_admin_user_http_auth_then_token_auth(self):
        with self._flask_app.app_context():
            # Using default participant information
            response = self._get_with_user_http_auth(self.test_client, 'admin', 'admin')

            self.assertEqual(200, response.status_code)
            self.assertEqual('application/json', response.headers['Content-Type'])
            self.assertGreater(len(response.json), 0)

            # Validate fields in json response
            self.assertTrue('user_token' in response.json)
            token = response.json['user_token']

            # Now try with token authentication
            # Not allowed for this endpoint
            response = self._get_with_user_token_auth(self.test_client, token=token)
            self.assertEqual(401, response.status_code)

    def test_get_endpoint_login_user1_2fa_already_setup(self):
        with self._flask_app.app_context():

            # Login should redirect to 2fa verification
            response = self._get_with_user_http_auth(self.test_client, 'test_user_2fa_1', 'Password12345!')
            self.assertEqual(200, response.status_code)
            self.assertTrue('redirect_url' in response.json)
            self.assertFalse('login_setup_2fa' in response.json['redirect_url'])
            self.assertTrue('login_validate_2fa' in response.json['redirect_url'])

            # Answer should not provide login information
            self.assertFalse('websocket_url' in response.json)
            self.assertFalse('user_uuid' in response.json)
            self.assertFalse('user_token' in response.json)

    def test_get_endpoint_login_user2_2fa_not_setup(self):
        with self._flask_app.app_context():

            # Login should redirect to 2fa verification
            response = self._get_with_user_http_auth(self.test_client, 'test_user_2fa_2', 'Password12345!')
            self.assertEqual(200, response.status_code)
            self.assertTrue('redirect_url' in response.json)
            self.assertTrue('login_setup_2fa' in response.json['redirect_url'])
            self.assertFalse('login_validate_2fa' in response.json['redirect_url'])

            # Answer should not provide login information
            self.assertFalse('websocket_url' in response.json)
            self.assertFalse('user_uuid' in response.json)
            self.assertFalse('user_token' in response.json)
