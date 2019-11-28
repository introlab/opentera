from libtera.db.Base import db, BaseModel


class TeraSessionTypeProject(db.Model, BaseModel):
    __tablename__ = 't_sessions_types_projects'
    id_session_type_project = db.Column(db.Integer, db.Sequence('id_session_type_project_sequence'), primary_key=True,
                                        autoincrement=True)
    id_session_type = db.Column('id_session_type', db.Integer, db.ForeignKey('t_sessions_types.id_session_type',
                                                                             ondelete='cascade'), nullable=False)
    id_project = db.Column('id_project', db.Integer, db.ForeignKey('t_projects.id_project', ondelete='cascade'),
                           nullable=False)

    session_type_project_session_type = db.relationship("TeraSessionType")
    session_type_project_project = db.relationship("TeraProject")

    def to_json(self, ignore_fields=[], minimal=False):
        ignore_fields.extend(['session_type_project_session_type', 'session_type_project_project'])

        if minimal:
            ignore_fields.extend([])

        rval = super().to_json(ignore_fields=ignore_fields)

        return rval

    @staticmethod
    def create_defaults():
        from libtera.db.models.TeraSessionType import TeraSessionType
        from libtera.db.models.TeraProject import TeraProject

        video_session = TeraSessionType.get_session_type_by_prefix('VIDEO')
        sensor_session = TeraSessionType.get_session_type_by_prefix('SENSOR')
        vsensor_session = TeraSessionType.get_session_type_by_prefix('STREAM')
        robot_session = TeraSessionType.get_session_type_by_prefix('ROBOT')

        project = TeraProject.get_project_by_projectname('Default Project #1')

        stp = TeraSessionTypeProject()
        stp.session_type_project_session_type = video_session
        stp.session_type_project_project = project
        db.session.add(stp)

        stp = TeraSessionTypeProject()
        stp.session_type_project_session_type = sensor_session
        stp.session_type_project_project = project
        db.session.add(stp)

        stp = TeraSessionTypeProject()
        stp.session_type_project_session_type = vsensor_session
        stp.session_type_project_project = project
        db.session.add(stp)

        stp = TeraSessionTypeProject()
        stp.session_type_project_session_type = robot_session
        stp.session_type_project_project = project
        db.session.add(stp)

        db.session.commit()

    @staticmethod
    def get_session_type_project_by_id(stp_id: int):
        return TeraSessionTypeProject.query.filter_by(id_session_type_project=stp_id).first()

    @staticmethod
    def query_projects_for_session_type(session_type_id: int):
        return TeraSessionTypeProject.query.filter_by(id_session_type=session_type_id).all()

    @staticmethod
    def query_sessions_types_for_project(project_id: int):
        return TeraSessionTypeProject.query.filter_by(id_project=project_id).all()

    @staticmethod
    def query_session_type_project_for_session_type_project(project_id: int, session_type_id: int):
        return TeraSessionTypeProject.query.filter_by(id_project=project_id, id_session_type=session_type_id).first()