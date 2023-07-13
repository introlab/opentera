from tests.opentera.db.models.BaseModelsTest import BaseModelsTest
from opentera.db.models.TeraTestType import TeraTestType
from opentera.db.models.TeraTest import TeraTest


class TeraTestTypeTest(BaseModelsTest):

    def test_defaults(self):
        with self._flask_app.app_context():
            pass

    def test_soft_delete(self):
        with self._flask_app.app_context():
            # Create new
            test_type = TeraTestType()
            test_type.test_type_name = "Test test type..."
            test_type.id_service = 1
            TeraTestType.insert(test_type)
            id_test_type = test_type.id_test_type

            # Soft delete
            TeraTestType.delete(id_test_type)

            # Make sure it is deleted
            self.assertIsNone(TeraTestType.get_test_type_by_id(id_test_type))

            # Query, with soft delete flag
            test_type = TeraTestType.query.filter_by(id_test_type=id_test_type)\
                .execution_options(include_deleted=True).first()
            self.assertIsNotNone(test_type)
            self.assertIsNotNone(test_type.deleted_at)

    def test_hard_delete(self):
        with self._flask_app.app_context():
            # Create new
            test_type = TeraTestType()
            test_type.test_type_name = "Test test type..."
            test_type.id_service = 1
            TeraTestType.insert(test_type)
            id_test_type = test_type.id_test_type

            test = TeraTest()
            test.id_participant = 1
            test.id_session = 1
            test.id_test_type = id_test_type
            test.test_name = "Test test!"
            TeraTest.insert(test)
            self.assertIsNotNone(test.id_test)
            id_test = test.id_test

            # Soft delete to prevent relationship integrity errors as we want to test hard-delete cascade here
            TeraTest.delete(id_test)
            TeraTestType.delete(id_test_type)

            # Check that relationships are still there
            self.assertIsNone(TeraTest.get_test_by_id(id_test))
            self.assertIsNotNone(TeraTest.get_test_by_id(id_test, True))
            self.assertIsNone(TeraTestType.get_test_type_by_id(id_test_type))
            self.assertIsNotNone(TeraTestType.get_test_type_by_id(id_test_type, True))

            # Hard delete
            TeraTestType.delete(id_test_type, hard_delete=True)

            # Make sure eveything is deleted
            self.assertIsNone(TeraTest.get_test_by_id(id_test, True))
            self.assertIsNone(TeraTestType.get_test_type_by_id(id_test_type, True))
