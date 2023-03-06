from opentera.db.Base import BaseModel
from opentera.db.SoftDeleteMixin import SoftDeleteMixin
from opentera.db.SoftInsertMixin import SoftInsertMixin
from sqlalchemy import Column, ForeignKey, Integer, String, Sequence, Boolean, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.exc import IntegrityError


class TeraDeviceSite(BaseModel, SoftDeleteMixin, SoftInsertMixin):
    __tablename__ = 't_devices_sites'
    id_device_site = Column(Integer, Sequence('id_device_site_sequence'), primary_key=True, autoincrement=True)
    id_device = Column(Integer, ForeignKey("t_devices.id_device", ondelete='cascade'), nullable=False)
    id_site = Column(Integer, ForeignKey("t_sites.id_site", ondelete='cascade'), nullable=False)

    device_site_site = relationship("TeraSite", viewonly=True)
    device_site_device = relationship("TeraDevice", viewonly=True)

    def to_json(self, ignore_fields=[], minimal=False):
        ignore_fields.extend(['device_site_site', 'device_site_device'])

        if minimal:
            ignore_fields.extend([])

        rval = super().to_json(ignore_fields=ignore_fields)

        return rval

    @staticmethod
    def create_defaults(test=False):
        if test:
            from opentera.db.models.TeraDevice import TeraDevice
            from opentera.db.models.TeraSite import TeraSite

            device1 = TeraDevice.get_device_by_name('Apple Watch #W05P1')
            device2 = TeraDevice.get_device_by_name('Kit Télé #1')
            # device3 = TeraDevice.get_device_by_name('Robot A')

            default_site = TeraSite.get_site_by_sitename('Default Site')
            secret_site = TeraSite.get_site_by_sitename('Top Secret Site')

            dev_site = TeraDeviceSite()
            dev_site.id_device = device1.id_device
            dev_site.id_site = default_site.id_site
            TeraDeviceSite.db().session.add(dev_site)

            dev_site = TeraDeviceSite()
            dev_site.id_device = device2.id_device
            dev_site.id_site = default_site.id_site
            TeraDeviceSite.db().session.add(dev_site)

            dev_site = TeraDeviceSite()
            dev_site.id_device = device1.id_device
            dev_site.id_site = secret_site.id_site
            TeraDeviceSite.db().session.add(dev_site)

            TeraDeviceSite.db().session.commit()
        else:
            # Automatically associate devices that are in a project to that site
            from opentera.db.models.TeraDeviceProject import TeraDeviceProject
            for dp in TeraDeviceProject.query_with_filters():
                project_site_id = dp.device_project_project.id_site
                if not TeraDeviceSite.get_device_site_id_for_device_and_site(site_id=project_site_id,
                                                                             device_id=
                                                                             dp.device_project_device.id_device):
                    # No association - create a new one
                    device_site = TeraDeviceSite()
                    device_site.id_site = project_site_id
                    device_site.id_device = dp.device_project_device.id_device
                    TeraDeviceSite.db().session.add(device_site)
                    TeraDeviceSite.db().session.commit()

    @staticmethod
    def get_device_site_by_id(device_site_id: int, with_deleted: bool = False):
        return TeraDeviceSite.query.execution_options(include_deleted=with_deleted)\
            .filter_by(id_device_site=device_site_id).first()

    @staticmethod
    def get_device_site_id_for_device_and_site(device_id: int, site_id: int, with_deleted: bool = False):
        return TeraDeviceSite.query.execution_options(include_deleted=with_deleted)\
            .filter_by(id_site=site_id, id_device=device_id).first()

    @staticmethod
    def get_devices_for_site(site_id: int, with_deleted: bool = False):
        return TeraDeviceSite.query.execution_options(include_deleted=with_deleted)\
            .filter_by(id_site=site_id).all()

    @staticmethod
    def get_sites_for_device(device_id: int, with_deleted: bool = False):
        return TeraDeviceSite.query.execution_options(include_deleted=with_deleted)\
            .filter_by(id_device=device_id).all()

    @staticmethod
    def delete_with_ids(device_id: int, site_id: int, autocommit: bool = True):
        delete_obj: TeraDeviceSite = TeraDeviceSite.query.filter_by(id_device=device_id, id_site=site_id).first()
        if delete_obj:
            TeraDeviceSite.delete(delete_obj.id_device_site, autocommit=autocommit)

    @classmethod
    def delete(cls, id_todel, autocommit: bool = True):
        from opentera.db.models.TeraDeviceProject import TeraDeviceProject

        delete_obj = TeraDeviceSite.query.filter_by(id_device_site=id_todel).first()
        if delete_obj:
            # Needed for device-project deletion later
            id_site = delete_obj.id_site
            id_device = delete_obj.id_device
            # Ok, delete it (will check integrity)
            super().delete(id_todel, autocommit)

            # Delete all association with projects for that site
            from opentera.db.models.TeraProject import TeraProject
            specific_device_projects = TeraDeviceProject.query.join(TeraProject). \
                filter(TeraDeviceProject.id_device == id_device).\
                filter(TeraProject.id_site == id_site).all()

            for device_project in specific_device_projects:
                TeraDeviceProject.delete(device_project.id_device_project, autocommit=autocommit)

    def delete_check_integrity(self) -> IntegrityError | None:
        from opentera.db.models.TeraDeviceProject import TeraDeviceProject
        from opentera.db.models.TeraProject import TeraProject

        # Will check if device is part of a project in the site
        specific_device_projects = TeraDeviceProject.query.join(TeraProject).\
            filter(TeraDeviceProject.id_device == self.id_device).filter(TeraProject.id_site == self.id_site).all()

        # Check integrity of device_projects
        for device_project in specific_device_projects:
            integrity_check = device_project.delete_check_integrity()
            if integrity_check is not None:
                return integrity_check

        # Everything is good
        return None

    @classmethod
    def update(cls, update_id: int, values: dict):
        return
