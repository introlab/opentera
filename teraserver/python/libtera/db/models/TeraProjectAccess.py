from libtera.db.Base import db, BaseModel
from libtera.db.models.TeraProject import TeraProject
from libtera.db.models.TeraUser import TeraUser


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
        role = TeraProjectAccess.query.filter_by(id_user=user.id_user, id_project=project.id_project).first()\
            .project_access_role
        return role

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
