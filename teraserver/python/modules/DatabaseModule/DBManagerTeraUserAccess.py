from sqlalchemy import true
from sqlalchemy import or_, and_, not_

from opentera.db.models.TeraUser import TeraUser
from opentera.db.models.TeraUserGroup import TeraUserGroup
from opentera.db.models.TeraSite import TeraSite
from opentera.db.models.TeraProject import TeraProject
from opentera.db.models.TeraParticipant import TeraParticipant
from opentera.db.models.TeraParticipantGroup import TeraParticipantGroup
from opentera.db.models.TeraDeviceType import TeraDeviceType
from opentera.db.models.TeraDeviceSubType import TeraDeviceSubType
from opentera.db.models.TeraSessionType import TeraSessionType
from opentera.db.models.TeraDevice import TeraDevice
from opentera.db.models.TeraDeviceProject import TeraDeviceProject
from opentera.db.models.TeraDeviceSite import TeraDeviceSite
from opentera.db.models.TeraDeviceParticipant import TeraDeviceParticipant
from opentera.db.models.TeraUserUserGroup import TeraUserUserGroup
from opentera.db.models.TeraSessionTypeSite import TeraSessionTypeSite
from opentera.db.models.TeraTestType import TeraTestType
from opentera.db.models.TeraTestTypeSite import TeraTestTypeSite
from opentera.db.models.TeraTestTypeProject import TeraTestTypeProject
from opentera.db.models.TeraSession import TeraSession
from opentera.db.models.TeraSessionUsers import TeraSessionUsers
from opentera.db.models.TeraSessionParticipants import TeraSessionParticipants
from opentera.db.models.TeraSessionDevices import TeraSessionDevices
from opentera.db.models.TeraService import TeraService
from opentera.db.models.TeraServiceRole import TeraServiceRole
from opentera.db.models.TeraServiceProject import TeraServiceProject
from opentera.db.models.TeraServiceSite import TeraServiceSite
from opentera.db.models.TeraAsset import TeraAsset
from opentera.db.models.TeraSessionTypeProject import TeraSessionTypeProject
from opentera.db.models.TeraSessionTypeServices import TeraSessionTypeServices
from opentera.db.models.TeraSessionEvent import TeraSessionEvent
from opentera.db.models.TeraServiceConfig import TeraServiceConfig
from opentera.db.models.TeraServiceAccess import TeraServiceAccess
from opentera.db.models.TeraTest import TeraTest
from opentera.db.models.TeraTestInvitation import TeraTestInvitation

import modules.Globals as Globals

class DBManagerTeraUserAccess:
    def __init__(self, user: TeraUser):
        self.user = user

    def get_accessible_users_ids(self, admin_only=False, include_site_access=False) -> list[int]:
        users = self.get_accessible_users(admin_only=admin_only, include_site_access=include_site_access)
        users_ids = []
        for user in users:
            if user.id_user not in users_ids:
                users_ids.append(user.id_user)
        return users_ids

    def get_accessible_users(self, admin_only=False, include_site_access=False) -> list[TeraUser]:
        if self.user.user_superadmin:
            users = TeraUser.query.order_by(TeraUser.user_firstname.asc()).all()
        else:
            projects = self.get_accessible_projects(admin_only=admin_only)
            users = []
            for project in projects:
                project_users = project.get_users_in_project(include_site_access=include_site_access)
                for user in project_users:
                    if user not in users:
                        users.append(user)
            # You are always available to yourself!
            if self.user not in users:
                users.append(self.user)

        # Sort by user first name
        return sorted(users, key=lambda suser: suser.user_firstname)

    def get_accessible_users_groups_ids(self, admin_only=False, by_sites=False) -> list[int]:
        users_groups = self.get_accessible_users_groups(admin_only=admin_only, by_sites=by_sites)
        users_groups_ids = [ug.id_user_group for ug in users_groups]
        return users_groups_ids

    def get_accessible_users_groups(self, admin_only=False, by_sites=False) -> list[TeraUserGroup]:
        users_groups = []
        all_users_groups = TeraUserGroup.query.order_by(TeraUserGroup.user_group_name.asc()).all()
        if self.user.user_superadmin:
            users_groups = all_users_groups
        else:
            if not by_sites:
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
            else:
                # Check access by sites instead of projects
                sites_access = self.user.get_sites_roles()

                if admin_only:
                    # Remove not admin roles
                    sites_access = {key: value for key, value in sites_access.items() if value['site_role'] == 'admin'}

                for user_group in all_users_groups:
                    group_site_access = user_group.get_sites_roles()
                    if set(group_site_access).intersection(sites_access):
                        # We have a project both in the user accessible list and in the user_group access list
                        users_groups.append(user_group)

        return users_groups

    def get_accessible_users_uuids(self, admin_only=False) -> list[str]:
        users = self.get_accessible_users(admin_only=admin_only)
        users_ids = []
        for user in users:
            if user.id_user not in users_ids:
                users_ids.append(user.user_uuid)
        return users_ids

    def get_project_role(self, project_id: int) -> str:
        projects_roles = self.user.get_projects_roles()
        role = [role for project, role in projects_roles.items() if project.id_project == int(project_id)]
        if len(role) == 1:
            return role[0]['project_role']
        return None

    def get_user_project_role(self, user_id: int, project_id: int) -> str:
        if user_id not in self.get_accessible_users_ids():
            return None
        user = TeraUser.get_user_by_id(id_user=user_id)
        role = [role for project, role in user.get_projects_roles().items() if project.id_project == int(project_id)]
        if len(role) == 1:
            return role[0]
        return None

    def get_accessible_projects(self, admin_only=False) -> list[TeraProject]:
        project_list = []
        if self.user.user_superadmin:
            # Is superadmin - admin on all projects
            project_list = TeraProject.query.all()
        else:
            # Build project list
            project_roles = self.user.get_projects_roles()
            for project in project_roles:
                if not admin_only or (admin_only and project_roles[project]['project_role'] == 'admin'):
                    project_list.append(project)

        return project_list

    def get_accessible_projects_ids(self, admin_only=False) -> list[int]:
        projects = []

        for project in self.get_accessible_projects(admin_only=admin_only):
            projects.append(project.id_project)

        return projects

    def get_accessible_devices(self, admin_only=False) -> list[TeraDevice]:
        if self.user.user_superadmin:
            return TeraDevice.query.all()

        # proj_id_list = self.get_accessible_projects_ids(admin_only=admin_only)
        # query = TeraDevice.query.join(TeraDeviceProject).filter(TeraDeviceProject.id_project.in_(proj_id_list))
        site_id_list = self.get_accessible_sites_ids(admin_only=admin_only)
        query = TeraDevice.query.join(TeraDeviceSite).filter(TeraDeviceSite.id_site.in_(site_id_list))
        return query.all()

    def get_accessible_devices_uuids(self, admin_only=False) -> list[str]:
        devices = []

        for device in self.get_accessible_devices(admin_only=admin_only):
            devices.append(device.device_uuid)
        return devices

    def get_accessible_devices_ids(self, admin_only=False) -> list[int]:
        devices = []

        for device in self.get_accessible_devices(admin_only=admin_only):
            devices.append(device.id_device)

        return devices

    def get_accessible_devices_types(self, admin_only=False) -> list[TeraDeviceType]:
        # if self.user.user_superadmin:
        #     return TeraDeviceType.query.all()
        return TeraDeviceType.get_devices_types()

        # from opentera.db.models.TeraSessionTypeDeviceType import TeraSessionTypeDeviceType
        # session_types_id_list = self.get_accessible_session_types_ids(admin_only=admin_only)
        # return TeraDeviceType.query.join(TeraSessionTypeDeviceType).join(TeraSessionType).\
        #     filter(TeraSessionType.id_session_type.in_(session_types_id_list)).all()

    def get_accessible_devices_types_ids(self, admin_only=False) -> list[int]:
        device_types = []
        accessible_dts = self.get_accessible_devices_types(admin_only=admin_only)
        for dt in accessible_dts:
            device_types.append(dt.id_device_type)
        return device_types

    def get_accessible_devices_types_names(self, admin_only=False) -> list[str]:
        device_types = []
        accessible_dts = self.get_accessible_devices_types(admin_only=admin_only)
        for dt in accessible_dts:
            device_types.append(dt.device_type_name)
        return device_types

    def get_accessible_devices_types_keys(self, admin_only=False) -> list[str]:
        device_types = []
        accessible_dts = self.get_accessible_devices_types(admin_only=admin_only)
        for dt in accessible_dts:
            device_types.append(dt.device_type_key)
        return device_types

    def get_accessible_devices_subtypes(self, admin_only=False) -> list[TeraDeviceSubType]:
        device_subtypes = []
        accessible_dts = self.get_accessible_devices_types(admin_only=admin_only)
        for dt in accessible_dts:
            subtypes = TeraDeviceSubType.get_device_subtypes_for_type(dt.id_device_type)
            device_subtypes.extend(subtypes)

        return device_subtypes

    def get_accessible_devices_subtypes_ids(self, admin_only=False) -> list[int]:
        device_subtypes_ids = []
        accessible_dts = self.get_accessible_devices_subtypes(admin_only=admin_only)
        for dt in accessible_dts:
            device_subtypes_ids.append(dt.id_device_subtype)
        return device_subtypes_ids

    def get_accessible_participants(self, admin_only=False) -> list[TeraParticipant]:
        project_id_list = self.get_accessible_projects_ids(admin_only=admin_only)
        # groups = TeraParticipantGroup.query.filter(TeraParticipantGroup.id_project.in_(project_id_list)).all()
        participant_list = []
        # for group in groups:
        #     participant_list.extend(TeraParticipant.query.
        #                             filter_by(id_participant_group=group.id_participant_group).all())
        participant_list.extend(TeraParticipant.query.filter(TeraParticipant.id_project.in_(project_id_list)))

        return participant_list

    def get_accessible_participants_uuids(self, admin_only=False) -> list[str]:
        participants = self.get_accessible_participants(admin_only)
        uuids = []
        for participant in participants:
            uuids.append(participant.participant_uuid)
        return uuids

    def get_accessible_participants_ids(self, admin_only=False) -> list[int]:
        parts = []

        for part in self.get_accessible_participants(admin_only=admin_only):
            parts.append(part.id_participant)

        return parts

    def get_accessible_groups(self, admin_only=False) -> list[TeraParticipantGroup]:
        project_id_list = self.get_accessible_projects_ids(admin_only=admin_only)
        return TeraParticipantGroup.query.filter(TeraParticipantGroup.id_project.in_(project_id_list)).all()

    def get_accessible_groups_ids(self, admin_only=False) -> list[int]:
        groups = []

        for group in self.get_accessible_groups(admin_only=admin_only):
            groups.append(group.id_participant_group)

        return groups

    def get_accessible_sites(self, admin_only=False) -> list[TeraSite]:
        if self.user.user_superadmin:
            site_list = TeraSite.query.order_by(TeraSite.site_name.asc()).all()
        else:
            site_list = []
            site_roles = self.user.get_sites_roles()
            for site in site_roles:
                if not admin_only or (admin_only and site_roles[site]['site_role'] == 'admin'):
                    site_list.append(site)

        return site_list

    def get_accessible_sites_ids(self, admin_only=False) -> list[int]:
        sites_ids = []

        for site in self.get_accessible_sites(admin_only=admin_only):
            sites_ids.append(site.id_site)

        return sites_ids

    def get_accessible_session_types(self, admin_only=False) -> list[TeraSessionType]:
        # from opentera.db.models.TeraSessionTypeProject import TeraSessionTypeProject
        # if self.user.user_superadmin:
        #     return TeraSessionType.query.all()
        #
        # project_id_list = self.get_accessible_projects_ids(admin_only=admin_only)
        # # return TeraSessionType.query.filter(TeraProject.id_project.in_(project_id_list)).all()
        # return TeraSessionType.query.join(TeraSessionTypeProject) \
        #     .filter(TeraSessionTypeProject.id_project.in_(project_id_list)).all()
        if self.user.user_superadmin:
            return TeraSessionType.query.all()

        site_id_list = self.get_accessible_sites_ids(admin_only=admin_only)
        query = TeraSessionType.query.join(TeraSessionTypeSite)\
            .filter(TeraSessionTypeSite.id_site.in_(site_id_list)).order_by(TeraSessionType.session_type_name.asc())
        return query.all()

    def get_accessible_session_types_ids(self, admin_only=False) -> list[int]:
        st_ids = []

        for st in self.get_accessible_session_types(admin_only=admin_only):
            st_ids.append(st.id_session_type)

        return st_ids

    def get_accessible_tests_types(self, admin_only=False) -> list[TeraTestType]:
        if self.user.user_superadmin:
            return TeraTestType.query.all()

        site_id_list = self.get_accessible_sites_ids(admin_only=admin_only)
        services_ids = self.get_accessible_services_ids()
        query = TeraTestType.query.join(TeraTestTypeSite)\
            .filter(TeraTestTypeSite.id_site.in_(site_id_list)).filter(TeraTestType.id_service.in_(services_ids))
        return query.all()

    def get_accessible_tests_types_ids(self, admin_only=False) -> list[int]:
        tt_ids = []

        for tt in self.get_accessible_tests_types(admin_only=admin_only):
            tt_ids.append(tt.id_test_type)

        return tt_ids

    def get_accessible_sessions(self, admin_only=False) -> list[TeraSession]:

        part_ids = self.get_accessible_participants_ids(admin_only=admin_only)
        user_ids = self.get_accessible_users_ids(admin_only=admin_only)
        # Also includes super admins users in the list ??
        # user_ids.extend([user.id_user for user in TeraUser.get_superadmins() if user.id_user not in user_ids])
        device_ids = self.get_accessible_devices_ids(admin_only=admin_only)
        service_ids = self.get_accessible_services_ids(admin_only=admin_only)
        # # THIS JOIN TAKES A LONG TIME TO PROCESS... IMPROVE!
        # # sessions = TeraSession.query.join(TeraSession.session_participants).join(TeraSession.session_users). \
        # #     filter(or_(TeraSessionParticipants.id_participant.in_(part_ids),
        # #                TeraSessionUsers.id_user == self.user.id_user,
        # #                TeraSession.id_creator_user == self.user.id_user)).all()
        # sessions = TeraSession.query.join(TeraSession.session_participants). \
        #     filter(TeraSessionParticipants.id_participant.in_(part_ids)).all()
        sessions = TeraSession.query.filter(or_(TeraSession.id_creator_user.in_(user_ids),
                                            TeraSession.id_creator_device.in_(device_ids),
                                            TeraSession.id_creator_participant.in_(part_ids),
                                            TeraSession.id_creator_service.in_(service_ids))).all()

        # Also check for sessions which we were part
        sessions_ids = [session.id_session for session in sessions]
        other_sessions = TeraSessionUsers.query.filter_by(id_user=self.user.id_user).\
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
        sessions = self.get_accessible_sessions(admin_only=admin_only)
        ses_ids = [ses.id_session for ses in sessions]

        # for ses in self.get_accessible_sessions(admin_only=admin_only):
        #     ses_ids.append(ses.id_session)

        return ses_ids

    def get_accessible_services(self, admin_only=False) -> list[TeraService]:
        if self.user.user_superadmin:
            return TeraService.query.all()

        # TODO: Check if SQL query is OK
        # Accessible services are those from projects and sites where the user is admin
        accessible_projects_ids = self.get_accessible_projects_ids()
        admin_sites_ids = self.get_accessible_sites_ids(admin_only=True)
        query = TeraService.query.outerjoin(TeraServiceProject).outerjoin(TeraServiceSite).filter(or_(
            TeraServiceProject.id_project.in_(accessible_projects_ids),
            TeraServiceSite.id_site.in_(admin_sites_ids)
        ))

        # if not include_system_services:
        #     query = query.filter(TeraService.service_system == False)

        if admin_only:
            query = query.join(TeraServiceRole).filter(TeraServiceRole.service_role_name == 'admin')

        query = query.group_by(TeraService.id_service)
        return query.all()

    def get_accessible_services_ids(self, admin_only=False) -> list[int]:
        services_ids = []

        for service in self.get_accessible_services(admin_only=admin_only):
            services_ids.append(service.id_service)

        return services_ids

    def get_site_role(self, site_id: int) -> str:
        sites_roles = self.user.get_sites_roles()
        role = [role for site, role in sites_roles.items() if site.id_site == int(site_id)]
        if len(role) == 1:
            return role[0]['site_role']
        return None

    def get_user_site_role(self, user_id: int, site_id: int) -> str:
        if user_id not in self.get_accessible_users_ids():
            return None
        user = TeraUser.get_user_by_id(id_user=user_id)
        role = [role for site, role in user.get_sites_roles().items() if site.id_site == site_id]
        if len(role) == 1:
            return role[0]
        return None

    def query_devices_for_site(self, site_id: int, device_type_id: int, enabled: bool = False) -> list[TeraDevice]:
        devices = []
        if site_id in self.get_accessible_sites_ids():
            query = TeraDevice.query.join(TeraDeviceSite).filter(TeraDeviceSite.id_site == site_id).\
                order_by(TeraDevice.device_name.asc())
        #     query = TeraDevice.query.join(TeraDeviceProject).join(TeraProject) \
        #         .filter(TeraProject.id_site == site_id) \
        #         .order_by(TeraDevice.device_name.asc())
            if device_type_id:
                query = query.filter(TeraDevice.id_device_type == device_type_id)
            if enabled:
                query = query.filter(TeraDevice.device_enabled == enabled)
            devices = query.all()
        return devices

    def query_devices_for_project(self, project_id: int, device_type_id: int = None, enabled: bool = False) -> list[TeraDevice]:
        devices = []
        projects_ids = self.get_accessible_projects_ids()
        if project_id in projects_ids:
            query = TeraDevice.query.join(TeraDeviceProject).filter_by(id_project=project_id) \
                .order_by(TeraDevice.device_name.asc())
            if device_type_id:
                query = query.filter(TeraDevice.id_device_type == device_type_id)
            if enabled is not None:
                query = query.filter(TeraDevice.device_enabled == enabled)
            devices = query.all()

        return devices

    def query_devices_projects_for_project(self, project_id: int, include_other_devices=False) -> list[TeraDeviceProject]:

        devices_ids = self.get_accessible_devices_ids()

        device_projects = TeraDeviceProject.query.filter(TeraDeviceProject.id_device.in_(devices_ids)) \
            .filter_by(id_project=project_id).all()

        if include_other_devices:
            # We must add the missing devices in the list
            project = TeraProject.get_project_by_id(project_id=project_id)
            if not project:
                return []
            other_devices = TeraDeviceSite.get_devices_for_site(site_id=project.id_site)
            other_devices_ids = [device.id_device for device in other_devices]
            missing_devices_ids = set(other_devices_ids).difference([dp.id_device for dp in device_projects])
            for missing_device_id in missing_devices_ids:
                device_project = TeraDeviceProject()
                device_project.id_project = None
                device_project.id_device = missing_device_id
                device_project.device_project_device = TeraDevice.get_device_by_id(missing_device_id)
                device_projects.append(device_project)

        # Sort by device name
        return sorted(device_projects, key=lambda dp: dp.device_project_device.device_name)

    def query_devices_sites_for_site(self, site_id: int, include_other_devices=False) -> list[TeraDeviceSite]:
        device_sites = TeraDeviceSite.get_devices_for_site(site_id=site_id)

        if include_other_devices:
            # We must add the missing devices in the list, even if we don't have access to them
            if self.user.user_superadmin:
                other_devices = TeraDevice.query_with_filters()
            else:
                sites_ids = self.get_accessible_sites_ids()
                other_devices = TeraDevice.query.join(TeraDeviceSite).filter(TeraDeviceSite.id_site.in_(sites_ids)) \
                    .all()
            device_ids = [device.id_device for device in other_devices]
            missing_devices_ids = set(device_ids).difference([ds.id_device for ds in device_sites])
            for missing_device_id in missing_devices_ids:
                device_site = TeraDeviceSite()
                device_site.id_site = None
                device_site.id_device = missing_device_id
                device_site.device_site_device = TeraDevice.get_device_by_id(missing_device_id)
                device_sites.append(device_site)

        # Sort by device name
        return sorted(device_sites, key=lambda ds: ds.device_site_device.device_name)

    def query_devices_sites_for_device(self, device_id: int, include_other_sites=False) -> list[TeraDeviceSite]:
        site_ids = self.get_accessible_sites_ids()

        query = TeraDeviceSite.query.filter(TeraDeviceSite.id_site.in_(site_ids)) \
            .filter_by(id_device=device_id)

        device_sites = query.all()
        if include_other_sites:
            # We must add the missing sites in the list
            missing_sites_ids = set(site_ids).difference([ds.id_site for ds in device_sites])
            for missing_site_id in missing_sites_ids:
                device_site = TeraDeviceSite()
                device_site.id_site = missing_site_id
                device_site.id_device = None
                device_site.device_site_site = TeraSite.get_site_by_id(missing_site_id)
                device_sites.append(device_site)

        # Sort by site name
        return sorted(device_sites, key=lambda ds: ds.device_site_site.site_name)

    def query_devices_projects_for_device(self, device_id: int, site_id: int = None, include_other_projects=False) -> list[TeraDeviceProject]:
        projects_ids = self.get_accessible_projects_ids()

        query = TeraDeviceProject.query.filter(TeraDeviceProject.id_project.in_(projects_ids)) \
            .filter_by(id_device=device_id)

        if site_id:
            query = query.join(TeraProject).filter(TeraProject.id_site == site_id)

        device_projects = query.all()
        if include_other_projects:
            # We must add the missing projects in the list
            missing_projects_ids = set(projects_ids).difference([dp.id_project for dp in device_projects])
            for missing_project_id in missing_projects_ids:
                device_project = TeraDeviceProject()
                device_project.id_project = missing_project_id
                device_project.id_device = None
                device_project.device_project_project = TeraProject.get_project_by_id(missing_project_id)
                device_projects.append(device_project)

        # Sort by project
        return sorted(device_projects, key=lambda dp: dp.device_project_project.project_name)

    def query_devices_by_type(self, id_type_device: int) -> list[TeraDevice]:
        accessibles_devices = self.get_accessible_devices_ids()
        devices = TeraDevice.query.filter_by(id_device_type=id_type_device)\
            .filter(TeraDevice.id_device.in_(accessibles_devices)).order_by(TeraDevice.device_name.asc()).all()
        return devices

    def query_devices_by_subtype(self, id_device_subtype: int) -> list[TeraDevice]:
        accessibles_devices = self.get_accessible_devices_ids()
        devices = TeraDevice.query.filter_by(id_device_subtype=id_device_subtype).filter(
            TeraDevice.id_device.in_(accessibles_devices)).order_by(TeraDevice.device_name.asc()).all()
        return devices

    def query_sites_for_device(self, device_id: int) -> list[TeraSite]:
        sites = []
        if device_id in self.get_accessible_devices_ids():
            site_devices = TeraDeviceSite.get_sites_for_device(device_id)
            for site_device in site_devices:
                sites.append(site_device.device_site_site)
        return sites

    def query_session_type_by_id(self, session_type_id: int) -> TeraSessionType:
        proj_ids = self.get_accessible_projects_ids()
        session_type = TeraSessionType.query.filter_by(id_session_type=session_type_id)\

        if not self.user.user_superadmin:
            # Super admin = get all session types even if not associated to a project
            session_type = session_type.filter(TeraProject.id_project.in_(proj_ids))

        return session_type.first()

    def query_test_type(self, test_type_id: int) -> TeraTestType:
        # site_ids = self.get_accessible_sites_ids()
        # proj_ids = self.get_accessible_projects_ids()
        service_ids = self.get_accessible_services_ids()
        test_type = TeraTestType.query.filter_by(id_test_type=test_type_id)\
            .filter(TeraTestType.id_service.in_(service_ids)).first()
        # .filter(TeraSite.id_site.in_(site_ids))\
        # .filter(TeraTestType.id_service.in_(service_ids)).filter(TeraProject.id_project.in_(proj_ids)).first()
        return test_type

    def query_projects_for_site(self, site_id: int) -> list[TeraProject]:
        proj_ids = self.get_accessible_projects_ids()
        projects = TeraProject.query.filter_by(id_site=site_id).filter(TeraProject.id_project.in_(proj_ids))

        return projects.all()

    def query_projects_for_session_type(self, session_type_id: int, include_other_projects: bool = False) -> list[TeraProject]:
        from opentera.db.models.TeraSessionTypeProject import TeraSessionTypeProject
        proj_ids = self.get_accessible_projects_ids()
        st_projects = TeraSessionTypeProject.query.filter(TeraSessionTypeProject.id_session_type == session_type_id)\
            .filter(TeraSessionTypeProject.id_project.in_(proj_ids)).all()

        if include_other_projects:
            # We must add the missing projects
            missing_proj_ids = set(proj_ids).difference([sp.id_project for sp in st_projects])
            for missing_proj_id in missing_proj_ids:
                st_project = TeraSessionTypeProject()
                st_project.id_project = missing_proj_id
                st_project.id_session_type = None
                st_project.session_type_project_project = TeraProject.get_project_by_id(missing_proj_id)
                st_projects.append(st_project)

        # Sort by project id
        return sorted(st_projects, key=lambda sp: sp.session_type_project_project.project_name)

    def query_projects_for_test_type(self, test_type_id: int, include_other_projects: bool = False) -> list[TeraProject]:
        proj_ids = self.get_accessible_projects_ids()
        tt_projects = TeraTestTypeProject.query.filter(TeraTestTypeProject.id_test_type == test_type_id)\
            .filter(TeraTestTypeProject.id_project.in_(proj_ids)).all()

        if include_other_projects:
            # We must add the missing projects
            missing_proj_ids = set(proj_ids).difference([tp.id_project for tp in tt_projects])
            for missing_proj_id in missing_proj_ids:
                tt_project = TeraTestTypeProject()
                tt_project.id_project = missing_proj_id
                tt_project.id_test_type = None
                tt_project.test_type_project_project = TeraProject.get_project_by_id(missing_proj_id)
                tt_projects.append(tt_project)

        # Sort by project id
        return sorted(tt_projects, key=lambda tp: tp.test_type_project_project.project_name)

    def query_all_participants_for_site(self, site_id: int) -> list[TeraParticipant]:
        part_ids = self.get_accessible_participants_ids()
        participants = TeraParticipant.query.join(TeraProject) \
            .filter(TeraProject.id_site == site_id, TeraParticipant.id_participant.in_(part_ids)) \
            .order_by(TeraParticipant.participant_name.asc()).all()
        return participants

    def query_enabled_participants_for_site(self, site_id: int) -> list[TeraParticipant]:
        part_ids = self.get_accessible_participants_ids()
        participants = TeraParticipant.query.join(TeraProject) \
            .filter(TeraProject.id_site == site_id, TeraParticipant.id_participant.in_(part_ids)) \
            .filter(TeraParticipant.participant_enabled == true()) \
            .order_by(TeraParticipant.participant_name.asc()).all()
        return participants

    def query_all_participants_for_project(self, project_id: int) -> list[TeraParticipant]:
        part_ids = self.get_accessible_participants_ids()
        participants = TeraParticipant.query.filter(TeraParticipant.id_project == project_id,
                                                    TeraParticipant.id_participant.in_(part_ids)) \
            .order_by(TeraParticipant.participant_name.asc()).all()
        return participants

    def query_enabled_participants_for_project(self, project_id: int) -> list[TeraParticipant]:
        part_ids = self.get_accessible_participants_ids()
        participants = TeraParticipant.query.filter(TeraParticipant.id_project == project_id,
                                                    TeraParticipant.id_participant.in_(part_ids)) \
            .filter(TeraParticipant.participant_enabled == true()) \
            .order_by(TeraParticipant.participant_name.asc()).all()
        return participants

    def query_participants_for_group(self, group_id: int) -> list[TeraParticipant]:
        part_ids = self.get_accessible_participants_ids()
        participants = TeraParticipant.query.filter(TeraParticipant.id_participant_group == group_id,
                                                    TeraParticipant.id_participant.in_(part_ids)) \
            .order_by(TeraParticipant.participant_name.asc()).all()
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

    def query_access_for_site(self, site_id: int, admin_only=False, include_empty_groups=False) -> dict:
        all_users_groups = self.get_accessible_users_groups(admin_only=admin_only, by_sites=True)
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

    def query_access_for_project(self, project_id: int, admin_only=False, include_empty_groups=False) -> dict:
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

    def query_site_access_for_user(self, user_id: int, admin_only=False) -> dict:
        from opentera.db.models.TeraUser import TeraUser
        user = TeraUser.get_user_by_id(user_id)
        site_roles = user.get_sites_roles()

        if admin_only:
            # Remove not admin roles
            site_roles = {key: value for key, value in site_roles.items() if value['site_role'] == 'admin'}

        # Filter only accessible sites for the current user
        accessible_sites = self.get_accessible_sites(admin_only=admin_only)
        site_roles = {site: site_roles[site] for site in set(site_roles).intersection(accessible_sites)}

        return site_roles

    def query_project_access_for_user(self, user_id: int, admin_only=False) -> dict:
        from opentera.db.models.TeraUser import TeraUser
        user = TeraUser.get_user_by_id(user_id)
        project_roles = user.get_projects_roles()

        if admin_only:
            # Remove not admin roles
            project_roles = {key: value for key, value in project_roles.items() if value['project_role'] == 'admin'}

        # Filter only accessible projects for the current user
        accessible_projects = self.get_accessible_projects(admin_only=admin_only)
        project_roles = {project: project_roles[project] for project in
                         set(project_roles).intersection(accessible_projects)}

        return project_roles

    def query_project_access_for_user_group(self, user_group_id: int, admin_only=False,
                                            include_projects_without_access=False) -> dict:
        from opentera.db.models.TeraUserGroup import TeraUserGroup
        user_group = TeraUserGroup.get_user_group_by_id(group_id=user_group_id)
        project_roles = user_group.get_projects_roles()
        if admin_only:
            # Remove not admin roles
            project_roles = {key: value for key, value in project_roles.items() if value['project_role'] == 'admin'}

        # Filter only accessible projects for the current user
        accessible_projects = self.get_accessible_projects(admin_only=admin_only)
        project_roles = {project: project_roles[project] for project in
                         set(project_roles).intersection(accessible_projects)}

        if include_projects_without_access:
            projects_without_access = set(accessible_projects).difference(project_roles)
            for project in projects_without_access:
                project_roles[project] = None

        return project_roles

    def query_site_access_for_user_group(self, user_group_id: int, admin_only=False,
                                         include_sites_without_access=False) -> dict:
        from opentera.db.models.TeraUserGroup import TeraUserGroup
        user_group = TeraUserGroup.get_user_group_by_id(group_id=user_group_id)
        site_roles = user_group.get_sites_roles()
        if admin_only:
            # Remove not admin roles
            site_roles = {key: value for key, value in site_roles.items() if value['site_role'] == 'admin'}

        # Filter only accessible sites for the current user
        accessible_sites = self.get_accessible_sites(admin_only=admin_only)
        site_roles = {site: site_roles[site] for site in set(site_roles).intersection(accessible_sites)}

        if include_sites_without_access:
            sites_without_access = set(accessible_sites).difference(site_roles)
            for site in sites_without_access:
                site_roles[site] = None

        return site_roles

    def query_participants_for_device(self, device_id: int) -> list[TeraParticipant]:
        from opentera.db.models.TeraParticipant import TeraParticipant
        parts = TeraParticipant.query.join(TeraParticipant.participant_devices).filter_by(id_device=device_id) \
            .filter(TeraDevice.id_device.in_(self.get_accessible_devices_ids()),
                    TeraParticipant.id_participant.in_(self.get_accessible_participants_ids())).all()
        return parts

    def query_device_participants_for_site(self, site_id: int) -> list[TeraDeviceParticipant]:
        device_parts = []
        if site_id in self.get_accessible_sites_ids():
            device_sites = TeraDeviceSite.get_devices_for_site(site_id=site_id)
            device_ids = list()
            for device_site in device_sites:
                if device_site.device_site_device.id_device not in device_ids:
                    device_ids.append(device_site.device_site_device.id_device)
                device_parts = TeraDeviceParticipant.query.join(TeraDeviceParticipant.device_participant_device) \
                    .join(TeraParticipant).join(TeraParticipant.participant_project).join(TeraProject.project_site) \
                    .filter_by(id_site=site_id).filter(TeraDevice.id_device.in_(device_ids)).all()
        return device_parts

    def query_device_participants_by_type(self, id_device_type: int, participant_id: int) -> list[TeraDeviceParticipant]:
        device_parts = TeraDeviceParticipant.query.join(TeraDevice) \
            .filter(TeraDevice.id_device_type == id_device_type,
                    TeraDeviceParticipant.id_participant == participant_id) \
            .order_by(TeraDeviceParticipant.id_device_participant.asc()).all()
        return device_parts

    def query_device_participants_for_device(self, device_id: int) -> list[TeraDeviceParticipant]:
        device_parts = TeraDeviceParticipant.query.filter_by(id_device=device_id).\
            filter(TeraDeviceParticipant.id_participant.in_(self.get_accessible_participants_ids())).all()
        return device_parts

    def query_session(self, session_id: int) -> TeraSession | None:


        # session = TeraSession.query.join(TeraSession.session_participants).join(TeraSession.session_users)\
        #     .filter(and_(TeraSession.id_session == session_id),
        #             or_(TeraParticipant.id_participant.in_(self.get_accessible_participants_ids()),
        #                 TeraSessionUsers.id_user == self.user.id_user,
        #                 TeraSession.id_creator_user == self.user.id_user)).first()

        session = TeraSession.get_session_by_id(session_id)

        if session:
            # Check if we are the creator of that session
            if session.id_creator_user == self.user.id_user:
                return session

            # Check if we are part of the users of that session
            if session.has_user(self.user.id_user):
                return session

            # Check if we have access to the project of that session
            accessible_projects = self.get_accessible_projects_ids()
            if session.get_associated_project_id() in accessible_projects:
                return session

        return None

    def query_session_events(self, session_id: int) -> list[TeraSessionEvent]:


        if self.query_session(session_id=session_id):
            return TeraSessionEvent.get_events_for_session(id_session=session_id)

        return []

    # def query_session_types_for_device(self, device_type_id: int):
    #     from opentera.db.models.TeraSessionTypeDeviceType import TeraSessionTypeDeviceType
    #     session_types_ids = self.get_accessible_session_types_ids()
    #
    #     session_types = TeraSessionTypeDeviceType.query.filter(TeraSessionTypeDeviceType.id_session_type.
    #                                                            in_(session_types_ids))\
    #         .filter_by(id_device_type=device_type_id).all()
    #     return session_types

    def query_session_types_for_project(self, project_id: int, include_other_session_types: bool = False) -> list[TeraSessionTypeProject]:
        session_types_ids = self.get_accessible_session_types_ids()
        service_ids = self.get_accessible_services_ids()

        session_types = TeraSessionTypeProject.query.filter(TeraSessionTypeProject.id_session_type.
                                                            in_(session_types_ids)) \
            .filter_by(id_project=project_id).join(TeraSessionType).filter(or_(
                TeraSessionType.session_type_category != TeraSessionType.SessionCategoryEnum.SERVICE.value, and_(
                    TeraSessionType.session_type_category == TeraSessionType.SessionCategoryEnum.SERVICE.value,
                    TeraSessionType.id_service.in_(service_ids)).self_group())).all()

        if include_other_session_types:
            # We must add the missing session types in the list
            project = TeraProject.get_project_by_id(project_id)
            site_sts = TeraSessionTypeSite.get_sessions_types_for_site(project.id_site)
            site_st_ids = [st.id_session_type for st in site_sts]
            st_ids = [st.id_session_type for st in session_types]
            missing_st_ids = set(site_st_ids).difference(st_ids)
            for missing_st_id in missing_st_ids:
                st_proj = TeraSessionTypeProject()
                st_proj.id_session_type = missing_st_id
                st_proj.id_project = None
                st_proj.session_type_project_session_type = TeraSessionType.get_session_type_by_id(missing_st_id)
                session_types.append(st_proj)

        # Sort by name
        return sorted(session_types, key=lambda s: s.session_type_project_session_type.session_type_name)

    def query_tests_types_for_project(self, project_id: int, include_other_tests_types: bool = False) -> list[TeraTestTypeProject]:
        test_types_ids = self.get_accessible_tests_types_ids()
        service_ids = self.get_accessible_services_ids()

        test_types = TeraTestTypeProject.query.filter(TeraTestTypeProject.id_test_type.in_(test_types_ids)) \
            .filter_by(id_project=project_id).join(TeraTestType).filter(TeraTestType.id_service.in_(service_ids)).all()

        if include_other_tests_types:
            # We must add the missing test types in the list
            project = TeraProject.get_project_by_id(project_id)
            site_tts = TeraTestType.query.filter(TeraTestType.id_service.in_(service_ids)).join(TeraTestTypeSite).\
                filter(TeraTestTypeSite.id_site == project.id_site)
            site_tt_ids = [tt.id_test_type for tt in site_tts]
            tt_ids = [tt.id_test_type for tt in test_types]
            missing_tt_ids = set(site_tt_ids).difference(tt_ids)
            for missing_tt_id in missing_tt_ids:
                tt_proj = TeraTestTypeProject()
                tt_proj.id_test_type = missing_tt_id
                tt_proj.id_project = None
                tt_proj.test_type_project_test_type = TeraTestType.get_test_type_by_id(missing_tt_id)
                test_types.append(tt_proj)

        # Sort by name
        return sorted(test_types, key=lambda s: s.test_type_project_test_type.test_type_name)

    def query_secondary_services_for_session_type(self, session_type_id: int, include_other_services: bool = False) -> list[TeraSessionTypeServices]:
        session_types_ids = self.get_accessible_session_types_ids()

        session_types_services = (TeraSessionTypeServices.query.filter(TeraSessionTypeServices.id_session_type.
                                                            in_(session_types_ids))
                         .filter_by(id_session_type=session_type_id).all())

        if include_other_services:
            service_ids = self.get_accessible_services_ids()
            st_service_ids = [st.id_service for st in session_types_services]
            missing_service_ids = set(service_ids).difference(st_service_ids)
            for missing_service_id in missing_service_ids:
                st_service = TeraSessionTypeServices()
                st_service.id_service = missing_service_id
                st_service.id_session_type = None
                st_service.session_type_service_service = TeraService.get_service_by_id(missing_service_id)
                session_types_services.append(st_service)
            return sorted(session_types_services, key=lambda s: s.session_type_service_service.service_name)

        # Sort by name
        return sorted(session_types_services, key=lambda s: s.session_type_service_session_type.session_type_name)

    def query_assets_associated_to_service(self, uuid_service: str) -> list[TeraAsset]:


        # If user has access to session, it should have access to its assets
        session_ids = self.get_accessible_sessions_ids()
        # device_ids = self.get_accessible_devices_ids()
        # participant_ids = self.get_accessible_participants_ids()
        # user_ids = self.get_accessible_users_ids()
        service_ids = self.get_accessible_services_ids()

        return TeraAsset.query.filter(TeraAsset.id_session.in_(session_ids))\
            .filter(TeraAsset.asset_service_uuid == uuid_service) \
            .filter(or_(TeraAsset.id_service.in_(service_ids), TeraAsset.id_service == None)) \
            .all()
        # .filter(or_(TeraAsset.id_device.in_(device_ids), TeraAsset.id_device == None)) \
        # .filter(or_(TeraAsset.id_participant.in_(participant_ids), TeraAsset.id_participant == None)) \
        # .filter(or_(TeraAsset.id_user.in_(user_ids), TeraAsset.id_user == None)) \

    def query_projects_for_service(self, service_id: int, site_id: int = None, include_other_projects=False) -> list[TeraServiceProject]:

        projects_ids = self.get_accessible_projects_ids()

        query = TeraServiceProject.query.filter(TeraServiceProject.id_project.in_(projects_ids)) \
            .filter_by(id_service=service_id)

        if site_id:
            query = query.join(TeraProject).filter(TeraProject.id_site == site_id)

        service_projects = query.all()
        if include_other_projects:
            # We must add the missing projects in the list
            missing_projects_ids = set(projects_ids).difference([sp.id_project for sp in service_projects])
            for missing_project_id in missing_projects_ids:
                service_project = TeraServiceProject()
                service_project.id_project = missing_project_id
                service_project.id_service = None
                service_project.service_project_project = TeraProject.get_project_by_id(missing_project_id)
                service_projects.append(service_project)

        # Sort by project
        return sorted(service_projects, key=lambda sp: sp.service_project_project.project_name)

    def query_session_types_sites_for_site(self, site_id: int, include_other_session_types=False) -> list[TeraSessionTypeSite]:
        st_sites = TeraSessionTypeSite.get_sessions_types_for_site(site_id=site_id)

        if include_other_session_types:
            # We must add the missing session types in the list, even if we don't have access to them
            if self.user.user_superadmin:
                other_sts = TeraSessionType.query_with_filters()
            else:
                sites_ids = self.get_accessible_sites_ids()
                other_sts = TeraSessionType.query.join(TeraSessionTypeSite)\
                    .filter(TeraSessionTypeSite.id_site.in_(sites_ids)).all()
            st_ids = [st.id_session_type for st in other_sts]
            missing_st_ids = set(st_ids).difference([st.id_session_type for st in st_sites])
            for missing_st_id in missing_st_ids:
                st_site = TeraSessionTypeSite()
                st_site.id_site = None
                st_site.id_session_type = missing_st_id
                st_site.session_type_site_session_type = TeraSessionType.get_session_type_by_id(missing_st_id)
                st_sites.append(st_site)

        # Sort by device name
        return sorted(st_sites, key=lambda s: s.session_type_site_session_type.session_type_name)

    def query_session_types_sites_for_session_type(self, session_type_id: int, include_other_sites=False) -> list[TeraSessionTypeSite]:
        site_ids = self.get_accessible_sites_ids()

        query = TeraSessionTypeSite.query.filter(TeraSessionTypeSite.id_site.in_(site_ids)) \
            .filter_by(id_session_type=session_type_id)

        st_sites = query.all()
        if include_other_sites:
            # We must add the missing sites in the list
            missing_sites_ids = set(site_ids).difference([s.id_site for s in st_sites])
            for missing_site_id in missing_sites_ids:
                st_site = TeraSessionTypeSite()
                st_site.id_site = missing_site_id
                st_site.id_session_type = None
                st_site.session_type_site_site = TeraSite.get_site_by_id(missing_site_id)
                st_sites.append(st_site)

        # Sort by site name
        return sorted(st_sites, key=lambda s: s.session_type_site_site.site_name)

    def query_tests_types_sites_for_site(self, site_id: int, include_other_tests_types=False) -> list[TeraTestTypeSite]:
        service_ids = self.get_accessible_services_ids()
        tt_sites = TeraTestTypeSite.query.filter_by(id_site=site_id).join(TeraTestType)\
            .filter(TeraTestType.id_service.in_(service_ids)).all()

        if include_other_tests_types:
            # We must add the missing test types in the list, even if we don't have access to them
            if self.user.user_superadmin:
                other_tts = TeraTestType.query_with_filters()
            else:
                sites_ids = self.get_accessible_sites_ids()
                other_tts = TeraTestType.query.join(TeraTestTypeSite)\
                    .filter(TeraTestTypeSite.id_site.in_(sites_ids)).filter(TeraTestType.id_service.in_(service_ids))\
                    .all()
            tt_ids = [tt.id_test_type for tt in other_tts]
            missing_tt_ids = set(tt_ids).difference([tt.id_test_type for tt in tt_sites])
            for missing_tt_id in missing_tt_ids:
                tt_site = TeraTestTypeSite()
                tt_site.id_site = None
                tt_site.id_test_type = missing_tt_id
                tt_site.test_type_site_test_type = TeraTestType.get_test_type_by_id(missing_tt_id)
                tt_sites.append(tt_site)

        # Sort by name
        return sorted(tt_sites, key=lambda s: s.test_type_site_test_type.test_type_name)

    def query_tests_types_sites_for_session_type(self, test_type_id: int, include_other_sites=False) -> list[TeraTestTypeSite]:
        site_ids = self.get_accessible_sites_ids()
        service_ids = self.get_accessible_services_ids()

        query = TeraTestTypeSite.query.filter(TeraTestTypeSite.id_site.in_(site_ids)) \
            .filter_by(id_test_type=test_type_id).join(TeraTestType).filter(TeraTestType.id_service.in_(service_ids))

        tt_sites = query.all()
        if include_other_sites:
            # We must add the missing sites in the list
            missing_sites_ids = set(site_ids).difference([s.id_site for s in tt_sites])
            for missing_site_id in missing_sites_ids:
                tt_site = TeraTestTypeSite()
                tt_site.id_site = missing_site_id
                tt_site.id_test_type = None
                tt_site.test_type_site_site = TeraSite.get_site_by_id(missing_site_id)
                tt_sites.append(tt_site)

        # Sort by site name
        return sorted(tt_sites, key=lambda s: s.test_type_site_site.site_name)

    def query_services_projects_for_project(self, project_id: int, include_other_services=False) -> list[TeraServiceProject]:
        services_ids = self.get_accessible_services_ids()

        service_projects = TeraServiceProject.query.filter(TeraServiceProject.id_service.in_(services_ids)) \
            .filter_by(id_project=project_id).all()

        if include_other_services:
            # We must add the missing services in the list, even if we don't have access to them
            # services_ids = self.get_accessible_services_ids(all_services=True)
            project = TeraProject.get_project_by_id(project_id=project_id)
            if not project:
                return []
            other_services = TeraServiceSite.get_services_for_site(id_site=project.id_site)
            other_services_ids = [service.id_service for service in other_services]
            missing_services_ids = set(other_services_ids).difference([sp.id_service for sp in service_projects])
            for missing_service_id in missing_services_ids:
                service_project = TeraServiceProject()
                service_project.id_project = None
                service_project.id_service = missing_service_id
                service_project.service_project_service = TeraService.get_service_by_id(missing_service_id)
                service_projects.append(service_project)

        # Sort by service name
        return sorted(service_projects, key=lambda sp: sp.service_project_service.service_name)

    def query_services_for_project(self, project_id: int, include_other_services=False) -> list[TeraService]:
        services_projects = self.query_services_projects_for_project(project_id, include_other_services)
        services = [sp.service_project_service for sp in services_projects]
        return services

    def query_sites_for_service(self, service_id: int, include_other_sites=False) -> list[TeraServiceSite]:
        site_ids = self.get_accessible_sites_ids()

        query = TeraServiceSite.query.filter(TeraServiceSite.id_site.in_(site_ids)) \
            .filter_by(id_service=service_id)

        service_sites = query.all()
        if include_other_sites:
            # We must add the missing sites in the list
            missing_sites_ids = set(site_ids).difference([ss.id_site for ss in service_sites])
            for missing_site_id in missing_sites_ids:
                service_site = TeraServiceSite()
                service_site.id_site = missing_site_id
                service_site.id_service = None
                service_site.service_site_site = TeraSite.get_site_by_id(missing_site_id)
                service_sites.append(service_site)

        # Sort by site name
        return sorted(service_sites, key=lambda ss: ss.service_site_site.site_name)

    def query_services_sites_for_site(self, site_id: int, include_other_services=False) -> list[TeraServiceSite]:
        services_ids = self.get_accessible_services_ids()

        service_sites = TeraServiceSite.query.filter(TeraServiceSite.id_service.in_(services_ids)) \
            .filter_by(id_site=site_id).filter(TeraServiceSite.id_service != Globals.opentera_service_id).all()

        if include_other_services:
            # We must add the missing services in the list, even if we don't have access to them
            if self.user.user_superadmin:
                other_services = [service for service in TeraService.query_with_filters()
                                  if service.service_key != 'OpenTeraServer']
            else:
                sites_ids = self.get_accessible_sites_ids()
                other_services = TeraService.query.join(TeraServiceSite).filter(TeraServiceSite.id_site.in_(sites_ids))\
                    .filter(TeraService.service_key != 'OpenTeraServer').all()
            services_ids = [service.id_service for service in other_services]
            missing_services_ids = set(services_ids).difference([ss.id_service for ss in service_sites])
            for missing_service_id in missing_services_ids:
                service_site = TeraServiceSite()
                service_site.id_site = None
                service_site.id_service = missing_service_id
                service_site.service_site_service = TeraService.get_service_by_id(missing_service_id)
                service_sites.append(service_site)

        # Sort by service name
        return sorted(service_sites, key=lambda ss: ss.service_site_service.service_name)

    def query_services_for_site(self, site_id: int, include_other_services=False) -> list[TeraService]:
        services_sites = self.query_services_sites_for_site(site_id, include_other_services)
        services = [ss.service_site_service for ss in services_sites]
        return services

    def query_users_usergroups_for_usergroup(self, user_group_id: int, enabled_only: bool = False,
                                             include_other_users: bool = False) -> list[TeraUserUserGroup]:
        accessible_users_ids = self.get_accessible_users_ids()
        query = TeraUserUserGroup.query.filter_by(id_user_group=user_group_id).filter(TeraUserUserGroup.id_user
                                                                                      .in_(accessible_users_ids)) \
            .join(TeraUser).order_by(TeraUser.user_firstname.asc())
        if enabled_only:
            query = query.filter(TeraUser.user_enabled is True)
        users_user_groups = query.all()

        if include_other_users:
            # We must add the missing users in the list
            users_ids = self.get_accessible_users_ids()
            missing_users_ids = set(users_ids).difference([uug.id_user for uug in users_user_groups])
            for missing_user_id in missing_users_ids:
                user = TeraUser.get_user_by_id(missing_user_id)
                if not user.user_superadmin:
                    user_user_group = TeraUserUserGroup()
                    user_user_group.id_user_group = None
                    user_user_group.id_user = missing_user_id
                    user_user_group.user_user_group_user = user
                    users_user_groups.append(user_user_group)

        # Sort by user first
        return sorted(users_user_groups, key=lambda suser: suser.user_user_group_user.user_firstname)
        # return users_user_groups

    def query_users_for_usergroup(self, user_group_id: int, enabled_only: bool = False) -> list[TeraUser]:
        user_usergroups = self.query_users_usergroups_for_usergroup(user_group_id=user_group_id,
                                                                    enabled_only=enabled_only)
        return [u.user_user_group_user for u in user_usergroups]

    def query_users_usergroups_for_user(self, user_id: int, include_other_user_groups: bool = False) -> list[TeraUserUserGroup]:
        accessible_user_groups_ids = self.get_accessible_users_groups_ids()
        query = TeraUserUserGroup.query.filter_by(id_user=user_id).filter(TeraUserUserGroup.id_user_group
                                                                          .in_(accessible_user_groups_ids))

        users_user_groups = query.all()
        if include_other_user_groups:
            # We must add the missing user groups in the list
            user_groups_ids = self.get_accessible_users_groups_ids()
            missing_ug_ids = set(user_groups_ids).difference([uug.id_user_group for uug in users_user_groups])
            for missing_ug_id in missing_ug_ids:
                user_user_group = TeraUserUserGroup()
                user_user_group.id_user_group = missing_ug_id
                user_user_group.id_user = None
                user_user_group.user_user_group_user_group = TeraUserGroup.get_user_group_by_id(missing_ug_id)
                users_user_groups.append(user_user_group)

        # return users_user_groups
        # Sort by user group name
        return sorted(users_user_groups, key=lambda suser: suser.user_user_group_user_group.user_group_name)

    def query_usergroups_for_user(self, user_id: int) -> list[TeraUserGroup]:
        user_usergroups = self.query_users_usergroups_for_user(user_id=user_id)
        return [ug.user_user_group_user_group for ug in user_usergroups]

    def query_users_for_site(self, site_id: int, enabled_only: bool = False, admin_only: bool = False,
                             include_super_admins: bool = False) -> list[TeraUser]:
        # is_site_admin = self.get_site_role(site_id) == 'admin'
        accessible_users = self.get_accessible_users(include_site_access=True)
        users = set()
        for user in accessible_users:
            if (enabled_only and not user.user_enabled) or (not include_super_admins and user.user_superadmin):
                continue
            sites_roles = user.get_sites_roles()
            if site_id in [site.id_site for site, site_role in sites_roles.items()
                           if (admin_only and site_role['site_role'] == 'admin') or not admin_only]:
                users.add(user)

        return users

    def query_users_for_project(self, project_id: int, enabled_only: bool = False, admin_only: bool = False,
                                include_super_admins: bool = False) -> list[TeraUser]:

        # Only returns site admins users if itself is site admin!
        # project = TeraProject.get_project_by_id(project_id)
        # is_site_admin = self.get_site_role(project.id_site) == 'admin'
        accessible_users = self.get_accessible_users(include_site_access=True)

        users = set()
        for user in accessible_users:
            if enabled_only and not user.user_enabled or (not include_super_admins and user.user_superadmin):
                continue
            project_roles = user.get_projects_roles()
            if project_id in [proj.id_project for proj, proj_role in project_roles.items()
                              if (admin_only and proj_role['project_role'] == 'admin') or not admin_only]:
                users.add(user)

        return sorted(users, key=lambda suser: suser.user_firstname)

    def query_service_configs(self, service_id: int = None, user_id: int = None, device_id: int = None,
                              participant_id: int = None, include_services_without_config: bool = False) -> list[TeraServiceConfig]:
        if service_id and service_id not in self.get_accessible_services_ids():
            return None
        if user_id and user_id not in self.get_accessible_users_ids():
            return None
        if device_id and device_id not in self.get_accessible_devices_ids():
            return None
        if participant_id and participant_id not in self.get_accessible_participants_ids():
            return None

        services_configs = None
        if service_id:
            if user_id:
                services_configs = TeraServiceConfig.get_service_config_for_service_for_user(service_id=service_id,
                                                                                             user_id=user_id)
            elif device_id:
                services_configs = TeraServiceConfig.get_service_config_for_service_for_device(service_id=service_id,
                                                                                               device_id=device_id)
            elif participant_id:
                services_configs = TeraServiceConfig.get_service_config_for_service_for_participant(
                    service_id=service_id, participant_id=participant_id)
            else:
                services_configs = TeraServiceConfig.get_service_config_for_service(service_id=service_id)
        else:
            if user_id:
                services_configs = TeraServiceConfig.query.filter_by(id_user=user_id). \
                    join(TeraServiceConfig.service_config_service).filter_by(service_editable_config=True).all()

            elif device_id:
                services_configs = TeraServiceConfig.query.filter_by(id_device=device_id). \
                    join(TeraServiceConfig.service_config_service).filter_by(service_editable_config=True).all()

            elif participant_id:
                services_configs = TeraServiceConfig.query.filter_by(id_participant=participant_id). \
                    join(TeraServiceConfig.service_config_service).filter_by(service_editable_config=True).all()

        if include_services_without_config:
            # Also create "empty" configs for service not in the list
            services = self.get_accessible_services()
            missing_services = set(services).difference([sc.service_config_service for sc in services_configs])
            for service in missing_services:
                # Check if that service allows for editable configs. If not, ignore!
                if service.service_editable_config:
                    temp_service_config = TeraServiceConfig()
                    temp_service_config.id_service = service.id_service
                    temp_service_config.service_config_service = service
                    temp_service_config.service_config_config = None
                    services_configs.append(temp_service_config)

        return services_configs

    def query_service_access(self, user_group_id: int = None, device_id: int = None, participant_group_id: int = None,
                             service_id: int = None, user_id: int = None) -> list[TeraServiceAccess]:

        accessible_services_ids = self.get_accessible_services_ids()

        query = TeraServiceAccess.query
        if user_group_id:
            query = query.filter_by(id_user_group=user_group_id)
        if device_id:
            query = query.filter_by(id_device=device_id)
        if participant_group_id:
            query = query.filter_by(id_participant_group=participant_group_id)
        if user_id:
            user = TeraUser.get_user_by_id(user_id)
            user_groups_ids = [ug.id_user_group for ug in user.user_user_groups]
            query = query.filter(TeraServiceAccess.id_user_group.in_(user_groups_ids))

        if service_id:
            query = query.join(TeraServiceAccess.service_access_role).filter_by(id_service=service_id)
        else:
            query = query.join(TeraServiceAccess.service_access_role).filter(TeraServiceRole
                                                                             .id_service.in_(accessible_services_ids))

        return query.all()

    def query_asset(self, asset_id: int = None, asset_uuid: str = None) -> TeraAsset | None:
        # from sqlalchemy import or_

        if not asset_id and not asset_uuid:
            return None

        if asset_id:
            asset: TeraAsset = TeraAsset.get_asset_by_id(asset_id)
        elif asset_uuid:
            asset: TeraAsset = TeraAsset.get_asset_by_uuid(asset_uuid)
        else:
            return None

        asset_session = self.query_session(asset.id_session)
        if not asset_session:
            # No access to asset session
            return None

        if asset.asset_service_uuid not in [service.service_uuid for service in self.get_accessible_services()]:
            return None

        return [asset]

    def query_test(self, test_id: int = None, test_uuid: str = None) -> TeraTest | None:
        if not test_id and not test_uuid:
            return None

        if test_id:
            test: TeraTest = TeraTest.get_test_by_id(test_id)
        elif test_uuid:
            test: TeraTest = TeraTest.get_test_by_uuid(test_uuid)
        else:
            return None

        if not test:
            return None

        test_session = self.query_session(test.id_session)
        if not test_session:
            # No access to asset session
            return None

        if test.test_test_type.id_service not in [service.id_service for service in self.get_accessible_services()]:
            return None

        return test

    def get_accessible_tests_invitations(self) -> list[TeraTestInvitation]:
        """
        Get all test invitations accessible by the current user
        """
        accessible_test_type_ids = self.get_accessible_tests_types_ids()
        accessible_user_ids = self.get_accessible_users_ids()
        accessible_participant_ids = self.get_accessible_participants_ids()
        accessible_device_ids = self.get_accessible_devices_ids()
        accessible_session_ids = self.get_accessible_sessions_ids()

        test_invitations = TeraTestInvitation.query.filter(
            TeraTestInvitation.id_test_type.in_(accessible_test_type_ids)
        ).filter(
            or_(
                and_(TeraTestInvitation.id_user.isnot(None),
                    TeraTestInvitation.id_user.in_(accessible_user_ids)),
                and_(TeraTestInvitation.id_participant.isnot(None),
                    TeraTestInvitation.id_participant.in_(accessible_participant_ids)),
                and_(TeraTestInvitation.id_device.isnot(None),
                    TeraTestInvitation.id_device.in_(accessible_device_ids)),
                and_(TeraTestInvitation.id_session.isnot(None),
                    TeraTestInvitation.id_session.in_(accessible_session_ids))
            )
        ).all()
        return test_invitations

    def get_accessible_tests_invitations_ids(self) -> list[int]:
        """
        Get all test invitations accessible by the current user
        """
        test_invitations = self.get_accessible_tests_invitations()
        return [test_invitation.id_test_invitation for test_invitation in test_invitations]
