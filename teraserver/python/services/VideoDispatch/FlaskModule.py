from flask import Flask, request, g, url_for
from flask_session import Session
from flask_restx import Api
from .ConfigManager import ConfigManager
from flask_babel import Babel

from modules.BaseModule import BaseModule


flask_app = Flask("VideoDispatchService")

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


# Simple fix for API documentation used with reverse proxy
class CustomAPI(Api):
    @property
    def specs_url(self):
        '''
        The Swagger specifications absolute url (ie. `swagger.json`)

        :rtype: str
        '''

        if 'X-Script-Name' in request.headers:
            return request.headers['X-Script-Name'] + url_for(self.endpoint('specs'), _external=False)
        else:
            return url_for(self.endpoint('specs'), _external=False)

    @property
    def base_url(self):
        '''
        The API base absolute url

        :rtype: str
        '''
        if 'X-Script-Name' in request.headers:
            return request.headers['X-Script-Name'] + url_for(self.endpoint('root'), _external=True)
        else:
            return url_for(self.endpoint('root'), _external=True)

    @property
    def base_path(self):
        '''
        The API path

        :rtype: str
        '''
        if 'X-Script-Name' in request.headers:
            return request.headers['X-Script-Name'] + url_for(self.endpoint('root'), _external=False)
        else:
            return url_for(self.endpoint('root'), _external=False)


api = CustomAPI(flask_app, version='1.0.0', title='VideoDispatchService API',
                description='VideoDispatchService API Documentation', doc='/doc',  prefix='/api',
                authorizations=authorizations)

# Namespaces
default_api_ns = api.namespace('videodispatch', description='default API')


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

        BaseModule.__init__(self, "VideoDispatchService.FlaskModule", config)

        flask_app.debug = config.service_config['debug_mode']
        flask_app.config.update({'SESSION_TYPE': 'redis'})
        import redis
        redis_url = redis.from_url('redis://%(username)s:%(password)s@%(hostname)s:%(port)s/%(db)s'
                                   % self.config.redis_config)

        flask_app.config.update({'SESSION_REDIS': redis_url})
        # This is used for session encryption
        flask_app.secret_key = config.service_config['ServiceUUID']
        flask_app.config.update({'BABEL_DEFAULT_LOCALE': 'fr'})
        # TODO set upload folder in config
        # TODO remove this configuration, it is not useful?
        # flask_app.config.update({'UPLOAD_FOLDER': 'uploads'})

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
        print('VideoDispatchService.FlaskModule - Received message ', pattern, channel, message)
        pass

    def init_api(self):
        # Default arguments
        kwargs = {'flaskModule': self}

        from .API.QuerySessionDispatch import QuerySessionDispatch
        from .API.QueryLogin import QueryLogin
        from .API.QueryStatus import QueryStatus
        from .API.QuerySessionManage import QuerySessionManage

        # Resources
        default_api_ns.add_resource(QuerySessionDispatch, '/sessiondispatch', resource_class_kwargs=kwargs)
        default_api_ns.add_resource(QueryLogin, '/login', resource_class_kwargs=kwargs)
        default_api_ns.add_resource(QueryStatus, '/status', resource_class_kwargs=kwargs)
        default_api_ns.add_resource(QuerySessionManage, '/sessionmanage', resource_class_kwargs=kwargs)

    def init_views(self):
        from .Views.Index import Index
        from .Views.Login import Login
        from .Views.Dashboard import Dashboard
        from .Views.DashboardMain import DashboardMain
        from .Views.Admin import Admin
        from .Views.Participant import Participant
        from .Views.ParticipantEndpoint import ParticipantEndpoint

        # Default arguments
        args = []
        kwargs = {'flaskModule': self}

        # Will create a function that calls the __index__ method with args, kwargs
        flask_app.add_url_rule('/', view_func=Index.as_view('index', *args, **kwargs))
        flask_app.add_url_rule('/login', view_func=Login.as_view('login', *args, **kwargs))
        flask_app.add_url_rule('/dashboard', view_func=Dashboard.as_view('dashboard', *args, **kwargs))
        flask_app.add_url_rule('/dashboard_main', view_func=DashboardMain.as_view('dashboard_main', *args, **kwargs))
        flask_app.add_url_rule('/admin', view_func=Admin.as_view('admin', *args, **kwargs))
        flask_app.add_url_rule('/participant', view_func=Participant.as_view('participant', *args, **kwargs))
        flask_app.add_url_rule('/participant_endpoint', view_func=ParticipantEndpoint.as_view('participant_endpoint',
                                                                                              *args, **kwargs))


@flask_app.after_request
def apply_caching(response):
    # This is required to expose the backend API to rendered webpages from other sources, such as services
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "*"
    return response

