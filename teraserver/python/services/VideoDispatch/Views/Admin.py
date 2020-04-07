from flask.views import MethodView
from flask import render_template, request
from services.VideoDispatch.AccessManager import AccessManager
from requests import get, post
import json


class Admin(MethodView):
    def __init__(self, *args, **kwargs):
        self.flaskModule = kwargs.get('flaskModule', None)

    @AccessManager.token_required
    def get(self):
        return render_template('admin.html')

    @AccessManager.token_required
    def post(self):
        return 'Not implemented', 501
