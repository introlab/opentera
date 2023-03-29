# Flask
from flask import Flask, request, g, url_for
from flask_restx import Api
from flask_babel import Babel

# OpenTera
from opentera.modules.BaseModule import BaseModule

from ConfigManager import ConfigManager

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
# TODO: Rename example service
flask_app = Flask("ExampleService")

# Translations

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
# TODO: Rename files in the translation folder accordingly to your service name (and change default_domain below)
babel = Babel(flask_app, locale_selector=get_locale,
              timezone_selector=get_timezone,
              default_domain='example_service')


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

        if req.requestHeaders.hasHeader('X-Participant-UUID'):
            req.requestHeaders.removeHeader('X-Participant-UUID')

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
# TODO: Update API title and description according to your own service
api = CustomAPI(flask_app, version='1.0.0', title='ExampleService API',
                description='ExampleService API Documentation', doc='/doc', prefix='/api',
                authorizations=authorizations)

# Namespaces
service_api_ns = api.namespace('', description='ExampleService API')


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
        flask_app.config.update({'SESSION_TYPE': 'redis'})
        flask_app.config.update({'BABEL_DEFAULT_LOCALE': 'fr'})
        flask_app.config.update({'SESSION_COOKIE_SECURE': True})

        flask_app.config.update({'UPLOAD_FOLDER': config.specific_service_config['files_directory']})

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
        print('FileTransferService.FlaskModule - Received message ', pattern, channel, message)
        pass

    def init_api(self):
        # Default arguments
        kwargs = {'flaskModule': self}
        from API.QueryAssetFileInfos import QueryAssetFileInfos
        from API.QueryAssetFile import QueryAssetFile
        from API.QueryVersion import QueryVersion

        # Those 2 APIs are required for any service that support assets
        service_api_ns.add_resource(QueryAssetFileInfos,    '/assets/infos', resource_class_kwargs=kwargs)
        service_api_ns.add_resource(QueryAssetFile,         '/assets', resource_class_kwargs=kwargs)

        # Version API - general information about the service
        service_api_ns.add_resource(QueryVersion,           '/version', resource_class_kwargs=kwargs)

        # TODO Define your own API endpoints here

    def init_views(self):
        # Default arguments
        args = []
        kwargs = {'flaskModule': self}

        # Default view
        from views.Index import Index
        flask_app.add_url_rule('/', view_func=Index.as_view('index', *args, **kwargs))

        # TODO Define any view you might be using here


@flask_app.errorhandler(404)
def page_not_found(e):
    return flask_app.send_static_file('404.html')


@flask_app.after_request
def apply_caching(response):
    # This is required to expose the backend API to rendered webpages from other sources, such as services
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "*"
    return response
