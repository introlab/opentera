from opentera.db.models import TeraSessionTypeServices
from tests.modules.FlaskModule.API.user.BaseUserAPITest import BaseUserAPITest
from opentera.db.models.TeraSessionType import TeraSessionType
from opentera.db.models.TeraService import TeraService
from opentera.db.models.TeraUser import TeraUser
from modules.DatabaseModule.DBManagerTeraUserAccess import DBManagerTeraUserAccess


class UserQuerySessionTypeServicesTest(BaseUserAPITest):
    test_endpoint = '/api/user/sessiontypes/services'

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

    def test_query_forbidden_session_type(self):
        with self._flask_app.app_context():
            params = {'id_session_type': 1}
            response = self._get_with_user_http_auth(self.test_client, params=params,
                                                     username='user4', password='user4')
            self.assertEqual(200, response.status_code)
            self.assertTrue(len(response.json) == 0)

    def test_query_session_type(self):
        with self._flask_app.app_context():
            session_types = TeraSessionType.query.all()
            for session_type in session_types:
                params = {'id_session_type': session_type.id_session_type}
                response = self._get_with_user_http_auth(self.test_client, params=params,
                                                         username='admin', password='admin')
                self.assertEqual(200, response.status_code)
                self.assertTrue(len(response.json) == len(session_type.session_type_secondary_services))
                if len(response.json) > 0:
                    for data in response.json:
                        self._validate_json(data)

    def test_query_session_type_with_services(self):
        with self._flask_app.app_context():
            session_types = TeraSessionType.query.all()
            services = TeraService.query.all()
            user: TeraUser = TeraUser.get_user_by_username('user')
            access = DBManagerTeraUserAccess(user)
            limited_services = access.get_accessible_services()
            for session_type in session_types:
                params = {'id_session_type': session_type.id_session_type, 'with_services': 1}
                response = self._get_with_user_http_auth(self.test_client, params=params,
                                                         username='admin', password='admin')
                self.assertEqual(200, response.status_code)
                self.assertTrue(len(response.json) == len(services))
                response = self._get_with_user_http_auth(self.test_client, params=params,
                                                         username='user', password='user')
                self.assertEqual(200, response.status_code)
                self.assertTrue(len(response.json) == len(limited_services))

    def test_query_session_type_list(self):
        with self._flask_app.app_context():
            session_types = TeraSessionType.query.all()
            for session_type in session_types:
                params = {'id_session_type': session_type.id_session_type, 'list': 1}
                response = self._get_with_user_http_auth(self.test_client, params=params,
                                                         username='admin', password='admin')
                self.assertEqual(200, response.status_code)
                self.assertTrue(len(response.json) == len(session_type.session_type_secondary_services))
                if len(response.json) > 0:
                    for data in response.json:
                        self._validate_json(data, minimal=True)

    def test_post_session_type(self):
        with self._flask_app.app_context():
            # New with minimal infos
            json_data = {}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Missing everything")  # Missing

            json_data = {'session_type': {}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Missing id_session_type")

            json_data = {'session_type': {'id_session_type': 1}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Missing services")

            json_data = {'session_type': {'id_session_type': 1, 'services': []}}
            response = self._post_with_user_http_auth(self.test_client, username='user', password='user',
                                                      json=json_data)
            self.assertEqual(403, response.status_code, msg="Only project/site admins can change things here")

            json_data = {'session_type': {'id_session_type': 5, 'services': []}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Remove from all services OK")

            params = {'id_session_type': 5}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertEqual(0, len(response.json))  # Everything was deleted!

            json_data = {'session_type': {'id_session_type': 5, 'services': [{'id_service': 1},
                                                                             {'id_service': 2},
                                                                             {'id_service': 3}]}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Add all services OK")

            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertEqual(3, len(response.json))  # Everything was added

            json_data = {'session_type': {'id_session_type': 5, 'services': [{'id_service': 1}]}}
            response = self._post_with_user_http_auth(self.test_client, username='siteadmin', password='siteadmin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Remove one service")
            self.assertIsNotNone(TeraSessionTypeServices.get_session_type_service_for_session_type_service(
                session_type_id=5, service_id=1))
            self.assertIsNone(TeraSessionTypeServices.get_session_type_service_for_session_type_service(
                session_type_id=5, service_id=2))

            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertEqual(1, len(response.json))

    def test_post_service(self):
        with self._flask_app.app_context():
            pass
            # Create test types and associate in the db for this test
            # json_type = {
            #     'session_type_name': 'Test Session Type',
            #     'session_type_online': True,
            #     'session_type_color': 'black',
            #     'session_type_category': 2
            # }
            # sestype1 = TeraSessionType()
            # sestype1.from_json(json_type)
            # TeraSessionType.insert(sestype1)
            #
            # sestype2 = TeraSessionType()
            # sestype2.from_json(json_type)
            # TeraSessionType.insert(sestype2)
            #
            # sts1 = TeraSessionTypeSite()
            # sts1.id_session_type = sestype1.id_session_type
            # sts1.id_site = 1
            # TeraSessionTypeSite.insert(sts1)
            #
            # sts2 = TeraSessionTypeSite()
            # sts2.id_session_type = sestype2.id_session_type
            # sts2.id_site = 1
            # TeraSessionTypeSite.insert(sts2)
            #
            # stp1 = TeraSessionTypeProject()
            # stp1.id_session_type = sestype1.id_session_type
            # stp1.id_project = 2
            # TeraSessionTypeProject.insert(stp1)
            #
            # stp2 = TeraSessionTypeProject()
            # stp2.id_session_type = sestype2.id_session_type
            # stp2.id_project = 2
            # TeraSessionTypeProject.insert(stp2)
            #
            # # Project update
            # json_data = {'project': {}}
            # response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
            #                                           json=json_data)
            # self.assertEqual(400, response.status_code, msg="Missing id_project")
            #
            # json_data = {'project': {'id_project': 2}}
            # response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
            #                                           json=json_data)
            # self.assertEqual(400, response.status_code, msg="Missing session types")
            #
            # json_data = {'project': {'id_project': 2, 'sessiontypes': []}}
            # response = self._post_with_user_http_auth(self.test_client, username='user', password='user',
            #                                           json=json_data)
            # self.assertEqual(403, response.status_code, msg="Only site admins can change things here")
            #
            # json_data = {'project': {'id_project': 2, 'sessiontypes': []}}
            # response = self._post_with_user_http_auth(self.test_client, username='siteadmin', password='siteadmin',
            #                                           json=json_data)
            # self.assertEqual(200, response.status_code, msg="Remove all session types OK")
            #
            # params = {'id_project': 2}
            # response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
            #                                          params=params)
            # self.assertEqual(200, response.status_code)
            # self.assertEqual(0, len(response.json))  # Everything was deleted!
            #
            # json_data = {'project': {'id_project': 2, 'sessiontypes': [{'id_session_type': sestype1.id_session_type},
            #                                                            {'id_session_type': sestype2.id_session_type},
            #                                                            {'id_session_type': 10}]}}
            # response = self._post_with_user_http_auth(self.test_client, username='siteadmin', password='siteadmin',
            #                                           json=json_data)
            # self.assertEqual(403, response.status_code,
            #                  msg="One session type not allowed - not part of the site project!")
            #
            # json_data = {'project': {'id_project': 2, 'sessiontypes': [{'id_session_type': sestype1.id_session_type},
            #                                                            {'id_session_type': sestype2.id_session_type}]}}
            # response = self._post_with_user_http_auth(self.test_client, username='siteadmin', password='siteadmin',
            #                                           json=json_data)
            # self.assertEqual(200, response.status_code, msg="New session type association OK")
            #
            # response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
            #                                          params=params)
            # self.assertEqual(200, response.status_code)
            # self.assertEqual(2, len(response.json))  # Everything was added
            #
            # json_data = {'project': {'id_project': 2, 'sessiontypes': [{'id_session_type': sestype1.id_session_type}]}}
            # response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
            #                                           json=json_data)
            # self.assertEqual(200, response.status_code, msg="Remove 1 type")
            # self.assertIsNotNone(TeraSessionTypeProject.get_session_type_project_for_session_type_project(
            #     session_type_id= sestype1.id_session_type, project_id=2))
            # self.assertIsNone(TeraSessionTypeProject.get_session_type_project_for_session_type_project(
            #     session_type_id=sestype2.id_session_type, project_id=2))
            #
            # response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
            #                                          params=params)
            # self.assertEqual(200, response.status_code)
            # self.assertEqual(1, len(response.json))
            #
            # json_data = {'project': {'id_project': 2, 'sessiontypes': []}}
            # response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
            #                                           json=json_data)
            # self.assertEqual(200, response.status_code, msg="Back to initial state")
            #
            # # Delete all created for that
            # TeraSessionTypeSite.delete(sts1.id_session_type_site)
            # TeraSessionTypeSite.delete(sts2.id_session_type_site)
            # TeraSessionType.delete(sestype1.id_session_type)
            # TeraSessionType.delete(sestype2.id_session_type)

    def test_post_session_type_project_and_delete(self):
        with self._flask_app.app_context():
            pass
            # Device-Project update
            # json_data = {'session_type_project': {}}
            # response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
            #                                           json=json_data)
            # self.assertEqual(400, response.status_code, msg="Badly formatted request")
            #
            # json_data = {'session_type_project': {'id_project': 1}}
            # response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
            #                                           json=json_data)
            # self.assertEqual(400, response.status_code, msg="Badly formatted request")
            #
            # json_data = {'session_type_project': {'id_project': 1, 'id_session_type': 1}}
            # response = self._post_with_user_http_auth(self.test_client, username='user', password='user',
            #                                           json=json_data)
            # self.assertEqual(403, response.status_code, msg="Only site admins can change things here")
            #
            # json_data = {'session_type_project': {'id_project': 1, 'id_session_type': 6}}
            # response = self._post_with_user_http_auth(self.test_client, username='siteadmin', password='siteadmin',
            #                                           json=json_data)
            # self.assertEqual(403, response.status_code, msg="Add new association not OK - type not part of the site")
            #
            # json_data = {'session_type_project': {'id_project': 2, 'id_session_type': 3}}
            # response = self._post_with_user_http_auth(self.test_client, username='siteadmin', password='siteadmin',
            #                                           json=json_data)
            # self.assertEqual(200, response.status_code, msg="Add new association OK")
            #
            # params = {'id_project': 2}
            # response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
            #                                          params=params)
            # self.assertEqual(200, response.status_code)
            #
            # current_id = None
            # for dp in response.json:
            #     if dp['id_session_type'] == 3:
            #         current_id = dp['id_session_type_project']
            #         break
            # self.assertFalse(current_id is None)
            #
            # response = self._delete_with_user_http_auth(self.test_client, username='user', password='user',
            #                                             params={'id': current_id})
            # self.assertEqual(403, response.status_code, msg="Delete denied")
            #
            # # Create a session of that type
            # project = TeraProject.get_project_by_id(2)
            # json_data = {
            #     'id_participant': 0,
            #     'id_project': project.id_project,
            #     'participant_name': 'Test Participant'
            # }
            #
            # participant = TeraParticipant()
            # participant.from_json(json_data)
            # TeraParticipant.insert(participant)
            #
            # json_session = {'id_session_type': 3,
            #                 'session_name': 'Session',
            #                 'session_start_datetime': datetime.datetime.now(),
            #                 'session_status': 0,
            #                 'id_creator_participant': participant.id_participant
            #                 }
            # session = TeraSession()
            # session.from_json(json_session)
            # TeraSession.insert(session)
            #
            # json_session = {'id_session_type': 3,
            #                 'session_name': 'Session 2',
            #                 'session_start_datetime': datetime.datetime.now(),
            #                 'session_status': 0
            #                 }
            # session2 = TeraSession()
            # session2.from_json(json_session)
            # TeraSession.insert(session2)
            #
            # ses_participant = TeraSessionParticipants()
            # ses_participant.id_participant = participant.id_participant
            # ses_participant.id_session = session2.id_session
            # TeraSessionParticipants.insert(ses_participant)
            #
            # response = self._delete_with_user_http_auth(self.test_client, username='siteadmin', password='siteadmin',
            #                                             params={'id': current_id})
            # self.assertEqual(500, response.status_code, msg="Has sessions of that type, can't delete")
            #
            # TeraSession.delete(session.id_session)
            #
            # response = self._delete_with_user_http_auth(self.test_client, username='siteadmin', password='siteadmin',
            #                                             params={'id': current_id})
            # self.assertEqual(500, response.status_code, msg="Still has sessions of that type, can't delete")
            #
            # TeraSession.delete(session2.id_session)
            #
            # response = self._delete_with_user_http_auth(self.test_client, username='siteadmin', password='siteadmin',
            #                                             params={'id': current_id})
            # self.assertEqual(200, response.status_code, msg="Delete OK")
            #
            # params = {'id_project': 2}
            # response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
            #                                          params=params)
            # self.assertEqual(200, response.status_code)
            # self.assertEqual(0, len(response.json))
            #
            # TeraParticipant.delete(participant.id_participant)

    def _validate_json(self, json, minimal=False):
        self.assertTrue('id_session_type' in json)
        self.assertTrue('id_session_type_service' in json)
        self.assertTrue('id_service' in json)
        if minimal:
            self.assertFalse('session_type_name' in json)
            self.assertFalse('service_name' in json)
        else:
            self.assertTrue('session_type_name' in json)
            self.assertTrue('service_name' in json)