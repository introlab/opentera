from tests.opentera.db.models.BaseModelsTest import BaseModelsTest
from opentera.db.models.TeraTestType import TeraTestType
from opentera.db.models.TeraTest import TeraTest
from opentera.db.models.TeraTestTypeSite import TeraTestTypeSite
from opentera.db.models.TeraTestTypeProject import TeraTestTypeProject


class TeraTestTypeTest(BaseModelsTest):

    def test_defaults(self):
        with self._flask_app.app_context():
            pass

    def test_soft_delete(self):
        with self._flask_app.app_context():
            # Create new
            test_type = TeraTestTypeTest.new_test_test_type()
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
            test_type = TeraTestTypeTest.new_test_test_type()
            id_test_type = test_type.id_test_type

            from tests.opentera.db.models.test_TeraTest import TeraTestTest
            test = TeraTestTest.new_test_test(id_session=1, id_participant=1, id_test_type=id_test_type)
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

    def test_undelete(self):
        with self._flask_app.app_context():
            # Create new
            test_type = TeraTestTypeTest.new_test_test_type()
            id_test_type = test_type.id_test_type

            from tests.opentera.db.models.test_TeraTest import TeraTestTest
            test = TeraTestTest.new_test_test(id_session=1, id_participant=1, id_test_type=id_test_type)
            self.assertIsNotNone(test.id_test)
            id_test = test.id_test

            # Associate with site
            from tests.opentera.db.models.test_TeraTestTypeSite import TeraTestTypeSiteTest
            tt_site = TeraTestTypeSiteTest.new_test_test_type_site(id_site=1, id_test_type=id_test_type)
            id_test_type_site = tt_site.id_test_type_site

            # ... and project
            from tests.opentera.db.models.test_TeraTestTypeProject import TeraTestTypeProjectTest
            tt_project = TeraTestTypeProjectTest.new_test_test_type_project(id_project=1, id_test_type=id_test_type)
            id_test_type_project = tt_project.id_test_type_project

            # Delete
            TeraTest.delete(id_test)
            TeraTestType.delete(id_test_type)

            # Check that everything was deleted
            self.assertIsNone(TeraTest.get_test_by_id(id_test))
            self.assertIsNone(TeraTestType.get_test_type_by_id(id_test_type))
            self.assertIsNone(TeraTestTypeSite.get_test_type_site_by_id(id_test_type_site))
            self.assertIsNone(TeraTestTypeProject.get_test_type_project_by_id(id_test_type_project))

            # Undelete
            TeraTestType.undelete(id_test_type)

            self.assertIsNone(TeraTest.get_test_by_id(id_test))
            self.assertIsNotNone(TeraTestType.get_test_type_by_id(id_test_type))
            self.assertIsNotNone(TeraTestTypeSite.get_test_type_site_by_id(id_test_type_site))
            self.assertIsNotNone(TeraTestTypeProject.get_test_type_project_by_id(id_test_type_project))

    @staticmethod
    def new_test_test_type(id_service: int = 1) -> TeraTestType:
        test_type = TeraTestType()
        test_type.test_type_name = "Test test type..."
        test_type.id_service = id_service
        TeraTestType.insert(test_type)
        return test_type
