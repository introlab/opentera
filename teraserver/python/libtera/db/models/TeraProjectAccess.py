from libtera.db.Base import db, BaseModel
from libtera.db.models.TeraProject import TeraProject
from libtera.db.models.TeraUser import TeraUser
from libtera.db.models.TeraSiteAccess import TeraSiteAccess


class TeraProjectAccess(db.Model, BaseModel):
    __tablename__ = 't_projects_access'
    id_project_access = db.Column(db.Integer, db.Sequence('id_project_access_sequence'), primary_key=True,
                                  autoincrement=True)
    id_project = db.Column(db.Integer, db.ForeignKey('t_projects.id_project'), nullable=False)
    id_user = db.Column(db.Integer, db.ForeignKey('t_users.id_user'), nullable=False)
    project_access_role = db.Column(db.String(100), nullable=False, unique=False)

    project_access_project = db.relationship('TeraProject')

    @staticmethod
    def get_count():
        count = db.session.query(db.func.count(TeraProjectAccess.id_project_access))
        return count.first()[0]

    @staticmethod
    def get_project_role_for_user(user: TeraUser, project: TeraProject):
        if user.user_superadmin:
            # SuperAdmin is always admin.
            return 'admin'

        role = TeraProjectAccess.query.filter_by(id_user=user.id_user, id_project=project.id_project).first()

        if role is not None:
            role_name = role.project_access_role
        else:
            # Site admins are always project admins
            site_role = TeraSiteAccess.get_site_role_for_user(user, project.project_site)
            if site_role == 'admin':
                role_name = 'admin'

        return role_name

    @staticmethod
    def get_accessible_projects_for_user(user: TeraUser):
        project_list = []
        if user.user_superadmin:
            # Is superadmin - admin on all projects
            project_list = TeraProject.query.all()
        else:
            # Build project list - get sites
            for site in TeraSiteAccess.get_accessible_sites_for_user(user):
                if TeraSiteAccess.get_site_role_for_user(user, site) == 'admin':
                    project_query = TeraProject.query.filter_by(id_site=site.id_site)
                    if project_query:
                        for project in project_query.all():
                            project_list.append(project)

            # Add specific projects
            for project_access in user.user_projects_access:
                project = project_access.project_access_project
                if project not in project_list:
                    project_list.append(project)
        return project_list

    @staticmethod
    def get_accessible_projects_ids_for_user(user: TeraUser):
        projects = []

        for project in TeraProjectAccess.get_accessible_projects_for_user(user):
            projects.append(project.id_project)

        return projects

    @staticmethod
    def get_projects_roles_for_user(user: TeraUser):
        projects_roles = {}
        project_list = TeraProjectAccess.get_accessible_projects_for_user(user)

        for project in project_list:
            role = TeraProjectAccess.get_project_role_for_user(user, project)
            projects_roles[project.project_name] = role
        return projects_roles

    @staticmethod
    def create_defaults():
        admin_access = TeraProjectAccess()
        admin_access.id_user = TeraUser.get_user_by_username('siteadmin').id_user
        admin_access.id_project = TeraProject.get_project_by_projectname('Default Project #1').id_project
        admin_access.project_access_role = 'admin'
        db.session.add(admin_access)

        user_access = TeraProjectAccess()
        user_access.id_user = TeraUser.get_user_by_username('user').id_user
        user_access.id_project = TeraProject.get_project_by_projectname('Default Project #1').id_project
        user_access.project_access_role = 'user'
        db.session.add(user_access)

        user2_access = TeraProjectAccess()
        user2_access.id_user = TeraUser.get_user_by_username('user2').id_user
        user2_access.id_project = TeraProject.get_project_by_projectname('Default Project #1').id_project
        user2_access.project_access_role = 'user'
        db.session.add(user2_access)

        user2_access_admin = TeraProjectAccess()
        user2_access_admin.id_user = TeraUser.get_user_by_username('user2').id_user
        user2_access_admin.id_project = TeraProject.get_project_by_projectname('Default Project #2').id_project
        user2_access_admin.project_access_role = 'admin'
        db.session.add(user2_access_admin)

        db.session.commit()
