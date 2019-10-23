from flask import Flask, request, g
from flask_session import Session
from flask_restful import Api
from libtera.ConfigManager import ConfigManager
from flask_babel import Babel

from modules.BaseModule import BaseModule, ModuleNames
from libtera.db.models.TeraServerSettings import TeraServerSettings

flask_app = Flask("OpenTera")

# Translations
babel = Babel(flask_app)


@babel.localeselector
def get_locale():
    # if a user is logged in, use the locale from the user settings
    user = getattr(g, 'user', None)
    if user is not None:
        return user.locale
    # otherwise try to guess the language from the user accept
    # header the browser transmits.  We support fr/en in this
    # example.  The best match wins.
    return request.accept_languages.best_match(['fr', 'en'])


@babel.timezoneselector
def get_timezone():
    user = getattr(g, 'user', None)
    if user is not None:
        return user.timezone


class FlaskModule(BaseModule):

    def __init__(self,  config: ConfigManager):

        BaseModule.__init__(self, ModuleNames.FLASK_MODULE_NAME.value, config)

        flask_app.debug = True
        # flask_app.secret_key = 'development'
        # Change secret key to use server UUID
        # This is used for session encryption
        flask_app.secret_key = TeraServerSettings.get_server_setting_value(TeraServerSettings.ServerUUID)

        flask_app.config.update({'SESSION_TYPE': 'redis'})
        flask_app.config.update({'BABEL_DEFAULT_LOCALE': 'fr'})
        # TODO set upload folder in config
        # TODO remove this configuration, it is not useful?
        flask_app.config.update({'UPLOAD_FOLDER': 'uploads'})

        # Not sure.
        # flask_app.config.update({'BABEL_DEFAULT_TIMEZONE': 'UTC'})

        self.session = Session(flask_app)
        self.api = Api(flask_app)

        # Init API
        self.init_api()

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

    def init_api(self):
        # Users...
        from .API.user.Login import Login
        from .API.user.Logout import Logout
        from .API.user.QueryUsers import QueryUsers
        from .API.user.QueryForms import QueryForms
        from .API.user.QueryOnlineUsers import QueryOnlineUsers
        from .API.user.QuerySites import QuerySites
        from .API.user.QueryProjects import QueryProjects
        from .API.user.QueryParticipants import QueryParticipants
        from .API.user.QueryDevices import QueryDevices
        from .API.user.QuerySiteAccess import QuerySiteAccess
        from .API.user.QueryDeviceSites import QueryDeviceSites
        from .API.user.QueryDeviceParticipants import QueryDeviceParticipants
        from .API.user.QueryProjectAccess import QueryProjectAccess
        from .API.user.QueryParticipantGroup import QueryParticipantGroup
        from .API.user.QuerySessions import QuerySessions
        from .API.user.QuerySessionTypes import QuerySessionTypes
        from .API.user.QuerySessionEvents import QuerySessionEvents
        from .API.user.QueryDeviceData import QueryDeviceData
        from .API.user.QuerySessionTypeDeviceType import QuerySessionTypeDeviceType
        from .API.user.QuerySessionTypeProject import QuerySessionTypeProject
        self.api.add_resource(Login, '/api/user/login', resource_class_args=[self])
        self.api.add_resource(Logout, '/api/user/logout', resource_class_args=[self])
        self.api.add_resource(QuerySites, '/api/user/sites', resource_class_args=[self])
        self.api.add_resource(QueryUsers, '/api/user/users', resource_class_args=[self])
        self.api.add_resource(QueryForms, '/api/user/forms', resource_class_args=[self])
        self.api.add_resource(QueryOnlineUsers, '/api/user/online', resource_class_args=[self])
        self.api.add_resource(QueryProjects, '/api/user/projects', resource_class_args=[self])
        self.api.add_resource(QueryParticipants, '/api/user/participants', resource_class_args=[self])
        self.api.add_resource(QueryDevices, '/api/user/devices', resource_class_args=[self])
        self.api.add_resource(QueryDeviceSites, '/api/user/devicesites', resource_class_args=[self])
        self.api.add_resource(QueryDeviceParticipants, '/api/user/deviceparticipants', resource_class_args=[self])
        self.api.add_resource(QuerySiteAccess, '/api/user/siteaccess', resource_class_args=[self])
        self.api.add_resource(QueryProjectAccess, '/api/user/projectaccess', resource_class_args=[self])
        self.api.add_resource(QueryParticipantGroup, '/api/user/groups', resource_class_args=[self])
        self.api.add_resource(QuerySessions, '/api/user/sessions', resource_class_args=[self])
        self.api.add_resource(QuerySessionTypes, '/api/user/sessiontypes', resource_class_args=[self])
        self.api.add_resource(QuerySessionTypeDeviceType, '/api/user/sessiontypedevicetypes',
                              resource_class_args=[self])
        self.api.add_resource(QuerySessionTypeProject, '/api/user/sessiontypeprojects',
                              resource_class_args=[self])
        self.api.add_resource(QuerySessionEvents, '/api/user/sessionevents', resource_class_args=[self])
        self.api.add_resource(QueryDeviceData, '/api/user/data', resource_class_args=[self])

        # Devices
        from .API.device.DeviceLogin import DeviceLogin
        from .API.device.DeviceUpload import DeviceUpload
        from .API.device.DeviceRegister import DeviceRegister
        from .API.device.DeviceQuerySessions import DeviceQuerySessions
        from .API.device.DeviceQuerySessionEvents import DeviceQuerySessionEvents

        self.api.add_resource(DeviceLogin, '/api/device/device_login', resource_class_args=[self])
        self.api.add_resource(DeviceUpload, '/api/device/device_upload', resource_class_args=[self])
        self.api.add_resource(DeviceRegister, '/api/device/device_register', resource_class_args=[self])
        self.api.add_resource(DeviceQuerySessions, '/api/device/sessions', resource_class_args=[self])
        self.api.add_resource(DeviceQuerySessionEvents, '/api/device/sessionevents', resource_class_args=[self])

    def init_views(self):
        from .Views.Index import Index
        from .Views.Upload import Upload
        from .Views.Auth import Auth
        from .Views.Participant import Participant
        from .Views.DeviceRegistration import DeviceRegistration

        # Default arguments
        args = []
        kwargs = {'flaskModule': self}

        # Will create a function that calls the __index__ method with args, kwargs
        flask_app.add_url_rule('/', view_func=Index.as_view('index', *args, **kwargs))
        flask_app.add_url_rule('/upload/', view_func=Upload.as_view('upload', *args, **kwargs))
        flask_app.add_url_rule('/auth/', view_func=Auth.as_view('auth', *args, **kwargs))
        flask_app.add_url_rule('/participant/', view_func=Participant.as_view('participant', *args, **kwargs))
        flask_app.add_url_rule('/device_registration', view_func=DeviceRegistration.as_view('device_register', *args,
                                                                                            **kwargs))