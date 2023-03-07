from opentera.db.Base import BaseModel
from opentera.db.SoftDeleteMixin import SoftDeleteMixin
from opentera.db.SoftInsertMixin import SoftInsertMixin
from sqlalchemy import Column, ForeignKey, Integer, String, Sequence, Boolean, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.exc import IntegrityError


class TeraDeviceProject(BaseModel, SoftDeleteMixin, SoftInsertMixin):
    __tablename__ = 't_devices_projects'
    id_device_project = Column(Integer, Sequence('id_device_project_sequence'), primary_key=True,
                               autoincrement=True)
    id_device = Column(Integer, ForeignKey("t_devices.id_device", ondelete='cascade'), nullable=False)
    id_project = Column(Integer, ForeignKey("t_projects.id_project", ondelete='cascade'), nullable=False)

    device_project_project = relationship("TeraProject", viewonly=True)
    device_project_device = relationship("TeraDevice", viewonly=True)

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
            dev_proj.id_device = device1.id_device
            dev_proj.id_project = project1.id_project
            TeraDeviceProject.db().session.add(dev_proj)

            dev_proj = TeraDeviceProject()
            dev_proj.id_device = device2.id_device
            dev_proj.id_project = project1.id_project
            TeraDeviceProject.db().session.add(dev_proj)

            dev_proj = TeraDeviceProject()
            dev_proj.id_device = device1.id_device
            dev_proj.id_project = project3.id_project
            TeraDeviceProject.db().session.add(dev_proj)

            TeraDeviceProject.db().session.commit()

    @staticmethod
    def get_device_project_by_id(device_project_id: int, with_deleted: bool = False):
        return TeraDeviceProject.query.execution_options(include_deleted=with_deleted)\
            .filter_by(id_device_project=device_project_id).first()

    @staticmethod
    def get_device_project_id_for_device_and_project(device_id: int, project_id: int, with_deleted: bool = False):
        return TeraDeviceProject.query.execution_options(include_deleted=with_deleted)\
            .filter_by(id_project=project_id, id_device=device_id).first()

    @staticmethod
    def get_devices_for_project(project_id: int, with_deleted: bool = False):
        return TeraDeviceProject.query.execution_options(include_deleted=with_deleted)\
            .filter_by(id_project=project_id).all()

    @staticmethod
    def get_projects_for_device(device_id: int, with_deleted: bool = False):
        return TeraDeviceProject.query.execution_options(include_deleted=with_deleted)\
            .filter_by(id_device=device_id).all()

    @staticmethod
    def delete_with_ids(device_id: int, project_id: int, autocommit: bool = True):
        delete_obj = TeraDeviceProject.query.filter_by(id_device=device_id, id_project=project_id).first()
        if delete_obj:
            TeraDeviceProject.delete(delete_obj.id_device_project, autocommit=autocommit)

    def delete_check_integrity(self) -> IntegrityError | None:
        from opentera.db.models.TeraDeviceParticipant import TeraDeviceParticipant
        from opentera.db.models.TeraParticipant import TeraParticipant
        from opentera.db.models.TeraSession import TeraSession

        if TeraDeviceParticipant.query.join(TeraParticipant).\
            filter(TeraParticipant.id_project == self.id_project).\
                filter(TeraDeviceParticipant.id_device == self.id_device).count():
            return IntegrityError('Project still has participant associated to the device',
                                  self.id_device_project, 't_participants')

        # Find sessions with matching device and project
        device_sessions = TeraSession.get_sessions_for_device(self.id_device)
        device_project_sessions = [ses.id_session for ses in device_sessions
                                   if ses.get_associated_project_id() == self.id_project]

        if len(device_project_sessions) > 0:
            return IntegrityError('Device still has sessions in this project',
                                  self.id_device_project, 't_sessions')

        return None

    @classmethod
    def insert(cls, dp):
        # Check if that site of that project has the site associated to it
        from opentera.db.models.TeraDeviceSite import TeraDeviceSite
        from opentera.db.models.TeraProject import TeraProject
        project = TeraProject.get_project_by_id(project_id=dp.id_project)

        if not project:
            raise IntegrityError(params='Project not found',
                                 orig='TeraDeviceProject.insert', statement='insert')

        device_site = TeraDeviceSite.get_device_site_id_for_device_and_site(site_id=project.id_site,
                                                                            device_id=dp.id_device)

        if not device_site:
            raise IntegrityError(params='Device not associated to project site',
                                 orig='TeraDeviceProject.insert', statement='insert')
        inserted_obj = super().insert(dp)
        return inserted_obj

    @classmethod
    def update(cls, update_id: int, values: dict):
        return
