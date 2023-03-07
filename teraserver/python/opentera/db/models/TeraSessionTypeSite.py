from opentera.db.Base import BaseModel
from opentera.db.models.TeraSessionTypeProject import TeraSessionTypeProject
from opentera.db.SoftDeleteMixin import SoftDeleteMixin
from opentera.db.SoftInsertMixin import SoftInsertMixin
from sqlalchemy import Column, ForeignKey, Integer, Sequence
from sqlalchemy.orm import relationship
from sqlalchemy.exc import IntegrityError


class TeraSessionTypeSite(BaseModel, SoftDeleteMixin, SoftInsertMixin):
    __tablename__ = 't_sessions_types_sites'
    id_session_type_site = Column(Integer, Sequence('id_session_type_site_sequence'), primary_key=True,
                                  autoincrement=True)
    id_session_type = Column('id_session_type', Integer, ForeignKey('t_sessions_types.id_session_type',
                                                                    ondelete='cascade'), nullable=False)
    id_site = Column('id_site', Integer, ForeignKey('t_sites.id_site', ondelete='cascade'), nullable=False)

    session_type_site_session_type = relationship("TeraSessionType", viewonly=True)
    session_type_site_site = relationship("TeraSite", viewonly=True)

    def to_json(self, ignore_fields=[], minimal=False):
        ignore_fields.extend(['session_type_site_session_type', 'session_type_site_site'])

        if minimal:
            ignore_fields.extend([])

        rval = super().to_json(ignore_fields=ignore_fields)

        return rval

    @staticmethod
    def create_defaults(test=False):
        if test:
            from opentera.db.models.TeraSessionType import TeraSessionType
            from opentera.db.models.TeraSite import TeraSite

            video_session = TeraSessionType.get_session_type_by_id(1)
            sensor_session = TeraSessionType.get_session_type_by_id(2)
            data_session = TeraSessionType.get_session_type_by_id(3)
            exerc_session = TeraSessionType.get_session_type_by_id(4)
            bureau_session = TeraSessionType.get_session_type_by_id(5)

            default_site = TeraSite.get_site_by_sitename('Default Site')
            secret_site = TeraSite.get_site_by_sitename('Top Secret Site')

            sts = TeraSessionTypeSite()
            sts.id_session_type = video_session.id_session_type
            sts.id_site = default_site.id_site
            TeraSessionTypeSite.db().session.add(sts)

            sts = TeraSessionTypeSite()
            sts.id_session_type = sensor_session.id_session_type
            sts.id_site = default_site.id_site
            TeraSessionTypeSite.db().session.add(sts)

            sts = TeraSessionTypeSite()
            sts.id_session_type = data_session.id_session_type
            sts.id_site = default_site.id_site
            TeraSessionTypeSite.db().session.add(sts)

            sts = TeraSessionTypeSite()
            sts.id_session_type = exerc_session.id_session_type
            sts.id_site = default_site.id_site
            TeraSessionTypeSite.db().session.add(sts)

            sts = TeraSessionTypeSite()
            sts.id_session_type = bureau_session.id_session_type
            sts.id_site = default_site.id_site
            TeraSessionTypeSite.db().session.add(sts)

            sts = TeraSessionTypeSite()
            sts.id_session_type = exerc_session.id_session_type
            sts.id_site = secret_site.id_site
            TeraSessionTypeSite.db().session.add(sts)

            TeraSessionTypeSite.db().session.commit()
        else:
            # Automatically associate session types that are in a project to that site
            from opentera.db.models.TeraSessionTypeProject import TeraSessionTypeProject
            for stp in TeraSessionTypeProject.query_with_filters():
                project_site_id = stp.session_type_project_project.id_site
                if not TeraSessionTypeSite.get_session_type_site_for_session_type_and_site(site_id=project_site_id,
                                                                                           session_type_id=
                                                                                           stp.id_session_type):
                    # No association - create a new one
                    st_site = TeraSessionTypeSite()
                    st_site.id_site = project_site_id
                    st_site.id_session_type = stp.id_session_type
                    TeraSessionTypeSite.db().session.add(st_site)
                    TeraSessionTypeSite.db().session.commit()

    @staticmethod
    def get_session_type_site_by_id(sts_id: int, with_deleted: bool = False):
        return TeraSessionTypeSite.query.execution_options(include_deleted=with_deleted)\
            .filter_by(id_session_type_site=sts_id).first()

    @staticmethod
    def get_sites_for_session_type(session_type_id: int, with_deleted: bool = False):
        return TeraSessionTypeSite.query.execution_options(include_deleted=with_deleted)\
            .filter_by(id_session_type=session_type_id).all()

    @staticmethod
    def get_sessions_types_for_site(site_id: int, with_deleted: bool = False):
        return TeraSessionTypeSite.query.execution_options(include_deleted=with_deleted)\
            .filter_by(id_site=site_id).all()

    @staticmethod
    def get_session_type_site_for_session_type_and_site(site_id: int, session_type_id: int, with_deleted: bool = False):
        return TeraSessionTypeSite.query.execution_options(include_deleted=with_deleted)\
            .filter_by(id_site=site_id, id_session_type=session_type_id).first()

    @staticmethod
    def get_session_type_site_for_site_and_service(site_id: int, service_id: int, with_deleted: bool = False):
        from opentera.db.models.TeraSessionType import TeraSessionType
        return TeraSessionTypeSite.query.execution_options(include_deleted=with_deleted).join(TeraSessionType). \
            filter(TeraSessionType.id_service == service_id). \
            filter(TeraSessionTypeSite.id_site == site_id).all()

    @staticmethod
    def check_integrity(obj_to_check):
        from opentera.db.models.TeraSessionType import TeraSessionType
        # If that session type is related to a service, make sure that the service is associated to that site
        if obj_to_check.session_type_site_session_type.session_type_category == \
                TeraSessionType.SessionCategoryEnum.SERVICE.value:
            service_sites = [site.id_site for site in
                             obj_to_check.session_type_site_session_type.session_type_service.service_sites]
            if obj_to_check.id_site not in service_sites:
                # We must also associate that service to that site!
                from opentera.db.models.TeraServiceSite import TeraServiceSite
                new_service_site = TeraServiceSite()
                new_service_site.id_service = obj_to_check.session_type_site_session_type \
                    .session_type_service.id_service
                new_service_site.id_site = obj_to_check.id_site
                TeraServiceSite.insert(new_service_site)

    @staticmethod
    def delete_with_ids(session_type_id: int, site_id: int, autocommit: bool = True):
        delete_obj: TeraSessionTypeSite = TeraSessionTypeSite.query.filter_by(id_session_type=session_type_id,
                                                                              id_site=site_id).first()
        if delete_obj:
            TeraSessionTypeSite.delete(delete_obj.id_session_type_site, autocommit=autocommit)

    @classmethod
    def delete(cls, id_todel, autocommit: bool = True):
        from opentera.db.models.TeraSessionTypeProject import TeraSessionTypeProject
        # Delete all association with projects for that site
        delete_obj = TeraSessionTypeSite.query.filter_by(id_session_type_site=id_todel).first()

        if delete_obj:
            projects = TeraSessionTypeProject.get_projects_for_session_type(delete_obj.id_session_type)
            for st_project in projects:
                if st_project.session_type_project_project.id_site == delete_obj.id_site:
                    TeraSessionTypeProject.delete(st_project.id_session_type_project, autocommit=autocommit)

            # Ok, delete it
            super().delete(id_todel, autocommit=autocommit)

    @classmethod
    def insert(cls, sts):
        inserted_obj = super().insert(sts)
        TeraSessionTypeSite.check_integrity(inserted_obj)
        return inserted_obj

    def delete_check_integrity(self) -> IntegrityError | None:
        for project in self.session_type_site_site.site_projects:
            ses_type_project = TeraSessionTypeProject.get_session_type_project_for_session_type_project(
                project.id_project, self.id_session_type)
            if ses_type_project:
                cannot_be_deleted_exception = ses_type_project.delete_check_integrity()
                if cannot_be_deleted_exception:
                    return IntegrityError('Still have sessions of that type in the site', self.id_session_type,
                                          't_sessions')
        return None

    @classmethod
    def update(cls, update_id: int, values: dict):
        return
