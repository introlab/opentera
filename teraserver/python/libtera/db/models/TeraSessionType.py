from libtera.db.Base import db, BaseModel
from enum import Enum, unique


class TeraSessionType(db.Model, BaseModel):
    @unique
    class SessionCategoryEnum(Enum):
        VIDEOCONFERENCE = 1
        TELEOPERATION = 2
        FILETRANSFER = 3
        STREAMING = 4

        def describe(self):
            return self.name, self.value

    __tablename__ = 't_sessions_types'
    id_session_type = db.Column(db.Integer, db.Sequence('id_session_type_sequence'), primary_key=True,
                                autoincrement=True)
    session_type_name = db.Column(db.String, nullable=False, unique=False)
    session_type_prefix = db.Column(db.String(10), nullable=False, unique=True)
    session_type_online = db.Column(db.Boolean, nullable=False)
    session_type_multiusers = db.Column(db.Boolean, nullable=False)
    session_type_config = db.Column(db.String, nullable=True)
    session_type_color = db.Column(db.String(7), nullable=False)
    session_type_category = db.Column(db.Integer, nullable=False)

    # session_type_projects = db.relationship("TeraProject", secondary=sessions_types_projects_table)
    session_type_projects = db.relationship("TeraSessionTypeProject")

    session_type_devices_types = db.relationship("TeraSessionTypeDeviceType")

    def to_json(self, ignore_fields=None, minimal=False):
        if ignore_fields is None:
            ignore_fields = []
        ignore_fields.extend(['session_type_projects', 'session_type_devices_types', 'SessionCategoryEnum'])
        if minimal:
            ignore_fields.extend(['session_type_prefix', 'session_type_online', 'session_type_multiusers',
                                  'session_type_profile'])
        rval = super().to_json(ignore_fields=ignore_fields)
        return rval

    @staticmethod
    def create_defaults():
        # from libtera.db.models.TeraProject import TeraProject
        # from libtera.db.models.TeraDeviceType import TeraDeviceType

        # type_project = TeraProject.get_project_by_projectname('Default Project #1')
        video_session = TeraSessionType()
        video_session.session_type_name = "Suivi vidéo"
        video_session.session_type_prefix = "VIDEO"
        video_session.session_type_online = True
        video_session.session_type_multiusers = False
        video_session.session_type_config = ""
        video_session.session_type_color = "#00FF00"
        video_session.session_type_category = TeraSessionType.SessionCategoryEnum.VIDEOCONFERENCE.value
        # video_session.session_type_projects = [type_project]
        # video_session.session_type_uses_devices_types = [TeraDeviceType.get_device_type(
        #     int(TeraDeviceType.DeviceTypeEnum.VIDEOCONFERENCE.value))]
        db.session.add(video_session)

        sensor_session = TeraSessionType()
        sensor_session.session_type_name = "Données Capteur"
        sensor_session.session_type_prefix = "SENSOR"
        sensor_session.session_type_online = False
        sensor_session.session_type_multiusers = False
        sensor_session.session_type_config = ""
        sensor_session.session_type_color = "#0000FF"
        sensor_session.session_type_category = TeraSessionType.SessionCategoryEnum.FILETRANSFER.value
        # sensor_session.session_type_projects = [type_project]
        # sensor_session.session_type_uses_devices_types = [TeraDeviceType.get_device_type(
        #     int(TeraDeviceType.DeviceTypeEnum.SENSOR.value))]
        db.session.add(sensor_session)

        vsensor_session = TeraSessionType()
        vsensor_session.session_type_name = "Collecte données"
        vsensor_session.session_type_prefix = "STREAM"
        vsensor_session.session_type_online = True
        vsensor_session.session_type_multiusers = False
        vsensor_session.session_type_config = ""
        vsensor_session.session_type_color = "#00FFFF"
        # vsensor_session.session_type_projects = [type_project]
        vsensor_session.session_type_category = TeraSessionType.SessionCategoryEnum.STREAMING.value
        # vsensor_session.session_type_uses_devices_types = [TeraDeviceType.get_device_type(
        #     int(TeraDeviceType.DeviceTypeEnum.SENSOR.value)), TeraDeviceType.get_device_type(
        #     int(TeraDeviceType.DeviceTypeEnum.VIDEOCONFERENCE.value))]
        db.session.add(vsensor_session)

        robot_session = TeraSessionType()
        robot_session.session_type_name = "Séance Robot"
        robot_session.session_type_prefix = "ROBOT"
        robot_session.session_type_online = True
        robot_session.session_type_multiusers = False
        robot_session.session_type_config = ""
        robot_session.session_type_color = "#FF00FF"
        # robot_session.session_type_projects = [type_project]
        robot_session.session_type_category = TeraSessionType.SessionCategoryEnum.TELEOPERATION.value
        # robot_session.session_type_uses_devices_types = [TeraDeviceType.get_device_type(
        #     int(TeraDeviceType.DeviceTypeEnum.ROBOT.value))]
        db.session.add(robot_session)

        db.session.commit()

    @staticmethod
    def get_session_type_by_id(ses_type_id: int):
        return TeraSessionType.query.filter_by(id_session_type=ses_type_id).first()

    @staticmethod
    def get_session_type_by_prefix(prefix: str):
        return TeraSessionType.query.filter_by(session_type_prefix=prefix).first()

    @staticmethod
    def get_category_name(category: SessionCategoryEnum):
        name = 'Inconue'
        if category == TeraSessionType.SessionCategoryEnum.VIDEOCONFERENCE:
            name = 'Vidéoconférence'
        if category == TeraSessionType.SessionCategoryEnum.FILETRANSFER:
            name = 'Envoi de fichiers (upload)'
        if category == TeraSessionType.SessionCategoryEnum.STREAMING:
            name = 'Transfert de données (streaming)'
        if category == TeraSessionType.SessionCategoryEnum.TELEOPERATION:
            name = 'Téléopération'

        return name


