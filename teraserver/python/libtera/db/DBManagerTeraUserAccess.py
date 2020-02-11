
from libtera.db.models.TeraUser import TeraUser
from libtera.db.models.TeraSite import TeraSite
from libtera.db.models.TeraProject import TeraProject
from libtera.db.models.TeraParticipant import TeraParticipant
from libtera.db.models.TeraParticipantGroup import TeraParticipantGroup
from libtera.db.models.TeraDeviceType import TeraDeviceType
from libtera.db.models.TeraSessionType import TeraSessionType
from libtera.db.models.TeraDevice import TeraDevice
from libtera.db.models.TeraSession import TeraSession
from libtera.db.models.TeraDeviceSite import TeraDeviceSite
from libtera.db.models.TeraDeviceParticipant import TeraDeviceParticipant

from libtera.db.models.TeraProjectAccess import TeraProjectAccess
from libtera.db.models.TeraSiteAccess import TeraSiteAccess


class DBManagerTeraUserAccess:
    def __init__(self, user: TeraUser):
        self.user = user

    def get_accessible_users_ids(self, admin_only=False):
        users = self.get_accessible_users(admin_only=admin_only)
        users_ids = []
        for user in users:
            if user.id_user not in users_ids:
                users_ids.append(user.id_user)
        return users_ids

    def get_accessible_users(self, admin_only=False):
        if self.user.user_superadmin:
            users = TeraUser.query.all()
        else:
            projects = self.get_accessible_projects(admin_only=admin_only)
            users = []
            for project in projects:
                project_users = project.get_users_in_project()
                for user in project_users:
                    if user not in users:
                        users.append(user)
            # You are always available to yourself!
            if self.user not in users:
                users.append(self)

        # TODO Sort by username
        return users

    def get_accessible_users_uuids(self, admin_only=False):
        users = self.get_accessible_users(admin_only=admin_only)
        users_ids = []
        for user in users:
            if user.id_user not in users_ids:
                users_ids.append(user.user_uuid)
        return users_ids

    def get_project_role(self, project_id: int):
        if self.user.user_superadmin:
            # SuperAdmin is always admin.
            return 'admin'

        role = TeraProjectAccess.query.filter_by(id_user=self.user.id_user, id_project=project_id).first()

        role_name = ''

        if role is not None:
            role_name = role.project_access_role
        else:
            # Site admins are always project admins
            project = TeraProject.get_project_by_id(project_id=project_id)
            site_role = self.get_site_role(project.id_site)
            if site_role == 'admin':
                role_name = 'admin'

        return role_name

    def get_accessible_projects(self, admin_only=False):
        project_list = []
        if self.user.user_superadmin:
            # Is superadmin - admin on all projects
            project_list = TeraProject.query.all()
        else:
            # Build project list - get sites where user is admin
            for site in self.get_accessible_sites():
                if self.get_site_role(site.id_site) == 'admin':
                    project_query = TeraProject.query.filter_by(id_site=site.id_site)
                    if project_query:
                        for project in project_query.all():
                            project_list.append(project)

            # Add specific projects
            for project_access in self.user.user_projects_access:
                project = project_access.project_access_project
                if project not in project_list:
                    if not admin_only or (admin_only and self.get_project_role(project.id_project) == 'admin'):
                        project_list.append(project)
        return project_list

    def get_accessible_devices(self, admin_only=False):
        if self.user.user_superadmin:
            return TeraDevice.query.all()

        site_id_list = self.get_accessible_sites_ids(admin_only=admin_only)
        return TeraDevice.query.filter(TeraDevice.id_site.in_(site_id_list)).all()

    def get_accessible_devices_ids(self, admin_only=False):
        devices = []

        for device in self.get_accessible_devices(admin_only=admin_only):
            devices.append(device.id_device)

        return devices

    def get_accessible_participants(self, admin_only=False):
        project_id_list = self.get_accessible_projects_ids(admin_only=admin_only)
        groups = TeraParticipantGroup.query.filter(TeraParticipantGroup.id_project.in_(project_id_list)).all()
        participant_list = []
        for group in groups:
            participant_list.extend(TeraParticipant.query.
                                    filter_by(id_participant_group=group.id_participant_group).all())

        return participant_list

    def get_accessible_participants_ids(self, admin_only=False):
        parts = []

        for part in self.get_accessible_participants(admin_only=admin_only):
            parts.append(part.id_participant)

        return parts

    def get_accessible_groups(self, admin_only=False):
        project_id_list = self.get_accessible_projects_ids(admin_only=admin_only)
        return TeraParticipantGroup.query.filter(TeraParticipantGroup.id_project.in_(project_id_list)).all()

    def get_accessible_groups_ids(self, admin_only=False):
        groups = []

        for group in self.get_accessible_groups(admin_only=admin_only):
            groups.append(group.id_participant_group)

        return groups

    def get_accessible_projects_ids(self, admin_only=False):
        projects = []

        for project in self.get_accessible_projects(admin_only=admin_only):
            projects.append(project.id_project)

        return projects

    def get_accessible_sites(self, admin_only=False):
        if self.user.user_superadmin:
            site_list = TeraSite.query.all()
        else:
            site_list = []
            for site_access in self.user.user_sites_access:
                if not admin_only or (admin_only and site_access.site_access_role == 'admin'):
                    site_list.append(site_access.site_access_site)

        return site_list

    def get_accessible_sites_ids(self, admin_only=False):
        sites_ids = []

        for site in self.get_accessible_sites(admin_only=admin_only):
            sites_ids.append(site.id_site)

        return sites_ids

    def get_accessible_session_types(self, admin_only=False):
        from libtera.db.models.TeraSessionTypeProject import TeraSessionTypeProject
        if self.user.user_superadmin:
            return TeraSessionType.query.all()

        project_id_list = self.get_accessible_projects_ids(admin_only=admin_only)
        # return TeraSessionType.query.filter(TeraProject.id_project.in_(project_id_list)).all()
        return TeraSessionType.query.join(TeraSessionTypeProject).filter(TeraSessionTypeProject.id_project.in_(project_id_list)).all()

    def get_accessible_session_types_ids(self, admin_only=False):
        st_ids = []

        for st in self.get_accessible_session_types(admin_only=admin_only):
            st_ids.append(st.id_session_type)

        return st_ids

    def get_projects_roles(self):
        projects_roles = {}
        project_list = self.get_accessible_projects()

        for project in project_list:
            role = self.get_project_role(project)
            projects_roles[project.project_name] = role
        return projects_roles

    def get_sites_roles(self):
        sites_roles = {}

        for site in self.get_accessible_sites():
            sites_roles[site] = self.get_site_role(site)

        return sites_roles

    def get_site_role(self, site_id: int):
        if self.user.user_superadmin:
            # SuperAdmin is always admin.
            return 'admin'

        role = TeraSiteAccess.query.filter_by(id_user=self.user.id_user, id_site=site_id).first()
        if role is not None:
            role_name = role.site_access_role
        else:
            role_name = None
        return role_name

    def query_device_by_id(self, device_id: int):
        if self.user.user_superadmin:
            device = TeraDevice.get_device_by_id(device_id)
        else:
            sites_ids = self.get_accessible_sites_ids()
            device = TeraDevice.query.filter_by(id_device=device_id).filter(TeraDevice.id_site.in_(sites_ids)).first()
        return device

    def query_devices_for_site(self, site_id: int):
        devices = []
        if site_id in self.get_accessible_sites_ids():
            site_devices = TeraDeviceSite.query_devices_for_site(site_id)
            for site_device in site_devices:
                devices.append(site_device.device_site_device)
        return devices

    def query_devices_by_type(self, type_device: int):
        devices = TeraDevice.query.filter_by(device_type=type_device).order_by(TeraDevice.id_device.asc()).all()
        return devices

    def query_devices_by_type_by_site(self, type_device: int, site_id: int):
        devices = []
        if site_id in self.get_accessible_sites_ids():
            devices = TeraDevice.query.join(TeraDeviceSite)\
                .filter(TeraDeviceSite.id_site == site_id, TeraDevice.device_type == type_device)\
                .order_by(TeraDevice.id_device.asc()).all()
        return devices

    def query_sites_for_device(self, device_id: int):
        sites = []
        if device_id in self.get_accessible_devices_ids():
            site_devices = TeraDeviceSite.query_sites_for_device(device_id)
            for site_device in site_devices:
                sites.append(site_device.device_site_site)
        return sites

    def query_session_type_by_id(self, session_type_id: int):
        proj_ids = self.get_accessible_projects_ids()
        session_type = TeraSessionType.query.filter_by(id_session_type=session_type_id).filter(TeraProject.id_project.
                                                                                               in_(proj_ids)).first()
        return session_type

    def query_projects_for_site(self, site_id: int):
        proj_ids = self.get_accessible_projects_ids()
        projects = TeraProject.query.filter_by(id_site=site_id).filter(TeraProject.id_project.in_(proj_ids)).all()
        return projects

    def query_projects_for_session_type(self, session_type_id: int):
        from libtera.db.models.TeraSessionTypeProject import TeraSessionTypeProject
        proj_ids = self.get_accessible_projects_ids()
        projects = TeraProject.query.join(TeraSessionTypeProject.session_type_project_project).filter(
            TeraSessionTypeProject.id_session_type == session_type_id).filter(TeraProject.id_project.in_(proj_ids))\
            .all()
        return projects

    def query_participants_for_site(self, site_id: int):
        part_ids = self.get_accessible_participants_ids()
        participants = TeraParticipant.query.join(TeraParticipantGroup, TeraProject)\
            .filter(TeraProject.id_site == site_id, TeraParticipant.id_participant.in_(part_ids))\
            .order_by(TeraParticipant.id_participant.asc()).all()
        return participants

    def query_participants_for_project(self, project_id: int):
        part_ids = self.get_accessible_participants_ids()
        participants = TeraParticipant.query.join(TeraParticipantGroup)\
            .filter(TeraParticipantGroup.id_project == project_id, TeraParticipant.id_participant.in_(part_ids))\
            .order_by(TeraParticipant.id_participant.asc()).all()
        return participants

    def query_participants_for_group(self, group_id: int):
        part_ids = self.get_accessible_participants_ids()
        participants = TeraParticipant.query.filter(TeraParticipant.id_participant_group == group_id,
                                                    TeraParticipant.id_participant.in_(part_ids))\
            .order_by(TeraParticipant.id_participant.asc()).all()
        return participants

    def query_access_for_site(self, site_id: int, admin_only=False):
        users = self.get_accessible_users()
        users_ids = []
        super_admins = []
        for user in users:
            if user.id_user not in users_ids:
                users_ids.append(user.id_user)
            if user.user_superadmin:
                # Super admin access = admin in all site
                super_admin = TeraSiteAccess.build_superadmin_access_object(site_id=site_id, user_id=user.id_user)
                super_admins.append(super_admin)

        if not admin_only:
            access = TeraSiteAccess.query.filter_by(id_site=site_id).filter(TeraSiteAccess.id_user.in_(users_ids)).all()
        else:
            access = TeraSiteAccess.query.filter_by(id_site=site_id, site_access_role='admin')\
                .filter(TeraSiteAccess.id_user.in_(users_ids)).all()

        # Add super admins to list, if needed
        for super_access in super_admins:
            if not any(x.id_user == super_access.id_user for x in access):
                access.append(super_access)

        return access

    def query_access_for_project(self, project_id: int, admin_only=False):
        users = self.get_accessible_users()
        users_ids = []
        super_admins = []

        proj = TeraProject.get_project_by_id(project_id)
        site_id = proj.id_site

        for user in users:
            if user.id_user not in users_ids:
                users_ids.append(user.id_user)
            user_access = DBManagerTeraUserAccess(user=user)
            if user.user_superadmin or user_access.get_site_role(site_id=site_id) == 'admin':
                # Super admin access or site admin = admin in this site
                super_admin = TeraProjectAccess.build_superadmin_access_object(project_id=project_id,
                                                                               user_id=user.id_user)
                super_admins.append(super_admin)

        if not admin_only:
            access = TeraProjectAccess.query.filter_by(id_project=project_id)\
                .filter(TeraProjectAccess.id_user.in_(users_ids)).all()
        else:
            access = TeraProjectAccess.query.filter_by(id_project=project_id, project_access_role='admin') \
                .filter(TeraProjectAccess.id_user.in_(users_ids)).all()

        # Add super admins to list, if needed
        for super_access in super_admins:
            if not any(x.id_user == super_access.id_user for x in access):
                access.append(super_access)

        return access

    def query_site_access_for_user(self, user_id: int, admin_only=False):
        from libtera.db.models.TeraUser import TeraUser
        user = TeraUser.get_user_by_id(user_id)
        if not user.user_superadmin:
            if not admin_only:
                access = TeraSiteAccess.query.filter_by(id_user=user_id).all()
            else:
                access = TeraSiteAccess.query.filter_by(id_user=user_id, site_access_role='admin').all()
        else:
            # User is super admin, set roles to admin for all accessible sites
            sites = self.get_accessible_sites()
            access = []
            for site in sites:
                access.append(TeraSiteAccess.build_superadmin_access_object(site_id=site.id_site, user_id=user_id))

        return access

    def query_project_access_for_user(self, user_id: int, admin_only=False):
        from libtera.db.models.TeraUser import TeraUser
        user = TeraUser.get_user_by_id(user_id)
        if not user.user_superadmin:
            if not admin_only:
                access = TeraProjectAccess.query.filter_by(id_user=user_id).all()
            else:
                access = TeraProjectAccess.query.filter_by(id_user=user_id, project_access_role='admin').all()
        else:
            # User is super admin, set roles to admin for all accessible projects
            projects = self.get_accessible_projects()
            access = []
            for project in projects:
                access.append(TeraProjectAccess.build_superadmin_access_object(project_id=project.id_project,
                                                                               user_id=user_id))

        return access

    # def query_participants_for_kit(self, kit_id: int):
    #     from libtera.db.models.TeraParticipant import TeraParticipant
    #
    #     parts = TeraParticipant.query.join(TeraParticipant.participant_kits).filter_by(id_kit=kit_id)\
    #         .filter(TeraKit.id_kit.in_(self.get_accessible_kits_ids()),
    #                 TeraParticipant.id_participant.in_(self.get_accessible_participants_ids())).all()
    #     return parts

    def query_participants_for_device(self, device_id: int):
        from libtera.db.models.TeraParticipant import TeraParticipant
        parts = TeraParticipant.query.join(TeraParticipant.participant_devices).filter_by(id_device=device_id)\
            .filter(TeraDevice.id_device.in_(self.get_accessible_devices_ids()),
                    TeraParticipant.id_participant.in_(self.get_accessible_participants_ids())).all()
        return parts

    def query_device_participants_for_site(self, site_id: int):
        device_parts = []
        if site_id in self.get_accessible_sites_ids():
            device_sites = TeraDeviceSite.query.filter_by(id_site=site_id).all()
            device_ids = list()
            for device_site in device_sites:
                if device_site.device_site_device.id_device not in device_ids:
                    device_ids.append(device_site.device_site_device.id_device)
            device_parts = TeraDeviceParticipant.query.join(TeraDeviceParticipant.device_participant_device)\
                .filter(TeraDevice.id_device.in_(device_ids)).all()
        return device_parts

    def query_session(self, session_id: int):
        from libtera.db.models.TeraParticipant import TeraParticipant
        from libtera.db.models.TeraSession import TeraSession

        session = TeraSession.query.join(TeraSession.session_participants).filter(TeraSession.id_session == session_id)\
            .filter(TeraParticipant.id_participant.in_(self.get_accessible_participants_ids())).first()

        return session

    def query_session_events(self, session_id: int):
        from libtera.db.models.TeraSessionEvent import TeraSessionEvent

        if self.query_session(session_id=session_id):
            return TeraSessionEvent.get_events_for_session(id_session=session_id)

        return []

    def query_session_types_for_device(self, device_type_id: int):
        from libtera.db.models.TeraSessionTypeDeviceType import TeraSessionTypeDeviceType
        session_types_ids = self.get_accessible_session_types_ids()

        session_types = TeraSessionTypeDeviceType.query.filter(TeraSessionTypeDeviceType.id_session_type.
                                                               in_(session_types_ids))\
            .filter_by(id_device_type=device_type_id).all()
        return session_types

    def query_session_types_for_project(self, project_id: int):
        from libtera.db.models.TeraSessionTypeProject import TeraSessionTypeProject
        session_types_ids = self.get_accessible_session_types_ids()

        session_types = TeraSessionTypeProject.query.filter(TeraSessionTypeProject.id_session_type.
                                                            in_(session_types_ids))\
            .filter_by(id_project=project_id).all()
        return session_types
