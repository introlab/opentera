from tests.opentera.db.models.BaseModelsTest import BaseModelsTest
from modules.FlaskModule.FlaskModule import flask_app
from opentera.db.models.TeraUserGroup import TeraUserGroup
from opentera.db.models.TeraProject import TeraProject
from opentera.db.models.TeraSite import TeraSite


class TeraUserGroupTest(BaseModelsTest):
    def test_defaults(self):
        with flask_app.app_context():
            groups = TeraUserGroup.query.all()
            self.assertGreater(len(groups), 0)

    def test_to_json_full_and_minimal(self):
        with flask_app.app_context():
            groups = TeraUserGroup.query.all()
            self.assertGreater(len(groups), 0)
            for group in groups:
                for minimal in [True, False]:
                    json_out = group.to_json(minimal=minimal)
                    self.assertGreater(len(json_out), 0)
                    self.assertTrue('id_user_group' in json_out)
                    self.assertTrue('user_group_name' in json_out)
                    self.assertFalse('user_group_services_access' in json_out)
                    self.assertFalse('user_group_users' in json_out)
                    self.assertFalse('user_group_projects_access' in json_out)

    def test_from_json(self):
        with flask_app.app_context():
            groups = TeraUserGroup.query.all()
            self.assertGreater(len(groups), 0)
            for group in groups:
                json_out = group.to_json()
                new_group = TeraUserGroup()
                new_group.from_json(json_out)
                self.assertEqual(new_group.id_user_group, group.id_user_group)
                self.assertEqual(new_group.user_group_name, group.user_group_name)

    def test_get_projects_roles(self):
        with flask_app.app_context():
            groups = TeraUserGroup.query.all()
            self.assertGreater(len(groups), 0)
            for group in groups:
                for no_inheritance in [True, False]:
                    projects_roles = group.get_projects_roles(no_inheritance=no_inheritance)
                    self.assertIsNotNone(projects_roles)
                    for project, role in projects_roles.items():
                        self.assertTrue(isinstance(project, TeraProject))
                        self.assertTrue(isinstance(role, dict))
                        self.assertIsNotNone(project)
                        self.assertIsNotNone(role)
                        self.assertTrue('project_role' in role)
                        self.assertTrue('inherited' in role)

                        if no_inheritance:
                            self.assertEqual(role['inherited'], False)
                        elif role['inherited']:
                            self.assertEqual(role['project_role'], 'admin')

    def test_get_sites_roles(self):
        with flask_app.app_context():
            groups = TeraUserGroup.query.all()
            self.assertGreater(len(groups), 0)
            for group in groups:
                site_roles = group.get_sites_roles()
                self.assertIsNotNone(site_roles)
                for site, role in site_roles.items():
                    self.assertTrue(isinstance(site, TeraSite))
                    self.assertTrue(isinstance(role, dict))
                    self.assertIsNotNone(site)
                    self.assertIsNotNone(role)
                    self.assertTrue('site_role' in role)
                    self.assertTrue('inherited' in role)
                    if role['inherited']:
                        self.assertEqual(role['site_role'], 'user')

    def test_get_user_group_by_group_name_without_deleted(self):
        with flask_app.app_context():
            groups = TeraUserGroup.query.all()
            self.assertGreater(len(groups), 0)
            for group in groups:
                group_name = group.user_group_name
                group_by_name = TeraUserGroup.get_user_group_by_group_name(group_name)
                self.assertIsNotNone(group_by_name)
                self.assertEqual(group_by_name.id_user_group, group.id_user_group)
                self.assertTrue(group_by_name.deleted_at is None)

    def test_get_user_group_by_group_name_with_deleted(self):
        with flask_app.app_context():
            groups = TeraUserGroup.query.all()
            self.assertGreater(len(groups), 0)
            # Delete all groups
            for group in groups:
                # self.db.session.info['include_deleted'] = True
                print('Session = ', self.db.session, self.db.session.info)
                group_name = group.user_group_name
                group_service_role_count = len(group.user_group_service_role)
                group_users_count = len(group.user_group_users)

                id_user_group = group.id_user_group
                group.delete(group.id_user_group)

                # from opentera.db.models.TeraUserUserGroup import TeraUserUserGroup
                # user_user_groups = TeraUserUserGroup.query_users_for_user_group(id_user_group, with_deleted=True)

                test_group = TeraUserGroup.get_user_group_by_group_name(name=group_name, with_deleted=True)
                self.assertIsNotNone(test_group)
                self.assertIsNotNone(test_group.deleted_at)
                # Make sure users are not deleted
                self.assertEqual(group_users_count, len(test_group.user_group_users), 'Group users count mismatch')
                for user in test_group.user_group_users:
                    self.assertIsNone(user.deleted_at)
                # Make sure service_roles are not deleted
                self.assertEqual(group_service_role_count, len(test_group.user_group_service_role),
                                 'Group service roles count mismatch')
                for service_role in test_group.user_group_service_role:
                    self.assertIsNone(service_role.deleted_at)

                # Undelete group
                TeraUserGroup.undelete(id_user_group)
                # self.db.session.info['include_deleted'] = False
                test_group = TeraUserGroup.get_user_group_by_group_name(name=group_name, with_deleted=False)
                self.assertIsNone(test_group.deleted_at)

    def test_get_user_group_by_id(self):
        with flask_app.app_context():
            groups = TeraUserGroup.query.all()
            self.assertGreater(len(groups), 0)
            for group in groups:
                group_id = group.id_user_group
                group_by_id = TeraUserGroup.get_user_group_by_id(group_id)
                self.assertIsNotNone(group_by_id)
                self.assertEqual(group_by_id.id_user_group, group.id_user_group)
                self.assertTrue(group_by_id.deleted_at is None)


    def test_insert_with_minimal_config(self):
        with flask_app.app_context():
            pass
    def test_update(self):
        with flask_app.app_context():
            pass

    def test_delete(self):
        with flask_app.app_context():
            pass

    def test_soft_delete(self):
       pass


