from flask.views import MethodView
from flask import render_template, request, redirect, flash
from modules.Globals import auth
from werkzeug.utils import secure_filename
from modules.FlaskModule.FlaskModule import flask_app
import os
from flask_jwt import JWT, jwt_required, current_identity
from flask_restful import Resource, reqparse

from functools import wraps


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        print('token_required')

        print('request', request)
        # Parse args
        parser = reqparse.RequestParser()
        parser.add_argument('token', type=str, help='Token', required=True)

        args = parser.parse_args(strict=False)

        # Verify token.
        if 'token' in args:
            # Returns the function if authenticated with token
            return f(*args, **kwargs)

        else:
            return 'Forbidden', 403

    return decorated


class Participant(MethodView):
    # Decorators everywhere?
    # decorators = [token_required]

    def __init__(self, *args, **kwargs):
        print('Participant.__init__', args, kwargs)
        self.flaskModule = kwargs.get('flaskModule', None)
        print(self.flaskModule)

    @token_required
    def get(self):
        return 'Participant GET'


