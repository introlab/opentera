from flask import Flask, render_template, jsonify, request, abort, session
from flask_session import Session
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

        # Init Views
        self.init_views()

    def init_api(self):
        # from .API.Index import Index
        from .API.QueryUsers import QueryUsers
        from .API.Profile import Profile
        self.api.add_resource(QueryUsers, '/api/users', resource_class_args=[self])
        self.api.add_resource(Profile, '/api/profile', resource_class_args=[self])

    def init_views(self):
        from .Views.Index import Index

        # Default arguments
        args = []
        kwargs = {'module': self}

        # Will create a function that calls the __index__ method with args, kwargs
        flask_app.add_url_rule('/', view_func=Index.as_view('index', *args, **kwargs))

