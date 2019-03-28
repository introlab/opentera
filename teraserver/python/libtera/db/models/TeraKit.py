from libtera.db.Base import db, BaseModel

kits_devices_required_table = db.Table('t_kits_devices_required', db.Column('id_kit', db.Integer,
                                                                            db.ForeignKey('t_kits.id_kit')),
                                       db.Column('id_device', db.Integer, db.ForeignKey('t_devices.id_device')))

kits_devices_optional_table = db.Table('t_kits_devices_optional', db.Column('id_kit', db.Integer,
                                                                            db.ForeignKey('t_kits.id_kit')),
                                       db.Column('id_device', db.Integer, db.ForeignKey('t_devices.id_device')))

kits_participants_table = db.Table('t_kits_participants', db.Column('id_kit', db.Integer,
                                                                    db.ForeignKey('t_kits.id_kit')),
                                   db.Column('id_participant', db.Integer,
                                             db.ForeignKey('t_participants.id_participant')))


class TeraKit(db.Model, BaseModel):
    __tablename__ = 't_kits'
    id_kit = db.Column(db.Integer, db.Sequence('id_kit_sequence'), primary_key=True, autoincrement=True)
    id_project = db.Column(db.Integer,  db.ForeignKey('t_projects.id_project'), nullable=True)
    kit_name = db.Column(db.String, nullable=False)
    kit_shareable = db.Column(db.Boolean, nullable=False)
    kit_lastonline = db.Column(db.TIMESTAMP, nullable=True)

    kit_required_devices = db.relationship("TeraDevice", secondary=kits_devices_required_table, cascade="all,delete")
    kit_optional_devices = db.relationship("TeraDevice", secondary=kits_devices_optional_table, cascade="all,delete")
    kit_participants = db.relationship("TeraParticipant", secondary=kits_participants_table,
                                       back_populates="participant_kits", cascade="all,delete")

