from tests.opentera.db.models.BaseModelsTest import BaseModelsTest
from sqlalchemy import exc
from opentera.db.models.TeraSite import TeraSite
from opentera.db.models.TeraProject import TeraProject
from opentera.db.models.TeraParticipant import TeraParticipant
from opentera.db.models.TeraSession import TeraSession
from opentera.db.models.TeraDeviceSite import TeraDeviceSite
from opentera.db.models.TeraServiceSite import TeraServiceSite
from opentera.db.models.TeraServiceRole import TeraServiceRole
from opentera.db.models.TeraSessionTypeSite import TeraSessionTypeSite
from opentera.db.models.TeraTestTypeSite import TeraTestTypeSite
from opentera.db.models.TeraDevice import TeraDevice


class TeraSiteTest(BaseModelsTest):

    def test_nullable_args(self):
        with self._flask_app.app_context():
            new_site = TeraSite()
            new_site.site_name = None
            self.db.session.add(new_site)
            self.assertRaises(exc.IntegrityError, self.db.session.commit)

    def test_unique_args(self):
        with self._flask_app.app_context():
            new_site1 = TeraSite()
            same_site1 = TeraSite()
            new_site1.site_name = None
            same_site1.site_name = None
            self.db.session.add(new_site1)
            self.db.session.add(same_site1)
            self.assertRaises(exc.IntegrityError, self.db.session.commit)

    def test_to_json(self):
        with self._flask_app.app_context():
            new_site = TeraSiteTest.new_test_site(name='Site Name')
            new_site_json = new_site.to_json()
            new_site_json_minimal = new_site.to_json(minimal=True)
            self.assertEqual(new_site_json['site_name'], 'Site Name')
            self.assertGreaterEqual(new_site_json['id_site'], 1)
            self.assertEqual(new_site_json_minimal['site_name'], 'Site Name')
            self.assertGreaterEqual(new_site_json_minimal['id_site'], 1)
            # Minimal doesnt change ignore fields

    def test_to_json_create_event(self):
        with self._flask_app.app_context():
            new_site = TeraSite()
            new_site.site_name = 'test_to_json_create_event'
            self.db.session.add(new_site)
            self.db.session.commit()
            self.db.session.rollback()
            new_site_json = new_site.to_json_create_event()
            self.assertEqual(new_site_json['site_name'], new_site.site_name)
            self.assertGreaterEqual(new_site_json['id_site'], 1)

    def test_to_json_update_event(self):
        with self._flask_app.app_context():
            new_site = TeraSiteTest.new_test_site()
            new_site_json = new_site.to_json_update_event()
            self.assertEqual(new_site_json['site_name'], new_site.site_name)
            self.assertGreaterEqual(new_site_json['id_site'], 1)

    def test_to_json_delete_event(self):
        with self._flask_app.app_context():
            new_site = TeraSiteTest.new_test_site()
            new_site_json_delete = new_site.to_json_delete_event()
            self.assertGreaterEqual(new_site_json_delete['id_site'], 1)

    def test_get_site_by_sitename(self):
        with self._flask_app.app_context():
            self.db.session.rollback()
            new_site = TeraSite()
            new_site.site_name = 'test_get_site_by_sitename'
            self.db.session.add(new_site)
            same_site = TeraSite.get_site_by_sitename(sitename=new_site.site_name)
            self.assertEqual(new_site, same_site)

    def test_get_site_by_id(self):
        with self._flask_app.app_context():
            new_site = TeraSite()
            new_site.site_name = 'test_get_site_by_id'
            self.db.session.add(new_site)
            self.db.session.commit()
            same_site = TeraSite.get_site_by_id(site_id=new_site.id_site)
            self.assertEqual(new_site, same_site)

    def test_insert_and_delete(self):
        with self._flask_app.app_context():
            new_site = TeraSiteTest.new_test_site()
            self.assertGreaterEqual(new_site.id_site, 1)
            id_to_del = TeraSite.get_site_by_id(new_site.id_site).id_site
            TeraSite.delete(id_todel=id_to_del)
            same_site = TeraSite()
            same_site.site_name = 'test_insert_and_delete'
            self.db.session.add(same_site)
            self.db.session.commit()

    def test_soft_delete(self):
        with self._flask_app.app_context():
            # Create new
            site = TeraSiteTest.new_test_site()
            id_site = site.id_site

            # Soft delete
            TeraSite.delete(id_site)

            # Make sure it is deleted
            self.assertIsNone(TeraSite.get_site_by_id(id_site))

            # Query, with soft delete flag
            site = TeraSite.query.filter_by(id_site=id_site).execution_options(include_deleted=True).first()
            self.assertIsNotNone(site)
            self.assertIsNotNone(site.deleted_at)

    def test_hard_delete(self):
        with self._flask_app.app_context():
            # Create new
            site = TeraSiteTest.new_test_site()
            id_site = site.id_site

            from test_TeraProject import TeraProjectTest
            project = TeraProjectTest.new_test_project(id_site=id_site)
            self.assertIsNotNone(project.id_project)
            id_project = project.id_project

            from test_TeraParticipant import TeraParticipantTest
            participant = TeraParticipantTest.new_test_participant(id_project=id_project)
            self.assertIsNotNone(participant.id_participant)
            id_participant = participant.id_participant

            from test_TeraSession import TeraSessionTest
            ses = TeraSessionTest.new_test_session(id_session_type=1, id_creator_participant=1,
                                                   participants=[participant])
            id_session = ses.id_session

            # Soft delete to prevent relationship integrity errors as we want to test hard-delete cascade here
            TeraSession.delete(id_session)
            TeraProject.delete(id_project)
            TeraSite.delete(id_site)

            # Check that relationships are still there
            self.assertIsNone(TeraSite.get_site_by_id(id_site))
            self.assertIsNotNone(TeraSite.get_site_by_id(id_site, True))
            self.assertIsNone(TeraProject.get_project_by_id(id_project))
            self.assertIsNotNone(TeraProject.get_project_by_id(id_project, True))
            self.assertIsNone(TeraParticipant.get_participant_by_id(id_participant))
            self.assertIsNotNone(TeraParticipant.get_participant_by_id(id_participant, True))
            self.assertIsNone(TeraSession.get_session_by_id(id_session))
            self.assertIsNotNone(TeraSession.get_session_by_id(id_session, True))

            # Hard delete
            self.db.session.expire_all()
            TeraSite.delete(id_site, hard_delete=True)

            # Make sure eveything is deleted
            self.assertIsNone(TeraSite.get_site_by_id(id_site, True))
            self.assertIsNone(TeraProject.get_project_by_id(id_project, True))
            self.assertIsNone(TeraParticipant.get_participant_by_id(id_participant, True))
            self.assertIsNone(TeraSession.get_session_by_id(id_session, True))

    def test_undelete(self):
        with self._flask_app.app_context():
            # Create new
            site = TeraSiteTest.new_test_site()
            id_site = site.id_site

            # Associate device
            from test_TeraDevice import TeraDeviceTest
            device = TeraDeviceTest.new_test_device()
            id_device = device.id_device

            from test_TeraDeviceSite import TeraDeviceSiteTest
            device = TeraDeviceSiteTest.new_test_device_site(id_device=id_device, id_site=id_site)
            id_device_site = device.id_device_site

            # ... and service
            from test_TeraServiceSite import TeraServiceSiteTest
            service_site = TeraServiceSiteTest.new_test_service_site(id_site=id_site, id_service=3)
            id_service_site = service_site.id_service_site

            # ... and roles
            from test_TeraServiceRole import TeraServiceRoleTest
            role = TeraServiceRoleTest.new_test_service_role(id_service=3, id_site=id_site, role_name='Test')
            id_role = role.id_service_role

            # ... and session type
            from test_TeraSessionTypeSite import TeraSessionTypeSiteTest
            ses_type = TeraSessionTypeSiteTest.new_test_session_type_site(id_site=id_site, id_session_type=1)
            id_session_type = ses_type.id_session_type_site

            # ... and test type
            from test_TeraTestTypeSite import TeraTestTypeSiteTest
            test_type = TeraTestTypeSiteTest.new_test_test_type_site(id_site=id_site, id_test_type=1)
            id_test_type = test_type.id_test_type_site

            # And now, delete!
            TeraSite.delete(id_site)
            self.assertIsNone(TeraSite.get_site_by_id(id_site))
            self.assertIsNone(TeraDeviceSite.get_device_site_by_id(id_device_site))
            self.assertIsNone(TeraServiceSite.get_service_site_by_id(id_service_site))
            self.assertIsNone(TeraServiceRole.get_service_role_by_id(id_role))
            self.assertIsNone(TeraSessionTypeSite.get_session_type_site_by_id(id_session_type))
            self.assertIsNone(TeraTestTypeSite.get_test_type_site_by_id(id_test_type))

            # Undelete
            TeraDevice.delete(id_device)
            TeraSite.undelete(id_site)

            # Check everything again!
            self.assertIsNotNone(TeraSite.get_site_by_id(id_site))
            # Should not be restored since device was deleted
            self.assertIsNone(TeraDeviceSite.get_device_site_by_id(id_device_site))
            self.assertIsNotNone(TeraServiceSite.get_service_site_by_id(id_service_site))
            self.assertIsNotNone(TeraServiceRole.get_service_role_by_id(id_role))
            self.assertIsNotNone(TeraSessionTypeSite.get_session_type_site_by_id(id_session_type))
            self.assertIsNotNone(TeraTestTypeSite.get_test_type_site_by_id(id_test_type))

    @staticmethod
    def new_test_site(name: str = 'Test Site') -> TeraSite:
        site = TeraSite()
        site.site_name = name
        TeraSite.insert(site)
        return site


