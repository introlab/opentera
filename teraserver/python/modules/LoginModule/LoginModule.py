
from flask_login import LoginManager, login_user, logout_user
from flask import session, jsonify

from modules.FlaskModule.FlaskModule import flask_app

from libtera.redis.RedisClient import RedisClient
from libtera.db.models.TeraUser import TeraUser

from modules.Globals import auth
from modules.RedisModule.RedisModule import get_redis
from libtera.ConfigManager import ConfigManager
import datetime

class LoginModule(RedisClient):

    login_manager = LoginManager()

    def __init__(self, config: ConfigManager):
        self.config = config

        # Init RedisClient
        RedisClient.__init__(self, config=self.config.redis_config)

        # Setup login manager
        self.setup_login_manager()

    def setup_login_manager(self):
        self.login_manager.init_app(flask_app)
        self.login_manager.session_protection = "strong"
        # self.login_manager.request_loader(self.load_user)

        flask_app.config.update({'REMEMBER_COOKIE_NAME': 'OpenTera',
                                 'REMEMBER_COOKIE_DURATION': 14,
                                 'REMEMBER_COOKIE_SECURE': True,
                                 'PERMANENT_SESSION_LIFETIME': datetime.timedelta(minutes=1),
                                 'REMEMBER_COOKIE_REFRESH_EACH_REQUEST': True})

    @staticmethod
    @login_manager.user_loader
    def load_user(user_id):
        print('LoginModule - load_user', user_id)
        return TeraUser.get_user_by_uuid(user_id)

    @staticmethod
    @auth.verify_password
    def verify_password(username, password):
        print('LoginModule - Verifying password for ', username)

        if TeraUser.verify_password(username=username, password=password):
            registered_user = TeraUser.get_user_by_username(username)
            print('Found user: ', registered_user)
            registered_user.update_last_online()

            login_user(registered_user, remember=True)
            print('Setting key with expiration in 60s', session['_id'], session['user_id'])

            get_redis().set(session['_id'], session['user_id'], ex=60)
            return True
        return False




