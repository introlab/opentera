# Flask
from flask import Flask, request, g, url_for
from flask_restx import Api, Namespace
from flask_babel import Babel

# OpenTera
from opentera.modules.BaseModule import BaseModule
from services.LoggingService.ConfigManager import ConfigManager

# WebSockets
from autobahn.twisted.resource import WSGIRootResource

# Twisted
from twisted.internet import reactor
from twisted.web.http import HTTPChannel
from twisted.web.server import Site
from twisted.web.static import File
from twisted.web.wsgi import WSGIResource
import os

# Flask application
flask_app = Flask("LoggingService")


def get_locale():
    # if a user is logged in, use the locale from the user settings
    user = getattr(g, 'user', None)
    if user is not None:
        return user.locale
    # otherwise try to guess the language from the user accept
    # header the browser transmits.  We support fr/en in this
    # example.  The best match wins.
    return request.accept_languages.best_match(['fr', 'en'])


def get_timezone():
    user = getattr(g, 'user', None)
    if user is not None:
        return user.timezone


# Translations
babel = Babel(flask_app, locale_selector=get_locale,
              timezone_selector=get_timezone,
              default_domain='loggingservice')


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

# API
api = CustomAPI(flask_app, version='1.0.0', title='LoggingService API',
                description='LoggingService API Documentation', doc='/doc', prefix='/api',
                authorizations=authorizations)

# Namespaces
logging_api_ns = api.namespace('logging', description='LoggingService API')


class FlaskModule(BaseModule):

    def __init__(self, config: ConfigManager):

        # Warning, the name must be unique!
        BaseModule.__init__(self, config.service_config['name'] + '.FlaskModule', config)

        flask_app.debug = config.service_config['debug_mode']
        flask_app.config.update({'SESSION_TYPE': 'redis'})
        import redis
        redis_url = redis.from_url('redis://%(username)s:%(password)s@%(hostname)s:%(port)s/%(db)s'
                                   % self.config.redis_config)

        flask_app.config.update({'SESSION_REDIS': redis_url})
        # This is used for session encryption
        flask_app.secret_key = config.service_config['ServiceUUID']
        flask_app.config.update({'BABEL_DEFAULT_LOCALE': 'fr'})
        flask_app.config.update({'SESSION_COOKIE_SECURE': True})
        flask_app.config.update({'PROPAGATE_EXCEPTIONS': True})

        # TODO set upload folder in config
        # TODO remove this configuration, it is not useful?
        # flask_app.config.update({'UPLOAD_FOLDER': 'uploads'})

        # Not sure.
        # flask_app.config.update({'BABEL_DEFAULT_TIMEZONE': 'UTC'})
        # self.session = Session(flask_app)

        # Init API
        FlaskModule.init_api(self, logging_api_ns)

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
        # val = internet.TCPServer(self.config.service_config['port'], site)
        val = reactor.listenTCP(self.config.service_config['port'], site)
        return val

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
        print('LoggingService.FlaskModule - Received message ', pattern, channel, message)
        pass

    @staticmethod
    def init_api(module: object, namespace: Namespace, additional_args: dict = dict()):
        # Default arguments
        kwargs = {'flaskModule': module}
        kwargs |= additional_args

        from services.LoggingService.API.QueryLogEntries import QueryLogEntries
        namespace.add_resource(QueryLogEntries, '/log_entries', resource_class_kwargs=kwargs)
        from services.LoggingService.API.QueryLoginEntries import QueryLoginEntries
        namespace.add_resource(QueryLoginEntries, '/login_entries', resource_class_kwargs=kwargs)

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

