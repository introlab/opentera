# Flask
from flask import Flask, request, g, url_for
from flask_restx import Api
from flask_babel import Babel

# OpenTera
from opentera.modules.BaseModule import BaseModule
from services.VideoRehabService.ConfigManager import ConfigManager

# WebSockets
from autobahn.twisted.resource import WSGIRootResource

# Twisted
from twisted.internet import reactor
from twisted.web.http import HTTPChannel
from twisted.web.server import Site
from twisted.web.static import File
from twisted.web.wsgi import WSGIResource
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
def get_locale():
    # if a user is logged in, use the locale from the user settings
    user = getattr(g, 'user', None)
    if user is not None:
        return user.locale
    # otherwise try to guess the language from the user accept
    # header the browser transmits.  We support fr/en in this
    # example.  The best match wins.
    lang = request.accept_languages.best_match(['fr', 'en'])
    return lang


def get_timezone():
    user = getattr(g, 'user', None)
    if user is not None:
        return user.timezone


babel = Babel(flask_app, locale_selector=get_locale, timezone_selector=get_timezone, default_domain='videorehabservice')


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


class FlaskModule(BaseModule):

    # API
    api = CustomAPI(flask_app, version='1.0.0', title='VideoRehabService API',
                    description='VideoRehabService API Documentation', doc='/doc', prefix='/api',
                    authorizations=authorizations)

    # Namespaces
    default_api_ns = api.namespace('default', description='default API')

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
        print('VideoDispatchService.FlaskModule - Received message ', pattern, channel, message)
        pass

    def init_api(self):
        # Default arguments
        kwargs = {'flaskModule': self}

    def init_views(self):
        # Default arguments
        args = []
        kwargs = {'flaskModule': self}

        from services.VideoRehabService.Views.Index import Index
        from services.VideoRehabService.Views.ParticipantLocalView import ParticipantLocalView
        from services.VideoRehabService.Views.ParticipantDashboard import ParticipantDashboard
        from services.VideoRehabService.Views.ParticipantEndpoint import ParticipantEndpoint
        from services.VideoRehabService.Views.ParticipantError import ParticipantError

        # Will create a function that calls the __index__ method with args, kwargs
        flask_app.add_url_rule('/', view_func=Index.as_view('index', *args, **kwargs))
        flask_app.add_url_rule('/participant_localview', view_func=ParticipantLocalView.as_view('participant_localview',
                                                                                                *args, **kwargs))
        flask_app.add_url_rule('/participant', view_func=ParticipantDashboard.as_view('participant_dashboard', *args,
                                                                                      **kwargs))
        flask_app.add_url_rule('/participant_endpoint',
                               view_func=ParticipantEndpoint.as_view('participant_endpoint', *args, **kwargs))
        flask_app.add_url_rule('/participant_error',
                               view_func=ParticipantError.as_view('participant_error', *args, **kwargs))

        # User
        # from services.VideoRehabService.Views.UserDashboard import UserDashboard
        from services.VideoRehabService.Views.UserError import UserError
        from services.VideoRehabService.Views.UserSessionLobby import UserSessionLobby

        # flask_app.add_url_rule('/user', view_func=UserDashboard.as_view('user_dashboard', *args, **kwargs))
        flask_app.add_url_rule('/user_error', view_func=UserError.as_view('user_error', *args, **kwargs))
        flask_app.add_url_rule('/user_session_lobby',
                               view_func=UserSessionLobby.as_view('user_session_lobby', *args, **kwargs))


@flask_app.after_request
def apply_caching(response):
    # This is required to expose the backend API to rendered webpages from other sources, such as services
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "*"
    return response

