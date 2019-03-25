from flask import Flask
from flask_session import Session
from flask_restful import Api
from libtera.redis.RedisClient import RedisClient
from libtera.ConfigManager import ConfigManager

flask_app = Flask("OpenTera")


class FlaskModule(RedisClient):

    def __init__(self,  config: ConfigManager):

        self.config = config

        # Init RedisClient
        RedisClient.__init__(self, config=self.config.redis_config)

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
        from .API.Login import Login
        from .API.Logout import Logout
        from .API.QueryUsers import QueryUsers
        from .API.Definitions import Definitions
        from .API.OnlineUsers import OnlineUsers
        from .API.QueryUserGroups import QueryUserGroups
        self.api.add_resource(Login, '/api/login', resource_class_args=[self])
        self.api.add_resource(Logout, '/api/logout', resource_class_args=[self])
        self.api.add_resource(QueryUsers, '/api/users', resource_class_args=[self])
        self.api.add_resource(QueryUserGroups, '/api/usergroups', resource_class_args=[self])
        self.api.add_resource(Definitions, '/api/definitions', resource_class_args=[self])
        self.api.add_resource(OnlineUsers, '/api/online', resource_class_args=[self])

    def init_views(self):
        from .Views.Index import Index

        # Default arguments
        args = []
        kwargs = {'flaskModule': self}

        # Will create a function that calls the __index__ method with args, kwargs
        flask_app.add_url_rule('/', view_func=Index.as_view('index', *args, **kwargs))
