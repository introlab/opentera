from tests.opentera.db.models.BaseModelsTest import BaseModelsTest
from opentera.db.models.TeraTest import TeraTest


class TeraTestTest(BaseModelsTest):

    def test_defaults(self):
        with self._flask_app.app_context():
            pass

    def test_soft_delete(self):
        with self._flask_app.app_context():
            # Create new
            test = TeraTest()
            test.id_participant = 1
            test.id_session = 1
            test.id_test_type = 1
            test.test_name = "Test test!"
            TeraTest.insert(test)
            id_test = test.id_test

            # Soft delete
            TeraTest.delete(id_test)

            # Make sure it is deleted
            self.assertIsNone(TeraTest.get_test_by_id(id_test))

            # Query, with soft delete flag
            test = TeraTest.query.filter_by(id_test=id_test).execution_options(include_deleted=True).first()
            self.assertIsNotNone(test)
            self.assertIsNotNone(test.deleted_at)

    def test_hard_delete(self):
        with self._flask_app.app_context():
            # Create new
            test = TeraTest()
            test.id_participant = 1
            test.id_session = 1
            test.id_test_type = 1
            test.test_name = "Test test!"
            TeraTest.insert(test)
            self.assertIsNotNone(test.id_test)
            id_test = test.id_test

            # Hard delete
            TeraTest.delete(id_test, hard_delete=True)

            # Make sure eveything is deleted
            self.assertIsNone(TeraTest.get_test_by_id(id_test, True))

    def test_undelete(self):
        with self._flask_app.app_context():
            # Create new
            test = TeraTest()
            test.id_participant = 1
            test.id_session = 1
            test.id_test_type = 1
            test.test_name = "Test test!"
            TeraTest.insert(test)
            self.assertIsNotNone(test.id_test)
            id_test = test.id_test

            # Soft delete
            TeraTest.delete(id_test)

            # Make sure it is deleted
            self.assertIsNone(TeraTest.get_test_by_id(id_test))

