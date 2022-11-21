from services.LoggingService.FlaskModule import CustomAPI, authorizations
from requests import Response
from modules.DatabaseModule.DBManager import DBManager
from services.LoggingService.ConfigManager import ConfigManager
from opentera.modules.BaseModule import BaseModule
from opentera.services.ServiceOpenTera import ServiceOpenTera
from opentera.redis.RedisVars import RedisVars
from opentera.services.ServiceAccessManager import ServiceAccessManager
from flask import Flask
from flask_babel import Babel
import redis
import uuid


class FakeFlaskModule(BaseModule):
    def __init__(self,  config: ConfigManager, flask_app):
        BaseModule.__init__(self, 'FakeFlaskModule', config)

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
        self.setup_fake_logging_api(flask_app)
        self.setup_fake_service_api(flask_app)

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


class FakeLoggingService(ServiceOpenTera):
    """
        The only thing we want here is a way to simulate communication with the base server.
        We will simulate the service API with the database.
    """
    service_token = str()

    def __init__(self, db=None):
        self.flask_app = Flask('FakeLoggingService')
        self.service_config = ConfigManager()
        self.service_config.create_defaults()

        from modules.LoginModule.LoginModule import LoginModule
        self.login_module = LoginModule(self.service_config)
        self.db_manager = DBManager(self.service_config, self.flask_app)
        # Cheating on db (reusing already opened from test)
        if db is not None:
            self.db_manager.db = db
        else:
            self.db_manager.open_local({}, echo=False, ram=True)

        with self.flask_app.app_context():
            # Update redis vars and basic token
            self.db_manager.create_defaults(self.service_config, test=True)

            from opentera.db.models.TeraService import TeraService
            logging_service: TeraService = TeraService.get_service_by_key('LoggingService')

            # Use LoggingService UUID
            if logging_service:
                self.service_config.service_config['ServiceUUID'] = logging_service.service_uuid

        # Will need redis from here
        ServiceOpenTera.__init__(self, self.service_config, {})

        # Setup modules
        self.flask_module = FakeFlaskModule(self.service_config, self.flask_app)
        self.test_client = self.flask_app.test_client()

        with self.flask_app.app_context():
            self.setup_service_access_manager()
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

        # Initialize service from redis, posing as LoggingService
        # Update Service Access information
        ServiceAccessManager.api_user_token_key = 'test'
        self.redis.set(RedisVars.RedisVar_UserTokenAPIKey,
                       ServiceAccessManager.api_user_token_key)

        # Participant token key from DB
        ServiceAccessManager.api_participant_token_key = TeraServerSettings.get_server_setting_value(
            TeraServerSettings.ServerParticipantTokenKey)
        self.redis.set(RedisVars.RedisVar_ParticipantTokenAPIKey,
                       ServiceAccessManager.api_participant_token_key)

        ServiceAccessManager.api_participant_static_token_key = 'test'
        self.redis.set(RedisVars.RedisVar_ParticipantStaticTokenAPIKey,
                       ServiceAccessManager.api_participant_static_token_key)

        # Device Token Key from DB
        ServiceAccessManager.api_device_token_key = TeraServerSettings.get_server_setting_value(
            TeraServerSettings.ServerDeviceTokenKey)

        self.redis.set(RedisVars.RedisVar_DeviceTokenAPIKey, ServiceAccessManager.api_device_token_key)

        ServiceAccessManager.api_device_static_token_key = 'test'
        self.redis.set(RedisVars.RedisVar_DeviceStaticTokenAPIKey, ServiceAccessManager.api_device_static_token_key)
        ServiceAccessManager.api_service_token_key = 'test'
        self.redis.set(RedisVars.RedisVar_ServiceTokenAPIKey, ServiceAccessManager.api_service_token_key)
        ServiceAccessManager.config_man = self.config

    def get_users_uuids(self):
        with self.flask_app.app_context():
            from opentera.db.models.TeraUser import TeraUser
            return [user.user_uuid for user in TeraUser.query.all() if user.user_enabled]

    def get_enabled_users(self):
        with self.flask_app.app_context():
            from opentera.db.models.TeraUser import TeraUser
            return [user for user in TeraUser.query.all() if user.user_enabled]

    def post_to_opentera(self, api_url: str, json_data: dict) -> Response:
        with self.flask_app.app_context():
            # Synchronous call to OpenTera fake backend
            request_headers = {'Authorization': 'OpenTera ' + self.service_token}
            return self.test_client.post(api_url, headers=request_headers, json=json_data)

    def get_from_opentera(self, api_url: str, params: dict) -> Response:
        with self.flask_app.app_context():
            # Synchronous call to OpenTera fake backend
            request_headers = {'Authorization': 'OpenTera ' + self.service_token}
            return self.test_client.get(api_url, headers=request_headers, query_string=params)

    def delete_from_opentera(self, api_url: str, params: dict) -> Response:
        with self.flask_app.app_context():
            # Synchronous call to OpenTera fake backend
            request_headers = {'Authorization': 'OpenTera ' + self.service_token}
            return self.test_client.delete(api_url, headers=request_headers, query_string=params)


if __name__ == '__main__':
    from opentera.db.models.TeraParticipant import TeraParticipant
    service = FakeLoggingService()
    with service.flask_app.app_context():
        participant = TeraParticipant.get_participant_by_id(1)
        response = service.get_from_opentera('/api/service/participants',
                                             {'participant_uuid': participant.participant_uuid})
        print(response)
