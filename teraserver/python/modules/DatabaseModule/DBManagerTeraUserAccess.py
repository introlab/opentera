
from libtera.db.models.TeraUser import TeraUser
from libtera.db.models.TeraUserGroup import TeraUserGroup
from libtera.db.models.TeraSite import TeraSite
from libtera.db.models.TeraProject import TeraProject
from libtera.db.models.TeraParticipant import TeraParticipant
from libtera.db.models.TeraParticipantGroup import TeraParticipantGroup
from libtera.db.models.TeraDeviceType import TeraDeviceType
from libtera.db.models.TeraDeviceSubType import TeraDeviceSubType
from libtera.db.models.TeraSessionType import TeraSessionType
from libtera.db.models.TeraDevice import TeraDevice
from libtera.db.models.TeraDeviceProject import TeraDeviceProject
from libtera.db.models.TeraSession import TeraSession
from libtera.db.models.TeraDeviceParticipant import TeraDeviceParticipant
from libtera.db.models.TeraUserUserGroup import TeraUserUserGroup

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
                users.append(self.user)

        # TODO Sort by username
        return users

    def get_accessible_users_groups_ids(self, admin_only=False):
        users_groups = self.get_accessible_users_groups(admin_only=admin_only)
        users_groups_ids = [ug.id_user_group for ug in users_groups]
        return users_groups_ids

    def get_accessible_users_groups(self, admin_only=False):
        users_groups = []
        all_users_groups = TeraUserGroup.query.order_by(TeraUserGroup.user_group_name.asc()).all()
        if self.user.user_superadmin:
            users_groups = all_users_groups
        else:
            # Gets user group that have access to projects we have access. We only consider projects because of the
            # hierarchy between sites and projects
            projects_access = self.user.get_projects_roles()

            if admin_only:
                # Remove not admin roles
                projects_access = {key: value for key, value in projects_access.items()
                                   if value['project_role'] == 'admin'}

            for user_group in all_users_groups:
                group_project_access = user_group.get_projects_roles()
                if set(group_project_access).intersection(projects_access):
                    # We have a project both in the user accessible list and in the user_group access list
                    users_groups.append(user_group)

        return users_groups

    def get_accessible_users_uuids(self, admin_only=False):
        users = self.get_accessible_users(admin_only=admin_only)
        users_ids = []
        for user in users:
            if user.id_user not in users_ids:
                users_ids.append(user.user_uuid)
        return users_ids

    def get_project_role(self, project_id: int):
        projects_roles = self.user.get_projects_roles()
        role = [role for project, role in projects_roles.items() if project.id_project == project_id]
        if len(role) == 1:
            return role[0]['project_role']
        return None

    def get_accessible_projects(self, admin_only=False):
        project_list = []
        if self.user.user_superadmin:
            # Is superadmin - admin on all projects
            project_list = TeraProject.query.all()
        else:
            # Build project list
            project_roles = self.user.get_projects_roles()
            for project in project_roles:
                if not admin_only or (admin_only and project_roles[project] == 'admin'):
                    project_list.append(project)

        return project_list

    def get_accessible_projects_ids(self, admin_only=False):
        projects = []

        for project in self.get_accessible_projects(admin_only=admin_only):
            projects.append(project.id_project)

        return projects

    def get_accessible_devices(self, admin_only=False):
        if self.user.user_superadmin:
            return TeraDevice.query.all()

        proj_id_list = self.get_accessible_projects_ids(admin_only=admin_only)
        query = TeraDevice.query.join(TeraDeviceProject).filter(TeraDeviceProject.id_project.in_(proj_id_list))
        return query.all()

    def get_accessible_devices_uuids(self, admin_only=False):
        devices = []

        for device in self.get_accessible_devices(admin_only=admin_only):
            devices.append(device.device_uuid)
        return devices

    def get_accessible_devices_ids(self, admin_only=False):
        devices = []

        for device in self.get_accessible_devices(admin_only=admin_only):
            devices.append(device.id_device)

        return devices

    def get_accessible_devices_types(self, admin_only=False):
        if self.user.user_superadmin:
            return TeraDeviceType.query.all()

        from libtera.db.models.TeraSessionTypeDeviceType import TeraSessionTypeDeviceType
        session_types_id_list = self.get_accessible_session_types_ids(admin_only=admin_only)
        return TeraDeviceType.query.join(TeraSessionTypeDeviceType).join(TeraSessionType).\
            filter(TeraSessionType.id_session_type.in_(session_types_id_list)).all()

    def get_accessible_devices_types_ids(self, admin_only=False):
        device_types = []
        accessible_dts = self.get_accessible_devices_types(admin_only=admin_only)
        for dt in accessible_dts:
            device_types.append(dt.id_device_type)
        return device_types

    def get_accessible_devices_subtypes(self, admin_only=False):
        device_subtypes = []
        accessible_dts = self.get_accessible_devices_types(admin_only=admin_only)
        for dt in accessible_dts:
            subtypes = TeraDeviceSubType.get_device_subtypes_for_type(dt.id_device_type)
            device_subtypes.extend(subtypes)

        return device_subtypes

    def get_accessible_participants(self, admin_only=False):
        project_id_list = self.get_accessible_projects_ids(admin_only=admin_only)
        # groups = TeraParticipantGroup.query.filter(TeraParticipantGroup.id_project.in_(project_id_list)).all()
        participant_list = []
        # for group in groups:
        #     participant_list.extend(TeraParticipant.query.
        #                             filter_by(id_participant_group=group.id_participant_group).all())
        participant_list.extend(TeraParticipant.query.filter(TeraParticipant.id_project.in_(project_id_list)))

        return participant_list

    def get_accessible_participants_uuids(self, admin_only=False):
        participants = self.get_accessible_participants(admin_only)
        uuids = []
        for participant in participants:
            uuids.append(participant.participant_uuid)
        return uuids

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

    def get_accessible_sites(self, admin_only=False):
        if self.user.user_superadmin:
            site_list = TeraSite.query.order_by(TeraSite.site_name.asc()).all()
        else:
            site_list = []
            site_roles = self.user.get_sites_roles()
            for site in site_roles:
                if not admin_only or (admin_only and site_roles[site] == 'admin'):
                    site_list.append(site)

            # for site_access in self.user.user_user_group.user_group_sites_access:
            #     if not admin_only or (admin_only and site_access.site_access_role == 'admin'):
            #         site_list.append(site_access.site_access_site)
            # # Also get sites from which we don't have a specific role, but that we have at least a project access into
            # # it
            # for project_access in self.user.user_user_group.user_group_projects_access:
            #     if project_access.project_access_project.project_site not in site_list:
            #         site_list.append(project_access.project_access_project.project_site)

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
        return TeraSessionType.query.join(TeraSessionTypeProject)\
            .filter(TeraSessionTypeProject.id_project.in_(project_id_list)).all()

    def get_accessible_session_types_ids(self, admin_only=False):
        st_ids = []

        for st in self.get_accessible_session_types(admin_only=admin_only):
            st_ids.append(st.id_session_type)

        return st_ids

    def get_accessible_sessions(self, admin_only=False):
        from libtera.db.models.TeraSession import TeraSession
        part_ids = self.get_accessible_participants_ids(admin_only=admin_only)
        return TeraSession.query.join(TeraSession.session_participants).\
            filter(TeraParticipant.id_participant.in_(part_ids)).all()

    def get_accessible_sessions_ids(self, admin_only=False):
        ses_ids = []

        for ses in self.get_accessible_sessions(admin_only=admin_only):
            ses_ids.append(ses.id_session)

        return ses_ids

    def get_accessible_services(self, admin_only=False):
        from libtera.db.models.TeraService import TeraService
        from libtera.db.models.TeraServiceProjectRole import TeraServiceProjectRole
        from libtera.db.models.TeraServiceRole import TeraServiceRole

        if self.user.user_superadmin:
            return TeraService.query.all()

        accessible_projects_ids = self.get_accessible_projects_ids()
        query = TeraService.query.join(TeraServiceProjectRole).filter(
            TeraServiceProjectRole.id_project.in_(accessible_projects_ids)).group_by(TeraService.id_service)

        if admin_only:
            query = query.join(TeraServiceRole).filter(TeraServiceRole.service_role_name == 'admin')

        return query.all()

    def get_accessible_services_ids(self, admin_only=False):
        services_ids = []

        for service in self.get_accessible_services(admin_only=admin_only):
            services_ids.append(service.id_service)

        return services_ids

    def get_site_role(self, site_id: int):
        sites_roles = self.user.get_sites_roles()
        role = [role for site, role in sites_roles.items() if site.id_site == site_id]
        if len(role) == 1:
            return role[0]['site_role']
        return None
        # role_name = None
        # site_roles = self.user.get_sites_roles()
        # for site in site_roles:
        #     if site.id_site == site_id:
        #         role_name = site_roles[site]
        #         break
        # return role_name

        # if self.user.user_superadmin:
        #     # SuperAdmin is always admin.
        #     return 'admin'
        #
        # role = TeraSiteAccess.query.filter_by(id_user_group=self.user.id_user_group, id_site=site_id).first()
        # if role is not None:
        #     role_name = role.site_access_role
        # else:
        #     # By default, if we have an access to any project in that site, we are a "user" of that site
        #     role_name = None
        #     project_access = TeraProjectAccess.get_projects_access_for_user_group(self.user.id_user_group)
        #     for pa in project_access:
        #         if pa.project_access_project.id_site == site_id:
        #             role_name = 'user'
        #             break
        #
        # return role_name

    def query_device_by_id(self, device_id: int):
        if self.user.user_superadmin:
            device = TeraDevice.get_device_by_id(device_id)
        else:
            sites_ids = self.get_accessible_sites_ids()
            device = TeraDevice.query.filter_by(id_device=device_id).filter(TeraDevice.id_site.in_(sites_ids)).first()
        return device

    def query_devices_for_site(self, site_id: int, device_type_id: int):
        devices = []
        if site_id in self.get_accessible_sites_ids():
            query = TeraDevice.query.join(TeraDeviceProject).join(TeraProject) \
                .filter(TeraProject.id_site == site_id) \
                .order_by(TeraDevice.id_device.asc())
            if device_type_id:
                query = query.filter(TeraDevice.device_type == device_type_id)
            devices = query.all()
        return devices

    def query_devices_for_project(self, project_id: int, device_type_id: int):
        devices = []
        if project_id in self.get_accessible_projects_ids():
            query = TeraDevice.query.join(TeraDeviceProject).filter_by(id_project=project_id)\
                .order_by(TeraDevice.id_device.asc())
            if device_type_id:
                query = query.filter(TeraDevice.device_type == device_type_id)
            devices = query.all()
        return devices

    def query_devices_by_type(self, id_type_device: int):
        accessibles_devices = self.get_accessible_devices_ids()
        devices = TeraDevice.query.filter_by(device_type=id_type_device).filter(TeraDevice
                                                                                .id_device.in_(accessibles_devices))\
            .order_by(TeraDevice.device_name.asc()).all()
        return devices

    def query_devices_by_subtype(self, id_device_subtype: int):
        accessibles_devices = self.get_accessible_devices_ids()
        devices = TeraDevice.query.filter_by(id_device_subtype=id_device_subtype).filter(
            TeraDevice.id_device.in_(accessibles_devices)).order_by(TeraDevice.device_name.asc()).all()
        return devices

    def query_sites_for_device(self, device_id: int):
        sites = []
        if device_id in self.get_accessible_devices_ids():
            site_devices = TeraDeviceProject.query_sites_for_device(device_id)
            for site_device in site_devices:
                sites.append(site_device.device_project_project.project_site)
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
        participants = TeraParticipant.query.join(TeraProject)\
            .filter(TeraProject.id_site == site_id, TeraParticipant.id_participant.in_(part_ids))\
            .order_by(TeraParticipant.id_participant.asc()).all()
        return participants

    def query_participants_for_project(self, project_id: int):
        part_ids = self.get_accessible_participants_ids()
        participants = TeraParticipant.query.filter(TeraParticipant.id_project == project_id,
                                                    TeraParticipant.id_participant.in_(part_ids))\
            .order_by(TeraParticipant.id_participant.asc()).all()
        return participants

    def query_participants_for_group(self, group_id: int):
        part_ids = self.get_accessible_participants_ids()
        participants = TeraParticipant.query.filter(TeraParticipant.id_participant_group == group_id,
                                                    TeraParticipant.id_participant.in_(part_ids))\
            .order_by(TeraParticipant.id_participant.asc()).all()
        return participants

    # def query_users_access_for_site(self, site_id: int, admin_only=False):
    #     users = self.get_accessible_users()
    #     users_access = []
    #     for user in users:
    #         if user.user_superadmin:
    #             # Super admin access = admin in all site
    #             access = TeraSiteAccess.build_superadmin_access_object(site_id=site_id,
    #                                                                    user_group_id=user.id_user_group)
    #         else:
    #             access = TeraSiteAccess.get_specific_site_access(id_user_group=user.id_user_group, id_site=site_id)
    #         if not admin_only or (admin_only and access.site_access_role == 'admin'):
    #             users_access.append(access)
    #     return users_access

    def query_access_for_site(self, site_id: int, admin_only=False, include_empty_groups=False):
        all_users_groups = self.get_accessible_users_groups(admin_only=admin_only)
        users_groups = {}
        for user_group in all_users_groups:
            if not admin_only:
                sites = {key.id_site: value for key, value in user_group.get_sites_roles().items()
                         if key.id_site == site_id}
            else:
                sites = {key.id_site: value for key, value in user_group.get_sites_roles().items()
                         if key.id_site == site_id and value['site_role'] == 'admin'}
            if site_id in sites:
                users_groups[user_group] = sites[site_id]
            elif include_empty_groups:
                users_groups[user_group] = None
        return users_groups

    def query_access_for_project(self, project_id: int, admin_only=False, include_empty_groups=False):
        all_users_groups = self.get_accessible_users_groups(admin_only=admin_only)
        users_groups = {}
        for user_group in all_users_groups:
            if not admin_only:
                projects = {key.id_project: value for key, value in user_group.get_projects_roles().items()
                            if key.id_project == project_id}
            else:
                projects = {key.id_project: value for key, value in user_group.get_projects_roles().items()
                            if key.id_project == project_id and value['project_role'] == 'admin'}
            if project_id in projects:
                users_groups[user_group] = projects[project_id]
            elif include_empty_groups:
                users_groups[user_group] = None
        return users_groups

    def query_site_access_for_user(self, user_id: int, admin_only=False):
        from libtera.db.models.TeraUser import TeraUser
        user = TeraUser.get_user_by_id(user_id)
        site_roles = user.get_sites_roles()

        if admin_only:
            # Remove not admin roles
            site_roles = {key: value for key, value in site_roles.items() if value['site_role'] == 'admin'}

        return site_roles

    def query_project_access_for_user(self, user_id: int, admin_only=False):
        from libtera.db.models.TeraUser import TeraUser
        user = TeraUser.get_user_by_id(user_id)
        project_roles = user.get_projects_roles()

        if admin_only:
            # Remove not admin roles
            project_roles = {key: value for key, value in project_roles.items() if value['project_role'] == 'admin'}

        return project_roles

    def query_participants_for_device(self, device_id: int):
        from libtera.db.models.TeraParticipant import TeraParticipant
        parts = TeraParticipant.query.join(TeraParticipant.participant_devices).filter_by(id_device=device_id)\
            .filter(TeraDevice.id_device.in_(self.get_accessible_devices_ids()),
                    TeraParticipant.id_participant.in_(self.get_accessible_participants_ids())).all()
        return parts

    def query_device_participants_for_site(self, site_id: int):
        device_parts = []
        if site_id in self.get_accessible_sites_ids():
            device_sites = TeraDeviceProject.query_devices_for_site(site_id=site_id)
            device_ids = list()
            for device_site in device_sites:
                if device_site.device_project_device.id_device not in device_ids:
                    device_ids.append(device_site.device_project_device.id_device)
                device_parts = TeraDeviceParticipant.query.join(TeraDeviceParticipant.device_participant_device)\
                    .join(TeraParticipant).join(TeraParticipant.participant_project).join(TeraProject.project_site)\
                    .filter_by(id_site=site_id).filter(TeraDevice.id_device.in_(device_ids)).all()
        return device_parts

    def query_device_participants_by_type(self, id_device_type: int, participant_id: int):
        device_parts = TeraDeviceParticipant.query.join(TeraDevice)\
            .filter(TeraDevice.device_type == id_device_type, TeraDeviceParticipant.id_participant == participant_id)\
            .order_by(TeraDeviceParticipant.id_device_participant.asc()).all()
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

    def query_assets_for_service(self, uuid_service: str):
        from libtera.db.models.TeraAsset import TeraAsset
        from sqlalchemy import or_

        session_ids = self.get_accessible_sessions_ids()
        device_ids = self.get_accessible_devices_ids()
        return TeraAsset.query.filter(TeraAsset.id_session.in_(session_ids))\
            .filter(or_(TeraAsset.id_device.in_(device_ids), TeraAsset.id_device == None))\
            .filter(TeraAsset.asset_service_uuid == uuid_service).all()

    def query_projects_for_service(self, service_id: int):
        from libtera.db.models.TeraServiceProject import TeraServiceProject
        projects_ids = self.get_accessible_projects_ids()

        projects = TeraServiceProject.query.filter(TeraServiceProject.id_project.in_(projects_ids)) \
            .filter_by(id_service=service_id).all()
        return projects

    def query_services_for_project(self, project_id: int):
        from libtera.db.models.TeraServiceProject import TeraServiceProject
        services_ids = self.get_accessible_services_ids()

        services = TeraServiceProject.query.filter(TeraServiceProject.id_service.in_(services_ids)) \
            .filter_by(id_project=project_id).all()
        return services

    def query_users_for_usergroup(self, user_group_id: int):
        accessible_users_ids = self.get_accessible_users_ids()
        return TeraUserUserGroup.query.filter_by(id_user_group=user_group_id).filter(TeraUserUserGroup.id_user
                                                                                     .in_(accessible_users_ids)).all()
