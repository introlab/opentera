from flask import Flask, request, g, url_for
from flask_session import Session
from flask_restplus import Api
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
        return url_for(self.endpoint('specs'), _external=False)

    def _register_doc(self, app_or_blueprint):
        if self._add_specs and self._doc:
            # Register documentation before root if enabled
            app_or_blueprint.add_url_rule(self._doc, 'doc', self.render_doc)
        # This is a hack to avoid a rule on /
        # app_or_blueprint.add_url_rule(self.prefix or '/', 'root', self.render_root)


api = CustomAPI(flask_app, version='1.0.0', title='VideoDispatchService API',
                description='VideoDispatchService API Documentation', doc='/doc',
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

        BaseModule.__init__(self, "VideoDispatchService.FlaskModule", config)

        flask_app.debug = True
        # flask_app.secret_key = 'development'
        # This is used for session encryption
        # TODO Change secret key
        # TODO STORE SECRET IN DB?
        flask_app.secret_key = 'VideoDispatchSecret'

        flask_app.config.update({'SESSION_TYPE': 'redis'})
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

        # from .API.Upload import Upload

        # Resources
        # default_api_ns.add_resource(Upload, '/upload', resource_class_kwargs=kwargs)

    def init_views(self):
        from .Views.Index import Index
        from .Views.Login import Login
        from .Views.Dashboard import Dashboard
        from .Views.DashboardMain import DashboardMain

        # Default arguments
        args = []
        kwargs = {'flaskModule': self}

        # Will create a function that calls the __index__ method with args, kwargs
        flask_app.add_url_rule('/', view_func=Index.as_view('index', *args, **kwargs))
        flask_app.add_url_rule('/login', view_func=Login.as_view('login', *args, **kwargs))
        flask_app.add_url_rule('/dashboard', view_func=Dashboard.as_view('dashboard', *args, **kwargs))
        flask_app.add_url_rule('/dashboard_main', view_func=DashboardMain.as_view('dashboard_main', *args, **kwargs))


@flask_app.after_request
def apply_caching(response):
    # This is required to expose the backend API to rendered webpages from other sources, such as services
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "*"
    return response

