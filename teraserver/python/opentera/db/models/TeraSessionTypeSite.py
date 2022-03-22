from opentera.db.Base import db, BaseModel


class TeraSessionTypeSite(db.Model, BaseModel):
    __tablename__ = 't_sessions_types_sites'
    id_session_type_site = db.Column(db.Integer, db.Sequence('id_session_type_site_sequence'), primary_key=True,
                                     autoincrement=True)
    id_session_type = db.Column('id_session_type', db.Integer, db.ForeignKey('t_sessions_types.id_session_type',
                                                                             ondelete='cascade'), nullable=False)
    id_site = db.Column('id_site', db.Integer, db.ForeignKey('t_sites.id_site', ondelete='cascade'), nullable=False)

    session_type_site_session_type = db.relationship("TeraSessionType", viewonly=True)
    session_type_site_site = db.relationship("TeraSite", viewonly=True)

    def to_json(self, ignore_fields=[], minimal=False):
        ignore_fields.extend(['session_type_site_session_type', 'session_type_site_site'])

        if minimal:
            ignore_fields.extend([])

        rval = super().to_json(ignore_fields=ignore_fields)

        return rval

    @staticmethod
    def create_defaults(test=False):
        if test:
            from opentera.db.models.TeraSessionType import TeraSessionType
            from opentera.db.models.TeraSite import TeraSite

            video_session = TeraSessionType.get_session_type_by_id(1)
            sensor_session = TeraSessionType.get_session_type_by_id(2)
            data_session = TeraSessionType.get_session_type_by_id(3)
            exerc_session = TeraSessionType.get_session_type_by_id(4)
            bureau_session = TeraSessionType.get_session_type_by_id(5)

            default_site = TeraSite.get_site_by_sitename('Default Site')
            secret_site = TeraSite.get_site_by_sitename('Top Secret Site')

            sts = TeraSessionTypeSite()
            sts.id_session_type = video_session.id_session_type
            sts.id_site = default_site.id_site
            db.session.add(sts)

            sts = TeraSessionTypeSite()
            sts.id_session_type = sensor_session.id_session_type
            sts.id_site = default_site.id_site
            db.session.add(sts)

            sts = TeraSessionTypeSite()
            sts.id_session_type = data_session.id_session_type
            sts.id_site = default_site.id_site
            db.session.add(sts)

            sts = TeraSessionTypeSite()
            sts.id_session_type = exerc_session.id_session_type
            sts.id_site = default_site.id_site
            db.session.add(sts)

            sts = TeraSessionTypeSite()
            sts.id_session_type = bureau_session.id_session_type
            sts.id_site = default_site.id_site
            db.session.add(sts)

            sts = TeraSessionTypeSite()
            sts.id_session_type = exerc_session.id_session_type
            sts.id_site = secret_site.id_site
            db.session.add(sts)

            db.session.commit()
        else:
            # Automatically associate session types that are in a project to that site
            from opentera.db.models.TeraSessionTypeProject import TeraSessionTypeProject
            for stp in TeraSessionTypeProject.query_with_filters():
                project_site_id = stp.session_type_project_project.id_site
                if not TeraSessionTypeSite.get_session_type_site_for_session_type_and_site(site_id=project_site_id,
                                                                                           session_type_id=
                                                                                           stp.id_session_type):
                    # No association - create a new one
                    st_site = TeraSessionTypeSite()
                    st_site.id_site = project_site_id
                    st_site.id_session_type = stp.id_session_type
                    db.session.add(st_site)
                    db.session.commit()

    @staticmethod
    def get_session_type_site_by_id(sts_id: int):
        return TeraSessionTypeSite.query.filter_by(id_session_type_site=sts_id).first()

    @staticmethod
    def get_sites_for_session_type(session_type_id: int):
        return TeraSessionTypeSite.query.filter_by(id_session_type=session_type_id).all()

    @staticmethod
    def get_sessions_types_for_site(site_id: int):
        return TeraSessionTypeSite.query.filter_by(id_site=site_id).all()

    @staticmethod
    def get_session_type_site_for_session_type_and_site(site_id: int, session_type_id: int):
        return TeraSessionTypeSite.query.filter_by(id_site=site_id, id_session_type=session_type_id).first()

    @staticmethod
    def get_session_type_site_for_site_and_service(site_id: int, service_id: int):
        from opentera.db.models.TeraSessionType import TeraSessionType
        return TeraSessionTypeSite.query.join(TeraSessionType). \
            filter(TeraSessionType.id_service == service_id). \
            filter(TeraSessionTypeSite.id_site == site_id).all()

    def check_integrity(self):
        from opentera.db.models.TeraSessionType import TeraSessionType
        # If that session type is related to a service, make sure that the service is associated to that site
        if self.session_type_site_session_type.session_type_category == \
                TeraSessionType.SessionCategoryEnum.SERVICE.value:
            service_sites = [site.id_site for site in
                             self.session_type_site_session_type.session_type_service.service_sites]
            if self.id_site not in service_sites:
                # We must also associate that service to that site!
                from opentera.db.models.TeraServiceSite import TeraServiceSite
                new_service_site = TeraServiceSite()
                new_service_site.id_service = self.session_type_site_session_type \
                    .session_type_service.id_service
                new_service_site.id_site = self.id_site
                TeraServiceSite.insert(new_service_site)

    @staticmethod
    def delete_with_ids(session_type_id: int, site_id: int):
        delete_obj: TeraSessionTypeSite = TeraSessionTypeSite.query.filter_by(id_session_type=session_type_id,
                                                                              id_site=site_id).first()
        if delete_obj:
            TeraSessionTypeSite.delete(delete_obj.id_session_type_site)

    @classmethod
    def delete(cls, id_todel):
        from opentera.db.models.TeraSessionTypeProject import TeraSessionTypeProject
        # Delete all association with projects for that site
        delete_obj = TeraSessionTypeSite.query.filter_by(id_session_type_site=id_todel).first()

        if delete_obj:
            projects = TeraSessionTypeProject.get_projects_for_session_type(delete_obj.id_session_type)
            for st_project in projects:
                TeraSessionTypeProject.delete(st_project.id_session_type_project)

            # Ok, delete it
            super().delete(id_todel)

    @classmethod
    def insert(cls, sts):
        super().insert(sts)
        sts.check_integrity()

    @classmethod
    def update(cls, update_id: int, values: dict):
        super().update(update_id, values)
        sts = TeraSessionTypeSite.get_session_type_site_by_id(update_id)
        sts.check_integrity()
