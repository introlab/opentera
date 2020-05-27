from libtera.db.Base import db, BaseModel


class TeraUserGroup(db.Model, BaseModel):
    __tablename__ = 't_users_groups'
    id_user_group = db.Column(db.Integer, db.Sequence('id_usergroup_sequence'), primary_key=True, autoincrement=True)
    user_group_name = db.Column(db.String, nullable=False, unique=False)

    user_group_sites_access = db.relationship('TeraSiteAccess', cascade="all,delete")
    user_group_projects_access = db.relationship("TeraProjectAccess", cascade="all,delete")
    user_group_users = db.relationship("TeraUser", secondary="t_users_users_groups", back_populates="user_user_groups")

    def to_json(self, ignore_fields=None, minimal=False):
        if ignore_fields is None:
            ignore_fields = []
        ignore_fields.extend(['user_group_users', 'user_group_sites_access', 'user_group_projects_access'])
        if minimal:
            ignore_fields.extend([])
        rval = super().to_json(ignore_fields=ignore_fields)

        return rval

    def get_projects_roles(self) -> dict:
        projects_roles = {}

        # Projects
        for project_access in self.user_group_projects_access:
            current_project_role = project_access.project_access_role
            projects_roles[project_access.project_access_project] = current_project_role

        # Sites - if we are admin in a site, we are automatically admin in all its project
        for site_access in self.user_group_sites_access:
            if site_access.site_access_role == 'admin':
                for project in site_access.site_access_site.site_projects:
                    projects_roles[project] = 'admin'

        return projects_roles

    def get_sites_roles(self) -> dict:
        sites_roles = {}
        # Sites
        for site_access in self.user_group_sites_access:
            sites_roles[site_access.site_access_site] = site_access.site_access_role

        # Projects - each project's site also provides a "user" access for that site
        for project_access in self.user_group_projects_access:
            if project_access.project_access_project.project_site not in sites_roles:
                sites_roles[project_access.project_access_project.project_site] = 'user'

        return sites_roles

    @staticmethod
    def get_user_group_by_group_name(name: str):
        return TeraUserGroup.query.filter_by(user_group_name=name).first()

    @staticmethod
    def get_user_group_by_id(group_id: int):
        return TeraUserGroup.query.filter_by(id_user_group=group_id).first()

    @staticmethod
    def create_defaults():
        from libtera.db.models.TeraProjectAccess import TeraProjectAccess
        from libtera.db.models.TeraProject import TeraProject
        from libtera.db.models.TeraSiteAccess import TeraSiteAccess
        from libtera.db.models.TeraSite import TeraSite

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
        db.session.commit()

        access = TeraProjectAccess()
        access.id_user_group = TeraUserGroup.get_user_group_by_group_name('Users - Projects 1 & 2').id_user_group
        access.id_project = TeraProject.get_project_by_projectname('Default Project #1').id_project
        access.project_access_role = 'user'
        db.session.add(access)
        access = TeraProjectAccess()
        access.id_user_group = TeraUserGroup.get_user_group_by_group_name('Users - Projects 1 & 2').id_user_group
        access.id_project = TeraProject.get_project_by_projectname('Default Project #2').id_project
        access.project_access_role = 'user'
        db.session.add(access)

        admin_access = TeraSiteAccess()
        admin_access.id_user_group = TeraUserGroup.get_user_group_by_group_name('Admins - Default Site').id_user_group
        admin_access.id_site = TeraSite.get_site_by_sitename('Default Site').id_site
        admin_access.site_access_role = 'admin'
        db.session.add(admin_access)

        access = TeraProjectAccess()
        access.id_user_group = TeraUserGroup.get_user_group_by_group_name('Admins - Project 1').id_user_group
        access.id_project = TeraProject.get_project_by_projectname('Default Project #1').id_project
        access.project_access_role = 'admin'
        db.session.add(access)

        access = TeraProjectAccess()
        access.id_user_group = TeraUserGroup.get_user_group_by_group_name('Users - Project 1').id_user_group
        access.id_project = TeraProject.get_project_by_projectname('Default Project #1').id_project
        access.project_access_role = 'user'
        db.session.add(access)

        db.session.commit()

