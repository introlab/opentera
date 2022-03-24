from opentera.db.Base import db, BaseModel


class TeraDeviceSite(db.Model, BaseModel):
    __tablename__ = 't_devices_sites'
    id_device_site = db.Column(db.Integer, db.Sequence('id_device_site_sequence'), primary_key=True, autoincrement=True)
    id_device = db.Column(db.Integer, db.ForeignKey("t_devices.id_device", ondelete='cascade'), nullable=False)
    id_site = db.Column(db.Integer, db.ForeignKey("t_sites.id_site", ondelete='cascade'), nullable=False)

    device_site_site = db.relationship("TeraSite", viewonly=True)
    device_site_device = db.relationship("TeraDevice", viewonly=True)

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
            db.session.add(dev_site)

            dev_site = TeraDeviceSite()
            dev_site.id_device = device2.id_device
            dev_site.id_site = default_site.id_site
            db.session.add(dev_site)

            dev_site = TeraDeviceSite()
            dev_site.id_device = device1.id_device
            dev_site.id_site = secret_site.id_site
            db.session.add(dev_site)

            db.session.commit()
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
                    db.session.add(device_site)
                    db.session.commit()

    @staticmethod
    def get_device_site_by_id(device_site_id: int):
        return TeraDeviceSite.query.filter_by(id_device_site=device_site_id).first()

    @staticmethod
    def get_device_site_id_for_device_and_site(device_id: int, site_id: int):
        return TeraDeviceSite.query.filter_by(id_site=site_id, id_device=device_id).first()

    @staticmethod
    def get_devices_for_site(site_id: int):
        return TeraDeviceSite.query.filter_by(id_site=site_id).all()

    @staticmethod
    def get_sites_for_device(device_id: int):
        return TeraDeviceSite.query.filter_by(id_device=device_id).all()

    @staticmethod
    def delete_with_ids(device_id: int, site_id: int):
        delete_obj: TeraDeviceSite = TeraDeviceSite.query.filter_by(id_device=device_id, id_site=site_id).first()
        if delete_obj:
            TeraDeviceSite.delete(delete_obj.id_device_site)

    @classmethod
    def delete(cls, id_todel):
        from opentera.db.models.TeraDeviceProject import TeraDeviceProject
        # Delete all association with projects for that site
        delete_obj = TeraDeviceSite.query.filter_by(id_device_site=id_todel).first()

        if delete_obj:
            projects = TeraDeviceProject.get_projects_for_device(delete_obj.id_device)
            for device_project in projects:
                TeraDeviceProject.delete(device_project.id_device_project)

            # Ok, delete it
            super().delete(id_todel)
