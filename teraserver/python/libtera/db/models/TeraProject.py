from libtera.db.Base import db, BaseModel
from libtera.db.models.TeraSite import TeraSite
from libtera.db.models.TeraProjectAccess import TeraProjectAccess


class TeraProject(db.Model, BaseModel):
    __tablename__ = 't_projects'
    id_project = db.Column(db.Integer, db.Sequence('id_project_sequence'), primary_key=True, autoincrement=True)
    id_site = db.Column(db.Integer, db.ForeignKey('t_sites.id_site'), nullable=False)
    project_name = db.Column(db.String, nullable=False, unique=False)

    project_site = db.relationship("TeraSite")

    def to_json(self, ignore_fields=None):
        if ignore_fields is None:
            ignore_fields = []
        ignore_fields.extend(['project_site'])
        rval = super().to_json(ignore_fields=ignore_fields)

        # Add sitename
        rval['site_name'] = self.project_site.site_name

        return rval

    def get_users_ids_in_project(self):
        # Get all users who has a role in the project
        users = self.get_users_in_project()
        users_ids = []

        for user in users:
            users_ids.append(user.id_user)

        return users_ids

    def get_users_in_project(self):
        # Get all users who has a role in the project
        project_access = TeraProjectAccess.query.filter(TeraProjectAccess.id_project == self.id_project).all()
        users = []
        for access in project_access:
            if access.project_access_user not in users:
                users.append(access.project_access_user)

        return users

    @staticmethod
    def create_defaults():
        base_project = TeraProject()
        base_project.project_name = 'Default Project #1'
        base_project.id_site = TeraSite.get_site_by_sitename('Default Site').id_site
        db.session.add(base_project)

        base_project2 = TeraProject()
        base_project2.project_name = 'Default Project #2'
        base_project2.id_site = TeraSite.get_site_by_sitename('Default Site').id_site
        db.session.add(base_project2)

        secret_project = TeraProject()
        secret_project.project_name = "Secret Project #1"
        secret_project.id_site = TeraSite.get_site_by_sitename('Top Secret Site').id_site
        db.session.add(secret_project)

        # Commit
        db.session.commit()

    @staticmethod
    def get_count():
        count = db.session.query(db.func.count(TeraProject.id_project))
        return count.first()[0]

    @staticmethod
    def get_project_by_projectname(projectname):
        return TeraProject.query.filter_by(project_name=projectname).first()

    @staticmethod
    def query_data(filter_args):
        if isinstance(filter_args, tuple):
            return TeraProject.query.filter_by(*filter_args).all()
        if isinstance(filter_args, dict):
            return TeraProject.query.filter_by(**filter_args).all()
        return None
