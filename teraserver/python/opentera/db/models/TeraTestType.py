from opentera.db.Base import db, BaseModel
import uuid


class TeraTestType(db.Model, BaseModel):
    __tablename__ = 't_tests_types'
    id_test_type = db.Column(db.Integer, db.Sequence('id_test_type_sequence'), primary_key=True, autoincrement=True)
    id_service = db.Column(db.Integer, db.ForeignKey("t_services.id_service", ondelete='cascade'), nullable=False)
    test_type_uuid = db.Column(db.String(36), nullable=False, unique=True)
    test_type_name = db.Column(db.String, nullable=False, unique=False)
    test_type_description = db.Column(db.String, nullable=True)
    test_type_key = db.Column(db.String, nullable=True, unique=True)
    # Test type service provides TeraForm style json format?
    test_type_has_json_format = db.Column(db.Boolean, nullable=False, default=False)
    # Test type service provides a generated HTML form?
    test_type_has_web_format = db.Column(db.Boolean, nullable=False, default=False)
    # Test type service provides a web based editor?
    test_type_has_web_editor = db.Column(db.Boolean, nullable=False, default=False)

    test_type_test_type_projects = db.relationship("TeraTestTypeProject", viewonly=True)
    test_type_test_type_sites = db.relationship("TeraTestTypeSite", viewonly=True)

    test_type_service = db.relationship("TeraService")
    test_type_projects = db.relationship("TeraProject", secondary="t_tests_types_projects")
    test_type_sites = db.relationship("TeraSite", secondary="t_tests_types_sites")

    def to_json(self, ignore_fields=None, minimal=False):
        if ignore_fields is None:
            ignore_fields = []
        ignore_fields.extend(['test_type_service', 'test_type_sites', 'test_type_projects',
                              'test_type_test_type_projects', 'test_type_test_type_sites'])

        if minimal:
            ignore_fields.extend(['test_type_description'])
        rval = super().to_json(ignore_fields=ignore_fields)

        if not minimal:
            # Also includes service key and uuid
            rval['test_type_service_key'] = self.test_type_service.service_key
            rval['test_type_service_uuid'] = self.test_type_service.service_uuid
        return rval

    @staticmethod
    def create_defaults(test=False):
        if test:
            from opentera.db.models.TeraService import TeraService

            test = TeraTestType()
            test.test_type_name = 'Pre-session evaluation'
            test.test_type_description = 'Evaluation shown before a session'
            test.id_service = TeraService.get_service_by_key('VideoRehabService').id_service
            test.test_type_uuid = str(uuid.uuid4())
            test.test_type_key = 'PRE'
            test.test_type_has_json_format = True
            db.session.add(test)

            test = TeraTestType()
            test.test_type_name = 'Post-session evaluation'
            test.test_type_description = 'Evaluation shown after a session'
            test.id_service = TeraService.get_service_by_key('VideoRehabService').id_service
            test.test_type_uuid = str(uuid.uuid4())
            test.test_type_has_json_format = True
            test.test_type_has_web_format = True
            db.session.add(test)

            test = TeraTestType()
            test.test_type_name = 'General survey'
            test.test_type_description = 'General satisfaction survey'
            test.id_service = TeraService.get_service_by_key('FileTransferService').id_service
            test.test_type_uuid = str(uuid.uuid4())
            test.test_type_has_web_format = True
            test.test_type_has_web_editor = True
            db.session.add(test)

            db.session.commit()

    @staticmethod
    def get_test_type_by_id(test_type_id: int):
        return TeraTestType.query.filter_by(id_test_type=test_type_id).first()

    @staticmethod
    def get_test_type_by_key(tt_key: int):
        return TeraTestType.query.filter_by(test_type_key=tt_key).first()

    @staticmethod
    def get_test_type_by_uuid(tt_uuid: int):
        return TeraTestType.query.filter_by(test_type_uuid=tt_uuid).first()

    @staticmethod
    def get_test_types_for_service(id_service: int):
        return TeraTestType.query.filter_by(id_service=id_service).all()

    @staticmethod
    def get_access_token(test_type_uuids: list, token_key: str, requester_uuid: str, can_edit: bool, expiration=3600):
        import time
        import jwt

        # Creating token
        now = time.time()
        payload = {
            'iat': int(now),
            'exp': int(now) + expiration,
            'iss': 'TeraServer',
            'test_type_uuids': test_type_uuids,
            'can_edit': can_edit,
            'requester_uuid': requester_uuid
        }

        return jwt.encode(payload, token_key, algorithm='HS256')

    def get_service_urls(self, server_url: str, server_port: int) -> dict:
        urls = {'test_type_json_url': None,
                'test_type_web_url': None,
                'test_type_web_editor_url': None}

        if not self.test_type_service.service_enabled:
            return urls  # Service disabled = no Urls!

        service_endpoint = self.test_type_service.service_clientendpoint
        base_url = 'https://' + server_url + ':' + str(server_port) + service_endpoint

        if self.test_type_has_json_format:
            urls['test_type_json_url'] = base_url + '/api/testtypes/form'

        if self.test_type_has_web_format:
            urls['test_type_web_url'] = base_url + '/api/testtypes/web'

        if self.test_type_has_web_editor:
            urls['test_type_web_editor_url'] = base_url + '/api/testtypes/web/edit'

        return urls

    @classmethod
    def insert(cls, test_type):
        # Generate UUID
        test_type.test_type_uuid = str(uuid.uuid4())

        super().insert(test_type)
