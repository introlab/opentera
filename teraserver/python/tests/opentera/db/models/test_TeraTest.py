from tests.opentera.db.models.BaseModelsTest import BaseModelsTest
from opentera.db.models.TeraTest import TeraTest
from opentera.db.models.TeraSession import TeraSession
from opentera.db.models.TeraParticipant import TeraParticipant
from opentera.db.models.TeraUser import TeraUser
from opentera.db.models.TeraDevice import TeraDevice
from sqlalchemy.exc import IntegrityError


class TeraTestTest(BaseModelsTest):

    def test_defaults(self):
        with self._flask_app.app_context():
            pass

    def test_db_events_not_none(self):
        with self._flask_app.app_context():
            test : TeraTest = TeraTestTest.new_test_test(id_session=1)
            self.assertIsNotNone(test.to_json_create_event())
            self.assertIsNotNone(test.to_json_update_event())
            self.assertIsNotNone(test.to_json_delete_event())

    def test_soft_delete(self):
        with self._flask_app.app_context():
            # Create new
            test = TeraTestTest.new_test_test(id_session=1, id_participant=1)
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
            test = TeraTestTest.new_test_test(id_session=1, id_device=1)
            self.assertIsNotNone(test.id_test)
            id_test = test.id_test

            # Hard delete
            TeraTest.delete(id_test, hard_delete=True)

            # Make sure eveything is deleted
            self.assertIsNone(TeraTest.get_test_by_id(id_test, True))

    def test_undelete(self):
        with self._flask_app.app_context():
            # Create new participant
            from tests.opentera.db.models.test_TeraParticipant import TeraParticipantTest
            participant = TeraParticipantTest.new_test_participant(id_project=1)
            id_participant = participant.id_participant

            # Create new device
            from tests.opentera.db.models.test_TeraDevice import TeraDeviceTest
            device = TeraDeviceTest.new_test_device()
            id_device = device.id_device

            # Create new user
            from tests.opentera.db.models.test_TeraUser import TeraUserTest
            user = TeraUserTest.new_test_user(user_name='test_testuser')
            id_user = user.id_user

            # Create new session
            from tests.opentera.db.models.test_TeraSession import TeraSessionTest
            ses = TeraSessionTest.new_test_session(participants=[participant], users=[user], devices=[device])
            id_session = ses.id_session

            # Create new test
            test = TeraTestTest.new_test_test(id_session=ses.id_session, id_user=id_user, id_participant=id_participant,
                                              id_device=id_device)
            self.assertIsNotNone(test.id_test)
            id_test = test.id_test

            # Undelete
            TeraTest.undelete(id_test)

            # Make sure it is back!
            self.db.session.expire_all()
            test = TeraTest.get_test_by_id(id_test)
            self.assertIsNotNone(test)
            self.assertIsNone(test.deleted_at)

            # Now, delete again but with its dependencies...
            # Test will be deleted with the session
            TeraSession.delete(id_session)
            TeraParticipant.delete(id_participant)
            TeraDevice.delete(id_device)
            TeraUser.delete(id_user)

            # Exception should be thrown when trying to undelete
            with self.assertRaises(IntegrityError):
                TeraTest.undelete(id_test)

            # Restore participant
            TeraParticipant.undelete(id_participant)
            participant = TeraParticipant.get_participant_by_id(id_participant)
            self.assertIsNotNone(participant)

            # Restore test - still has dependencies issues...
            with self.assertRaises(IntegrityError):
                TeraTest.undelete(id_test)

            # Restore user
            TeraUser.undelete(id_user)
            user = TeraUser.get_user_by_id(id_user)
            self.assertIsNotNone(user)

            # Restore test - still has dependencies issues...
            with self.assertRaises(IntegrityError):
                TeraTest.undelete(id_test)

            # Restore device
            TeraDevice.undelete(id_device)
            device = TeraDevice.get_device_by_id(id_device)
            self.assertIsNotNone(device)

            # Restore test - still has dependencies issues...
            with self.assertRaises(IntegrityError):
                TeraTest.undelete(id_test)

            # Restore session
            TeraSession.undelete(id_session)

            ses = TeraSession.get_session_by_id(id_session)
            self.assertIsNotNone(ses)

            # Test was restored with the session...
            self.db.session.expire_all()
            test = TeraTest.get_test_by_id(id_test)
            self.assertIsNotNone(test)
            self.assertIsNone(test.deleted_at)

    @staticmethod
    def new_test_test(id_session: int, id_test_type: int = 1, id_device: int | None = None,
                      id_participant: int | None = None, id_service: int | None = None,
                      id_user: int | None = None) -> TeraTest:
        test = TeraTest()
        test.id_session = id_session
        test.id_test_type = id_test_type
        test.test_name = "Test test!"
        if id_device:
            test.id_device = id_device
        if id_participant:
            test.id_participant = id_participant
        if id_service:
            test.id_service = id_service
        if id_user:
            test.id_user = id_user
        TeraTest.insert(test)

        return test
