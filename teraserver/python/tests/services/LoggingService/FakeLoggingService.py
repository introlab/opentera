from modules.FlaskModule.FlaskModule import flask_app
from requests import get, post, Response, delete
from modules.DatabaseModule.DBManager import DBManager
from opentera.config.ConfigManager import ConfigManager
from opentera.modules.BaseModule import BaseModule
import redis
from opentera.redis.RedisVars import RedisVars
from flask_session import Session
import uuid
from opentera.services.ServiceAccessManager import ServiceAccessManager


class FakeFlaskModule(BaseModule):
    def __init__(self,  config: ConfigManager):
        BaseModule.__init__(self, 'FlaskModule-test', config)
        flask_app.debug = True
        flask_app.test = True
        flask_app.secret_key = str(uuid.uuid4())  # Normally service UUID
        flask_app.config.update({'SESSION_TYPE': 'redis'})
        redis_url = redis.from_url('redis://%(username)s:%(password)s@%(hostname)s:%(port)s/%(db)s'
                                   % self.config.redis_config)

        flask_app.config.update({'SESSION_REDIS': redis_url})
        flask_app.config.update({'BABEL_DEFAULT_LOCALE': 'fr'})
        flask_app.config.update({'SESSION_COOKIE_SECURE': True})
        flask_app.config.update({'SQLALCHEMY_TRACK_MODIFICATIONS': True})

        # Create session
        self.session = Session(flask_app)
        self.setup_fake_service_api()

    def setup_fake_service_api(self):
        with flask_app.app_context():
            # Setup Fake Service API
            from modules.FlaskModule.FlaskModule import service_api_ns
            # Default arguments
            kwargs = {'flaskModule': self,
                      'test': True}

            # Services
            from modules.FlaskModule.API.service.ServiceQueryParticipants import ServiceQueryParticipants
            from modules.FlaskModule.API.service.ServiceQueryAssets import ServiceQueryAssets
            from modules.FlaskModule.API.service.ServiceQuerySessions import ServiceQuerySessions
            from modules.FlaskModule.API.service.ServiceQuerySessionEvents import ServiceQuerySessionEvents
            from modules.FlaskModule.API.service.ServiceQuerySiteProjectAccessRoles import \
                ServiceQuerySiteProjectAccessRoles
            from modules.FlaskModule.API.service.ServiceQueryUsers import ServiceQueryUsers
            from modules.FlaskModule.API.service.ServiceQueryServices import ServiceQueryServices
            from modules.FlaskModule.API.service.ServiceQueryProjects import ServiceQueryProjects
            from modules.FlaskModule.API.service.ServiceQuerySites import ServiceQuerySites
            from modules.FlaskModule.API.service.ServiceSessionManager import ServiceSessionManager
            from modules.FlaskModule.API.service.ServiceQuerySessionTypes import ServiceQuerySessionTypes
            from modules.FlaskModule.API.service.ServiceQueryDevices import ServiceQueryDevices
            from modules.FlaskModule.API.service.ServiceQueryTestTypes import ServiceQueryTestTypes
            from modules.FlaskModule.API.service.ServiceQueryTests import ServiceQueryTests
            from modules.FlaskModule.API.service.ServiceQueryAccess import ServiceQueryAccess

            service_api_ns.add_resource(ServiceQueryUsers, '/users', resource_class_kwargs=kwargs)
            service_api_ns.add_resource(ServiceQueryParticipants, '/participants', resource_class_kwargs=kwargs)
            service_api_ns.add_resource(ServiceQueryDevices, '/devices', resource_class_kwargs=kwargs)
            service_api_ns.add_resource(ServiceQueryAssets, '/assets', resource_class_kwargs=kwargs)
            service_api_ns.add_resource(ServiceQuerySessions, '/sessions', resource_class_kwargs=kwargs)
            service_api_ns.add_resource(ServiceQuerySessionEvents, '/sessions/events', resource_class_kwargs=kwargs)
            service_api_ns.add_resource(ServiceQuerySiteProjectAccessRoles, '/users/access', resource_class_kwargs=kwargs)
            service_api_ns.add_resource(ServiceQueryServices, '/services', resource_class_kwargs=kwargs)
            service_api_ns.add_resource(ServiceQueryProjects, '/projects', resource_class_kwargs=kwargs)
            service_api_ns.add_resource(ServiceQuerySites, '/sites', resource_class_kwargs=kwargs)
            service_api_ns.add_resource(ServiceSessionManager, '/sessions/manager', resource_class_kwargs=kwargs)
            service_api_ns.add_resource(ServiceQuerySessionTypes, '/sessiontypes', resource_class_kwargs=kwargs)
            service_api_ns.add_resource(ServiceQueryTestTypes, '/testtypes', resource_class_kwargs=kwargs)
            service_api_ns.add_resource(ServiceQueryTests, '/tests', resource_class_kwargs=kwargs)
            service_api_ns.add_resource(ServiceQueryAccess, '/access', resource_class_kwargs=kwargs)

            # Add namespace
            # api.add_namespace(service_api_ns)


class FakeLoggingService:
    """
        The only thing we want here is a way to simulate communication with the base server.
        We will simulate the service API with the database.
    """
    service_token = str()

    def __init__(self):
        self.config = ConfigManager()
        self.config.create_defaults()
        self.redis = redis.Redis(host=self.config.redis_config['hostname'],
                                 port=self.config.redis_config['port'],
                                 username=self.config.redis_config['username'],
                                 password=self.config.redis_config['password'],
                                 db=self.config.redis_config['db'])
        from modules.LoginModule.LoginModule import LoginModule
        self.login_module = LoginModule(self.config)
        # self.flask_module = FakeFlaskModule(self.config)
        self.db_manager = DBManager(self.config)
        self.db_manager.open_local({}, echo=False, ram=True)
        with flask_app.app_context():
            self.db_manager.create_defaults(self.config, test=True)
        self.flask_module = FakeFlaskModule(self.config)
        self.test_client = flask_app.test_client()

        # Update redis vars and basic token
        self.setup_service_access_manager()
        self.service_token = self.generate_service_token()

    def generate_service_token(self) -> str:
        with flask_app.app_context():
            # Use redis key to generate token
            # Fake service uuid
            from opentera.db.models.TeraService import TeraService
            logging_service: TeraService = TeraService.get_service_by_key('LoggingService')
            if logging_service:
                return logging_service.get_token(ServiceAccessManager.api_service_token_key)
            else:
                return ''

    def setup_service_access_manager(self):
        # Initialize service from redis, posing as LoggingService
        # Update Service Access information
        ServiceAccessManager.api_user_token_key = 'test'
        self.redis.set(RedisVars.RedisVar_UserTokenAPIKey,
                       ServiceAccessManager.api_user_token_key)
        ServiceAccessManager.api_participant_token_key = 'test'
        self.redis.set(RedisVars.RedisVar_ParticipantTokenAPIKey,
                       ServiceAccessManager.api_participant_token_key)
        ServiceAccessManager.api_participant_static_token_key = 'test'
        self.redis.set(RedisVars.RedisVar_ParticipantStaticTokenAPIKey,
                       ServiceAccessManager.api_participant_static_token_key)
        ServiceAccessManager.api_device_token_key = 'test'
        self.redis.set(RedisVars.RedisVar_DeviceTokenAPIKey, ServiceAccessManager.api_device_token_key)
        ServiceAccessManager.api_device_static_token_key = 'test'
        self.redis.set(RedisVars.RedisVar_DeviceStaticTokenAPIKey, ServiceAccessManager.api_device_static_token_key)
        ServiceAccessManager.api_service_token_key = 'test'
        self.redis.set(RedisVars.RedisVar_ServiceTokenAPIKey, ServiceAccessManager.api_service_token_key)
        ServiceAccessManager.config_man = self.config

    def post_to_opentera(self, api_url: str, json_data: dict) -> Response:
        # Synchronous call to OpenTera fake backend
        request_headers = {'Authorization': 'OpenTera ' + self.service_token}
        return self.test_client.post(api_url, headers=request_headers, json=json_data)

    def get_from_opentera(self, api_url: str, params: dict) -> Response:
        # Synchronous call to OpenTera fake backend
        request_headers = {'Authorization': 'OpenTera ' + self.service_token}
        return self.test_client.get(api_url, headers=request_headers, query_string=params)

    def delete_from_opentera(self, api_url: str, params: dict) -> Response:
        # Synchronous call to OpenTera fake backend
        request_headers = {'Authorization': 'OpenTera ' + self.service_token}
        return self.test_client.delete(api_url, headers=request_headers, query_string=params)


if __name__ == '__main__':
    from opentera.db.models.TeraParticipant import TeraParticipant
    service = FakeLoggingService()
    with flask_app.app_context():
        participant = TeraParticipant.get_participant_by_id(1)
        response = service.get_from_opentera('/api/service/participants',
                                             {'participant_uuid': participant.participant_uuid})
        print(response)
