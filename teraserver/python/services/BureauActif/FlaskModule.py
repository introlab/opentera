from flask import Flask, request, g
from flask_session import Session
from flask_restx import Api

from .ConfigManager import ConfigManager
from flask_babel import Babel

from modules.BaseModule import BaseModule
import redis


flask_app = Flask("BureauActifService")

# Translations
babel = Babel(flask_app)

# API
# TODO - Fix auth
authorizations = {
    'HTTPAuth': {
        'type': 'basic',
        'in': 'header'
    },
    'Token Authentication': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'OpenTera'
    }
}

api = Api(flask_app,
          version='1.0.0', title='BureauActifService API',
          description='BureauActifService API Documentation', doc='/doc',
          authorizations=authorizations)

# Namespaces
default_api_ns = api.namespace('api', description='default API')


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

        BaseModule.__init__(self, "BureauActifService.FlaskModule", config)

        flask_app.debug = config.service_config['debug_mode']
        flask_app.secret_key = config.service_config['ServiceUUID']

        flask_app.config.update({'SESSION_TYPE': 'redis'})
        redis_url = redis.from_url('redis://%(username)s:%(password)s@%(hostname)s:%(port)s/%(db)s'
                                   % self.config.redis_config)

        flask_app.config.update({'SESSION_REDIS': redis_url})

        flask_app.config.update({'BABEL_DEFAULT_LOCALE': 'fr'})
        # TODO set upload folder in config
        # TODO remove this configuration, it is not useful?
        flask_app.config.update({'UPLOAD_FOLDER': 'uploads'})

        # Not sure.
        # flask_app.config.update({'BABEL_DEFAULT_TIMEZONE': 'UTC'})

        self.session = Session(flask_app)

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
        print('BureauActifService.FlaskModule - Received message ', pattern, channel, message)
        pass

    def init_api(self):
        # Default arguments
        kwargs = {'flaskModule': self}

        from .API.QueryRawData import QueryRawData
        from .API.QueryCalendarData import QueryCalendarData
        from .API.QueryTimelineData import QueryTimelineData
        from .API.QueryLoginType import QueryLoginType
        from .API.QueryServiceInfos import QueryServiceInfos

        # Resources
        default_api_ns.add_resource(QueryRawData, '/rawdata', resource_class_kwargs=kwargs)
        default_api_ns.add_resource(QueryCalendarData, '/calendardata', resource_class_kwargs=kwargs)
        default_api_ns.add_resource(QueryTimelineData, '/timelinedata', resource_class_kwargs=kwargs)
        default_api_ns.add_resource(QueryLoginType, '/me', resource_class_kwargs=kwargs)
        default_api_ns.add_resource(QueryServiceInfos, '/serviceinfos', resource_class_kwargs=kwargs)

    def init_views(self):
        from .Views.Index import Index
        from .Views.Login import Login

        # Default arguments
        args = []
        kwargs = {'flaskModule': self}

        # Will create a function that calls the __index__ method with args, kwargs
        flask_app.add_url_rule('/index', view_func=Index.as_view('index', *args, **kwargs))
        flask_app.add_url_rule('/login', view_func=Login.as_view('login', *args, **kwargs))


@flask_app.after_request
def apply_caching(response):
    # This is required to expose the backend API to rendered webpages from other sources, such as services
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "*"
    return response
