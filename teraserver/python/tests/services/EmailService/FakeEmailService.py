from services.EmailService.FlaskModule import CustomAPI, authorizations
from requests import Response
from modules.DatabaseModule.DBManager import DBManager
from services.EmailService.ConfigManager import ConfigManager
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
import opentera.messages.python as messages


class FakeFlaskModule(BaseModule):
    def __init__(self,  config: ConfigManager, flask_app):
        BaseModule.__init__(self, 'FakeFlaskModule', config)

        # Will allow for user api to work
        self.config.server_config = {'hostname': '127.0.0.1', 'port': 40075}

        self.flask_app = flask_app
        self.api = CustomAPI(self.flask_app, version='1.0.0', title='EmailService API',
                             description='FakeEmailService API Documentation', doc='/doc', prefix='/api',
                             authorizations=authorizations)

        self.babel = Babel(self.flask_app)

        self.flask_app.debug = False
        self.flask_app.testing = True
        self.flask_app.secret_key = str(uuid.uuid4())  # Normally service UUID
        self.flask_app.config.update({'SESSION_TYPE': 'redis'})
        redis_url = redis.from_url('redis://%(username)s:%(password)s@%(hostname)s:%(port)s/%(db)s'
                                   % self.config.redis_config)

        self.flask_app.config.update({'SESSION_REDIS': redis_url})
        self.flask_app.config.update({'BABEL_DEFAULT_LOCALE': 'fr'})
        self.flask_app.config.update({'SESSION_COOKIE_SECURE': True})
        self.flask_app.config.update({'UPLOAD_FOLDER': '.'})
        self.email_api_namespace = self.api.namespace('', description='EmailService API')
        self.service_api_namespace = self.api.namespace('service', description='Fake EmailService service API')
        self.user_api_namespace = self.api.namespace('user', description='Fake EmailService user API')
        self.participant_api_namespace = self.api.namespace('participant',
                                                            description='Fake EmailService participant API')
        self.device_api_namespace = self.api.namespace('device', description='Fake EmailService device API')
        self.setup_fake_email_api(flask_app)
        self.setup_fake_service_api(flask_app)
        self.setup_fake_user_api(flask_app)
        self.setup_fake_participant_api(flask_app)
        self.setup_fake_device_api(flask_app)

    def setup_fake_email_api(self, flask_app):
        from services.EmailService.FlaskModule import FlaskModule
        with flask_app.app_context():
            # Setup Fake Service API
            kwargs = {'flaskModule': self,
                      'test': True}
            FlaskModule.init_api(self, self.email_api_namespace, kwargs)

    def setup_fake_service_api(self, flask_app):
        from modules.FlaskModule.FlaskModule import FlaskModule
        with flask_app.app_context():
            # Setup Fake API
            kwargs = {'flaskModule': self,
                      'test': True}

            # The trick is to initialize main server api to the newly created namespace
            FlaskModule.init_service_api(self, self.service_api_namespace, kwargs)

    def setup_fake_user_api(self, flask_app):
        from modules.FlaskModule.FlaskModule import FlaskModule
        with flask_app.app_context():
            # Setup Fake API
            kwargs = {'flaskModule': self,
                      'test': True}

            # The trick is to initialize main server api to the newly created namespace
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


class FakeEmailService(ServiceOpenTera):
    """
        The only thing we want here is a way to simulate communication with the base server.
        We will simulate the service API with the database.
    """
    service_token = str()

    def __init__(self, db=None):
        self.flask_app = Flask('FakeEmailService')
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
            ServiceOpenTera.__init__(self, self.config_man, {'service_key': 'EmailService'})

            self.login_module = LoginModule(self.config_man)

            from opentera.db.models.TeraService import TeraService
            email_service: TeraService = TeraService.get_service_by_key('EmailService')

            # Use EmailService UUID
            if email_service:
                self.config['ServiceUUID'] = email_service.service_uuid
                self.config_man.service_config['ServiceUUID'] = email_service.service_uuid

        # Setup modules
        self.flask_module = FakeFlaskModule(self.config_man, self.flask_app)
        self.test_client = self.flask_app.test_client()

        with self.flask_app.app_context():
            self.service_token = self.generate_service_token()

    def generate_service_token(self) -> str:
        with self.flask_app.app_context():
            # Use redis key to generate token
            # Fake service uuid
            from opentera.db.models.TeraService import TeraService
            email_service: TeraService = TeraService.get_service_by_key('EmailService')
            if email_service:
                return email_service.get_token(ServiceAccessManager.api_service_token_key)
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

        # Device Token Key (dynamic = static)
        ServiceAccessManager.api_device_token_key = TeraServerSettings.get_server_setting_value(
            TeraServerSettings.ServerDeviceTokenKey)
        self.redis.set(RedisVars.RedisVar_DeviceTokenAPIKey, ServiceAccessManager.api_device_token_key)

        # Service Token Key (dynamic)
        ServiceAccessManager.api_service_token_key = 'test_api_service_token_key'
        self.redis.set(RedisVars.RedisVar_ServiceTokenAPIKey, ServiceAccessManager.api_service_token_key)
        ServiceAccessManager.config_man = self.config_man

    def get_users_uuids(self):
        with self.flask_app.app_context():
            from opentera.db.models.TeraUser import TeraUser
            return [user.user_uuid for user in TeraUser.query.all() if user.user_enabled]

    def get_enabled_users(self):
        with self.flask_app.app_context():
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

    def post_to_opentera(self, api_url: str, json_data: dict, token=None) -> Response:
        with self.flask_app.app_context():
            # Synchronous call to OpenTera fake backend
            if not token:
                token = self.service_token
            request_headers = {'Authorization': 'OpenTera ' + token}
            answer = self.test_client.post(api_url, headers=request_headers, json=json_data)
            return FakeEmailService.convert_to_standard_request_response(answer)

    def get_from_opentera(self, api_url: str, params: dict, token=None) -> Response:
        with self.flask_app.app_context():
            # Synchronous call to OpenTera fake backend
            if not token:
                token = self.service_token
            request_headers = {'Authorization': 'OpenTera ' + token}
            answer = self.test_client.get(api_url, headers=request_headers, query_string=params)
            return FakeEmailService.convert_to_standard_request_response(answer)

    def delete_from_opentera(self, api_url: str, params: dict, token=None) -> Response:
        with self.flask_app.app_context():
            # Synchronous call to OpenTera fake backend
            if not token:
                token = self.service_token
            request_headers = {'Authorization': 'OpenTera ' + token}
            answer = self.test_client.delete(api_url, headers=request_headers, query_string=params)
            return FakeEmailService.convert_to_standard_request_response(answer)

    def asset_event_received(self, event: messages.DatabaseEvent):
        pass
