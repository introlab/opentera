# Flask
from flask import Flask, request, g, url_for
from flask_session import Session
from flask_restx import Api
from flask_babel import Babel

# OpenTera
from modules.BaseModule import BaseModule, ModuleNames
from services.VideoRehabService.ConfigManager import ConfigManager

# WebSockets
from autobahn.twisted.resource import WebSocketResource, WSGIRootResource

# Twisted
from twisted.application import internet, service
from twisted.internet import reactor, ssl
from twisted.python.threadpool import ThreadPool
from twisted.web.http import HTTPChannel
from twisted.web.server import Site
from twisted.web.static import File
from twisted.web.wsgi import WSGIResource
from twisted.python import log
from OpenSSL import SSL
import sys
import os

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


# Flask application
flask_app = Flask("VideoRehabService")

# Translations
babel = Babel(flask_app)


class MyHTTPChannel(HTTPChannel):
    def allHeadersReceived(self):
        # Verify if we have a client with a certificate...
        # cert = self.transport.getPeerCertificate()
        cert = None
        if getattr(self.transport, "getPeerCertificate", None):
            cert = self.transport.getPeerCertificate()

        # Current request
        req = self.requests[-1]

        # SAFETY X-Device-UUID, X-Participant-UUID must not be set in header before testing certificate
        if req.requestHeaders.hasHeader('X-Device-UUID'):
            req.requestHeaders.removeHeader('X-Device-UUID')
            # TODO raise error?

        if req.requestHeaders.hasHeader('X-Participant-UUID'):
            req.requestHeaders.removeHeader('X-Participant-UUID')
            # TODO raise error ?

        if cert is not None:
            # Certificate found, add information in header
            subject = cert.get_subject()
            # Get UID if possible
            if 'Device' in subject.CN and hasattr(subject, 'UID'):
                user_id = subject.UID
                req.requestHeaders.addRawHeader('X-Device-UUID', user_id)
            if 'Participant' in subject.CN and hasattr(subject, 'UID'):
                user_id = subject.UID
                req.requestHeaders.addRawHeader('X-Participant-UUID', user_id)

        HTTPChannel.allHeadersReceived(self)


class MySite(Site):
    protocol = MyHTTPChannel

    def __init__(self, resource, requestFactory=None, *args, **kwargs):
        super().__init__(resource, requestFactory, *args, **kwargs)


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


class FlaskModule(BaseModule):

    # API
    api = CustomAPI(flask_app, version='1.0.0', title='VideoRehabService API',
                    description='VideoRehabService API Documentation', doc='/doc', prefix='/api',
                    authorizations=authorizations)

    # Namespaces
    default_api_ns = api.namespace('default', description='default API')

    def __init__(self, config: ConfigManager):

        # Warning, the name must be unique!
        BaseModule.__init__(self, config.service_config['name'] + '.TwistedModule', config)

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
        # self.session = Session(flask_app)

        # Init API
        self.init_api()

        # Init Views
        self.init_views()

    def create_service(self):
        # create a Twisted Web WSGI resource for our Flask server
        wsgi_resource = WSGIResource(reactor, reactor.getThreadPool(), flask_app)

        # create resource for static assets
        # static_resource = File(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates', 'assets'))
        base_folder = os.path.dirname(os.path.abspath(__file__))
        static_resource = File(os.path.join(base_folder, 'static'))
        static_resource.contentTypes['.js'] = 'text/javascript'
        static_resource.forbidden = True

        # the path "/assets" served by our File stuff and
        root_resource = WSGIRootResource(wsgi_resource, {b'assets': static_resource})

        # Create a Twisted Web Site
        site = MySite(root_resource)

        return internet.TCPServer(self.config.service_config['port'], site)

    def __del__(self):
        pass

    def verifyCallback(self, connection, x509, errnum, errdepth, ok):
        if not ok:
            print('Invalid cert from subject:', connection, x509.get_subject(), errnum, errdepth, ok)
            return False
        else:
            print("Certs are fine", connection, x509.get_subject(), errnum, errdepth, ok)
        return True

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

    def init_views(self):
        # Default arguments
        args = []
        kwargs = {'flaskModule': self}


@flask_app.after_request
def apply_caching(response):
    # This is required to expose the backend API to rendered webpages from other sources, such as services
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "*"
    return response

