from libtera.db.Base import db, BaseModel


kits_participants_table = db.Table('t_kits_participants',
                                   db.Column('id_kit', db.Integer,
                                             db.ForeignKey('t_kits.id_kit', ondelete='cascade')),
                                   db.Column('id_participant', db.Integer,
                                             db.ForeignKey('t_participants.id_participant', ondelete='cascade')))


class TeraKit(db.Model, BaseModel):
    __tablename__ = 't_kits'
    id_kit = db.Column(db.Integer, db.Sequence('id_kit_sequence'), primary_key=True, autoincrement=True)
    id_project = db.Column(db.Integer,  db.ForeignKey('t_projects.id_project', ondelete='set null'), nullable=True)
    id_site = db.Column(db.Integer, db.ForeignKey('t_sites.id_site', ondelete='cascade'), nullable=False)
    kit_name = db.Column(db.String, nullable=False)
    kit_shareable = db.Column(db.Boolean, nullable=False)
    kit_lastonline = db.Column(db.TIMESTAMP, nullable=True)

    kit_devices = db.relationship("TeraKitDevice")

    kit_participants = db.relationship("TeraParticipant", secondary=kits_participants_table,
                                       back_populates="participant_kits", cascade="all,delete")

    kit_project = db.relationship("TeraProject")
    kit_site = db.relationship("TeraSite")

    def to_json(self, ignore_fields=None, minimal=False):
        if ignore_fields is None:
            ignore_fields = []

        ignore_fields += ['kit_devices', 'kit_participants', 'kit_project', 'kit_site']

        return super().to_json(ignore_fields=ignore_fields)

    @staticmethod
    def create_defaults():
        from libtera.db.models.TeraDevice import TeraDevice
        from libtera.db.models.TeraParticipant import TeraParticipant
        from libtera.db.models.TeraProject import TeraProject
        from libtera.db.models.TeraSite import TeraSite

        site = TeraSite.get_site_by_sitename('Default Site')

        kit1 = TeraKit()
        kit1.kit_name = 'Kit #1'
        kit1.kit_shareable = False

        # Apple Watch #W05P1
        # device = TeraDevice.get_device_by_name('Apple Watch #W05P1')
        # kit1.kit_required_devices.append(device)

        participant = TeraParticipant.get_participant_by_name('Test Participant #1')
        kit1.kit_participants.append(participant)

        kit1.kit_site = site

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

    @staticmethod
    def get_kit_by_id(kit_id: int):
        return TeraKit.query.filter_by(id_kit=kit_id).first()

    @staticmethod
    def get_kits_for_site(site_id: int):
        return TeraKit.query.filter_by(id_site=site_id).all()

    @staticmethod
    def get_kits_for_project(project_id: int):
        return TeraKit.query.filter_by(id_project=project_id).all()

    @staticmethod
    def update_kit(id_kit: int, values={}):
        if 'id_project' in values:
            if values['id_project'] == 0:
                values['id_project'] = None

        TeraKit.query.filter_by(id_kit=id_kit).update(values)
        db.session.commit()

    @staticmethod
    def insert_kit(kit):
        kit.id_kit = None
        if kit.id_project == 0:
            kit.id_project = None

        # Clear last online field
        kit.kit_lastonline = None

        db.session.add(kit)
        db.session.commit()

    @staticmethod
    def delete_kit(id_kit):
        TeraKit.query.filter_by(id_kit=id_kit).delete()
        db.session.commit()
