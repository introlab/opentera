from opentera.db.Base import db, BaseModel
from enum import Enum, unique
from flask_babel import gettext


class TeraSessionType(db.Model, BaseModel):
    @unique
    class SessionCategoryEnum(Enum):
        SERVICE = 1
        DATACOLLECT = 2
        FILETRANSFER = 3
        PROTOCOL = 4

        def describe(self):
            return self.name, self.value

    __tablename__ = 't_sessions_types'
    id_session_type = db.Column(db.Integer, db.Sequence('id_session_type_sequence'), primary_key=True,
                                autoincrement=True)
    id_service = db.Column(db.Integer, db.ForeignKey('t_services.id_service', ondelete='cascade'), nullable=True)
    session_type_name = db.Column(db.String, nullable=False, unique=False)
    session_type_online = db.Column(db.Boolean, nullable=False)
    session_type_config = db.Column(db.String, nullable=True)
    session_type_color = db.Column(db.String(7), nullable=False)
    session_type_category = db.Column(db.Integer, nullable=False)

    session_type_session_type_projects = db.relationship("TeraSessionTypeProject", viewonly=True)
    session_type_session_type_sites = db.relationship("TeraSessionTypeSite", viewonly=True)

    session_type_projects = db.relationship("TeraProject", secondary="t_sessions_types_projects",
                                            back_populates="project_session_types")
    session_type_sites = db.relationship("TeraSite", secondary="t_sessions_types_sites")

    session_type_service = db.relationship("TeraService")

    session_type_sessions = db.relationship("TeraSession", passive_deletes=True, back_populates='session_session_type')

    def to_json(self, ignore_fields=None, minimal=False):
        if ignore_fields is None:
            ignore_fields = []
        ignore_fields.extend(['session_type_projects', 'session_type_devices_types', 'SessionCategoryEnum',
                              'session_type_service', 'session_type_sessions', 'session_type_session_type_projects',
                              'session_type_sites', 'session_type_session_type_sites'])
        if minimal:
            ignore_fields.extend(['session_type_online',
                                  'session_type_profile',
                                  'session_type_config'])
        rval = super().to_json(ignore_fields=ignore_fields)

        if not minimal:
            # Also includes service key and uuid
            if self.session_type_service:
                rval['session_type_service_key'] = self.session_type_service.service_key
                rval['session_type_service_uuid'] = self.session_type_service.service_uuid
        return rval

    def to_json_create_event(self):
        return self.to_json(minimal=True)

    def to_json_update_event(self):
        return self.to_json(minimal=True)

    def to_json_delete_event(self):
        # Minimal information, delete can not be filtered
        return {'id_session_type': self.id_session_type, 'id_service': self.id_service}

    @staticmethod
    def create_defaults(test=False):
        # from opentera.db.models.TeraProject import TeraProject
        # from opentera.db.models.TeraDeviceType import TeraDeviceType
        from opentera.db.models.TeraService import TeraService

        # type_project = TeraProject.get_project_by_projectname('Default Project #1')
        video_session = TeraSessionType()
        video_session.session_type_name = "Suivi vidéo"
        video_session.session_type_online = True
        video_session.session_type_config = ""
        video_session.session_type_color = "#00FF00"
        video_session.session_type_category = TeraSessionType.SessionCategoryEnum.SERVICE.value
        video_session.id_service = TeraService.get_service_by_key('VideoRehabService').id_service
        # video_session.session_type_projects = [type_project]
        # video_session.session_type_uses_devices_types = [TeraDeviceType.get_device_type(
        #     int(TeraDeviceType.DeviceTypeEnum.VIDEOCONFERENCE.value))]
        db.session.add(video_session)

        sensor_session = TeraSessionType()
        sensor_session.session_type_name = "Données Capteur"
        sensor_session.session_type_online = False
        sensor_session.session_type_config = ""
        sensor_session.session_type_color = "#0000FF"
        sensor_session.session_type_category = TeraSessionType.SessionCategoryEnum.FILETRANSFER.value
        # sensor_session.session_type_projects = [type_project]
        # sensor_session.session_type_uses_devices_types = [TeraDeviceType.get_device_type(
        #     int(TeraDeviceType.DeviceTypeEnum.SENSOR.value))]
        db.session.add(sensor_session)

        vsensor_session = TeraSessionType()
        vsensor_session.session_type_name = "Collecte données"
        vsensor_session.session_type_online = True
        vsensor_session.session_type_config = ""
        vsensor_session.session_type_color = "#00FFFF"
        # vsensor_session.session_type_projects = [type_project]
        vsensor_session.session_type_category = TeraSessionType.SessionCategoryEnum.DATACOLLECT.value
        # vsensor_session.session_type_uses_devices_types = [TeraDeviceType.get_device_type(
        #     int(TeraDeviceType.DeviceTypeEnum.SENSOR.value)), TeraDeviceType.get_device_type(
        #     int(TeraDeviceType.DeviceTypeEnum.VIDEOCONFERENCE.value))]
        db.session.add(vsensor_session)

        robot_session = TeraSessionType()
        robot_session.session_type_name = "Exercices individuels"
        robot_session.session_type_online = False
        robot_session.session_type_config = ""
        robot_session.session_type_color = "#FF00FF"
        # robot_session.session_type_projects = [type_project]
        robot_session.session_type_category = TeraSessionType.SessionCategoryEnum.PROTOCOL.value
        # robot_session.session_type_uses_devices_types = [TeraDeviceType.get_device_type(
        #     int(TeraDeviceType.DeviceTypeEnum.ROBOT.value))]
        db.session.add(robot_session)

        bureau_session = TeraSessionType()
        bureau_session.session_type_name = "FileTransfer"
        bureau_session.session_type_online = False
        bureau_session.session_type_config = ""
        bureau_session.session_type_color = "#FF00FF"
        bureau_session.session_type_category = TeraSessionType.SessionCategoryEnum.SERVICE.value
        # robot_session.session_type_uses_devices_types = [TeraDeviceType.get_device_type(
        #     int(TeraDeviceType.DeviceTypeEnum.ROBOT.value))]
        bureau_session.id_service = TeraService.get_service_by_key('FileTransferService').id_service
        db.session.add(bureau_session)

        db.session.commit()

    @staticmethod
    def get_session_type_by_id(ses_type_id: int):
        return TeraSessionType.query.filter_by(id_session_type=ses_type_id).first()

    @staticmethod
    def get_session_types_for_service(id_service: int):
        return TeraSessionType.query.filter_by(id_service=id_service).all()

    @staticmethod
    def get_category_name(category: SessionCategoryEnum):
        name = gettext('Unknown')
        if category == TeraSessionType.SessionCategoryEnum.SERVICE:
            name = gettext('Service')
        if category == TeraSessionType.SessionCategoryEnum.FILETRANSFER:
            name = gettext('File Transfer')
        if category == TeraSessionType.SessionCategoryEnum.DATACOLLECT:
            name = gettext('Data Collect')
        if category == TeraSessionType.SessionCategoryEnum.PROTOCOL:
            name = gettext('Protocol')

        return name

    @classmethod
    def update(cls, id_st: int, values: dict):
        # Set service id to None if setted to 0
        if 'id_service' in values:
            if values['id_service'] == 0:
                del values['id_service']

        super().update(id_st, values)

    @classmethod
    def insert(cls, st):
        if st.id_service == 0:
            st.id_service = None

        super().insert(st)
