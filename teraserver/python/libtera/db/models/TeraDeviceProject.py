from libtera.db.Base import db, BaseModel


class TeraDeviceProject(db.Model, BaseModel):
    __tablename__ = 't_devices_projects'
    id_device_project = db.Column(db.Integer, db.Sequence('id_device_project_sequence'), primary_key=True,
                                  autoincrement=True)
    id_device_site = db.Column(db.Integer, db.ForeignKey("t_devices_sites.id_device_site", ondelete='cascade'),
                               nullable=False)
    id_project = db.Column(db.Integer, db.ForeignKey("t_projects.id_project", ondelete='cascade'), nullable=False)

    device_project_project = db.relationship("TeraProject")
    device_project_device_site = db.relationship("TeraDeviceSite")

    def to_json(self, ignore_fields=[], minimal=False):
        ignore_fields.extend(['device_project_project', 'device_project_device_site', 'id_device_site'])

        if minimal:
            ignore_fields.extend([])

        rval = super().to_json(ignore_fields=ignore_fields)

        # Add id_device in reply
        rval['id_device'] = self.device_project_device_site.id_device

        return rval

    @staticmethod
    def create_defaults():
        from libtera.db.models.TeraSite import TeraSite
        from libtera.db.models.TeraDeviceSite import TeraDeviceSite
        from libtera.db.models.TeraDevice import TeraDevice
        from libtera.db.models.TeraProject import TeraProject
        default_site = TeraSite.get_site_by_sitename('Default Site')
        secret_site = TeraSite.get_site_by_sitename('Top Secret Site')
        device1 = TeraDevice.get_device_by_name('Apple Watch #W05P1')
        device2 = TeraDevice.get_device_by_name('Kit Télé #1')
        device3 = TeraDevice.get_device_by_name('Robot A')
        project1 = TeraProject.get_project_by_projectname('Default Project #1')
        project2 = TeraProject.get_project_by_projectname('Default Project #1')

        dev_proj = TeraDeviceProject()
        dev_proj.device_project_device_site = TeraDeviceSite.get_device_site_id_for_device_and_site(device1.id_device,
                                                                                                    default_site.id_site
                                                                                                    )
        dev_proj.device_project_project = project1
        db.session.add(dev_proj)

        dev_proj = TeraDeviceProject()
        dev_proj.device_project_device_site = TeraDeviceSite.get_device_site_id_for_device_and_site(device2.id_device,
                                                                                                    default_site.id_site
                                                                                                    )
        dev_proj.device_project_project = project2
        db.session.add(dev_proj)

        db.session.commit()

    @staticmethod
    def get_device_project_by_id(device_project_id: int):
        return TeraDeviceProject.query.filter_by(id_device_project=device_project_id).first()

    @staticmethod
    def get_device_project_id_for_device_and_project(device_id: int, project_id: int):
        from libtera.db.models.TeraDeviceSite import TeraDeviceSite
        return TeraDeviceProject.query.filter_by(id_project=project_id)\
            .join(TeraDeviceProject.device_project_device_site)\
            .join(TeraDeviceSite.device_site_device)\
            .filter_by(id_device=device_id).first()

    @staticmethod
    def query_devices_for_project(project_id: int):
        return TeraDeviceProject.query.filter_by(id_project=project_id).all()

    @staticmethod
    def query_projects_for_device(device_id: int):
        from libtera.db.models.TeraDeviceSite import TeraDeviceSite
        return TeraDeviceProject.query.join(TeraDeviceProject.device_project_device_site).\
            join(TeraDeviceSite.device_site_device).filter_by(id_device=device_id).all()
