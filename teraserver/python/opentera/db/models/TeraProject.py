from opentera.db.Base import db, BaseModel


class TeraProject(db.Model, BaseModel):
    __tablename__ = 't_projects'
    id_project = db.Column(db.Integer, db.Sequence('id_project_sequence'), primary_key=True, autoincrement=True)
    id_site = db.Column(db.Integer, db.ForeignKey('t_sites.id_site', ondelete='cascade'), nullable=False)
    project_name = db.Column(db.String, nullable=False, unique=False)

    project_site = db.relationship("TeraSite")
    project_participants = db.relationship("TeraParticipant", passive_deletes=True)
    project_participants_groups = db.relationship("TeraParticipantGroup", passive_deletes=True)
    project_devices = db.relationship("TeraDevice", secondary="t_devices_projects", back_populates="device_projects")
    project_session_types = db.relationship("TeraSessionType", secondary="t_sessions_types_projects",
                                            back_populates="session_type_projects")

    def to_json(self, ignore_fields=None, minimal=False):
        if ignore_fields is None:
            ignore_fields = []

        ignore_fields.extend(['project_site', 'project_participants', 'project_participants_groups', 'project_devices',
                              'project_session_types'])
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

    def get_users_ids_in_project(self):
        # Get all users who has a role in the project
        users = self.get_users_in_project()
        users_ids = []

        for user in users:
            users_ids.append(user.id_user)

        return users_ids

    def get_users_in_project(self):
        import modules.Globals as Globals
        from opentera.db.models.TeraServiceAccess import TeraServiceAccess
        from opentera.db.models.TeraUser import TeraUser
        # Get all users who has a role in the project
        project_access = TeraServiceAccess.get_service_access_for_project(id_service=Globals.opentera_service_id,
                                                                          id_project=self.id_project)

        users = []
        for access in project_access:
            # Get all users in the related group
            if access.service_access_user_group:
                access_users = access.service_access_user_group.user_group_users
                for user in access_users:
                    if user not in users:
                        users.append(user)

        # Also appends super admins!
        # for user in TeraUser.get_superadmins():
        #     if user not in users:
        #         users.append(user)

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
    def get_project_by_projectname(projectname):
        return TeraProject.query.filter_by(project_name=projectname).first()

    @staticmethod
    def get_project_by_id(project_id):
        return TeraProject.query.filter_by(id_project=project_id).first()

    @staticmethod
    def query_data(filter_args):
        if isinstance(filter_args, tuple):
            return TeraProject.query.filter_by(*filter_args).all()
        if isinstance(filter_args, dict):
            return TeraProject.query.filter_by(**filter_args).all()
        return None

    @classmethod
    def delete(cls, id_todel):
        super().delete(id_todel)

        # from opentera.db.models.TeraSession import TeraSession
        # TeraSession.delete_orphaned_sessions()

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
        db.session.add(access_role)

        access_role = TeraServiceRole()
        access_role.id_service = opentera_service_id
        access_role.id_project = project.id_project
        access_role.service_role_name = 'user'
        db.session.add(access_role)

        db.session.commit()
