from libtera.db.Base import db, BaseModel


class TeraProjectAccess(db.Model, BaseModel):
    __tablename__ = 't_projects_access'
    id_project_access = db.Column(db.Integer, db.Sequence('id_project_access_sequence'), primary_key=True,
                                  autoincrement=True)
    id_project = db.Column(db.Integer, db.ForeignKey('t_projects.id_project'), nullable=False)
    id_user = db.Column(db.Integer, db.ForeignKey('t_users.id_user'), nullable=False)
    project_access_role = db.Column(db.String(100), nullable=False, unique=False)

    project_access_project = db.relationship('TeraProject')
    project_access_user = db.relationship('TeraUser')

    @staticmethod
    def get_count():
        count = db.session.query(db.func.count(TeraProjectAccess.id_project_access))
        return count.first()[0]

    @staticmethod
    def create_defaults():
        pass
