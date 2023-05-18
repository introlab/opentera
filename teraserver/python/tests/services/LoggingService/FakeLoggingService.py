from services.LoggingService.FlaskModule import CustomAPI, authorizations
from requests import Response
from modules.DatabaseModule.DBManager import DBManager
from services.LoggingService.ConfigManager import ConfigManager
from opentera.modules.BaseModule import BaseModule
from opentera.services.ServiceOpenTera import ServiceOpenTera
from opentera.redis.RedisVars import RedisVars
from opentera.services.ServiceAccessManager import ServiceAccessManager
from modules.LoginModule.LoginModule import LoginModule
from flask import Flask
from flask import Response as FlaskResponse
from flask_babel import Babel
import redis
import uuid
from io import BytesIO


class FakeFlaskModule(BaseModule):
    def __init__(self,  config: ConfigManager, flask_app):
        BaseModule.__init__(self, 'FakeFlaskModule', config)

        # Will allow for user api to work
        self.config.server_config = {'hostname': '127.0.0.1', 'port': 40075}

        self.flask_app = flask_app
        self.api = CustomAPI(self.flask_app, version='1.0.0', title='LoggingService API',
                             description='FakeLoggingService API Documentation', doc='/doc', prefix='/api',
                             authorizations=authorizations)

        self.babel = Babel(self.flask_app)

        flask_app.debug = False
        flask_app.testing = True
        flask_app.secret_key = str(uuid.uuid4())  # Normally service UUID
        flask_app.config.update({'SESSION_TYPE': 'redis'})
        redis_url = redis.from_url('redis://%(username)s:%(password)s@%(hostname)s:%(port)s/%(db)s'
                                   % self.config.redis_config)

        flask_app.config.update({'SESSION_REDIS': redis_url})
        flask_app.config.update({'BABEL_DEFAULT_LOCALE': 'fr'})
        flask_app.config.update({'SESSION_COOKIE_SECURE': True})
        self.logging_api_namespace = self.api.namespace('logging', description='LoggingService API')
        self.service_api_namespace = self.api.namespace('service', description='Fake TeraServer service API')
        self.user_api_namespace = self.api.namespace('user', description='Fake TeraServer user API')
        self.participant_api_namespace = self.api.namespace('participant',
                                                            description='Fake TeraServer participant API')
        self.device_api_namespace = self.api.namespace('device', description='Fake TeraServer device API')

        self.setup_fake_logging_api(flask_app)
        self.setup_fake_service_api(flask_app)
        self.setup_fake_user_api(flask_app)
        self.setup_fake_participant_api(flask_app)
        self.setup_fake_device_api(flask_app)

    def setup_fake_logging_api(self, flask_app):
        from services.LoggingService.FlaskModule import FlaskModule
        with flask_app.app_context():
            # Setup Fake Service API
            kwargs = {'flaskModule': self,
                      'test': True}
            FlaskModule.init_api(self, self.logging_api_namespace, kwargs)

    def setup_fake_service_api(self, flask_app):
        from modules.FlaskModule.FlaskModule import FlaskModule
        with flask_app.app_context():
            # Setup Fake Service API
            kwargs = {'flaskModule': self,
                      'test': True}

            # The trick is to initialize main server api to thew newly created namespace
            FlaskModule.init_service_api(self, self.service_api_namespace, kwargs)

    def setup_fake_user_api(self, flask_app):
        from modules.FlaskModule.FlaskModule import FlaskModule
        with flask_app.app_context():
            # Setup Fake Service API
            kwargs = {'flaskModule': self,
                      'test': True}

            # The trick is to initialize main server api to thew newly created namespace
            FlaskModule.init_user_api(self, self.user_api_namespace, kwargs)

    def setup_fake_participant_api(self, flask_app):
        from modules.FlaskModule.FlaskModule import FlaskModule
        with flask_app.app_context():
            # Setup Fake API
            kwargs = {'flaskModule': self,
                      'test': True}

            # The trick is to initialize main server api to the newly created namespace
            FlaskModule.init_participant_api(self, self.participant_api_namespace, kwargs)

    def setup_fake_device_api(self, flask_app):
        from modules.FlaskModule.FlaskModule import FlaskModule
        with flask_app.app_context():
            # Setup Fake API
            kwargs = {'flaskModule': self,
                      'test': True}

            # The trick is to initialize main server api to the newly created namespace
            FlaskModule.init_device_api(self, self.device_api_namespace, kwargs)


class FakeLoggingService(ServiceOpenTera):
    """
        The only thing we want here is a way to simulate communication with the base server.
        We will simulate the service API with the database.
    """
    service_token = str()

    def __init__(self, db=None):
        self.flask_app = Flask('FakeLoggingService')
        self.config_man = ConfigManager()
        self.config_man.create_defaults()
        self.db_manager = DBManager(self.config_man, self.flask_app)
        # Cheating on db (reusing already opened from test)
        if db is not None:
            self.db_manager.db = db
        else:
            self.db_manager.open_local({}, echo=False, ram=True)

        with self.flask_app.app_context():
            # Update redis vars and basic token
            self.db_manager.create_defaults(self.config_man, test=True)

            self.setup_service_access_manager()

            # Redis variables & db must be initialized before
            ServiceOpenTera.__init__(self, self.config_man, {'service_key': 'LoggingService'})

            self.login_module = LoginModule(self.config_man, self.flask_app)

            from opentera.db.models.TeraService import TeraService
            logging_service: TeraService = TeraService.get_service_by_key('LoggingService')

            # Use LoggingService UUID
            if logging_service:
                self.config['ServiceUUID'] = logging_service.service_uuid
                self.config_man.service_config['ServiceUUID'] = logging_service.service_uuid

        # Setup modules
        self.flask_module = FakeFlaskModule(self.config_man, self.flask_app)
        self.test_client = self.flask_app.test_client()

        self.service_token = self.generate_service_token()

    def generate_service_token(self) -> str:
        with self.flask_app.app_context():
            # Use redis key to generate token
            # Fake service uuid
            from opentera.db.models.TeraService import TeraService
            logging_service: TeraService = TeraService.get_service_by_key('LoggingService')
            if logging_service:
                return logging_service.get_token(ServiceAccessManager.api_service_token_key)
            else:
                return ''

    def setup_service_access_manager(self):
        from opentera.db.models.TeraServerSettings import TeraServerSettings

        self.redis = redis.Redis(host=self.config_man.redis_config['hostname'],
                                 port=self.config_man.redis_config['port'],
                                 db=self.config_man.redis_config['db'],
                                 username=self.config_man.redis_config['username'],
                                 password=self.config_man.redis_config['password'],
                                 client_name=self.__class__.__name__)

        # Initialize service from redis, posing as FileTransferService
        # User token key (dynamic)
        ServiceAccessManager.api_user_token_key = 'test_api_user_token_key'
        self.redis.set(RedisVars.RedisVar_UserTokenAPIKey,
                       ServiceAccessManager.api_user_token_key)

        # Participant token key from DB (static)
        ServiceAccessManager.api_participant_static_token_key = TeraServerSettings.get_server_setting_value(
            TeraServerSettings.ServerParticipantTokenKey)
        self.redis.set(RedisVars.RedisVar_ParticipantStaticTokenAPIKey,
                       ServiceAccessManager.api_participant_static_token_key)

        # Participant token key (dynamic)
        ServiceAccessManager.api_participant_token_key = 'test_api_participant_token_key'
        self.redis.set(RedisVars.RedisVar_ParticipantTokenAPIKey,
                       ServiceAccessManager.api_participant_token_key)

        # Device Token Key from DB (static)
        ServiceAccessManager.api_device_static_token_key = TeraServerSettings.get_server_setting_value(
            TeraServerSettings.ServerDeviceTokenKey)
        self.redis.set(RedisVars.RedisVar_DeviceStaticTokenAPIKey, ServiceAccessManager.api_device_static_token_key)

        # Device Token Key (dynamic)
        ServiceAccessManager.api_device_token_key = 'test_api_device_token_key'
        self.redis.set(RedisVars.RedisVar_DeviceTokenAPIKey, ServiceAccessManager.api_device_token_key)

        # Service Token Key (dynamic)
        ServiceAccessManager.api_service_token_key = 'test_api_service_token_key'
        self.redis.set(RedisVars.RedisVar_ServiceTokenAPIKey, ServiceAccessManager.api_service_token_key)
        ServiceAccessManager.config_man = self.config_man

    def get_users_uuids(self):
        from opentera.db.models.TeraUser import TeraUser
        return [user.user_uuid for user in TeraUser.query.all() if user.user_enabled]

    def get_enabled_users(self):
        from opentera.db.models.TeraUser import TeraUser
        return [user for user in TeraUser.query.all() if user.user_enabled]

    @staticmethod
    def convert_to_standard_request_response(flask_response: FlaskResponse):
        result = Response()
        result.status_code = flask_response.status_code
        result.headers = flask_response.headers
        result.encoding = flask_response.content_encoding
        result.raw = BytesIO(flask_response.data)
        return result

    def post_to_opentera(self, api_url: str, json_data: dict) -> Response:
        # Synchronous call to OpenTera fake backend
        request_headers = {'Authorization': 'OpenTera ' + self.service_token}
        answer = self.test_client.post(api_url, headers=request_headers, json=json_data)
        return FakeLoggingService.convert_to_standard_request_response(answer)

    def get_from_opentera(self, api_url: str, params: dict) -> Response:
        # Synchronous call to OpenTera fake backend
        request_headers = {'Authorization': 'OpenTera ' + self.service_token}
        answer = self.test_client.get(api_url, headers=request_headers, query_string=params)
        return FakeLoggingService.convert_to_standard_request_response(answer)

    def delete_from_opentera(self, api_url: str, params: dict) -> Response:
        # Synchronous call to OpenTera fake backend
        request_headers = {'Authorization': 'OpenTera ' + self.service_token}
        answer = self.test_client.delete(api_url, headers=request_headers, query_string=params)
        return FakeLoggingService.convert_to_standard_request_response(answer)


if __name__ == '__main__':
    from opentera.db.models.TeraParticipant import TeraParticipant
    service = FakeLoggingService()
    with service.flask_app.app_context():
        participant = TeraParticipant.get_participant_by_id(1)
        response = service.get_from_opentera('/api/service/participants',
                                             {'participant_uuid': participant.participant_uuid})
        print(response)
