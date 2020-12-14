import os
from tests.libtera.db.models.BaseModelsTest import BaseModelsTest
from sqlalchemy import exc
from libtera.db.Base import db

from libtera.db.models.TeraServiceRole import TeraServiceRole


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
        db.session.rollback()

    def test_unique_args(self):
        pass

    def test_relationships(self):
        new_service_role = TeraServiceRole()
        new_service_role.id_service = 10
        new_service_role.service_role_name = 'Role Name'
        db.session.add(new_service_role)
        self.assertRaises(exc.IntegrityError, db.session.commit)
        db.session.rollback()

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

    # def test_get_service_role(self):
    #     new_service_role = TeraServiceRole()
    #     new_service_role.id_service = 10
    #     new_service_role.id_project = 11
    #     new_service_role.id_site = 12
    #     new_service_role.service_role_name = 'Role Name'
    #     db.session.add(new_service_role)
    #     db.session.commit()
    #     breakpoint()
    #     same_service_role = TeraServiceRole.get_service_roles(service_id=new_service_role.id_service)
    #     breakpoint()
    #     self.assertEqual(same_service_role.id_service, new_service_role.id_service)
    #     self.assertEqual(same_service_role.id_project, new_service_role.id_project)
    #     self.assertEqual(same_service_role.id_site, new_service_role.id_site)
    #     self.assertEqual(same_service_role.service_role_name, new_service_role.service_role_name)

    # Aborting further testing because of the db raltionships and the __repr__ function
    # using db.relationship('TeraService)