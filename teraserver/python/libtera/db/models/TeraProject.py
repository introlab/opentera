from libtera.db.Base import db, BaseModel


class TeraProject(db.Model, BaseModel):
    __tablename__ = 't_projects'
    id_project = db.Column(db.Integer, db.Sequence('id_project_sequence'), primary_key=True, autoincrement=True)
    project_name = db.Column(db.String, nullable=False, unique=False)


