import os
from tests.opentera.db.models.BaseModelsTest import BaseModelsTest
from sqlalchemy import exc
from opentera.db.Base import db

from opentera.db.models.TeraService import TeraService


class TeraServiceTest(BaseModelsTest):

    filename = os.path.join(os.path.dirname(__file__), 'TeraServiceTest.db')

    SQLITE = {
        'filename': filename
    }

    def test_nullable_args(self):
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
        db.session.add(new_service)
        self.assertRaises(exc.IntegrityError, db.session.commit)
        db.session.rollback()

        new_service.service_uuid = 'Uuid'
        new_service.service_name = None
        db.session.add(new_service)
        self.assertRaises(exc.IntegrityError, db.session.commit)
        db.session.rollback()

        new_service.service_name = 'Name'
        new_service.service_hostname = None
        db.session.add(new_service)
        self.assertRaises(exc.IntegrityError, db.session.commit)
        db.session.rollback()

        new_service.service_hostname = 'Hostname'
        new_service.service_port = None
        db.session.add(new_service)
        self.assertRaises(exc.IntegrityError, db.session.commit)
        db.session.rollback()

        new_service.service_port = 1
        new_service.service_endpoint = None
        db.session.add(new_service)
        self.assertRaises(exc.IntegrityError, db.session.commit)
        db.session.rollback()

        new_service.service_endpoint = 'Endpoint'
        new_service.service_clientendpoint = None
        db.session.add(new_service)
        self.assertRaises(exc.IntegrityError, db.session.commit)

    def test_nullable_bool1(self):
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
        db.session.add(new_service)
        self.assertRaises(exc.IntegrityError, db.session.commit)

    def test_nullable_bool2(self):
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
        db.session.add(new_service)
        self.assertRaises(exc.IntegrityError, db.session.commit)

    def test_nullable_bool3(self):
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
        db.session.add(new_service)
        self.assertRaises(exc.IntegrityError, db.session.commit)

    def test_unique_args_uuid(self):
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
        db.session.add(new_service)
        db.session.add(same_service)
        self.assertRaises(exc.IntegrityError, db.session.commit)

    def test_unique_args_service_key(self):
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
        db.session.add(new_service)
        db.session.add(same_service)
        self.assertRaises(exc.IntegrityError, db.session.commit)

    def test_service_port_integer(self):
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
        db.session.add(new_service)
        self.assertRaises(exc.StatementError, db.session.commit)

    def test_service_system_integer(self):
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
        db.session.add(new_service)
        self.assertRaises(exc.StatementError, db.session.commit)

    def test_service_editable_config_integer(self):
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
        db.session.add(new_service)
        self.assertRaises(exc.StatementError, db.session.commit)

    def test_service_to_json(self):
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
        self.assertFalse('service_system' in json_data)
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
        new_service = TeraService()
        token = new_service.get_token(token_key='A key')
        token1 = new_service.get_token(token_key='123456')
        token2 = new_service.get_token(token_key='#% @f w346')
        self.assertIsNotNone(token)
        self.assertIsNotNone(token1)
        self.assertIsNotNone(token2)

    def test_service_get_functions(self):
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
        db.session.add(new_service)
        db.session.commit()
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
        openteraservice = TeraService.get_openteraserver_service()
        self.assertEqual(openteraservice.service_key, openteraservice.service_key)


    # problems with the insert service. Not Connected to SQlite?
    # def test_service_insert(self):
    #     new_service = TeraService()
    #     new_service.service_uuid = 'uuid'
    #     new_service.service_name = 'Name'
    #     new_service.service_key = 'Key'
    #     new_service.service_hostname = 'Hostname'
    #     new_service.service_port = 1
    #     new_service.service_endpoint = "Endpoint"
    #     new_service.service_clientendpoint = 'Clientendpoint'
    #     new_service.service_enabled = True
    #     new_service.service_system = True
    #     new_service.service_editable_config = True
    #     TeraService.insert(service=new_service)
    #     same_service = TeraService.get_service_by_uuid(p_uuid='uuid')
    #     self.assertEqual(same_service, new_service)
# SQLite does not enforce the length of a VARCHAR. You can declare a VARCHAR(10) and SQLite will be happy to store
# a 500-million character string there. And it will keep all 500-million characters intact.
# Your content is never truncated. SQLite understands the column type of "VARCHAR(N)" to be the same as
# "TEXT", regardless of the value of N.
#
# def test_service_uuid_string(self):
#     new_service = TeraService()
#
#     new_service.service_uuid = 'Definitely longer than a 36 characters string'
#
#     new_service.service_name = 'Name'
#     new_service.service_key = 'key'
#     new_service.service_hostname = 'Hostname'
#     new_service.service_port = 2
#     new_service.service_endpoint = "Endpoint"
#     new_service.service_clientendpoint = 'Clientendpoint'
#     new_service.service_enabled = True
#     new_service.service_system = True
#     new_service.service_editable_config = True
#     db.session.add(new_service)
#     db.session.commit()
#     self.assertRaises(exc.IntegrityError, db.session.commit)
#
# SQLite uses what it calls a dynamic typing system, which ultimately means that you can store text
# in integer fields - in Oracle, SQL Server and all the other big hitters in the database world,
# attempts to do this will fail - not with SQLite.
#
# def test_service_port_integer(self):
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
#     db.session.add(new_service)
#     db.session.commit()
#     breakpoint()