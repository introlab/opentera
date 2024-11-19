from modules.DatabaseModule.DBManager import DBManager
from modules.DatabaseModule.DBManagerTeraServiceAccess import DBManagerTeraServiceAccess
from opentera.db.models.TeraUser import TeraUser
from opentera.db.models.TeraParticipant import TeraParticipant
from opentera.db.models.TeraParticipantGroup import TeraParticipantGroup
from opentera.db.models.TeraService import TeraService
from opentera.db.models.TeraDevice import TeraDevice
from opentera.db.models.TeraProject import TeraProject
from opentera.db.models.TeraSite import TeraSite
from opentera.db.models.TeraSession import TeraSession
from tests.opentera.db.models.BaseModelsTest import BaseModelsTest


class DBManagerTeraServiceAccessTest(BaseModelsTest):

    def test_video_rehab_service_get_accessible_devices_ids_and_uuids(self):
        """
        This will test at the same time get_accessible_devices and get_accessible_devices_ids/uuids.
        """
        with self._flask_app.app_context():
            service =  TeraService.get_service_by_key('VideoRehabService')
            self.assertIsNotNone(service)
            service_access = DBManager.serviceAccess(service)
            devices_ids : set[int] = set(service_access.get_accessible_devices_ids())
            devices_uuids : set[str] = set(service_access.get_accessible_devices_uuids())

            all_devices = TeraDevice.query.all()
            accessible_devices = set()
            for device in all_devices:
                for project in device.device_projects:
                    if project.id_project in service_access.get_accessible_projects_ids():
                        accessible_devices.add(device.id_device)

            self.assertEqual(len(devices_ids), len(accessible_devices))
            self.assertEqual(len(devices_uuids), len(devices_ids))
            self.assertEqual(devices_ids, accessible_devices)

    def test_video_rehab_service_get_accessible_projects_ids(self):
        """
        This will test at the same time get_accessible_projects and get_accessible_projects_ids.
        """
        with self._flask_app.app_context():
            service =  TeraService.get_service_by_key('VideoRehabService')
            self.assertIsNotNone(service)
            service_access = DBManager.serviceAccess(service)
            projects_ids = set(service_access.get_accessible_projects_ids())

            all_projects: list[TeraProject] = TeraProject.query.all()
            accessible_projects = set()
            for project in all_projects:
                for project_service in project.project_services:
                    if project_service.id_service == service.id_service:
                        accessible_projects.add(project.id_project)
            self.assertEqual(len(projects_ids), len(accessible_projects))
            self.assertEqual(projects_ids, accessible_projects)

    def test_video_rehab_service_get_accessible_sessions_ids(self):
        """
        This will test at the same time get_accessible_sessions and get_accessible_sessions_ids.
        """
        with self._flask_app.app_context():
            service =  TeraService.get_service_by_key('VideoRehabService')
            self.assertIsNotNone(service)
            service_access = DBManager.serviceAccess(service)
            sessions_ids = set(service_access.get_accessible_sessions_ids())

            all_sessions = TeraSession.query.all()
            accessible_sessions = set()

            for session in all_sessions:
                # Creator
                if session.id_creator_service == service.id_service:
                    accessible_sessions.add(session.id_session)
                # Participants
                for participant in session.session_participants:
                    if participant.id_participant in service_access.get_accessible_participants_ids():
                        accessible_sessions.add(session.id_session)
                # Users
                for user in session.session_users:
                    if user.id_user in service_access.get_accessible_users_ids():
                        accessible_sessions.add(session.id_session)
                # Devices
                for device in session.session_devices:
                    if device.id_device in service_access.get_accessible_devices_ids():
                        accessible_sessions.add(session.id_session)

            self.assertEqual(len(sessions_ids), len(accessible_sessions))
            self.assertEqual(sessions_ids, accessible_sessions)

    def test_video_rehab_service_get_accessible_sites_id(self):
        """
        This will test at the same time get_accessible_sites and get_accessible_sites_ids.
        """
        with self._flask_app.app_context():
            service =  TeraService.get_service_by_key('VideoRehabService')
            self.assertIsNotNone(service)
            service_access = DBManager.serviceAccess(service)
            sites_ids = set(service_access.get_accessible_sites_ids())

            all_sites = TeraSite.query.all()
            accessible_sites = set()
            for site in all_sites:
                for project in site.site_projects:
                    if project.id_project in service_access.get_accessible_projects_ids():
                        accessible_sites.add(site.id_site)
            self.assertEqual(len(sites_ids), len(accessible_sites))
            self.assertEqual(sites_ids, accessible_sites)

    def test_video_rehab_service_get_accessible_participants_id(self):
        """
        This will test at the same time get_accessible_participants and get_accessible_participants_ids.
        """
        with self._flask_app.app_context():
            service =  TeraService.get_service_by_key('VideoRehabService')
            self.assertIsNotNone(service)
            service_access = DBManager.serviceAccess(service)
            participants_ids = set(service_access.get_accessible_participants_ids())

            all_participants = TeraParticipant.query.all()
            accessible_participants = set()
            for participant in all_participants:
                if participant.id_project in service_access.get_accessible_projects_ids():
                    accessible_participants.add(participant.id_participant)
            self.assertEqual(len(participants_ids), len(accessible_participants))
            self.assertEqual(participants_ids, accessible_participants)

    def test_video_rehab_service_get_accessible_participant_groups_id(self):
        """
        This will test at the same time get_accessible_participant_groups and get_accessible_participant_groups_ids.
        """
        with self._flask_app.app_context():
            service =  TeraService.get_service_by_key('VideoRehabService')
            self.assertIsNotNone(service)
            service_access = DBManager.serviceAccess(service)
            participant_groups_ids = set(service_access.get_accessible_participants_groups_ids())

            all_participant_groups = TeraParticipantGroup.query.all()
            accessible_participant_groups = set()
            for participant_group in all_participant_groups:
                if participant_group.id_project in service_access.get_accessible_projects_ids():
                    accessible_participant_groups.add(participant_group.id_participant_group)
            self.assertEqual(len(participant_groups_ids), len(accessible_participant_groups))
            self.assertEqual(participant_groups_ids, accessible_participant_groups)
