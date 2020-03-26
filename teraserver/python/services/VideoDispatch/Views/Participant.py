from flask.views import MethodView
from flask import render_template, request
from services.VideoDispatch.AccessManager import AccessManager, current_participant_client

import json


class Participant(MethodView):

    def __init__(self, *args, **kwargs):
        self.flaskModule = kwargs.get('flaskModule', None)

    @AccessManager.token_required
    def get(self):
        # print('get')

        hostname = self.flaskModule.config.server_config['hostname']
        port = self.flaskModule.config.server_config['port']
        backend_hostname = self.flaskModule.config.backend_config['hostname']
        backend_port = self.flaskModule.config.backend_config['port']
        if 'X_EXTERNALHOST' in request.headers:
            backend_hostname = request.headers['X_EXTERNALHOST']

        if 'X_EXTERNALPORT' in request.headers:
            backend_port = request.headers['X_EXTERNALPORT']

        return render_template('participant.html', hostname=hostname, port=port,
                               backend_hostname=backend_hostname, backend_port=backend_port)

    def post(self):
        print('post')
        pass