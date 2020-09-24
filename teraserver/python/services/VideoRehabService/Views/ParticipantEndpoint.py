from flask.views import MethodView
from flask import render_template, request
from services.shared.ServiceAccessManager import ServiceAccessManager, current_participant_client

import json


class ParticipantEndpoint(MethodView):

    def __init__(self, *args, **kwargs):
        self.flaskModule = kwargs.get('flaskModule', None)

    @ServiceAccessManager.static_token_required
    def get(self):
        backend_hostname = self.flaskModule.config.backend_config['hostname']
        backend_port = self.flaskModule.config.backend_config['port']

        if 'X_EXTERNALHOST' in request.headers:
            backend_hostname = request.headers['X_EXTERNALHOST']

        if 'X_EXTERNALPORT' in request.headers:
            backend_port = request.headers['X_EXTERNALPORT']

        participant_name = 'Anonymous'

        # Get participant information
        if current_participant_client:
            participant_info = current_participant_client.get_participant_infos()
            if participant_info and 'participant_name' in participant_info:
                participant_name = participant_info['participant_name']

            return render_template('participant_endpoint.html', backend_hostname=backend_hostname,
                                   backend_port=backend_port,
                                   participant_name=participant_name,
                                   participant_token=current_participant_client.participant_token)
        else:
            return 'Unauthorized', 403
