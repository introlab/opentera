import os
from tests.opentera.db.models.BaseModelsTest import BaseModelsTest
from sqlalchemy import exc
from opentera.db.Base import db

from opentera.db.models.TeraServiceRole import TeraServiceRole


class TeraServiceRoleTest(BaseModelsTest):

    filename = os.path.join(os.path.dirname(__file__), 'TeraServiceRoleTest.db')

    SQLITE = {
        'filename': filename
    }

    def test_nullable_args(self):
        new_service_role = TeraServiceRole()
        new_service_role.id_service = 1
        new_service_role.service_role_name = None

        db.session.add(new_service_role)
        self.assertRaises(exc.IntegrityError, db.session.commit)
        db.session.rollback()

        new_service_role = TeraServiceRole()
        new_service_role.id_service = None
        new_service_role.service_role_name = 'Service_role_name'

        db.session.add(new_service_role)
        self.assertRaises(exc.IntegrityError, db.session.commit)

    def test_unique_args(self):
        pass

    def test_relationships(self):
        new_service_role = TeraServiceRole()
        new_service_role.id_service = 10
        new_service_role.service_role_name = 'Role Name'
        db.session.add(new_service_role)
        self.assertRaises(exc.IntegrityError, db.session.commit)

    def test_service_role_to_json(self):
        new_service_role = TeraServiceRole()
        new_service_role.id_service = 1
        new_service_role.id_project = 1
        new_service_role.id_site = 1
        new_service_role.service_role_name = 'Role Name'
        db.session.add(new_service_role)
        db.session.commit()
        json_data = new_service_role.to_json()
        json_data_minimal = new_service_role.to_json(minimal=True)
        self._check_json(new_service_role, json_data)
        self._check_json(new_service_role, json_data_minimal, minimal=True)

    def _check_json(self, service_role, json_data, minimal=False):
        self.assertEqual(service_role.id_service, json_data['id_service'])
        self.assertEqual(service_role.id_project, json_data['id_project'])
        self.assertEqual(service_role.id_site, json_data['id_site'])
        self.assertEqual(service_role.service_role_name, json_data['service_role_name'])
        if minimal:
            pass

    def test_get_service_role(self):
        new_service_role = TeraServiceRole()
        new_service_role.id_service = 1
        new_service_role.id_project = 1
        new_service_role.id_site = 1
        new_service_role.service_role_name = 'Role Name'
        db.session.add(new_service_role)
        db.session.commit()
        same_service_role = TeraServiceRole.get_service_roles(service_id=new_service_role.id_service)
        for service_role in same_service_role:
            self.assertEqual(service_role.service_role_service.service_name, 'OpenTera Server')
        self.assertEqual(same_service_role[-1], new_service_role)

    def test_get_service_roles_for_site(self):
        new_service_role = TeraServiceRole()
        db.session.rollback()
        new_service_role.id_service = 1
        new_service_role.id_project = 1
        new_service_role.id_site = 1
        new_service_role.service_role_name = 'Role Name'
        db.session.add(new_service_role)
        db.session.commit()
        same_service_role = TeraServiceRole.get_service_roles_for_site(service_id=new_service_role.id_service,
                                                                       site_id=new_service_role.id_site)
        for service_role in same_service_role:
            self.assertEqual(service_role.service_role_service.service_name, 'OpenTera Server')
            self.assertEqual(service_role.id_site, new_service_role.id_site)
        self.assertEqual(same_service_role[-1], new_service_role)

    def test_get_specific_service_role_for_site(self):
        new_service_role = TeraServiceRole()
        new_service_role.id_service = 1
        new_service_role.id_project = 1
        new_service_role.id_site = 1
        new_service_role.service_role_name = 'Role Name'
        db.session.add(new_service_role)
        db.session.commit()
        same_service_role = TeraServiceRole.get_specific_service_role_for_site(service_id=new_service_role.id_service,
                                       site_id=new_service_role.id_site, rolename=new_service_role.service_role_name)
        self.assertEqual(same_service_role.service_role_name, new_service_role.service_role_name)
        # the BaseModelstest is changing the same_service_role.id_service_role
        # when the class is the but not the test alone

    def test_get_service_roles_for_project(self):
        new_service_role = TeraServiceRole()
        new_service_role.id_service = 1
        new_service_role.id_project = 1
        new_service_role.id_site = 1
        new_service_role.service_role_name = 'Role Name'
        db.session.add(new_service_role)
        db.session.commit()
        same_service_role = TeraServiceRole.get_service_roles_for_project(service_id=new_service_role.id_service,
                                                                          project_id=new_service_role.id_project)
        for service_role in same_service_role:
            self.assertEqual(service_role.service_role_service.service_name, 'OpenTera Server')
        self.assertEqual(same_service_role[-1], new_service_role)

    def test_get_specific_service_role_for_project(self):
        new_service_role = TeraServiceRole()
        new_service_role.id_service = 1
        new_service_role.id_project = 1
        new_service_role.id_site = 1
        new_service_role.service_role_name = 'Role Name'
        db.session.add(new_service_role)
        db.session.commit()
        same_service_role = TeraServiceRole.get_specific_service_role_for_project(
            service_id=new_service_role.id_service, project_id=new_service_role.id_project,
            rolename=new_service_role.service_role_name)
        self.assertEqual(same_service_role.service_role_name, new_service_role.service_role_name)

    def test_get_service_role_by_id(self):
        new_service_role = TeraServiceRole()
        new_service_role.id_service = 1
        new_service_role.id_project = 1
        new_service_role.id_site = 1
        new_service_role.service_role_name = 'Role Name'
        db.session.add(new_service_role)
        db.session.commit()
        same_service_role = TeraServiceRole.get_service_role_by_id(role_id=new_service_role.id_service_role)
        self.assertEqual(same_service_role, new_service_role)
