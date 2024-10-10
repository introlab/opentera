from tests.modules.FlaskModule.API.user.BaseUserAPITest import BaseUserAPITest
from opentera.db.models.TeraSessionType import TeraSessionType
from opentera.db.models.TeraSessionTypeSite import TeraSessionTypeSite
from opentera.db.models.TeraSessionTypeProject import TeraSessionTypeProject
from opentera.db.models.TeraSite import TeraSite
from opentera.db.models.TeraParticipant import TeraParticipant
from opentera.db.models.TeraSession import TeraSession
from opentera.db.models.TeraSessionParticipants import TeraSessionParticipants
import datetime


class UserQuerySessionTypeSitesTest(BaseUserAPITest):
    test_endpoint = '/api/user/sessiontypes/sites'

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

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
            self.assertEqual(400, response.status_code)

    def test_query_as_user(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='user', password='user')
            self.assertEqual(400, response.status_code)

    def test_query_site_as_admin(self):
        with self._flask_app.app_context():
            params = {'id_site': 10}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(len(response.json), 0)

            params = {'id_site': 2}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(len(response.json), 1)

            for data_item in response.json:
                self._checkJson(json_data=data_item)

    def test_query_site_with_session_types_as_admin(self):
        with self._flask_app.app_context():
            params = {'id_site': 1, 'with_session_type': 1}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(5, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)

    def test_query_session_type_as_admin(self):
        with self._flask_app.app_context():
            params = {'id_session_type': 30}  # Invalid
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(0, len(response.json))

            params = {'id_session_type': 1}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(1, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)

    def test_query_session_type_with_site_as_admin(self):
        with self._flask_app.app_context():
            params = {'id_session_type': 3, 'with_sites': 1}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(2, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)

    def test_query_list_as_admin(self):
        with self._flask_app.app_context():
            params = {'id_site': 1, 'list': 1}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(5, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item, minimal=True)

    def test_query_site_as_user(self):
        with self._flask_app.app_context():
            params = {'id_site': 2}
            response = self._get_with_user_http_auth(self.test_client, username='user', password='user', params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(0, len(response.json))

            params = {'id_site': 1}
            response = self._get_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(0, len(response.json))

            params = {'id_site': 1}
            response = self._get_with_user_http_auth(self.test_client, username='user', password='user', params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(5, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)

    def test_query_site_with_session_types_as_user(self):
        with self._flask_app.app_context():
            params = {'id_site': 1, 'with_session_type': 1}
            response = self._get_with_user_http_auth(self.test_client, username='user', password='user', params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(5, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)

    def test_query_session_type_as_user(self):
        with self._flask_app.app_context():
            params = {'id_session_type': 30}  # Invalid
            response = self._get_with_user_http_auth(self.test_client, username='user', password='user', params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(0, len(response.json))

            params = {'id_session_type': 4}
            response = self._get_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(0, len(response.json))

            params = {'id_session_type': 2}
            response = self._get_with_user_http_auth(self.test_client, username='user', password='user', params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(1, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)

    def test_query_session_type_with_sites_as_user(self):
        with self._flask_app.app_context():
            params = {'id_session_type': 1, 'with_sites': 1}
            response = self._get_with_user_http_auth(self.test_client, username='user', password='user', params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(1, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)

    def test_query_list_as_user(self):
        with self._flask_app.app_context():
            params = {'id_session_type': 1, 'list': 1}

            response = self._get_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(0, len(response.json))

            response = self._get_with_user_http_auth(self.test_client, username='user', password='user', params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(1, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item, minimal=True)

    def test_post_session_type(self):
        with self._flask_app.app_context():
            json_data = {}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Missing everything")  # Missing

            # Update
            json_data = {'session_type': {}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Missing id_session_type")

            json_data = {'session_type': {'id_session_type': 4}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Missing sites")

            json_data = {'session_type': {'id_session_type': 4, 'sites': []}}
            response = self._post_with_user_http_auth(self.test_client, username='user', password='user',
                                                      json=json_data)
            self.assertEqual(403, response.status_code, msg="Only site admins can change things here")

            response = self._post_with_user_http_auth(self.test_client, username='siteadmin', password='siteadmin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Remove from all accessible sites OK")

            params = {'id_session_type': 4}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertEqual(1, len(response.json))  # One should remain in the "top secret" site

            json_data = {'session_type': {'id_session_type': 4, 'sites': []}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Remove from all accessible sites OK")

            params = {'id_session_type': 4}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertEqual(0, len(response.json))  # None remaining now

            json_data = {'session_type': {'id_session_type': 4, 'sites': [{'id_site': 1},
                                                                          {'id_site': 2}]}}
            response = self._post_with_user_http_auth(self.test_client, username='siteadmin', password='siteadmin',
                                                      json=json_data)
            self.assertEqual(403, response.status_code, msg="No access to site 2")

            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="All posted ok")

            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertEqual(2, len(response.json))  # Everything was added

            json_data = {'session_type': {'id_session_type': 4, 'sites': [{'id_site': 1}]}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Remove one site")

            self.assertIsNone(TeraSessionTypeSite.get_session_type_site_for_session_type_and_site(
                session_type_id=4, site_id=2))

            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertEqual(1, len(response.json))

            json_data = {'session_type': {'id_session_type': 4, 'sites': [{'id_site': 1},
                                                                          {'id_site': 2}]}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Add all sites OK")

            # Recreate default associations - projects
            json_data = {'session_type_project': [{'id_session_type': 4, 'id_project': 1}]}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data, endpoint='/api/user/sessiontypes/projects')
            self.assertEqual(200, response.status_code)

    def test_post_site(self):
        with self._flask_app.app_context():
            # Create test types and associate in the db for this test
            json_type = {
                'session_type_name': 'Test Session Type',
                'session_type_online': True,
                'session_type_color': 'black',
                'session_type_category': 2
            }
            sestype1 = TeraSessionType()
            sestype1.from_json(json_type)
            TeraSessionType.insert(sestype1)

            sestype2 = TeraSessionType()
            sestype2.from_json(json_type)
            TeraSessionType.insert(sestype2)

            sts1 = TeraSessionTypeSite()
            sts1.id_session_type = sestype1.id_session_type
            sts1.id_site = 2
            TeraSessionTypeSite.insert(sts1)

            sts2 = TeraSessionTypeSite()
            sts2.id_session_type = sestype2.id_session_type
            sts2.id_site = 2
            TeraSessionTypeSite.insert(sts2)

            json_data = {'site': {}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Missing id_site")

            json_data = {'site': {'id_site': 2}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Missing services")

            json_data = {'site': {'id_site': 2, 'sessiontypes': []}}
            response = self._post_with_user_http_auth(self.test_client, username='user', password='user',
                                                      json=json_data)
            self.assertEqual(403, response.status_code, msg="Only super admins can change things here")

            response = self._post_with_user_http_auth(self.test_client, username='siteadmin', password='siteadmin',
                                                      json=json_data)
            self.assertEqual(403, response.status_code, msg="Only super admins can change things here")

            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Remove all session types OK")

            params = {'id_site': 2}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertEqual(0, len(response.json))  # Everything was deleted!

            json_data = {'site': {'id_site': 2, 'sessiontypes': [{'id_session_type': sestype1.id_session_type},
                                                                 {'id_session_type': sestype2.id_session_type}]}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Add all session types OK")

            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertEqual(2, len(response.json))  # Everything was added

            json_data = {'site': {'id_site': 2, 'sessiontypes': [{'id_session_type': sestype2.id_session_type}]}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Remove 1 session type")

            self.assertIsNone(TeraSessionTypeSite.get_session_type_site_for_session_type_and_site(
                session_type_id=sestype1.id_session_type, site_id=2))

            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertEqual(1, len(response.json))

            TeraSessionType.delete(sestype1.id_session_type)
            TeraSessionType.delete(sestype2.id_session_type)

            json_data = {'site': {'id_site': 2, 'sessiontypes': [{'id_session_type': 4}]}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Back to defaults")
            #
            # # Recreate default associations - projects
            # json_data = {'session_type_project': [{'id_session_type': 1, 'id_project': 1},
            #                                       {'id_session_type': 2, 'id_project': 1},
            #                                       {'id_session_type': 3, 'id_project': 1},
            #                                       {'id_session_type': 4, 'id_project': 1},
            #                                       {'id_session_type': 5, 'id_project': 1}]}
            # response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
            #                                           json=json_data, endpoint='/api/user/sessiontypes/projects')
            # self.assertEqual(200, response.status_code)

    def test_post_session_type_site_and_delete(self):
        with self._flask_app.app_context():
            json_data = {'session_type_site': {}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Badly formatted request")

            json_data = {'session_type_site': {'id_site': 2}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Badly formatted request")

            json_data = {'session_type_site': {'id_site': 2, 'id_session_type': 3}}
            response = self._post_with_user_http_auth(self.test_client, username='user', password='user',
                                                      json=json_data)
            self.assertEqual(403, response.status_code, msg="Only site admins can change things here")

            response = self._post_with_user_http_auth(self.test_client, username='siteadmin', password='siteadmin',
                                                      json=json_data)
            self.assertEqual(403, response.status_code, msg="Not site admin either for that site")

            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Add new association OK")

            params = {'id_site': 2}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertEqual(2, len(response.json))

            current_id = None
            for sp in response.json:
                if sp['id_session_type'] == 3:
                    current_id = sp['id_session_type_site']
                    break
            self.assertFalse(current_id is None)
            params = {'id': current_id}
            response = self._delete_with_user_http_auth(self.test_client, username='user', password='user',
                                                        params=params)
            self.assertEqual(403, response.status_code, msg="Delete denied")

            response = self._delete_with_user_http_auth(self.test_client, username='siteadmin', password='siteadmin',
                                                        params=params)
            self.assertEqual(403, response.status_code, msg="Delete still denied")

            # Try to add a seesion of that type and check that we can't delete it!
            project = TeraSite.get_site_by_id(2).site_projects[0]
            stp1 = TeraSessionTypeProject()
            stp1.id_session_type = 3
            stp1.id_project = project.id_project
            TeraSessionTypeProject.insert(stp1)

            json_data = {
                'id_participant': 0,
                'id_project': project.id_project,
                'participant_name': 'Test Participant'
            }

            participant = TeraParticipant()
            participant.from_json(json_data)
            TeraParticipant.insert(participant)

            json_session = {'id_session_type': 3,
                            'session_name': 'Session',
                            'session_start_datetime': datetime.datetime.now(),
                            'session_status': 0,
                            'id_creator_participant': participant.id_participant
                            }
            session = TeraSession()
            session.from_json(json_session)
            TeraSession.insert(session)

            json_session = {'id_session_type': 3,
                            'session_name': 'Session 2',
                            'session_start_datetime': datetime.datetime.now(),
                            'session_status': 0
                            }
            session2 = TeraSession()
            session2.from_json(json_session)
            TeraSession.insert(session2)

            ses_participant = TeraSessionParticipants()
            ses_participant.id_participant = participant.id_participant
            ses_participant.id_session = session2.id_session
            TeraSessionParticipants.insert(ses_participant)

            response = self._delete_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                        params={'id': current_id})
            self.assertEqual(500, response.status_code, msg="Has tests of that type, can't delete")

            TeraSession.delete(session.id_session)

            response = self._delete_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                        params={'id': current_id})
            self.assertEqual(500, response.status_code, msg="Has tests of that type, can't delete")

            TeraSession.delete(session2.id_session)

            response = self._delete_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                        params=params)
            self.assertEqual(200, response.status_code, msg="Delete OK")

            params = {'id_site': 2}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertEqual(1, len(response.json))  # Back to initial state!

    def _checkJson(self, json_data, minimal=False):
        self.assertGreater(len(json_data), 0)
        self.assertTrue(json_data.__contains__('id_session_type_site'))
        self.assertTrue(json_data.__contains__('id_session_type'))
        self.assertTrue(json_data.__contains__('id_site'))

        if not minimal:
            self.assertTrue(json_data.__contains__('session_type_name'))
            self.assertTrue(json_data.__contains__('site_name'))
        else:
            self.assertFalse(json_data.__contains__('session_type_name'))
            self.assertFalse(json_data.__contains__('site_name'))
