
import os

# from sqlalchemy.orm import relationship
# from sqlalchemy import exc

# WebSockets
from autobahn.twisted.resource import WebSocketResource, WSGIRootResource
from autobahn.twisted.websocket import WebSocketServerFactory, WebSocketServerProtocol

# Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, current_user, login_required, AnonymousUserMixin
from flask import Flask, session, request, flash, url_for, redirect, render_template, abort, g, jsonify
from passlib.hash import bcrypt
from flask_httpauth import HTTPBasicAuth

# Twisted
from twisted.application import internet, service
from twisted.internet import reactor, ssl
from twisted.python.threadpool import ThreadPool
from twisted.web.server import Site
from twisted.web.static import File
from twisted.web.wsgi import WSGIResource
from twisted.python import log

import datetime

class MySettings:
    INTERFACE = "localhost"
    PORT = 5000
    THREAD_POOL_SIZE = 2


settings = MySettings()

# DB driver
db = SQLAlchemy()


class TeraWebSocketServerProtocol(WebSocketServerProtocol):

    def __init(self):
        pass

    def onMessage(self, msg, binary):
        print('TeraWebSocketProtocol onMessage', self, msg, binary)
        # Echo
        self.sendMessage(msg, binary)

    def onConnect(self, request):
        print('onConnect', self, request)

    def onClose(self, wasClean, code, reason):
        print('onClose', self, wasClean, code, reason)

    def onOpenHandshakeTimeout(self):
        print('onOpenHandshakeTimeout', self)


class User(db.Model):
    __tablename__ = "users"
    id = db.Column('user_id', db.Integer, primary_key=True)
    username = db.Column('username', db.String(20), unique=True, index=True)
    password = db.Column('password', db.String(100))
    email = db.Column('email', db.String(50), unique=True, index=True)
    registered_on = db.Column('registered_on', db.DateTime)

    def __init__(self, username, password, email):
        self.username = username
        # Store encrypted password
        self.password = bcrypt.encrypt(password)
        self.email = email
        self.registered_on = datetime.datetime.utcnow()

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    def validate_password(self, password):
        return bcrypt.verify(password, self.password)

    def __repr__(self):
        return "<User(username ='%s', email='%s')>" % (self.username, self.email)


def setup_app():
    print('setup_app')

    # Basic HTTP auth
    auth = HTTPBasicAuth()

    app = Flask(__name__)

    def setup_database():
        print('setup_database')
        db.init_app(app)
        db.app = app
        # Create all tables
        db.create_all()

    def setup_flask_login():
        print('setup_flask_login')
        login_manager = LoginManager()
        login_manager.init_app(app)
        login_manager.login_view = 'client_login'

        @login_manager.user_loader
        def load_user(user_id):
            print('load_user')
            return User.query.get(int(user_id))

    # Application configuration
    app.debug = True
    app.secret_key = 'development'
    POSTGRES = {
        'user': 'TeraAgent',
        'pw': 'tera',
        'db': 'test',
        'host': 'localhost',
        'port': '5432',
    }

    # db_uri = 'postgresql://%(user)s:%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES
    db_uri = 'sqlite:///tera.sqlite'
    app.config.update({
        'SQLALCHEMY_DATABASE_URI': db_uri,
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'SQLALCHEMY_ECHO': True
    })

    setup_database()
    setup_flask_login()

    @auth.verify_password
    def verify_password(username, password):
        print('verify_password', username, password)

        if username == 'admin' and password == 'admin':
            # user = User(username, password, 'test@test.com')
            # db.session.add(user)
            # db.session.commit()
            # flask.flash('User successfully registered')
            registered_user = User.query.filter_by(username=username).first()
            print('registered_user ', registered_user)

            if registered_user is None:
                registered_user = User(username, password, 'admin@admin.com')
                db.session.add(registered_user)
                db.session.commit()
                print('user created ', username)

            login_user(registered_user, remember=True)
            g.user = registered_user
            flash('Logged in successfully')
            return True
        return False

    @app.route('/client_login', methods=['GET', 'POST'])
    @auth.login_required
    def test():
        print('test should require login')
        return "wss://%s:%d/wss" % (settings.INTERFACE, settings.PORT)

    @app.route('/', methods=['GET', 'POST'])
    def index():
        return render_template('index.html')

    return app


def setup_twisted(app):
    print('setup_twisted')

    # create a Twisted Web resource for our WebSocket server
    wss_factory = WebSocketServerFactory(u"wss://%s:%d" % (settings.INTERFACE, settings.PORT))
    wss_factory.protocol = TeraWebSocketServerProtocol
    wss_resource = WebSocketResource(wss_factory)

    # create a Twisted Web WSGI resource for our Flask server
    wsgi_resource = WSGIResource(reactor, reactor.getThreadPool(), app)

    # create resource for static assets
    # static_resource = File(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates', 'assets'))

    # the path "/assets" served by our File stuff and
    # the path "/wss" served by our WebSocket stuff
    root_resource = WSGIRootResource(wsgi_resource,  {b'wss': wss_resource})

    # Create a Twisted Web Site
    site = Site(root_resource)

    # setup an application for serving the site
    # web_service = internet.TCPServer(settings.PORT, site, interface=settings.INTERFACE)
    # application = service.Application(__name__)
    # web_service.setServiceParent(application)

    reactor.listenSSL(settings.PORT, site,
                      ssl.DefaultOpenSSLContextFactory(privateKeyFileName='certificates/key.pem',
                                                       certificateFileName='certificates/cert.crt'))
    print('setup_twisted done')


if __name__ == '__main__':
    print('Starting...')
    import sys
    log.startLogging(sys.stdout)
    app = setup_app()
    # app.run()
    setup_twisted(app)
    # print('Running reactor')
    reactor.run()

