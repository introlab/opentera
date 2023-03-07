from opentera.db.Base import BaseModel
from opentera.db.models.TeraSession import TeraSession
from opentera.db.SoftDeleteMixin import SoftDeleteMixin
from opentera.db.SoftInsertMixin import SoftInsertMixin
from sqlalchemy import Column, ForeignKey, Integer, Sequence
from sqlalchemy.orm import relationship
from sqlalchemy.exc import IntegrityError


class TeraSessionTypeProject(BaseModel, SoftDeleteMixin, SoftInsertMixin):
    __tablename__ = 't_sessions_types_projects'
    id_session_type_project = Column(Integer, Sequence('id_session_type_project_sequence'), primary_key=True,
                                     autoincrement=True)
    id_session_type = Column('id_session_type', Integer, ForeignKey('t_sessions_types.id_session_type',
                                                                    ondelete='cascade'), nullable=False)
    id_project = Column('id_project', Integer, ForeignKey('t_projects.id_project', ondelete='cascade'),
                        nullable=False)

    session_type_project_session_type = relationship("TeraSessionType", viewonly=True)
    session_type_project_project = relationship("TeraProject", viewonly=True)

    def to_json(self, ignore_fields=[], minimal=False):
        ignore_fields.extend(['session_type_project_session_type', 'session_type_project_project'])

        if minimal:
            ignore_fields.extend([])

        rval = super().to_json(ignore_fields=ignore_fields)

        return rval

    @staticmethod
    def create_defaults(test=False):
        if test:
            from opentera.db.models.TeraSessionType import TeraSessionType
            from opentera.db.models.TeraProject import TeraProject

            video_session = TeraSessionType.get_session_type_by_id(1)
            sensor_session = TeraSessionType.get_session_type_by_id(2)
            data_session = TeraSessionType.get_session_type_by_id(3)
            exerc_session = TeraSessionType.get_session_type_by_id(4)
            bureau_session = TeraSessionType.get_session_type_by_id(5)

            project = TeraProject.get_project_by_projectname('Default Project #1')

            stp = TeraSessionTypeProject()
            stp.id_session_type = video_session.id_session_type
            stp.id_project = project.id_project
            TeraSessionTypeProject.db().session.add(stp)

            stp = TeraSessionTypeProject()
            stp.id_session_type = sensor_session.id_session_type
            stp.id_project = project.id_project
            TeraSessionTypeProject.db().session.add(stp)

            stp = TeraSessionTypeProject()
            stp.id_session_type = data_session.id_session_type
            stp.id_project = project.id_project
            TeraSessionTypeProject.db().session.add(stp)

            stp = TeraSessionTypeProject()
            stp.id_session_type = exerc_session.id_session_type
            stp.id_project = project.id_project
            TeraSessionTypeProject.db().session.add(stp)

            stp = TeraSessionTypeProject()
            stp.id_session_type = bureau_session.id_session_type
            stp.id_project = project.id_project
            TeraSessionTypeProject.db().session.add(stp)

            TeraSessionTypeProject.db().session.commit()

    @staticmethod
    def get_session_type_project_by_id(stp_id: int, with_deleted: bool = False):
        return TeraSessionTypeProject.query.execution_options(include_deleted=with_deleted)\
            .filter_by(id_session_type_project=stp_id).first()

    @staticmethod
    def get_projects_for_session_type(session_type_id: int, with_deleted: bool = False):
        return TeraSessionTypeProject.query.execution_options(include_deleted=with_deleted)\
            .filter_by(id_session_type=session_type_id).all()

    @staticmethod
    def get_sessions_types_for_project(project_id: int, with_deleted: bool = False):
        return TeraSessionTypeProject.query.execution_options(include_deleted=with_deleted)\
            .filter_by(id_project=project_id).all()

    @staticmethod
    def get_session_type_project_for_session_type_project(project_id: int, session_type_id: int,
                                                          with_deleted: bool = False):
        return TeraSessionTypeProject.query.execution_options(include_deleted=with_deleted)\
            .filter_by(id_project=project_id, id_session_type=session_type_id).first()

    @staticmethod
    def get_session_type_project_for_project_and_service(project_id: int, service_id: int, with_deleted: bool = False):
        from opentera.db.models.TeraSessionType import TeraSessionType
        return TeraSessionTypeProject.query.execution_options(include_deleted=with_deleted).join(TeraSessionType).\
            filter(TeraSessionType.id_service == service_id).\
            filter(TeraSessionTypeProject.id_project == project_id).all()

    @staticmethod
    def delete_with_ids(session_type_id: int, project_id: int, autocommit: bool = True):
        delete_obj: TeraSessionTypeProject = TeraSessionTypeProject.query.filter_by(id_session_type=session_type_id,
                                                                                    id_project=project_id).first()
        if delete_obj:
            TeraSessionTypeProject.delete(delete_obj.id_session_type_project, autocommit=autocommit)

    @staticmethod
    def check_integrity(obj_to_check):
        from opentera.db.models.TeraSessionType import TeraSessionType
        # If that session type is related to a service, make sure that the service is associated to that project
        if obj_to_check.session_type_project_session_type.session_type_category == \
                TeraSessionType.SessionCategoryEnum.SERVICE.value:
            service_projects = [proj.id_project for proj in
                                obj_to_check.session_type_project_session_type.session_type_service.service_projects]
            if obj_to_check.id_project not in service_projects:
                # We must also associate that service to that project!
                from opentera.db.models.TeraServiceProject import TeraServiceProject
                new_service_project = TeraServiceProject()
                new_service_project.id_service = obj_to_check.session_type_project_session_type \
                    .session_type_service.id_service
                new_service_project.id_project = obj_to_check.session_type_project_project.id_project
                TeraServiceProject.insert(new_service_project)

    def delete_check_integrity(self) -> IntegrityError | None:
        sessions = TeraSession.get_sessions_for_project(project_id=self.id_project,
                                                        session_type_id=self.id_session_type)
        if len(sessions) > 0:
            return IntegrityError('Session type has sessions in this project', self.id_session_type, 't_sessions')
        return None

    @classmethod
    def insert(cls, stp):
        # Check if that site of that project has the site associated to it
        from opentera.db.models.TeraSessionTypeSite import TeraSessionTypeSite
        from opentera.db.models.TeraProject import TeraProject
        project = TeraProject.get_project_by_id(project_id=stp.id_project)
        st_site = TeraSessionTypeSite.get_session_type_site_for_session_type_and_site(site_id=project.id_site,
                                                                                      session_type_id=
                                                                                      stp.id_session_type)
        if not st_site:
            raise IntegrityError(params='Session type not associated to project site',
                                 orig='TeraSessionTypeProject.insert', statement='insert')
        inserted_obj = super().insert(stp)
        TeraSessionTypeProject.check_integrity(inserted_obj)
        return inserted_obj

    @classmethod
    def update(cls, update_id: int, values: dict):
        return
