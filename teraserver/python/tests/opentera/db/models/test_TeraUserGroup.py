from tests.opentera.db.models.BaseModelsTest import BaseModelsTest
from opentera.db.models.TeraUserGroup import TeraUserGroup
from opentera.db.models.TeraUserUserGroup import TeraUserUserGroup
from opentera.db.models.TeraProject import TeraProject
from opentera.db.models.TeraServiceRole import TeraServiceRole
from opentera.db.models.TeraServiceAccess import TeraServiceAccess
from opentera.db.models.TeraUser import TeraUser
from opentera.db.models.TeraSite import TeraSite
from sqlalchemy.exc import SQLAlchemyError


class TeraUserGroupTest(BaseModelsTest):
    def test_defaults(self):
        with self._flask_app.app_context():
            groups = TeraUserGroup.query.all()
            self.assertGreater(len(groups), 0)

    def test_to_json_full_and_minimal(self):
        with self._flask_app.app_context():
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
        with self._flask_app.app_context():
            groups = TeraUserGroup.query.all()
            self.assertGreater(len(groups), 0)
            for group in groups:
                json_out = group.to_json()
                new_group = TeraUserGroup()
                new_group.from_json(json_out)
                self.assertEqual(new_group.id_user_group, group.id_user_group)
                self.assertEqual(new_group.user_group_name, group.user_group_name)

    def test_to_json_create_event(self):
        with self._flask_app.app_context():
            groups = TeraUserGroup.query.all()
            self.assertGreater(len(groups), 0)
            for group in groups:
                to_json_minimal = group.to_json(minimal=True)
                to_json_create_event = group.to_json_create_event()
                self.assertEqual(to_json_minimal, to_json_create_event)

    def test_to_json_update_event(self):
        with self._flask_app.app_context():
            groups = TeraUserGroup.query.all()
            self.assertGreater(len(groups), 0)
            for group in groups:
                to_json_minimal = group.to_json(minimal=True)
                to_json_update_event = group.to_json_update_event()
                self.assertEqual(to_json_minimal, to_json_update_event)

    def test_to_json_delete_event(self):
        with self._flask_app.app_context():
            groups = TeraUserGroup.query.all()
            self.assertGreater(len(groups), 0)
            for group in groups:
                to_json_minimal = group.to_json(minimal=True)
                to_json_delete_event = group.to_json_delete_event()
                self.assertNotEqual(to_json_minimal, to_json_delete_event)
                self.assertEqual(1, len(to_json_delete_event))
                self.assertTrue('id_user_group' in to_json_delete_event)

    def test_get_projects_roles(self):
        with self._flask_app.app_context():
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
        with self._flask_app.app_context():
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

    def test_get_user_group_by_group_name(self):
        with self._flask_app.app_context():
            groups = TeraUserGroup.query.all()
            self.assertGreater(len(groups), 0)
            for group in groups:
                group_name = group.user_group_name
                group_by_name = TeraUserGroup.get_user_group_by_group_name(group_name)
                self.assertIsNotNone(group_by_name)
                self.assertEqual(group_by_name.id_user_group, group.id_user_group)
                self.assertTrue(group_by_name.deleted_at is None)

    # def test_get_user_group_by_group_name_with_deleted(self):
    #     with self._flask_app.app_context():
    #         groups = TeraUserGroup.query.all()
    #         self.assertGreater(len(groups), 0)
    #         # Delete all groups
    #         for group in groups:
    #             # self.db.session.info['include_deleted'] = True
    #             print('Session = ', self.db.session, self.db.session.info)
    #             group_name = group.user_group_name
    #             group_service_role_count = len(group.user_group_services_roles)
    #             group_users_count = len(group.user_group_users)
    #
    #             id_user_group = group.id_user_group
    #             group.delete(group.id_user_group)
    #
    #             # from opentera.db.models.TeraUserUserGroup import TeraUserUserGroup
    #             # user_user_groups = TeraUserUserGroup.query_users_for_user_group(id_user_group, with_deleted=True)
    #
    #             test_group = TeraUserGroup.get_user_group_by_group_name(name=group_name, with_deleted=True)
    #             self.assertIsNotNone(test_group)
    #             self.assertIsNotNone(test_group.deleted_at)
    #             # Make sure users are not deleted
    #             self.assertEqual(group_users_count, len(test_group.user_group_users), 'Group users count mismatch')
    #             for user in test_group.user_group_users:
    #                 self.assertIsNone(user.deleted_at)
    #             # Make sure service_roles are not deleted
    #             self.assertEqual(group_service_role_count, len(test_group.user_group_services_roles),
    #                              'Group service roles count mismatch')
    #             for service_role in test_group.user_group_services_roles:
    #                 self.assertIsNone(service_role.deleted_at)
    #
    #             # Undelete group
    #             # TeraUserGroup.undelete(id_user_group)
    #             # test_group = TeraUserGroup.get_user_group_by_group_name(name=group_name, with_deleted=False)
    #             # self.assertIsNone(test_group.deleted_at)

    def test_get_user_group_by_id(self):
        with self._flask_app.app_context():
            groups = TeraUserGroup.query.all()
            self.assertGreater(len(groups), 0)
            for group in groups:
                group_id = group.id_user_group
                group_by_id = TeraUserGroup.get_user_group_by_id(group_id)
                self.assertIsNotNone(group_by_id)
                self.assertEqual(group_by_id.id_user_group, group.id_user_group)
                self.assertTrue(group_by_id.deleted_at is None)

    def test_insert_with_missing_non_nullable_properties(self):
        with self._flask_app.app_context():
            new_group = TeraUserGroup()
            self.assertRaises(SQLAlchemyError, TeraUserGroup.insert, new_group)

    def test_insert_with_invalid_user(self):
        with self._flask_app.app_context():
            new_group = TeraUserGroup()
            new_group.user_group_name = 'Test group'
            new_user = TeraUser()
            new_group.user_group_users = [new_user]
            self.assertRaises(SQLAlchemyError, TeraUserGroup.insert, new_group)

    def test_insert_with_invalid_service_roles(self):
        with self._flask_app.app_context():
            new_group = TeraUserGroup()
            new_group.user_group_name = 'Test group'
            new_service_role = TeraServiceRole()
            new_group.user_group_services_roles = [new_service_role]
            self.assertRaises(SQLAlchemyError, TeraUserGroup.insert, new_group)

    def test_insert_with_empty_users_and_roles(self):
        with self._flask_app.app_context():
            new_group = TeraUserGroup()
            new_group.user_group_name = 'Test group'
            new_group.user_group_users = []
            new_group.user_group_services_roles = []
            TeraUserGroup.insert(new_group)
            id_user_group = new_group.id_user_group
            self.assertIsNotNone(new_group.id_user_group)
            self.assertTrue(new_group.id_user_group > 0)
            self.assertIsNotNone(TeraUserGroup.get_user_group_by_id(id_user_group))
            # Cleanup
            TeraUserGroup.delete(new_group.id_user_group, hard_delete=True)
            self.assertIsNone(TeraUserGroup.get_user_group_by_id(id_user_group))

    def test_update_with_modified_id_user_group(self):
        with self._flask_app.app_context():
            with self._flask_app.app_context():
                groups = TeraUserGroup.query.all()
                self.assertGreater(len(groups), 0)
                for group in groups:
                    # Change id_user_group to an invalid value
                    invalid_fields = {'id_user_group': group.id_user_group + 100}
                    # TeraUserGroup.update(group.id_user_group, invalid_fields)
                    self.assertRaises(SQLAlchemyError, TeraUserGroup.update, group.id_user_group, invalid_fields)
                    TeraUserGroup.db().session.rollback()

    def test_update_with_invalid_fields(self):
        with self._flask_app.app_context():
            with self._flask_app.app_context():
                groups = TeraUserGroup.query.all()
                self.assertGreater(len(groups), 0)
                for group in groups:
                    # Change id_user_group to an invalid value
                    invalid_fields = {'invalid_field_1': 'field1',
                                      'invalid_field_2': 'field2',
                                      'invalid_field_3': 'field3'}

                    # TeraUserGroup.update(group.id_user_group, invalid_fields)
                    self.assertRaises(SQLAlchemyError, TeraUserGroup.update, group.id_user_group, invalid_fields)
                    TeraUserGroup.db().session.rollback()

    def test_soft_delete(self):
        with self._flask_app.app_context():
            # Create new
            ug = TeraUserGroupTest.new_test_usergroup()
            self.assertIsNotNone(ug.id_user_group)
            id_user_group = ug.id_user_group

            # Soft delete
            TeraUserGroup.delete(id_user_group)
            # Make sure participant is deleted
            self.assertIsNone(TeraUserGroup.get_user_group_by_id(id_user_group))

            # Query, with soft delete flag
            ug = TeraUserGroup.query.filter_by(id_user_group=id_user_group).\
                execution_options(include_deleted=True).first()
            self.assertIsNotNone(ug)
            self.assertIsNotNone(ug.deleted_at)

    def test_hard_delete(self):
        with self._flask_app.app_context():
            # Create new
            ug = TeraUserGroupTest.new_test_usergroup()
            self.assertIsNotNone(ug.id_user_group)
            id_user_group = ug.id_user_group

            from tests.opentera.db.models.test_TeraUser import TeraUserTest
            user = TeraUserTest.new_test_user(user_name="user_ug_harddelete", user_groups=[ug])
            self.assertIsNotNone(user.id_user)
            id_user = user.id_user

            # Soft delete to prevent relationship integrity errors as we want to test hard-delete cascade here
            id_user_user_group = TeraUserUserGroup.query_user_user_group_for_user_user_group(id_user, id_user_group)\
                .id_user_user_group
            TeraUserUserGroup.delete(id_user_user_group)
            TeraUserGroup.delete(id_user_group)

            # Check that relationships are still there
            self.assertIsNotNone(TeraUser.get_user_by_id(id_user))
            self.assertIsNone(TeraUserGroup.get_user_group_by_id(id_user_group))
            self.assertIsNotNone(TeraUserGroup.get_user_group_by_id(id_user_group, True))
            self.assertIsNone(TeraUserUserGroup.get_user_user_group_by_id(id_user_user_group))
            self.assertIsNotNone(TeraUserUserGroup.get_user_user_group_by_id(id_user_user_group, True))

            # Hard delete
            TeraUserGroup.delete(id_user_group, hard_delete=True)

            # Make sure eveything is deleted
            self.assertIsNotNone(TeraUser.get_user_by_id(id_user, True))
            self.assertIsNone(TeraUserGroup.get_user_group_by_id(id_user_group, True))
            self.assertIsNone(TeraUserUserGroup.get_user_user_group_by_id(id_user_user_group, True))

    def test_undelete(self):
        with self._flask_app.app_context():
            # Create new
            ug = TeraUserGroupTest.new_test_usergroup()
            self.assertIsNotNone(ug.id_user_group)
            id_user_group = ug.id_user_group

            from tests.opentera.db.models.test_TeraUser import TeraUserTest
            user = TeraUserTest.new_test_user(user_name="user_ug_undelete", user_groups=[ug])
            self.assertIsNotNone(user.id_user)
            id_user = user.id_user

            # Add service access
            from tests.opentera.db.models.test_TeraServiceAccess import TeraServiceAccessTest
            access = TeraServiceAccessTest.new_test_service_access(id_service_role=1, id_user_group=id_user_group)
            id_access = access.id_service_access

            # Delete
            id_user_user_group = TeraUserUserGroup.query_user_user_group_for_user_user_group(id_user, id_user_group) \
                .id_user_user_group
            TeraUserUserGroup.delete(id_user_user_group)
            TeraUserGroup.delete(id_user_group)

            self.assertIsNone(TeraUserGroup.get_user_group_by_id(id_user_group))
            self.assertIsNone(TeraServiceAccess.get_service_access_by_id(id_access))
            self.assertIsNone(TeraUserUserGroup.get_user_user_group_by_id(id_user_user_group))

            # Undelete
            TeraUserGroup.undelete(id_user_group)

            self.assertIsNotNone(TeraUserGroup.get_user_group_by_id(id_user_group))
            self.assertIsNotNone(TeraUserUserGroup.get_user_user_group_by_id(id_user_user_group))
            self.assertIsNotNone(TeraServiceAccess.get_service_access_by_id(id_access))

    @staticmethod
    def new_test_usergroup() -> TeraUserGroup:
        ug = TeraUserGroup()
        ug.user_group_name = "Test User Group"
        TeraUserGroup.insert(ug)
        return ug
