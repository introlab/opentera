from tests.opentera.db.models.BaseModelsTest import BaseModelsTest
from sqlalchemy import exc
from opentera.db.models.TeraService import TeraService
from opentera.db.models.TeraServiceSite import TeraServiceSite
from opentera.db.models.TeraServiceProject import TeraServiceProject
from opentera.db.models.TeraServiceRole import TeraServiceRole


class TeraServiceTest(BaseModelsTest):

    def test_nullable_args(self):
        with self._flask_app.app_context():
            new_service = TeraService()
            new_service.service_name = 'Name'
            new_service.service_key = 'Key'
            new_service.service_hostname = 'Hostname'
            new_service.service_port = 1
            new_service.service_endpoint = "Endpoint"
            new_service.service_clientendpoint = 'Clientendpoint'
            new_service.service_enabled = True
            new_service.service_system = True
            new_service.service_editable_config = True
            self.db.session.add(new_service)
            self.assertRaises(exc.IntegrityError, self.db.session.commit)
            self.db.session.rollback()

            new_service.service_uuid = 'Uuid'
            new_service.service_name = None
            self.db.session.add(new_service)
            self.assertRaises(exc.IntegrityError, self.db.session.commit)
            self.db.session.rollback()

            new_service.service_name = 'Name'
            new_service.service_hostname = None
            self.db.session.add(new_service)
            self.assertRaises(exc.IntegrityError, self.db.session.commit)
            self.db.session.rollback()

            new_service.service_hostname = 'Hostname'
            new_service.service_port = None
            self.db.session.add(new_service)
            self.assertRaises(exc.IntegrityError, self.db.session.commit)
            self.db.session.rollback()

            new_service.service_port = 1
            new_service.service_endpoint = None
            self.db.session.add(new_service)
            self.assertRaises(exc.IntegrityError, self.db.session.commit)
            self.db.session.rollback()

            new_service.service_endpoint = 'Endpoint'
            new_service.service_clientendpoint = None
            self.db.session.add(new_service)
            self.assertRaises(exc.IntegrityError, self.db.session.commit)

    def test_nullable_bool1(self):
        with self._flask_app.app_context():
            #testing bool service_enabled
            new_service = TeraService()
            new_service.service_name = 'Name'
            new_service.service_key = 'Key'
            new_service.service_hostname = 'Hostname'
            new_service.service_port = 1
            new_service.service_endpoint = "Endpoint"
            new_service.service_clientendpoint = 'Clientendpoint'
            new_service.service_system = True
            new_service.service_editable_config = True
            new_service.service_enabled = None
            self.db.session.add(new_service)
            self.assertRaises(exc.IntegrityError, self.db.session.commit)

    def test_nullable_bool2(self):
        with self._flask_app.app_context():
            # testing bool service_system
            new_service = TeraService()
            new_service.service_name = 'Name'
            new_service.service_key = 'Key'
            new_service.service_hostname = 'Hostname'
            new_service.service_port = 1
            new_service.service_endpoint = "Endpoint"
            new_service.service_clientendpoint = 'Clientendpoint'
            new_service.service_enabled = False
            new_service.service_editable_config = True

            new_service.service_system = None
            self.db.session.add(new_service)
            self.assertRaises(exc.IntegrityError, self.db.session.commit)

    def test_nullable_bool3(self):
        with self._flask_app.app_context():
            # testing bool service_editable_config
            new_service = TeraService()
            new_service.service_name = 'Name'
            new_service.service_key = 'Key'
            new_service.service_hostname = 'Hostname'
            new_service.service_port = 1
            new_service.service_endpoint = "Endpoint"
            new_service.service_clientendpoint = 'Clientendpoint'
            new_service.service_system = True
            new_service.service_enabled = False

            new_service.service_editable_config = None
            self.db.session.add(new_service)
            self.assertRaises(exc.IntegrityError, self.db.session.commit)

    def test_unique_args_uuid(self):
        with self._flask_app.app_context():
            new_service = TeraService()
            same_service = TeraService()

            new_service.service_name = 'Name'
            new_service.service_key = 'Key'
            new_service.service_hostname = 'Hostname'
            new_service.service_port = 1
            new_service.service_endpoint = "Endpoint"
            new_service.service_clientendpoint = 'Clientendpoint'
            new_service.service_enabled = True
            new_service.service_system = True
            new_service.service_editable_config = True

            same_service.service_name = 'Same Name'
            same_service.service_key = 'Same Key'
            same_service.service_hostname = 'Same Hostname'
            same_service.service_port = 2
            same_service.service_endpoint = "Same Endpoint"
            same_service.service_clientendpoint = 'Same Clientendpoint'
            same_service.service_enabled = True
            same_service.service_system = True
            same_service.service_editable_config = True

            new_service.service_uuid = 'uuid'
            same_service.service_uuid = 'uuid'
            self.db.session.add(new_service)
            self.db.session.add(same_service)
            self.assertRaises(exc.IntegrityError, self.db.session.commit)

    def test_unique_args_service_key(self):
        with self._flask_app.app_context():
            new_service = TeraService()
            same_service = TeraService()

            new_service.service_uuid = 'uuid'
            new_service.service_name = 'Name'
            new_service.service_hostname = 'Hostname'
            new_service.service_port = 1
            new_service.service_endpoint = "Endpoint"
            new_service.service_clientendpoint = 'Clientendpoint'
            new_service.service_enabled = True
            new_service.service_system = True
            new_service.service_editable_config = True

            same_service.service_uuid = 'Same uuid'
            same_service.service_name = 'Same Name'
            same_service.service_hostname = 'Same Hostname'
            same_service.service_port = 2
            same_service.service_endpoint = "Same Endpoint"
            same_service.service_clientendpoint = 'Same Clientendpoint'
            same_service.service_enabled = True
            same_service.service_system = True
            same_service.service_editable_config = True

            new_service.service_key = 'key'
            same_service.service_key = 'key'
            self.db.session.add(new_service)
            self.db.session.add(same_service)
            self.assertRaises(exc.IntegrityError, self.db.session.commit)

    def test_service_port_integer(self):
        with self._flask_app.app_context():
            new_service = TeraService()
            new_service.service_uuid = 'uuid'
            new_service.service_name = 'Name'
            new_service.service_key = 'key'
            new_service.service_hostname = 'Hostname'
            new_service.service_port = 3
            new_service.service_endpoint = "Endpoint"
            new_service.service_clientendpoint = 'Clientendpoint'
            new_service.service_enabled = 'not a bool'
            new_service.service_system = True
            new_service.service_editable_config = True
            self.db.session.add(new_service)
            self.assertRaises(exc.StatementError, self.db.session.commit)

    def test_service_system_integer(self):
        with self._flask_app.app_context():
            new_service = TeraService()
            new_service.service_uuid = 'uuid'
            new_service.service_name = 'Name'
            new_service.service_key = 'key'
            new_service.service_hostname = 'Hostname'
            new_service.service_port = 3
            new_service.service_endpoint = "Endpoint"
            new_service.service_clientendpoint = 'Clientendpoint'
            new_service.service_enabled = False
            new_service.service_system = 'not a bool'
            new_service.service_editable_config = True
            self.db.session.add(new_service)
            self.assertRaises(exc.StatementError, self.db.session.commit)

    def test_service_editable_config_integer(self):
        with self._flask_app.app_context():
            new_service = TeraService()
            new_service.service_uuid = 'uuid'
            new_service.service_name = 'Name'
            new_service.service_key = 'key'
            new_service.service_hostname = 'Hostname'
            new_service.service_port = 3
            new_service.service_endpoint = "Endpoint"
            new_service.service_clientendpoint = 'Clientendpoint'
            new_service.service_enabled = False
            new_service.service_system = False
            new_service.service_editable_config = 15
            self.db.session.add(new_service)
            self.assertRaises(exc.StatementError, self.db.session.commit)

    def test_service_to_json(self):
        with self._flask_app.app_context():
            new_service = TeraService()
            new_service.service_uuid = 'UUID'
            new_service.service_key = 'KEY'
            new_service.service_hostname = 'HOSTNAME'
            new_service.service_port = 1234
            new_service.service_endpoint = 'ENDPOINT'
            new_service.service_clientendpoint = 'CLIENTENDPOINT'
            new_service.service_endpoint_user = 'USER'
            new_service.service_endpoint_participant = 'PARTICIPANT'
            new_service.service_endpoint_device = 'DEVICE'
            new_service.service_enabled = True
            new_service.service_system = True
            new_service.service_editable_config = True
            new_service.service_default_config = 'DEFAULT CONFIG'
            json_values = new_service.to_json()
            json_minimal = new_service.to_json(minimal=True)
            TeraServiceTest._check_json(self, service=new_service, json_data=json_values)
            TeraServiceTest._check_json(self, service=new_service, json_data=json_minimal, minimal=True)

    def _check_json(self, service, json_data, minimal=False):
        self.assertEqual(json_data['service_uuid'], service.service_uuid)
        self.assertEqual(json_data['service_name'], service.service_name)
        self.assertEqual(json_data['service_key'], service.service_key)
        self.assertEqual(json_data['service_hostname'], service.service_hostname)
        self.assertEqual(json_data['service_port'], service.service_port)
        self.assertEqual(json_data['service_endpoint'], service.service_endpoint)
        self.assertEqual(json_data['service_clientendpoint'], service.service_clientendpoint)
        self.assertEqual(json_data['service_endpoint_participant'], service.service_endpoint_participant)
        self.assertEqual(json_data['service_endpoint_device'], service.service_endpoint_device)
        self.assertEqual(json_data['service_endpoint_user'], service.service_endpoint_user)
        self.assertEqual(json_data['service_enabled'], service.service_enabled)
        self.assertEqual(json_data['service_system'], service.service_system)
        self.assertEqual(json_data['service_editable_config'], service.service_editable_config)
        self.assertEqual(json_data['service_enabled'], service.service_enabled)
        if minimal:
            self.assertFalse('service_default_config' in json_data)
            self.assertFalse('service_roles' in json_data)
            self.assertFalse('service_projects' in json_data)
        else:
            self.assertEqual(json_data['service_default_config'], service.service_default_config)
            self.assertEqual(json_data['service_roles'], [])
            self.assertEqual(json_data['service_projects'], [])

    def test_service_get_token(self):
        with self._flask_app.app_context():
            new_service = TeraService()
            token = new_service.get_token(token_key='A key')
            token1 = new_service.get_token(token_key='123456')
            token2 = new_service.get_token(token_key='#% @f w346')
            self.assertIsNotNone(token)
            self.assertIsNotNone(token1)
            self.assertIsNotNone(token2)

    def test_service_get_functions(self):
        with self._flask_app.app_context():
            new_service = TeraService()
            new_service.service_uuid = 'uuid'
            new_service.service_name = 'Name'
            new_service.service_key = 'Key'
            new_service.service_hostname = 'Hostname'
            new_service.service_port = 1
            new_service.service_endpoint = "Endpoint"
            new_service.service_clientendpoint = 'Clientendpoint'
            new_service.service_enabled = True
            new_service.service_system = True
            new_service.service_editable_config = True
            self.db.session.add(new_service)
            self.db.session.commit()
            key_none = TeraService.get_service_by_key(key='Not a real key')
            key_present = TeraService.get_service_by_key(key='Key')
            uuid_none = TeraService.get_service_by_uuid(p_uuid='Not a real uuid')
            uuid_present = TeraService.get_service_by_uuid(p_uuid='uuid')
            name_none = TeraService.get_service_by_name(name='Not a real name')
            name_present = TeraService.get_service_by_name(name='Name')
            id_none = TeraService.get_service_by_id(s_id='Not a real id')
            id_present = TeraService.get_service_by_id(s_id=new_service.id_service)
            self.assertEqual(new_service, key_present)
            self.assertIsNone(key_none)
            self.assertEqual(new_service, uuid_present)
            self.assertIsNone(uuid_none)
            self.assertEqual(new_service, name_present)
            self.assertIsNone(name_none)
            self.assertEqual(new_service, id_present)
            self.assertIsNone(id_none)

    def test_service_get_openteraserver_service(self):
        with self._flask_app.app_context():
            openteraservice = TeraService.get_openteraserver_service()
            self.assertEqual(openteraservice.service_key, openteraservice.service_key)

    def test_service_insert(self):
        import uuid
        with self._flask_app.app_context():
            new_service = TeraService()
            # new_service.service_uuid = str(uuid.uuid4())
            new_service.service_name = 'Name'
            new_service.service_key = 'Key-Insert'
            new_service.service_hostname = 'Hostname'
            new_service.service_port = 1
            new_service.service_endpoint = "Endpoint"
            new_service.service_clientendpoint = 'Clientendpoint'
            new_service.service_enabled = True
            new_service.service_system = True
            new_service.service_editable_config = True
            TeraService.insert(new_service)
            same_service = TeraService.get_service_by_uuid(new_service.service_uuid)
            self.assertEqual(same_service, new_service)

    def test_service_uuid_string(self):
        """
        # SQLite does not enforce the length of a VARCHAR. You can declare a VARCHAR(10) and SQLite will be happy to store
        # a 500-million character string there. And it will keep all 500-million characters intact.
        # Your content is never truncated. SQLite understands the column type of "VARCHAR(N)" to be the same as
        # "TEXT", regardless of the value of N.
        #
        """
        return
        # with self._flask_app.app_context():
        #     new_service = TeraService()
        #     new_service.service_uuid = 'Definitely longer than a 36 characters string'
        #     new_service.service_name = 'Name'
        #     new_service.service_key = 'key'
        #     new_service.service_hostname = 'Hostname'
        #     new_service.service_port = 2
        #     new_service.service_endpoint = "Endpoint"
        #     new_service.service_clientendpoint = 'Clientendpoint'
        #     new_service.service_enabled = True
        #     new_service.service_system = True
        #     new_service.service_editable_config = True
        #     self.db.session.add(new_service)
        #     self.db.session.commit()
        #     self.assertRaises(exc.IntegrityError, self.db.session.commit)

    def test_service_port_integer_value(self):
        """
        #
        # SQLite uses what it calls a dynamic typing system, which ultimately means that you can store text
        # in integer fields - in Oracle, SQL Server and all the other big hitters in the database world,
        # attempts to do this will fail - not with SQLite.
        """
        return
        # with self._flask_app.app_context():
        #     new_service = TeraService()
        #
        #     new_service.service_uuid = 'uuid'
        #     new_service.service_name = 'Name'
        #     new_service.service_key = 'key'
        #     new_service.service_hostname = 'Hostname'
        #
        #     new_service.service_port = 'not an integer'
        #
        #     new_service.service_endpoint = "Endpoint"
        #     new_service.service_clientendpoint = 'Clientendpoint'
        #     new_service.service_enabled = True
        #     new_service.service_system = True
        #     new_service.service_editable_config = True
        #     self.db.session.add(new_service)
        #     self.db.session.commit()

    def test_soft_delete(self):
        with self._flask_app.app_context():
            # Create new
            service = TeraServiceTest.new_test_service('TestService')
            self.assertIsNotNone(service.id_service)
            id_service = service.id_service

            # Soft delete
            TeraService.delete(id_service)

            # Make sure it is deleted
            self.assertIsNone(TeraService.get_service_by_id(id_service))

            # Query, with soft delete flag
            service = TeraService.query.filter_by(id_service=id_service).execution_options(include_deleted=True).first()
            self.assertIsNotNone(service)
            self.assertIsNotNone(service.deleted_at)

    def test_hard_delete(self):
        with self._flask_app.app_context():
            # Create new
            service = TeraServiceTest.new_test_service('TestService')
            self.assertIsNotNone(service.id_service)
            id_service = service.id_service

            # Create a new site association for that service
            from test_TeraServiceSite import TeraServiceSiteTest
            site_service = TeraServiceSiteTest.new_test_service_site(id_site=1, id_service=id_service)
            self.assertIsNotNone(site_service.id_service_site)
            id_site_service = site_service.id_service_site

            # Soft delete to prevent relationship integrity errors as we want to test hard-delete cascade here
            TeraServiceSite.delete(id_site_service)
            TeraService.delete(id_service)

            # Check that relationships are still there
            self.assertIsNone(TeraService.get_service_by_id(id_service))
            self.assertIsNotNone(TeraService.get_service_by_id(id_service, True))
            self.assertIsNone(TeraServiceSite.get_service_site_by_id(id_site_service))
            self.assertIsNotNone(TeraServiceSite.get_service_site_by_id(id_site_service, True))

            # Hard delete
            TeraService.delete(id_service, hard_delete=True)

            # Make sure eveything is deleted
            self.assertIsNone(TeraService.get_service_by_id(id_service, True))
            self.assertIsNone(TeraServiceSite.get_service_site_by_id(id_site_service, True))

    def test_undelete(self):
        with self._flask_app.app_context():
            # Create new
            service = TeraServiceTest.new_test_service('TestService')
            self.assertIsNotNone(service.id_service)
            id_service = service.id_service

            # Create service roles
            from test_TeraServiceRole import TeraServiceRoleTest
            role = TeraServiceRoleTest.new_test_service_role(id_service=id_service, role_name='admin')
            id_role_admin = role.id_service_role

            role = TeraServiceRoleTest.new_test_service_role(id_service=id_service, role_name='user')
            id_role_user = role.id_service_role

            # Create service sites association
            from test_TeraServiceSite import TeraServiceSiteTest
            service_site = TeraServiceSiteTest.new_test_service_site(id_site=1, id_service=id_service)
            id_service_site = service_site.id_service_site

            # Create service projects association
            from test_TeraServiceProject import TeraServiceProjectTest
            service_project = TeraServiceProjectTest.new_test_service_project(id_service=id_service, id_project=1)
            id_service_project = service_project.id_service_project

            # Soft delete to prevent relationship integrity errors as we want to test hard-delete cascade here
            TeraServiceSite.delete(id_service_site)
            TeraServiceProject.delete(id_service_project)
            TeraService.delete(id_service)
            self.assertIsNone(TeraService.get_service_by_id(id_service))
            self.assertIsNone(TeraServiceRole.get_service_role_by_id(id_role_user))
            self.assertIsNone(TeraServiceRole.get_service_role_by_id(id_role_admin))

            # Undelete service
            TeraService.undelete(id_service)
            self.assertIsNotNone(TeraService.get_service_by_id(id_service))
            self.assertIsNotNone(TeraServiceProject.get_service_project_by_id(id_service_project))
            self.assertIsNotNone(TeraServiceSite.get_service_site_by_id(id_service_site))
            self.assertIsNotNone(TeraServiceRole.get_service_role_by_id(id_role_user))
            self.assertIsNotNone(TeraServiceRole.get_service_role_by_id(id_role_admin))

    @staticmethod
    def new_test_service(service_key: str):
        service = TeraService()
        service.service_name = 'Test Service'
        service.service_key = service_key
        service.service_hostname = 'localhost'
        service.service_port = 12345
        service.service_endpoint = 'test'
        service.service_clientendpoint = '/'
        TeraService.insert(service)
        return service
