from libtera.db.Base import db, BaseModel
from libtera.db.models.TeraSite import TeraSite


class TeraProject(db.Model, BaseModel):
    __tablename__ = 't_projects'
    id_project = db.Column(db.Integer, db.Sequence('id_project_sequence'), primary_key=True, autoincrement=True)
    id_site = db.Column(db.Integer, db.ForeignKey('t_sites.id_site'), nullable=False)
    project_name = db.Column(db.String, nullable=False, unique=False)

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
