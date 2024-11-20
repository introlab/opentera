from sqlalchemy import or_, not_, and_

from opentera.db.models.TeraService import TeraService
from opentera.db.models import TeraUser
from opentera.db.models.TeraUserGroup import TeraUserGroup
from opentera.db.models.TeraServiceAccess import TeraServiceAccess
from opentera.db.models.TeraParticipantGroup import TeraParticipantGroup
from opentera.db.models.TeraServiceRole import TeraServiceRole
from opentera.db.models.TeraProject import TeraProject
from opentera.db.models.TeraParticipant import TeraParticipant
from opentera.db.models.TeraServiceProject import TeraServiceProject
from opentera.db.models.TeraDevice import TeraDevice
from opentera.db.models.TeraDeviceProject import TeraDeviceProject
from opentera.db.models.TeraSession import TeraSession
from opentera.db.models.TeraSessionUsers import TeraSessionUsers
from opentera.db.models.TeraSessionParticipants import TeraSessionParticipants
from opentera.db.models.TeraSessionDevices import TeraSessionDevices
from opentera.db.models.TeraServiceSite import TeraServiceSite
from opentera.db.models.TeraSessionType import TeraSessionType
from opentera.db.models.TeraTestType import TeraTestType
from opentera.db.models.TeraAsset import TeraAsset
from opentera.db.models.TeraTest import TeraTest
from opentera.db.models.TeraSite import TeraSite

from modules.DatabaseModule.DBManagerTeraUserAccess import DBManagerTeraUserAccess
from modules.DatabaseModule.DBManagerTeraParticipantAccess import DBManagerTeraParticipantAccess
from modules.DatabaseModule.DBManagerTeraDeviceAccess import DBManagerTeraDeviceAccess


class DBManagerTeraServiceAccess:
    def __init__(self, service: TeraService):
        self.service = service

    def get_accessible_devices(self, admin_only=False) -> list[TeraDevice]:
        # Get projects available to that service
        proj_id_list = self.get_accessible_projects_ids(admin_only=admin_only)

        query = TeraDevice.query.join(TeraDeviceProject).filter(TeraDeviceProject.id_project.in_(proj_id_list))
        return query.all()

    def get_accessible_devices_ids(self, admin_only=False) -> list[int]:
        return [device.id_device for device in self.get_accessible_devices(admin_only=admin_only)]

    def get_accessible_devices_uuids(self, admin_only=False) -> list[str]:
        return [device.device_uuid for device in self.get_accessible_devices(admin_only=admin_only)]

    def get_accessible_projects(self, admin_only=False) -> list[TeraProject]:
        project_list = []

        # Build project list - get projects where that service is associated

        service_projects = TeraServiceProject.get_projects_for_service(self.service.id_service)

        for service_project in service_projects:
            project_list.append(service_project.service_project_project)

        return project_list

    def get_accessible_projects_ids(self, admin_only=False) -> list[int]:
        projects = []

        for project in self.get_accessible_projects(admin_only=admin_only):
            projects.append(project.id_project)

        return projects

    def get_accessible_sessions(self, admin_only=False) -> list[TeraSession]:
        part_ids = self.get_accessible_participants_ids(admin_only=admin_only)
        user_ids = self.get_accessible_users_ids(admin_only=admin_only)

        # DL 2024-11-20: Removed super admins from the list of users to get sessions from
        # user_ids.extend([user.id_user for user in TeraUser.get_superadmins() if user.id_user not in user_ids])

        device_ids = self.get_accessible_devices_ids(admin_only=admin_only)
        sessions = TeraSession.query.filter(or_(TeraSession.id_creator_user.in_(user_ids),
                                                TeraSession.id_creator_device.in_(device_ids),
                                                TeraSession.id_creator_participant.in_(part_ids),
                                                TeraSession.id_creator_service.in_([self.service.id_service]))).all()

        # Also check for sessions which users we have access to were part
        sessions_ids = [session.id_session for session in sessions]
        other_sessions = TeraSessionUsers.query.filter(TeraSessionUsers.id_user.in_(user_ids)). \
            filter(not_(TeraSessionUsers.id_session.in_(sessions_ids)))
        sessions.extend(other_sessions)

        # ... and sessions which participants we have access to were part
        sessions_ids = [session.id_session for session in sessions]
        other_sessions = TeraSessionParticipants.query.filter(TeraSessionParticipants.id_participant.in_(part_ids)). \
            filter(not_(TeraSessionParticipants.id_session.in_(sessions_ids)))
        sessions.extend(other_sessions)

        # ... and sessions which devices we have access to were part!
        sessions_ids = [session.id_session for session in sessions]
        other_sessions = TeraSessionDevices.query.filter(TeraSessionDevices.id_device.in_(device_ids)). \
            filter(not_(TeraSessionDevices.id_session.in_(sessions_ids)))
        sessions.extend(other_sessions)

        return sessions

    def get_accessible_sessions_ids(self, admin_only=False) -> list[int]:
        ses_ids = []

        for ses in self.get_accessible_sessions(admin_only=admin_only):
            ses_ids.append(ses.id_session)

        return ses_ids

    def get_accessibles_sites(self) -> list[TeraSite]:
        # Build site list - get sites where that service is associated
        service_sites = TeraServiceSite.get_sites_for_service(self.service.id_service)

        site_list = []
        for service_site in service_sites:
            site_list.append(service_site.service_site_site)
        return site_list

    def get_accessible_sites_ids(self) -> list[int]:
        return [site.id_site for site in self.get_accessibles_sites()]

    def get_accessible_participants(self, admin_only=False) -> list[TeraParticipant]:
        project_id_list = self.get_accessible_projects_ids(admin_only=admin_only)
        participant_list = []
        participant_list.extend(TeraParticipant.query.filter(TeraParticipant.id_project.in_(project_id_list)))
        return participant_list

    def get_accessible_participants_ids(self, admin_only=False) -> list[int]:
        return [participant.id_participant for participant in self.get_accessible_participants(admin_only=admin_only)]

    def get_accessible_participants_uuids(self, admin_only=False) -> list[str]:
        return [participant.participant_uuid for participant in self.get_accessible_participants(admin_only=admin_only)]

    def get_accessible_participants_groups(self) -> list[TeraParticipantGroup]:
        project_id_list = self.get_accessible_projects_ids()
        groups = TeraParticipantGroup.query.join(TeraProject).filter(TeraProject.id_project.in_(project_id_list)).all()
        return groups

    def get_accessible_participants_groups_ids(self) -> list[int]:
        return [group.id_participant_group for group in self.get_accessible_participants_groups()]

    def get_accessible_users(self, admin_only=False) -> list[TeraUser]:
        projects = self.get_accessible_projects(admin_only=admin_only)
        users = []
        for project in projects:
            # DL 2024-11-20: Removed super admins from the list of users
            project_users = project.get_users_in_project(include_superadmins=False, include_site_access=True)
            users.extend([user for user in project_users if user not in users])

        # Sort by user first name
        return sorted(users, key=lambda suser: suser.user_firstname)

    def get_accessible_users_ids(self, admin_only=False) -> list[int]:
        return [user.id_user for user in self.get_accessible_users(admin_only=admin_only)]

    def get_accessible_usergroups(self) -> list[TeraUserGroup]:
        # Usergroup is accessible if it has a direct association to this service
        access = TeraServiceAccess.query.join(TeraServiceRole). \
            filter(TeraServiceRole.id_service == self.service.id_service). \
            filter(TeraServiceAccess.id_user_group != None).all()

        usergroups = []
        if access:
            for service_access in access:
                ug = service_access.service_access_user_group
                if ug not in usergroups:
                    usergroups.append(ug)

        return usergroups

    def get_accessible_usergroups_ids(self) -> list[int]:
        return [ug.id_user_group for ug in self.get_accessible_usergroups()]

    def get_accessible_users_uuids(self, admin_only=False) -> list[str]:
        return [user.user_uuid for user in self.get_accessible_users(admin_only=admin_only)]

    def get_accessible_sessions_types(self) -> list[TeraSessionType]:
        query = TeraSessionType.query.filter(TeraSessionType.id_service == self.service.id_service)\
            .order_by(TeraSessionType.session_type_name.asc())

        return query.all()

    def get_accessible_sessions_types_ids(self) -> list[int]:
        return [st.id_session_type for st in self.get_accessible_sessions_types()]

    def get_accessible_tests_types(self) -> list[TeraTestType]:
        query = TeraTestType.query.filter(TeraTestType.id_service == self.service.id_service)\
            .order_by(TeraTestType.test_type_name.asc())
        return query.all()

    def get_accessible_tests_types_for_participant(self, id_participant: int) -> list[TeraTestType]:
        # Initial list is all test types related to the service
        participant = TeraParticipant.get_participant_by_id(id_participant)
        if participant:
            test_type_participant = DBManagerTeraParticipantAccess(participant).get_accessible_tests_types()
            # Keep only test types in this service
            test_types = [test_type for test_type in test_type_participant if test_type.id_service == self.service.id_service]
            return test_types
        return []

    def get_accessible_tests_types_ids_for_participant(self, id_participant: int) -> list[int]:
        return [tt.id_test_type for tt in self.get_accessible_tests_types_for_participant(id_participant)]

    def get_accessible_tests_types_for_user(self, id_user: int) -> list[TeraTestType]:
        # Initial list is all test types related to the service
        user = TeraUser.get_user_by_id(id_user)
        if user:
            test_type_user = DBManagerTeraUserAccess(user).get_accessible_tests_types()
            # Keep only test types in this service
            test_types = [test_type for test_type in test_type_user if test_type.id_service == self.service.id_service]
            return test_types
        return []

    def get_accessible_tests_types_for_device(self, id_device: int) -> list[TeraTestType]:
        device = TeraDevice.get_device_by_id(id_device)
        if device:
            test_type_device = DBManagerTeraDeviceAccess(device).get_accessible_tests_types()
            # Keep only test types in this service
            test_types = [test_type for test_type in test_type_device if test_type.id_service == self.service.id_service]
            return test_types
        return []

    def get_accessible_tests_types_ids_for_device(self, id_device: int) -> list[int]:
        return [tt.id_test_type for tt in self.get_accessible_tests_types_for_device(id_device)]

    def get_accessible_tests_types_ids_for_user(self, id_user: int) -> list[int]:
        return [tt.id_test_type for tt in self.get_accessible_tests_types_for_user(id_user)]

    def get_accessible_tests_types_ids(self) -> list[int]:
        return [tt.id_test_type for tt in self.get_accessible_tests_types()]

    def get_site_role(self, site_id: int, uuid_user: str) -> str | None:
        user = self.get_user_with_uuid(uuid_user)
        sites_roles = user.get_sites_roles()
        role = [role for site, role in sites_roles.items() if site.id_site == int(site_id)]
        if len(role) == 1:
            return role[0]['site_role']
        return None

    def get_project_role(self, project_id: int, uuid_user: str) -> str | None:
        user = self.get_user_with_uuid(uuid_user)
        projects_roles = user.get_projects_roles()
        role = [role for project, role in projects_roles.items() if project.id_project == int(project_id)]
        if len(role) == 1:
            return role[0]['project_role']
        return None

    def get_user_with_uuid(self, uuid_user) -> TeraUser:
        return TeraUser.get_user_by_uuid(uuid_user)

    def query_sites_for_user(self, user_id: int, admin_only: bool = False) -> list[TeraSite]:
        sites = []
        if user_id in self.get_accessible_users_ids():

            user = TeraUser.get_user_by_id(id_user=user_id)
            acc_sites_ids = self.get_accessible_sites_ids()
            if user.user_superadmin:
                sites = TeraSite.query.order_by(TeraSite.site_name.asc()).all()
            else:
                site_roles = user.get_sites_roles()
                sites = [site for site in site_roles if not admin_only or
                         (admin_only and site_roles[site]['site_role'] == 'admin')]

            sites = [site for site in sites if site.id_site in acc_sites_ids]

        return sites

    def query_asset(self, asset_id: int) -> TeraAsset | None:
        # If a service has access to a session, it should have access to its assets
        session_ids = self.get_accessible_sessions_ids()
        # device_ids = self.get_accessible_devices_ids()
        # participant_ids = self.get_accessible_participants_ids()
        # user_ids = self.get_accessible_users_ids()
        # service_ids = self.get_accessible_services_ids()

        return TeraAsset.query.filter(TeraAsset.id_session.in_(session_ids)).filter(TeraAsset.id_asset == asset_id)\
            .all()
        # .filter(or_(TeraAsset.id_service.in_(service_ids), TeraAsset.id_service == None)) \

    def query_test(self, test_id: int = None, test_uuid: str = None) -> TeraTest | None:
        if not test_id and not test_uuid:
            return None

        test = None
        if test_id:
            test = TeraTest.get_test_by_id(test_id)
        elif test_uuid:
            test = TeraTest.get_test_by_uuid(test_uuid)

        if not test:
            return None

        test_session = self.query_session(test.id_session)
        if not test_session:
            # No access to asset session
            return None

        return test

    def query_session(self, session_id: int) -> TeraSession | None:
        session = TeraSession.get_session_by_id(session_id)

        if session:
            # Check if we are the creator of that session
            if session.id_creator_service == self.service.id_service:
                return session

            # Check if we have access to the project of that session
            accessible_projects = self.get_accessible_projects_ids()
            if session.get_associated_project_id() in accessible_projects:
                return session

        return None

    def query_usergroups_for_site(self, site_id: int) -> dict[TeraUserGroup, dict]:
        all_users_groups = self.get_accessible_usergroups()
        users_groups = {}
        for user_group in all_users_groups:
            sites = {key.id_site: value for key, value in user_group.get_sites_roles().items()
                     if key.id_site == site_id}
            if site_id in sites:
                users_groups[user_group] = sites[site_id]
        return users_groups

    def query_usergroups_for_project(self, project_id: int) -> dict[TeraUserGroup, dict]:
        all_users_groups = self.get_accessible_usergroups()
        users_groups = {}
        for user_group in all_users_groups:

            projects = {key.id_project: value for key, value in user_group.get_projects_roles().items()
                        if key.id_project == project_id}

            if project_id in projects:
                users_groups[user_group] = projects[project_id]

        return users_groups
