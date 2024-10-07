from tests.modules.FlaskModule.API.user.BaseUserAPITest import BaseUserAPITest
from opentera.db.models.TeraUser import TeraUser
from opentera.db.models.TeraUserGroup import TeraUserGroup
from opentera.db.models.TeraProject import TeraProject
from opentera.db.models.TeraSession import TeraSession
from opentera.db.models.TeraAsset import TeraAsset
from opentera.db.models.TeraTest import TeraTest
from opentera.db.models.TeraSessionUsers import TeraSessionUsers
from opentera.db.models.TeraService import TeraService
import datetime


class UserQueryUsersTest(BaseUserAPITest):
    test_endpoint = '/api/user/users'

    def test_no_auth(self):
        with self._flask_app.app_context():
            response = self.test_client.get(self.test_endpoint)
            self.assertEqual(401, response.status_code)

    def test_post_no_auth(self):
        with self._flask_app.app_context():
            response = self.test_client.post(self.test_endpoint)
            self.assertEqual(401, response.status_code)

    def test_delete_no_auth(self):
        with self._flask_app.app_context():
            response = self.test_client.delete(self.test_endpoint)
            self.assertEqual(401, response.status_code)

    def test_get_endpoint_invalid_http_auth(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='invalid', password='invalid')
            self.assertEqual(401, response.status_code)

    def test_get_endpoint_invalid_token_auth(self):
        with self._flask_app.app_context():
            response = self._get_with_user_token_auth(self.test_client, token='invalid')
            self.assertEqual(401, response.status_code)

    def test_post_endpoint_invalid_token_auth(self):
        with self._flask_app.app_context():
            response = self._post_with_user_token_auth(self.test_client, token='invalid')
            self.assertEqual(401, response.status_code)

    def test_post_endpoint_invalid_http_auth(self):
        with self._flask_app.app_context():
            response = self._post_with_user_http_auth(self.test_client, username='invalid', password='invalid')
            self.assertEqual(401, response.status_code)

    def test_delete_endpoint_invalid_http_auth(self):
        with self._flask_app.app_context():
            response = self._delete_with_user_http_auth(self.test_client, username='invalid', password='invalid')
            self.assertEqual(401, response.status_code)

    def test_delete_endpoint_invalid_token_auth(self):
        with self._flask_app.app_context():
            response = self._delete_with_user_token_auth(self.test_client, token='invalid')
            self.assertEqual(401, response.status_code)

    def test_query_no_params_as_admin(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin')
            self.assertEqual(200, response.status_code)
            target_count = TeraUser.get_count()
            self.assertEqual(target_count, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)

    def test_query_as_user(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='user', password='user')
            user: TeraUser = TeraUser.get_user_by_username('user')
            users_ids = []
            for project in user.get_projects_roles():
                project_users = project.get_users_in_project()
                for user in project_users:
                    if user.id_user not in users_ids:
                        users_ids.append(user.id_user)
            if user.id_user not in users_ids:
                users_ids.append(user.id_user)
            self.assertEqual(len(response.json), len(users_ids))

            for data_item in response.json:
                self._checkJson(json_data=data_item)

    def test_query_list_as_admin(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params="list=true")
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            for data_item in response.json:
                self._checkJson(json_data=data_item, minimal=True)

    def test_query_specific_user_as_admin(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params="id_user=4")
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(1, len(response.json))

            user_uuid = None
            for data_item in response.json:
                self._checkJson(json_data=data_item)
                self.assertEqual(data_item['id_user'], 4)
                user_uuid = data_item['user_uuid']

            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params="user_uuid=" + user_uuid)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(1, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)
                self.assertEqual(data_item['user_uuid'], user_uuid)
                self.assertEqual(data_item['id_user'], 4)

            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params="id_user=4&list=true")
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(1, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item, minimal=True)

            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_user': 3, 'with_usergroups': True})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(1, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)
                self.assertTrue(data_item.__contains__('user_user_groups'))
                target_count = len(TeraUser.get_user_by_id(data_item['id_user']).user_user_groups)
                self.assertEqual(len(data_item["user_user_groups"]), target_count)

    def test_query_specific_user_as_user(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='user', password='user',
                                                     params={'id_user': 1})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(0, len(response.json))

            response = self._get_with_user_http_auth(self.test_client, username='user', password='user',
                                                     params={'id_user': 4})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(1, len(response.json))

            user_uuid = None
            for data_item in response.json:
                self._checkJson(json_data=data_item)
                self.assertEqual(data_item['id_user'], 4)
                user_uuid = data_item['user_uuid']

            response = self._get_with_user_http_auth(self.test_client, username='user', password='user',
                                                     params={'user_uuid': user_uuid})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(1, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)
                self.assertEqual(data_item['user_uuid'], user_uuid)
                self.assertEqual(data_item['id_user'], 4)

    def test_query_specific_usergroup_as_admin(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_user_group': 3})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            target_count = len(TeraUserGroup.get_user_group_by_id(3).user_group_users)
            self.assertEqual(target_count, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)

            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_user_group': 3, 'list': True})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(target_count, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item, minimal=True)

            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_user_group': 3, 'with_usergroups': True})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(target_count, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)
                self.assertTrue(data_item.__contains__('user_user_groups'))

    def test_query_specific_usergroup_as_user(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                     params={'id_user_group': 1})
            self.assertEqual(200, response.status_code)
            json_data = response.json
            self.assertEqual(len(json_data), 0)

            response = self._get_with_user_http_auth(self.test_client, username='user', password='user',
                                                     params={'id_user_group': 1})
            self.assertEqual(200, response.status_code)
            self.assertEqual(1, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)

    def test_query_specific_project(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='user3', password='user3',
                                                     params={'id_project': 1})
            self.assertEqual(200, response.status_code)
            target_count = len(TeraProject.get_project_by_id(1).get_users_in_project(include_site_access=True))
            self.assertEqual(target_count, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)

            response = self._get_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                     params={'id_project': 1})
            self.assertEqual(200, response.status_code)
            self.assertEqual(0, len(response.json))

    def test_query_with_status(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'with_status': 1})
            self.assertEqual(200, response.status_code)
            target_count = TeraUser.get_count()
            self.assertEqual(target_count, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)
                self.assertTrue(data_item.__contains__('user_online'))
                self.assertTrue(data_item.__contains__('user_busy'))

            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'with_status': 1, 'list': 1})
            self.assertEqual(200, response.status_code)
            self.assertEqual(target_count, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item, minimal=True)
                self.assertTrue(data_item.__contains__('user_online'))
                self.assertTrue(data_item.__contains__('user_busy'))

    def test_query_specific_username_as_admin(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'username': 'user3'})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(1, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)
                self.assertEqual(data_item['user_username'], 'user3')

            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'username': 'user3', 'list': True})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(1, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item, minimal=True)

            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'username': 'user3', 'with_usergroups': True})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(1, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)
                self.assertTrue(data_item.__contains__('user_user_groups'))
                self.assertEqual(data_item['user_username'], 'user3')

    def test_query_specific_username_as_user(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='user', password='user',
                                                     params={'username': 'user4'})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(0, len(response.json))

            response = self._get_with_user_http_auth(self.test_client, username='user', password='user',
                                                     params={'username': 'user2'})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(1, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)
                self.assertEqual(data_item['user_username'], 'user2')

    def test_query_self(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'self': True})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(1, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)
                self.assertEqual(data_item['user_username'], 'admin')
                self.assertTrue(data_item.__contains__('projects'))
                self.assertTrue(data_item.__contains__('sites'))

            response = self._get_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                     params={'self': True})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(1, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)
                self.assertEqual(data_item['user_username'], 'user4')
                self.assertTrue(data_item.__contains__('projects'))
                self.assertTrue(data_item.__contains__('sites'))

    def test_password_strength(self):
        with self._flask_app.app_context():
            json_data = {
                'user': {
                    'id_user': 0,
                    'user_username': 'new_test_user',
                    'user_enabled': True,
                    'user_firstname': 'Test',
                    'user_lastname': 'Test',
                    'user_profile': '',
                    'user_user_groups': [{'id_user_group': 3}],
                    'user_password': 'password'
                }
            }
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Password not long enough")

            json_data['user']['user_password'] = 'password12345!'
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Password without capital letters")

            json_data['user']['user_password'] = 'PASSWORD12345!'
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Password without lower case letters")

            json_data['user']['user_password'] = 'Password12345'
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Password without special characters")

            json_data['user']['user_password'] = 'Password!!!!'
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Password without numbers")

            json_data['user']['user_password'] = 'Password12345!'
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Password OK")
            self.assertGreater(len(response.json), 0)
            json_data = response.json[0]
            self._checkJson(json_data)
            current_id = json_data['id_user']

            # Modify password
            json_data = {
                'user': {
                    'id_user': current_id,
                    'user_password': 'password'
                }
            }

            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Password not long enough")

            json_data['user']['user_password'] = 'password12345!'
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Password without capital letters")

            json_data['user']['user_password'] = 'PASSWORD12345!'
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Password without lower case letters")

            json_data['user']['user_password'] = 'Password12345'
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Password without special characters")

            json_data['user']['user_password'] = 'Password!!!!'
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Password without numbers")

            json_data['user']['user_password'] = 'Password12345!!'
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Password OK")

            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Password same as old")

            TeraUser.delete(current_id)

    def test_post_and_delete(self):
        with self._flask_app.app_context():
            json_data = {
                'id_user': 0
            }
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Missing user")

            # New with minimal infos
            json_data = {
                'user': {
                    'user_username': 'admin',
                    'user_enabled': True,
                    'user_firstname': 'Test',
                    'user_lastname': 'Test',
                    'user_profile': ''
                }
            }

            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Missing id_user")

            json_data['user']['id_user'] = 0
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Missing fields")

            json_data['user']['user_password'] = ''
            response = self._post_with_user_http_auth(self.test_client, username='siteadmin', password='siteadmin',
                                                      json=json_data)
            self.assertEqual(403, response.status_code, msg="Missing usergroups")

            json_data['user']['user_user_groups'] = [{'id_user_group': 3}, {'id_user_group': 5}]
            response = self._post_with_user_http_auth(self.test_client, username='siteadmin', password='siteadmin',
                                                      json=json_data)
            self.assertEqual(403, response.status_code, msg="No access to user groups!")

            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Invalid password")

            json_data['user']['user_password'] = 'testTest11*&'
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(response.status_code, 409, msg="Username unavailable")

            json_data['user']['user_username'] = 'selftest'
            response = self._post_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                      json=json_data)
            self.assertEqual(403, response.status_code, msg="Post denied for user")

            response = self._post_with_user_http_auth(self.test_client, username='siteadmin', password='siteadmin',
                                                      json=json_data)
            self.assertEqual(403, response.status_code, msg="No access to usergroup")

            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Post new")
            self.assertGreater(len(response.json), 0)
            json_data = response.json[0]
            self._checkJson(json_data)
            current_id = json_data['id_user']

            json_data = {
                'user': {
                    'id_user': current_id,
                    'user_user_groups': [{'id_user_group': 3}, {'id_user_group': 1}]
                }
            }

            response = self._post_with_user_http_auth(self.test_client, username='siteadmin', password='siteadmin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Changed user groups")

            # Check that user groups where changed, but also included the original one (5)
            user: TeraUser = TeraUser.get_user_by_id(current_id)
            self.assertEqual(3, len(user.user_user_groups))
            for user_group in user.user_user_groups:
                self.assertTrue([1, 3, 5].__contains__(user_group.id_user_group))

            json_data['user']['user_user_groups'] = [{'id_user_group': 3}]
            response = self._post_with_user_http_auth(self.test_client, username='siteadmin', password='siteadmin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Changed user groups")

            # Check that the user group that the user didn't have acces (5) is still there
            user: TeraUser = TeraUser.get_user_by_id(current_id)
            self.assertEqual(2, len(user.user_user_groups))
            for user_group in user.user_user_groups:
                self.assertTrue([3, 5].__contains__(user_group.id_user_group))

            response = self._post_with_user_http_auth(self.test_client, username='user', password='user',
                                                      json=json_data)
            self.assertEqual(403, response.status_code, msg="User can't modify that user")

            json_data['user']['user_username'] = 'selftest2'
            response = self._post_with_user_http_auth(self.test_client, username='siteadmin', password='siteadmin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Can't change user_username")

            del json_data['user']['user_username']
            json_data['user']['user_enabled'] = False
            response = self._post_with_user_http_auth(self.test_client, username='siteadmin', password='siteadmin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Post update OK")
            self.assertGreater(len(response.json), 0)
            json_reply = response.json[0]
            self._checkJson(json_reply)
            self.assertEqual(json_reply['user_enabled'], False)
            self.assertFalse(user.user_enabled)

            response = self._delete_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                        params={'id': current_id})
            self.assertEqual(403, response.status_code, msg="Delete denied")

            # Create elements that will prevent deletion
            json_session = {'id_session_type': 1,
                            'session_name': 'Session #1',
                            'session_start_datetime': datetime.datetime.now(),
                            'session_status': 0
                            }
            session1 = TeraSession()
            session1.from_json(json_session)
            TeraSession.insert(session1)
            json_user_session = {'id_session': session1.id_session,
                                 'id_user': current_id
                                 }
            new_user_session = TeraSessionUsers()
            new_user_session.from_json(json_user_session)
            TeraSessionUsers.insert(new_user_session)
            json_session = {'id_session_type': 1,
                            'session_name': 'Session #2',
                            'session_start_datetime': datetime.datetime.now(),
                            'session_status': 0,
                            'id_creator_user': current_id
                            }
            session2 = TeraSession()
            session2.from_json(json_session)
            TeraSession.insert(session2)
            json_session = {'id_session_type': 1,
                            'session_name': 'Session #3',
                            'session_start_datetime': datetime.datetime.now(),
                            'session_status': 0,
                            }
            session3 = TeraSession()
            session3.from_json(json_session)
            TeraSession.insert(session3)
            json_session = {'id_session_type': 1,
                            'session_name': 'Session #4',
                            'session_start_datetime': datetime.datetime.now(),
                            'session_status': 0,
                            }
            session4 = TeraSession()
            session4.from_json(json_session)
            TeraSession.insert(session4)
            json_test = {'id_test_type': 1,
                         'id_session': session3.id_session,
                         'test_name': 'Test User',
                         'id_user': current_id,
                         'test_datetime': datetime.datetime.now()
                         }
            new_test = TeraTest()
            new_test.from_json(json_test)
            TeraTest.insert(new_test)
            service_uuid = TeraService.get_openteraserver_service().service_uuid
            json_asset = {'id_session': session4.id_session,
                          'id_user': current_id,
                          'asset_name': 'Test User Asset',
                          'asset_type': 'Test asset',
                          'asset_service_uuid': service_uuid}
            new_asset = TeraAsset()
            new_asset.from_json(json_asset)
            TeraAsset.insert(new_asset)

            response = self._delete_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                        params={'id': current_id})
            self.assertEqual(response.status_code, 500, msg="Can't delete, has sessions")

            TeraSession.delete(session1.id_session)
            response = self._delete_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                        params={'id': current_id})
            self.assertEqual(response.status_code, 500, msg="Can't delete, has created sessions")

            TeraSession.delete(session2.id_session)
            response = self._delete_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                        params={'id': current_id})
            self.assertEqual(response.status_code, 500, msg="Can't delete, has assets")
            TeraAsset.delete(new_asset.id_asset)

            response = self._delete_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                        params={'id': current_id})
            self.assertEqual(response.status_code, 500, msg="Can't delete, has tests")
            TeraTest.delete(new_test.id_test)

            response = self._delete_with_user_http_auth(self.test_client, username='siteadmin', password='siteadmin',
                                                        params={'id': current_id})
            self.assertEqual(200, response.status_code, msg="Deleted groups, but not user = OK")
            self.assertIsNotNone(TeraUser.get_user_by_id(current_id))

            response = self._delete_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                        params={'id': current_id})
            self.assertEqual(200, response.status_code, msg="Deleted user completely")
            self.assertIsNone(TeraUser.get_user_by_id(current_id))

    def _checkJson(self, json_data, minimal=False):
        self.assertGreater(len(json_data), 0)
        self.assertTrue(json_data.__contains__('id_user'))
        self.assertTrue(json_data.__contains__('user_enabled'))
        self.assertTrue(json_data.__contains__('user_firstname'))
        self.assertTrue(json_data.__contains__('user_lastname'))
        self.assertTrue(json_data.__contains__('user_name'))
        self.assertTrue(json_data.__contains__('user_uuid'))

        if minimal:
            self.assertFalse(json_data.__contains__('user_email'))
            self.assertFalse(json_data.__contains__('user_lastonline'))
            self.assertFalse(json_data.__contains__('user_notes'))
            self.assertFalse(json_data.__contains__('user_profile'))
            self.assertFalse(json_data.__contains__('user_username'))
        else:
            self.assertTrue(json_data.__contains__('user_email'))
            self.assertTrue(json_data.__contains__('user_lastonline'))
            self.assertTrue(json_data.__contains__('user_notes'))
            self.assertTrue(json_data.__contains__('user_profile'))
            self.assertTrue(json_data.__contains__('user_username'))
