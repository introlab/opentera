from flask_login import logout_user
from flask_restx import Resource, reqparse
from flask_babel import gettext
from flask import session
from modules.FlaskModule.FlaskModule import user_api_ns as api


class UserLogout(Resource):
    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)
        self.parser = reqparse.RequestParser()

    @api.doc(description='Logout from the server')
    def get(self):
        print('logout user')
        logout_user()
        session.clear()
        return gettext("User logged out."), 200
