from opentera.db.Base import BaseModel
from opentera.db.SoftDeleteMixin import SoftDeleteMixin
from opentera.db.SoftInsertMixin import SoftInsertMixin
from opentera.db.models.TeraSessionType import TeraSessionType
from opentera.db.models.TeraSessionTypeProject import TeraSessionTypeProject
from opentera.db.models.TeraTestTypeProject import TeraTestTypeProject
from opentera.db.models.TeraTestType import TeraTestType
from opentera.db.models.TeraTest import TeraTest
from opentera.db.models.TeraSession import TeraSession
from opentera.db.models.TeraAsset import TeraAsset
from sqlalchemy import Column, ForeignKey, Integer, Sequence, or_
from sqlalchemy.orm import relationship
from sqlalchemy.exc import IntegrityError


class TeraServiceProject(BaseModel, SoftDeleteMixin, SoftInsertMixin):
    __tablename__ = 't_services_projects'
    id_service_project = Column(Integer, Sequence('id_service_project_sequence'), primary_key=True, autoincrement=True)
    id_service = Column(Integer, ForeignKey('t_services.id_service', ondelete='cascade'), nullable=False)
    id_project = Column(Integer, ForeignKey('t_projects.id_project', ondelete='cascade'), nullable=False)

    service_project_service = relationship("TeraService", viewonly=True)
    service_project_project = relationship("TeraProject", viewonly=True)

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
    def get_services_for_project(id_project: int, with_deleted: bool = False):
        return TeraServiceProject.query.execution_options(include_deleted=with_deleted)\
            .filter_by(id_project=id_project).all()

    @staticmethod
    def get_projects_for_service(id_service: int, with_deleted: bool = False):
        return TeraServiceProject.query.execution_options(include_deleted=with_deleted)\
            .filter_by(id_service=id_service).all()

    @staticmethod
    def get_service_project_by_id(service_project_id: int, with_deleted: bool = False):
        return TeraServiceProject.query.execution_options(include_deleted=with_deleted)\
            .filter_by(id_service_project=service_project_id).first()

    @staticmethod
    def get_service_project_for_service_project(project_id: int, service_id: int, with_deleted: bool = False):
        return TeraServiceProject.query.execution_options(include_deleted=with_deleted)\
            .filter_by(id_project=project_id, id_service=service_id).first()

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
            TeraServiceProject.db().session.add(service_project)

            service_project = TeraServiceProject()
            service_project.id_project = project1.id_project
            service_project.id_service = servicevideorehab.id_service
            TeraServiceProject.db().session.add(service_project)

            service_project = TeraServiceProject()
            service_project.id_project = project2.id_project
            service_project.id_service = servicefile.id_service
            TeraServiceProject.db().session.add(service_project)

            service_project = TeraServiceProject()
            service_project.id_project = 3
            service_project.id_service = servicefile.id_service
            TeraServiceProject.db().session.add(service_project)

            TeraServiceProject.db().session.commit()

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
        return super().insert(stp)

    @classmethod
    def update(cls, update_id: int, values: dict):
        return

    @staticmethod
    def delete_with_ids(service_id: int, project_id: int, autocommit: bool = True):
        delete_obj = TeraServiceProject.query.filter_by(id_service=service_id, id_project=project_id).first()
        if delete_obj:
            TeraServiceProject.delete(delete_obj.id_service_project, autocommit=autocommit)

    def delete_check_integrity(self) -> IntegrityError | None:
        # This check will be quite long to process with lot of sessions and data...
        session_types_ids = \
            [st.id_session_type for st in TeraSessionType.get_session_types_for_service(self.id_service)]

        sessions = TeraSession.get_sessions_for_project(self.id_project)
        for session in sessions:
            if session.id_session_type in session_types_ids:
                return IntegrityError('Service has sessions of related session type in this project', self.id_service,
                                      't_sessions')
            if TeraTest.query.join(TeraTestType).filter(TeraTest.id_session == session.id_session).\
                    filter(or_(TeraTest.id_service == self.id_service, TeraTestType.id_service == self.id_service))\
                    .count() > 0:
                return IntegrityError('Service has tests of related test type in this project', self.id_service,
                                      't_tests')
            if TeraAsset.query.filter_by(id_session=session.id_session).\
                filter(or_(TeraAsset.asset_service_uuid == self.service_project_service.service_uuid,
                           TeraAsset.id_service == self.id_service)).count() > 0:
                return IntegrityError('Service has related assets in this project', self.id_service, 't_assets')
        return None

    @classmethod
    def delete(cls, id_todel, autocommit: bool = True):
        # Delete all session type association to that project
        delete_obj: TeraServiceProject = TeraServiceProject.query.filter_by(id_service_project=id_todel).first()

        if delete_obj:
            session_types = TeraSessionTypeProject.get_session_type_project_for_project_and_service(
                project_id=delete_obj.id_project, service_id=delete_obj.id_service)
            for session_type in session_types:
                TeraSessionTypeProject.delete(session_type.id_session_type_project, autocommit=autocommit)

            test_types = TeraTestTypeProject.get_test_type_project_for_project_and_service(
                project_id=delete_obj.id_project, service_id=delete_obj.id_service)
            for test_type in test_types:
                TeraTestTypeProject.delete(test_type.id_test_type_project, autocommit=autocommit)

            # Ok, delete it
            super().delete(id_todel, autocommit=autocommit)
