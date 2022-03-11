from opentera.db.Base import db, BaseModel
from sqlalchemy.exc import IntegrityError


class TeraSessionTypeProject(db.Model, BaseModel):
    __tablename__ = 't_sessions_types_projects'
    id_session_type_project = db.Column(db.Integer, db.Sequence('id_session_type_project_sequence'), primary_key=True,
                                        autoincrement=True)
    id_session_type = db.Column('id_session_type', db.Integer, db.ForeignKey('t_sessions_types.id_session_type',
                                                                             ondelete='cascade'), nullable=False)
    id_project = db.Column('id_project', db.Integer, db.ForeignKey('t_projects.id_project', ondelete='cascade'),
                           nullable=False)

    session_type_project_session_type = db.relationship("TeraSessionType", viewonly=True)
    session_type_project_project = db.relationship("TeraProject", viewonly=True)

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
            stp.id_session_type = video_session.id_session_type
            stp.id_project = project.id_project
            db.session.add(stp)

            stp = TeraSessionTypeProject()
            stp.id_session_type = sensor_session.id_session_type
            stp.id_project = project.id_project
            db.session.add(stp)

            stp = TeraSessionTypeProject()
            stp.id_session_type = data_session.id_session_type
            stp.id_project = project.id_project
            db.session.add(stp)

            stp = TeraSessionTypeProject()
            stp.id_session_type = exerc_session.id_session_type
            stp.id_project = project.id_project
            db.session.add(stp)

            stp = TeraSessionTypeProject()
            stp.id_session_type = bureau_session.id_session_type
            stp.id_project = project.id_project
            db.session.add(stp)

            db.session.commit()

    @staticmethod
    def get_session_type_project_by_id(stp_id: int):
        return TeraSessionTypeProject.query.filter_by(id_session_type_project=stp_id).first()

    @staticmethod
    def get_projects_for_session_type(session_type_id: int):
        return TeraSessionTypeProject.query.filter_by(id_session_type=session_type_id).all()

    @staticmethod
    def get_sessions_types_for_project(project_id: int):
        return TeraSessionTypeProject.query.filter_by(id_project=project_id).all()

    @staticmethod
    def get_session_type_project_for_session_type_project(project_id: int, session_type_id: int):
        return TeraSessionTypeProject.query.filter_by(id_project=project_id, id_session_type=session_type_id).first()

    @staticmethod
    def get_session_type_project_for_project_and_service(project_id: int, service_id: int):
        from opentera.db.models.TeraSessionType import TeraSessionType
        return TeraSessionTypeProject.query.join(TeraSessionType).\
            filter(TeraSessionType.id_service == service_id).\
            filter(TeraSessionTypeProject.id_project == project_id).all()

    @staticmethod
    def delete_with_ids(session_type_id: int, project_id: int):
        delete_obj: TeraSessionTypeProject = TeraSessionTypeProject.query.filter_by(id_session_type=session_type_id,
                                                                                    id_project=project_id).first()
        if delete_obj:
            TeraSessionTypeProject.delete(delete_obj.id_session_type_project)

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
                new_service_project.id_service = self.session_type_project_session_type \
                    .session_type_service.id_service
                new_service_project.id_project = self.session_type_project_project.id_project
                TeraServiceProject.insert(new_service_project)

    @classmethod
    def insert(cls, stp):
        # Check if that site of that project has the site associated to it
        from opentera.db.models.TeraSessionTypeSite import TeraSessionTypeSite
        from opentera.db.models.TeraProject import TeraProject
        project = TeraProject.get_project_by_id(project_id=stp.id_project)
        st_site = TeraSessionTypeSite.get_session_type_site_for_session_type_and_site(site_id=project.id_site,
                                                                                      session_type_id=
                                                                                      stp.id_session_type)
        if not st_site:
            raise IntegrityError(params='Session type not associated to project site',
                                 orig='TeraSessionTypeProject.insert', statement='insert')
        super().insert(stp)
        stp.check_integrity()

    @classmethod
    def update(cls, update_id: int, values: dict):
        values = cls.clean_values(values)
        stp = cls.query.filter(getattr(cls, cls.get_primary_key_name()) == update_id).first()  # .update(values)
        stp.from_json(values)
        # Check if that site of that project has the site associated to the session type
        from opentera.db.models.TeraSessionTypeSite import TeraSessionTypeSite
        st_site = TeraSessionTypeSite.get_session_type_site_for_session_type_and_site(
            site_id=stp.session_type_project_project.id_site, session_type_id=stp.id_session_type)
        if not st_site:
            raise IntegrityError(params='Session type not associated to project site',
                                 orig='TeraSessionTypeProject.update', statement='update')

        stp = TeraSessionTypeProject.get_session_type_project_by_id(update_id)
        stp.check_integrity()
        cls.commit()
