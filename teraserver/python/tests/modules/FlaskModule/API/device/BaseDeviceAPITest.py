import unittest
from opentera.db.Base import BaseModel
from opentera.db.models.TeraDevice import TeraDevice
from modules.DatabaseModule.DBManager import DBManager
from modules.LoginModule.LoginModule import LoginModule
from modules.UserManagerModule.UserManagerModule import UserManagerModule
from opentera.config.ConfigManager import ConfigManager
from opentera.modules.BaseModule import BaseModule, ModuleNames
from flask.testing import FlaskClient
from opentera.redis.RedisVars import RedisVars
from opentera.db.models.TeraServerSettings import TeraServerSettings
from flask_session import Session
from modules.FlaskModule.FlaskModule import flask_app
import redis
from twisted.internet import reactor
from threading import Thread
from datetime import datetime
from opentera.modules.BaseModule import ModuleNames, create_module_message_topic_from_name
import opentera.messages.python as messages
import modules.Globals as Globals
import time


class FakeFlaskModule(BaseModule):
    def __init__(self,  config: ConfigManager):
        BaseModule.__init__(self, ModuleNames.FLASK_MODULE_NAME.value, config)

        flask_app.debug = False
        flask_app.testing = True
        flask_app.secret_key = TeraServerSettings.get_server_setting_value(TeraServerSettings.ServerUUID)
        flask_app.config.update({'SESSION_TYPE': 'redis'})
        redis_url = redis.from_url('redis://%(username)s:%(password)s@%(hostname)s:%(port)s/%(db)s'
                                   % self.config.redis_config)

        flask_app.config.update({'SESSION_REDIS': redis_url})
        flask_app.config.update({'BABEL_DEFAULT_LOCALE': 'fr'})
        flask_app.config.update({'SESSION_COOKIE_SECURE': True})

        # Create session
        self.session = Session(flask_app)


class BaseDeviceAPITest(unittest.TestCase):
    test_endpoint: str = ''
    user_token_key = TeraServerSettings.generate_token_key(32)
    participant_token_key = TeraServerSettings.generate_token_key(32)
    service_token_key = TeraServerSettings.generate_token_key(32)

    @classmethod
    def setUpClass(cls):
        cls._config = BaseDeviceAPITest.getConfig()

        cls._db_man: DBManager = DBManager(cls._config)
        # Setup DB in RAM
        cls._db_man.open_local({}, echo=False, ram=True)
        BaseModel.set_db(cls._db_man.db)

        # Creating default users / tests. Time-consuming, only once per test file.
        cls._db_man.create_defaults(cls._config, test=True)

        # This is needed for Logins and tokens
        cls._login_module = LoginModule(cls._config)
        Globals.login_module = cls._login_module    # TODO: Create a fake logger so we don't actually log?

        # This is needed for User management
        cls._user_manager_module = UserManagerModule(cls._config)

    @classmethod
    def tearDownClass(cls):
        cls._config = None
        cls._db_man.db.session.remove()
        cls._db_man = None
        LoginModule.redis_client = None

    @classmethod
    def getConfig(cls) -> ConfigManager:
        config = ConfigManager()
        config.create_defaults()
        return config

    def setUp(self):
        # Setup required keys
        self.setup_redis_keys()
        # self.session = db.create_scoped_session()

    def tearDown(self):
        # Make sure pending queries are rolled backed.
        # self.session.remove()
        pass

    def setup_redis_keys(self):
        # Initialize keys (create only if not found)
        # Service (dynamic)
        if not LoginModule.redis_client.exists(RedisVars.RedisVar_ServiceTokenAPIKey):
            LoginModule.redis_client.set(RedisVars.RedisVar_ServiceTokenAPIKey, self.service_token_key)
        else:
            self.service_token_key = LoginModule.redis_client.get(RedisVars.RedisVar_ServiceTokenAPIKey).decode('utf-8')

        # User (dynamic)
        if not LoginModule.redis_client.exists(RedisVars.RedisVar_UserTokenAPIKey):
            LoginModule.redis_client.set(RedisVars.RedisVar_UserTokenAPIKey, self.user_token_key)
        else:
            self.user_token_key = LoginModule.redis_client.get(RedisVars.RedisVar_UserTokenAPIKey).decode('utf-8')

        # Participant (dynamic)
        if not LoginModule.redis_client.exists(RedisVars.RedisVar_ParticipantTokenAPIKey):
            LoginModule.redis_client.set(RedisVars.RedisVar_ParticipantTokenAPIKey, self.participant_token_key)
        else:
            self.participant_token_key = LoginModule.redis_client.get(
                RedisVars.RedisVar_ParticipantTokenAPIKey).decode('utf-8')

        if not LoginModule.redis_client.exists(RedisVars.RedisVar_DeviceTokenAPIKey):
            LoginModule.redis_client.set(RedisVars.RedisVar_DeviceTokenAPIKey,
                                         TeraServerSettings.get_server_setting_value(
                                             TeraServerSettings.ServerDeviceTokenKey))

        if not LoginModule.redis_client.exists(RedisVars.RedisVar_DeviceStaticTokenAPIKey):
            LoginModule.redis_client.set(RedisVars.RedisVar_DeviceStaticTokenAPIKey,
                                         TeraServerSettings.get_server_setting_value(
                                             TeraServerSettings.ServerDeviceTokenKey))

        if not LoginModule.redis_client.exists(RedisVars.RedisVar_ParticipantStaticTokenAPIKey):
            LoginModule.redis_client.set(RedisVars.RedisVar_ParticipantStaticTokenAPIKey,
                                         TeraServerSettings.get_server_setting_value(
                                             TeraServerSettings.ServerParticipantTokenKey))

    def _simulate_device_online(self, device: TeraDevice):
        self.assertTrue(device.device_enabled)
        self.assertTrue(device.device_onlineable)
        tera_message = messages.TeraModuleMessage()
        tera_message.head.version = 1
        tera_message.head.time = datetime.now().timestamp()
        tera_message.head.seq = 0
        tera_message.head.source = 'device' + device.device_uuid
        tera_message.head.dest = create_module_message_topic_from_name(ModuleNames.USER_MANAGER_MODULE_NAME)

        device_connected = messages.DeviceEvent()
        device_connected.device_uuid = str(device.device_uuid)
        device_connected.device_name = device.device_name
        device_connected.type = messages.DeviceEvent.DEVICE_CONNECTED
        # Need to use Any container
        any_message = messages.Any()
        any_message.Pack(device_connected)
        tera_message.data.extend([any_message])
        # Send device connected message
        self._user_manager_module.handle_device_connected(tera_message.head, device_connected)

    def _simulate_device_offline(self, device: TeraDevice):
        self.assertTrue(device.device_enabled)
        self.assertTrue(device.device_onlineable)
        tera_message = messages.TeraModuleMessage()
        tera_message.head.version = 1
        tera_message.head.time = datetime.now().timestamp()
        tera_message.head.seq = 0
        tera_message.head.source = 'device' + device.device_uuid
        tera_message.head.dest = create_module_message_topic_from_name(ModuleNames.USER_MANAGER_MODULE_NAME)

        device_disconnected = messages.DeviceEvent()
        device_disconnected.device_uuid = str(device.device_uuid)
        device_disconnected.device_name = device.device_name
        device_disconnected.type = messages.DeviceEvent.DEVICE_DISCONNECTED
        # Need to use Any container
        any_message = messages.Any()
        any_message.Pack(device_disconnected)
        tera_message.data.extend([any_message])
        # Send device connected message
        self._user_manager_module.handle_device_disconnected(tera_message.head, device_disconnected)

    def _get_with_device_token_auth(self, client: FlaskClient, token: str = '', params={}, endpoint=None):
        if params is None:
            params = {}
        if endpoint is None:
            endpoint = self.test_endpoint
        headers = {'Authorization': 'OpenTera ' + token}
        return client.get(endpoint, headers=headers, query_string=params)

    def _post_with_device_token_auth(self, client: FlaskClient, token: str = '', json: dict = {},
                                     params: dict = {}, endpoint: str = None):
        if params is None:
            params = {}
        if endpoint is None:
            endpoint = self.test_endpoint
        headers = {'Authorization': 'OpenTera ' + token}
        return client.post(endpoint, headers=headers, query_string=params, json=json)

    def _post_data_no_auth(self, client: FlaskClient, json: dict = None, params: dict = {}, headers: dict = {},
                           data: bytes = None, endpoint: str = None):

        if params is None:
            params = {}
        if endpoint is None:
            endpoint = self.test_endpoint
        if data is not None:
            headers = {'Content-Type': 'application/octet-stream', 'Content-Transfer-Encoding': 'Base64'}

        return client.post(endpoint, headers=headers, query_string=params, json=json, data=data)

    def _delete_with_device_token_auth(self, client: FlaskClient, token: str = '',
                                       params: dict = {}, endpoint: str = None):
        if params is None:
            params = {}
        if endpoint is None:
            endpoint = self.test_endpoint
        headers = {'Authorization': 'OpenTera ' + token}
        return client.delete(endpoint, headers=headers, query_string=params)
