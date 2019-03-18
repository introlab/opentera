from flask import Flask, render_template, jsonify, request, abort, session
from flask_session import Session

from modules.Globals import auth


from flask_restful import Api

flask_app = Flask("OpenTera")


class FlaskModule:

    def __init__(self):
        flask_app.debug = True
        flask_app.secret_key = 'development'
        flask_app.config.update({'SESSION_TYPE': 'redis'})
        self.session = Session(flask_app)
        self.api = Api(flask_app)

        # Init API
        self.init_api()

    def init_api(self):
        # from .API.Index import Index
        from .API.QueryUsers import QueryUsers
        from .API.Profile import Profile
        self.api.add_resource(QueryUsers, '/api/users', resource_class_args=[self])
        self.api.add_resource(Profile, '/api/profile', resource_class_args=[self])

    # Index for testing...
    @flask_app.route('/', methods=['GET', 'POST'])
    @auth.login_required
    def index():
        return render_template('index.html')
