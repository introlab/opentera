from opentera.db.Base import BaseModel
from opentera.db.models.TeraSession import TeraSession
from opentera.db.models.TeraSessionType import TeraSessionType
from opentera.db.models.TeraSessionTypeSite import TeraSessionTypeSite
from opentera.db.models.TeraSessionTypeProject import TeraSessionTypeProject
from opentera.db.models.TeraServiceSite import TeraServiceSite
from opentera.db.models.TeraServiceProject import TeraServiceProject
from opentera.db.models.TeraService import TeraService
from opentera.db.SoftDeleteMixin import SoftDeleteMixin
from opentera.db.SoftInsertMixin import SoftInsertMixin
from sqlalchemy import Column, ForeignKey, Integer, Sequence
from sqlalchemy.orm import relationship
from sqlalchemy.exc import IntegrityError


class TeraSessionTypeServices(BaseModel, SoftDeleteMixin, SoftInsertMixin):
    __tablename__ = 't_sessions_types_services'
    id_session_type_service = Column(Integer, Sequence('id_session_type_service_sequence'), primary_key=True,
                                     autoincrement=True)
    id_session_type = Column('id_session_type', Integer, ForeignKey('t_sessions_types.id_session_type',
                                                                    ondelete='cascade'), nullable=False)
    id_service = Column('id_service', Integer, ForeignKey('t_services.id_service', ondelete='cascade'),
                        nullable=False)

    session_type_service_session_type = relationship("TeraSessionType", viewonly=True)
    session_type_service_service = relationship("TeraService", viewonly=True)

    def to_json(self, ignore_fields=None, minimal=False):
        if ignore_fields is None:
            ignore_fields = []
        ignore_fields.extend(['session_type_service_session_type', 'session_type_service_service'])

        if minimal:
            ignore_fields.extend([])

        rval = super().to_json(ignore_fields=ignore_fields)

        return rval

    def to_json_create_event(self):
        json_data = self.to_json(minimal=True)
        # Query session type information
        session_type = TeraSessionType.get_session_type_by_id(self.id_session_type)
        if session_type:
            json_data['session_type_id_service'] = session_type.id_service
        return json_data

    def to_json_update_event(self):
        json_data = self.to_json(minimal=True)
        json_data['session_type_id_service'] = self.session_type_service_session_type.id_service
        return json_data

    def to_json_delete_event(self):
        # Minimal information, delete can not be filtered
        return {'id_session_type_service': self.id_session_type_service}

    @staticmethod
    def create_defaults(test=False):
        if test:
            from opentera.db.models.TeraSessionType import TeraSessionType
            data_session = TeraSessionType.get_session_type_by_id(3)
            secondary_service = TeraService.get_service_by_key("FileTransferService")

            sts = TeraSessionTypeServices()
            sts.id_session_type = data_session.id_session_type
            sts.id_service = secondary_service.id_service
            TeraSessionTypeServices.db().session.add(sts)

            TeraSessionTypeServices.db().session.commit()

    @staticmethod
    def get_session_type_service_by_id(sts_id: int, with_deleted: bool = False):
        return TeraSessionTypeServices.query.execution_options(include_deleted=with_deleted)\
            .filter_by(id_session_type_service=sts_id).first()

    @staticmethod
    def get_services_for_session_type(session_type_id: int, with_deleted: bool = False):
        return TeraSessionTypeServices.query.execution_options(include_deleted=with_deleted)\
            .filter_by(id_session_type=session_type_id).all()

    @staticmethod
    def get_sessions_types_for_service(service_id: int, with_deleted: bool = False):
        return TeraSessionTypeServices.query.execution_options(include_deleted=with_deleted)\
            .filter_by(id_service=service_id).all()

    @staticmethod
    def check_integrity(obj_to_check):
        # Make sure service is associated to sites of that session type
        session_type_sites = TeraSessionTypeSite.get_sites_for_session_type(obj_to_check.id_session_type)
        for site in session_type_sites:
            association = TeraServiceSite.get_service_site_for_service_site(site.id_site, obj_to_check.id_service)
            if not association:
                # Associate service to site
                new_service_site = TeraServiceSite()
                new_service_site.id_service = obj_to_check.id_service
                new_service_site.id_site = site.id_site
                TeraServiceSite.insert(new_service_site)

        # Make sure service is associated to projects of that session type
        session_types_projects = TeraSessionTypeProject.get_projects_for_session_type(obj_to_check.id_session_type)
        for project in session_types_projects:
            association = TeraServiceProject.get_service_project_for_service_project(project.id_project,
                                                                                     obj_to_check.id_service)
            if not association:
                # Associate service to project
                new_service_project = TeraServiceProject()
                new_service_project.id_service = obj_to_check.id_service
                new_service_project.id_project = project.id_project
                TeraServiceProject.insert(new_service_project)

    @staticmethod
    def delete_with_ids(session_type_id: int, service_id: int, autocommit: bool = True):
        delete_obj: TeraSessionTypeServices = TeraSessionTypeServices.query.filter_by(id_session_type=session_type_id,
                                                                                      id_service=service_id).first()
        if delete_obj:
            TeraSessionTypeServices.delete(delete_obj.id_session_type_service, autocommit=autocommit)

    def delete_check_integrity(self, with_deleted: bool = False) -> IntegrityError | None:
        sessions_count = TeraSession.get_count({'id_session_type': self.id_session_type}, with_deleted=with_deleted)
        if sessions_count > 0:
            return IntegrityError('Session type has sessions', self.id_session_type, 't_sessions')
        return None

    @classmethod
    def insert(cls, sts):
        inserted_obj = super().insert(sts)
        TeraSessionTypeServices.check_integrity(inserted_obj)
        return inserted_obj

    @classmethod
    def update(cls, update_id: int, values: dict):
        return
