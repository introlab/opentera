from flask import Flask, request, g
from flask_session import Session
from flask_restful import Api
from .ConfigManager import ConfigManager
from flask_babel import Babel

from modules.BaseModule import BaseModule


flask_app = Flask("BureauActifService")

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

        BaseModule.__init__(self, "BureauActifService.FlaskModule", config)

        flask_app.debug = True
        # flask_app.secret_key = 'development'
        # This is used for session encryption
        # TODO Change secret key
        # TODO STORE SECRET IN DB?
        flask_app.secret_key = 'BureauActifSecret'

        flask_app.config.update({'SESSION_TYPE': 'redis'})
        flask_app.config.update({'BABEL_DEFAULT_LOCALE': 'fr'})
        # TODO set upload folder in config
        # TODO remove this configuration, it is not useful?
        # flask_app.config.update({'UPLOAD_FOLDER': 'uploads'})

        # Not sure.
        # flask_app.config.update({'BABEL_DEFAULT_TIMEZONE': 'UTC'})

        self.session = Session(flask_app)
        self.api = Api(flask_app)

        # Init API
        self.init_api()

        # Init Views
        self.init_views()

        # Init API docs
        self.init_api_docs()

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
        pass

    def init_views(self):
        from .Views.Index import Index
        from .Views.Login import Login

        # Default arguments
        args = []
        kwargs = {'flaskModule': self}

        # Will create a function that calls the __index__ method with args, kwargs
        flask_app.add_url_rule('/', view_func=Index.as_view('index', *args, **kwargs))
        flask_app.add_url_rule('/login', view_func=Login.as_view('login', *args, **kwargs))

    def init_api_docs(self):
        pass

