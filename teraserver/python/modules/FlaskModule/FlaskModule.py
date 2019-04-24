from flask import Flask, request, g
from flask_session import Session
from flask_restful import Api
from libtera.redis.RedisClient import RedisClient
from libtera.ConfigManager import ConfigManager
from flask_babel import Babel

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
    # header the browser transmits.  We support de/fr/en in this
    # example.  The best match wins.
    return request.accept_languages.best_match(['fr', 'en'])


@babel.timezoneselector
def get_timezone():
    user = getattr(g, 'user', None)
    if user is not None:
        return user.timezone


class FlaskModule(RedisClient):

    def __init__(self,  config: ConfigManager):

        self.config = config

        # Init RedisClient
        RedisClient.__init__(self, config=self.config.redis_config)

        flask_app.debug = True
        flask_app.secret_key = 'development'
        flask_app.config.update({'SESSION_TYPE': 'redis'})
        flask_app.config.update({'BABEL_DEFAULT_LOCALE': 'fr'})
        # TODO set upload folder in config
        flask_app.config.update({'UPLOAD_FOLDER': 'uploads'})

        # Not sure.
        # flask_app.config.update({'BABEL_DEFAULT_TIMEZONE': 'UTC'})

        self.session = Session(flask_app)
        self.api = Api(flask_app)

        # Init API
        self.init_api()

        # Init Views
        self.init_views()

    def init_api(self):
        # from .API.Index import Index
        from .API.Login import Login
        from .API.Logout import Logout
        from .API.QueryUsers import QueryUsers
        from .API.QueryForms import QueryForms
        from .API.OnlineUsers import OnlineUsers
        from .API.QuerySites import QuerySites
        from .API.QueryProjects import QueryProjects
        from .API.QueryParticipants import QueryParticipants
        from .API.QueryDevices import QueryDevices
        from .API.QueryKits import QueryKits
        from .API.QuerySiteAccess import QuerySiteAccess
        from .API.QueryKitDevice import QueryKitDevice

        self.api.add_resource(Login, '/api/login', resource_class_args=[self])
        self.api.add_resource(QuerySites, '/api/sites', resource_class_args=[self])
        self.api.add_resource(Logout, '/api/logout', resource_class_args=[self])
        self.api.add_resource(QueryUsers, '/api/users', resource_class_args=[self])
        self.api.add_resource(QueryForms, '/api/forms', resource_class_args=[self])
        self.api.add_resource(OnlineUsers, '/api/online', resource_class_args=[self])
        self.api.add_resource(QueryProjects, '/api/projects', resource_class_args=[self])
        self.api.add_resource(QueryParticipants, '/api/participants', resource_class_args=[self])
        self.api.add_resource(QueryDevices, '/api/devices', resource_class_args=[self])
        self.api.add_resource(QueryKits, '/api/kits', resource_class_args=[self])
        self.api.add_resource(QuerySiteAccess, '/api/siteaccess', resource_class_args=[self])
        self.api.add_resource(QueryKitDevice, '/api/kitdevices', resource_class_args=[self])

    def init_views(self):
        from .Views.Index import Index
        from .Views.Upload import Upload
        from .Views.Auth import Auth
        from .Views.Participant import Participant

        # Default arguments
        args = []
        kwargs = {'flaskModule': self}

        # Will create a function that calls the __index__ method with args, kwargs
        flask_app.add_url_rule('/', view_func=Index.as_view('index', *args, **kwargs))
        flask_app.add_url_rule('/upload/', view_func=Upload.as_view('upload', *args, **kwargs))
        flask_app.add_url_rule('/auth/', view_func=Participant.as_view('auth', *args, **kwargs))
        flask_app.add_url_rule('/participant/', view_func=Participant.as_view('participant', *args, **kwargs))
