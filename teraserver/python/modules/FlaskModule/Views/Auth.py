from flask.views import MethodView
from flask import render_template, request, redirect, flash
from modules.Globals import auth
from werkzeug.utils import secure_filename
from modules.FlaskModule.FlaskModule import flask_app
import os


class Auth(MethodView):
    # Decorators everywhere?
    # decorators = [jwt_required]

    def __init__(self, *args, **kwargs):
        print('Auth.__init__', args, kwargs)
        self.flaskModule = kwargs.get('flaskModule', None)
        print(self.flaskModule)

    # @auth.login_required
    def get(self):
        return 'Auth GET'
