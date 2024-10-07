from tests.modules.FlaskModule.API.user.BaseUserAPITest import BaseUserAPITest
from opentera.db.models.TeraUser import TeraUser


class UserLoginChangePassword(BaseUserAPITest):
    test_endpoint = '/api/user/login/change_password'

    def setUp(self):
        super().setUp()
        # Create users with password change needed
        with self._flask_app.app_context():
            self.user1: dict = self._create_change_password_user('test_user_1', 'Password12345!')

    def tearDown(self):
        # Delete users with 2fa enabled
        with self._flask_app.app_context():
            TeraUser.delete(self.user1['id_user'], hard_delete=True)
        super().tearDown()

    @staticmethod
    def _create_change_password_user(username, password):
        user = TeraUser()
        user.id_user = 0 # New user
        user.user_username = username
        user.user_password = password
        user.user_firstname = username
        user.user_lastname = username
        user.user_email = f"{username}@test.com"
        user.user_enabled = True
        user.user_profile = {}
        user.user_force_password_change = True

        TeraUser.insert(user)
        return user.to_json(minimal=False)

    def _login_user(self, username, password):
        response = self._get_with_user_http_auth(self.test_client, username, password, endpoint='/api/user/login')
        self.assertEqual(200, response.status_code)
        self.assertEqual('application/json', response.headers['Content-Type'])
        self.assertGreater(len(response.json), 0)
        return response

    def test_post_endpoint_no_auth(self):
        with self._flask_app.app_context():
            response = self.test_client.post(self.test_endpoint)
            self.assertEqual(401, response.status_code)

    def test_post_endpoint_invalid_token_auth(self):
        with self._flask_app.app_context():
            response = self._post_with_user_token_auth(self.test_client, 'invalid')
            self.assertEqual(401, response.status_code)

    def test_post_endpoint_with_no_session(self):
        with self._flask_app.app_context():
            response = self.test_client.post(self.test_endpoint)
            self.assertEqual(401, response.status_code)

    def test_get_endpoint(self):
        with self._flask_app.app_context():
            response = self.test_client.get(self.test_endpoint)
            self.assertEqual(405, response.status_code)

    def test_post_password_without_force_required(self):
        with self._flask_app.app_context():
            # First login to create session
            response = self._login_user('admin', 'admin')
            self.assertEqual(200, response.status_code)
            self.assertFalse('redirect_url' in response.json)

    def test_post_password_change_mismatched(self):
        with self._flask_app.app_context():
            # First login to create session
            response = self._login_user('test_user_1', 'Password12345!')
            self.assertEqual(200, response.status_code)
            self.assertTrue('redirect_url' in response.json)
            self.assertTrue('login_change_password' in response.json['redirect_url'])

            params = {'new_password': 'NewPassword12345!',
                      'confirm_password': 'NotNewPassword12345!'}
            response = self.test_client.post(self.test_endpoint, json=params)
            self.assertEqual(400, response.status_code)

    def test_post_password_change_same_as_old(self):
        with self._flask_app.app_context():
            # First login to create session
            response = self._login_user('test_user_1', 'Password12345!')
            self.assertEqual(200, response.status_code)
            self.assertTrue('redirect_url' in response.json)
            self.assertTrue('login_change_password' in response.json['redirect_url'])

            params = {'new_password': 'Password12345!',
                      'confirm_password': 'Password12345!'}
            response = self.test_client.post(self.test_endpoint, json=params)
            self.assertEqual(400, response.status_code)

    def test_post_password_change_insecure(self):
        with self._flask_app.app_context():
            # First login to create session
            response = self._login_user('test_user_1', 'Password12345!')
            self.assertEqual(200, response.status_code)
            self.assertTrue('redirect_url' in response.json)
            self.assertTrue('login_change_password' in response.json['redirect_url'])

            json_data = {'new_password': 'password', 'confirm_password': 'password'}
            response = self.test_client.post(self.test_endpoint, json=json_data)
            self.assertEqual(400, response.status_code, msg="Password not long enough")

            json_data['new_password'] = 'password12345!'
            json_data['confirm_password'] = json_data['new_password']
            response = self.test_client.post(self.test_endpoint, json=json_data)
            self.assertEqual(400, response.status_code, msg="Password without capital letters")

            json_data['new_password'] = 'PASSWORD12345!'
            json_data['confirm_password'] = json_data['new_password']
            response = self.test_client.post(self.test_endpoint, json=json_data)
            self.assertEqual(400, response.status_code, msg="Password without lower case letters")

            json_data['new_password'] = 'Password12345'
            json_data['confirm_password'] = json_data['new_password']
            response = self.test_client.post(self.test_endpoint, json=json_data)
            self.assertEqual(400, response.status_code, msg="Password without special characters")

            json_data['new_password'] = 'Password!!!!'
            json_data['confirm_password'] = json_data['new_password']
            response = self.test_client.post(self.test_endpoint, json=json_data)
            self.assertEqual(400, response.status_code, msg="Password without numbers")

            json_data['new_password'] = 'Password12345!!'
            json_data['confirm_password'] = json_data['new_password']
            response = self.test_client.post(self.test_endpoint, json=json_data)
            self.assertEqual(200, response.status_code, msg="Password OK")

            # Reset to original password
            user = TeraUser.get_user_by_id(self.user1['id_user'])
            user.user_force_password_change = True
            user.db().session.commit()

            json_data['new_password'] = 'Password12345!'
            json_data['confirm_password'] = json_data['new_password']
            response = self.test_client.post(self.test_endpoint, json=json_data)
            self.assertEqual(200, response.status_code, msg="Password back to last")

    def test_post_password_change_not_required(self):
        with self._flask_app.app_context():
            # First login to create session
            response = self._login_user('test_user_1', 'Password12345!')
            self.assertEqual(200, response.status_code)
            self.assertTrue('redirect_url' in response.json)
            self.assertTrue('login_change_password' in response.json['redirect_url'])

            user = TeraUser.get_user_by_id(self.user1['id_user'])
            user.user_force_password_change = False
            user.db().session.commit()

            json_data = {'new_password': 'Password12345!!', 'confirm_password': 'Password12345!!'}
            response = self.test_client.post(self.test_endpoint, json=json_data)
            self.assertEqual(400, response.status_code, msg="Password not required to be changed")

            user = TeraUser.get_user_by_id(self.user1['id_user'])
            user.user_force_password_change = True
            user.db().session.commit()

    def test_post_password_change_ok(self):
        with self._flask_app.app_context():
            # First login to create session
            response = self._login_user('test_user_1', 'Password12345!')
            self.assertEqual(200, response.status_code)
            self.assertTrue('redirect_url' in response.json)
            self.assertTrue('login_change_password' in response.json['redirect_url'])

            json_data = {'new_password': 'Password12345!!', 'confirm_password': 'Password12345!!'}
            response = self.test_client.post(self.test_endpoint, json=json_data)
            self.assertEqual(200, response.status_code, msg="Password OK")

            # Reset to original password
            user = TeraUser.get_user_by_id(self.user1['id_user'])
            user.user_force_password_change = True
            user.user_password = 'Password12345!'
            user.db().session.commit()