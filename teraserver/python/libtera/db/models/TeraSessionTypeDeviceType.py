from libtera.db.Base import db, BaseModel


class TeraSessionTypeDeviceType(db.Model, BaseModel):
    __tablename__ = 't_sessions_types_devices'
    id_session_type_device_type = db.Column(db.Integer, db.Sequence('id_session_type_device_type_sequence'),
                                            primary_key=True, autoincrement=True)
    id_device_type = db.Column(db.Integer, db.ForeignKey("t_devices_types.id_device_type", ondelete='cascade'),
                               nullable=False)
    id_session_type = db.Column(db.Integer, db.ForeignKey("t_sessions_types.id_session_type", ondelete='cascade'),
                                nullable=False)

    session_type_device_session_type = db.relationship("TeraSessionType")
    session_type_device_device_type = db.relationship("TeraDeviceType")

    def to_json(self, ignore_fields=[], minimal=False):
        ignore_fields.extend(['session_type_device_session_type', 'session_type_device_device_type'])

        if minimal:
            ignore_fields.extend([])

        rval = super().to_json(ignore_fields=ignore_fields)

        return rval

    @staticmethod
    def create_defaults():
        from libtera.db.models.TeraSessionType import TeraSessionType
        from libtera.db.models.TeraDeviceType import TeraDeviceType

        video_session = TeraSessionType.get_session_type_by_prefix('VIDEO')
        sensor_session = TeraSessionType.get_session_type_by_prefix('SENSOR')
        data_session = TeraSessionType.get_session_type_by_prefix('DATA')
        exer_session = TeraSessionType.get_session_type_by_prefix('EXERC')

        devices = TeraSessionTypeDeviceType()
        devices.session_type_device_session_type = video_session
        devices.session_type_device_device_type = TeraDeviceType.get_device_type(
            int(TeraDeviceType.DeviceTypeEnum.VIDEOCONFERENCE.value))
        db.session.add(devices)

        devices = TeraSessionTypeDeviceType()
        devices.session_type_device_session_type = sensor_session
        devices.session_type_device_device_type = TeraDeviceType.get_device_type(
            int(TeraDeviceType.DeviceTypeEnum.SENSOR.value))
        db.session.add(devices)

        devices = TeraSessionTypeDeviceType()
        devices.session_type_device_session_type = sensor_session
        devices.session_type_device_device_type = TeraDeviceType.get_device_type(
            int(TeraDeviceType.DeviceTypeEnum.BUREAU_ACTIF.value))
        db.session.add(devices)

        devices = TeraSessionTypeDeviceType()
        devices.session_type_device_session_type = data_session
        devices.session_type_device_device_type = TeraDeviceType.get_device_type(
            int(TeraDeviceType.DeviceTypeEnum.SENSOR.value))
        db.session.add(devices)
        devices = TeraSessionTypeDeviceType()
        devices.session_type_device_session_type = exer_session
        devices.session_type_device_device_type = TeraDeviceType.get_device_type(
            int(TeraDeviceType.DeviceTypeEnum.VIDEOCONFERENCE.value))
        db.session.add(devices)

        devices = TeraSessionTypeDeviceType()
        devices.session_type_device_session_type = video_session
        devices.session_type_device_device_type = TeraDeviceType.get_device_type(
            int(TeraDeviceType.DeviceTypeEnum.ROBOT.value))
        db.session.add(devices)
        db.session.commit()

    @staticmethod
    def get_session_type_device_type_by_id(stdt_id: int):
        return TeraSessionTypeDeviceType.query.filter_by(id_session_type_device=stdt_id).first()

    @staticmethod
    def query_device_types_for_session_type(session_type_id: int):
        return TeraSessionTypeDeviceType.query.filter_by(id_session_type=session_type_id).all()

    @staticmethod
    def query_sessions_types_for_device_type(device_type_id: int):
        return TeraSessionTypeDeviceType.query.filter_by(id_device_type=device_type_id).all()

    @staticmethod
    def query_session_type_device_for_device_session_type(device_type_id: int, session_type_id: int):
        return TeraSessionTypeDeviceType.query.filter_by(id_device_type=device_type_id,
                                                         id_session_type=session_type_id).first()
