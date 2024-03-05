from opentera.db.models.TeraService import TeraService
from opentera.db.models import TeraUser
from opentera.db.models.TeraServiceAccess import TeraServiceAccess
from opentera.db.models.TeraParticipantGroup import TeraParticipantGroup
from opentera.db.models.TeraServiceRole import TeraServiceRole
from opentera.db.models.TeraProject import TeraProject

from sqlalchemy import or_, not_, and_


class DBManagerTeraServiceAccess:
    def __init__(self, service: TeraService):
        self.service = service

    def get_accessible_devices(self, admin_only=False):
        from opentera.db.models.TeraDevice import TeraDevice
        from opentera.db.models.TeraDeviceProject import TeraDeviceProject

        # Get projects available to that service
        proj_id_list = self.get_accessible_projects_ids(admin_only=admin_only)

        query = TeraDevice.query.join(TeraDeviceProject).filter(TeraDeviceProject.id_project.in_(proj_id_list))
        return query.all()

    def get_accessible_devices_ids(self, admin_only=False):
        return [device.id_device for device in self.get_accessible_devices(admin_only=admin_only)]

    def get_accessible_devices_uuids(self, admin_only=False):
        return [device.device_uuid for device in self.get_accessible_devices(admin_only=admin_only)]

    def get_accessible_projects(self, admin_only=False):
        project_list = []

        # Build project list - get projects where that service is associated
        from opentera.db.models.TeraServiceProject import TeraServiceProject
        service_projects = TeraServiceProject.get_projects_for_service(self.service.id_service)

        for service_project in service_projects:
            project_list.append(service_project.service_project_project)

        return project_list

    def get_accessible_projects_ids(self, admin_only=False):
        projects = []

        for project in self.get_accessible_projects(admin_only=admin_only):
            projects.append(project.id_project)

        return projects

    def get_accessible_sessions(self, admin_only=False):
        from opentera.db.models.TeraSession import TeraSession
        from opentera.db.models.TeraSessionUsers import TeraSessionUsers
        from opentera.db.models.TeraSessionParticipants import TeraSessionParticipants
        from opentera.db.models.TeraSessionDevices import TeraSessionDevices

        part_ids = self.get_accessible_participants_ids(admin_only=admin_only)
        user_ids = self.get_accessible_users_ids(admin_only=admin_only)
        # Also includes super admins users in the list
        user_ids.extend([user.id_user for user in TeraUser.get_superadmins() if user.id_user not in user_ids])
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

    def get_accessible_sessions_ids(self, admin_only=False):
        ses_ids = []

        for ses in self.get_accessible_sessions(admin_only=admin_only):
            ses_ids.append(ses.id_session)

        return ses_ids

    def get_accessibles_sites(self):
        # Build site list - get sites where that service is associated
        from opentera.db.models.TeraServiceSite import TeraServiceSite
        service_sites = TeraServiceSite.get_sites_for_service(self.service.id_service)

        site_list = []
        for service_site in service_sites:
            site_list.append(service_site.service_site_site)
        return site_list

    def get_accessibles_sites_ids(self):
        return [site.id_site for site in self.get_accessibles_sites()]

    def get_accessible_participants(self, admin_only=False):
        project_id_list = self.get_accessible_projects_ids(admin_only=admin_only)
        participant_list = []

        from opentera.db.models.TeraParticipant import TeraParticipant
        participant_list.extend(TeraParticipant.query.filter(TeraParticipant.id_project.in_(project_id_list)))

        return participant_list

    def get_accessible_participants_ids(self, admin_only=False):
        return [participant.id_participant for participant in self.get_accessible_participants(admin_only=admin_only)]

    def get_accessible_participants_uuids(self, admin_only=False):
        return [participant.participant_uuid for participant in self.get_accessible_participants(admin_only=admin_only)]

    def get_accessible_participants_groups(self):
        project_id_list = self.get_accessible_projects_ids()
        groups = TeraParticipantGroup.query.join(TeraProject).filter(TeraProject.id_project.in_(project_id_list)).all()
        return groups

    def get_accessible_participants_groups_ids(self):
        return [group.id_participant_group for group in self.get_accessible_participants_groups()]

    def get_accessible_users(self, admin_only=False):
        projects = self.get_accessible_projects(admin_only=admin_only)
        users = []
        for project in projects:
            # Always include super admins for services
            project_users = project.get_users_in_project(include_superadmins=True, include_site_access=True)
            users.extend([user for user in project_users if user not in users])

        # Sort by user first name
        return sorted(users, key=lambda suser: suser.user_firstname)

    def get_accessible_users_ids(self, admin_only=False):
        return [user.id_user for user in self.get_accessible_users(admin_only=admin_only)]

    def get_accessible_usergroups(self):
        # Usergroup is accessible if it has a direct association to this service
        access = TeraServiceAccess.query.join(TeraServiceRole). \
            filter(TeraServiceRole.id_service == self.service.id_service). \
            filter(TeraServiceAccess.id_user_group != None).all()

        # Usergroup is accessible if it has access to a service site / project or if it has a role in the service
        # project_ids = self.get_accessible_projects_ids()
        # site_ids = self.get_accessibles_sites_ids()
        # access = TeraServiceAccess.query.join(TeraServiceRole).\
        #     filter(or_(TeraServiceRole.id_service == self.service.id_service,
        #                and_(TeraServiceRole.id_service == TeraService.get_openteraserver_service().id_service,
        #                     or_(TeraServiceRole.id_project == None, TeraServiceRole.id_project.in_(project_ids)),
        #                     or_(TeraServiceRole.id_site == None, TeraServiceRole.id_site.in_(site_ids)),
        #                     ).self_group()
        #                )
        #            ).filter(TeraServiceAccess.id_user_group != None).all()

        usergroups = []
        if access:
            for service_access in access:
                ug = service_access.service_access_user_group
                if ug not in usergroups:
                    usergroups.append(ug)

        return usergroups

    def get_accessible_usergroups_ids(self):
        return [ug.id_user_group for ug in self.get_accessible_usergroups()]

    def get_accessible_users_uuids(self, admin_only=False):
        return [user.user_uuid for user in self.get_accessible_users(admin_only=admin_only)]

    def get_accessible_sessions_types(self):
        from opentera.db.models.TeraSessionType import TeraSessionType

        query = TeraSessionType.query.filter(TeraSessionType.id_service == self.service.id_service)\
            .order_by(TeraSessionType.session_type_name.asc())

        return query.all()

    def get_accessible_sessions_types_ids(self):
        return [st.id_session_type for st in self.get_accessible_sessions_types()]

    def get_accessible_tests_types(self):
        from opentera.db.models.TeraTestType import TeraTestType

        query = TeraTestType.query.filter(TeraTestType.id_service == self.service.id_service)\
            .order_by(TeraTestType.test_type_name.asc())

        return query.all()

    def get_accessible_tests_types_ids(self):
        return [tt.id_test_type for tt in self.get_accessible_tests_types()]

    def get_site_role(self, site_id: int, uuid_user: str):
        user = self.get_user_with_uuid(uuid_user)
        sites_roles = user.get_sites_roles()
        role = [role for site, role in sites_roles.items() if site.id_site == int(site_id)]
        if len(role) == 1:
            return role[0]['site_role']
        return None

    def get_project_role(self, project_id: int, uuid_user: str):
        user = self.get_user_with_uuid(uuid_user)
        projects_roles = user.get_projects_roles()
        role = [role for project, role in projects_roles.items() if project.id_project == int(project_id)]
        if len(role) == 1:
            return role[0]['project_role']
        return None

    def get_user_with_uuid(self, uuid_user):
        return TeraUser.get_user_by_uuid(uuid_user)

    def query_sites_for_user(self, user_id: int, admin_only: bool = False):
        sites = []
        if user_id in self.get_accessible_users_ids():
            from opentera.db.models.TeraSite import TeraSite
            user = TeraUser.get_user_by_id(id_user=user_id)
            acc_sites_ids = self.get_accessibles_sites_ids()
            if user.user_superadmin:
                sites = TeraSite.query.order_by(TeraSite.site_name.asc()).all()
            else:
                site_roles = user.get_sites_roles()
                sites = [site for site in site_roles if not admin_only or
                         (admin_only and site_roles[site]['site_role'] == 'admin')]

            sites = [site for site in sites if site.id_site in acc_sites_ids]

        return sites

    def query_asset(self, asset_id: int):
        from opentera.db.models.TeraAsset import TeraAsset
        from sqlalchemy import or_

        # If a service has access to a session, it should have access to its assets
        session_ids = self.get_accessible_sessions_ids()
        # device_ids = self.get_accessible_devices_ids()
        # participant_ids = self.get_accessible_participants_ids()
        # user_ids = self.get_accessible_users_ids()
        # service_ids = self.get_accessible_services_ids()

        return TeraAsset.query.filter(TeraAsset.id_session.in_(session_ids)).filter(TeraAsset.id_asset == asset_id)\
            .all()
        # .filter(or_(TeraAsset.id_service.in_(service_ids), TeraAsset.id_service == None)) \

    def query_test(self, test_id: int = None, test_uuid: str = None):
        from opentera.db.models.TeraTest import TeraTest

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

    def query_session(self, session_id: int):
        from opentera.db.models.TeraSession import TeraSession

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

    def query_usergroups_for_site(self, site_id: int):
        all_users_groups = self.get_accessible_usergroups()
        users_groups = {}
        for user_group in all_users_groups:
            sites = {key.id_site: value for key, value in user_group.get_sites_roles().items()
                     if key.id_site == site_id}
            if site_id in sites:
                users_groups[user_group] = sites[site_id]
        return users_groups

    def query_usergroups_for_project(self, project_id: int):
        all_users_groups = self.get_accessible_usergroups()
        users_groups = {}
        for user_group in all_users_groups:

            projects = {key.id_project: value for key, value in user_group.get_projects_roles().items()
                        if key.id_project == project_id}

            if project_id in projects:
                users_groups[user_group] = projects[project_id]

        return users_groups
