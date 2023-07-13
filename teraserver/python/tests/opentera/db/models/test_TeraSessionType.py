from tests.opentera.db.models.BaseModelsTest import BaseModelsTest
from opentera.db.models.TeraSessionType import TeraSessionType
from opentera.db.models.TeraSession import TeraSession


class TeraSessionTypeTest(BaseModelsTest):

    def test_defaults(self):
        with self._flask_app.app_context():
            pass

    def test_soft_delete(self):
        with self._flask_app.app_context():
            # Create new
            ses_type = TeraSessionType()
            ses_type.session_type_online = False
            ses_type.session_type_color = ""
            ses_type.session_type_category = TeraSessionType.SessionCategoryEnum.DATACOLLECT.value
            ses_type.session_type_name = 'Session Type Test'
            TeraSessionType.insert(ses_type)
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
            ses_type = TeraSessionType()
            ses_type.session_type_online = False
            ses_type.session_type_color = ""
            ses_type.session_type_category = TeraSessionType.SessionCategoryEnum.DATACOLLECT.value
            ses_type.session_type_name = 'Session Type Test'
            TeraSessionType.insert(ses_type)
            id_session_type = ses_type.id_session_type

            # Create a new session of that session type
            ses = TeraSession()
            ses.id_creator_service = 1
            ses.id_session_type = id_session_type
            ses.session_name = "Test session"
            TeraSession.insert(ses)
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
