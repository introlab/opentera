from libtera.db.Base import db, BaseModel


class TeraDeviceSite(db.Model, BaseModel):
    __tablename__ = 't_devices_sites'
    id_device_site = db.Column(db.Integer, db.Sequence('id_device_site_sequence'), primary_key=True, autoincrement=True)
    id_device = db.Column(db.Integer, db.ForeignKey("t_devices.id_device", ondelete='cascade'), nullable=False)
    id_site = db.Column(db.Integer, db.ForeignKey("t_sites.id_site", ondelete='cascade'), nullable=False)

    device_site_site = db.relationship("TeraSite")
    device_site_device = db.relationship("TeraDevice")

    def to_json(self, ignore_fields=[], minimal=False):
        ignore_fields.extend(['device_site_site', 'device_site_device'])

        if minimal:
            ignore_fields.extend([])

        rval = super().to_json(ignore_fields=ignore_fields)

        return rval

    @staticmethod
    def create_defaults():
        from libtera.db.models.TeraSite import TeraSite
        from libtera.db.models.TeraDevice import TeraDevice
        default_site = TeraSite.get_site_by_sitename('Default Site')
        secret_site = TeraSite.get_site_by_sitename('Top Secret Site')
        device1 = TeraDevice.get_device_by_name('Apple Watch #W05P1')
        device2 = TeraDevice.get_device_by_name('Kit Télé #1')
        device3 = TeraDevice.get_device_by_name('Robot A')

        dev_site = TeraDeviceSite()
        dev_site.device_site_device = device1
        dev_site.device_site_site = default_site
        db.session.add(dev_site)

        dev_site = TeraDeviceSite()
        dev_site.device_site_device = device1
        dev_site.device_site_site = secret_site
        db.session.add(dev_site)

        dev_site = TeraDeviceSite()
        dev_site.device_site_device = device2
        dev_site.device_site_site = default_site
        db.session.add(dev_site)

        db.session.commit()

    @staticmethod
    def get_device_site_by_id(device_site_id: int):
        return TeraDeviceSite.query.filter_by(id_device_site=device_site_id).first()

    @staticmethod
    def query_devices_for_site(site_id: int):
        return TeraDeviceSite.query.filter_by(id_site=site_id).all()

    @staticmethod
    def query_sites_for_device(device_id: int):
        return TeraDeviceSite.query.filter_by(id_device=device_id).all()

    @staticmethod
    def query_device_site_for_device_site(device_id: int, site_id: int):
        return TeraDeviceSite.query.filter_by(id_device=device_id, id_site=site_id).first()

    @staticmethod
    def update_device_site(id_device_site, values={}):
        TeraDeviceSite.query.filter_by(id_device_site=id_device_site).update(values)
        db.session.commit()

    @staticmethod
    def insert_device_site(device_site):
        device_site.id_device_site = None

        db.session.add(device_site)
        db.session.commit()

    @staticmethod
    def delete_device_site(id_device_site):
        TeraDeviceSite.query.filter_by(id_device_site=id_device_site).delete()
        db.session.commit()

    @staticmethod
    def delete_device_sites(device_sites):
        if not isinstance(device_sites, list):
            return

        for devicesite in device_sites:
            db.session.delete(devicesite)
        db.session.commit()
