from opentera.db.Base import db, BaseModel


class TeraDeviceProject(db.Model, BaseModel):
    __tablename__ = 't_devices_projects'
    id_device_project = db.Column(db.Integer, db.Sequence('id_device_project_sequence'), primary_key=True,
                                  autoincrement=True)
    id_device = db.Column(db.Integer, db.ForeignKey("t_devices.id_device", ondelete='cascade'), nullable=False)
    id_project = db.Column(db.Integer, db.ForeignKey("t_projects.id_project", ondelete='cascade'), nullable=False)

    device_project_project = db.relationship("TeraProject")
    device_project_device = db.relationship("TeraDevice")

    def to_json(self, ignore_fields=[], minimal=False):
        ignore_fields.extend(['device_project_project', 'device_project_device'])

        if minimal:
            ignore_fields.extend([])

        rval = super().to_json(ignore_fields=ignore_fields)

        return rval

    @staticmethod
    def create_defaults(test=False):
        if test:
            from opentera.db.models.TeraDevice import TeraDevice
            from opentera.db.models.TeraProject import TeraProject
            device1 = TeraDevice.get_device_by_name('Apple Watch #W05P1')
            device2 = TeraDevice.get_device_by_name('Kit Télé #1')
            device3 = TeraDevice.get_device_by_name('Robot A')
            project1 = TeraProject.get_project_by_projectname('Default Project #1')
            project2 = TeraProject.get_project_by_projectname('Default Project #2')
            project3 = TeraProject.get_project_by_projectname('Secret Project #1')

            dev_proj = TeraDeviceProject()
            dev_proj.device_project_device = device1
            dev_proj.device_project_project = project1
            db.session.add(dev_proj)

            dev_proj = TeraDeviceProject()
            dev_proj.device_project_device = device2
            dev_proj.device_project_project = project1
            db.session.add(dev_proj)

            dev_proj = TeraDeviceProject()
            dev_proj.device_project_device = device1
            dev_proj.device_project_project = project3
            db.session.add(dev_proj)

            db.session.commit()

    @staticmethod
    def get_device_project_by_id(device_project_id: int):
        return TeraDeviceProject.query.filter_by(id_device_project=device_project_id).first()

    @staticmethod
    def get_device_project_id_for_device_and_project(device_id: int, project_id: int):
        return TeraDeviceProject.query.filter_by(id_project=project_id, id_device=device_id).first()

    @staticmethod
    def query_devices_for_project(project_id: int):
        return TeraDeviceProject.query.filter_by(id_project=project_id).all()

    @staticmethod
    def query_projects_for_device(device_id: int):
        return TeraDeviceProject.query.filter_by(id_device=device_id).all()

    @staticmethod
    def query_sites_for_device(device_id: int) -> list:
        from opentera.db.models.TeraProject import TeraProject
        return TeraDeviceProject.query.filter_by(id_device=device_id).join(TeraDeviceProject.device_project_project)\
            .join(TeraProject.project_site).all()
        # TeraSite.query.join(TeraSite.site_projects).join(TeraDeviceProject.device_project_project)\
        # .filter(id_device=device_id).all()

    @staticmethod
    def query_devices_for_site(site_id: int) -> list:
        from opentera.db.models.TeraDevice import TeraDevice
        return TeraDeviceProject.query.join(TeraDeviceProject.device_project_project).filter_by(id_site=site_id).all()
        # return TeraDevice.query.join(TeraDevice.device_projects).filter_by(id_site=site_id).all()
