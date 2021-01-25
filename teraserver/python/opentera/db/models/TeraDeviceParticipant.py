from opentera.db.Base import db, BaseModel


class TeraDeviceParticipant(db.Model, BaseModel):
    __tablename__ = 't_devices_participants'
    id_device_participant = db.Column(db.Integer, db.Sequence('id_device_participant_sequence'), primary_key=True,
                                      autoincrement=True)
    id_device = db.Column(db.Integer, db.ForeignKey("t_devices.id_device"), nullable=False)
    id_participant = db.Column(db.Integer, db.ForeignKey("t_participants.id_participant", ondelete='cascade'),
                               nullable=False)

    device_participant_participant = db.relationship("TeraParticipant")
    device_participant_device = db.relationship("TeraDevice")

    def to_json(self, ignore_fields=[], minimal=False):
        ignore_fields.extend(['device_participant_participant', 'device_participant_device'])

        if minimal:
            ignore_fields.extend([])

        rval = super().to_json(ignore_fields=ignore_fields)

        return rval

    @staticmethod
    def create_defaults(test=False):
        if test:
            from opentera.db.models.TeraParticipant import TeraParticipant
            from opentera.db.models.TeraDevice import TeraDevice
            participant1 = TeraParticipant.get_participant_by_id(1)
            participant2 = TeraParticipant.get_participant_by_id(2)
            device1 = TeraDevice.get_device_by_name('Apple Watch #W05P1')
            device2 = TeraDevice.get_device_by_name('Kit Télé #1')
            device3 = TeraDevice.get_device_by_name('Robot A')

            dev_participant = TeraDeviceParticipant()
            dev_participant.device_participant_device = device1
            dev_participant.device_participant_participant = participant1
            db.session.add(dev_participant)

            dev_participant = TeraDeviceParticipant()
            dev_participant.device_participant_device = device1
            dev_participant.device_participant_participant = participant2
            db.session.add(dev_participant)

            dev_participant = TeraDeviceParticipant()
            dev_participant.device_participant_device = device2
            dev_participant.device_participant_participant = participant2
            db.session.add(dev_participant)

            db.session.commit()

    @staticmethod
    def get_device_participant_by_id(device_participant_id: int):
        return TeraDeviceParticipant.query.filter_by(id_device_participant=device_participant_id).first()

    @staticmethod
    def query_devices_for_participant(participant_id: int):
        return TeraDeviceParticipant.query.filter_by(id_participant=participant_id).all()

    @staticmethod
    def query_participants_for_device(device_id: int):
        return TeraDeviceParticipant.query.filter_by(id_device=device_id).all()

    @staticmethod
    def query_device_participant_for_participant_device(device_id: int, participant_id: int):
        return TeraDeviceParticipant.query.filter_by(id_device=device_id, id_participant=participant_id).first()
