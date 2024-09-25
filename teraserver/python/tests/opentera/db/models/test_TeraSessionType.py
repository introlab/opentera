from tests.opentera.db.models.BaseModelsTest import BaseModelsTest
from opentera.db.models.TeraSessionType import TeraSessionType
from opentera.db.models.TeraSession import TeraSession
from opentera.db.models.TeraService import TeraService
from opentera.db.models.TeraSessionTypeProject import TeraSessionTypeProject
from opentera.db.models.TeraSessionTypeSite import TeraSessionTypeSite
from sqlalchemy.exc import IntegrityError


class TeraSessionTypeTest(BaseModelsTest):

    def test_defaults(self):
        with self._flask_app.app_context():
            pass

    def test_soft_delete(self):
        with self._flask_app.app_context():
            # Create new
            ses_type = TeraSessionTypeTest.new_test_session_type()
            id_session_type = ses_type.id_session_type

            # Soft delete
            TeraSessionType.delete(id_session_type)

            # Make sure it is deleted
            self.assertIsNone(TeraSessionType.get_session_type_by_id(id_session_type))

            # Query, with soft delete flag
            ses_type = TeraSessionType.query.filter_by(id_session_type=id_session_type).\
                execution_options(include_deleted=True).first()
            self.assertIsNotNone(ses_type)
            self.assertIsNotNone(ses_type.deleted_at)

    def test_hard_delete(self):
        with self._flask_app.app_context():
            # Create new
            ses_type = TeraSessionTypeTest.new_test_session_type()
            id_session_type = ses_type.id_session_type

            # Create a new session of that session type
            from tests.opentera.db.models.test_TeraSession import TeraSessionTest
            ses = TeraSessionTest.new_test_session(id_session_type=id_session_type, id_creator_service=1)
            id_session = ses.id_session

            # Soft delete to prevent relationship integrity errors as we want to test hard-delete cascade here
            TeraSession.delete(id_session)
            TeraSessionType.delete(id_session_type)

            # Check that relationships are still there
            self.assertIsNone(TeraSessionType.get_session_type_by_id(id_session_type))
            self.assertIsNotNone(TeraSessionType.get_session_type_by_id(id_session_type, True))
            self.assertIsNone(TeraSession.get_session_by_id(id_session))
            self.assertIsNotNone(TeraSession.get_session_by_id(id_session, True))

            # Hard delete
            TeraSessionType.delete(id_session_type, hard_delete=True)

            # Make sure eveything is deleted
            self.assertIsNone(TeraSessionType.get_session_type_by_id(id_session_type, True))
            self.assertIsNone(TeraSession.get_session_by_id(id_session, True))

    def test_undelete(self):
        with self._flask_app.app_context():
            # Create new service
            from tests.opentera.db.models.test_TeraService import TeraServiceTest
            service = TeraServiceTest.new_test_service('SessionTypeService')
            id_service = service.id_service

            # Create new
            ses_type = TeraSessionTypeTest.new_test_session_type(id_service=id_service)
            id_session_type = ses_type.id_session_type

            # Create a new session of that session type
            from tests.opentera.db.models.test_TeraSession import TeraSessionTest
            ses = TeraSessionTest.new_test_session(id_session_type=id_session_type, id_creator_service=1)
            id_session = ses.id_session

            # Associate session type to site
            from tests.opentera.db.models.test_TeraSessionTypeSite import TeraSessionTypeSiteTest
            ses_site = TeraSessionTypeSiteTest.new_test_session_type_site(id_site=1, id_session_type=id_session_type)
            id_session_type_site = ses_site.id_session_type_site

            # ... and project
            from tests.opentera.db.models.test_TeraSessionTypeProject import TeraSessionTypeProjectTest
            ses_proj = TeraSessionTypeProjectTest.new_test_session_type_project(id_project=1,
                                                                                id_session_type=id_session_type)
            id_session_type_project = ses_proj.id_session_type_project

            # Soft delete to prevent relationship integrity errors as we want to test hard-delete cascade here
            TeraSession.delete(id_session)
            TeraSessionType.delete(id_session_type)
            self.assertIsNone(TeraSessionType.get_session_type_by_id(id_session_type))
            self.assertIsNone(TeraSession.get_session_by_id(id_session))
            self.assertIsNotNone(TeraService.get_service_by_id(id_service))
            self.assertIsNone(TeraSessionTypeSite.get_session_type_site_by_id(id_session_type_site))
            self.assertIsNone(TeraSessionTypeProject.get_session_type_project_by_id(id_session_type_project))

            # Delete service
            TeraService.delete(id_service)

            # Try to undelete SessionType - should not work
            with self.assertRaises(IntegrityError):
                TeraSessionType.undelete(id_session_type)

            # Should now work...
            TeraService.undelete(id_service)
            TeraSessionType.undelete(id_session_type)
            self.assertIsNotNone(TeraSessionType.get_session_type_by_id(id_session_type))
            self.assertIsNone(TeraSession.get_session_by_id(id_session))
            self.assertIsNotNone(TeraService.get_service_by_id(id_service))
            self.assertIsNotNone(TeraSessionTypeSite.get_session_type_site_by_id(id_session_type_site))
            self.assertIsNotNone(TeraSessionTypeProject.get_session_type_project_by_id(id_session_type_project))

    @staticmethod
    def new_test_session_type(id_service: int | None = None) -> TeraSessionType:
        ses_type = TeraSessionType()
        if id_service:
            ses_type.id_service = id_service
        ses_type.session_type_online = False
        ses_type.session_type_color = ""
        ses_type.session_type_category = TeraSessionType.SessionCategoryEnum.DATACOLLECT.value
        ses_type.session_type_name = 'Session Type Test'
        TeraSessionType.insert(ses_type)
        return ses_type
