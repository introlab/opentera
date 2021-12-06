from opentera.db.Base import db, BaseModel


class TeraUserGroup(db.Model, BaseModel):
    __tablename__ = 't_users_groups'
    id_user_group = db.Column(db.Integer, db.Sequence('id_usergroup_sequence'), primary_key=True, autoincrement=True)
    user_group_name = db.Column(db.String, nullable=False, unique=False)

    user_group_services_access = db.relationship('TeraServiceAccess', cascade="all,delete",
                                                 back_populates='service_access_user_group')
    user_group_users = db.relationship("TeraUser", secondary="t_users_users_groups", back_populates="user_user_groups",
                                       passive_deletes=True)

    def to_json(self, ignore_fields=None, minimal=False):
        if ignore_fields is None:
            ignore_fields = []
        ignore_fields.extend(['user_group_users', 'user_group_services_access', 'user_group_projects_access'])
        if minimal:
            ignore_fields.extend([])
        rval = super().to_json(ignore_fields=ignore_fields)

        return rval

    def to_json_create_event(self):
        return self.to_json(minimal=True)

    def to_json_update_event(self):
        return self.to_json(minimal=True)

    def to_json_delete_event(self):
        # Minimal information, delete can not be filtered
        return {'id_user_group': self.id_user_group}

    def get_projects_roles(self, no_inheritance: bool = False) -> dict:
        projects_roles = {}

        # Projects
        for service_access in self.user_group_services_access:
            if service_access.service_access_role.id_project:
                projects_roles[service_access.service_access_role.service_role_project] = \
                    {'project_role': service_access.service_access_role.service_role_name, 'inherited': False}

        # Sites - if we are admin in a site, we are automatically admin in all its project
        if not no_inheritance:
            for service_access in self.user_group_services_access:
                if service_access.service_access_role.id_site:
                    if service_access.service_access_role.service_role_name == 'admin':
                        for project in service_access.service_access_role.service_role_site.site_projects:
                            projects_roles[project] = {'project_role': 'admin', 'inherited': True}

        return projects_roles

    def get_sites_roles(self) -> dict:
        sites_roles = {}
        # Sites
        for service_access in self.user_group_services_access:
            if service_access.service_access_role.id_site:
                sites_roles[service_access.service_access_role.service_role_site] = \
                    {'site_role': service_access.service_access_role.service_role_name, 'inherited': False}

        # Projects - each project's site also provides a "user" access for that site
        for service_access in self.user_group_services_access:
            if service_access.service_access_role.id_project:
                project_site = service_access.service_access_role.service_role_project.project_site
                if project_site not in sites_roles:
                    sites_roles[project_site] = {'site_role': 'user', 'inherited': True}

        return sites_roles

    @staticmethod
    def get_user_group_by_group_name(name: str):
        return TeraUserGroup.query.filter_by(user_group_name=name).first()

    @staticmethod
    def get_user_group_by_id(group_id: int):
        return TeraUserGroup.query.filter_by(id_user_group=group_id).first()

    @staticmethod
    def create_defaults(test=False):
        if test:
            from opentera.db.models.TeraProject import TeraProject
            from opentera.db.models.TeraServiceAccess import TeraServiceAccess
            from opentera.db.models.TeraServiceRole import TeraServiceRole
            from opentera.db.models.TeraService import TeraService
            from opentera.db.models.TeraSite import TeraSite

            opentera_service_id = TeraService.get_openteraserver_service().id_service

            ugroup = TeraUserGroup()
            ugroup.user_group_name = "Users - Projects 1 & 2"
            db.session.add(ugroup)

            ugroup = TeraUserGroup()
            ugroup.user_group_name = "Admins - Project 1"
            db.session.add(ugroup)

            ugroup = TeraUserGroup()
            ugroup.user_group_name = "Admins - Default Site"
            db.session.add(ugroup)

            ugroup = TeraUserGroup()
            ugroup.user_group_name = "Users - Project 1"
            db.session.add(ugroup)

            ugroup = TeraUserGroup()
            ugroup.user_group_name = "No access!"
            db.session.add(ugroup)

            db.session.commit()

            id_user_group = TeraUserGroup.get_user_group_by_group_name('Users - Projects 1 & 2').id_user_group
            access = TeraServiceAccess()
            access.id_user_group = id_user_group
            id_project = TeraProject.get_project_by_projectname('Default Project #1').id_project
            user_role = TeraServiceRole.get_specific_service_role_for_project(service_id=opentera_service_id,
                                                                              project_id=id_project, rolename='user')
            access.id_service_role = user_role.id_service_role
            db.session.add(access)

            access = TeraServiceAccess()
            access.id_user_group = id_user_group
            id_project = TeraProject.get_project_by_projectname('Default Project #2').id_project
            user_role = TeraServiceRole.get_specific_service_role_for_project(service_id=opentera_service_id,
                                                                              project_id=id_project, rolename='user')
            access.id_service_role = user_role.id_service_role
            db.session.add(access)

            admin_access = TeraServiceAccess()
            admin_role = TeraServiceRole.get_specific_service_role_for_site(service_id=opentera_service_id,
                                                                            site_id=TeraSite
                                                                            .get_site_by_sitename('Default Site').id_site,
                                                                            rolename='admin')
            admin_access.id_service_role = admin_role.id_service_role
            admin_access.id_user_group = TeraUserGroup.get_user_group_by_group_name('Admins - Default Site').id_user_group
            db.session.add(admin_access)

            access = TeraServiceAccess()
            access.id_user_group = TeraUserGroup.get_user_group_by_group_name('Admins - Project 1').id_user_group
            id_project = TeraProject.get_project_by_projectname('Default Project #1').id_project
            admin_role = TeraServiceRole.get_specific_service_role_for_project(service_id=opentera_service_id,
                                                                               project_id=id_project, rolename='admin')
            access.id_service_role = admin_role.id_service_role
            db.session.add(access)

            access = TeraServiceAccess()
            access.id_user_group = TeraUserGroup.get_user_group_by_group_name('Users - Project 1').id_user_group
            user_role = TeraServiceRole.get_specific_service_role_for_project(service_id=opentera_service_id,
                                                                              project_id=id_project, rolename='user')
            access.id_service_role = user_role.id_service_role
            db.session.add(access)

            db.session.commit()

