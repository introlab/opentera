from libtera.db.Base import db, BaseModel
from libtera.db.models.TeraParticipant import TeraParticipant
from enum import Enum

sessions_participants_table = db.Table('t_sessions_participants', db.Column('id_session', db.Integer,
                                                                            db.ForeignKey('t_sessions.id_session',
                                                                                          ondelete='cascade')),
                                       db.Column('id_participant', db.Integer,
                                                 db.ForeignKey('t_participants.id_participant', ondelete='cascade')))


class TeraSessionStatus(Enum):
    STATUS_NOTSTARTED = 0
    STATUS_INPROGRESS = 1
    STATUS_COMPLETED = 2
    STATUS_CANCELLED = 3
    STATUS_TERMINATED = 4


class TeraSession(db.Model, BaseModel):
    __tablename__ = 't_sessions'
    id_session = db.Column(db.Integer, db.Sequence('id_session_sequence'), primary_key=True, autoincrement=True)
    id_session_type = db.Column(db.Integer, db.ForeignKey('t_sessions_types.id_session_type'), nullable=False)
    id_user = db.Column(db.Integer, db.ForeignKey('t_users.id_user'), nullable=False)
    session_name = db.Column(db.String, nullable=False)
    session_datetime = db.Column(db.TIMESTAMP, nullable=False)
    session_status = db.Column(db.Integer, nullable=False)
    session_comments = db.Column(db.String, nullable=True)
    session_participants = db.relationship("TeraParticipant", secondary=sessions_participants_table,
                                           back_populates="participant_sessions", cascade="all,delete")

    session_user = db.relationship('TeraUser')
    session_session_type = db.relationship('TeraSessionType')

    def to_json(self, ignore_fields=[], minimal=False):
        ignore_fields.extend(['session_participants', 'session_user',
                              'session_session_type'])
        if minimal:
            ignore_fields.extend([])

        return super().to_json(ignore_fields=ignore_fields)

    @staticmethod
    def create_defaults():
        base_session = TeraSession()
        base_project.project_name = 'Default Project #1'
        base_project.id_site = TeraSite.get_site_by_sitename('Default Site').id_site
        db.session.add(base_project)

        base_project2 = TeraProject()
        base_project2.project_name = 'Default Project #2'
        base_project2.id_site = TeraSite.get_site_by_sitename('Default Site').id_site
        db.session.add(base_project2)

        secret_project = TeraProject()
        secret_project.project_name = "Secret Project #1"
        secret_project.id_site = TeraSite.get_site_by_sitename('Top Secret Site').id_site
        db.session.add(secret_project)

        # Commit
        db.session.commit()

    @staticmethod
    def get_count():
        count = db.session.query(db.func.count(TeraSession.id_session))
        return count.first()[0]

    @staticmethod
    def get_session_by_id(ses_id: int):
        return TeraSession.query.filter_by(id_session=ses_id).first()

    @staticmethod
    def get_sessions_for_participant(part_id: int):
        return TeraSession.query.join(TeraSession.session_participants).filter(TeraParticipant.id_participant ==
                                                                               part_id).all()


