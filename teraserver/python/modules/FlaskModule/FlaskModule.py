from flask import Flask, request, g, url_for
from flask_session import Session
from flask_restx import Api
from opentera.config.ConfigManager import ConfigManager
from flask_babel import Babel
from opentera.modules.BaseModule import BaseModule, ModuleNames
from opentera.db.models.TeraServerSettings import TeraServerSettings
import redis

# Flask application
flask_app = Flask("TeraServer")

# Translations
babel = Babel(flask_app)

# API
authorizations = {
    'HTTPAuth': {
        'type': 'basic',
        'in': 'header'
    },
    'Token Authentication': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization',
        'default': 'OpenTera',
        'bearerFormat': 'JWT'
    }
}


# Simple fix for API documentation used with reverse proxy
class CustomAPI(Api):
    @property
    def specs_url(self):
        '''
        The Swagger specifications absolute url (ie. `swagger.json`)

        :rtype: str
        '''
        return url_for(self.endpoint('specs'), _external=False)


api = CustomAPI(flask_app, version='1.0.0', title='OpenTeraServer API',
                description='TeraServer API Documentation', doc='/doc', prefix='/api',
                authorizations=authorizations)

# Namespaces
user_api_ns = api.namespace('user', description='API for user calls')
device_api_ns = api.namespace('device', description='API for device calls')
participant_api_ns = api.namespace('participant', description='API for participant calls')
service_api_ns = api.namespace('service', descriptino='API for service calls')


@babel.localeselector
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


@babel.timezoneselector
def get_timezone():
    user = getattr(g, 'user', None)
    if user is not None:
        return user.timezone


class FlaskModule(BaseModule):

    def __init__(self,  config: ConfigManager):

        BaseModule.__init__(self, ModuleNames.FLASK_MODULE_NAME.value, config)

        # Use debug mode flag
        flask_app.debug = config.server_config['debug_mode']
        # flask_app.secret_key = 'development'
        # Change secret key to use server UUID
        # This is used for session encryption
        flask_app.secret_key = TeraServerSettings.get_server_setting_value(TeraServerSettings.ServerUUID)

        flask_app.config.update({'SESSION_TYPE': 'redis'})
        redis_url = redis.from_url('redis://%(username)s:%(password)s@%(hostname)s:%(port)s/%(db)s'
                                   % self.config.redis_config)

        flask_app.config.update({'SESSION_REDIS': redis_url})
        flask_app.config.update({'BABEL_DEFAULT_LOCALE': 'fr'})
        flask_app.config.update({'SESSION_COOKIE_SECURE': True})
        # TODO set upload folder in config
        # TODO remove this configuration, it is not useful?
        flask_app.config.update({'UPLOAD_FOLDER': 'uploads'})

        # Not sure.
        # flask_app.config.update({'BABEL_DEFAULT_TIMEZONE': 'UTC'})

        self.session = Session(flask_app)

        # Init API
        self.init_user_api()
        self.init_device_api()
        self.init_participant_api()
        self.init_service_api()

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

    def init_user_api(self):

        # Default arguments
        kwargs = {'flaskModule': self}

        # Users...
        from .API.user.UserLogin import UserLogin
        from .API.user.UserLogout import UserLogout
        from .API.user.UserQueryUsers import UserQueryUsers
        from .API.user.UserQueryUserPreferences import UserQueryUserPreferences
        from .API.user.UserQueryUserGroups import UserQueryUserGroups
        from .API.user.UserQueryForms import UserQueryForms
        from .API.user.UserQueryOnlineUsers import UserQueryOnlineUsers
        from .API.user.UserQueryOnlineParticipants import UserQueryOnlineParticipants
        from .API.user.UserQueryOnlineDevices import UserQueryOnlineDevices
        from .API.user.UserQuerySites import UserQuerySites
        from .API.user.UserQueryProjects import UserQueryProjects
        from .API.user.UserQueryParticipants import UserQueryParticipants
        from .API.user.UserQueryDevices import UserQueryDevices
        from .API.user.UserQuerySiteAccess import UserQuerySiteAccess
        from .API.user.UserQueryDeviceSites import UserQueryDeviceSites
        from .API.user.UserQueryDeviceProjects import UserQueryDeviceProjects
        from .API.user.UserQueryDeviceParticipants import UserQueryDeviceParticipants
        from .API.user.UserQueryProjectAccess import UserQueryProjectAccess
        from .API.user.UserQueryParticipantGroup import UserQueryParticipantGroup
        from .API.user.UserQuerySessions import UserQuerySessions
        from .API.user.UserQuerySessionTypes import UserQuerySessionTypes
        from .API.user.UserQuerySessionEvents import UserQuerySessionEvents
        # from .API.user.UserQueryDeviceData import UserQueryDeviceData
        from .API.user.UserQuerySessionTypeProject import UserQuerySessionTypeProject
        from .API.user.UserQueryDeviceTypes import UserQueryDeviceTypes
        from .API.user.UserQueryDeviceSubTypes import UserQueryDeviceSubTypes
        from .API.user.UserQueryAssets import UserQueryAssets
        from .API.user.UserQueryServices import UserQueryServices
        from .API.user.UserQueryServiceProjects import UserQueryServiceProjects
        from .API.user.UserQueryServiceAccess import UserQueryServiceAccess
        from .API.user.UserSessionManager import UserSessionManager
        from .API.user.UserQueryServiceConfigs import UserQueryServiceConfig
        from .API.user.UserQueryStats import UserQueryUserStats
        from .API.user.UserQueryUserUserGroups import UserQueryUserUserGroups
        from .API.user.UserRefreshToken import UserRefreshToken
        from .API.user.UserQueryVersions import UserQueryVersions

        # Resources
        user_api_ns.add_resource(UserLogin, '/login', resource_class_kwargs=kwargs)
        user_api_ns.add_resource(UserLogout, '/logout', resource_class_kwargs=kwargs)
        user_api_ns.add_resource(UserQuerySites, '/sites', resource_class_kwargs=kwargs)
        user_api_ns.add_resource(UserQueryUsers, '/users', resource_class_kwargs=kwargs)
        user_api_ns.add_resource(UserQueryOnlineUsers, '/users/online', resource_class_kwargs=kwargs)
        user_api_ns.add_resource(UserQueryUserGroups, '/usergroups', resource_class_kwargs=kwargs)
        user_api_ns.add_resource(UserQueryUserUserGroups, '/users/usergroups', resource_class_kwargs=kwargs)
        user_api_ns.add_resource(UserQueryUserPreferences, '/users/preferences', resource_class_kwargs=kwargs)
        user_api_ns.add_resource(UserQueryForms, '/forms', resource_class_kwargs=kwargs)
        user_api_ns.add_resource(UserQueryProjects, '/projects', resource_class_kwargs=kwargs)
        user_api_ns.add_resource(UserQueryParticipants, '/participants', resource_class_kwargs=kwargs)
        user_api_ns.add_resource(UserQueryOnlineParticipants, '/participants/online', resource_class_kwargs=kwargs)
        user_api_ns.add_resource(UserQueryDevices, '/devices', resource_class_kwargs=kwargs)
        user_api_ns.add_resource(UserQueryOnlineDevices, '/devices/online', resource_class_kwargs=kwargs)
        user_api_ns.add_resource(UserQueryDeviceSites, '/devicesites', resource_class_kwargs=kwargs)
        user_api_ns.add_resource(UserQueryDeviceProjects, '/deviceprojects', resource_class_kwargs=kwargs)
        user_api_ns.add_resource(UserQueryDeviceParticipants, '/deviceparticipants', resource_class_kwargs=kwargs)
        user_api_ns.add_resource(UserQuerySiteAccess, '/siteaccess', resource_class_kwargs=kwargs)
        user_api_ns.add_resource(UserQueryProjectAccess, '/projectaccess', resource_class_kwargs=kwargs)
        user_api_ns.add_resource(UserQueryParticipantGroup, '/groups', resource_class_kwargs=kwargs)
        user_api_ns.add_resource(UserQuerySessions,  '/sessions', resource_class_kwargs=kwargs)
        user_api_ns.add_resource(UserSessionManager, '/sessions/manager', resource_class_kwargs=kwargs)
        user_api_ns.add_resource(UserQuerySessionTypes, '/sessiontypes', resource_class_kwargs=kwargs)
        user_api_ns.add_resource(UserQuerySessionTypeProject, '/sessiontypeprojects', resource_class_kwargs=kwargs)
        user_api_ns.add_resource(UserQuerySessionEvents,    '/sessions/events', resource_class_kwargs=kwargs)
        # user_api_ns.add_resource(UserQueryDeviceData,       '/data', resource_class_kwargs=kwargs)
        user_api_ns.add_resource(UserQueryDeviceTypes, '/devicetypes', resource_class_kwargs=kwargs)
        user_api_ns.add_resource(UserQueryDeviceSubTypes,   '/devicesubtypes', resource_class_kwargs=kwargs)
        user_api_ns.add_resource(UserQueryAssets,           '/assets', resource_class_kwargs=kwargs)
        user_api_ns.add_resource(UserQueryServices,         '/services', resource_class_kwargs=kwargs)
        user_api_ns.add_resource(UserQueryServiceProjects,  '/services/projects', resource_class_kwargs=kwargs)
        user_api_ns.add_resource(UserQueryServiceAccess,    '/services/access', resource_class_kwargs=kwargs)
        user_api_ns.add_resource(UserQueryServiceConfig,    '/services/configs', resource_class_kwargs=kwargs)
        user_api_ns.add_resource(UserQueryUserStats,        '/stats', resource_class_kwargs=kwargs)
        user_api_ns.add_resource(UserRefreshToken,          '/refresh_token', resource_class_kwargs=kwargs)
        user_api_ns.add_resource(UserQueryVersions,         '/versions', resource_class_kwargs=kwargs)
        api.add_namespace(user_api_ns)

    def init_device_api(self):
        # Default arguments
        kwargs = {'flaskModule': self}

        # Devices
        from .API.device.DeviceLogin import DeviceLogin
        from .API.device.DeviceLogout import DeviceLogout
        # from .API.device.DeviceUpload import DeviceUpload
        from .API.device.DeviceRegister import DeviceRegister
        from .API.device.DeviceQuerySessions import DeviceQuerySessions
        from .API.device.DeviceQuerySessionEvents import DeviceQuerySessionEvents
        from .API.device.DeviceQueryDevices import DeviceQueryDevices
        from .API.device.DeviceQueryAssets import DeviceQueryAssets
        from .API.device.DeviceQueryParticipants import DeviceQueryParticipants

        # Resources
        # TODO remove legacy endpoint 'device_login'
        device_api_ns.add_resource(DeviceLogin, '/device_login', resource_class_kwargs=kwargs)
        device_api_ns.add_resource(DeviceLogin, '/login', resource_class_kwargs=kwargs)

        # TODO remove legacy endpoint 'device_logout'
        device_api_ns.add_resource(DeviceLogout, '/device_logout', resource_class_kwargs=kwargs)
        device_api_ns.add_resource(DeviceLogout, '/logout', resource_class_kwargs=kwargs)

        # TODO remove legacy endpoint 'device_upload'
        # device_api_ns.add_resource(DeviceUpload, '/device_upload', resource_class_kwargs=kwargs)
        # device_api_ns.add_resource(DeviceUpload, '/upload', resource_class_kwargs=kwargs)

        # TODO remove legacy endpoint 'device_register'
        device_api_ns.add_resource(DeviceRegister, '/device_register', resource_class_kwargs=kwargs)
        device_api_ns.add_resource(DeviceRegister, '/register', resource_class_kwargs=kwargs)

        device_api_ns.add_resource(DeviceQuerySessions, '/sessions', resource_class_kwargs=kwargs)
        device_api_ns.add_resource(DeviceQuerySessionEvents, '/sessionevents', resource_class_kwargs=kwargs)
        device_api_ns.add_resource(DeviceQueryDevices, '/devices', resource_class_kwargs=kwargs)
        device_api_ns.add_resource(DeviceQueryAssets, '/assets', resource_class_kwargs=kwargs)
        device_api_ns.add_resource(DeviceQueryParticipants, '/participants', resource_class_kwargs=kwargs)

        # Finally add namespace
        api.add_namespace(device_api_ns)

    def init_participant_api(self):
        # Default arguments
        kwargs = {'flaskModule': self}

        # Participants
        from .API.participant.ParticipantLogin import ParticipantLogin
        from .API.participant.ParticipantLogout import ParticipantLogout
        # from .API.participant.ParticipantQueryDeviceData import ParticipantQueryDeviceData
        from .API.participant.ParticipantQueryDevices import ParticipantQueryDevices
        from .API.participant.ParticipantQueryParticipants import ParticipantQueryParticipants
        from .API.participant.ParticipantQuerySessions import ParticipantQuerySessions
        from .API.participant.ParticipantRefreshToken import ParticipantRefreshToken
        # Resources
        participant_api_ns.add_resource(ParticipantLogin, '/login', resource_class_kwargs=kwargs)
        participant_api_ns.add_resource(ParticipantLogout, '/logout', resource_class_kwargs=kwargs)
        # participant_api_ns.add_resource(ParticipantQueryDeviceData, '/data', resource_class_kwargs=kwargs)
        participant_api_ns.add_resource(ParticipantQueryDevices, '/devices', resource_class_kwargs=kwargs)
        participant_api_ns.add_resource(ParticipantQueryParticipants, '/participants', resource_class_kwargs=kwargs)
        participant_api_ns.add_resource(ParticipantQuerySessions, '/sessions', resource_class_kwargs=kwargs)
        participant_api_ns.add_resource(ParticipantRefreshToken, '/refresh_token', resource_class_kwargs=kwargs)

        api.add_namespace(participant_api_ns)

    def init_service_api(self):
        # Default arguments
        kwargs = {'flaskModule': self}

        # Services
        from .API.service.ServiceQueryParticipants import ServiceQueryParticipants
        from .API.service.ServiceQueryAssets import ServiceQueryAssets
        from .API.service.ServiceQuerySessions import ServiceQuerySessions
        from .API.service.ServiceQuerySessionEvents import ServiceQuerySessionEvents
        from .API.service.ServiceQuerySiteProjectAccessRoles import ServiceQuerySiteProjectAccessRoles
        from .API.service.ServiceQueryUsers import ServiceQueryUsers

        service_api_ns.add_resource(ServiceQueryParticipants, '/participants', resource_class_kwargs=kwargs)
        service_api_ns.add_resource(ServiceQueryAssets, '/assets', resource_class_kwargs=kwargs)
        service_api_ns.add_resource(ServiceQuerySessions, '/sessions', resource_class_kwargs=kwargs)
        service_api_ns.add_resource(ServiceQuerySessionEvents, '/sessions/events', resource_class_kwargs=kwargs)
        service_api_ns.add_resource(ServiceQuerySiteProjectAccessRoles, '/users/access', resource_class_kwargs=kwargs)
        service_api_ns.add_resource(ServiceQueryUsers, '/users', resource_class_kwargs=kwargs)

        # Add namespace
        api.add_namespace(service_api_ns)

    def init_views(self):

        from .Views.About import About

        # Default arguments
        args = []
        kwargs = {'flaskModule': self}

        # About
        flask_app.add_url_rule('/about', view_func=About.as_view('about', *args, **kwargs))


@flask_app.after_request
def apply_caching(response):
    # This is required to expose the backend API to rendered webpages from other sources, such as services
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "*"
    return response

