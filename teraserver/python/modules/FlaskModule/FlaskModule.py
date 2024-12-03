import time
import datetime
from flask import Flask, request, g, url_for
from flask_restx import Api, Namespace
from flask_babel import Babel
import redis

from opentera.config.ConfigManager import ConfigManager
from opentera.modules.BaseModule import BaseModule, ModuleNames
from opentera.db.models.TeraServerSettings import TeraServerSettings
from opentera.OpenTeraServerVersion import opentera_server_version_string
from modules.Globals import opentera_doc_url


# Flask application
flask_app = Flask("TeraServer")


def get_locale():
    # if a user is logged in, use the locale from the user settings
    user = getattr(g, 'user', None)
    if user is not None:
        return user.locale
    # otherwise try to guess the language from the user accept
    # header the browser transmits.  We support fr/en in this
    # example.  The best match wins.
    lang = request.accept_languages.best_match(['fr', 'en'])
    return lang


def get_timezone():
    user = getattr(g, 'user', None)
    if user is not None:
        return user.timezone


# Translations
babel = Babel(flask_app, locale_selector=get_locale, timezone_selector=get_timezone)

# API
authorizations = {
    'basicAuth': {
        'type': 'basic'
    },
    'tokenAuth': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization',
        'description': 'Enter token with the `OpenTera` prefix, e.g. "OpenTera 12345"'
    }
}


# Simple fix for API documentation used with reverse proxy
class CustomAPI(Api):
    @property
    def specs_url(self):
        """
        The Swagger specifications absolute url (ie. `swagger.json`)

        :rtype: str
        """
        return url_for(self.endpoint('specs'), _external=False)


# if doc is set to False, documentation is disabled
api = CustomAPI(flask_app, version=opentera_server_version_string, title='OpenTeraServer API',
                description='TeraServer API Documentation', doc=opentera_doc_url, prefix='/api',
                authorizations=authorizations, security='basicAuth')

# Namespaces
user_api_ns = api.namespace('user', description='API for user calls')
device_api_ns = api.namespace('device', description='API for device calls')
participant_api_ns = api.namespace('participant', description='API for participant calls')
service_api_ns = api.namespace('service', description='API for service calls')
test_api_ns = api.namespace('test', description='API for tests')


class FlaskModule(BaseModule):

    def __init__(self,  config: ConfigManager, test_mode=False):

        BaseModule.__init__(self, ModuleNames.FLASK_MODULE_NAME.value, config)

        # Use debug mode flag
        flask_app.debug = config.server_config['debug_mode']
        self.test_mode = test_mode

        # Change secret key to use server UUID
        # This is used for session encryption
        flask_app.secret_key = TeraServerSettings.get_server_setting_value(TeraServerSettings.ServerUUID)

        flask_app.config.update({'SESSION_TYPE': 'redis'})
        redis_url = redis.from_url('redis://%(username)s:%(password)s@%(hostname)s:%(port)s/%(db)s'
                                   % self.config.redis_config)

        flask_app.config.update({'SESSION_REDIS': redis_url})
        flask_app.config.update({'BABEL_DEFAULT_LOCALE': 'fr'})
        flask_app.config.update({'SESSION_COOKIE_SECURE': True})
        flask_app.config.update({'SESSION_COOKIE_SAMESITE': 'Strict'})
        flask_app.config.update({'PROPAGATE_EXCEPTIONS': flask_app.debug})
        flask_app.config.update({'PERMANENT_SESSION_LIFETIME': datetime.timedelta(minutes=5)})
        # TODO set upload folder in config
        # TODO remove this configuration, it is not useful?
        flask_app.config.update({'UPLOAD_FOLDER': 'uploads'})

        # Not sure.
        # flask_app.config.update({'BABEL_DEFAULT_TIMEZONE': 'UTC'})

        # self.session = Session(flask_app)

        # Init API
        FlaskModule.init_user_api(self, user_api_ns)
        FlaskModule.init_device_api(self, device_api_ns)
        FlaskModule.init_participant_api(self, participant_api_ns)
        FlaskModule.init_service_api(self, service_api_ns)
        if self.test_mode:
            FlaskModule.init_test_api(self, test_api_ns)

        # Init Views
        self.init_views()

    def setup_module_pubsub(self):
        # Additional subscribe
        pass

    def notify_module_messages(self, pattern, channel, message):
        """
        We have received a published message from redis
        """
        print('FlaskModule - Received message ', pattern, channel, message)
        pass

    @staticmethod
    def init_user_api(module: object, namespace: Namespace, additional_args: dict = dict()):

        # Default arguments
        kwargs = {'flaskModule': module}
        kwargs |= additional_args

        # Users...
        from modules.FlaskModule.API.user.UserLogin import UserLogin
        from modules.FlaskModule.API.user.UserLogin2FA import UserLogin2FA
        from modules.FlaskModule.API.user.UserLoginSetup2FA import UserLoginSetup2FA
        from modules.FlaskModule.API.user.UserLoginChangePassword import UserLoginChangePassword
        from modules.FlaskModule.API.user.UserLogout import UserLogout
        from modules.FlaskModule.API.user.UserQueryUsers import UserQueryUsers
        from modules.FlaskModule.API.user.UserQueryUserPreferences import UserQueryUserPreferences
        from modules.FlaskModule.API.user.UserQueryUserGroups import UserQueryUserGroups
        from modules.FlaskModule.API.user.UserQueryForms import UserQueryForms
        from modules.FlaskModule.API.user.UserQueryOnlineUsers import UserQueryOnlineUsers
        from modules.FlaskModule.API.user.UserQueryOnlineParticipants import UserQueryOnlineParticipants
        from modules.FlaskModule.API.user.UserQueryOnlineDevices import UserQueryOnlineDevices
        from modules.FlaskModule.API.user.UserQuerySites import UserQuerySites
        from modules.FlaskModule.API.user.UserQueryProjects import UserQueryProjects
        from modules.FlaskModule.API.user.UserQueryParticipants import UserQueryParticipants
        from modules.FlaskModule.API.user.UserQueryDevices import UserQueryDevices
        from modules.FlaskModule.API.user.UserQuerySiteAccess import UserQuerySiteAccess
        from modules.FlaskModule.API.user.UserQueryDeviceSites import UserQueryDeviceSites
        from modules.FlaskModule.API.user.UserQueryDeviceProjects import UserQueryDeviceProjects
        from modules.FlaskModule.API.user.UserQueryDeviceParticipants import UserQueryDeviceParticipants
        from modules.FlaskModule.API.user.UserQueryProjectAccess import UserQueryProjectAccess
        from modules.FlaskModule.API.user.UserQueryParticipantGroup import UserQueryParticipantGroup
        from modules.FlaskModule.API.user.UserQuerySessions import UserQuerySessions
        from modules.FlaskModule.API.user.UserQuerySessionTypes import UserQuerySessionTypes
        from modules.FlaskModule.API.user.UserQuerySessionEvents import UserQuerySessionEvents
        from modules.FlaskModule.API.user.UserQuerySessionTypeServices import UserQuerySessionTypeServices
        from modules.FlaskModule.API.user.UserQuerySessionTypeSites import UserQuerySessionTypeSites
        from modules.FlaskModule.API.user.UserQuerySessionTypeProjects import UserQuerySessionTypeProjects
        from modules.FlaskModule.API.user.UserQueryDeviceTypes import UserQueryDeviceTypes
        from modules.FlaskModule.API.user.UserQueryDeviceSubTypes import UserQueryDeviceSubTypes
        from modules.FlaskModule.API.user.UserQueryAssets import UserQueryAssets
        from modules.FlaskModule.API.user.UserQueryAssetsArchive import UserQueryAssetsArchive
        from modules.FlaskModule.API.user.UserQueryServices import UserQueryServices
        from modules.FlaskModule.API.user.UserQueryServiceProjects import UserQueryServiceProjects
        from modules.FlaskModule.API.user.UserQueryServiceSites import UserQueryServiceSites
        from modules.FlaskModule.API.user.UserQueryServiceAccess import UserQueryServiceAccess
        from modules.FlaskModule.API.user.UserQueryServiceRoles import UserQueryServiceRole
        from modules.FlaskModule.API.user.UserSessionManager import UserSessionManager
        from modules.FlaskModule.API.user.UserQueryServiceConfigs import UserQueryServiceConfig
        from modules.FlaskModule.API.user.UserQueryStats import UserQueryUserStats
        from modules.FlaskModule.API.user.UserQueryUserUserGroups import UserQueryUserUserGroups
        from modules.FlaskModule.API.user.UserRefreshToken import UserRefreshToken
        from modules.FlaskModule.API.user.UserQueryVersions import UserQueryVersions
        from modules.FlaskModule.API.user.UserQueryTestTypeSites import UserQueryTestTypeSites
        from modules.FlaskModule.API.user.UserQueryTestTypeProjects import UserQueryTestTypeProjects
        from modules.FlaskModule.API.user.UserQueryTestType import UserQueryTestTypes
        from modules.FlaskModule.API.user.UserQueryTests import UserQueryTests
        from modules.FlaskModule.API.user.UserQueryTestsInvitations import UserQueryTestsInvitations
        from modules.FlaskModule.API.user.UserQueryDisconnect import UserQueryDisconnect
        from modules.FlaskModule.API.user.UserQueryServerSettings import UserQueryServerSettings
        # from modules.FlaskModule.API.user.UserQueryUndelete import UserQueryUndelete

        # Resources
        namespace.add_resource(UserQueryAssets,               '/assets', resource_class_kwargs=kwargs)
        namespace.add_resource(UserQueryAssetsArchive,        '/assets/archive', resource_class_kwargs=kwargs)
        namespace.add_resource(UserQueryDevices,              '/devices', resource_class_kwargs=kwargs)
        namespace.add_resource(UserQueryOnlineDevices,        '/devices/online', resource_class_kwargs=kwargs)
        namespace.add_resource(UserQueryDeviceSites,          '/devices/sites', resource_class_kwargs=kwargs)
        namespace.add_resource(UserQueryDeviceProjects,       '/devices/projects', resource_class_kwargs=kwargs)
        namespace.add_resource(UserQueryDeviceParticipants,   '/devices/participants', resource_class_kwargs=kwargs)
        namespace.add_resource(UserQueryDeviceTypes,          '/devicetypes', resource_class_kwargs=kwargs)
        namespace.add_resource(UserQueryDeviceSubTypes,       '/devicesubtypes', resource_class_kwargs=kwargs)
        namespace.add_resource(UserQueryForms,                '/forms', resource_class_kwargs=kwargs)
        namespace.add_resource(UserQueryParticipantGroup,     '/groups', resource_class_kwargs=kwargs)
        namespace.add_resource(UserLogin,                     '/login', resource_class_kwargs=kwargs)
        namespace.add_resource(UserLogin2FA,                  '/login/2fa', resource_class_kwargs=kwargs)
        namespace.add_resource(UserLoginSetup2FA,             '/login/setup_2fa', resource_class_kwargs=kwargs)
        namespace.add_resource(UserLoginChangePassword,       '/login/change_password', resource_class_kwargs=kwargs)
        namespace.add_resource(UserLogout,                    '/logout', resource_class_kwargs=kwargs)
        namespace.add_resource(UserQueryParticipants,         '/participants', resource_class_kwargs=kwargs)
        namespace.add_resource(UserQueryOnlineParticipants,   '/participants/online', resource_class_kwargs=kwargs)
        namespace.add_resource(UserQueryProjectAccess,        '/projectaccess', resource_class_kwargs=kwargs)
        namespace.add_resource(UserQueryProjects,             '/projects', resource_class_kwargs=kwargs)
        namespace.add_resource(UserRefreshToken,              '/refresh_token', resource_class_kwargs=kwargs)
        namespace.add_resource(UserQuerySessions,             '/sessions', resource_class_kwargs=kwargs)
        namespace.add_resource(UserSessionManager,            '/sessions/manager', resource_class_kwargs=kwargs)
        namespace.add_resource(UserQuerySessionTypes,         '/sessiontypes', resource_class_kwargs=kwargs)
        namespace.add_resource(UserQuerySessionTypeProjects,  '/sessiontypes/projects', resource_class_kwargs=kwargs)
        namespace.add_resource(UserQuerySessionTypeSites,     '/sessiontypes/sites', resource_class_kwargs=kwargs)
        namespace.add_resource(UserQuerySessionTypeServices,  '/sessiontypes/services', resource_class_kwargs=kwargs)
        namespace.add_resource(UserQuerySessionEvents,        '/sessions/events', resource_class_kwargs=kwargs)
        namespace.add_resource(UserQueryServerSettings,       '/server/settings', resource_class_kwargs=kwargs)
        namespace.add_resource(UserQueryServices,             '/services', resource_class_kwargs=kwargs)
        namespace.add_resource(UserQueryServiceProjects,      '/services/projects', resource_class_kwargs=kwargs)
        namespace.add_resource(UserQueryServiceSites,         '/services/sites', resource_class_kwargs=kwargs)
        namespace.add_resource(UserQueryServiceAccess,        '/services/access', resource_class_kwargs=kwargs)
        namespace.add_resource(UserQueryServiceConfig,        '/services/configs', resource_class_kwargs=kwargs)
        namespace.add_resource(UserQueryServiceRole,          '/services/roles', resource_class_kwargs=kwargs)
        namespace.add_resource(UserQuerySites,                '/sites', resource_class_kwargs=kwargs)
        namespace.add_resource(UserQuerySiteAccess,           '/siteaccess', resource_class_kwargs=kwargs)
        namespace.add_resource(UserQueryUserStats,            '/stats', resource_class_kwargs=kwargs)
        namespace.add_resource(UserQueryTests,                '/tests', resource_class_kwargs=kwargs)
        namespace.add_resource(UserQueryTestsInvitations,     '/tests/invitations', resource_class_kwargs=kwargs)
        namespace.add_resource(UserQueryTestTypes,            '/testtypes', resource_class_kwargs=kwargs)
        namespace.add_resource(UserQueryTestTypeProjects,     '/testtypes/projects', resource_class_kwargs=kwargs)
        namespace.add_resource(UserQueryTestTypeSites,        '/testtypes/sites', resource_class_kwargs=kwargs)
        namespace.add_resource(UserQueryUsers,                '/users', resource_class_kwargs=kwargs)
        namespace.add_resource(UserQueryOnlineUsers,          '/users/online', resource_class_kwargs=kwargs)
        namespace.add_resource(UserQueryUserGroups,           '/usergroups', resource_class_kwargs=kwargs)
        namespace.add_resource(UserQueryUserUserGroups,       '/users/usergroups', resource_class_kwargs=kwargs)
        namespace.add_resource(UserQueryDisconnect,           '/disconnect', resource_class_kwargs=kwargs)
        namespace.add_resource(UserQueryUserPreferences,      '/users/preferences', resource_class_kwargs=kwargs)
        namespace.add_resource(UserQueryVersions,             '/versions', resource_class_kwargs=kwargs)
        # namespace.add_resource(UserQueryUndelete,             '/undelete', resource_class_kwargs=kwargs)

    @staticmethod
    def init_device_api(module: object, namespace: Namespace, additional_args: dict = dict()):
        # Default arguments
        kwargs = {'flaskModule': module}
        kwargs |= additional_args

        # Devices
        from modules.FlaskModule.API.device.DeviceLogin import DeviceLogin
        from modules.FlaskModule.API.device.DeviceLogout import DeviceLogout
        from modules.FlaskModule.API.device.DeviceRegister import DeviceRegister
        from modules.FlaskModule.API.device.DeviceQuerySessions import DeviceQuerySessions
        from modules.FlaskModule.API.device.DeviceQuerySessionEvents import DeviceQuerySessionEvents
        from modules.FlaskModule.API.device.DeviceQueryDevices import DeviceQueryDevices
        from modules.FlaskModule.API.device.DeviceQueryAssets import DeviceQueryAssets
        from modules.FlaskModule.API.device.DeviceQueryParticipants import DeviceQueryParticipants
        from modules.FlaskModule.API.device.DeviceQueryStatus import DeviceQueryStatus

        # Resources
        namespace.add_resource(DeviceLogin,                 '/login', resource_class_kwargs=kwargs)
        namespace.add_resource(DeviceLogout,                '/logout', resource_class_kwargs=kwargs)
        namespace.add_resource(DeviceRegister,              '/register', resource_class_kwargs=kwargs)
        namespace.add_resource(DeviceQuerySessions,         '/sessions', resource_class_kwargs=kwargs)
        namespace.add_resource(DeviceQuerySessionEvents,    '/sessions/events', resource_class_kwargs=kwargs)
        namespace.add_resource(DeviceQueryDevices,          '/devices', resource_class_kwargs=kwargs)
        namespace.add_resource(DeviceQueryAssets,           '/assets', resource_class_kwargs=kwargs)
        namespace.add_resource(DeviceQueryParticipants,     '/participants', resource_class_kwargs=kwargs)
        namespace.add_resource(DeviceQueryStatus,           '/status', resource_class_kwargs=kwargs)

    @staticmethod
    def init_participant_api(module: object, namespace: Namespace, additional_args: dict = dict()):
        # Default arguments
        kwargs = {'flaskModule': module}
        kwargs |= additional_args

        # Participants
        from modules.FlaskModule.API.participant.ParticipantLogin import ParticipantLogin
        from modules.FlaskModule.API.participant.ParticipantLogout import ParticipantLogout
        from modules.FlaskModule.API.participant.ParticipantQueryDevices import ParticipantQueryDevices
        from modules.FlaskModule.API.participant.ParticipantQueryParticipants import ParticipantQueryParticipants
        from modules.FlaskModule.API.participant.ParticipantQuerySessions import ParticipantQuerySessions
        from modules.FlaskModule.API.participant.ParticipantRefreshToken import ParticipantRefreshToken
        from modules.FlaskModule.API.participant.ParticipantQueryAssets import ParticipantQueryAssets
        # Resources
        namespace.add_resource(ParticipantLogin,               '/login', resource_class_kwargs=kwargs)
        namespace.add_resource(ParticipantLogout,              '/logout', resource_class_kwargs=kwargs)
        namespace.add_resource(ParticipantQueryAssets,         '/assets', resource_class_kwargs=kwargs)
        namespace.add_resource(ParticipantQueryDevices,        '/devices', resource_class_kwargs=kwargs)
        namespace.add_resource(ParticipantQueryParticipants,   '/participants', resource_class_kwargs=kwargs)
        namespace.add_resource(ParticipantQuerySessions,       '/sessions', resource_class_kwargs=kwargs)
        namespace.add_resource(ParticipantRefreshToken,        '/refresh_token', resource_class_kwargs=kwargs)

    @staticmethod
    def init_service_api(module: object, namespace: Namespace, additional_args: dict = dict()):
        # Default arguments
        kwargs = {'flaskModule': module}
        kwargs |= additional_args

        # Services
        from modules.FlaskModule.API.service.ServiceQueryParticipants import ServiceQueryParticipants
        from modules.FlaskModule.API.service.ServiceQueryAssets import ServiceQueryAssets
        from modules.FlaskModule.API.service.ServiceQuerySessions import ServiceQuerySessions
        from modules.FlaskModule.API.service.ServiceQuerySessionEvents import ServiceQuerySessionEvents
        from modules.FlaskModule.API.service.ServiceQuerySiteProjectAccessRoles \
            import ServiceQuerySiteProjectAccessRoles
        from modules.FlaskModule.API.service.ServiceQueryUsers import ServiceQueryUsers
        from modules.FlaskModule.API.service.ServiceQueryServices import ServiceQueryServices
        from modules.FlaskModule.API.service.ServiceQueryProjects import ServiceQueryProjects
        from modules.FlaskModule.API.service.ServiceQuerySites import ServiceQuerySites
        from modules.FlaskModule.API.service.ServiceSessionManager import ServiceSessionManager
        from modules.FlaskModule.API.service.ServiceQuerySessionTypes import ServiceQuerySessionTypes
        from modules.FlaskModule.API.service.ServiceQuerySessionTypeProjects import ServiceQuerySessionTypeProjects
        from modules.FlaskModule.API.service.ServiceQueryDevices import ServiceQueryDevices
        from modules.FlaskModule.API.service.ServiceQueryTestTypes import ServiceQueryTestTypes
        from modules.FlaskModule.API.service.ServiceQueryTestTypeProjects import ServiceQueryTestTypeProjects
        from modules.FlaskModule.API.service.ServiceQueryTests import ServiceQueryTests
        from modules.FlaskModule.API.service.ServiceQueryAccess import ServiceQueryAccess
        from modules.FlaskModule.API.service.ServiceQueryDisconnect import ServiceQueryDisconnect
        from modules.FlaskModule.API.service.ServiceQueryRoles import ServiceQueryRoles
        from modules.FlaskModule.API.service.ServiceQueryServiceAccess import ServiceQueryServiceAccess
        from modules.FlaskModule.API.service.ServiceQueryUserGroups import ServiceQueryUserGroups
        from modules.FlaskModule.API.service.ServiceQueryParticipantGroups import ServiceQueryParticipantGroups

        namespace.add_resource(ServiceQueryAccess,                  '/access', resource_class_kwargs=kwargs)
        namespace.add_resource(ServiceQueryAssets,                  '/assets', resource_class_kwargs=kwargs)
        namespace.add_resource(ServiceQueryDevices,                 '/devices', resource_class_kwargs=kwargs)
        namespace.add_resource(ServiceQueryDisconnect,              '/disconnect', resource_class_kwargs=kwargs)
        namespace.add_resource(ServiceQueryParticipantGroups,       '/groups', resource_class_kwargs=kwargs)
        namespace.add_resource(ServiceQueryParticipants,            '/participants', resource_class_kwargs=kwargs)
        namespace.add_resource(ServiceQueryProjects,                '/projects', resource_class_kwargs=kwargs)
        namespace.add_resource(ServiceQueryRoles,                   '/roles', resource_class_kwargs=kwargs)
        namespace.add_resource(ServiceQueryServiceAccess,           '/serviceaccess', resource_class_kwargs=kwargs)
        namespace.add_resource(ServiceQueryServices,                '/services', resource_class_kwargs=kwargs)
        namespace.add_resource(ServiceQuerySessions,                '/sessions', resource_class_kwargs=kwargs)
        namespace.add_resource(ServiceQuerySessionEvents,           '/sessions/events', resource_class_kwargs=kwargs)
        namespace.add_resource(ServiceSessionManager,               '/sessions/manager', resource_class_kwargs=kwargs)
        namespace.add_resource(ServiceQuerySessionTypes,            '/sessiontypes', resource_class_kwargs=kwargs)
        namespace.add_resource(ServiceQuerySessionTypeProjects,     '/sessiontypes/projects', resource_class_kwargs=kwargs)
        namespace.add_resource(ServiceQuerySites,                   '/sites', resource_class_kwargs=kwargs)
        namespace.add_resource(ServiceQueryTests,                   '/tests', resource_class_kwargs=kwargs)
        namespace.add_resource(ServiceQueryTestTypes,               '/testtypes', resource_class_kwargs=kwargs)
        namespace.add_resource(ServiceQueryTestTypeProjects,        '/testtypes/projects', resource_class_kwargs=kwargs)
        namespace.add_resource(ServiceQueryUserGroups,              '/usergroups', resource_class_kwargs=kwargs)
        namespace.add_resource(ServiceQueryUsers,                   '/users', resource_class_kwargs=kwargs)
        namespace.add_resource(ServiceQuerySiteProjectAccessRoles,  '/users/access', resource_class_kwargs=kwargs)

    @staticmethod
    def init_test_api(module: object, namespace: Namespace, additional_args: dict = dict()):
        # Default arguments
        kwargs = {'flaskModule': module}
        kwargs |= additional_args

        from modules.FlaskModule.API.test.TestDBReset import TestDBReset
        namespace.add_resource(TestDBReset, '/database/reset', resource_class_kwargs=kwargs)

    def init_views(self):
        from modules.FlaskModule.Views.About import About
        from modules.FlaskModule.Views.DisabledDoc import DisabledDoc
        from modules.FlaskModule.Views.LoginView import LoginView
        from modules.FlaskModule.Views.LoginChangePasswordView import LoginChangePasswordView
        from modules.FlaskModule.Views.LoginSetup2FAView import LoginSetup2FAView
        from modules.FlaskModule.Views.LoginValidate2FAView import LoginValidate2FAView

        # Default arguments
        args = []
        kwargs = {'flaskModule': self}

        # About
        flask_app.add_url_rule('/about', view_func=About.as_view('about', *args, **kwargs))

        # Login
        flask_app.add_url_rule('/login', view_func=LoginView.as_view('login', *args, **kwargs))
        flask_app.add_url_rule('/login_change_password', view_func=LoginChangePasswordView.as_view(
            'login_change_password', *args, **kwargs))
        flask_app.add_url_rule('/login_setup_2fa', view_func=LoginSetup2FAView.as_view(
            'login_setup_2fa', *args, **kwargs))
        flask_app.add_url_rule('/login_validate_2fa', view_func=LoginValidate2FAView.as_view(
            'login_validate_2fa', *args, **kwargs))

        if not self.config.server_config['enable_docs']:
            # Disabled docs view
            flask_app.add_url_rule('/doc', view_func=DisabledDoc.as_view('doc', *args, **kwargs))


@flask_app.after_request
def post_process_request(response):
    # This is required to expose the backend API to rendered webpages from other sources, such as services
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "*"

    # Remove WWW-Authenticate from header to prevent browsers to prevent an authentication pop-up
    if response.status_code == 401 and 'WWW-Authenticate' in response.headers:
        del response.headers['WWW-Authenticate']

    # Request processing time
    print(f"Process time: {(time.time() - g.start_time)*1000} ms")
    return response


@flask_app.before_request
def compute_request_time():
    g.start_time = time.time()
