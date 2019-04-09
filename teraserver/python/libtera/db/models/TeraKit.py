from libtera.db.Base import db, BaseModel


kits_devices_required_table = db.Table('t_kits_devices_required', db.Column('id_kit', db.Integer,
                                                                            db.ForeignKey('t_kits.id_kit',
                                                                                          ondelete='cascade')),
                                       db.Column('id_device', db.Integer, db.ForeignKey('t_devices.id_device',
                                                                                        ondelete='cascade')))

kits_devices_optional_table = db.Table('t_kits_devices_optional', db.Column('id_kit', db.Integer,
                                                                            db.ForeignKey('t_kits.id_kit',
                                                                                          ondelete='cascade')),
                                       db.Column('id_device', db.Integer, db.ForeignKey('t_devices.id_device',
                                                                                        ondelete='cascade')))

kits_participants_table = db.Table('t_kits_participants', db.Column('id_kit', db.Integer,
                                                                    db.ForeignKey('t_kits.id_kit', ondelete='cascade')),
                                   db.Column('id_participant', db.Integer,
                                             db.ForeignKey('t_participants.id_participant', ondelete='cascade')))


class TeraKit(db.Model, BaseModel):
    __tablename__ = 't_kits'
    id_kit = db.Column(db.Integer, db.Sequence('id_kit_sequence'), primary_key=True, autoincrement=True)
    id_project = db.Column(db.Integer,  db.ForeignKey('t_projects.id_project', ondelete='set null'), nullable=True)
    kit_name = db.Column(db.String, nullable=False)
    kit_shareable = db.Column(db.Boolean, nullable=False)
    kit_lastonline = db.Column(db.TIMESTAMP, nullable=True)

    kit_required_devices = db.relationship("TeraDevice", secondary=kits_devices_required_table, cascade="all,delete")
    kit_optional_devices = db.relationship("TeraDevice", secondary=kits_devices_optional_table, cascade="all,delete")
    kit_participants = db.relationship("TeraParticipant", secondary=kits_participants_table,
                                       back_populates="participant_kits", cascade="all,delete")

    kit_project = db.relationship("TeraProject")

    @staticmethod
    def create_defaults():

        from libtera.db.models.TeraDevice import TeraDevice
        from libtera.db.models.TeraParticipant import TeraParticipant
        from libtera.db.models.TeraProject import TeraProject

        kit1 = TeraKit()
        kit1.kit_name = 'Kit #1'
        kit1.kit_shareable = False

        # Apple Watch #W05P1
        # device = TeraDevice.get_device_by_name('Apple Watch #W05P1')
        # kit1.kit_required_devices.append(device)

        participant = TeraParticipant.get_participant_by_name('Test Participant #1')
        kit1.kit_participants.append(participant)

        project = TeraProject.get_project_by_projectname('Default Project #1')
        kit1.kit_project = project

        db.session.add(kit1)
        db.session.commit()

    @staticmethod
    def get_kit_by_name(name):
        return TeraKit.query.filter_by(kit_name=name).first()

    @staticmethod
    def get_count():
        count = db.session.query(db.func.count(TeraKit.id_kit))
        return count.first()[0]
