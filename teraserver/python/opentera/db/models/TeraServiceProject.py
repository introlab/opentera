from opentera.db.Base import db, BaseModel
from sqlalchemy.exc import IntegrityError


class TeraServiceProject(db.Model, BaseModel):
    __tablename__ = 't_services_projects'
    id_service_project = db.Column(db.Integer, db.Sequence('id_service_project_sequence'), primary_key=True,
                                   autoincrement=True)
    id_service = db.Column(db.Integer, db.ForeignKey('t_services.id_service', ondelete='cascade'), nullable=False)
    id_project = db.Column(db.Integer, db.ForeignKey('t_projects.id_project', ondelete='cascade'), nullable=False)

    service_project_service = db.relationship("TeraService", viewonly=True)
    service_project_project = db.relationship("TeraProject", viewonly=True)

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

            servicefile = TeraService.get_service_by_key('FileTransferService')
            servicevideorehab = TeraService.get_service_by_key('VideoRehabService')

            service_project = TeraServiceProject()
            service_project.id_project = project1.id_project
            service_project.id_service = servicefile.id_service
            db.session.add(service_project)

            service_project = TeraServiceProject()
            service_project.id_project = project1.id_project
            service_project.id_service = servicevideorehab.id_service
            db.session.add(service_project)

            service_project = TeraServiceProject()
            service_project.id_project = project2.id_project
            service_project.id_service = servicefile.id_service
            db.session.add(service_project)

            service_project = TeraServiceProject()
            service_project.id_project = 3
            service_project.id_service = servicefile.id_service
            db.session.add(service_project)

            db.session.commit()

    @classmethod
    def insert(cls, stp):
        # Check if that site of that project has the site associated to it
        from opentera.db.models.TeraServiceSite import TeraServiceSite
        from opentera.db.models.TeraProject import TeraProject
        project = TeraProject.get_project_by_id(project_id=stp.id_project)
        service_site = TeraServiceSite.get_service_site_for_service_site(site_id=project.id_site,
                                                                         service_id=stp.id_service)
        if not service_site:
            raise IntegrityError(params='Service not associated to project site', orig='TeraServiceProject.insert',
                                 statement='insert')
        super().insert(stp)

    @classmethod
    def update(cls, update_id: int, values: dict):
        values = cls.clean_values(values)
        stp = cls.query.filter(getattr(cls, cls.get_primary_key_name()) == update_id).first()  # .update(values)
        stp.from_json(values)
        # Check if that site of that project has the site associated to it
        from opentera.db.models.TeraServiceSite import TeraServiceSite
        service_site = TeraServiceSite.get_service_site_for_service_site(site_id=stp.service_project_project.id_site,
                                                                         service_id=stp.id_service)
        if not service_site:
            raise IntegrityError(params='Service not associated to project site', orig='TeraServiceProject.update',
                                 statement='update')
        cls.commit()

    @staticmethod
    def delete_with_ids(service_id: int, project_id: int):
        delete_obj = TeraServiceProject.query.filter_by(id_service=service_id, id_project=project_id).first()
        if delete_obj:
            TeraServiceProject.delete(delete_obj.id_service_project)

    @classmethod
    def delete(cls, id_todel):
        from opentera.db.models.TeraSessionTypeProject import TeraSessionTypeProject
        # Delete all session type association to that project
        delete_obj: TeraServiceProject = TeraServiceProject.query.filter_by(id_service_project=id_todel).first()

        if delete_obj:
            session_types = TeraSessionTypeProject.get_session_type_project_for_project_and_service(
                project_id=delete_obj.id_project, service_id=delete_obj.id_service)
            for session_type in session_types:
                TeraSessionTypeProject.delete(session_type.id_session_type_project)

            # Ok, delete it
            super().delete(id_todel)
