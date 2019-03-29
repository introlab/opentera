from libtera.db.Base import db, BaseModel


sessions_types_devices_table = db.Table('t_sessions_types_devices', db.Column('id_session_type', db.Integer,
                                                                              db.ForeignKey(
                                                                                  't_sessions_types.id_session_type')),
                                        db.Column('id_device_type', db.Integer,
                                                  db.ForeignKey('t_devices_types.id_device_type')))

sessions_types_projects_table = db.Table('t_sessions_types_projects', db.Column('id_session_type', db.Integer,
                                                                                db.ForeignKey(
                                                                                  't_sessions_types.id_session_type')),
                                         db.Column('id_project', db.Integer, db.ForeignKey('t_projects.id_project')))


class TeraSessionType(db.Model, BaseModel):
    __tablename__ = 't_sessions_types'
    id_session_type = db.Column(db.Integer, db.Sequence('id_session_type_sequence'), primary_key=True,
                                autoincrement=True)
    id_project = db.Column(db.Integer, db.ForeignKey('t_projects.id_project'), nullable=False)
    session_type_name = db.Column(db.String, nullable=False, unique=False)
    session_type_prefix = db.Column(db.String(10), nullable=False, unique=False)
    session_type_online = db.Column(db.Boolean, nullable=False)
    session_type_multiusers = db.Column(db.Boolean, nullable=False)
    session_type_profile = db.Column(db.String, nullable=True)

    session_type_projects = db.relationship("TeraProject", secondary=sessions_types_projects_table,
                                            cascade="all,delete")

    session_type_uses_devices_types = db.relationship("TeraDeviceType", secondary=sessions_types_devices_table,
                                                      cascade="all,delete")


