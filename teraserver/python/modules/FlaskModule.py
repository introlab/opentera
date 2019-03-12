from flask import Flask, render_template, jsonify, request, abort, session
from flask_session import Session
from sqlalchemy.exc import InvalidRequestError
from modules.Globals import auth

from libtera.db.models.TeraUser import TeraUser

flask_app = Flask("OpenTera")


class FlaskModule:

    def __init__(self):
        flask_app.debug = True
        flask_app.secret_key = 'development'
        flask_app.config.update({'SESSION_TYPE': 'redis'})
        self.session = Session(flask_app)

    def run(self, server_config):
        # Self Generated certificates. Not for production.
        context = (server_config['ssl_path'] + '/cert.crt',
                   server_config['ssl_path'] + '/key.pem')

        flask_app.run(ssl_context=context, port=server_config['port'])

    @staticmethod
    @flask_app.route('/api/profile', methods=['GET', 'POST'])
    @auth.login_required
    def profile():
        print('profile')
        profile = {'profile': 'empty'}
        return jsonify(profile)

    @staticmethod
    @flask_app.route('/', methods=['GET', 'POST'])
    @auth.login_required
    def index():
        return render_template('index.html')

    # Queries
    @staticmethod
    @flask_app.route('/api/query/users', methods=['GET', 'POST', 'DELETE'])
    @auth.login_required
    def users():
        if request.method == 'GET':
            if not request.args:
                # Return current user information
                user = TeraUser.get_user_by_uuid(session['user_id'])
                return jsonify([user.to_json()])

            # Parse query items
            # TODO: Check access rights
            try:
                users = TeraUser.query_data(request.args.to_dict())
                users_list = []
                for user in users:
                    users_list.append(user.to_json())
                return jsonify(users_list)
            except InvalidRequestError:
                abort(500)

            return

        if request.method == 'POST':
            abort(501)

        if request.method == 'DELETE':
            abort(501)
