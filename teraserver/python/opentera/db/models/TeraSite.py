from opentera.db.Base import BaseModel
from opentera.db.SoftDeleteMixin import SoftDeleteMixin
from sqlalchemy import Column, ForeignKey, Integer, String, Sequence, Boolean, TIMESTAMP
from sqlalchemy.orm import relationship


class TeraSite(BaseModel, SoftDeleteMixin):
    __tablename__ = 't_sites'
    id_site = Column(Integer, Sequence('id_site_sequence'), primary_key=True, autoincrement=True)
    site_name = Column(String, nullable=False)

    site_devices = relationship("TeraDevice", secondary="t_devices_sites", back_populates="device_sites")
    site_projects = relationship("TeraProject", cascade="delete", passive_deletes=True,
                                    back_populates='project_site', lazy='joined')

    def to_json(self, ignore_fields=None, minimal=False):
        if ignore_fields is None:
            ignore_fields = []

        ignore_fields.extend(['site_projects', 'site_devices'])

        return super().to_json(ignore_fields=ignore_fields)

    def to_json_create_event(self):
        return self.to_json(minimal=True)

    def to_json_update_event(self):
        return self.to_json(minimal=True)

    def to_json_delete_event(self):
        # Minimal information, delete can not be filtered
        return {'id_site': self.id_site}

    @staticmethod
    def create_defaults(test=False):
        base_site = TeraSite()
        base_site.site_name = 'Default Site'
        TeraSite.insert(base_site)

        if test:
            base_site = TeraSite()
            base_site.site_name = 'Top Secret Site'
            TeraSite.insert(base_site)

    @staticmethod
    def get_site_by_sitename(sitename):
        return TeraSite.query.filter_by(site_name=sitename).first()

    @staticmethod
    def get_site_by_id(site_id: int):
        return TeraSite.query.filter_by(id_site=site_id).first()

    # @staticmethod
    # def query_data(filter_args):
    #     if isinstance(filter_args, tuple):
    #         return TeraSite.query.filter_by(*filter_args).all()
    #     if isinstance(filter_args, dict):
    #         return TeraSite.query.filter_by(**filter_args).all()
    #     return None

    @classmethod
    def insert(cls, site):
        # Creates admin and user roles for that site
        super().insert(site)

        from opentera.db.models.TeraServiceRole import TeraServiceRole
        from opentera.db.models.TeraService import TeraService
        opentera_service_id = TeraService.get_openteraserver_service().id_service
        access_role = TeraServiceRole()
        access_role.id_service = opentera_service_id
        access_role.id_site = site.id_site
        access_role.service_role_name = 'admin'
        TeraServiceRole.insert(access_role)

        access_role = TeraServiceRole()
        access_role.id_service = opentera_service_id
        access_role.id_site = site.id_site
        access_role.service_role_name = 'user'
        TeraServiceRole.insert(access_role)
