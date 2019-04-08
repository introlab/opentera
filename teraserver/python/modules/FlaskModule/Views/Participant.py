from flask.views import MethodView
from modules.LoginModule.LoginModule import LoginModule, current_participant




from flask import render_template, request, redirect, flash
from modules.Globals import auth
from werkzeug.utils import secure_filename
from modules.FlaskModule.FlaskModule import flask_app
import os
from flask_jwt import JWT, jwt_required, current_identity
from flask_restful import Resource, reqparse


class Participant(MethodView):
    def __init__(self, *args, **kwargs):
        print('Participant.__init__', args, kwargs)
        self.flaskModule = kwargs.get('flaskModule', None)
        print(self.flaskModule)

    @LoginModule.token_required
    def get(self):

        print('current participant', current_participant)
        return 'Participant GET'


