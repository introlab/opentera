from tests.opentera.db.models.BaseModelsTest import BaseModelsTest
from opentera.db.models.TeraUserUserGroup import TeraUserUserGroup
from opentera.db.models.TeraUser import TeraUser
from opentera.db.models.TeraUserGroup import TeraUserGroup
from sqlalchemy.exc import DatabaseError


class TeraUserUserGroupTest(BaseModelsTest):

    def test_defaults(self):
        with self._flask_app.app_context():
            user_user_groups = TeraUserUserGroup.query.all()
            self.assertGreater(len(user_user_groups), 0)

            for user_user_group in user_user_groups:
                self.assertIsNotNone(user_user_group.id_user_user_group)
                self.assertIsNotNone(user_user_group.id_user)
                self.assertIsNotNone(user_user_group.id_user_group)
                # Test relationships
                self.assertIsNotNone(user_user_group.user_user_group_user)
                self.assertIsNotNone(user_user_group.user_user_group_user_group)
                self.assertEqual(user_user_group.id_user, user_user_group.user_user_group_user.id_user)
                self.assertEqual(user_user_group.id_user_group,
                                 user_user_group.user_user_group_user_group.id_user_group)

    def test_to_json(self):
        with self._flask_app.app_context():
            user_user_groups = TeraUserUserGroup.query.all()
            self.assertGreater(len(user_user_groups), 0)
            for user_user_group in user_user_groups:
                json = user_user_group.to_json()
                self.assertGreater(len(json), 0)
                self.assertTrue('id_user' in json)
                self.assertTrue('id_user_group' in json)
                self.assertTrue('id_user_user_group' in json)

    def test_from_json(self):
        with self._flask_app.app_context():
            user_user_groups = TeraUserUserGroup.query.all()
            self.assertGreater(len(user_user_groups), 0)
            for user_user_group in user_user_groups:
                json = user_user_group.to_json()
                new_user_user_group = TeraUserUserGroup()
                new_user_user_group.from_json(json)
                self.assertEqual(new_user_user_group.id_user, user_user_group.id_user)
                self.assertEqual(new_user_user_group.id_user_group, user_user_group.id_user_group)
                self.assertEqual(new_user_user_group.id_user_user_group, user_user_group.id_user_user_group)

    def test_insert_with_new_uug(self):
        with self._flask_app.app_context():
            initial_count = TeraUserUserGroup.query.count()
            user = TeraUser.get_user_by_username('user3')
            group = TeraUserGroup.get_user_group_by_group_name("Admins - Default Site")
            uug = TeraUserUserGroup()
            uug.id_user = user.id_user
            uug.id_user_group = group.id_user_group
            uug_result = TeraUserUserGroup.insert(uug)
            self.assertIsNotNone(uug_result)
            self.assertEqual(uug, uug_result)
            # Cleanup
            TeraUserUserGroup.delete(uug_result.id_user_user_group, hard_delete=True)
            self.assertEqual(initial_count, TeraUserUserGroup.query.count())
            self.assertIsNone(TeraUserUserGroup.get_user_user_group_by_id(
                uug_result.id_user_user_group, with_deleted=True))

    def test_insert_with_existing_uug(self):
        with self._flask_app.app_context():
            user_user_groups = TeraUserUserGroup.query.all()
            initial_count = len(user_user_groups)
            self.assertGreater(len(user_user_groups), 0)
            for user_user_group in user_user_groups:
                # Re-create the same user_user_group
                uug = TeraUserUserGroup()
                uug.id_user = user_user_group.id_user
                uug.id_user_group = user_user_group.id_user_group
                uug_result = TeraUserUserGroup.insert(uug)
                self.assertIsNotNone(uug_result)
                self.assertEqual(uug_result.id_user, user_user_group.id_user)
                self.assertEqual(uug_result.id_user_group, user_user_group.id_user_group)
                self.assertEqual(user_user_group, uug_result)
                self.assertNotEquals(uug, uug_result)
                self.assertEqual(initial_count, TeraUserUserGroup.query.count())

    def test_insert_with_invalid_uug(self):
        with self._flask_app.app_context():
            uug = TeraUserUserGroup()
            self.assertRaises(DatabaseError, TeraUserUserGroup.insert, uug)

    def test_insert_with_deleted_uug(self):
        with self._flask_app.app_context():
            user_user_groups = TeraUserUserGroup.query.all()
            for user_user_group in user_user_groups:
                # Delete the user_user_group
                id_user_user_group = user_user_group.id_user_user_group
                TeraUserUserGroup.delete(user_user_group.id_user_user_group)
                user_user_group = TeraUserUserGroup.get_user_user_group_by_id(
                    id_user_user_group, with_deleted=True)

                self.assertIsNotNone(user_user_group.deleted_at)
                # Re-create the same user_user_group
                uug = TeraUserUserGroup()
                uug.id_user = user_user_group.id_user
                uug.id_user_group = user_user_group.id_user_group
                uug_result = TeraUserUserGroup.insert(uug)
                self.assertIsNotNone(uug_result)
                self.assertEqual(uug_result.id_user, user_user_group.id_user)
                self.assertEqual(uug_result.id_user_group, user_user_group.id_user_group)
                self.assertEqual(user_user_group, uug_result)
                self.assertNotEquals(uug, uug_result)
                self.assertIsNone(uug_result.deleted_at)

    def test_update_does_nothing(self):
        with self._flask_app.app_context():
            user_user_groups = TeraUserUserGroup.query.all()
            for user_user_group in user_user_groups:
                update_info = {'id_user': None, 'id_user_group': None}
                TeraUserUserGroup.update(user_user_group.id_user_user_group, update_info)
                self.assertIsNotNone(user_user_group.id_user)
                self.assertIsNotNone(user_user_group.id_user_group)

    def test_hard_delete(self):
        with self._flask_app.app_context():
            user = TeraUser.get_user_by_username('user3')
            group = TeraUserGroup.get_user_group_by_group_name("Admins - Default Site")
            uug = TeraUserUserGroup()
            uug.id_user = user.id_user
            uug.id_user_group = group.id_user_group
            uug_result = TeraUserUserGroup.insert(uug)
            self.assertIsNotNone(uug_result)
            id_user_user_group = uug.id_user_user_group
            TeraUserUserGroup.delete(id_user_user_group, hard_delete=True)
            self.assertIsNone(TeraUserUserGroup.get_user_user_group_by_id(id_user_user_group, with_deleted=True))

    def test_soft_delete(self):
        with self._flask_app.app_context():
            user = TeraUser.get_user_by_username('user3')
            group = TeraUserGroup.get_user_group_by_group_name("Admins - Default Site")
            uug = TeraUserUserGroup()
            uug.id_user = user.id_user
            uug.id_user_group = group.id_user_group
            uug_result = TeraUserUserGroup.insert(uug)
            self.assertIsNotNone(uug_result)
            id_user_user_group = uug.id_user_user_group
            TeraUserUserGroup.delete(id_user_user_group)
            self.assertIsNotNone(TeraUserUserGroup.get_user_user_group_by_id(id_user_user_group, with_deleted=True))
