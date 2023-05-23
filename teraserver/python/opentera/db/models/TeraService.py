from opentera.db.Base import BaseModel
from opentera.db.SoftDeleteMixin import SoftDeleteMixin
from sqlalchemy import Column, Integer, String, Sequence, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.exc import IntegrityError

import uuid


class TeraService(BaseModel, SoftDeleteMixin):
    __tablename__ = 't_services'

    id_service = Column(Integer, Sequence('id_service_sequence'), primary_key=True, autoincrement=True)
    service_uuid = Column(String(36), nullable=False, unique=True)
    service_name = Column(String, nullable=False)
    service_key = Column(String, nullable=False, unique=True)
    service_hostname = Column(String, nullable=False)
    service_port = Column(Integer, nullable=False)
    service_endpoint = Column(String, nullable=False)
    service_clientendpoint = Column(String, nullable=False)
    service_endpoint_user = Column(String, nullable=True)
    service_endpoint_participant = Column(String, nullable=True)
    service_endpoint_device = Column(String, nullable=True)
    service_enabled = Column(Boolean, nullable=False, default=False)
    service_system = Column(Boolean, nullable=False, default=False)
    service_editable_config = Column(Boolean, nullable=False, default=False)
    service_default_config = Column(String, nullable=True, default='{}')

    service_roles = relationship('TeraServiceRole', cascade='delete')
    service_projects = relationship('TeraServiceProject', cascade='delete')
    service_sites = relationship('TeraServiceSite', cascade='delete')

    service_created_sessions = relationship("TeraSession", cascade='delete', back_populates='session_creator_service',
                                            passive_deletes=True)

    service_assets = relationship("TeraAsset", cascade='delete', foreign_keys="TeraAsset.id_service",
                                  back_populates='asset_service', passive_deletes=True)

    service_owned_assets = relationship("TeraAsset", cascade='delete', foreign_keys="TeraAsset.asset_service_uuid",
                                        back_populates='asset_service_owner', passive_deletes=True)

    service_tests = relationship("TeraTest", cascade='delete', back_populates='test_service', passive_deletes=True)

    def __init__(self):
        pass

    def __str__(self):
        return '<TeraService ' + str(self.service_name) + ' >'

    def __repr__(self):
        return self.__str__()

    def to_json(self, ignore_fields=None, minimal=False):
        if ignore_fields is None:
            ignore_fields = []

        ignore_fields.extend(['service_roles', 'service_projects', 'service_sites'])

        if minimal:
            ignore_fields.extend(['service_default_config'])

        json_service = super().to_json(ignore_fields=ignore_fields)
        if not minimal:
            # Add roles for that service
            roles = []
            for role in self.service_roles:
                roles.append(role.to_json())
            json_service['service_roles'] = roles
            # Add projects for that service
            service_projects = []
            for sp in self.service_projects:
                service_projects.append(sp.to_json())
            json_service['service_projects'] = service_projects

        if not self.service_endpoint_user:
            del json_service['service_endpoint_user']

        if not self.service_endpoint_participant:
            del json_service['service_endpoint_participant']

        if not self.service_endpoint_device:
            del json_service['service_endpoint_device']

        return json_service

    def get_token(self, token_key: str, expiration=3600):
        import time
        import jwt
        # Creating token with user info
        now = time.time()
        payload = {
            'iat': int(now),
            'exp': int(now) + expiration,
            'iss': 'TeraServer',
            'service_uuid': self.service_uuid
        }

        return jwt.encode(payload, token_key, algorithm='HS256')

    @staticmethod
    def get_service_by_key(key: str, with_deleted: bool = False):
        service = TeraService.query.execution_options(include_deleted=with_deleted).filter_by(service_key=key).first()

        if service:
            return service

        return None

    @staticmethod
    def get_service_by_uuid(p_uuid: str, with_deleted: bool = False):
        service = TeraService.query.execution_options(include_deleted=with_deleted)\
            .filter_by(service_uuid=p_uuid).first()

        if service:
            return service

        return None

    @staticmethod
    def get_service_by_name(name: str, with_deleted: bool = False):
        return TeraService.query.execution_options(include_deleted=with_deleted).filter_by(service_name=name).first()

    @staticmethod
    def get_service_by_id(s_id: int, with_deleted: bool = False):
        return TeraService.query.execution_options(include_deleted=with_deleted).filter_by(id_service=s_id).first()

    @staticmethod
    def get_openteraserver_service():
        return TeraService.get_service_by_key('OpenTeraServer')

    @staticmethod
    def create_defaults(test=False):
        new_service = TeraService()
        new_service.service_uuid = '00000000-0000-0000-0000-000000000001'
        new_service.service_key = 'OpenTeraServer'
        new_service.service_name = 'OpenTera Server'
        new_service.service_hostname = '127.0.0.1'
        new_service.service_port = 4040
        new_service.service_endpoint = '/'
        new_service.service_clientendpoint = '/'
        new_service.service_endpoint_participant = '/participant'
        new_service.service_endpoint_user = '/user'
        new_service.service_endpoint_device = '/device'
        new_service.service_enabled = True
        new_service.service_system = True
        new_service.service_editable_config = True
        TeraService.db().session.add(new_service)

        new_service = TeraService()
        new_service.service_uuid = str(uuid.uuid4())
        new_service.service_key = 'LoggingService'
        new_service.service_name = 'Logging Service'
        new_service.service_hostname = '127.0.0.1'
        new_service.service_port = 4041
        new_service.service_endpoint = '/'
        new_service.service_clientendpoint = '/log'
        new_service.service_enabled = True
        new_service.service_system = True
        TeraService.db().session.add(new_service)

        new_service = TeraService()
        new_service.service_uuid = str(uuid.uuid4())
        new_service.service_key = 'FileTransferService'
        new_service.service_name = 'File Transfer Service'
        new_service.service_hostname = '127.0.0.1'
        new_service.service_port = 4042
        new_service.service_endpoint = '/'
        new_service.service_clientendpoint = '/file'
        new_service.service_enabled = True
        new_service.service_system = True
        TeraService.db().session.add(new_service)

        new_service = TeraService()
        new_service.service_uuid = str(uuid.uuid4())
        new_service.service_key = 'BureauActif'
        new_service.service_name = 'Bureau Actif'
        new_service.service_hostname = '127.0.0.1'
        new_service.service_port = 4050
        new_service.service_endpoint = '/'
        new_service.service_clientendpoint = '/bureau'
        new_service.service_enabled = True
        TeraService.db().session.add(new_service)

        new_service = TeraService()
        new_service.service_uuid = str(uuid.uuid4())
        new_service.service_key = 'VideoRehabService'
        new_service.service_name = 'Télé-réadaptation vidéo'
        new_service.service_hostname = '127.0.0.1'
        new_service.service_port = 4070
        new_service.service_endpoint = '/'
        new_service.service_clientendpoint = '/rehab'
        new_service.service_endpoint_participant = '/participant'
        # Not yet implemented...
        # new_service.service_endpoint_user = '/user'
        # new_service.service_endpoint_device = '/device'
        new_service.service_enabled = True
        new_service.service_editable_config = True
        new_service.service_system = True
        TeraService.db().session.add(new_service)

        new_service = TeraService()
        new_service.service_uuid = str(uuid.uuid4())
        new_service.service_key = 'RobotTeleOperationService'
        new_service.service_name = 'Robot Teleoperation Service'
        new_service.service_hostname = '127.0.0.1'
        new_service.service_port = 4080
        new_service.service_endpoint = '/'
        new_service.service_clientendpoint = '/robot'
        new_service.service_enabled = True
        TeraService.db().session.add(new_service)
        TeraService.db().session.commit()

    def to_json_create_event(self):
        return self.to_json(minimal=False)

    def to_json_update_event(self):
        return self.to_json(minimal=False)

    def to_json_delete_event(self):
        # Minimal information, delete can not be filtered
        return {'id_service': self.id_service, 'service_key': self.service_key}

    @classmethod
    def insert(cls, service):
        service.service_uuid = str(uuid.uuid4())
        super().insert(service)

        # Create default admin-user role for each service
        # from opentera.db.models.TeraServiceRole import TeraServiceRole
        # new_role = TeraServiceRole()
        # new_role.id_service = service.id_service
        # new_role.service_role_name = 'admin'
        # TeraServiceRole.insert(new_role)
        #
        # new_role = TeraServiceRole()
        # new_role.id_service = service.id_service
        # new_role.service_role_name = 'user'
        # TeraServiceRole.insert(new_role)

    def delete_check_integrity(self) -> IntegrityError | None:
        for service_site in self.service_sites:
            if service_site.delete_check_integrity():
                return IntegrityError('Have sessions, assets or tests using that service', self.id_service,
                                      't_sessions')
        return None

    @classmethod
    def update(cls, update_id: int, values: dict):
        # Prevent changes on UUID
        if 'service_uuid' in values:
            del values['service_uuid']

        super().update(update_id, values)
