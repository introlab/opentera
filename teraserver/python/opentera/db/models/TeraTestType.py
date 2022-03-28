from opentera.db.Base import db, BaseModel


class TeraTestType(db.Model, BaseModel):
    __tablename__ = 't_tests_types'
    id_test_type = db.Column(db.Integer, db.Sequence('id_test_type_sequence'), primary_key=True, autoincrement=True)
    id_service = db.Column(db.Integer, db.ForeignKey("t_services.id_service"), nullable=False)
    test_type_name = db.Column(db.String, nullable=False, unique=False)
    test_type_description = db.Column(db.String, nullable=True)

    test_type_service = db.relationship("TeraService", cascade='delete')

    def to_json(self, ignore_fields=None, minimal=False):
        if ignore_fields is None:
            ignore_fields = []
        ignore_fields.extend(['test_type_service'])

        if minimal:
            ignore_fields.extend(['test_type_description'])
        rval = super().to_json(ignore_fields=ignore_fields)

        if not minimal:
            # Also includes service key and uuid
            rval['test_type_service_key'] = self.session_type_service.service_key
            rval['test_type_service_uuid'] = self.session_type_service.service_uuid
        return rval

    @staticmethod
    def create_defaults(test=False):
        if test:
            from opentera.db.models.TeraService import TeraService

            test = TeraTestType()
            test.test_type_name = 'Pre-session evaluation'
            test.test_type_description = 'Evaluation shown before a session'
            test.id_service = TeraService.get_service_by_key('VideoRehabService').id_service
            db.session.add(test)

            test = TeraTestType()
            test.test_type_name = 'Post-session evaluation'
            test.test_type_description = 'Evaluation shown after a session'
            test.id_service = TeraService.get_service_by_key('VideoRehabService').id_service
            db.session.add(test)

            test = TeraTestType()
            test.test_type_name = 'General survey'
            test.test_type_description = 'General satisfaction survey'
            test.id_service = TeraService.get_service_by_key('BureauActif').id_service
            db.session.add(test)

            db.session.commit()

    @staticmethod
    def get_test_type_by_id(test_type_id: int):
        return TeraTestType.query.filter_by(test_type_id=test_type_id).first()

    @staticmethod
    def get_test_types_for_service(id_service: int):
        return TeraTestType.query.filter_by(id_service=id_service).all()


