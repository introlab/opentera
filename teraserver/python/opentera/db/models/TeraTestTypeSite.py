from opentera.db.Base import db, BaseModel


class TeraTestTypeSite(db.Model, BaseModel):
    __tablename__ = 't_tests_types_sites'
    id_test_type_site = db.Column(db.Integer, db.Sequence('id_test_type_site_sequence'), primary_key=True,
                                  autoincrement=True)
    id_test_type = db.Column('id_test_type', db.Integer, db.ForeignKey('t_tests_types.id_test_type',
                                                                       ondelete='cascade'), nullable=False)
    id_site = db.Column('id_site', db.Integer, db.ForeignKey('t_sites.id_site', ondelete='cascade'), nullable=False)

    test_type_site_test_type = db.relationship("TeraTestType", viewonly=True)
    test_type_site_site = db.relationship("TeraSite", viewonly=True)

    def to_json(self, ignore_fields=None, minimal=False):
        if ignore_fields is None:
            ignore_fields = []
        ignore_fields.extend(['test_type_site_test_type', 'test_type_site_site'])

        if minimal:
            ignore_fields.extend([])

        rval = super().to_json(ignore_fields=ignore_fields)

        return rval

    @staticmethod
    def create_defaults(test=False):
        if test:
            from opentera.db.models.TeraTestType import TeraTestType
            from opentera.db.models.TeraSite import TeraSite

            pre_test = TeraTestType.get_test_type_by_id(1)
            post_test = TeraTestType.get_test_type_by_id(2)
            general_test = TeraTestType.get_test_type_by_id(3)

            default_site = TeraSite.get_site_by_sitename('Default Site')
            secret_site = TeraSite.get_site_by_sitename('Top Secret Site')

            tts = TeraTestTypeSite()
            tts.id_test_type = pre_test.id_test_type
            tts.id_site = default_site.id_site
            db.session.add(tts)

            tts = TeraTestTypeSite()
            tts.id_test_type = post_test.id_test_type
            tts.id_site = default_site.id_site
            db.session.add(tts)

            tts = TeraTestTypeSite()
            tts.id_test_type = pre_test.id_test_type
            tts.id_site = secret_site.id_site
            db.session.add(tts)

            tts = TeraTestTypeSite()
            tts.id_test_type = general_test.id_test_type
            tts.id_site = secret_site.id_site
            db.session.add(tts)

            db.session.commit()

    @staticmethod
    def get_test_type_site_by_id(tts_id: int):
        return TeraTestTypeSite.query.filter_by(id_test_type_site=tts_id).first()

    @staticmethod
    def get_sites_for_test_type(test_type_id: int):
        return TeraTestTypeSite.query.filter_by(id_test_type=test_type_id).all()

    @staticmethod
    def get_tests_types_for_site(site_id: int):
        return TeraTestTypeSite.query.filter_by(id_site=site_id).all()

    @staticmethod
    def get_test_type_site_for_test_type_and_site(site_id: int, test_type_id: int):
        return TeraTestTypeSite.query.filter_by(id_site=site_id, id_test_type=test_type_id).first()

    @staticmethod
    def get_test_type_site_for_site_and_service(site_id: int, service_id: int):
        from opentera.db.models.TeraTestType import TeraTestType
        return TeraTestTypeSite.query.join(TeraTestType). \
            filter(TeraTestType.id_service == service_id). \
            filter(TeraTestTypeSite.id_site == site_id).all()

    def check_integrity(self):
        # If that test type is related to a service, make sure that the service is associated to that site
        service_sites = [site.id_site for site in
                         self.test_type_site_test_type.test_type_service.service_sites]
        if self.id_site not in service_sites:
            # We must also associate that service to that site!
            from opentera.db.models.TeraServiceSite import TeraServiceSite
            new_service_site = TeraServiceSite()
            new_service_site.id_service = self.test_type_site_test_type.test_type_service.id_service
            new_service_site.id_site = self.id_site
            TeraServiceSite.insert(new_service_site)

    @staticmethod
    def delete_with_ids(test_type_id: int, site_id: int):
        delete_obj: TeraTestTypeSite = TeraTestTypeSite.query.filter_by(id_test_type=test_type_id,
                                                                        id_site=site_id).first()
        if delete_obj:
            TeraTestTypeSite.delete(delete_obj.id_test_type_site)

    @classmethod
    def delete(cls, id_todel):
        from opentera.db.models.TeraTestTypeProject import TeraTestTypeProject
        # Delete all association with projects for that site
        delete_obj = TeraTestTypeSite.query.filter_by(id_test_type_site=id_todel).first()

        if delete_obj:
            projects = TeraTestTypeProject.get_projects_for_test_type(delete_obj.id_test_type)
            for tt_project in projects:
                TeraTestTypeProject.delete(tt_project.id_test_type_project)

            # Ok, delete it
            super().delete(id_todel)

    @classmethod
    def insert(cls, tts):
        super().insert(tts)
        tts.check_integrity()

    @classmethod
    def update(cls, update_id: int, values: dict):
        super().update(update_id, values)
        tts = TeraTestTypeSite.get_test_type_site_by_id(update_id)
        tts.check_integrity()
