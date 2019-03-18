
from flask_login import LoginManager, login_user, logout_user
from flask import session, jsonify

from modules.FlaskModule.FlaskModule import flask_app

from libtera.redis.RedisClient import RedisClient
from libtera.db.models.TeraUser import TeraUser

from modules.Globals import auth
from modules.RedisModule.RedisModule import get_redis


class LoginModule:

    login_manager = LoginManager()

    def __init__(self):
        pass

    def setup(self):
        self.login_manager.init_app(flask_app)
        self.login_manager.session_protection = "strong"

        flask_app.config.update({'REMEMBER_COOKIE_NAME': 'OpenTera',
                                 'REMEMBER_COOKIE_DURATION': 14,
                                 'REMEMBER_COOKIE_SECURE': True,
                                 'REMEMBER_COOKIE_REFRESH_EACH_REQUEST': True})

    @staticmethod
    @login_manager.user_loader
    def load_user(user_id):
        print('LoginModule - Loading user')
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

    ###########################################################
    # Handlers
    ###########################################################
    @staticmethod
    @flask_app.route('/api/login', methods=['GET', 'POST'])
    @auth.login_required
    def login():
        # print('Setting key with expiration in 60s', session['_id'], session['user_id'])
        # get_redis().set(session['_id'], session['user_id'], ex=60)
        reply = {"websocket_url": "wss://localhost:4040/wss?id=" + session['_id'],
                 "user_uuid": session['user_id']}
        json_reply = jsonify(reply)

        return json_reply

    @staticmethod
    @flask_app.route('/api/logout')
    def logout():
        logout_user()
        return "User logged out."




