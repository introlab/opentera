from opentera.db.Base import db, BaseModel


class TeraServiceProject(db.Model, BaseModel):
    __tablename__ = 't_services_projects'
    id_service_project = db.Column(db.Integer, db.Sequence('id_service_project_sequence'), primary_key=True,
                                   autoincrement=True)
    id_service = db.Column(db.Integer, db.ForeignKey('t_services.id_service', ondelete='cascade'), nullable=False)
    id_project = db.Column(db.Integer, db.ForeignKey('t_projects.id_project', ondelete='cascade'), nullable=False)

    service_project_service = db.relationship("TeraService")
    service_project_project = db.relationship("TeraProject")

    def __init__(self):
        pass

    def to_json(self, ignore_fields=None, minimal=False):
        if ignore_fields is None:
            ignore_fields = []

        ignore_fields.extend(['service_project_service', 'service_project_project'])

        if minimal:
            ignore_fields.extend([])

        return super().to_json(ignore_fields=ignore_fields)

    @staticmethod
    def get_services_for_project(id_project: int):
        return TeraServiceProject.query.filter_by(id_project=id_project).all()

    @staticmethod
    def get_projects_for_service(id_service: int):
        return TeraServiceProject.query.filter_by(id_service=id_service).all()

    @staticmethod
    def get_service_project_by_id(service_project_id: int):
        return TeraServiceProject.query.filter_by(id_service_project=service_project_id).first()

    @staticmethod
    def get_service_project_for_service_project(project_id: int, service_id: int):
        return TeraServiceProject.query.filter_by(id_project=project_id, id_service=service_id).first()

    @staticmethod
    def create_defaults(test=False):
        if test:
            from opentera.db.models.TeraService import TeraService
            from opentera.db.models.TeraProject import TeraProject

            project1 = TeraProject.get_project_by_projectname('Default Project #1')
            project2 = TeraProject.get_project_by_projectname('Default Project #2')

            servicebureau = TeraService.get_service_by_key('BureauActif')
            # serviceviddispatch = TeraService.get_service_by_key('VideoDispatch')
            servicevideorehab = TeraService.get_service_by_key('VideoRehabService')

            service_project = TeraServiceProject()
            service_project.id_project = project1.id_project
            service_project.id_service = servicebureau.id_service
            db.session.add(service_project)

            service_project = TeraServiceProject()
            service_project.id_project = project1.id_project
            service_project.id_service = servicevideorehab.id_service
            db.session.add(service_project)

            service_project = TeraServiceProject()
            service_project.id_project = project2.id_project
            service_project.id_service = servicebureau.id_service
            db.session.add(service_project)

            db.session.commit()

    @staticmethod
    def delete_with_ids(service_id: int, project_id: int):
        delete_obj = TeraServiceProject.query.filter_by(id_service=service_id, id_project=project_id).first()
        if delete_obj:
            db.session.delete(delete_obj)
            db.session.commit()
