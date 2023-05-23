from opentera.db.Base import BaseModel
from opentera.db.SoftDeleteMixin import SoftDeleteMixin
from sqlalchemy import Column, ForeignKey, Integer, String, Sequence, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.exc import IntegrityError


class TeraProject(BaseModel, SoftDeleteMixin):
    __tablename__ = 't_projects'
    id_project = Column(Integer, Sequence('id_project_sequence'), primary_key=True, autoincrement=True)
    id_site = Column(Integer, ForeignKey('t_sites.id_site', ondelete='cascade'), nullable=False)
    project_name = Column(String, nullable=False, unique=False)
    project_enabled = Column(Boolean, nullable=False, default=True)
    project_description = Column(String, nullable=True)

    project_site = relationship("TeraSite", back_populates='site_projects')
    project_participants = relationship("TeraParticipant", cascade='delete', back_populates='participant_project',
                                        passive_deletes=True)
    project_participants_groups = relationship("TeraParticipantGroup", cascade='delete', passive_deletes=True)
    project_devices = relationship("TeraDevice", secondary="t_devices_projects", back_populates="device_projects")
    project_session_types = relationship("TeraSessionType", secondary="t_sessions_types_projects",
                                         back_populates="session_type_projects")

    project_services = relationship("TeraService", secondary="t_services_projects", viewonly=True)

    project_services_roles = relationship("TeraServiceRole", cascade='delete', passive_deletes=True)

    project_tests_types = relationship("TeraTestType", secondary="t_tests_types_projects", viewonly=True)

    def to_json(self, ignore_fields=None, minimal=False):
        if ignore_fields is None:
            ignore_fields = []

        ignore_fields.extend(['project_site', 'project_participants', 'project_participants_groups', 'project_devices',
                              'project_session_types', 'project_services', 'project_services_roles',
                              'project_tests_types'])

        rval = super().to_json(ignore_fields=ignore_fields)

        # Add sitename
        if 'site_name' not in ignore_fields and not minimal:
            rval['site_name'] = self.project_site.site_name

        return rval

    def to_json_create_event(self):
        return self.to_json(minimal=True)

    def to_json_update_event(self):
        return self.to_json(minimal=True)

    def to_json_delete_event(self):
        # Minimal information, delete can not be filtered
        return {'id_project': self.id_project}

    def get_users_ids_in_project(self, with_deleted: bool = False):
        # Get all users who has a role in the project
        users = self.get_users_in_project(with_deleted=with_deleted)
        users_ids = []

        for user in users:
            users_ids.append(user.id_user)

        return users_ids

    def get_users_in_project(self, include_superadmins=False, include_site_access=False, with_deleted: bool = False):
        import modules.Globals as Globals
        from opentera.db.models.TeraServiceAccess import TeraServiceAccess
        from opentera.db.models.TeraUser import TeraUser
        # Get all users who have a role in the project
        project_access = TeraServiceAccess.get_service_access(id_service=Globals.opentera_service_id,
                                                              id_project=self.id_project,
                                                              with_deleted=with_deleted)

        users = []
        for access in project_access:
            # Get all users in the related group
            if access.service_access_user_group:
                access_users = access.service_access_user_group.user_group_users
                for user in access_users:
                    if user not in users:
                        users.append(user)

        # Also appends users with site access but no direct access to project
        if include_site_access:
            site_access = TeraServiceAccess.get_service_access(id_service=Globals.opentera_service_id,
                                                               id_site=self.id_site,
                                                               with_deleted=with_deleted)
            for access in site_access:
                if access.service_access_role.service_role_name == 'admin':
                    if access.service_access_user_group:
                        access_users = access.service_access_user_group.user_group_users
                        for user in access_users:
                            if user not in users:
                                users.append(user)

        # Also appends super admins!
        if include_superadmins:
            for user in TeraUser.get_superadmins():
                if user not in users:
                    users.append(user)

        return users

    @staticmethod
    def create_defaults(test=False):
        if test:
            from opentera.db.models.TeraSite import TeraSite
            base_project = TeraProject()
            base_project.project_name = 'Default Project #1'
            base_project.id_site = TeraSite.get_site_by_sitename('Default Site').id_site
            TeraProject.insert(base_project)

            base_project2 = TeraProject()
            base_project2.project_name = 'Default Project #2'
            base_project2.id_site = TeraSite.get_site_by_sitename('Default Site').id_site
            TeraProject.insert(base_project2)

            secret_project = TeraProject()
            secret_project.project_name = "Secret Project #1"
            secret_project.id_site = TeraSite.get_site_by_sitename('Top Secret Site').id_site
            TeraProject.insert(secret_project)

    @staticmethod
    def get_project_by_projectname(projectname, with_deleted: bool = False):
        return TeraProject.query.execution_options(include_deleted=with_deleted) \
            .filter_by(project_name=projectname).first()

    @staticmethod
    def get_project_by_id(project_id, with_deleted: bool = False):
        return TeraProject.query.execution_options(include_deleted=with_deleted) \
            .filter_by(id_project=project_id).first()

    # @staticmethod
    # def query_data(filter_args, with_deleted: bool = False):
    #     if isinstance(filter_args, tuple):
    #         return TeraProject.query.execution_options(include_deleted=with_deleted)\
    #             .filter_by(*filter_args).all()
    #     if isinstance(filter_args, dict):
    #         return TeraProject.query.execution_options(include_deleted=with_deleted)\
    #             .filter_by(**filter_args).all()
    #     return None

    def delete_check_integrity(self) -> IntegrityError | None:
        for participant in self.project_participants:
            cannot_be_deleted_exception = participant.delete_check_integrity()
            if cannot_be_deleted_exception:
                return IntegrityError('Still have participants with session', self.id_project, 't_participants')
        return None

    @classmethod
    def update(cls, update_id: int, values: dict):
        # Update general infos
        super().update(update_id, values)

        # If project is inactive, disable all participants from that project
        if 'project_enabled' in values and not values['project_enabled']:
            from opentera.db.models.TeraDeviceParticipant import TeraDeviceParticipant
            project = TeraProject.get_project_by_id(update_id)
            for participant in project.project_participants:
                participant.participant_enabled = False  # Set participant inactive
                devices = TeraDeviceParticipant.query_devices_for_participant(participant.id_participant)
                for device in devices:
                    TeraDeviceParticipant.delete(device.id_device_participant)
            cls.db().session.commit()

    @classmethod
    def insert(cls, project):
        # Creates admin and user roles for that project
        super().insert(project)

        from opentera.db.models.TeraServiceRole import TeraServiceRole
        from opentera.db.models.TeraService import TeraService
        opentera_service_id = TeraService.get_openteraserver_service().id_service

        access_role = TeraServiceRole()
        access_role.id_service = opentera_service_id
        access_role.id_project = project.id_project
        access_role.service_role_name = 'admin'
        TeraProject.db().session.add(access_role)

        access_role = TeraServiceRole()
        access_role.id_service = opentera_service_id
        access_role.id_project = project.id_project
        access_role.service_role_name = 'user'
        TeraProject.db().session.add(access_role)

        TeraProject.db().session.commit()
