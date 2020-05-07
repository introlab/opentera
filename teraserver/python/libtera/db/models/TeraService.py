from libtera.db.Base import db, BaseModel

import uuid


class TeraService(db.Model, BaseModel):
    __tablename__ = 't_services'
    id_service = db.Column(db.Integer, db.Sequence('id_service_sequence'), primary_key=True, autoincrement=True)
    service_uuid = db.Column(db.String(36), nullable=False, unique=True)
    service_name = db.Column(db.String, nullable=False)
    service_key = db.Column(db.String, nullable=False)
    service_hostname = db.Column(db.String, nullable=False)
    service_port = db.Column(db.Integer, nullable=False)
    service_endpoint = db.Column(db.String, nullable=False)
    service_clientendpoint = db.Column(db.String, nullable=False)
    service_enabled = db.Column(db.Boolean, nullable=False, default=False)

    service_roles = db.relationship('TeraServiceRole')

    def __init__(self):
        pass

    def __str__(self):
        return '<TeraService ' + str(self.service_name) + ' >'

    def __repr__(self):
        return self.__str__()

    def to_json(self, ignore_fields=None, minimal=False):
        if ignore_fields is None:
            ignore_fields = []

        ignore_fields.extend(['service_roles'])

        if minimal:
            ignore_fields.extend([])

        return super().to_json(ignore_fields=ignore_fields)

    @staticmethod
    def get_service_by_key(key: str):
        service = TeraService.query.filter_by(service_key=key).first()

        if service:
            return service

        return None

    @staticmethod
    def get_service_by_uuid(p_uuid: str):
        service = TeraService.query.filter_by(service_uuid=p_uuid).first()

        if service:
            return service

        return None

    @staticmethod
    def get_service_by_name(name: str):
        return TeraService.query.filter_by(service_name=name).first()

    @staticmethod
    def get_service_by_id(s_id: int):
        return TeraService.query.filter_by(id_service=s_id).first()

    @staticmethod
    def create_defaults():
        new_service = TeraService()
        new_service.service_uuid = str(uuid.uuid4())
        new_service.service_key = 'BureauActif'
        new_service.service_name = 'Bureau Actif'
        new_service.service_hostname = 'localhost'
        new_service.service_port = 4050
        new_service.service_endpoint = '/'
        new_service.service_clientendpoint = '/bureau'
        new_service.service_enabled = True
        db.session.add(new_service)

        new_service = TeraService()
        new_service.service_uuid = str(uuid.uuid4())
        new_service.service_key = 'VideoDispatch'
        new_service.service_name = 'Salle d\'attente vidéo'
        new_service.service_hostname = 'localhost'
        new_service.service_port = 4060
        new_service.service_endpoint = '/'
        new_service.service_clientendpoint = '/videodispatch'
        new_service.service_enabled = True
        db.session.add(new_service)

        new_service = TeraService()
        new_service.service_uuid = str(uuid.uuid4())
        new_service.service_key = 'VideoRehabService'
        new_service.service_name = 'Télé-réadaptation vidéo'
        new_service.service_hostname = 'localhost'
        new_service.service_port = 4070
        new_service.service_endpoint = '/'
        new_service.service_clientendpoint = '/rehab'
        new_service.service_enabled = True
        db.session.add(new_service)

        new_service = TeraService()
        new_service.service_uuid = str(uuid.uuid4())
        new_service.service_key = 'RobotTeleOperationService'
        new_service.service_name = 'Robot Teleoperation Service'
        new_service.service_hostname = 'localhost'
        new_service.service_port = 4080
        new_service.service_endpoint = '/'
        new_service.service_clientendpoint = '/robot'
        new_service.service_enabled = True
        db.session.add(new_service)

        db.session.commit()

    @classmethod
    def insert(cls, service):
        service.service_uuid = str(uuid.uuid4())
        super().insert(service)

