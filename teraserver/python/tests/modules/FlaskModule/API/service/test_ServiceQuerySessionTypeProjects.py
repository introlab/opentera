import datetime

from tests.modules.FlaskModule.API.service.BaseServiceAPITest import BaseServiceAPITest

from opentera.db.models.TeraSessionTypeProject import TeraSessionTypeProject
from opentera.db.models.TeraTest import TeraTest
from opentera.db.models.TeraSession import TeraSession
from opentera.db.models.TeraSessionType import TeraSessionType
from opentera.db.models.TeraSessionParticipants import TeraSessionParticipants
from opentera.db.models.TeraProject import TeraProject
from opentera.db.models.TeraParticipant import TeraParticipant
from opentera.db.models.TeraTestType import TeraTestType
from opentera.db.models.TeraSessionTypeSite import TeraSessionTypeSite
from opentera.db.models.TeraServiceProject import TeraServiceProject



class ServiceQuerySessionTypeProjectsTest(BaseServiceAPITest):
    test_endpoint = '/api/service/sessiontypes/projects'

    def test_get_endpoint_no_auth(self):
        with self._flask_app.app_context():
            response = self.test_client.get(self.test_endpoint)
            self.assertEqual(401, response.status_code)

    def test_post_endpoint_no_auth(self):
        with self._flask_app.app_context():
            response = self.test_client.post(self.test_endpoint, query_string=None, headers=None, json={})
            self.assertEqual(401, response.status_code)

    def test_delete_no_auth(self):
        with self._flask_app.app_context():
            response = self.test_client.delete(self.test_endpoint)
            self.assertEqual(401, response.status_code)

    def test_get_endpoint_invalid_token_auth(self):
        with self._flask_app.app_context():
            response = self._get_with_service_token_auth(self.test_client, token='invalid')
            self.assertEqual(401, response.status_code)

    def test_post_endpoint_invalid_token_auth(self):
        with self._flask_app.app_context():
            response = self._post_with_service_token_auth(self.test_client, token='invalid')
            self.assertEqual(401, response.status_code)

    def test_query_with_no_params(self):
        with self._flask_app.app_context():
            response = self._get_with_service_token_auth(self.test_client, token=self.service_token)
            self.assertEqual(400, response.status_code)

    def test_query_project(self):
        with self._flask_app.app_context():
            params = {'id_project': 10}
            response = self._get_with_service_token_auth(self.test_client, token=self.service_token, params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(0, len(response.json), 0)

            params = {'id_project': 1}
            response = self._get_with_service_token_auth(self.test_client, token=self.service_token, params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(4, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)

    def test_query_session_type(self):
        with self._flask_app.app_context():
            params = {'id_session_type': 30}  # Invalid
            response = self._get_with_service_token_auth(self.test_client, token=self.service_token, params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(0, len(response.json))

            params = {'id_session_type': 1}
            response = self._get_with_service_token_auth(self.test_client, token=self.service_token, params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(1, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)

    def test_query_session_type_with_sites(self):
        with self._flask_app.app_context():
            params = {'id_session_type': 1, 'with_sites': 1}
            response = self._get_with_service_token_auth(self.test_client, token=self.service_token, params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(1, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)
                self.assertTrue('id_site' in data_item)
                self.assertTrue('site_name' in data_item)

    def test_post_session_type(self):
        with self._flask_app.app_context():
            new_st : TeraSessionType = TeraSessionType()
            new_st.session_type_category = TeraSessionType.SessionCategoryEnum.SERVICE.value
            new_st.session_type_name = "Session Type Test"
            new_st.id_service = self.id_service
            new_st.session_type_color = "#FF0000"
            new_st.session_type_online = True
            new_st.session_type_config = "config"
            new_st.id_service = self.id_service
            TeraSessionType.insert(new_st)

            # New with minimal infos
            json_data = {}
            response = self._post_with_service_token_auth(self.test_client, token=self.service_token, json=json_data)
            self.assertEqual(400, response.status_code, msg="Missing everything")  # Missing

            json_data = {'session_type': {}}
            response = self._post_with_service_token_auth(self.test_client, token=self.service_token, json=json_data)
            self.assertEqual(400, response.status_code, msg="Missing id_session_type")

            json_data = {'session_type': {'id_session_type': 1}}
            response = self._post_with_service_token_auth(self.test_client, token=self.service_token, json=json_data)
            self.assertEqual(400, response.status_code, msg="Missing projects")

            json_data = {'session_type': {'id_session_type': 33, 'projects': []}}
            response = self._post_with_service_token_auth(self.test_client, token=self.service_token, json=json_data)
            self.assertEqual(403, response.status_code, msg="No access to session type")

            session_type: TeraSessionType = TeraSessionType.get_session_type_by_id(new_st.id_session_type)
            self.assertEqual(0, len(session_type.session_type_projects))

            json_data = {'session_type': {'id_session_type': new_st.id_session_type, 'projects': [{'id_project': 1},
                                                                                         {'id_project': 2},
                                                                                         {'id_project': 3}]}}
            response = self._post_with_service_token_auth(self.test_client, token=self.service_token, json=json_data)
            self.assertEqual(403, response.status_code, msg="One project not part of site")

            json_data = {'session_type': {'id_session_type': new_st.id_session_type, 'projects': [{'id_project': 3}]}}
            response = self._post_with_service_token_auth(self.test_client, token=self.service_token, json=json_data)
            self.assertEqual(403, response.status_code, msg="No access to project")

            json_data = {'session_type': {'id_session_type': new_st.id_session_type, 'projects': [{'id_project': 1},
                                                                                         {'id_project': 2}]}}
            response = self._post_with_service_token_auth(self.test_client, token=self.service_token, json=json_data)
            self.assertEqual(403, response.status_code, msg="At least one not associated to site")

            sts : TeraSessionTypeSite = TeraSessionTypeSite()
            sts.id_session_type = new_st.id_session_type
            sts.id_site = 1
            TeraSessionTypeSite.insert(sts)

            json_data = {'session_type': {'id_session_type': new_st.id_session_type, 'projects': [{'id_project': 1}]}}
            response = self._post_with_service_token_auth(self.test_client, token=self.service_token, json=json_data)
            self.assertEqual(200, response.status_code, msg="OK now")

            session_type: TeraSessionType = TeraSessionType.get_session_type_by_id(new_st.id_session_type)
            self.assertEqual(1, len(session_type.session_type_projects))

            json_data = {'session_type': {'id_session_type': new_st.id_session_type, 'projects': []}}
            response = self._post_with_service_token_auth(self.test_client, token=self.service_token, json=json_data)
            self.assertEqual(200, response.status_code, msg="Remove from all projects OK")

            json_data = {'session_type': {'id_session_type': new_st.id_session_type, 'projects': [{'id_project': 1}]}}
            response = self._post_with_service_token_auth(self.test_client, token=self.service_token, json=json_data)
            self.assertEqual(200, response.status_code, msg="Remove one project")

            self.assertIsNone(TeraSessionTypeProject.get_session_type_project_for_session_type_project(project_id=3,
                                                                                              session_type_id=
                                                                                              new_st.id_session_type))
            self.assertIsNone(TeraSessionTypeProject.get_session_type_project_for_session_type_project(project_id=2,
                                                                                              session_type_id=
                                                                                              new_st.id_session_type))
            self.assertIsNotNone(TeraSessionTypeProject.get_session_type_project_for_session_type_project(project_id=1,
                                                                                                 session_type_id=
                                                                                                 new_st.id_session_type))

            TeraSessionType.delete(new_st.id_session_type)

    def test_post_project(self):
        with self._flask_app.app_context():
            # Create test types and associate in the db for this test
            json_session_type = {
                'session_type_name': 'Test Type',
                'id_service': 1,
                'session_type_color': '#FF0000',
                'session_type_online': True,
                'session_type_config': 'config',
                'session_type_category': TeraSessionType.SessionCategoryEnum.SERVICE.value
            }

            st1 = TeraSessionType()
            st1.from_json(json_session_type)
            TeraTestType.insert(st1)

            st2 = TeraSessionType()
            st2.from_json(json_session_type)
            TeraSessionType.insert(st2)

            sts1 = TeraSessionTypeSite()
            sts1.id_session_type = st1.id_session_type
            sts1.id_site = 1
            TeraSessionTypeSite.insert(sts1)

            sts2 = TeraSessionTypeSite()
            sts2.id_session_type = st2.id_session_type
            sts2.id_site = 1
            TeraSessionTypeSite.insert(sts2)

            stp1 = TeraSessionTypeProject()
            stp1.id_session_type = st1.id_session_type
            stp1.id_project = 2
            TeraSessionTypeProject.insert(stp1)

            stp2 = TeraSessionTypeProject()
            stp2.id_session_type = st2.id_session_type
            stp2.id_project = 2
            TeraSessionTypeProject.insert(stp2)

            # Project update
            json_data = {}
            response = self._post_with_service_token_auth(self.test_client, token=self.service_token, json=json_data)
            self.assertEqual(400, response.status_code, msg="Missing project")

            json_data = {'project': {}}
            response = self._post_with_service_token_auth(self.test_client, token=self.service_token, json=json_data)
            self.assertEqual(400, response.status_code, msg="Missing id_project")

            json_data = {'project': {'id_project': 1}}
            response = self._post_with_service_token_auth(self.test_client, token=self.service_token, json=json_data)
            self.assertEqual(400, response.status_code, msg="Missing session types")

            json_data = {'project': {'id_project': 2, 'sessions_types': []}}
            response = self._post_with_service_token_auth(self.test_client, token=self.service_token, json=json_data)
            self.assertEqual(403, response.status_code, msg="No access to project")

            service_project: TeraServiceProject = TeraServiceProject()
            service_project.id_service = self.id_service
            service_project.id_project = 2
            TeraServiceProject.insert(service_project)

            json_data = {'project': {'id_project': 2, 'sessions_types': []}}
            response = self._post_with_service_token_auth(self.test_client, token=self.service_token, json=json_data)
            self.assertEqual(200, response.status_code, msg="Remove all test types OK")

            project: TeraProject = TeraProject.get_project_by_id(2)
            self.assertEqual(0, len(project.project_tests_types))  # Everything was deleted!

            json_data = {'project': {'id_project': 2, 'sessions_types': [{'id_session_type': st1.id_session_type},
                                                                    {'id_session_type': st2.id_session_type},
                                                                    {'id_session_type': 3}]}}
            response = self._post_with_service_token_auth(self.test_client, token=self.service_token, json=json_data)
            self.assertEqual(200, response.status_code, msg="Test type not in site but added")

            json_data = {'project': {'id_project': 2, 'sessions_types': [{'id_session_type': st1.id_session_type},
                                                                    {'id_session_type': st2.id_session_type}]}}
            response = self._post_with_service_token_auth(self.test_client, token=self.service_token, json=json_data)
            self.assertEqual(200, response.status_code, msg="New test type association OK")

            project: TeraProject = TeraProject.get_project_by_id(2)
            self.assertEqual(2, len(project.project_session_types))

            json_data = {'project': {'id_project': 2, 'sessions_types': [{'id_session_type': st1.id_session_type}]}}
            response = self._post_with_service_token_auth(self.test_client, token=self.service_token, json=json_data)
            self.assertEqual(200, response.status_code, msg="Remove 1 type")
            self.assertIsNotNone(TeraSessionTypeProject.
                                 get_session_type_project_for_session_type_project(project_id=2,
                                                                             session_type_id=st1.id_session_type))
            self.assertIsNone(TeraSessionTypeProject.
                              get_session_type_project_for_session_type_project(project_id=2,
                                                                          session_type_id=st2.id_session_type))

            project: TeraProject = TeraProject.get_project_by_id(2)
            self.assertEqual(1, len(project.project_session_types))

            # Delete all created for that test
            TeraSessionTypeSite.delete(sts1.id_session_type_site)
            TeraSessionTypeSite.delete(sts2.id_session_type_site)
            TeraSessionType.delete(st1.id_session_type)
            TeraSessionType.delete(st2.id_session_type)
            TeraServiceProject.delete(service_project.id_service_project)

    def test_post_session_type_project_and_delete(self):
        with self._flask_app.app_context():
            # TestType-Project update
            json_data = {'sessions_types_projects': {}}
            response = self._post_with_service_token_auth(self.test_client, token=self.service_token, json=json_data)
            self.assertEqual(400, response.status_code, msg="Badly formatted request")

            json_data = {'sessions_types_projects': {'id_project': 1}}
            response = self._post_with_service_token_auth(self.test_client, token=self.service_token, json=json_data)
            self.assertEqual(400, response.status_code, msg="Badly formatted request")

            json_data = {'sessions_types_projects': {'id_project': 2, 'id_session_type': 1}}
            response = self._post_with_service_token_auth(self.test_client, token=self.service_token, json=json_data)
            self.assertEqual(403, response.status_code, msg="No access to project")

            json_data = {'sessions_types_projects': {'id_project': 2, 'id_session_type': 1}}
            response = self._post_with_service_token_auth(self.test_client, token=self.service_token, json=json_data)
            self.assertEqual(403, response.status_code, msg="Service no access to project")

            service_project: TeraServiceProject = TeraServiceProject()
            service_project.id_service = self.id_service
            service_project.id_project = 2
            TeraServiceProject.insert(service_project)

            response = self._post_with_service_token_auth(self.test_client, token=self.service_token, json=json_data)
            self.assertEqual(200, response.status_code, msg="Add new association OK")

            params = {'id_project': 2}
            response = self._get_with_service_token_auth(self.test_client, token=self.service_token, params=params)
            self.assertEqual(200, response.status_code)

            current_id = None
            for dp in response.json:
                if dp['id_session_type'] == 1:
                    current_id = dp['id_session_type_project']
                    break
            self.assertFalse(current_id is None)

            # Create a test of that type for a session
            project = TeraProject.get_project_by_id(2)
            json_data = {
                'id_participant': 0,
                'id_project': project.id_project,
                'participant_name': 'Test Participant'
            }

            participant = TeraParticipant()
            participant.from_json(json_data)
            TeraParticipant.insert(participant)

            json_session = {'id_session_type': 1,
                            'session_name': 'Session',
                            'session_start_datetime': datetime.datetime.now(),
                            'session_status': 0,
                            'id_creator_participant': participant.id_participant
                            }
            session = TeraSession()
            session.from_json(json_session)
            TeraSession.insert(session)


            ses_participant = TeraSessionParticipants()
            ses_participant.id_participant = participant.id_participant
            ses_participant.id_session = session.id_session
            TeraSessionParticipants.insert(ses_participant)

            response = self._delete_with_service_token_auth(self.test_client, token=self.service_token,
                                                            params={'id': current_id})
            self.assertEqual(500, response.status_code, msg="Has sessions of that type, can't delete")

            TeraSession.delete(session.id_session)


            response = self._delete_with_service_token_auth(self.test_client, token=self.service_token,
                                                            params={'id': current_id})
            self.assertEqual(200, response.status_code, msg="Delete OK")

            TeraParticipant.delete(participant.id_participant)

            params = {'id_project': 2}
            response = self._get_with_service_token_auth(self.test_client, token=self.service_token, params=params)
            self.assertEqual(200, response.status_code)
            self.assertEqual(TeraSessionTypeProject.query.filter_by(id_project=2).count(), len(response.json))

            TeraServiceProject.delete(service_project.id_service_project)

    def _checkJson(self, json_data, minimal=False):
        self.assertGreater(len(json_data), 0)
        self.assertTrue('id_session_type_project' in json_data)
        self.assertTrue('id_session_type' in json_data)
        self.assertTrue('id_project' in json_data)

        if not minimal:
            self.assertTrue('session_type_name' in json_data)
            self.assertTrue('project_name' in json_data)
        else:
            self.assertFalse('session_type_name' in json_data)
            self.assertFalse('project_name' in json_data)
