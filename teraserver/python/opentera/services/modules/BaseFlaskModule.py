# Flask
import datetime

from flask import Flask, request, g, url_for
from flask_restx import Api, Resource
from flask_babel import Babel, gettext

# OpenTera
from opentera.modules.BaseModule import BaseModule
from opentera.services.ServiceConfigManager import ServiceConfigManager

# WebSockets
from autobahn.twisted.resource import WSGIRootResource

# Twisted
from twisted.internet import reactor
from twisted.web.http import HTTPChannel
from twisted.web.server import Site
from twisted.web.static import File
from twisted.web.wsgi import WSGIResource
import os

from abc import ABC, abstractmethod
from typing import final

# API
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
flask_app = Flask("OpenTeraService")

# Translations
babel = Babel(flask_app, default_domain='danceservice')


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

    def __init__(self, resource, request_factory=None, *args, **kwargs):
        super().__init__(resource, request_factory, *args, **kwargs)


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
        """
        The Swagger specifications absolute url (ie. `swagger.json`)
        :rtype: str
        """

        if 'X-Script-Name' in request.headers:
            return request.headers['X-Script-Name'] + url_for(self.endpoint('specs'), _external=False)
        else:
            return url_for(self.endpoint('specs'), _external=False)

    @property
    def base_url(self):
        """
        The API base absolute url
        :rtype: str
        """
        if 'X-Script-Name' in request.headers:
            return request.headers['X-Script-Name'] + url_for(self.endpoint('root'), _external=True)
        else:
            return url_for(self.endpoint('root'), _external=True)

    @property
    def base_path(self):
        """
        The API path
        :rtype: str
        """
        if 'X-Script-Name' in request.headers:
            return request.headers['X-Script-Name'] + url_for(self.endpoint('root'), _external=False)
        else:
            return url_for(self.endpoint('root'), _external=False)


api = CustomAPI(flask_app, version='1.0.0', title='OpenTera Service API',
                description='OpenTera Service API Documentation', doc='/doc', prefix='/api',
                authorizations=authorizations)

# Namespaces
default_api_ns = api.namespace('', description='default API')


class DefaultAssetAPI(Resource):

    def get(self):
        return gettext("Not implemented"), 501

    def post(self):
        return gettext("Not implemented"), 501

    def delete(self):
        return gettext("Not implemented"), 501


class BaseFlaskModule(BaseModule, ABC):

    def __init__(self, config: ServiceConfigManager, api_version: str = "1.0.0",
                 asset_infos_api_resource: Resource = None, asset_api_resource: Resource = None):

        # Warning, the name must be unique!
        BaseModule.__init__(self, config.service_config['name'] + '.FlaskModule', config)

        # Update contextual names based on service
        flask_app.import_name = config.service_config['name']
        babel.domain_instance = config.service_config['name']
        api.title = config.service_config['name'] + ' API'
        api.description = config.service_config['name'] + " Service API Documentation"
        api.version = api_version

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

        flask_app.config.update({'UPLOAD_FOLDER': config.service_config['upload_path']})

        # Not sure.
        # flask_app.config.update({'BABEL_DEFAULT_TIMEZONE': 'UTC'})

        # Init basic API
        self.init_basic_api(asset_infos_api_resource, asset_api_resource)

        # Init API
        self.init_api()

        # Init Views
        self.init_views()

    def create_service(self, static_resource_path: str = None, assets_resource_path: str = None):
        # create a Twisted Web WSGI resource for our Flask server
        wsgi_resource = WSGIResource(reactor, reactor.getThreadPool(), flask_app)

        # create resource for static assets
        # static_resource = File(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates', 'assets'))
        import importlib
        m = importlib.import_module(self.__module__)
        base_folder = os.path.dirname(os.path.abspath(m.__file__))
        if not static_resource_path:
            static_resource = File(os.path.join(base_folder, 'static'))
        else:
            static_resource = File(static_resource_path)
        static_resource.contentTypes['.js'] = 'text/javascript'
        static_resource.contentTypes['.css'] = 'text/css'
        static_resource.forbidden = False

        if not assets_resource_path:
            assets_resource = File(os.path.join(base_folder, 'assets'))
        else:
            assets_resource = File(assets_resource_path)
        assets_resource.contentTypes['.js'] = 'text/javascript'
        assets_resource.contentTypes['.css'] = 'text/css'
        assets_resource.forbidden = False

        # the path "/assets" served by our File stuff and
        root_resource = WSGIRootResource(wsgi_resource, {b'static': static_resource, b'assets': assets_resource})

        # Create a Twisted Website
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
        print('OpenTeraService.FlaskModule - Received message ', pattern, channel, message)
        pass

    @abstractmethod
    def init_api(self):  # Must be overridden in children
        pass

    @abstractmethod
    def init_views(self):  # Must be overridden in children
        pass

    @final
    # Can't be overridden in children
    def init_basic_api(self, asset_infos_api_resource: Resource, asset_api_resource: Resource):
        # Default arguments
        kwargs = {'flaskModule': self}

        # Assets API
        if asset_infos_api_resource:
            default_api_ns.add_resource(asset_infos_api_resource,   '/assets/infos', resource_class_kwargs=kwargs)
        else:
            default_api_ns.add_resource(DefaultAssetAPI,            '/assets/infos', resource_class_kwargs=kwargs)

        if asset_api_resource:
            default_api_ns.add_resource(asset_api_resource, '/assets', resource_class_kwargs=kwargs)
        else:
            default_api_ns.add_resource(DefaultAssetAPI,    '/assets', resource_class_kwargs=kwargs)


@flask_app.errorhandler(404)
def page_not_found(e):
    return flask_app.send_static_file('404.html')
    # try:
    #     return flask_app.send_static_file('index.html')
    # except NotFound:
    #     # If the file was not found, send the default index file
    #     return flask_app.send_static_file('default_index.html')


@flask_app.after_request
def apply_caching(response):
    # This is required to expose the backend API to rendered webpages from other sources, such as services
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "*"
    return response


@flask_app.template_filter('format_datetime')
def format_datetime(iso_value: str, date_format: str):
    date_value = datetime.datetime.fromisoformat(iso_value)
    from flask_babel import format_datetime as babel_format_datetime
    return babel_format_datetime(date_value, date_format, False)
