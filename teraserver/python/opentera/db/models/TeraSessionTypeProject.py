from opentera.db.Base import db, BaseModel


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
    def create_defaults(test=False):
        if test:
            from opentera.db.models.TeraSessionType import TeraSessionType
            from opentera.db.models.TeraProject import TeraProject

            video_session = TeraSessionType.get_session_type_by_id(1)
            sensor_session = TeraSessionType.get_session_type_by_id(2)
            data_session = TeraSessionType.get_session_type_by_id(3)
            exerc_session = TeraSessionType.get_session_type_by_id(4)
            bureau_session = TeraSessionType.get_session_type_by_id(5)

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
            stp.session_type_project_session_type = data_session
            stp.session_type_project_project = project
            db.session.add(stp)

            stp = TeraSessionTypeProject()
            stp.session_type_project_session_type = exerc_session
            stp.session_type_project_project = project
            db.session.add(stp)

            stp = TeraSessionTypeProject()
            stp.session_type_project_session_type = bureau_session
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

    def check_integrity(self):
        from opentera.db.models.TeraSessionType import TeraSessionType
        # If that session type is related to a service, make sure that the service is associated to that project
        if self.session_type_project_session_type.session_type_category == \
                TeraSessionType.SessionCategoryEnum.SERVICE.value:
            service_projects = [proj.id_project for proj in
                                self.session_type_project_session_type.session_type_service.service_projects]
            if self.id_project not in service_projects:
                # We must also associate that service to that project!
                from opentera.db.models.TeraServiceProject import TeraServiceProject
                new_service_project = TeraServiceProject()
                new_service_project.service_project_service = self.session_type_project_session_type \
                    .session_type_service
                new_service_project.service_project_project = self.session_type_project_project
                TeraServiceProject.insert(new_service_project)

    @classmethod
    def insert(cls, stp):
        super().insert(stp)
        stp.check_integrity()

    @classmethod
    def update(cls, update_id: int, values: dict):
        super().update(update_id, values)
        stp = TeraSessionTypeProject.get_session_type_project_by_id(update_id)
        stp.check_integrity()
