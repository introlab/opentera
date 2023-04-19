from BaseUserAPITest import BaseUserAPITest
from opentera.db.models.TeraParticipantGroup import TeraParticipantGroup
from opentera.db.models.TeraParticipant import TeraParticipant
from opentera.db.models.TeraUser import TeraUser
from opentera.db.models.TeraProject import TeraProject
from opentera.db.models.TeraSite import TeraSite
from opentera.db.models.TeraService import TeraService
from opentera.db.models.TeraServiceProject import TeraServiceProject
from opentera.db.models.TeraSessionType import TeraSessionType


class UserQueryFormsTest(BaseUserAPITest):
    test_endpoint = '/api/user/forms'

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test_get_endpoint_no_auth(self):
        with self._flask_app.app_context():
            response = self.test_client.get(self.test_endpoint)
            self.assertEqual(401, response.status_code)

    def test_get_endpoint_invalid_http_auth(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client)
            self.assertEqual(401, response.status_code)

    def test_get_endpoint_invalid_token_auth(self):
        with self._flask_app.app_context():
            response = self._get_with_user_token_auth(self.test_client)
            self.assertEqual(401, response.status_code)

    def test_get_user_form(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'type': 'user'})
            self.assertEqual(200, response.status_code)
            form_data = response.json
            self.assertEqual('user', form_data['objecttype'])

            from opentera.forms.TeraUserForm import TeraUserForm
            compare_data = TeraUserForm.get_user_form()
            self.assertEqual(compare_data, form_data)

    def test_get_site_form(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'type': 'site'})
            self.assertEqual(200, response.status_code)
            form_data = response.json
            self.assertEqual('site', form_data['objecttype'])

            from opentera.forms.TeraSiteForm import TeraSiteForm
            compare_data = TeraSiteForm.get_site_form()
            self.assertEqual(compare_data, form_data)

    def test_get_project_form(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='user3', password='user3',
                                                     params={'type': 'project'})
            self.assertEqual(200, response.status_code)
            form_data = response.json
            self.assertEqual('project', form_data['objecttype'])

            from opentera.forms.TeraProjectForm import TeraProjectForm
            user: TeraUser = TeraUser.get_user_by_username('user3')
            compare_data = TeraProjectForm.get_project_form(user.get_sites_roles().keys())
            self.assertEqual(compare_data, form_data)

    def test_get_device_form(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'type': 'device'})
            self.assertEqual(200, response.status_code)
            form_data = response.json
            self.assertEqual('device', form_data['objecttype'])

            from opentera.forms.TeraDeviceForm import TeraDeviceForm
            compare_data = TeraDeviceForm.get_device_form()
            self.assertEqual(compare_data, form_data)

    def test_get_participant_form_as_admin(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'type': 'participant'})
            self.assertEqual(200, response.status_code)
            form_data = response.json
            self.assertEqual('participant', form_data['objecttype'])

            from opentera.forms.TeraParticipantForm import TeraParticipantForm
            groups = TeraParticipantGroup.query.all()
            compare_data = TeraParticipantForm.get_participant_form(groups)
            self.assertEqual(compare_data, form_data)

            # Now try with specific participant id
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'type': 'participant', 'id': 1})
            self.assertEqual(200, response.status_code)
            form_data = response.json
            participant = TeraParticipant.get_participant_by_id(1)
            groups = TeraParticipantGroup.get_participant_group_for_project(participant.id_project)
            compare_data = TeraParticipantForm.get_participant_form(groups)
            self.assertEqual(compare_data, form_data)

            # And try with a project id
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'type': 'participant', 'id_project': 2})
            self.assertEqual(200, response.status_code)
            form_data = response.json
            groups = TeraParticipantGroup.get_participant_group_for_project(2)
            compare_data = TeraParticipantForm.get_participant_form(groups)
            self.assertEqual(compare_data, form_data)

    def test_get_participant_form_as_user(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='user', password='user',
                                                     params={'type': 'participant'})
            self.assertEqual(200, response.status_code)
            form_data = response.json
            self.assertEqual('participant', form_data['objecttype'])

            from opentera.forms.TeraParticipantForm import TeraParticipantForm
            user: TeraUser = TeraUser.get_user_by_username('user')
            projects = user.get_projects_roles().keys()
            groups = []
            for project in list(projects):
                groups.extend(project.project_participants_groups)
            compare_data = TeraParticipantForm.get_participant_form(groups)
            self.assertEqual(compare_data, form_data)

            # Now try with specific participant id
            response = self._get_with_user_http_auth(self.test_client, username='user', password='user',
                                                     params={'type': 'participant', 'id': 1})
            self.assertEqual(200, response.status_code)
            form_data = response.json
            participant = TeraParticipant.get_participant_by_id(1)
            groups = TeraParticipantGroup.get_participant_group_for_project(participant.id_project)
            compare_data = TeraParticipantForm.get_participant_form(groups)
            self.assertEqual(compare_data, form_data)

            # And try with a project id
            response = self._get_with_user_http_auth(self.test_client, username='user', password='user',
                                                     params={'type': 'participant', 'id_project': 2})
            self.assertEqual(200, response.status_code)
            form_data = response.json
            groups = TeraParticipantGroup.get_participant_group_for_project(2)
            compare_data = TeraParticipantForm.get_participant_form(groups)
            self.assertEqual(compare_data, form_data)

    def test_get_participant_group_form_as_admin(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'type': 'group'})
            self.assertEqual(200, response.status_code)
            form_data = response.json
            self.assertEqual('group', form_data['objecttype'])

            from opentera.forms.TeraParticipantGroupForm import TeraParticipantGroupForm
            projects = TeraProject.query.all()
            compare_data = TeraParticipantGroupForm.get_participant_group_form(projects)
            self.assertEqual(compare_data, form_data)

            # Now try with specific id
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'type': 'group', 'id': 1})
            self.assertEqual(200, response.status_code)
            form_data = response.json
            group = TeraParticipantGroup.get_participant_group_by_id(1)
            projects = group.participant_group_project.project_site.site_projects
            compare_data = TeraParticipantGroupForm.get_participant_group_form(projects)
            self.assertEqual(compare_data, form_data)

            # And try with a related id
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'type': 'group', 'id_site': 2})
            self.assertEqual(200, response.status_code)
            form_data = response.json
            site = TeraSite.get_site_by_id(2)
            projects = []
            for project in site.site_projects:
                projects.append(project)
            compare_data = TeraParticipantGroupForm.get_participant_group_form(projects)
            self.assertEqual(compare_data, form_data)

    def test_get_participant_group_form_as_user(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='user', password='user',
                                                     params={'type': 'group'})
            self.assertEqual(200, response.status_code)
            form_data = response.json
            self.assertEqual('group', form_data['objecttype'])

            from opentera.forms.TeraParticipantGroupForm import TeraParticipantGroupForm
            user: TeraUser = TeraUser.get_user_by_username('user')
            projects = user.get_projects_roles().keys()
            compare_data = TeraParticipantGroupForm.get_participant_group_form(projects)
            self.assertEqual(compare_data, form_data)

            # Now try with specific id
            response = self._get_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                     params={'type': 'group', 'id': 1})
            self.assertEqual(200, response.status_code)
            form_data = response.json
            compare_data = TeraParticipantGroupForm.get_participant_group_form([])
            self.assertEqual(compare_data, form_data)

            response = self._get_with_user_http_auth(self.test_client, username='user3', password='user3',
                                                     params={'type': 'group', 'id': 1})
            self.assertEqual(200, response.status_code)
            form_data = response.json
            user = TeraUser.get_user_by_username('user3')
            projects = user.get_projects_roles().keys()
            compare_data = TeraParticipantGroupForm.get_participant_group_form(projects)
            self.assertEqual(compare_data, form_data)

            # And try with a specific related id
            response = self._get_with_user_http_auth(self.test_client, username='user', password='user',
                                                     params={'type': 'group', 'id_site': 1})
            self.assertEqual(200, response.status_code)
            form_data = response.json
            site = TeraSite.get_site_by_id(1)
            projects = []
            for project in site.site_projects:
                projects.append(project)
            compare_data = TeraParticipantGroupForm.get_participant_group_form(projects)
            self.assertEqual(compare_data, form_data)

    def test_get_session_type_form_as_admin(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'type': 'session_type'})
            self.assertEqual(200, response.status_code)
            form_data = response.json
            self.assertEqual('session_type', form_data['objecttype'])

            from opentera.forms.TeraSessionTypeForm import TeraSessionTypeForm
            services = TeraService.query.all()
            compare_data = TeraSessionTypeForm.get_session_type_form(services)
            self.assertEqual(compare_data, form_data)

    def test_get_session_type_form_as_user(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='user3', password='user3',
                                                     params={'type': 'session_type'})
            self.assertEqual(200, response.status_code)
            form_data = response.json
            self.assertEqual('session_type', form_data['objecttype'])

            from opentera.forms.TeraSessionTypeForm import TeraSessionTypeForm
            user = TeraUser.get_user_by_username('user3')
            projects = user.get_projects_roles().keys()
            services = []
            for project in projects:
                project_services = TeraServiceProject.get_services_for_project(project.id_project)
                services.extend([ps.service_project_service for ps in project_services
                                 if ps.service_project_service not in services])
            compare_data = TeraSessionTypeForm.get_session_type_form(services)
            self.assertEqual(compare_data, form_data)

    def test_get_session_type_config_form(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'type': 'session_type_config'})
            self.assertEqual(400, response.status_code, msg='Missing id_session_type')

            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'type': 'session_type_config', 'id': 1})
            self.assertEqual(200, response.status_code)
            form_data = response.json
            self.assertEqual('session_type_config', form_data['objecttype'])
            self.assertTrue('sections' in form_data)

            # from opentera.forms.TeraSessionTypeConfigForm import TeraSessionTypeConfigForm
            # st: TeraSessionType = TeraSessionType.get_session_type_by_id(1)
            # compare_data = TeraSessionTypeConfigForm.get_session_type_config_form(st)
            # self.assertEqual(compare_data, form_data)

    def test_get_session_form(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'type': 'session'})
            self.assertEqual(200, response.status_code)
            form_data = response.json
            self.assertEqual('session', form_data['objecttype'])

    def test_get_device_type_form(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'type': 'device_type'})
            self.assertEqual(200, response.status_code)
            form_data = response.json
            self.assertEqual('device_type', form_data['objecttype'])

            from opentera.forms.TeraDeviceTypeForm import TeraDeviceTypeForm
            compare_data = TeraDeviceTypeForm.get_device_type_form()
            self.assertEqual(compare_data, form_data)

    def test_get_device_subtype_form(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'type': 'device_subtype'})
            self.assertEqual(200, response.status_code)
            form_data = response.json
            self.assertEqual('device_subtype', form_data['objecttype'])

            from opentera.forms.TeraDeviceSubTypeForm import TeraDeviceSubTypeForm
            compare_data = TeraDeviceSubTypeForm.get_device_subtype_form()
            self.assertEqual(compare_data, form_data)

    def test_get_user_group_form(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'type': 'user_group'})
            self.assertEqual(200, response.status_code)
            form_data = response.json
            self.assertEqual('user_group', form_data['objecttype'])

            from opentera.forms.TeraUserGroupForm import TeraUserGroupForm
            compare_data = TeraUserGroupForm.get_user_group_form()
            self.assertEqual(compare_data, form_data)

    def test_get_service_form(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'type': 'service'})
            self.assertEqual(200, response.status_code)
            form_data = response.json
            self.assertEqual('service', form_data['objecttype'])

            from opentera.forms.TeraServiceForm import TeraServiceForm
            compare_data = TeraServiceForm.get_service_form()
            self.assertEqual(compare_data, form_data)

    def test_get_service_config_form(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'type': 'service_config'})
            self.assertEqual(200, response.status_code)
            form_data = response.json
            self.assertEqual('service_config', form_data['objecttype'])

            from opentera.forms.TeraServiceConfigForm import TeraServiceConfigForm
            compare_data = TeraServiceConfigForm.get_service_config_form()
            self.assertEqual(compare_data, form_data)

            service = TeraService.get_service_by_key('VideoRehabService')
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'type': 'service_config', 'id': service.id_service})
            self.assertEqual(200, response.status_code)
            form_data = response.json
            compare_data = TeraServiceConfigForm.get_service_config_config_form(service.service_key)
            self.assertEqual(compare_data, form_data)

            service = TeraService.get_service_by_key('VideoRehabService')
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'type': 'service_config', 'key': service.service_key})
            self.assertEqual(200, response.status_code)
            form_data = response.json
            self.assertEqual(compare_data, form_data)

            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'type': 'service_config', 'id': 12})
            self.assertEqual(400, response.status_code)

    def tests_get_versions_form(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'type': 'versions'})
            self.assertEqual(200, response.status_code)
            form_data = response.json
            self.assertEqual('versions', form_data['objecttype'])

            from opentera.forms.TeraVersionsForm import TeraVersionsForm
            compare_data = TeraVersionsForm.get_versions_form()
            self.assertEqual(compare_data, form_data)

    def tests_get_test_type_form(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'type': 'test_type'})
            self.assertEqual(200, response.status_code)
            form_data = response.json
            self.assertEqual('test_type', form_data['objecttype'])

            from opentera.forms.TeraTestTypeForm import TeraTestTypeForm
            services = TeraService.query.all()
            compare_data = TeraTestTypeForm.get_test_type_form(services)
            self.assertEqual(compare_data, form_data)

    def tests_unknown_form(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'type': 'unknown'})
            self.assertEqual(400, response.status_code)
